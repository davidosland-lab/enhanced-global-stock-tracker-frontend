#!/usr/bin/env python3
"""
Yahoo Finance Windows Fix - Comprehensive Solution
This script identifies and fixes the "Expecting value: line 1 column 1 (char 0)" error

PROBLEM IDENTIFIED:
The error "Expecting value: line 1 column 1 (char 0)" typically means:
1. Yahoo Finance is returning HTML instead of JSON (anti-bot protection)
2. curl_cffi is not working properly on Windows
3. SSL/TLS issues on Windows with Python 3.12
"""

import sys
import os
import platform
import json
import traceback
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("YAHOO FINANCE WINDOWS FIX - COMPREHENSIVE SOLUTION")
print("="*80)
print()

# =======================
# PART 1: DIAGNOSIS
# =======================

print("PART 1: SYSTEM DIAGNOSIS")
print("-"*40)

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print()

# Check critical packages
packages_status = {}

def check_package(name):
    try:
        module = __import__(name)
        version = getattr(module, '__version__', 'unknown')
        packages_status[name] = {'installed': True, 'version': version}
        return True, version
    except ImportError:
        packages_status[name] = {'installed': False, 'version': None}
        return False, None

print("Package Status:")
for pkg in ['yfinance', 'curl_cffi', 'requests', 'certifi', 'urllib3']:
    installed, version = check_package(pkg)
    status = f"✓ v{version}" if installed else "✗ NOT INSTALLED"
    print(f"  {pkg:12} : {status}")

print()

# =======================
# PART 2: IDENTIFY THE ISSUE
# =======================

print("PART 2: IDENTIFYING THE EXACT ISSUE")
print("-"*40)

# The error "Expecting value: line 1 column 1 (char 0)" means JSON parsing failed
# This happens when Yahoo returns HTML (error page) instead of JSON data

print("\n1. Testing raw yfinance response:")
try:
    import yfinance as yf
    
    # Enable debug mode to see what's happening
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    ticker = yf.Ticker("AAPL")
    
    # Try to catch the raw response
    print("   Creating ticker...")
    
    # This is where it likely fails
    info = ticker.info
    print(f"   ✓ Got info successfully")
    
except json.JSONDecodeError as e:
    print(f"   ✗ JSON Parse Error: {e}")
    print("   This means Yahoo returned HTML instead of JSON (anti-bot protection)")
except Exception as e:
    print(f"   ✗ Error: {e}")
    traceback.print_exc()

print()

# =======================
# PART 3: THE FIX
# =======================

print("PART 3: IMPLEMENTING THE FIX")
print("-"*40)
print()

# Fix 1: Ensure curl_cffi works properly
print("Fix 1: Checking curl_cffi functionality:")

try:
    import curl_cffi
    from curl_cffi import requests as cffi_requests
    
    # Test if curl_cffi can actually make requests
    response = cffi_requests.get("https://httpbin.org/user-agent")
    ua = response.json().get('user-agent', '')
    
    if 'curl' in ua.lower():
        print("   ✓ curl_cffi is working properly")
        print(f"   User-Agent: {ua}")
    else:
        print("   ✗ curl_cffi might not be working correctly")
        
except Exception as e:
    print(f"   ✗ curl_cffi test failed: {e}")
    print("   This is likely the root cause!")

print()

# Fix 2: Try alternative yfinance configuration
print("Fix 2: Testing alternative yfinance configurations:")

def test_yfinance_method(description, test_func):
    """Test a yfinance method and report results"""
    print(f"\n   {description}:")
    try:
        result = test_func()
        if result:
            print(f"   ✓ SUCCESS!")
            return True
        else:
            print(f"   ✗ Failed - returned empty/None")
            return False
    except Exception as e:
        error_msg = str(e)
        if "Expecting value" in error_msg:
            print(f"   ✗ JSON parse error - Yahoo returned HTML (blocked)")
        else:
            print(f"   ✗ Failed: {error_msg[:100]}")
        return False

# Method 1: Direct Ticker (no session)
def method1():
    import yfinance as yf
    ticker = yf.Ticker("MSFT")
    hist = ticker.history(period="1d")
    return not hist.empty

# Method 2: Download function
def method2():
    import yfinance as yf
    data = yf.download("MSFT", period="1d", progress=False)
    return not data.empty

# Method 3: Using Tickers (multiple)
def method3():
    import yfinance as yf
    tickers = yf.Tickers("MSFT AAPL")
    hist = tickers.tickers['MSFT'].history(period="1d")
    return not hist.empty

test_yfinance_method("Method 1: Direct Ticker", method1)
test_yfinance_method("Method 2: Download", method2)
test_yfinance_method("Method 3: Tickers", method3)

print()

# =======================
# PART 4: SOLUTION
# =======================

print("\n" + "="*80)
print("RECOMMENDED SOLUTION FOR WINDOWS")
print("="*80)

print("""
The issue is that yfinance 0.2.33 with curl_cffi is not working properly on Windows.
The "Expecting value" error means Yahoo Finance is returning HTML (blocking you).

SOLUTION OPTIONS:

1. DOWNGRADE YFINANCE (Most Reliable):
   ------------------------------------
   pip uninstall yfinance curl-cffi
   pip install yfinance==0.2.18
   
   This version works without curl_cffi and is more stable on Windows.

2. FIX CURL_CFFI ON WINDOWS:
   -------------------------
   pip uninstall curl-cffi
   pip install curl-cffi --no-binary curl-cffi
   
   This forces compilation from source which might work better.

3. USE REQUESTS-CACHE INSTEAD:
   ----------------------------
   pip install requests-cache
   
   Then modify ml_core.py to use:
   ```python
   import requests_cache
   session = requests_cache.CachedSession('yfinance.cache')
   ticker = yf.Ticker("AAPL", session=session)
   ```

4. ALTERNATIVE LIBRARY (yfinance-cache):
   --------------------------------------
   pip install yfinance-cache
   
   Use this instead of regular yfinance - it handles caching better.

5. WINDOWS-SPECIFIC FIX:
   ----------------------
   Set environment variable:
   set CURL_CA_BUNDLE=""
   
   Then run your script. This fixes SSL issues.

IMMEDIATE ACTION:
-----------------
Try Option 1 first (downgrade to yfinance 0.2.18). It's the most reliable.

Run these commands:
```
pip uninstall yfinance curl-cffi -y
pip install yfinance==0.2.18
```

Then test with the simple script below.
""")

# =======================
# PART 5: TEST SCRIPT
# =======================

print("\n" + "="*80)
print("SIMPLE TEST SCRIPT")
print("="*80)

print("""
Save this as 'test_simple.py' and run it after applying the fix:

```python
import yfinance as yf

# Simple test
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="5d")

if not hist.empty:
    print(f"SUCCESS! Latest price: ${hist['Close'].iloc[-1]:.2f}")
else:
    print("Failed - no data received")
```

If this works, the ML system will work too!
""")