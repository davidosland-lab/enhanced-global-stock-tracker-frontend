"""
US Market Futures Proxy Module (Advanced)

Provides synthetic US market futures estimates using:
- NQ=F (E-mini NASDAQ-100 futures) - PRIMARY for tech-heavy stocks
- ES=F (E-mini S&P 500 futures) - PRIMARY for broad market
- ^VIX (Volatility Index)
- DX-Y.NYB (US Dollar Index)
- CL=F (WTI Crude Oil)
- GC=F (Gold futures)

Version: 1.0.0
Date: 2026-03-03
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from yahooquery import Ticker
import pytz

# Setup logging
logger = logging.getLogger(__name__)


class USProxyConfig:
    """Configuration for US market proxy calculation"""
    
    def __init__(self):
        # Data fetching
        self.interval = "5m"  # 5-minute intraday
        self.lookback_intraday = "2d"  # Last 2 days for intraday
        self.z_lookback_days = 60  # 60 days for Z-score calculation
        
        # Ticker symbols
        self.ticker_nq = "NQ=F"  # E-mini NASDAQ-100 futures (PRIMARY for tech)
        self.ticker_es = "ES=F"  # E-mini S&P 500 futures (PRIMARY for broad market)
        self.ticker_vix = "^VIX"  # Volatility Index
        self.ticker_dollar = "DX-Y.NYB"  # US Dollar Index
        self.ticker_oil = "CL=F"  # WTI Crude Oil
        self.ticker_gold = "GC=F"  # Gold futures (safe haven)
        
        # Weights - balanced between NASDAQ and S&P 500
        self.w_nq = 0.40  # NASDAQ futures (tech-heavy)
        self.w_es = 0.40  # S&P 500 futures (broad market)
        self.w_vix = -0.15  # Inverse volatility
        self.w_dollar = -0.05  # Inverse (strong dollar hurts US stocks slightly)
        self.w_oil = 0.05  # Oil (energy sector)
        self.w_gold = -0.05  # Inverse (gold up = risk-off)
        
        # Regime detection thresholds
        self.vix_jump_threshold = 3.0  # % VIX jump = risk-off
        self.proxy_z_risk_off_threshold = -1.0  # Z-score < -1.0 = risk-off
        
        # Caps and limits
        self.max_proxy_move = 4.0  # Cap proxy move at +/-4.0% (US markets more volatile)
        self.max_z_score = 4.0  # Cap Z-score at +/-4.0
        
        # Confidence parameters
        self.confidence_base = 0.75  # Higher base (direct futures)
        self.confidence_min = 0.40
        self.confidence_max = 0.95


class USProxy:
    """
    Advanced US market futures proxy calculator
    
    Uses NASDAQ (NQ=F) and S&P 500 (ES=F) futures as primary sources.
    """
    
    def __init__(self, config: Optional[USProxyConfig] = None):
        """
        Initialize US Proxy
        
        Args:
            config: Optional configuration object
        """
        self.config = config or USProxyConfig()
        self.timezone_ny = pytz.timezone('America/New_York')
        logger.info("US Market Proxy initialized with advanced configuration")
    
    def _safe_last(self, series: pd.Series) -> Optional[float]:
        """Safely get last value from pandas Series"""
        if series is None or len(series) == 0:
            return None
        val = series.iloc[-1]
        if pd.isna(val):
            return None
        return float(val)
    
    def _pct_change(self, current: Optional[float], previous: Optional[float]) -> Optional[float]:
        """Calculate percentage change"""
        if current is None or previous is None or previous == 0:
            return None
        return ((current - previous) / abs(previous)) * 100.0
    
    def _fetch_intraday_close(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Fetch current and previous close for a symbol using intraday data
        
        Returns:
            Tuple of (current_close, previous_close)
        """
        try:
            ticker = Ticker(symbol)
            hist = ticker.history(period=self.config.lookback_intraday, 
                                 interval=self.config.interval)
            
            if hist is None or len(hist) == 0:
                logger.warning(f"No intraday data for {symbol}")
                return None, None
            
            # Get last two closes
            closes = hist['close'].dropna()
            if len(closes) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return None, None
            
            current_close = float(closes.iloc[-1])
            previous_close = float(closes.iloc[-2])
            
            return current_close, previous_close
            
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")
            return None, None
    
    def _realized_vol_from_returns(self, returns: pd.Series, window: int = 20) -> float:
        """Calculate realized volatility from returns"""
        if len(returns) < window:
            window = max(5, len(returns))
        return returns.rolling(window=window).std().iloc[-1] * np.sqrt(252) * 100
    
    def _compute_vol_gate(self, current_vol: float, historical_avg: float) -> float:
        """
        Compute volatility gate multiplier
        
        High vol -> reduce confidence, apply damping
        """
        if historical_avg == 0:
            return 1.0
        
        vol_ratio = current_vol / historical_avg
        
        if vol_ratio > 2.0:
            # Extreme volatility -> damp by 50%
            return 0.5
        elif vol_ratio > 1.5:
            # High volatility -> damp by 25%
            return 0.75
        elif vol_ratio < 0.5:
            # Low volatility -> amplify by 10%
            return 1.1
        else:
            # Normal volatility
            return 1.0
    
    def _weighted_proxy_move(self, 
                            nq_pct: Optional[float],
                            es_pct: Optional[float],
                            vix_pct: Optional[float],
                            dollar_pct: Optional[float],
                            oil_pct: Optional[float],
                            gold_pct: Optional[float]) -> Optional[float]:
        """
        Calculate weighted proxy move from all drivers
        
        Both NQ=F and ES=F are primary sources (direct futures)
        
        Returns:
            Weighted percentage move (uncapped)
        """
        components = []
        
        # Primary drivers: NQ and ES futures
        if nq_pct is not None:
            components.append(self.config.w_nq * nq_pct)
        if es_pct is not None:
            components.append(self.config.w_es * es_pct)
        
        # Secondary drivers: volatility, dollar, commodities
        if vix_pct is not None:
            components.append(self.config.w_vix * vix_pct)
        if dollar_pct is not None:
            components.append(self.config.w_dollar * dollar_pct)
        if oil_pct is not None:
            components.append(self.config.w_oil * oil_pct)
        if gold_pct is not None:
            components.append(self.config.w_gold * gold_pct)
        
        if not components:
            return None
        
        return sum(components)
    
    def _vol_adjust(self, proxy_move: float, vol_gate: float) -> float:
        """Apply volatility adjustment to proxy move"""
        adjusted = proxy_move * vol_gate
        
        # Apply caps
        if adjusted > self.config.max_proxy_move:
            adjusted = self.config.max_proxy_move
        elif adjusted < -self.config.max_proxy_move:
            adjusted = -self.config.max_proxy_move
        
        return adjusted
    
    def _compute_z_score(self, current_move: float, symbol: str = "ES=F") -> Optional[float]:
        """
        Compute Z-score of current move vs. 60-day distribution
        
        Args:
            current_move: Current percentage move
            symbol: Symbol to use for historical data (default ES=F)
        
        Returns:
            Z-score or None if insufficient data
        """
        try:
            ticker = Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.config.z_lookback_days)
            
            hist = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                end=end_date.strftime('%Y-%m-%d'),
                                interval='1d')
            
            if hist is None or len(hist) < 20:
                # Fallback to S&P 500 index
                if symbol != "^GSPC":
                    logger.warning(f"Insufficient historical data for {symbol}, trying ^GSPC")
                    return self._compute_z_score(current_move, symbol="^GSPC")
                logger.warning(f"Insufficient historical data for Z-score calculation")
                return None
            
            # Calculate daily returns
            returns = hist['close'].pct_change().dropna() * 100.0
            
            if len(returns) < 20:
                return None
            
            mean_return = returns.mean()
            std_return = returns.std()
            
            if std_return == 0:
                return None
            
            z_score = (current_move - mean_return) / std_return
            
            # Apply cap
            if z_score > self.config.max_z_score:
                z_score = self.config.max_z_score
            elif z_score < -self.config.max_z_score:
                z_score = -self.config.max_z_score
            
            return z_score
            
        except Exception as e:
            logger.warning(f"Failed to compute Z-score: {e}")
            return None
    
    def _determine_regime(self, 
                         vix_pct: Optional[float],
                         proxy_z: Optional[float],
                         proxy_move: float,
                         nq_available: bool,
                         es_available: bool) -> Tuple[str, float, float]:
        """
        Determine market regime and calculate confidence + risk multiplier
        
        Returns:
            Tuple of (regime, confidence, risk_multiplier)
        """
        regime = "neutral"
        confidence = self.config.confidence_base
        risk_multiplier = 1.0
        
        # Boost confidence if both primary futures available
        if nq_available and es_available:
            confidence = min(self.config.confidence_max, confidence + 0.15)
        elif nq_available or es_available:
            confidence = min(self.config.confidence_max, confidence + 0.10)
        
        # Risk-off indicators
        risk_off_signals = 0
        
        if vix_pct is not None and vix_pct > self.config.vix_jump_threshold:
            risk_off_signals += 1
            regime = "risk_off"
        
        if proxy_z is not None and proxy_z < self.config.proxy_z_risk_off_threshold:
            risk_off_signals += 1
            regime = "risk_off"
        
        if abs(proxy_move) > 2.5:
            risk_off_signals += 1
        
        # Risk-on indicators
        if vix_pct is not None and vix_pct < -2.0:
            regime = "risk_on"
            confidence = min(self.config.confidence_max, confidence + 0.10)
        
        # Adjust confidence based on risk-off signals
        if risk_off_signals >= 2:
            regime = "risk_off"
            confidence = max(self.config.confidence_min, confidence - 0.20)
            risk_multiplier = 1.3  # Increase risk weighting
        elif risk_off_signals == 1:
            confidence = max(self.config.confidence_min, confidence - 0.10)
            risk_multiplier = 1.15
        
        # Boost confidence if Z-score is moderate
        if proxy_z is not None and abs(proxy_z) < 1.0:
            confidence = min(self.config.confidence_max, confidence + 0.05)
        
        return regime, confidence, risk_multiplier
    
    def compute_us_proxy(self) -> Dict:
        """
        Compute synthetic US market futures proxy
        
        Returns:
            Dictionary with:
            - asof: timestamp
            - us_proxy_pct: estimated US market move %
            - us_proxy_z: Z-score
            - regime: market regime (risk_on/risk_off/neutral)
            - confidence: confidence level (0-1)
            - risk_multiplier: risk adjustment factor
            - drivers: breakdown of component moves
            - meta: configuration metadata
        """
        logger.info("Computing US market proxy...")
        
        # Fetch intraday closes for all drivers
        nq_curr, nq_prev = self._fetch_intraday_close(self.config.ticker_nq)
        es_curr, es_prev = self._fetch_intraday_close(self.config.ticker_es)
        vix_curr, vix_prev = self._fetch_intraday_close(self.config.ticker_vix)
        dollar_curr, dollar_prev = self._fetch_intraday_close(self.config.ticker_dollar)
        oil_curr, oil_prev = self._fetch_intraday_close(self.config.ticker_oil)
        gold_curr, gold_prev = self._fetch_intraday_close(self.config.ticker_gold)
        
        # Calculate percentage moves
        nq_pct = self._pct_change(nq_curr, nq_prev)
        es_pct = self._pct_change(es_curr, es_prev)
        vix_pct = self._pct_change(vix_curr, vix_prev)
        dollar_pct = self._pct_change(dollar_curr, dollar_prev)
        oil_pct = self._pct_change(oil_curr, oil_prev)
        gold_pct = self._pct_change(gold_curr, gold_prev)
        
        # Track if primary futures available
        nq_available = nq_pct is not None
        es_available = es_pct is not None
        
        # Calculate weighted proxy move
        proxy_move = self._weighted_proxy_move(nq_pct, es_pct, vix_pct, 
                                              dollar_pct, oil_pct, gold_pct)
        
        if proxy_move is None:
            logger.error("Failed to compute proxy move - insufficient data")
            return {
                'asof': datetime.now(self.timezone_ny).isoformat(),
                'us_proxy_pct': None,
                'us_proxy_z': None,
                'regime': 'unknown',
                'confidence': 0.0,
                'risk_multiplier': 1.0,
                'drivers': {},
                'meta': {'error': 'Insufficient data'},
                'available': False
            }
        
        # Calculate volatility gate (using ES=F)
        try:
            ticker_es = Ticker(self.config.ticker_es)
            hist_es = ticker_es.history(period='60d', interval='1d')
            if hist_es is not None and len(hist_es) >= 20:
                returns = hist_es['close'].pct_change().dropna() * 100.0
                current_vol = self._realized_vol_from_returns(returns, window=20)
                historical_avg = returns.rolling(window=60).std().mean() * np.sqrt(252) * 100
                vol_gate = self._compute_vol_gate(current_vol, historical_avg)
            else:
                vol_gate = 1.0
        except Exception as e:
            logger.warning(f"Failed to compute volatility gate: {e}")
            vol_gate = 1.0
        
        # Apply volatility adjustment
        proxy_move_adj = self._vol_adjust(proxy_move, vol_gate)
        
        # Compute Z-score
        proxy_z = self._compute_z_score(proxy_move_adj, symbol=self.config.ticker_es)
        
        # Determine regime
        regime, confidence, risk_multiplier = self._determine_regime(vix_pct, proxy_z, proxy_move_adj,
                                                                     nq_available, es_available)
        
        # Build result
        result = {
            'asof': datetime.now(self.timezone_ny).isoformat(),
            'us_proxy_pct': round(proxy_move_adj, 2),
            'us_proxy_z': round(proxy_z, 2) if proxy_z is not None else None,
            'regime': regime,
            'confidence': round(confidence, 2),
            'risk_multiplier': round(risk_multiplier, 2),
            'drivers': {
                'nq_pct': round(nq_pct, 2) if nq_pct is not None else None,
                'es_pct': round(es_pct, 2) if es_pct is not None else None,
                'vix_pct': round(vix_pct, 2) if vix_pct is not None else None,
                'dollar_pct': round(dollar_pct, 2) if dollar_pct is not None else None,
                'oil_pct': round(oil_pct, 2) if oil_pct is not None else None,
                'gold_pct': round(gold_pct, 2) if gold_pct is not None else None,
                'vol_gate': round(vol_gate, 2)
            },
            'meta': {
                'interval': self.config.interval,
                'lookback_intraday': self.config.lookback_intraday,
                'z_lookback_days': self.config.z_lookback_days,
                'nq_available': nq_available,
                'es_available': es_available,
                'primary_sources': f"NQ={nq_available}, ES={es_available}",
                'weights': {
                    'nq': self.config.w_nq,
                    'es': self.config.w_es,
                    'vix': self.config.w_vix,
                    'dollar': self.config.w_dollar,
                    'oil': self.config.w_oil,
                    'gold': self.config.w_gold
                }
            },
            'available': True,
            'source': 'us_proxy_advanced'
        }
        
        sources_str = f"NQ={'[OK]' if nq_available else '[X]'}, ES={'[OK]' if es_available else '[X]'}"
        z_str = f"{proxy_z:.2f}" if proxy_z is not None else "N/A"
        logger.info(f"US Market Proxy: {proxy_move_adj:.2f}% (Z={z_str}, "
                   f"Regime={regime}, Confidence={confidence:.0%}, Sources={sources_str})")
        
        return result


if __name__ == "__main__":
    # Test the proxy
    proxy = USProxy()
    result = proxy.compute_us_proxy()
    print("\n" + "="*80)
    print("US MARKET PROXY TEST RESULTS")
    print("="*80)
    print(f"\nTimestamp: {result['asof']}")
    print(f"US Market Proxy Move: {result['us_proxy_pct']}%")
    print(f"Z-Score: {result['us_proxy_z']}")
    print(f"Regime: {result['regime']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Risk Multiplier: {result['risk_multiplier']}")
    print(f"Primary Sources: {result['meta']['primary_sources']}")
    print("\nDrivers:")
    for key, val in result['drivers'].items():
        if val is not None:
            print(f"  {key}: {val}%")
    print("="*80 + "\n")
