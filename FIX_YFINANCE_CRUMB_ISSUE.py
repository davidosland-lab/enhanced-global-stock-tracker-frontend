#!/usr/bin/env python3
"""
Fix yfinance Crumb/Cookie Issue
Clears cache and forces re-authentication with Yahoo Finance
"""

import os
import shutil
import sys

print("="*70)
print("yfinance Crumb/Cookie Fix".center(70))
print("="*70)

# Step 1: Clear yfinance cache
print("\n1. Clearing yfinance cache...")

cache_locations = [
    os.path.expanduser("~/.cache/py-yfinance"),
    os.path.expanduser("~/AppData/Local/py-yfinance"),  # Windows
    "/tmp/yf_cache",
    ".yfinance_cache"
]

cleared = 0
for cache_dir in cache_locations:
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✓ Cleared: {cache_dir}")
            cleared += 1
        except Exception as e:
            print(f"   ⚠ Could not clear {cache_dir}: {e}")

if cleared == 0:
    print("   ℹ No cache directories found (already clean)")

# Step 2: Test fresh connection
print("\n2. Testing fresh yfinance connection...")

try:
    import yfinance as yf
    
    # Force new session
    print("   Creating new ticker object...")
    ticker = yf.Ticker("AAPL")
    
    print("   Fetching data (this will get new crumb)...")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        print(f"   ✓ SUCCESS! AAPL: ${price:.2f}")
        print(f"   ✓ Got {len(hist)} days of data")
        print("\n✅ yfinance is working - crumb obtained successfully")
        sys.exit(0)
    else:
        print("   ✗ No data returned")
        print("\n❌ Still having issues - see additional fixes below")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("\n❌ Still having issues - see additional fixes below")
    sys.exit(1)
