"""
EventRiskGuard
--------------
Prepares your screener for earnings/macro days by:
- detecting upcoming events (earnings, dividends, Basel III reports)
- scanning 72h news with FinBERT
- generating risk flags & position haircuts
- optional beta-based hedge suggestion vs XJO

Dependencies:
  pip install yfinance pandas numpy scikit-learn beautifulsoup4

Integrates with:
  - overnight_pipeline.py (risk assessment before prediction)
  - batch_predictor.py (weight haircuts)
  - report_generator.py (visualization)
"""

from __future__ import annotations
import math
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# Config (tweak to your taste)
# -----------------------------
EVENT_LOOKAHEAD_DAYS = 7
EARNINGS_BUFFER_DAYS = 3   # sit out +/- N days (entry/size haircuts)
DIV_BUFFER_DAYS = 1
NEWS_WINDOW_DAYS = 3
NEG_SENTIMENT_THRES = -0.10  # average FinBERT polarity below this => bearish
HAIRCUT_MAX = 0.70   # up to 70% weight reduction
HAIRCUT_MIN = 0.20
VOL_SPIKE_MULT = 1.35   # if realized vol > 1.35x 30d median => add haircut
XJO_TICKER = "^AXJO"  # ASX 200 index
RISK_FREE = 0.02     # used in beta calc (not essential)

# 🆕 Basel III and regulatory report keywords
REGULATORY_KEYWORDS = [
    'basel iii', 'pillar 3', 'prudential disclosure', 'apra',
    'capital adequacy', 'liquidity coverage', 'net stable funding'
]


@dataclass
class EventInfo:
    ticker: str
    event_type: str       # 'earnings' | 'dividend' | 'macro' | 'basel_iii' | 'regulatory'
    date: datetime
    source: str
    title: Optional[str] = None
    url: Optional[str] = None


@dataclass
class GuardResult:
    ticker: str
    has_upcoming_event: bool
    days_to_event: Optional[int]
    event_type: Optional[str]
    event_title: Optional[str]  # 🆕 for regulatory reports
    event_url: Optional[str]    # 🆕 for regulatory reports
    avg_sentiment_72h: Optional[float]
    vol_spike: bool
    risk_score: float          # 0..1 (1 = highest risk)
    weight_haircut: float      # 0..1 fraction to reduce target weight
    skip_trading: bool         # True if sit out window
    suggested_hedge_beta: Optional[float]  # beta vs XJO (rolling)
    suggested_hedge_ratio: Optional[float] # dollars short XJO per $ long ticker
    warning_message: Optional[str] = None  # 🆕 Human-readable warning


# -----------------------------
# FinBERT sentiment helper
# -----------------------------
def compute_finbert_sentiment_for_news(headlines: List[str]) -> Optional[float]:
    """
    Compute average FinBERT sentiment from list of headlines.
    Returns value in [-1, 1] range.
    """
    if not headlines:
        return None
    
    try:
        # Try to import FinBERT bridge from your existing system
        try:
            from .finbert_bridge import get_finbert_bridge
        except ImportError:
            try:
                from finbert_bridge import get_finbert_bridge
            except ImportError:
                logger.warning("FinBERT bridge not available; using fallback sentiment")
                return _fallback_sentiment(headlines)
        
        fb = get_finbert_bridge()
        scores = []
        
        for h in headlines:
            try:
                out = fb.analyze(h)
                
                # Normalize: assume out['sentiment'] in [-1,1] or map labels
                if isinstance(out, dict):
                    if 'sentiment' in out:
                        scores.append(float(out['sentiment']))
                    elif 'label' in out:
                        # Crude mapping if only label present
                        label = out['label'].lower()
                        if label == 'positive':
                            scores.append(+0.5)
                        elif label == 'negative':
                            scores.append(-0.5)
                        else:
                            scores.append(0.0)
            except Exception as e:
                logger.debug(f"FinBERT error on headline: {e}")
                continue
        
        if not scores:
            return None
        
        return float(np.mean(scores))
        
    except Exception as e:
        logger.warning(f"FinBERT sentiment failed: {e}, using fallback")
        return _fallback_sentiment(headlines)


