"""
Market Regime Engine Wrapper
============================
Generic wrapper for market regime detection across all markets (AU, US, UK).

This module provides a unified interface to the comprehensive MarketRegimeDetector
from the models/ package, making it compatible with EventRiskGuard and other
pipeline components that expect a market regime engine.

Usage:
    from market_regime_engine import MarketRegimeEngine, MarketRegimeConfig
    
    config = MarketRegimeConfig(market='AU')
    engine = MarketRegimeEngine(config=config)
    result = engine.analyse()
    
    print(f"Regime: {result['regime_label']}")
    print(f"Crash Risk: {result['crash_risk_score']:.3f}")
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketRegimeConfig:
    """
    Configuration for Market Regime Engine
    
    Attributes:
        market: Market identifier ('AU', 'US', 'UK')
        index_symbol: Primary market index symbol (e.g., '^AXJO', '^GSPC', '^FTSE')
        vol_symbol: Volatility index symbol (e.g., '^VIX') or None
        fx_symbol: FX pair symbol (e.g., 'AUDUSD=X', 'DX-Y.NYB', 'GBPUSD=X')
    """
    market: str = 'AU'
    index_symbol: str = '^AXJO'
    vol_symbol: Optional[str] = None
    fx_symbol: str = 'AUDUSD=X'


class MarketRegimeEngine:
    """
    Unified Market Regime Engine
    
    Wraps the comprehensive MarketRegimeDetector to provide:
    - 14 market regime types (Bullish/Neutral/Bearish/Special)
    - Cross-market feature analysis
    - Crash risk scoring
    - Compatible interface for EventRiskGuard and pipelines
    """
    
    def __init__(self, config: Optional[MarketRegimeConfig] = None):
        """
        Initialize Market Regime Engine
        
        Args:
            config: Market configuration (defaults to AU market)
        """
        self.config = config or MarketRegimeConfig()
        self.detector = None
        self.data_fetcher = None
        
        try:
            # Import from root models package
            # Add parent directories to path to find models/
            current_dir = Path(__file__).parent.absolute()
            root_dir = current_dir.parent.parent.parent  # Go up from screening -> models -> pipelines -> root
            
            if str(root_dir) not in sys.path:
                sys.path.insert(0, str(root_dir))
            
            # Import the comprehensive regime intelligence modules
            from models.market_regime_detector import MarketRegimeDetector
            from models.market_data_fetcher import MarketDataFetcher
            
            # Initialize components
            self.data_fetcher = MarketDataFetcher()
            self.detector = MarketRegimeDetector()
            
            logger.info(f"[OK] Market Regime Engine initialized for {self.config.market} market")
            logger.info(f"    Index: {self.config.index_symbol} | FX: {self.config.fx_symbol}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Market Regime Engine: {e}")
            logger.debug(f"Error details: {type(e).__name__}: {e}")
            raise
    
    def analyse(self) -> Dict:
        """
        Perform complete market regime analysis
        
        Returns:
            Dictionary with regime analysis results:
            {
                'regime_label': str,           # e.g., 'Trending Bull', 'High Volatility', 'UNKNOWN'
                'crash_risk_score': float,     # 0.0-1.0 (0=safe, 1=high risk)
                'confidence': str,             # 'HIGH', 'MEDIUM', 'LOW'
                'primary_regime': str,         # Main regime classification
                'secondary_regimes': list,     # Additional active regimes
                'regime_strength': float,      # Regime strength 0-1
                'sector_impacts': dict,        # Expected sector performance
                'cross_market_features': dict, # Market context signals
                'timestamp': str               # ISO timestamp
            }
        """
        try:
            if not self.detector or not self.data_fetcher:
                return self._get_fallback_analysis()
            
            # Fetch current market data
            market_data = self.data_fetcher.fetch_market_data()
            
            if not market_data:
                logger.warning("No market data available for regime detection")
                return self._get_fallback_analysis()
            
            # Detect regime using comprehensive detector
            regime_result = self.detector.detect_regime(market_data)
            
            # Extract regime information
            primary_regime = regime_result.get('primary_regime', 'UNKNOWN')
            confidence = regime_result.get('confidence', 0.0)
            regime_strength = regime_result.get('regime_strength', 0.0)
            
            # Map to simplified regime label for compatibility
            regime_label = self._map_regime_label(primary_regime)
            
            # Calculate crash risk from regime data
            crash_risk = self._calculate_crash_risk(regime_result, market_data)
            
            # Map confidence to label
            if confidence >= 0.7:
                confidence_label = 'HIGH'
            elif confidence >= 0.4:
                confidence_label = 'MEDIUM'
            else:
                confidence_label = 'LOW'
            
            result = {
                'regime_label': regime_label,
                'crash_risk_score': crash_risk,
                'confidence': confidence_label,
                'primary_regime': primary_regime,
                'secondary_regimes': regime_result.get('secondary_regimes', []),
                'regime_strength': regime_strength,
                'sector_impacts': regime_result.get('sector_impacts', {}),
                'cross_market_features': market_data,
                'timestamp': regime_result.get('timestamp', ''),
                'market': self.config.market,
                'index': self.config.index_symbol
            }
            
            logger.info(f"Regime Analysis: {regime_label} | Crash Risk: {crash_risk:.3f} | Confidence: {confidence_label}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in regime analysis: {e}")
            logger.debug(f"Error details: {type(e).__name__}: {e}", exc_info=True)
            return self._get_fallback_analysis()
    
    def _map_regime_label(self, primary_regime: str) -> str:
        """
        Map comprehensive regime types to simplified labels for compatibility
        
        Args:
            primary_regime: Regime from MarketRegimeDetector
        
        Returns:
            Simplified regime label
        """
        regime_mapping = {
            # Bullish regimes
            'Trending Bull': 'bullish',
            'Ranging Bull': 'bullish',
            'Volatile Bull': 'bullish_volatile',
            
            # Neutral regimes
            'Ranging Consolidation': 'neutral',
            'Volatile Consolidation': 'neutral_volatile',
            
            # Bearish regimes
            'Trending Bear': 'bearish',
            'Ranging Bear': 'bearish',
            'Volatile Bear': 'bearish_volatile',
            
            # Special regimes
            'High Volatility': 'high_vol',
            'Low Volatility': 'low_vol',
            'Momentum Reversal': 'reversal',
            'Breakout': 'breakout',
            'Breakdown': 'breakdown',
            'Unknown': 'UNKNOWN'
        }
        
        return regime_mapping.get(primary_regime, 'UNKNOWN')
    
    def _calculate_crash_risk(self, regime_result: Dict, market_data: Dict) -> float:
        """
        Calculate crash risk score from regime and market data
        
        Args:
            regime_result: Result from regime detector
            market_data: Current market data
        
        Returns:
            Crash risk score 0.0-1.0
        """
        try:
            primary_regime = regime_result.get('primary_regime', 'Unknown')
            regime_strength = regime_result.get('regime_strength', 0.0)
            
            # Base crash risk by regime type
            crash_risk_map = {
                'Trending Bear': 0.7,
                'Volatile Bear': 0.8,
                'Ranging Bear': 0.6,
                'High Volatility': 0.75,
                'Breakdown': 0.85,
                'Momentum Reversal': 0.5,
                'Volatile Consolidation': 0.4,
                'Bearish Volatile': 0.8,
                'Ranging Consolidation': 0.2,
                'Low Volatility': 0.1,
                'Trending Bull': 0.15,
                'Ranging Bull': 0.2,
                'Volatile Bull': 0.35,
                'Breakout': 0.25,
                'Unknown': 0.3
            }
            
            base_risk = crash_risk_map.get(primary_regime, 0.3)
            
            # Adjust for regime strength (strong regimes more certain)
            risk_adjustment = regime_strength * 0.2  # +/- 20%
            
            # Adjust for VIX if available
            vix_level = market_data.get('vix_level', 20)
            if vix_level > 30:
                vix_adjustment = min((vix_level - 30) / 30, 0.3)  # Up to +30%
            elif vix_level < 15:
                vix_adjustment = -0.1  # -10% for low VIX
            else:
                vix_adjustment = 0
            
            # Combined crash risk
            crash_risk = base_risk + risk_adjustment + vix_adjustment
            
            # Clamp to 0-1
            return max(0.0, min(1.0, crash_risk))
            
        except Exception as e:
            logger.warning(f"Error calculating crash risk: {e}")
            return 0.3  # Default moderate risk
    
    def _get_fallback_analysis(self) -> Dict:
        """
        Return fallback analysis when regime detection fails
        
        Returns:
            Default regime analysis dictionary
        """
        return {
            'regime_label': 'UNKNOWN',
            'crash_risk_score': 0.0,
            'confidence': 'LOW',
            'primary_regime': 'Unknown',
            'secondary_regimes': [],
            'regime_strength': 0.0,
            'sector_impacts': {},
            'cross_market_features': {},
            'timestamp': '',
            'market': self.config.market,
            'index': self.config.index_symbol,
            'error': 'Regime detection unavailable'
        }


# For backward compatibility with old code
class MarketRegimeConfig:
    """Configuration class for market regime engine"""
    def __init__(self, 
                 market: str = 'AU',
                 index_symbol: str = '^AXJO',
                 vol_symbol: Optional[str] = None,
                 fx_symbol: str = 'AUDUSD=X'):
        self.market = market
        self.index_symbol = index_symbol
        self.vol_symbol = vol_symbol
        self.fx_symbol = fx_symbol
