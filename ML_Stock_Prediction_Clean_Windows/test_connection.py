#!/usr/bin/env python3
"""
Test internet connection and Yahoo Finance access
"""

import requests
import yfinance as yf
import json

def test_internet():
    """Test basic internet connectivity"""
    print("Testing internet connection...")
    urls = [
        ("Google", "https://www.google.com"),
        ("Yahoo", "https://www.yahoo.com"),
        ("Yahoo Finance", "https://finance.yahoo.com")
    ]
    
    for name, url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {name}: Connected")
            else:
                print(f"  ⚠️  {name}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")
    print()

def test_yfinance_methods():
    """Test different methods to fetch data"""
    print("Testing Yahoo Finance data access methods...")
    
    symbols = ["AAPL", "MSFT", "SPY"]
    
    for symbol in symbols:
        print(f"\nTesting {symbol}:")
        
        # Method 1: Direct ticker
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                print(f"  ✅ Method 1 (info): Price ${info.get('regularMarketPrice', 'N/A')}")
            else:
                print(f"  ⚠️  Method 1 (info): Limited data")
        except Exception as e:
            print(f"  ❌ Method 1 (info): {str(e)[:50]}")
        
        # Method 2: History
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                print(f"  ✅ Method 2 (history): Got {len(hist)} rows")
            else:
                print(f"  ⚠️  Method 2 (history): No data")
        except Exception as e:
            print(f"  ❌ Method 2 (history): {str(e)[:50]}")
        
        # Method 3: Download
        try:
            data = yf.download(symbol, period="1d", progress=False)
            if not data.empty:
                print(f"  ✅ Method 3 (download): Got {len(data)} rows")
            else:
                print(f"  ⚠️  Method 3 (download): No data")
        except Exception as e:
            print(f"  ❌ Method 3 (download): {str(e)[:50]}")

def check_proxy():
    """Check if proxy settings might be needed"""
    print("\nChecking proxy settings...")
    import os
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxies_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ⚠️  {var} = {value}")
            proxies_found = True
    
    if not proxies_found:
        print("  ✅ No proxy settings detected")
    else:
        print("  ℹ️  Proxy settings found - may need configuration")

def suggest_alternatives():
    """Suggest alternative data sources"""
    print("\n" + "="*50)
    print("Alternative Solutions:")
    print("="*50)
    print("""
If Yahoo Finance is blocked or not working:

1. **Use a VPN** to bypass network restrictions

2. **Try Alpha Vantage API** (free tier available):
   - Sign up at: https://www.alphavantage.co/support/#api-key
   - Install: pip install alpha-vantage
   
3. **Use IEX Cloud** (free tier available):
   - Sign up at: https://iexcloud.io/
   - Install: pip install pyEX

4. **Try after market hours** - Sometimes works better

5. **Check firewall/antivirus** - May be blocking connections

6. **Use a different network** - Try mobile hotspot

7. **Manual data entry** - For testing, you can create CSV files
   with historical data and load them instead
""")

def main():
    print("="*60)
    print("Yahoo Finance Connection Diagnostic")
    print("="*60)
    print()
    
    test_internet()
    test_yfinance_methods()
    check_proxy()
    suggest_alternatives()
    
    print("\n" + "="*60)
    print("Diagnostic Complete")
    print("="*60)

if __name__ == "__main__":
    main()