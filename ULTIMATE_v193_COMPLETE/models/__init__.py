"""
Market Regime Intelligence Module

Provides advanced market regime detection and regime-aware opportunity scoring.
"""

from .market_data_fetcher import MarketDataFetcher
from .market_regime_detector import MarketRegimeDetector
from .regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer
from .cross_market_features import CrossMarketFeatures

__all__ = [
    'MarketDataFetcher',
    'MarketRegimeDetector',
    'RegimeAwareOpportunityScorer',
    'CrossMarketFeatures'
]
