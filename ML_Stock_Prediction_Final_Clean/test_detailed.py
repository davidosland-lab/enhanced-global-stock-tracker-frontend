#!/usr/bin/env python3
"""
Detailed test to identify the exact failure point
"""

import sys
import traceback

print("="*60)
print("DETAILED YAHOO FINANCE TEST")
print("="*60)
print()

# 1. Check versions
print("1. Environment Check:")
print(f"   Python: {sys.version}")

try:
    import yfinance as yf
    print(f"   yfinance: {yf.__version__}")
except ImportError as e:
    print(f"   yfinance: NOT INSTALLED - {e}")
    sys.exit(1)

try:
    import curl_cffi
    print(f"   curl_cffi: {curl_cffi.__version__}")
except ImportError:
    print("   curl_cffi: NOT INSTALLED")

try:
    import requests
    print(f"   requests: {requests.__version__}")
except ImportError:
    print("   requests: NOT INSTALLED")

print()

# 2. Test basic ticker creation
print("2. Creating Ticker object:")
try:
    ticker = yf.Ticker("AAPL")
    print("   ✓ Ticker created successfully")
except Exception as e:
    print(f"   ✗ Failed to create ticker: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 3. Test getting info (lighter weight than history)
print("3. Getting ticker.info:")
try:
    info = ticker.info
    if info:
        print(f"   ✓ Got info - keys: {len(info)}")
        print(f"   Symbol: {info.get('symbol', 'N/A')}")
        print(f"   Name: {info.get('longName', 'N/A')}")
    else:
        print("   ✗ Info is empty/None")
except Exception as e:
    print(f"   ✗ Failed to get info: {e}")
    print("\n   Full error details:")
    traceback.print_exc()

print()

# 4. Test getting history
print("4. Getting ticker.history():")
try:
    hist = ticker.history(period="5d")
    if hist is not None and not hist.empty:
        print(f"   ✓ Got history - {len(hist)} days")
        print(f"   Latest close: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("   ✗ History is empty")
except Exception as e:
    print(f"   ✗ Failed to get history: {e}")
    print("\n   Full error details:")
    traceback.print_exc()

print()

# 5. Test download function
print("5. Testing yf.download():")
try:
    data = yf.download("AAPL", period="5d", progress=False)
    if data is not None and not data.empty:
        print(f"   ✓ Download worked - {len(data)} days")
    else:
        print("   ✗ Download returned empty")
except Exception as e:
    print(f"   ✗ Download failed: {e}")
    traceback.print_exc()

print()

# 6. Check for proxy settings
print("6. Network Configuration:")
import os
for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY']:
    if var in os.environ:
        print(f"   {var}: {os.environ[var]}")
    
if not any(var in os.environ for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']):
    print("   No proxy configured")

print()

# 7. Test direct web access
print("7. Testing web access to finance.yahoo.com:")
try:
    import requests
    response = requests.get("https://finance.yahoo.com", timeout=5)
    print(f"   ✓ Connected - Status: {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot reach Yahoo Finance: {e}")

print()
print("="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)