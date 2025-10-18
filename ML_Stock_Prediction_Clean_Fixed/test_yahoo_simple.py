#!/usr/bin/env python3
"""
Simple test to verify Yahoo Finance works
"""

import yfinance as yf

print("Testing Yahoo Finance...")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        print(f"✅ Success! Got {len(hist)} days of data")
        print(f"Latest close: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("❌ No data received")
except Exception as e:
    print(f"❌ Error: {e}")