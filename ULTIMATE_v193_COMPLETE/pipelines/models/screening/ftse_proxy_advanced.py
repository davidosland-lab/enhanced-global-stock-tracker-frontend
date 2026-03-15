"""
FTSE 100 Futures Proxy Module (Advanced)

Provides a synthetic FTSE 100 futures estimate using:
- Z=F (FTSE 100 futures) - PRIMARY direct futures
- ES=F (E-mini S&P 500 futures) - global correlation
- ^VIX (US Volatility Index)
- ^VFTSE (UK Volatility Index)
- GBPUSD=X (British Pound)
- BZ=F (Brent Crude) - UK energy sector exposure

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


class FTSEProxyConfig:
    """Configuration for FTSE proxy calculation"""
    
    def __init__(self):
        # Data fetching
        self.interval = "5m"  # 5-minute intraday
        self.lookback_intraday = "2d"  # Last 2 days for intraday
        self.z_lookback_days = 60  # 60 days for Z-score calculation
        
        # Ticker symbols
        self.ticker_ftse_futures = "Z=F"  # FTSE 100 futures (PRIMARY)
        self.ticker_es = "ES=F"  # E-mini S&P 500 futures (global correlation)
        self.ticker_vix = "^VIX"  # US Volatility Index
        self.ticker_vftse = "^VFTSE"  # UK Volatility Index
        self.ticker_gbp = "GBPUSD=X"  # British Pound
        self.ticker_brent = "BZ=F"  # Brent Crude (UK energy sector)
        
        # Weights (if Z=F is available, use it heavily; otherwise blend)
        self.w_ftse_futures = 0.85  # FTSE futures primary (if available)
        self.w_es = 0.25  # E-mini S&P 500 (global correlation)
        self.w_vix = -0.10  # Inverse volatility
        self.w_vftse = -0.10  # Inverse UK volatility
        self.w_gbp = -0.15  # Inverse (strong GBP hurts FTSE exporters)
        self.w_brent = 0.10  # Brent crude (energy sector)
        
        # Regime detection thresholds
        self.vix_jump_threshold = 3.0  # % VIX jump = risk-off
        self.vftse_jump_threshold = 3.0  # % VFTSE jump = risk-off
        self.proxy_z_risk_off_threshold = -1.0  # Z-score < -1.0 = risk-off
        
        # Caps and limits
        self.max_proxy_move = 3.5  # Cap proxy move at +/-3.5%
        self.max_z_score = 4.0  # Cap Z-score at +/-4.0
        
        # Confidence parameters
        self.confidence_base = 0.70
        self.confidence_min = 0.35
        self.confidence_max = 0.90


class FTSEProxy:
    """
    Advanced FTSE 100 futures proxy calculator
    
    Uses FTSE 100 futures (Z=F) as primary source, with global market
    drivers as backup/confirmation.
    """
    
    def __init__(self, config: Optional[FTSEProxyConfig] = None):
        """
        Initialize FTSE Proxy
        
        Args:
            config: Optional configuration object
        """
        self.config = config or FTSEProxyConfig()
        self.timezone_london = pytz.timezone('Europe/London')
        logger.info("FTSE Proxy initialized with advanced configuration")
    
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
                            ftse_futures_pct: Optional[float],
                            es_pct: Optional[float],
                            vix_pct: Optional[float],
                            vftse_pct: Optional[float],
                            gbp_pct: Optional[float],
                            brent_pct: Optional[float]) -> Optional[float]:
        """
        Calculate weighted proxy move from all drivers
        
        Priority: If FTSE futures (Z=F) available, use it heavily (85%)
        Otherwise blend other drivers
        
        Returns:
            Weighted percentage move (uncapped)
        """
        # If FTSE futures available, use it as primary driver
        if ftse_futures_pct is not None:
            components = [self.config.w_ftse_futures * ftse_futures_pct]
            
            # Add other drivers as confirmation/adjustment (smaller weights)
            if es_pct is not None:
                components.append(0.10 * es_pct)  # Reduced from 0.25
            if vix_pct is not None:
                components.append(self.config.w_vix * vix_pct)
            if vftse_pct is not None:
                components.append(self.config.w_vftse * vftse_pct)
            if gbp_pct is not None:
                components.append(self.config.w_gbp * gbp_pct)
            if brent_pct is not None:
                components.append(self.config.w_brent * brent_pct)
        else:
            # Fallback: use blended approach without direct futures
            logger.warning("FTSE futures (Z=F) unavailable - using blended proxy")
            components = []
            
            if es_pct is not None:
                components.append(self.config.w_es * es_pct)
            if vix_pct is not None:
                components.append(self.config.w_vix * vix_pct)
            if vftse_pct is not None:
                components.append(self.config.w_vftse * vftse_pct)
            if gbp_pct is not None:
                components.append(self.config.w_gbp * gbp_pct)
            if brent_pct is not None:
                components.append(self.config.w_brent * brent_pct)
        
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
    
    def _compute_z_score(self, current_move: float, symbol: str = "Z=F") -> Optional[float]:
        """
        Compute Z-score of current move vs. 60-day distribution
        
        Args:
            current_move: Current percentage move
            symbol: Symbol to use for historical data (default Z=F, fallback ^FTSE)
        
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
                # Fallback to FTSE 100 index
                if symbol != "^FTSE":
                    logger.warning(f"Insufficient historical data for {symbol}, trying ^FTSE")
                    return self._compute_z_score(current_move, symbol="^FTSE")
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
                         vftse_pct: Optional[float],
                         proxy_z: Optional[float],
                         proxy_move: float,
                         ftse_futures_available: bool) -> Tuple[str, float, float]:
        """
        Determine market regime and calculate confidence + risk multiplier
        
        Returns:
            Tuple of (regime, confidence, risk_multiplier)
        """
        regime = "neutral"
        confidence = self.config.confidence_base
        risk_multiplier = 1.0
        
        # Boost confidence if using direct FTSE futures
        if ftse_futures_available:
            confidence = min(self.config.confidence_max, confidence + 0.15)
        
        # Risk-off indicators
        risk_off_signals = 0
        
        if vix_pct is not None and vix_pct > self.config.vix_jump_threshold:
            risk_off_signals += 1
            regime = "risk_off"
        
        if vftse_pct is not None and vftse_pct > self.config.vftse_jump_threshold:
            risk_off_signals += 1
            regime = "risk_off"
        
        if proxy_z is not None and proxy_z < self.config.proxy_z_risk_off_threshold:
            risk_off_signals += 1
            regime = "risk_off"
        
        if abs(proxy_move) > 2.0:
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
    
    def compute_ftse_proxy(self) -> Dict:
        """
        Compute synthetic FTSE 100 futures proxy
        
        Returns:
            Dictionary with:
            - asof: timestamp
            - ftse_proxy_pct: estimated FTSE move %
            - ftse_proxy_z: Z-score
            - regime: market regime (risk_on/risk_off/neutral)
            - confidence: confidence level (0-1)
            - risk_multiplier: risk adjustment factor
            - drivers: breakdown of component moves
            - meta: configuration metadata
        """
        logger.info("Computing FTSE proxy...")
        
        # Fetch intraday closes for all drivers
        ftse_futures_curr, ftse_futures_prev = self._fetch_intraday_close(self.config.ticker_ftse_futures)
        es_curr, es_prev = self._fetch_intraday_close(self.config.ticker_es)
        vix_curr, vix_prev = self._fetch_intraday_close(self.config.ticker_vix)
        vftse_curr, vftse_prev = self._fetch_intraday_close(self.config.ticker_vftse)
        gbp_curr, gbp_prev = self._fetch_intraday_close(self.config.ticker_gbp)
        brent_curr, brent_prev = self._fetch_intraday_close(self.config.ticker_brent)
        
        # Calculate percentage moves
        ftse_futures_pct = self._pct_change(ftse_futures_curr, ftse_futures_prev)
        es_pct = self._pct_change(es_curr, es_prev)
        vix_pct = self._pct_change(vix_curr, vix_prev)
        vftse_pct = self._pct_change(vftse_curr, vftse_prev)
        gbp_pct = self._pct_change(gbp_curr, gbp_prev)
        brent_pct = self._pct_change(brent_curr, brent_prev)
        
        # Track if FTSE futures available
        ftse_futures_available = ftse_futures_pct is not None
        
        # Calculate weighted proxy move
        proxy_move = self._weighted_proxy_move(ftse_futures_pct, es_pct, vix_pct, 
                                              vftse_pct, gbp_pct, brent_pct)
        
        if proxy_move is None:
            logger.error("Failed to compute proxy move - insufficient data")
            return {
                'asof': datetime.now(self.timezone_london).isoformat(),
                'ftse_proxy_pct': None,
                'ftse_proxy_z': None,
                'regime': 'unknown',
                'confidence': 0.0,
                'risk_multiplier': 1.0,
                'drivers': {},
                'meta': {'error': 'Insufficient data'},
                'available': False
            }
        
        # Calculate volatility gate (using FTSE futures if available, else FTSE index)
        try:
            symbol_for_vol = self.config.ticker_ftse_futures if ftse_futures_available else "^FTSE"
            ticker = Ticker(symbol_for_vol)
            hist = ticker.history(period='60d', interval='1d')
            if hist is not None and len(hist) >= 20:
                returns = hist['close'].pct_change().dropna() * 100.0
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
        
        # Compute Z-score (prefer FTSE futures, fallback to index)
        proxy_z = self._compute_z_score(proxy_move_adj, 
                                        symbol=self.config.ticker_ftse_futures if ftse_futures_available else "^FTSE")
        
        # Determine regime
        regime, confidence, risk_multiplier = self._determine_regime(vix_pct, vftse_pct, proxy_z, 
                                                                     proxy_move_adj, ftse_futures_available)
        
        # Build result
        result = {
            'asof': datetime.now(self.timezone_london).isoformat(),
            'ftse_proxy_pct': round(proxy_move_adj, 2),
            'ftse_proxy_z': round(proxy_z, 2) if proxy_z is not None else None,
            'regime': regime,
            'confidence': round(confidence, 2),
            'risk_multiplier': round(risk_multiplier, 2),
            'drivers': {
                'ftse_futures_pct': round(ftse_futures_pct, 2) if ftse_futures_pct is not None else None,
                'es_pct': round(es_pct, 2) if es_pct is not None else None,
                'vix_pct': round(vix_pct, 2) if vix_pct is not None else None,
                'vftse_pct': round(vftse_pct, 2) if vftse_pct is not None else None,
                'gbp_pct': round(gbp_pct, 2) if gbp_pct is not None else None,
                'brent_pct': round(brent_pct, 2) if brent_pct is not None else None,
                'vol_gate': round(vol_gate, 2)
            },
            'meta': {
                'interval': self.config.interval,
                'lookback_intraday': self.config.lookback_intraday,
                'z_lookback_days': self.config.z_lookback_days,
                'ftse_futures_available': ftse_futures_available,
                'primary_source': 'Z=F (FTSE futures)' if ftse_futures_available else 'Blended proxy',
                'weights': {
                    'ftse_futures': self.config.w_ftse_futures if ftse_futures_available else 0.0,
                    'es': 0.10 if ftse_futures_available else self.config.w_es,
                    'vix': self.config.w_vix,
                    'vftse': self.config.w_vftse,
                    'gbp': self.config.w_gbp,
                    'brent': self.config.w_brent
                }
            },
            'available': True,
            'source': 'ftse_proxy_advanced'
        }
        
        source_str = "Z=F (FTSE futures)" if ftse_futures_available else "Blended"
        z_str = f"{proxy_z:.2f}" if proxy_z is not None else "N/A"
        logger.info(f"FTSE Proxy: {proxy_move_adj:.2f}% (Z={z_str}, "
                   f"Regime={regime}, Confidence={confidence:.0%}, Source={source_str})")
        
        return result


if __name__ == "__main__":
    # Test the proxy
    proxy = FTSEProxy()
    result = proxy.compute_ftse_proxy()
    print("\n" + "="*80)
    print("FTSE 100 PROXY TEST RESULTS")
    print("="*80)
    print(f"\nTimestamp: {result['asof']}")
    print(f"FTSE Proxy Move: {result['ftse_proxy_pct']}%")
    print(f"Z-Score: {result['ftse_proxy_z']}")
    print(f"Regime: {result['regime']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Risk Multiplier: {result['risk_multiplier']}")
    print(f"Primary Source: {result['meta']['primary_source']}")
    print("\nDrivers:")
    for key, val in result['drivers'].items():
        if val is not None:
            print(f"  {key}: {val}%")
    print("="*80 + "\n")
