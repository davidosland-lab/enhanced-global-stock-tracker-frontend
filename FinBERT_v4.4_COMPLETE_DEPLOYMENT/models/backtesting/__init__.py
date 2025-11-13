"""
FinBERT v4.0 - Backtesting Framework
====================================

A comprehensive backtesting framework for testing FinBERT, LSTM, and ensemble prediction models
with realistic trading conditions and performance metrics.

Components:
-----------
Phase 1 - Foundation:
    - HistoricalDataLoader: Fetches and caches historical stock data
    - DataValidator: Validates data quality and detects anomalies
    - CacheManager: Manages SQLite cache for performance

Phase 2 - Prediction Engine:
    - BacktestPredictionEngine: Generates predictions with walk-forward validation

Phase 3 - Trading Simulator:
    - TradingSimulator: Simulates trading with realistic costs and metrics

Author: FinBERT v4.0 Development Team
Date: October 2024
Version: 1.0.0
"""

from .data_loader import HistoricalDataLoader
from .data_validator import DataValidator
from .cache_manager import CacheManager
from .prediction_engine import BacktestPredictionEngine
from .trading_simulator import TradingSimulator

__version__ = '1.0.0'
__all__ = [
    'HistoricalDataLoader',
    'DataValidator',
    'CacheManager',
    'BacktestPredictionEngine',
    'TradingSimulator',
]
