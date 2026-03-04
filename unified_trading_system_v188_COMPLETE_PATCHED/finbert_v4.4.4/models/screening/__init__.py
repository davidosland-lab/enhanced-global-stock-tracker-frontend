"""
Overnight Stock Screening Module
================================

Automated screening system for ASX stocks with multi-market expansion capability.

Author: FinBERT v4.4
Date: November 2025
"""

# Only import modules that exist in this directory
try:
    from .stock_scanner import StockScanner
    __all__ = ['StockScanner']
except ImportError:
    __all__ = []

__version__ = '1.0.0'

# Note: Full screening modules (spi_monitor, batch_predictor, opportunity_scorer)
# are located in pipelines/models/screening/ directory
