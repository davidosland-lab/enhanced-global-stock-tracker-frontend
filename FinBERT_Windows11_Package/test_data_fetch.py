#!/usr/bin/env python3
"""
Diagnostic tool to test data fetching and identify issues
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("DATA FETCHING DIAGNOSTIC TOOL")
print("=" * 70)
print()

# Test imports
print("1. TESTING IMPORTS")
print("-" * 40)

required_packages = {
    'pandas': 'pandas',
    'numpy': 'numpy', 
    'yfinance': 'yfinance',
    'requests': 'requests',
    'flask': 'flask',
    'sklearn': 'scikit-learn',
    'feedparser': 'feedparser',
    'bs4': 'beautifulsoup4'
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} is NOT installed")
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠ Install missing packages with:")
    print(f"pip install {' '.join(missing_packages)}")
    print()

# Test yfinance data fetching
print("\n2. TESTING YAHOO FINANCE DATA FETCHING")
print("-" * 40)

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'SPY', 'QQQ', 'BTC-USD', 'GC=F', '^VIX']

for symbol in test_symbols:
    try:
        print(f"\nTesting {symbol}...")
        ticker = yf.Ticker(symbol)
        
        # Test different periods
        periods = ['1d', '5d', '1mo', '3mo', '6mo']
        for period in periods:
            try:
                df = ticker.history(period=period)
                if not df.empty:
                    print(f"  ✓ {period}: {len(df)} rows fetched")
                    if period == '1mo':  # Show sample data
                        print(f"    Latest close: ${df['Close'].iloc[-1]:.2f}")
                        print(f"    Date range: {df.index[0].date()} to {df.index[-1].date()}")
                else:
                    print(f"  ✗ {period}: No data returned")
            except Exception as e:
                print(f"  ✗ {period}: Error - {str(e)[:50]}")
                
        # Test ticker info
        try:
            info = ticker.info
            if info:
                print(f"  ✓ Ticker info available")
                print(f"    Name: {info.get('shortName', 'N/A')}")
                print(f"    Market Cap: {info.get('marketCap', 'N/A')}")
        except:
            print(f"  ⚠ Ticker info not available")
            
    except Exception as e:
        print(f"✗ Failed to fetch {symbol}: {e}")

# Test alternative data fetching method
print("\n3. TESTING ALTERNATIVE DATA FETCH METHOD")
print("-" * 40)

def fetch_with_fallback(symbol, period='1mo'):
    """Try multiple methods to fetch data"""
    import yfinance as yf
    import pandas as pd
    
    methods_tried = []
    
    # Method 1: Standard yfinance
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if not df.empty:
            return df, "Standard yfinance"
    except Exception as e:
        methods_tried.append(f"yfinance: {str(e)[:30]}")
    
    # Method 2: Download function
    try:
        df = yf.download(symbol, period=period, progress=False)
        if not df.empty:
            return df, "yfinance.download"
    except Exception as e:
        methods_tried.append(f"download: {str(e)[:30]}")
    
    # Method 3: Specific date range
    try:
        end_date = datetime.now()
        if period == '1mo':
            start_date = end_date - timedelta(days=30)
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
        else:
            start_date = end_date - timedelta(days=365)
            
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if not df.empty:
            return df, "Date range download"
    except Exception as e:
        methods_tried.append(f"date range: {str(e)[:30]}")
    
    return None, methods_tried

# Test with common symbols
test_cases = [
    ('AAPL', '1mo'),
    ('MSFT', '3mo'),
    ('SPY', '6mo'),
    ('BTC-USD', '1mo')
]

for symbol, period in test_cases:
    print(f"\nTesting {symbol} for {period}:")
    data, method = fetch_with_fallback(symbol, period)
    if data is not None:
        print(f"  ✓ Success using: {method}")
        print(f"    Data shape: {data.shape}")
        print(f"    Columns: {list(data.columns)}")
    else:
        print(f"  ✗ All methods failed")
        for error in method:
            print(f"    - {error}")

# Test network connectivity
print("\n4. TESTING NETWORK CONNECTIVITY")
print("-" * 40)

import requests

test_urls = [
    ('Yahoo Finance', 'https://finance.yahoo.com'),
    ('Google', 'https://www.google.com'),
    ('GitHub', 'https://api.github.com'),
]

for name, url in test_urls:
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ {name}: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"✗ {name}: Connection failed")
    except requests.exceptions.Timeout:
        print(f"✗ {name}: Timeout")
    except Exception as e:
        print(f"✗ {name}: {e}")

# Check for proxy settings
print("\n5. CHECKING PROXY SETTINGS")
print("-" * 40)

proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
proxy_found = False

for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"⚠ {var} is set: {value}")
        proxy_found = True

if not proxy_found:
    print("✓ No proxy settings detected")
else:
    print("\n⚠ Proxy settings might interfere with data fetching")
    print("  You may need to configure yfinance to use the proxy")

# Test minimum data requirements
print("\n6. TESTING MINIMUM DATA REQUIREMENTS")
print("-" * 40)

def check_data_sufficiency(df):
    """Check if DataFrame has enough data for training"""
    if df is None or df.empty:
        return False, "No data"
    
    if len(df) < 100:
        return False, f"Only {len(df)} rows (need 100+)"
    
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {missing}"
    
    # Check for NaN values
    nan_counts = df[required_columns].isna().sum()
    if nan_counts.sum() > len(df) * 0.1:  # More than 10% NaN
        return False, f"Too many NaN values: {nan_counts.to_dict()}"
    
    return True, f"{len(df)} rows with all required columns"

print("\nChecking AAPL data sufficiency:")
try:
    ticker = yf.Ticker('AAPL')
    for period in ['1mo', '3mo', '6mo', '1y']:
        df = ticker.history(period=period)
        sufficient, message = check_data_sufficiency(df)
        if sufficient:
            print(f"  ✓ {period}: {message}")
        else:
            print(f"  ✗ {period}: {message}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Provide solutions
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY AND SOLUTIONS")
print("=" * 70)

if missing_packages:
    print("\n1. MISSING PACKAGES")
    print("   Run this command:")
    print(f"   pip install {' '.join(missing_packages)}")

print("\n2. COMMON FIXES FOR 'INSUFFICIENT DATA' ERROR:")
print("   a) Try a longer time period (6mo or 1y instead of 1mo)")
print("   b) Use well-known symbols (AAPL, MSFT, SPY)")
print("   c) Check if markets are open (data might be delayed)")
print("   d) Clear yfinance cache:")
print("      - Windows: Delete C:\\Users\\<username>\\AppData\\Local\\py-yfinance")
print("      - Or run: yfinance.cache.clear()")

print("\n3. IF BEHIND CORPORATE FIREWALL/PROXY:")
print("   Set proxy in your script:")
print("   ```python")
print("   import yfinance as yf")
print("   yf.set_proxy('http://your-proxy:port')")
print("   ```")

print("\n4. ALTERNATIVE: USE MANUAL DATA")
print("   If yfinance is blocked, you can:")
print("   a) Download CSV from Yahoo Finance manually")
print("   b) Use alternative data sources (Alpha Vantage, IEX Cloud)")
print("   c) Use cached/offline data for testing")

print("\n" + "=" * 70)
print("Run this diagnostic to identify your specific issue!")
print("=" * 70)