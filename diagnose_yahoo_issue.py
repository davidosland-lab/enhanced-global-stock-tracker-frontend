#!/usr/bin/env python3
"""
Comprehensive diagnostic to identify why Yahoo Finance works in sandbox but not locally
"""

import sys
import platform
import subprocess

print("="*60)
print("Yahoo Finance Diagnostic Tool")
print("="*60)
print()

# 1. Check Python version
print("1. Python Version:")
print(f"   {sys.version}")
print()

# 2. Check yfinance version
try:
    import yfinance as yf
    print("2. yfinance Version:")
    print(f"   {yf.__version__}")
except ImportError as e:
    print(f"2. yfinance Error: {e}")
print()

# 3. Check requests version
try:
    import requests
    print("3. requests Version:")
    print(f"   {requests.__version__}")
except ImportError as e:
    print(f"3. requests Error: {e}")
print()

# 4. Check if curl_cffi is installed
print("4. curl_cffi Status:")
try:
    import curl_cffi
    print(f"   ✓ Installed - Version {curl_cffi.__version__}")
except ImportError:
    print("   ✗ NOT INSTALLED - This might be the issue!")
    print("   yfinance 0.2.18+ requires curl_cffi")
    print("   Install with: pip install curl_cffi")
print()

# 5. Test basic yfinance call
print("5. Testing Basic yfinance Call:")
try:
    import yfinance as yf
    
    # Method 1: Simple ticker
    print("   Method 1: yf.Ticker('AAPL')")
    ticker = yf.Ticker("AAPL")
    
    # Try to get info first (lighter weight)
    print("   Getting ticker info...")
    info = ticker.info
    if info:
        print(f"   ✓ Got info - Market Cap: ${info.get('marketCap', 'N/A'):,}")
    
    # Now try history
    print("   Getting price history...")
    hist = ticker.history(period="1d")
    if not hist.empty:
        print(f"   ✓ Got history - Latest: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("   ✗ History is empty")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    print("   Full traceback:")
    traceback.print_exc()
print()

# 6. Test with different methods
print("6. Testing Alternative Methods:")

# Method A: Using download
try:
    print("   Method A: yf.download('AAPL')")
    data = yf.download("AAPL", period="1d", progress=False)
    if not data.empty:
        print(f"   ✓ Download worked - Got {len(data)} rows")
    else:
        print("   ✗ Download returned empty")
except Exception as e:
    print(f"   ✗ Download failed: {e}")

print()

# 7. Check network/proxy settings
print("7. Network Configuration:")
import os
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
has_proxy = False
for var in proxy_vars:
    if var in os.environ:
        print(f"   {var}: {os.environ[var]}")
        has_proxy = True
if not has_proxy:
    print("   No proxy configured")
print()

# 8. Test direct URL access
print("8. Testing Direct Yahoo Finance URL:")
try:
    import requests
    
    # Don't use session, let requests handle it
    url = "https://finance.yahoo.com"
    print(f"   Accessing {url}")
    response = requests.get(url, timeout=5)
    print(f"   ✓ Status Code: {response.status_code}")
    print(f"   ✓ Response Length: {len(response.text)} bytes")
except Exception as e:
    print(f"   ✗ Failed to access Yahoo Finance: {e}")
print()

# 9. Platform info
print("9. Platform Information:")
print(f"   System: {platform.system()}")
print(f"   Release: {platform.release()}")
print(f"   Machine: {platform.machine()}")
print(f"   Processor: {platform.processor()}")
print()

# 10. Recommendations
print("="*60)
print("RECOMMENDATIONS:")
print("="*60)

# Check if curl_cffi is the issue
try:
    import curl_cffi
except ImportError:
    print("\n❗ CRITICAL: curl_cffi is not installed!")
    print("   Modern yfinance requires curl_cffi to bypass anti-bot measures.")
    print("\n   FIX: Run these commands:")
    print("   pip uninstall yfinance")
    print("   pip install yfinance --upgrade")
    print("   pip install curl_cffi")

# Check yfinance version
try:
    import yfinance as yf
    version_parts = yf.__version__.split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
    
    if major == 0 and minor < 2:
        print("\n❗ Old yfinance version detected!")
        print(f"   Current: {yf.__version__}")
        print("   Recommended: 0.2.18 or higher")
        print("\n   FIX: pip install yfinance --upgrade")
    elif major == 0 and minor == 2:
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0
        if patch >= 18:
            print(f"\n✓ yfinance version {yf.__version__} is good")
        else:
            print(f"\n⚠ yfinance {yf.__version__} might have issues")
            print("   Consider upgrading: pip install yfinance --upgrade")
except:
    pass

print("\n" + "="*60)
print("End of Diagnostic")
print("="*60)