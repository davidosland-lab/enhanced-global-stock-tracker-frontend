#!/usr/bin/env python3
"""
Network Diagnostic Tool for Stock Analysis
Identifies and fixes connectivity issues
"""

import sys
import os
import time
import json
import requests
from datetime import datetime

print("=" * 70)
print("NETWORK DIAGNOSTIC FOR STOCK ANALYSIS")
print("=" * 70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# Test basic connectivity
print("1. TESTING INTERNET CONNECTIVITY")
print("-" * 40)

test_urls = [
    ("Google", "https://www.google.com"),
    ("GitHub", "https://api.github.com"),
    ("Yahoo", "https://finance.yahoo.com"),
]

internet_ok = False
for name, url in test_urls:
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ {name:<15} Status: {response.status_code}")
        internet_ok = True
    except requests.exceptions.Timeout:
        print(f"✗ {name:<15} TIMEOUT")
    except requests.exceptions.ConnectionError:
        print(f"✗ {name:<15} CONNECTION ERROR")
    except Exception as e:
        print(f"✗ {name:<15} ERROR: {str(e)[:30]}")

if not internet_ok:
    print("\n⚠ WARNING: No internet connectivity detected!")
    print("Please check your network connection.")
    sys.exit(1)

print()
print("2. TESTING YAHOO FINANCE API")
print("-" * 40)

# Test different Yahoo Finance endpoints
yahoo_tests = [
    ("Direct API v8", "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"),
    ("Direct API v7", "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL"),
    ("Alternative API", "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"),
]

yahoo_working = None
for name, url in yahoo_tests:
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            print(f"✓ {name:<20} Working!")
            yahoo_working = url
            break
        else:
            print(f"⚠ {name:<20} Status: {response.status_code}")
    except Exception as e:
        print(f"✗ {name:<20} Error: {str(e)[:30]}")

print()
print("3. TESTING WITH YFINANCE LIBRARY")
print("-" * 40)

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
    
    # Test with timeout and retries
    ticker = yf.Ticker("AAPL")
    
    # Try to get data with different methods
    methods = [
        ("history(1d)", lambda: ticker.history(period="1d")),
        ("history(5d)", lambda: ticker.history(period="5d")),
        ("info", lambda: ticker.info),
    ]
    
    for method_name, method_func in methods:
        try:
            result = method_func()
            if result is not None and (not hasattr(result, 'empty') or not result.empty):
                print(f"✓ {method_name:<15} Success!")
            else:
                print(f"⚠ {method_name:<15} Empty result")
        except Exception as e:
            error_msg = str(e)
            if "Expecting value" in error_msg:
                print(f"✗ {method_name:<15} JSON parse error (API may be blocked)")
            else:
                print(f"✗ {method_name:<15} {error_msg[:40]}")
            
except ImportError:
    print("✗ yfinance not installed")
except Exception as e:
    print(f"✗ yfinance error: {e}")

print()
print("4. TESTING ALPHA VANTAGE API")
print("-" * 40)

api_key = "68ZFANK047DL0KSR"
av_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={api_key}&outputsize=compact"

try:
    response = requests.get(av_url, timeout=10)
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        print("✓ Alpha Vantage API working!")
        print(f"  Latest data points: {len(data['Time Series (Daily)'])}")
    elif 'Note' in data:
        print("⚠ Alpha Vantage rate limit reached")
        print(f"  Message: {data['Note'][:50]}")
    elif 'Error Message' in data:
        print("✗ Alpha Vantage error")
        print(f"  Message: {data['Error Message'][:50]}")
    else:
        print("⚠ Alpha Vantage unexpected response")
except Exception as e:
    print(f"✗ Alpha Vantage error: {e}")

print()
print("=" * 70)
print("DIAGNOSTIC RESULTS")
print("=" * 70)

# Provide recommendations
print("\nRECOMMENDATIONS:")
print("-" * 40)

if not yahoo_working:
    print("⚠ Yahoo Finance appears to be blocked or rate-limited")
    print("  Solutions:")
    print("  1. Wait 15-30 minutes (rate limit may reset)")
    print("  2. Use a VPN to change your IP address")
    print("  3. Use the robust version: python app_enhanced_sentiment_robust.py")
    print("  4. The robust version will use Alpha Vantage or demo data")
else:
    print("✓ Yahoo Finance is accessible")
    print("  If yfinance still fails, try:")
    print("  1. Update yfinance: pip install --upgrade yfinance")
    print("  2. Clear yfinance cache: delete .cache folder")

print()
print("QUICK FIXES TO TRY:")
print("-" * 40)
print("1. Update yfinance:")
print("   pip install --upgrade yfinance")
print()
print("2. Use robust version (handles all errors):")
print("   python app_enhanced_sentiment_robust.py")
print()
print("3. Use no-sklearn version (simpler, fewer dependencies):")
print("   python app_sentiment_no_sklearn.py")
print()
print("4. If all APIs fail, the robust version will use demo data")
print()

# Test if we can at least generate demo data
print("5. TESTING DEMO DATA GENERATION")
print("-" * 40)

try:
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=10)
    data = []
    for date in dates:
        data.append({
            'Open': 100.0,
            'High': 101.0,
            'Low': 99.0,
            'Close': 100.5,
            'Volume': 1000000
        })
    df = pd.DataFrame(data, index=dates)
    
    if not df.empty:
        print("✓ Demo data generation works!")
        print("  The robust version will use this if APIs fail")
    else:
        print("✗ Demo data generation failed")
        
except Exception as e:
    print(f"✗ Demo data error: {e}")

print()
print("=" * 70)
print("Diagnostic complete!")
print("=" * 70)