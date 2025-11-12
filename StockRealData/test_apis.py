#!/usr/bin/env python3
"""
API Connection Tester - Diagnose why data fetching fails
"""

import sys
import json
import requests
import yfinance as yf
from datetime import datetime, timedelta

def test_internet():
    """Test basic internet connectivity"""
    print("Testing internet connection...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print("✓ Internet connection OK")
        return True
    except:
        print("✗ No internet connection")
        return False

def test_yahoo_finance():
    """Test Yahoo Finance API"""
    print("\n" + "="*60)
    print("Testing Yahoo Finance...")
    print("="*60)
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in symbols:
        print(f"\nTesting {symbol}:")
        
        # Method 1: Ticker
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info:
                print(f"  ✓ Ticker.info works - Price: ${info.get('currentPrice', 'N/A')}")
            else:
                print(f"  ✗ Ticker.info returned empty")
        except Exception as e:
            print(f"  ✗ Ticker.info failed: {str(e)[:100]}")
        
        # Method 2: History
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            if not hist.empty:
                print(f"  ✓ Ticker.history works - Got {len(hist)} data points")
                print(f"    Latest close: ${hist['Close'].iloc[-1]:.2f}")
            else:
                print(f"  ✗ Ticker.history returned empty")
        except Exception as e:
            print(f"  ✗ Ticker.history failed: {str(e)[:100]}")
        
        # Method 3: Download
        try:
            end = datetime.now()
            start = end - timedelta(days=7)
            data = yf.download(symbol, start=start, end=end, progress=False)
            if not data.empty:
                print(f"  ✓ yf.download works - Got {len(data)} data points")
            else:
                print(f"  ✗ yf.download returned empty")
        except Exception as e:
            print(f"  ✗ yf.download failed: {str(e)[:100]}")

def test_alpha_vantage():
    """Test Alpha Vantage API"""
    print("\n" + "="*60)
    print("Testing Alpha Vantage...")
    print("="*60)
    
    api_key = "68ZFANK047DL0KSR"
    symbol = "AAPL"
    
    # Test 1: Daily data
    print("\nTesting daily data endpoint:")
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': api_key,
        'datatype': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            print(f"  ✗ API Error: {data['Error Message']}")
        elif 'Note' in data:
            print(f"  ✗ API Limit: {data['Note']}")
        elif 'Time Series (Daily)' in data:
            ts = data['Time Series (Daily)']
            dates = list(ts.keys())[:5]
            print(f"  ✓ Daily data works - Got {len(ts)} days")
            print(f"    Latest date: {dates[0]}")
            print(f"    Latest close: ${ts[dates[0]]['4. close']}")
        else:
            print(f"  ✗ Unexpected response structure")
            print(f"    Keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)[:100]}")
    
    # Test 2: API key validation
    print("\nTesting API key validity:")
    test_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey={api_key}"
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'Error Message' not in data and 'Note' not in data:
                print(f"  ✓ API key is valid")
            else:
                print(f"  ✗ API key issue or rate limit")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Connection failed: {str(e)[:100]}")

def test_proxy_settings():
    """Check for proxy settings that might block connections"""
    print("\n" + "="*60)
    print("Checking proxy settings...")
    print("="*60)
    
    import os
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxies_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"  Found {var}: {value}")
            proxies_found = True
    
    if not proxies_found:
        print("  No proxy settings found (good)")
    else:
        print("\n  ⚠ Proxy settings detected. This might block API access.")
        print("  Try running: set HTTP_PROXY= && set HTTPS_PROXY=")

def suggest_fixes():
    """Suggest fixes based on test results"""
    print("\n" + "="*60)
    print("SUGGESTED FIXES")
    print("="*60)
    
    print("""
1. FIREWALL/ANTIVIRUS:
   - Temporarily disable Windows Defender/antivirus
   - Add Python to firewall exceptions
   - Check if corporate firewall blocks finance APIs

2. NETWORK ISSUES:
   - Try using a different network (mobile hotspot)
   - Check if VPN is blocking connections
   - Clear DNS cache: ipconfig /flushdns

3. ALTERNATIVE DATA SOURCE:
   - Use financial data CSV files for testing
   - Try different stock symbols (SPY, QQQ)
   - Use market hours data only (9:30 AM - 4 PM EST)

4. MANUAL TEST:
   Open browser and try:
   - https://query1.finance.yahoo.com/v8/finance/chart/AAPL
   - https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=68ZFANK047DL0KSR
   
   If these don't work in browser, it's a network issue.
""")

def main():
    print("="*60)
    print("STOCK ANALYSIS SYSTEM - API DIAGNOSTICS")
    print("="*60)
    print(f"Testing at: {datetime.now()}")
    print(f"Python: {sys.version}")
    
    # Run tests
    if not test_internet():
        print("\n✗ No internet connection - cannot proceed")
        return
    
    test_yahoo_finance()
    test_alpha_vantage()
    test_proxy_settings()
    suggest_fixes()
    
    print("\n" + "="*60)
    print("Diagnostics complete!")
    print("="*60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")