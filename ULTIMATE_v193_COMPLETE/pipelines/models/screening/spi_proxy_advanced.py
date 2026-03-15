"""
SPI 200 Futures Proxy Module (Advanced)

Provides a synthetic SPI 200 futures estimate using:
- ES=F (E-mini S&P 500 futures) - primary driver
- NQ=F (E-mini NASDAQ futures)
- ^VIX (Volatility Index)
- AUDUSD=X (Australian Dollar)
- TIO=F (Iron Ore futures) - optional
- BZ=F (Brent Crude) - optional

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


class SPIProxyConfig:
    """Configuration for SPI proxy calculation with regime-based weights"""
    
    def __init__(self):
        # Data fetching
        self.interval = "5m"  # 5-minute intraday
        self.lookback_intraday = "2d"  # Last 2 days for intraday
        self.z_lookback_days = 60  # 60 days for Z-score calculation
        
        # Ticker symbols
        self.ticker_es = "ES=F"  # E-mini S&P 500 futures
        self.ticker_nq = "NQ=F"  # E-mini NASDAQ futures
        self.ticker_vix = "^VIX"  # Volatility Index
        self.ticker_aud = "AUDUSD=X"  # Australian Dollar
        self.ticker_iron = "TIO=F"  # Iron Ore futures (optional)
        self.ticker_brent = "BZ=F"  # Brent Crude (optional)
        
        # REGIME-BASED WEIGHTS (v193.11.6 Enhancement)
        # Different weights for different market conditions
        
        # RISK-OFF Regime (VIX > 25, World Risk > 75, Major selloffs)
        self.weights_risk_off = {
            'w_es': 0.85,      # S&P dominates in risk-off
            'w_nq': 0.15,      # NASDAQ less important
            'w_aud': -0.05,    # AUD matters less
            'w_vix': -0.40,    # VIX impact much stronger
            'w_iron': 0.05,    # Commodities less important
            'w_brent': 0.05,
            'sentiment_factor': 0.75  # Sentiment adjustment more aggressive
        }
        
        # NORMAL Regime (VIX 15-25, World Risk 40-75, Regular trading)
        self.weights_normal = {
            'w_es': 0.75,      # S&P primary driver (increased from 0.55)
            'w_nq': 0.25,      # NASDAQ important (increased from 0.20)
            'w_aud': -0.05,    # AUD minor inverse
            'w_vix': -0.30,    # VIX moderate impact (increased from -0.20)
            'w_iron': 0.10,    # Iron ore moderate (decreased from 0.20)
            'w_brent': 0.05,
            'sentiment_factor': 0.50  # Moderate sentiment adjustment
        }
        
        # RISK-ON Regime (VIX < 15, World Risk < 40, Bull market)
        self.weights_risk_on = {
            'w_es': 0.65,      # S&P still important
            'w_nq': 0.30,      # Tech matters more in bull markets
            'w_aud': -0.05,    # AUD less important
            'w_vix': -0.15,    # VIX less important
            'w_iron': 0.15,    # Commodities more important
            'w_brent': 0.10,   # Oil more important
            'sentiment_factor': 0.35  # Less sentiment adjustment needed
        }
        
        # Default to NORMAL regime weights (backward compatible)
        self.w_es = self.weights_normal['w_es']
        self.w_nq = self.weights_normal['w_nq']
        self.w_aud = self.weights_normal['w_aud']
        self.w_vix = self.weights_normal['w_vix']
        self.w_iron = self.weights_normal['w_iron']
        self.w_brent = self.weights_normal['w_brent']
        
        # Regime detection thresholds
        self.vix_jump_threshold = 3.0  # % VIX jump = risk-off
        self.proxy_z_risk_off_threshold = -1.0  # Z-score < -1.0 = risk-off
        self.vix_risk_off_threshold = 25.0  # VIX > 25 = risk-off
        self.vix_risk_on_threshold = 15.0   # VIX < 15 = risk-on
        
        # Caps and limits
        self.max_proxy_move = 3.5  # Cap proxy move at +/-3.5%
        self.max_z_score = 4.0  # Cap Z-score at +/-4.0
        
        # Confidence parameters
        self.confidence_base = 0.70
        self.confidence_min = 0.35
        self.confidence_max = 0.90


class SPIProxy:
    """
    Advanced SPI 200 futures proxy calculator
    
    Uses multiple global market drivers to estimate SPI 200 futures
    movement when direct SPI futures data is unavailable.
    """
    
    def __init__(self, config: Optional[SPIProxyConfig] = None):
        """
        Initialize SPI Proxy
        
        Args:
            config: Optional configuration object
        """
        self.config = config or SPIProxyConfig()
        self.timezone_sydney = pytz.timezone('Australia/Sydney')
        logger.info("SPI Proxy initialized with advanced configuration")
    
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
                            es_pct: Optional[float],
                            nq_pct: Optional[float],
                            vix_pct: Optional[float],
                            aud_pct: Optional[float],
                            iron_pct: Optional[float],
                            brent_pct: Optional[float]) -> Optional[float]:
        """
        Calculate weighted proxy move from all drivers
        
        Returns:
            Weighted percentage move (uncapped)
        """
        components = []
        
        if es_pct is not None:
            components.append(self.config.w_es * es_pct)
        if nq_pct is not None:
            components.append(self.config.w_nq * nq_pct)
        if vix_pct is not None:
            components.append(self.config.w_vix * vix_pct)
        if aud_pct is not None:
            components.append(self.config.w_aud * aud_pct)
        if iron_pct is not None:
            components.append(self.config.w_iron * iron_pct)
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
                         proxy_move: float) -> Tuple[str, float, float]:
        """
        Determine market regime and calculate confidence + risk multiplier
        
        Returns:
            Tuple of (regime, confidence, risk_multiplier)
        """
        regime = "neutral"
        confidence = self.config.confidence_base
        risk_multiplier = 1.0
        
        # Risk-off indicators
        risk_off_signals = 0
        
        if vix_pct is not None and vix_pct > self.config.vix_jump_threshold:
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
    
    def _detect_market_regime(self, vix_curr: Optional[float], world_risk_score: Optional[float] = None) -> str:
        """
        Detect current market regime for regime-based weight selection
        
        Args:
            vix_curr: Current VIX level
            world_risk_score: World event risk score (0-100)
            
        Returns:
            'risk_off', 'risk_on', or 'normal'
        """
        # RISK-OFF conditions (priority order)
        if world_risk_score is not None and world_risk_score > 75:
            return 'risk_off'  # Critical world events
        
        if vix_curr is not None:
            if vix_curr > self.config.vix_risk_off_threshold:  # VIX > 25
                return 'risk_off'
            elif vix_curr < self.config.vix_risk_on_threshold:  # VIX < 15
                if world_risk_score is None or world_risk_score < 40:
                    return 'risk_on'  # Low VIX + low risk
        
        return 'normal'  # Default regime
    
    def _apply_regime_weights(self, regime: str):
        """
        Apply regime-specific weights to config
        
        Args:
            regime: 'risk_off', 'risk_on', or 'normal'
        """
        if regime == 'risk_off':
            weights = self.config.weights_risk_off
            logger.info(f"[REGIME] RISK-OFF detected - using aggressive S&P weighting (0.85)")
        elif regime == 'risk_on':
            weights = self.config.weights_risk_on
            logger.info(f"[REGIME] RISK-ON detected - using tech-heavy weighting (NASDAQ 0.30)")
        else:
            weights = self.config.weights_normal
            logger.info(f"[REGIME] NORMAL market - using balanced weighting")
        
        # Update config weights
        self.config.w_es = weights['w_es']
        self.config.w_nq = weights['w_nq']
        self.config.w_aud = weights['w_aud']
        self.config.w_vix = weights['w_vix']
        self.config.w_iron = weights['w_iron']
        self.config.w_brent = weights['w_brent']
        
        logger.info(f"  S&P Weight: {self.config.w_es:.2f}, NASDAQ: {self.config.w_nq:.2f}, VIX: {self.config.w_vix:.2f}")
    
    def compute_spi_proxy(self, world_risk_score: Optional[float] = None) -> Dict:
        """
        Compute synthetic SPI 200 futures proxy with regime-based weights
        
        Args:
            world_risk_score: Optional world event risk score (0-100) for regime detection
        
        Returns:
            Dictionary with:
            - asof: timestamp
            - spi_proxy_pct: estimated SPI move %
            - spi_proxy_z: Z-score
            - regime: market regime (risk_on/risk_off/normal)
            - confidence: confidence level (0-1)
            - risk_multiplier: risk adjustment factor
            - drivers: breakdown of component moves
            - meta: configuration metadata
        """
        logger.info("Computing SPI proxy...")
        
        # Fetch intraday closes for all drivers
        es_curr, es_prev = self._fetch_intraday_close(self.config.ticker_es)
        nq_curr, nq_prev = self._fetch_intraday_close(self.config.ticker_nq)
        vix_curr, vix_prev = self._fetch_intraday_close(self.config.ticker_vix)
        aud_curr, aud_prev = self._fetch_intraday_close(self.config.ticker_aud)
        iron_curr, iron_prev = self._fetch_intraday_close(self.config.ticker_iron)
        brent_curr, brent_prev = self._fetch_intraday_close(self.config.ticker_brent)
        
        # Detect market regime and apply appropriate weights
        market_regime = self._detect_market_regime(vix_curr, world_risk_score)
        self._apply_regime_weights(market_regime)
        
        # Calculate percentage moves
        es_pct = self._pct_change(es_curr, es_prev)
        nq_pct = self._pct_change(nq_curr, nq_prev)
        vix_pct = self._pct_change(vix_curr, vix_prev)
        aud_pct = self._pct_change(aud_curr, aud_prev)
        iron_pct = self._pct_change(iron_curr, iron_prev)
        brent_pct = self._pct_change(brent_curr, brent_prev)
        
        # Calculate weighted proxy move (now uses regime-specific weights)
        proxy_move = self._weighted_proxy_move(es_pct, nq_pct, vix_pct, 
                                              aud_pct, iron_pct, brent_pct)
        
        if proxy_move is None:
            logger.error("Failed to compute proxy move - insufficient data")
            return {
                'asof': datetime.now(self.timezone_sydney).isoformat(),
                'spi_proxy_pct': None,
                'spi_proxy_z': None,
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
        regime, confidence, risk_multiplier = self._determine_regime(vix_pct, proxy_z, proxy_move_adj)
        
        # Build result
        result = {
            'asof': datetime.now(self.timezone_sydney).isoformat(),
            'spi_proxy_pct': round(proxy_move_adj, 2),
            'spi_proxy_z': round(proxy_z, 2) if proxy_z is not None else None,
            'regime': regime,
            'confidence': round(confidence, 2),
            'risk_multiplier': round(risk_multiplier, 2),
            'drivers': {
                'es_pct': round(es_pct, 2) if es_pct is not None else None,
                'nq_pct': round(nq_pct, 2) if nq_pct is not None else None,
                'vix_pct': round(vix_pct, 2) if vix_pct is not None else None,
                'aud_pct': round(aud_pct, 2) if aud_pct is not None else None,
                'iron_pct': round(iron_pct, 2) if iron_pct is not None else None,
                'brent_pct': round(brent_pct, 2) if brent_pct is not None else None,
                'vol_gate': round(vol_gate, 2)
            },
            'meta': {
                'interval': self.config.interval,
                'lookback_intraday': self.config.lookback_intraday,
                'z_lookback_days': self.config.z_lookback_days,
                'weights': {
                    'es': self.config.w_es,
                    'nq': self.config.w_nq,
                    'vix': self.config.w_vix,
                    'aud': self.config.w_aud,
                    'iron': self.config.w_iron,
                    'brent': self.config.w_brent
                }
            },
            'available': True,
            'source': 'spi_proxy_advanced'
        }
        
        z_str = f"{proxy_z:.2f}" if proxy_z is not None else "N/A"
        logger.info(f"SPI Proxy: {proxy_move_adj:.2f}% (Z={z_str}, "
                   f"Regime={regime}, Confidence={confidence:.0%})")
        
        return result


if __name__ == "__main__":
    # Test the proxy
    proxy = SPIProxy()
    result = proxy.compute_spi_proxy()
    print("\n" + "="*80)
    print("SPI 200 PROXY TEST RESULTS")
    print("="*80)
    print(f"\nTimestamp: {result['asof']}")
    print(f"SPI Proxy Move: {result['spi_proxy_pct']}%")
    print(f"Z-Score: {result['spi_proxy_z']}")
    print(f"Regime: {result['regime']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Risk Multiplier: {result['risk_multiplier']}")
    print("\nDrivers:")
    for key, val in result['drivers'].items():
        if val is not None:
            print(f"  {key}: {val}%")
    print("="*80 + "\n")
