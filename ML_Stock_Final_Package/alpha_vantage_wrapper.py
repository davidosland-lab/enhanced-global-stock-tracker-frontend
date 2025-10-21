#!/usr/bin/env python3
"""
Wrapper for Alpha Vantage to fix import issues
"""

# Import the actual class
from alpha_vantage_fetcher import AlphaVantageDataFetcher

# Create an alias for compatibility
AlphaVantageFetcher = AlphaVantageDataFetcher

# Export both names
__all__ = ['AlphaVantageFetcher', 'AlphaVantageDataFetcher']