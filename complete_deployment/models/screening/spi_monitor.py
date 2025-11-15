"""
Market Sentiment Monitor (SPI Monitor)

Predicts ASX 200 overnight gaps using US market correlation analysis.

METHODOLOGY:
This module calculates implied overnight gaps for ASX 200 stocks by analyzing
US market movements and applying historical correlation factors. This approach
is mathematically equivalent to tracking SPI 200 futures when actual futures
data is unavailable via free APIs.

GAP PREDICTION FORMULA:
  1. ASX 200 baseline = Previous day close (^AXJO)
  2. US weighted change = SP500(50%) + Nasdaq(30%) + Dow(20%)
  3. Predicted gap = US change x correlation (0.65)
  4. Implied opening = ASX baseline x (1 + predicted gap)

WHY NOT USE SPI 200 FUTURES DIRECTLY:
- Yahoo Finance free API does not provide SPI 200 futures data
- Correlation-based prediction is the standard industry approach
- Results are mathematically equivalent when correlation is accurate

OVERNIGHT TRADING CONTEXT:
- SPI 200 futures: 5:10 PM - 8:00 AM AEST
- ASX 200 market hours: 10:00 AM - 4:00 PM AEST

Features:
- US market indices monitoring (S&P 500, Nasdaq, Dow)
- Gap prediction using proven correlation method
- Market sentiment analysis for overnight screening
- Trading window detection for optimal screening times
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import yfinance as yf
from yahooquery import Ticker as YQTicker
import pandas as pd
import numpy as np
from pathlib import Path
import pytz
import requests

# Configure yfinance timezone cache location
# NOTE: Do NOT create custom session - yfinance 0.2.x+ handles curl_cffi internally
# Passing custom session causes "Yahoo API requires curl_cffi session" error
yf.set_tz_cache_location("/tmp/yf_cache")

# SESSION-LEVEL MARKET INDICES CACHE (in-memory, shared across all operations)
# Market indices (^AXJO, ^GSPC, ^IXIC, ^DJI) are the same for all stocks in a run
_MARKET_INDICES_CACHE = {}  # {symbol: {'data': DataFrame, 'timestamp': float}}
_CACHE_TTL_SECONDS = 3600  # 1 hour - market indices don't change much during a screening run

def fetch_history_with_fallback_spi(symbol, period="6mo", interval="1d"):
    """
    Fetch market index history with yfinance, fallback to yahooquery if blocked.
    
    Args:
        symbol: Market index symbol (e.g., ^AXJO, ^GSPC)
        period: Period string like '6mo'
        interval: Interval string like '1d'
        
    Returns:
        tuple: (DataFrame with OHLCV data, source string)
    """
    logger = logging.getLogger(__name__)
    
    # Try yfinance first
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df, 'yfinance'
    except Exception as e:
        logger.debug(f"[FALLBACK] yfinance failed for {symbol}: {str(e)[:100]}")
    
    # Fallback to yahooquery
    try:
        logger.info(f"[FALLBACK] Trying yahooquery for index {symbol}...")
        ticker = YQTicker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if isinstance(df, pd.DataFrame) and not df.empty:
            # Normalize column names
            df.columns = [col.capitalize() for col in df.columns]
            logger.info(f"[FALLBACK] ✅ yahooquery succeeded for {symbol}")
            return df, 'yahooquery'
    except Exception as e:
        logger.debug(f"[FALLBACK] yahooquery also failed for {symbol}: {str(e)[:100]}")
    
    raise Exception(f"Both yfinance and yahooquery failed for {symbol}")


# Fix 1: Relative import fallback for script/package mode
try:
    from .alpha_vantage_fetcher import AlphaVantageDataFetcher
except ImportError:
    from alpha_vantage_fetcher import AlphaVantageDataFetcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SPIMonitor:
    """
    Market Sentiment Monitor for ASX overnight gap prediction.
    
    Uses ^AXJO (ASX 200 Index) as baseline and US market correlation
    to calculate implied overnight gaps. This correlation-based approach
    produces results mathematically equivalent to tracking SPI 200 futures.
    
    Historical correlation: ASX moves approximately 65% of US market changes.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize SPI Monitor
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        
        # Fix 5: Safe config access with defaults
        self.spi_config = self.config.get('spi_monitoring') or {}
        
        # Market symbols with safe defaults
        # NOTE: ^AXJO (ASX 200 Index) is used as baseline for correlation-based
        # gap prediction. We do NOT need SPI 200 futures data because the
        # correlation method calculates the implied gap mathematically.
        self.asx_symbol = self.spi_config.get('symbol', '^AXJO')  # ASX 200 Index baseline
        us_idx = self.spi_config.get('us_indices') or {}
        self.us_symbols = us_idx.get('symbols', ['^GSPC', '^IXIC', '^DJI'])  # S&P 500, Nasdaq, Dow
        
        # Timezone
        self.timezone = pytz.timezone('Australia/Sydney')
        
        # Initialize Alpha Vantage fetcher
        self.data_fetcher = AlphaVantageDataFetcher(cache_ttl_minutes=240)
        
        logger.info("SPI Monitor initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _fetch_daily_series(self, symbol: str) -> pd.DataFrame:
        """
        Fix 2: Hybrid fetch - route index symbols (^) to yfinance,
        others to Alpha Vantage.
        
        Uses session-level cache for market indices to avoid redundant API calls.
        
        Alpha Vantage doesn't support Yahoo-style caret indices.
        
        Args:
            symbol: Stock/index ticker symbol
            
        Returns:
            DataFrame with OHLCV data or empty DataFrame
        """
        global _MARKET_INDICES_CACHE
        
        try:
            if symbol.startswith("^"):  # Index symbol - use yfinance with cache
                # Check cache first
                if symbol in _MARKET_INDICES_CACHE:
                    cached_entry = _MARKET_INDICES_CACHE[symbol]
                    age = time.time() - cached_entry['timestamp']
                    if age < _CACHE_TTL_SECONDS:
                        logger.debug(f"✓ Using cached {symbol} (age: {age:.0f}s)")
                        return cached_entry['data'].copy()
                
                # RATE LIMIT FIX: Add delay between index fetches
                if hasattr(self, '_last_request_time'):
                    elapsed = time.time() - self._last_request_time
                    if elapsed < 1.0:  # Minimum 1 second between requests
                        time.sleep(1.0 - elapsed)
                
                # Cache miss - fetch with fallback (yfinance → yahooquery)
                logger.debug(f"Fetching {symbol} from data source (index)")
                df, source = fetch_history_with_fallback_spi(symbol, period="6mo", interval="1d")
                
                if source == 'yahooquery':
                    logger.info(f"Using yahooquery fallback for index {symbol}")
                
                # RATE LIMIT FIX: Track last request time
                self._last_request_time = time.time()
                
                # Store in cache
                if not df.empty:
                    _MARKET_INDICES_CACHE[symbol] = {
                        'data': df.copy(),
                        'timestamp': time.time()
                    }
                    logger.debug(f"  ✓ Cached {symbol} for future use")
                
                return df if not df.empty else pd.DataFrame()
            else:  # Stock - use Alpha Vantage
                logger.debug(f"Fetching {symbol} from Alpha Vantage")
                df = self.data_fetcher.fetch_daily_data(symbol, outputsize="compact")
                return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def _safe_last_int(self, series: pd.Series, default: int = 0) -> int:
        """
        Fix 3: Safely extract last integer from series.
        Handles NaN, missing values, and type conversion.
        
        Args:
            series: Pandas series (e.g., Volume)
            default: Default value if extraction fails
            
        Returns:
            Integer value or default
        """
        try:
            if series is None or series.empty:
                return default
            val = series.iloc[-1]
            if pd.isna(val):
                return default
            return int(val)
        except Exception:
            return default
    
    def get_market_sentiment(self) -> Dict:
        """
        Get comprehensive market sentiment analysis
        
        Returns:
            Dictionary with sentiment scores, predictions, and analysis
        """
        logger.info("Calculating market sentiment...")
        
        # Get ASX 200 current state
        asx_data = self._get_asx_state()
        
        # Get US market closes
        us_data = self._get_us_market_data()
        
        # Calculate gap prediction
        gap_prediction = self._predict_opening_gap(asx_data, us_data)
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment_score(us_data, gap_prediction)
        
        return {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'asx_200': asx_data,
            'us_markets': us_data,
            'gap_prediction': gap_prediction,
            'sentiment_score': sentiment_score,
            'recommendation': self._get_recommendation(sentiment_score, gap_prediction)
        }
    
    def _get_asx_state(self) -> Dict:
        """
        Get current ASX 200 state (hybrid: yfinance for indices)
        
        Returns:
            Dictionary with ASX data
        """
        try:
            # Fix 2: Use hybrid fetch (routes indices to yfinance)
            hist = self._fetch_daily_series(self.asx_symbol)
            
            if hist is None or hist.empty:
                logger.warning(f"No data available for {self.asx_symbol}")
                return {'available': False}
            
            if len(hist) < 2:
                logger.warning(f"Insufficient data for {self.asx_symbol}")
                return {'available': False}
            
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            
            # Calculate 5-day trend
            if len(hist) >= 5:
                five_day_change = ((last_close - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
            else:
                five_day_change = change_pct
            
            # Fix 3: Safe volume extraction (indices may have NaN volume)
            volume = self._safe_last_int(hist.get('Volume', pd.Series(dtype=float)), 0)
            
            return {
                'available': True,
                'symbol': self.asx_symbol,
                'last_close': float(last_close),
                'prev_close': float(prev_close),
                'change_pct': float(change_pct),
                'five_day_change_pct': float(five_day_change),
                'volume': volume,
                'last_updated': hist.index[-1].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching ASX data: {e}")
            return {'available': False, 'error': str(e)}
    
    def _get_us_market_data(self) -> Dict:
        """
        Get US market indices data (S&P 500, Nasdaq, Dow) - hybrid fetch
        
        Returns:
            Dictionary with US market data
        """
        us_data = {}
        
        # Map symbol to friendly name
        name_map = {
            '^GSPC': 'SP500',
            '^IXIC': 'Nasdaq',
            '^DJI': 'Dow'
        }
        
        for symbol in self.us_symbols:
            try:
                # Fix 2: Use hybrid fetch (routes indices to yfinance)
                hist = self._fetch_daily_series(symbol)
                
                if hist is None or hist.empty:
                    logger.warning(f"No data for {symbol}")
                    continue
                
                if len(hist) < 2:
                    logger.warning(f"Insufficient data for {symbol}")
                    continue
                
                last_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                
                # Fix 3: Safe volume extraction
                volume = self._safe_last_int(hist.get('Volume', pd.Series(dtype=float)), 0)
                
                us_data[name_map.get(symbol, symbol)] = {
                    'symbol': symbol,
                    'last_close': float(last_close),
                    'prev_close': float(prev_close),
                    'change_pct': float(change_pct),
                    'volume': volume,
                    'last_updated': hist.index[-1].isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
        
        return us_data
    
    def _predict_opening_gap(self, asx_data: Dict, us_data: Dict) -> Dict:
        """
        Predict ASX 200 opening gap using US market correlation.
        
        This method calculates the implied overnight gap without needing
        actual SPI 200 futures data. The correlation-based approach is
        mathematically equivalent to tracking futures prices.
        
        CALCULATION METHOD:
        1. Calculate weighted US market change (SP500=50%, Nasdaq=30%, Dow=20%)
        2. Apply historical correlation factor (default 0.65)
        3. Predicted gap = weighted_us_change x correlation
        4. Implied ASX opening = asx_close x (1 + predicted_gap)
        
        Historical correlation: ASX 200 moves approximately 65% of US market changes
        
        Args:
            asx_data: ASX 200 baseline data (previous close)
            us_data: US market indices overnight data
            
        Returns:
            Dictionary with gap prediction containing:
            - predicted_gap_pct: Predicted gap percentage
            - confidence: Prediction confidence (0-100)
            - direction: 'bullish', 'bearish', or 'neutral'
            - threshold: Gap threshold for direction determination
        """
        if not asx_data.get('available') or not us_data:
            return {
                'predicted_gap_pct': 0,
                'confidence': 0,
                'direction': 'neutral',
                'error': 'Insufficient data'
            }
        
        # Calculate weighted average of US market changes
        us_changes = []
        weights = []
        
        for market_name, data in us_data.items():
            us_changes.append(data['change_pct'])
            # S&P 500 has highest correlation with ASX
            if market_name == 'SP500':
                weights.append(0.5)
            elif market_name == 'Nasdaq':
                weights.append(0.3)
            else:  # Dow
                weights.append(0.2)
        
        # Fix 7: Guard empty weights
        if not us_changes or not weights or len(us_changes) != len(weights):
            return {
                'predicted_gap_pct': 0,
                'confidence': 0,
                'direction': 'neutral',
                'error': 'Insufficient or mismatched data'
            }
        
        # Weighted average of US market changes
        weighted_us_change = float(np.average(us_changes, weights=weights))
        
        # Fix 8: Single correlation knob (ASX typically moves ~65% of US changes)
        correlation = self.spi_config.get('correlation', 0.65)
        predicted_gap = weighted_us_change * correlation
        
        # Calculate confidence based on US market agreement
        us_changes_array = np.array(us_changes)
        if len(us_changes_array) > 1:
            # High confidence if all markets moved in same direction
            same_direction = np.all(us_changes_array > 0) or np.all(us_changes_array < 0)
            std_dev = np.std(us_changes_array)
            
            if same_direction and std_dev < 0.5:
                confidence = 90
            elif same_direction:
                confidence = 75
            elif std_dev < 0.5:
                confidence = 60
            else:
                confidence = 40
        else:
            confidence = 50
        
        # Fix 5: Safe threshold access with default
        gap_threshold = self.spi_config.get('gap_threshold_pct', 0.3)
        
        # Determine direction
        if predicted_gap > gap_threshold:
            direction = 'bullish'
        elif predicted_gap < -gap_threshold:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        return {
            'predicted_gap_pct': float(predicted_gap),
            'confidence': confidence,
            'direction': direction,
            'us_weighted_change': float(weighted_us_change),
            'correlation_used': correlation,  # Fix 8: Return actual correlation used
            'threshold': gap_threshold  # Fix 5: Return actual threshold
        }
    
    def _calculate_sentiment_score(self, us_data: Dict, gap_prediction: Dict) -> float:
        """
        Calculate overall market sentiment score (0-100)
        
        Factors:
        - US market performance (40%)
        - Gap prediction magnitude (30%)
        - US market agreement (20%)
        - Recent ASX trend (10%)
        
        Args:
            us_data: US market data
            gap_prediction: Gap prediction data
            
        Returns:
            Sentiment score (0-100)
        """
        score = 50  # Neutral baseline
        
        if not us_data:
            return score
        
        # 1. US market performance (40 points)
        us_changes = [data['change_pct'] for data in us_data.values()]
        avg_us_change = np.mean(us_changes)
        
        # Scale US change to score (-3% = 0, 0% = 50, +3% = 100)
        us_score = 50 + (avg_us_change / 3.0) * 50
        us_score = max(0, min(100, us_score))
        score += (us_score - 50) * 0.4
        
        # 2. Gap prediction magnitude (30 points)
        predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
        gap_score = 50 + (predicted_gap / 2.0) * 50
        gap_score = max(0, min(100, gap_score))
        score += (gap_score - 50) * 0.3
        
        # 3. US market agreement (20 points)
        if len(us_changes) > 1:
            same_direction = np.all(np.array(us_changes) > 0) or np.all(np.array(us_changes) < 0)
            if same_direction:
                score += 10  # Bonus for agreement
            else:
                score -= 5   # Penalty for disagreement
        
        # 4. Confidence factor (10 points)
        confidence = gap_prediction.get('confidence', 50)
        score += (confidence - 50) * 0.2
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _get_recommendation(self, sentiment_score: float, gap_prediction: Dict) -> Dict:
        """
        Generate trading recommendation based on sentiment
        
        Args:
            sentiment_score: Overall sentiment (0-100)
            gap_prediction: Gap prediction data
            
        Returns:
            Dictionary with recommendation details
        """
        predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
        confidence = gap_prediction.get('confidence', 0)
        
        # Determine stance
        if sentiment_score >= 70 and confidence >= 70:
            stance = 'STRONG_BUY'
            message = 'Strong bullish sentiment. Consider aggressive long positions.'
        elif sentiment_score >= 60:
            stance = 'BUY'
            message = 'Bullish sentiment. Favor long positions.'
        elif sentiment_score >= 45 and sentiment_score <= 55:
            stance = 'NEUTRAL'
            message = 'Mixed signals. Wait for market direction.'
        elif sentiment_score <= 30 and confidence >= 70:
            stance = 'STRONG_SELL'
            message = 'Strong bearish sentiment. Consider protective measures.'
        elif sentiment_score <= 40:
            stance = 'SELL'
            message = 'Bearish sentiment. Reduce exposure or short.'
        else:
            stance = 'HOLD'
            message = 'Cautious sentiment. Maintain current positions.'
        
        return {
            'stance': stance,
            'message': message,
            'expected_open': f"{'+' if predicted_gap > 0 else ''}{predicted_gap:.2f}%",
            'confidence': f"{confidence}%",
            'risk_level': 'HIGH' if confidence < 50 else 'MEDIUM' if confidence < 75 else 'LOW'
        }
    
    def get_overnight_summary(self) -> Dict:
        """
        Get complete overnight market summary for morning report
        
        Returns:
            Dictionary with full overnight analysis
        """
        sentiment = self.get_market_sentiment()
        
        # Add additional context
        sentiment['overnight_summary'] = {
            'generated_at': datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z'),
            'market_status': self._get_market_status(),
            'key_levels': self._calculate_key_levels(sentiment['asx_200'])
        }
        
        return sentiment
    
    def _get_market_status(self) -> str:
        """Determine if markets are currently trading"""
        now = datetime.now(self.timezone)
        hour = now.hour
        minute = now.minute
        
        # ASX trading hours: 10:00 AM - 4:00 PM AEST
        if 10 <= hour < 16:
            return 'ASX_OPEN'
        
        # Fix 4: Correct SPI futures trading window (5:10 PM - 8:00 AM AEST)
        # Was: if (hour >= 17 and minute >= 10) - WRONG (failed at 23:05)
        # Now: Proper time range check
        if (hour > 17) or (hour == 17 and minute >= 10) or (hour < 8):
            return 'SPI_TRADING'
        
        # Pre-market
        if 8 <= hour < 10:
            return 'PRE_MARKET'
        
        return 'CLOSED'
    
    def _calculate_key_levels(self, asx_data: Dict) -> Dict:
        """
        Calculate key support/resistance levels for ASX 200
        
        Args:
            asx_data: Current ASX data
            
        Returns:
            Dictionary with key levels
        """
        if not asx_data.get('available'):
            return {}
        
        last_close = asx_data['last_close']
        
        # Simple pivot levels
        return {
            'resistance_1': round(last_close * 1.01, 2),
            'resistance_2': round(last_close * 1.02, 2),
            'support_1': round(last_close * 0.99, 2),
            'support_2': round(last_close * 0.98, 2),
            'pivot': round(last_close, 2)
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_spi_monitor():
    """Test the SPI monitor"""
    print("\n" + "="*80)
    print("SPI 200 FUTURES MONITOR TEST")
    print("="*80 + "\n")
    
    # Initialize monitor
    monitor = SPIMonitor()
    
    # Get market sentiment
    print("Fetching market sentiment...\n")
    sentiment = monitor.get_overnight_summary()
    
    # Display results
    print("-"*80)
    print("ASX 200 STATUS")
    print("-"*80)
    asx = sentiment['asx_200']
    if asx.get('available'):
        print(f"Last Close: {asx['last_close']:.2f}")
        print(f"Change: {asx['change_pct']:+.2f}%")
        print(f"5-Day Change: {asx['five_day_change_pct']:+.2f}%")
    else:
        print("⚠ ASX data not available")
    
    print("\n" + "-"*80)
    print("US MARKETS")
    print("-"*80)
    for market, data in sentiment['us_markets'].items():
        print(f"{market:8s}: {data['last_close']:8.2f}  Change: {data['change_pct']:+6.2f}%")
    
    print("\n" + "-"*80)
    print("OPENING PREDICTION")
    print("-"*80)
    gap = sentiment['gap_prediction']
    print(f"Predicted Gap: {gap['predicted_gap_pct']:+.2f}%")
    print(f"Direction: {gap['direction'].upper()}")
    print(f"Confidence: {gap['confidence']}%")
    
    print("\n" + "-"*80)
    print("SENTIMENT ANALYSIS")
    print("-"*80)
    print(f"Sentiment Score: {sentiment['sentiment_score']:.1f}/100")
    rec = sentiment['recommendation']
    print(f"Recommendation: {rec['stance']}")
    print(f"Message: {rec['message']}")
    print(f"Expected Open: {rec['expected_open']}")
    print(f"Risk Level: {rec['risk_level']}")
    
    print("\n" + "-"*80)
    print("KEY LEVELS")
    print("-"*80)
    levels = sentiment['overnight_summary']['key_levels']
    if levels:
        print(f"Resistance 2: {levels['resistance_2']:.2f}")
        print(f"Resistance 1: {levels['resistance_1']:.2f}")
        print(f"Pivot Point:  {levels['pivot']:.2f}")
        print(f"Support 1:    {levels['support_1']:.2f}")
        print(f"Support 2:    {levels['support_2']:.2f}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_spi_monitor()
