"""
Historical Backtesting Module for Unified Trading System
=========================================================

Copied from FinBERT v4.4.4 with adaptations for the unified system.

This module provides real historical backtesting with:
- Yahoo Finance real data integration
- Walk-forward validation (no look-ahead bias)
- Three prediction models: LSTM, Technical, Momentum
- Ensemble prediction combining all three
- Portfolio-level management
- Realistic execution costs (commission, slippage)

Usage:
    from core.backtesting import HistoricalDataLoader, BacktestPredictionEngine
    from core.backtesting import PortfolioBacktester
    
Version: 1.0.0 (Adapted from FinBERT v4.4.4)
Date: February 28, 2026
"""

__version__ = "1.0.0"

# Import main components
from .data_loader import HistoricalDataLoader
from .prediction_engine import BacktestPredictionEngine
from .backtest_engine import PortfolioBacktestEngine
from .portfolio_backtester import PortfolioBacktester, run_portfolio_backtest
from .trading_simulator import TradingSimulator

__all__ = [
    'HistoricalDataLoader',
    'BacktestPredictionEngine',
    'PortfolioBacktestEngine',
    'PortfolioBacktester',
    'run_portfolio_backtest',
    'TradingSimulator'
]
