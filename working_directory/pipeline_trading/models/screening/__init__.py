"""
Pipeline Trading - Morning Report System
=========================================

Automated overnight stock screening and morning report generation for global markets.

Markets Supported:
- AU (ASX) - Australian Securities Exchange
- US (NYSE/NASDAQ) - United States markets  
- UK (LSE) - London Stock Exchange

Components:
- overnight_pipeline.py - ASX orchestrator
- us_overnight_pipeline.py - US orchestrator
- uk_overnight_pipeline.py - UK orchestrator
- stock_scanner.py - ASX scanner
- us_stock_scanner.py - US scanner
- uk_stock_scanner.py - UK scanner
- spi_monitor.py - Market sentiment monitor
- batch_predictor.py - ML predictions (FinBERT + LSTM)
- opportunity_scorer.py - Ranks opportunities
- report_generator.py - Creates morning reports

Author: Pipeline Trading System
Version: 1.0.0
Date: January 3, 2026
"""

__version__ = '1.0.0'
__author__ = 'Pipeline Trading System'

from .stock_scanner import StockScanner
from .us_stock_scanner import USStockScanner
from .spi_monitor import SPIMonitor
from .batch_predictor import BatchPredictor
from .opportunity_scorer import OpportunityScorer
from .report_generator import ReportGenerator
from .overnight_pipeline import OvernightPipeline
from .us_overnight_pipeline import USOvernightPipeline

__all__ = [
    'StockScanner',
    'USStockScanner',
    'SPIMonitor',
    'BatchPredictor',
    'OpportunityScorer',
    'ReportGenerator',
    'OvernightPipeline',
    'USOvernightPipeline',
]
