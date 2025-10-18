#!/usr/bin/env python3
"""Test Yahoo Finance connection"""

import yfinance as yf

try:
    print("Testing Yahoo Finance API...")
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        latest = hist['Close'].iloc[-1]
        print(f"SUCCESS: Yahoo Finance working!")
        print(f"AAPL latest price: ${latest:.2f}")
    else:
        print("WARNING: No data received (market may be closed)")
except Exception as e:
    print(f"ERROR: Yahoo Finance test failed - {e}")