#!/usr/bin/env python3
"""
Diagnostic to find why Yahoo Finance fails
Run this to identify the exact issue
"""

import sys
print("="*60)
print("YAHOO FINANCE DIAGNOSTIC")
print("="*60)
print()

# 1. Python version
print(f"1. Python: {sys.version}")
print()

# 2. Check yfinance
try:
    import yfinance as yf
    print(f"2. yfinance: {yf.__version__}")
except Exception as e:
    print(f"2. yfinance ERROR: {e}")
    sys.exit(1)
print()

# 3. CRITICAL - Check curl_cffi
print("3. curl_cffi (REQUIRED for modern yfinance):")
try:
    import curl_cffi
    print(f"   ✓ INSTALLED - Version {curl_cffi.__version__}")
except ImportError:
    print("   ✗ NOT INSTALLED!")
    print("   THIS IS LIKELY THE PROBLEM!")
    print()
    print("   FIX THIS NOW:")
    print("   pip install curl_cffi")
    print()
print()

# 4. Test the EXACT code from test_yahoo.py
print("4. Testing EXACT code from test_yahoo.py:")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        latest = hist['Close'].iloc[-1]
        print(f"   ✓ SUCCESS: Got data - AAPL: ${latest:.2f}")
    else:
        print("   ✗ FAILED: Empty data")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    
    # Show the actual error type
    print(f"   Error Type: {type(e).__name__}")
    
    # If it's the JSON error, it's definitely curl_cffi
    if "Expecting value" in str(e):
        print()
        print("   *** CONFIRMED: This is the curl_cffi issue ***")
        print("   yfinance is trying to use curl_cffi but it's not installed")
        print()
        print("   SOLUTION:")
        print("   1. pip install curl_cffi")
        print("   2. Restart your terminal/command prompt")
        print("   3. Run this test again")

print()
print("="*60)
print("SUMMARY")
print("="*60)

try:
    import curl_cffi
    print("✓ System should be working")
except ImportError:
    print("✗ curl_cffi is MISSING - Install it with: pip install curl_cffi")