def _fallback_sentiment(headlines: List[str]) -> float:
    """Simple keyword-based fallback sentiment"""
    negative_words = ['loss', 'drop', 'fall', 'decline', 'weak', 'lower', 'miss', 'warning']
    positive_words = ['gain', 'rise', 'up', 'growth', 'strong', 'higher', 'beat', 'surge']
    
    score = 0.0
    count = 0
    
    for h in headlines:
        h_lower = h.lower()
        neg_count = sum(1 for w in negative_words if w in h_lower)
        pos_count = sum(1 for w in positive_words if w in h_lower)
        
        if neg_count + pos_count > 0:
            score += (pos_count - neg_count) / (pos_count + neg_count)
            count += 1
    
    return score / count if count > 0 else 0.0


# -----------------------------
# Event providers (pluggable)
# -----------------------------
class YFinanceEventProvider:
    """Lightweight: uses yf.Ticker.calendar + dividends schedule when present."""
    
    def get_upcoming_events(self, ticker: str, lookahead_days: int) -> List[EventInfo]:
        evts: List[EventInfo] = []
        
        try:
            tk = yf.Ticker(ticker)
            cal = tk.calendar  # DataFrame with index like 'Earnings Date'
            now = datetime.now(timezone.utc)
            horizon = now + timedelta(days=lookahead_days)

            # Earnings (best-effort; yfinance can be sparse for ASX)
            for label in ['Earnings Date', 'Earnings Date 1', 'EarningsDate']:
                if cal is not None and label in cal.index:
                    edate = cal.loc[label].values[0]
                    if pd.notna(edate):
                        ed = pd.to_datetime(edate).to_pydatetime()
                        if not ed.tzinfo:
                            ed = ed.replace(tzinfo=timezone.utc)
                        if now <= ed <= horizon:
                            evts.append(EventInfo(
                                ticker=ticker,
                                event_type='earnings',
                                date=ed,
                                source='yfinance.calendar'
                            ))

            # Dividends (next ex-div if upcoming)
            try:
                divs = tk.dividends
                if divs is not None and not divs.empty:
                    # Ensure index is timezone-aware
                    if divs.index.tz is None:
                        divs.index = divs.index.tz_localize('UTC')
                    else:
                        divs.index = divs.index.tz_convert('UTC')
                    
                    future_divs = divs[divs.index >= now]
                    if not future_divs.empty:
                        first = future_divs.index[0].to_pydatetime()
                        if now <= first <= horizon:
                            evts.append(EventInfo(
                                ticker=ticker,
                                event_type='dividend',
                                date=first,
                                source='yfinance.dividends'
                            ))
            except Exception as e:
                logger.debug(f"Dividend check failed for {ticker}: {e}")

        except Exception as e:
            logger.debug(f"YFinanceEventProvider failed for {ticker}: {e}")
        
        return evts


