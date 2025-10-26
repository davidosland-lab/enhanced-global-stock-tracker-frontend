#!/usr/bin/env python3
"""
Test Economic Data Fetching
"""

import os
import sys
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Test economic indicators
import yfinance as yf
from datetime import datetime

print("="*60)
print("TESTING ECONOMIC DATA FETCHING")
print("="*60)
print()

print("Fetching real-time economic indicators from Yahoo Finance...")
print("-"*60)

indicators = {}

# Test each indicator
test_symbols = [
    ("^VIX", "VIX (Volatility Index)"),
    ("^TNX", "10-Year Treasury Yield"),
    ("DX-Y.NYB", "US Dollar Index"),
    ("GC=F", "Gold Futures"),
    ("CL=F", "WTI Crude Oil"),
    ("^GSPC", "S&P 500"),
    ("^DJI", "Dow Jones"),
    ("^IXIC", "NASDAQ"),
]

for symbol, name in test_symbols:
    try:
        print(f"\nFetching {name} ({symbol})...")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            close_price = float(hist['Close'].iloc[-1])
            print(f"  ✓ {name}: {close_price:.2f}")
            indicators[symbol] = close_price
        else:
            print(f"  ✗ No data for {name}")
            
    except Exception as e:
        print(f"  ✗ Error fetching {name}: {e}")

print()
print("="*60)
print("SUMMARY")
print("="*60)

if indicators:
    print("✓ Economic data fetching is WORKING!")
    print()
    print("Current Values:")
    for symbol, value in indicators.items():
        name = next(n for s, n in test_symbols if s == symbol)
        print(f"  • {name}: {value:.2f}")
else:
    print("✗ No economic data could be fetched")
    print("Check your internet connection")

print()
print("These values will be displayed in the web interface")
print("under 'Economic Indicators' section")
print()

input("Press Enter to exit...")