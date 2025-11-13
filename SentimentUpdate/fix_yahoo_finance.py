#!/usr/bin/env python3
"""
Fix Yahoo Finance connectivity issues
"""

import os
import sys
import time
import shutil

print("=" * 60)
print("YAHOO FINANCE FIX UTILITY")
print("=" * 60)
print()

print("1. Checking yfinance version...")
try:
    import yfinance as yf
    print(f"   Current version: {yf.__version__}")
    
    # Check if outdated
    import subprocess
    result = subprocess.run(["pip", "list", "--outdated"], capture_output=True, text=True)
    if "yfinance" in result.stdout:
        print("   ⚠ yfinance is outdated!")
        print("   Updating yfinance...")
        subprocess.run(["pip", "install", "--upgrade", "yfinance"])
        print("   ✓ Updated to latest version")
    else:
        print("   ✓ yfinance is up to date")
except ImportError:
    print("   ✗ yfinance not installed")
    sys.exit(1)

print()
print("2. Clearing yfinance cache...")
cache_dir = os.path.expanduser("~/.cache/py-yfinance")
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print("   ✓ Cache cleared")
else:
    print("   ✓ No cache found")

print()
print("3. Testing Yahoo Finance connection...")
print("   Waiting 2 seconds to avoid rate limit...")
time.sleep(2)

try:
    import yfinance as yf
    
    # Test with AAPL
    ticker = yf.Ticker("AAPL")
    
    # Add delay between requests
    print("   Testing history endpoint...")
    hist = ticker.history(period="1d")
    
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        print(f"   ✓ Successfully fetched AAPL: ${price:.2f}")
    else:
        print("   ✗ Empty response from Yahoo")
        
    time.sleep(1)  # Small delay
    
    # Test info endpoint
    print("   Testing info endpoint...")
    info = ticker.info
    if info:
        print(f"   ✓ Info endpoint working")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    
print()
print("4. Testing market indicators...")

indicators = {
    "^VIX": "VIX",
    "^GSPC": "S&P 500",
    "^TNX": "10Y Treasury"
}

for symbol, name in indicators.items():
    time.sleep(0.5)  # Delay between requests
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            value = hist['Close'].iloc[-1]
            print(f"   ✓ {name}: {value:.2f}")
        else:
            print(f"   ✗ {name}: No data")
    except Exception as e:
        print(f"   ✗ {name}: {str(e)[:30]}")

print()
print("=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

print("""
If still having issues:

1. Update yfinance manually:
   pip uninstall yfinance
   pip install yfinance --upgrade

2. Use Alpha Vantage as primary source:
   - Already configured with API key
   - More stable but slower

3. Add delays between API calls:
   - Yahoo rate limits aggressively
   - Add time.sleep(0.5) between calls

4. Check your network:
   - Try with mobile hotspot
   - Try with VPN
   - Check firewall settings
""")

print("=" * 60)