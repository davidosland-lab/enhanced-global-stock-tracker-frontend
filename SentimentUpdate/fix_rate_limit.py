#!/usr/bin/env python3
"""
Fix Yahoo Finance Rate Limiting Issues
"""

import os
import sys
import time
import random

print("=" * 60)
print("FIXING YAHOO FINANCE RATE LIMIT (429 ERROR)")
print("=" * 60)
print()

print("The 429 error means Yahoo is blocking you due to too many requests.")
print("This is temporary and will clear after waiting.")
print()

print("SOLUTIONS:")
print("-" * 40)
print()

print("1. IMMEDIATE FIX - Wait for rate limit to reset:")
print("   Yahoo typically resets limits after 1-2 hours")
print("   Current time:", time.strftime("%Y-%m-%d %H:%M:%S"))
print("   Try again after:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 3600)))
print()

print("2. USE ALPHA VANTAGE INSTEAD:")
print("   Alpha Vantage is already configured with your API key")
print("   It's more reliable but slightly slower")
print()

print("3. USE A VPN:")
print("   Yahoo rate limits by IP address")
print("   Switching to a VPN will give you a new IP")
print()

print("4. CLEAR COOKIES AND CACHE:")
print("   Sometimes Yahoo uses cookies for rate limiting")
print()

# Clear any Python cache
import shutil
cache_dirs = [
    os.path.expanduser("~/.cache/py-yfinance"),
    os.path.expanduser("~/.cache/yfinance"),
    os.path.join(os.getcwd(), "__pycache__"),
    os.path.join(os.getcwd(), ".cache")
]

for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✓ Cleared cache: {cache_dir}")
        except:
            pass

print()
print("5. TESTING ALPHA VANTAGE:")
print("-" * 40)

try:
    import requests
    api_key = "68ZFANK047DL0KSR"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
    
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if 'Global Quote' in data:
        price = data['Global Quote'].get('05. price', 'N/A')
        print(f"   ✓ Alpha Vantage working! AAPL: ${price}")
        print("   You can use Alpha Vantage while Yahoo is rate limited")
    else:
        print(f"   ⚠ Alpha Vantage response: {data}")
except Exception as e:
    print(f"   ✗ Alpha Vantage error: {e}")

print()
print("=" * 60)
print("RECOMMENDED ACTION:")
print("=" * 60)
print()
print("Since Yahoo is rate limiting you (429 error), do one of:")
print()
print("A) Wait 1-2 hours for the rate limit to reset")
print("B) Use a VPN to get a new IP address") 
print("C) Use the Alpha Vantage version (see below)")
print()
print("To use Alpha Vantage as primary source, run:")
print("   python app_alphavantage_primary.py")
print()
print("=" * 60)