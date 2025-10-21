#!/usr/bin/env python3
"""
Yahoo Finance Bypass - Alternative Data Fetching Methods
This script tries multiple methods to get around Yahoo Finance blocking
"""

import sys
import time
import json
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("YAHOO FINANCE BYPASS - Testing Alternative Methods")
print("="*70)
print()

# Method 1: Try with requests directly
print("Method 1: Direct API call with requests")
print("-"*40)
try:
    import requests
    
    # Yahoo Finance API endpoint
    url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
    
    # Try different user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Yahoo Finance/1.0'
    ]
    
    for ua in user_agents:
        headers = {'User-Agent': ua}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    price = result['meta']['regularMarketPrice']
                    print(f"✓ SUCCESS with UA: {ua[:30]}...")
                    print(f"  AAPL Current Price: ${price:.2f}")
                    break
            else:
                print(f"✗ Status {response.status_code} with UA: {ua[:30]}...")
        except Exception as e:
            print(f"✗ Failed with UA {ua[:30]}...: {str(e)[:50]}")
    
except Exception as e:
    print(f"✗ Method 1 failed: {e}")

print()

# Method 2: Try with different yfinance approach
print("Method 2: yfinance with session and headers")
print("-"*40)
try:
    import yfinance as yf
    from requests import Session
    
    session = Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    ticker = yf.Ticker("MSFT", session=session)
    hist = ticker.history(period="1d")
    
    if not hist.empty:
        print(f"✓ SUCCESS! MSFT price: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("✗ No data returned")
        
except Exception as e:
    print(f"✗ Method 2 failed: {e}")

print()

# Method 3: Clear cache and try again
print("Method 3: Clear cache and retry")
print("-"*40)
try:
    import os
    import shutil
    
    # Clear yfinance cache
    cache_dirs = [
        os.path.join(os.path.expanduser('~'), '.cache', 'py-yfinance'),
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'py-yfinance'),
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
            print(f"  Cleared cache: {cache_dir}")
    
    # Try again with clean cache
    import yfinance as yf
    
    # Use Ticker without session
    ticker = yf.Ticker("GOOGL")
    info = ticker.info
    
    if info and 'regularMarketPrice' in info:
        print(f"✓ SUCCESS! GOOGL price: ${info['regularMarketPrice']:.2f}")
    else:
        # Try history as fallback
        hist = ticker.history(period="1d")
        if not hist.empty:
            print(f"✓ SUCCESS! GOOGL price: ${hist['Close'].iloc[-1]:.2f}")
        else:
            print("✗ No data returned")
            
except Exception as e:
    print(f"✗ Method 3 failed: {e}")

print()

# Method 4: Use download with specific dates
print("Method 4: Download with specific date range")
print("-"*40)
try:
    import yfinance as yf
    from datetime import datetime, timedelta
    
    end = datetime.now()
    start = end - timedelta(days=7)
    
    data = yf.download(
        "TSLA",
        start=start.strftime('%Y-%m-%d'),
        end=end.strftime('%Y-%m-%d'),
        progress=False,
        threads=False,
        group_by=None,
        auto_adjust=True,
        prepost=False
    )
    
    if not data.empty:
        print(f"✓ SUCCESS! TSLA price: ${data['Close'].iloc[-1]:.2f}")
        print(f"  Got {len(data)} days of data")
    else:
        print("✗ No data returned")
        
except Exception as e:
    print(f"✗ Method 4 failed: {e}")

print()

# Method 5: Try older API endpoint
print("Method 5: Try legacy Yahoo Finance endpoint")
print("-"*40)
try:
    import requests
    import pandas as pd
    
    symbol = "AMZN"
    url = f"https://finance.yahoo.com/quote/{symbol}/history"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Try to extract price from HTML
        import re
        price_match = re.search(r'data-symbol="' + symbol + r'"[^>]*data-field="regularMarketPrice"[^>]*>([0-9,]+\.[0-9]+)', response.text)
        if price_match:
            price = float(price_match.group(1).replace(',', ''))
            print(f"✓ Found AMZN price from HTML: ${price:.2f}")
        else:
            print("✗ Could not extract price from HTML")
    else:
        print(f"✗ Got status code: {response.status_code}")
        
except Exception as e:
    print(f"✗ Method 5 failed: {e}")

print()
print("="*70)
print("RECOMMENDATIONS BASED ON RESULTS:")
print("="*70)

print("""
If ALL methods failed:
1. Yahoo Finance is actively blocking your IP address
2. You're behind a restrictive firewall/proxy
3. Your ISP is blocking financial data sites

SOLUTIONS:
- Wait 1-24 hours for rate limit to reset
- Use a VPN to change your IP address
- Try from a different network (mobile hotspot)
- Contact your network administrator if on corporate network

If SOME methods worked:
- Use the working method in your code
- The issue is with specific yfinance versions or methods
""")

# Save working configuration if any
print("\nTesting which configuration works best...")
working_configs = []

# Test each configuration
configs = [
    ("yf.download", "yf.download('AAPL', period='5d', progress=False)"),
    ("yf.Ticker", "yf.Ticker('AAPL').history(period='5d')"),
    ("yf.Ticker.info", "yf.Ticker('AAPL').info")
]

import yfinance as yf
for name, code in configs:
    try:
        result = eval(code)
        if result is not None and (hasattr(result, 'empty') and not result.empty or result):
            working_configs.append(name)
            print(f"✓ {name} works")
    except:
        print(f"✗ {name} doesn't work")

if working_configs:
    print(f"\nWORKING CONFIGURATIONS: {', '.join(working_configs)}")
    print("Update your code to use these methods.")
else:
    print("\nNO WORKING CONFIGURATION FOUND")
    print("This is a network/IP blocking issue, not a code issue.")
    print("You need to resolve the network problem first.")