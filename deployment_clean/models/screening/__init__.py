"""
Overnight Stock Screening System

This package provides automated stock screening capabilities for overnight analysis.
Designed for the Australian market (ASX) with expansion capability to other markets.

Modules:
    - stock_scanner: Stock validation and technical analysis
    - spi_monitor: SPI 200 futures and market sentiment tracking
    - batch_predictor: Mass prediction engine using ensemble models
    - opportunity_scorer: Ranking and scoring algorithm
    - report_generator: Morning report creation with HTML/charts
"""

__version__ = "1.0.0"
__author__ = "FinBERT Trading System"

from .stock_scanner import StockScanner
from .spi_monitor import SPIMonitor
from .batch_predictor import BatchPredictor
from .opportunity_scorer import OpportunityScorer
from .report_generator import ReportGenerator

__all__ = [
    'StockScanner',
    'SPIMonitor',
    'BatchPredictor',
    'OpportunityScorer',
    'ReportGenerator'
]
