#!/usr/bin/env python3
"""
Check what Yahoo Finance is actually returning
This will show the raw response to understand why it's failing
"""

import requests
import json

print("="*70)
print("CHECKING YAHOO FINANCE RAW RESPONSE")
print("="*70)
print()

# Test 1: Check the actual API response
print("Test 1: Raw API Response")
print("-"*40)

url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        try:
            data = response.json()
            if 'chart' in data:
                if 'error' in data['chart'] and data['chart']['error']:
                    print("ERROR FROM YAHOO:")
                    print(json.dumps(data['chart']['error'], indent=2))
                elif 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    print("SUCCESS! Data received:")
                    print(f"  Symbol: {result['meta']['symbol']}")
                    print(f"  Price: ${result['meta'].get('regularMarketPrice', 'N/A')}")
                else:
                    print("Unexpected response structure:")
                    print(json.dumps(data, indent=2)[:500])
            else:
                print("No 'chart' in response. Full response:")
                print(json.dumps(data, indent=2)[:500])
        except json.JSONDecodeError:
            print("Response is not JSON. First 500 chars:")
            print(response.text[:500])
    else:
        print(f"HTTP Error {response.status_code}")
        print("Response body (first 500 chars):")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("ERROR: Request timed out (network issue or blocked)")
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection failed - {e}")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Test 2: Check yfinance's actual error
print("Test 2: yfinance Detailed Error")
print("-"*40)

import yfinance as yf
import logging

# Enable debug logging to see what yfinance is doing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('yfinance')
logger.setLevel(logging.DEBUG)

try:
    # Try to download with debug info
    print("Attempting to download AAPL data with debug logging...")
    data = yf.download('AAPL', period='5d', progress=False, threads=False)
    
    if data.empty:
        print("Download returned empty DataFrame")
        
        # Try Ticker method for more details
        print("\nTrying Ticker method for more details...")
        ticker = yf.Ticker('AAPL')
        
        # Check if we can get info
        try:
            info = ticker.info
            print(f"Ticker.info returned: {info}")
        except Exception as e:
            print(f"Ticker.info error: {e}")
            
        # Check history
        try:
            hist = ticker.history(period='5d')
            print(f"Ticker.history returned: {hist}")
        except Exception as e:
            print(f"Ticker.history error: {e}")
    else:
        print(f"Success! Got {len(data)} rows of data")
        
except Exception as e:
    print(f"Error during download: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("DIAGNOSIS")
print("="*70)

print("""
What the errors mean:

1. "No data found for this date range, symbol may be delisted"
   - This is yfinance's generic error when it can't get data
   - Does NOT mean the symbol is actually delisted

2. If Status Code is 429:
   - You are rate-limited
   
3. If Status Code is 403:
   - Your IP is blocked or you need authentication

4. If Status Code is 200 but no data:
   - Yahoo returned an error in the JSON response
   
5. If Connection times out:
   - Network issue or IP is completely blocked

Run this script to see what's actually happening!
""")