class ManualCSVEventProvider:
    """
    Optional: point this to a CSV you maintain with confirmed ASX dates.
    Columns: ticker,event_type,date (YYYY-MM-DD),title (optional),url (optional)
    
    Example CSV:
    ticker,event_type,date,title,url
    CBA.AX,basel_iii,2025-11-11,"Basel III Pillar 3 Report","https://www.asx.com.au/..."
    ANZ.AX,earnings,2025-11-15,"Q1 Results","https://www.asx.com.au/..."
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        self.df = None
        
        if csv_path is None:
            # Try default path
            csv_path = Path(__file__).parent.parent / 'config' / 'event_calendar.csv'
        
        if csv_path and os.path.exists(csv_path):
            try:
                self.df = pd.read_csv(csv_path, parse_dates=['date'])
                logger.info(f"Loaded {len(self.df)} events from {csv_path}")
            except Exception as e:
                logger.warning(f"Manual CSV load failed: {e}")
        else:
            logger.debug(f"Event calendar CSV not found at {csv_path}")

    def get_upcoming_events(self, ticker: str, lookahead_days: int) -> List[EventInfo]:
        if self.df is None or self.df.empty:
            return []
        
        now = pd.Timestamp.utcnow()
        horizon = now + pd.Timedelta(days=lookahead_days)
        
        # Make dates timezone-aware if they aren't already
        if self.df['date'].dt.tz is None:
            date_col = self.df['date'].dt.tz_localize('UTC')
        else:
            date_col = self.df['date'].dt.tz_convert('UTC')
        
        rows = self.df[
            (self.df['ticker'].str.upper() == ticker.upper()) &
            (date_col >= now) &
            (date_col <= horizon)
        ]
        
        out = []
        for _, r in rows.iterrows():
            # Get the date and make it timezone-aware
            evt_date = r['date']
            if not hasattr(evt_date, 'tz') or evt_date.tz is None:
                evt_date = pd.Timestamp(evt_date).tz_localize('UTC')
            else:
                evt_date = pd.Timestamp(evt_date).tz_convert('UTC')
            
            out.append(EventInfo(
                ticker=ticker,
                event_type=str(r['event_type']).lower(),
                date=evt_date.to_pydatetime(),
                source='manual.csv',
                title=r.get('title'),
                url=r.get('url')
            ))
        
        return out


# -----------------------------
# Hedge helper (rolling beta)
# -----------------------------
def rolling_beta(ticker: str, index_ticker: str = XJO_TICKER,
                 lookback_days: int = 252) -> Optional[float]:
    """
    Calculate rolling beta vs index (default ASX 200).
    Returns None if insufficient data.
    """
    try:
        px = yf.download(
            [ticker, index_ticker],
            period=f"{max(lookback_days, 60)}d",
            interval="1d",
            auto_adjust=True,
            progress=False
        )['Close'].dropna()
        
        if isinstance(px, pd.Series) or px.shape[0] < 60:
            return None
        
        rets = px.pct_change().dropna()
        
        if index_ticker not in rets.columns or ticker not in rets.columns:
            return None
        
        x = rets[index_ticker].values.reshape(-1, 1)
        y = rets[ticker].values.reshape(-1, 1)
        
        if len(x) < 60:
            return None
        
        model = LinearRegression().fit(x, y)
        beta = float(model.coef_[0][0])
        
        return beta
        
    except Exception as e:
        logger.debug(f"Beta calc failed for {ticker}: {e}")
        return None


# -----------------------------
# Volatility spike detector
# -----------------------------
def realized_vol_spike(ticker: str, window: int = 10, ref: int = 30,
                       mult: float = VOL_SPIKE_MULT) -> bool:
    """
    Detect if recent volatility is significantly higher than baseline.
    Returns True if recent realized vol > mult * median baseline vol.
    """
    try:
        px = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            auto_adjust=True,
            progress=False
        )['Close'].dropna()
        
        if px.shape[0] < ref + window + 5:
            return False
        
        ret = px.pct_change().dropna()
        
        # Recent realized volatility
        rv = np.sqrt((ret.tail(window) ** 2).sum())
        
        # Baseline median volatility
        ref_med = np.median(ret.rolling(ref).std().dropna())
        
        return bool(rv > mult * ref_med)
        
    except Exception as e:
        logger.debug(f"Vol spike check failed for {ticker}: {e}")
        return False


# -----------------------------
# Guard core
# -----------------------------
class EventRiskGuard:
    """
    Main Event Risk Guard class.
    
    Usage:
        guard = EventRiskGuard()
        result = guard.assess('CBA.AX')
        
        if result.skip_trading:
            print(f"Skip trading {result.ticker}: {result.warning_message}")
        elif result.weight_haircut > 0:
            print(f"Reduce {result.ticker} position by {result.weight_haircut*100:.0f}%")
    """
    
    def __init__(self, extra_providers: Optional[List] = None, csv_path: Optional[str] = None):
        """
        Initialize Event Risk Guard.
        
        Args:
            extra_providers: Additional event provider instances
            csv_path: Path to manual event calendar CSV
        """
        self.providers = [
            YFinanceEventProvider(),
            ManualCSVEventProvider(csv_path=csv_path)
        ]
        
        if extra_providers:
            self.providers.extend(extra_providers)
        
        # Initialize Market Regime Engine for crash risk assessment
        try:
            from .market_regime_engine import MarketRegimeEngine
            self.regime_engine = MarketRegimeEngine()
            self.regime_available = True
            logger.info("✓ Market Regime Engine initialized successfully")
        except (ImportError, ModuleNotFoundError, Exception) as e:
            try:
                from market_regime_engine import MarketRegimeEngine
                self.regime_engine = MarketRegimeEngine()
                self.regime_available = True
                logger.info("✓ Market Regime Engine initialized successfully")
            except (ImportError, ModuleNotFoundError, Exception) as e2:
                self.regime_engine = None
                self.regime_available = False
                logger.warning(f"  Market Regime Engine not available: {e2} (optional)")
                logger.warning("  Install hmmlearn to enable: pip install hmmlearn>=0.3.0")
        
        logger.info("Event Risk Guard initialized with %d providers", len(self.providers))

    def _collect_events(self, ticker: str) -> List[EventInfo]:
        """Collect events from all providers and deduplicate."""
        evts: List[EventInfo] = []
        
        for p in self.providers:
            try:
                evts.extend(p.get_upcoming_events(ticker, EVENT_LOOKAHEAD_DAYS))
            except Exception as e:
                logger.debug(f"Provider error: {e}")
        
        # De-duplicate on (type, date)
        uniq = {}
        for e in evts:
            k = (e.event_type, e.date.date())
            if k not in uniq:
                uniq[k] = e
        
        return list(uniq.values())

    def _news_headlines(self, ticker: str, days: int = NEWS_WINDOW_DAYS) -> List[str]:
        """Fetch recent news headlines from yfinance."""
        try:
            tk = yf.Ticker(ticker)
            news = tk.news or []
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            out = []
            
            for n in news:
                # yfinance returns UNIX seconds in 'providerPublishTime'
                ts = n.get('providerPublishTime')
                if ts:
                    dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                    if dt >= cutoff and 'title' in n:
                        out.append(n['title'])
            
            return out[:30]  # Limit to 30 most recent
            
        except Exception as e:
            logger.debug(f"News fetch failed for {ticker}: {e}")
            return []

    def _check_regulatory_keywords(self, event: EventInfo) -> bool:
        """Check if event title contains regulatory keywords (Basel III, etc.)"""
        if not event.title:
            return False
        
        title_lower = event.title.lower()
        return any(kw in title_lower for kw in REGULATORY_KEYWORDS)
    
    def _get_regime_crash_risk(self) -> Tuple[str, float]:
        """
        Get market regime and crash risk score from Market Regime Engine.
        
        Returns:
            Tuple of (regime_label, crash_risk_score)
        """
        if not self.regime_available or self.regime_engine is None:
            return ("UNKNOWN", 0.0)
        
        try:
            regime_data = self.regime_engine.analyse()
            regime_label = regime_data.get('regime_label', 'UNKNOWN').upper()
            crash_risk = regime_data.get('crash_risk_score', 0.0)
            
            logger.info(f"Market Regime Engine: {regime_label}, Crash Risk: {crash_risk:.3f}")
            
            return (regime_label, crash_risk)
        except Exception as e:
            logger.warning(f"Market Regime Engine analysis failed: {e}")
            return ("UNKNOWN", 0.0)

    def assess(self, ticker: str) -> GuardResult:
        """
        Assess event risk for a given ticker.
        
        Returns GuardResult with:
        - Event detection status
        - Risk score (0-1)
        - Weight haircut recommendation
        - Skip trading flag
        - Warning message
        """
        evts = self._collect_events(ticker)
        now = datetime.now(timezone.utc)
        next_evt = min(evts, key=lambda e: e.date, default=None)

        has_evt = next_evt is not None
        days_to = None
        e_type = None
        e_title = None
        e_url = None
        skip = False
        haircut = 0.0
        warning = None

        if has_evt:
            e_type = next_evt.event_type
            e_title = next_evt.title
            e_url = next_evt.url
            days_to = max(0, (next_evt.date - now).days)
            
            # 🆕 Check if regulatory report (Basel III, Pillar 3)
            is_regulatory = self._check_regulatory_keywords(next_evt) or \
                           e_type in ['basel_iii', 'regulatory', 'pillar_3']
            
            # Sit-out buffer: earnings and regulatory stricter than dividends
            if e_type == 'earnings' and abs((next_evt.date - now).days) <= EARNINGS_BUFFER_DAYS:
                skip = True
                warning = f"⚠️ Earnings in {days_to}d - within {EARNINGS_BUFFER_DAYS}d buffer"
            elif is_regulatory and abs((next_evt.date - now).days) <= EARNINGS_BUFFER_DAYS:
                skip = True
                warning = f"🚨 REGULATORY REPORT in {days_to}d - HIGH RISK (Basel III/Pillar 3)"
            elif e_type == 'dividend' and abs((next_evt.date - now).days) <= DIV_BUFFER_DAYS:
                skip = True
                warning = f"📅 Dividend in {days_to}d - within {DIV_BUFFER_DAYS}d buffer"

        # Sentiment last 72h
        headlines = self._news_headlines(ticker)
        avg_sent = compute_finbert_sentiment_for_news(headlines)

        # Vol spike?
        vspike = realized_vol_spike(ticker)

        # Risk score (0..1)
        risk = 0.0
        if has_evt:
            risk += 0.45
            if e_type == 'earnings' or self._check_regulatory_keywords(next_evt):
                risk += 0.20  # 🆕 Higher weight for regulatory reports
        
        if avg_sent is not None and avg_sent < NEG_SENTIMENT_THRES:
            risk += 0.25
            if not warning:
                warning = f"⚠️ Negative sentiment ({avg_sent:+.2f}) detected in recent news"
        
        if vspike:
            risk += 0.15
            if warning:
                warning += " + Volatility spike detected"
            else:
                warning = "⚠️ Volatility spike detected"
        
        risk = float(max(0.0, min(1.0, risk)))

        # Translate risk -> haircut
        if risk >= 0.8:
            haircut = HAIRCUT_MAX
        elif risk >= 0.5:
            haircut = (HAIRCUT_MAX + HAIRCUT_MIN) / 2.0
        elif risk >= 0.25:
            haircut = HAIRCUT_MIN
        else:
            haircut = 0.0

        # Beta & hedge guidance
        beta = rolling_beta(ticker, XJO_TICKER)
        hedge_ratio = None
        if beta is not None and beta > 0:
            # Simple: $ hedge = beta * $ long to be market-neutral vs index
            hedge_ratio = beta

        return GuardResult(
            ticker=ticker,
            has_upcoming_event=has_evt,
            days_to_event=days_to,
            event_type=e_type,
            event_title=e_title,
            event_url=e_url,
            avg_sentiment_72h=avg_sent,
            vol_spike=vspike,
            risk_score=risk,
            weight_haircut=haircut,
            skip_trading=skip,
            suggested_hedge_beta=beta,
            suggested_hedge_ratio=hedge_ratio,
            warning_message=warning
        )

    def assess_batch(self, tickers: List[str]) -> Dict[str, GuardResult]:
        """
        Assess event risk for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping ticker -> GuardResult
        """
        # Get market regime once for all tickers (performance optimization)
        regime_label, regime_crash_risk = self._get_regime_crash_risk()
        
        logger.info(f"Batch assessment starting for {len(tickers)} tickers")
        logger.info(f"Market Regime: {regime_label}, Crash Risk: {regime_crash_risk:.3f}")
        
        results = {}
        
        for ticker in tickers:
            try:
                results[ticker] = self.assess(ticker)
            except Exception as e:
                logger.error(f"Event risk assessment failed for {ticker}: {e}")
                # Return safe default
                results[ticker] = GuardResult(
                    ticker=ticker,
                    has_upcoming_event=False,
                    days_to_event=None,
                    event_type=None,
                    event_title=None,
                    event_url=None,
                    avg_sentiment_72h=None,
                    vol_spike=False,
                    risk_score=0.0,
                    weight_haircut=0.0,
                    skip_trading=False,
                    suggested_hedge_beta=None,
                    suggested_hedge_ratio=None,
                    warning_message="Assessment failed"
                )
        
        return results


# -----------------------------
# Convenience functions
# -----------------------------
def create_guard_dataframe(results: Dict[str, GuardResult]) -> pd.DataFrame:
    """
    Convert guard results to DataFrame for reporting.
    
    Args:
        results: Dictionary of ticker -> GuardResult
        
    Returns:
        DataFrame with all guard results
    """
    rows = []
    
    for ticker, gr in results.items():
        rows.append({
            'ticker': ticker,
            'has_event': gr.has_upcoming_event,
            'event_type': gr.event_type or '—',
            'event_title': gr.event_title or '—',
            'event_url': gr.event_url or '—',
            'days_to_event': gr.days_to_event if gr.days_to_event is not None else 999,
            'sentiment_72h': gr.avg_sentiment_72h if gr.avg_sentiment_72h is not None else 0.0,
            'vol_spike': gr.vol_spike,
            'risk_score': gr.risk_score,
            'weight_haircut': gr.weight_haircut,
            'skip_trading': gr.skip_trading,
            'hedge_beta': gr.suggested_hedge_beta,
            'hedge_ratio': gr.suggested_hedge_ratio,
            'warning': gr.warning_message or '—'
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by risk score descending
    df = df.sort_values('risk_score', ascending=False)
    
    return df


# -----------------------------
# Main entry point for testing
# -----------------------------
if __name__ == "__main__":
    import sys
    
    # Test with CBA.AX
    test_ticker = sys.argv[1] if len(sys.argv) > 1 else "CBA.AX"
    
    logger.info(f"Testing Event Risk Guard for {test_ticker}")
    
    guard = EventRiskGuard()
    result = guard.assess(test_ticker)
    
    print("\n" + "=" * 60)
    print(f"Event Risk Assessment: {test_ticker}")
    print("=" * 60)
    print(f"Has Upcoming Event: {result.has_upcoming_event}")
    
    if result.has_upcoming_event:
        print(f"Event Type: {result.event_type}")
        print(f"Days to Event: {result.days_to_event}")
        if result.event_title:
            print(f"Event Title: {result.event_title}")
        if result.event_url:
            print(f"Event URL: {result.event_url}")
    
    print(f"\nSentiment (72h): {result.avg_sentiment_72h:+.3f}" if result.avg_sentiment_72h else "\nSentiment: N/A")
    print(f"Volatility Spike: {'YES' if result.vol_spike else 'NO'}")
    print(f"\nRisk Score: {result.risk_score:.2f} / 1.00")
    print(f"Weight Haircut: {result.weight_haircut*100:.0f}%")
    print(f"Skip Trading: {'YES - SIT OUT' if result.skip_trading else 'NO'}")
    
    if result.suggested_hedge_beta:
        print(f"\nHedge Beta (vs XJO): {result.suggested_hedge_beta:.2f}")
        print(f"Suggested Hedge Ratio: {result.suggested_hedge_ratio:.2f}")
    
    if result.warning_message:
        print(f"\n{result.warning_message}")
    
    print("=" * 60 + "\n")
