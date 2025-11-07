#!/usr/bin/env python3
"""
FinBERT System Diagnostic Tool
Identifies and fixes common issues
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

print("=" * 60)
print("FinBERT v3.3 DIAGNOSTIC TOOL")
print("=" * 60)
print()

# Test 1: Check if backend is running
print("TEST 1: Checking backend server...")
try:
    response = urllib.request.urlopen('http://localhost:5000/health', timeout=5)
    data = json.loads(response.read())
    print("✅ Backend is running:", data)
except Exception as e:
    print("❌ Backend not accessible:", str(e))
    print("   Solution: Make sure app_finbert_complete_v3.2.py is running")
    print()

# Test 2: Check Yahoo Finance API
print("\nTEST 2: Testing Yahoo Finance API...")
symbol = 'AAPL'
try:
    # Test daily data
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read())
    
    if 'chart' in data and 'result' in data['chart']:
        result = data['chart']['result'][0]
        price = result['meta'].get('regularMarketPrice', 0)
        print(f"✅ Yahoo Finance working - AAPL price: ${price:.2f}")
    else:
        print("❌ Yahoo Finance returned unexpected format")
except urllib.error.HTTPError as e:
    print(f"❌ Yahoo Finance HTTP Error {e.code}: {e.reason}")
    if e.code == 404:
        print("   The API endpoint may have changed")
except Exception as e:
    print(f"❌ Yahoo Finance error: {e}")

# Test 3: Test intraday data
print("\nTEST 3: Testing intraday data (3m interval)...")
try:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read())
    
    if 'chart' in data and 'result' in data['chart']:
        result = data['chart']['result'][0]
        timestamps = result.get('timestamp', [])
        if timestamps:
            print(f"✅ Intraday data working - {len(timestamps)} data points")
        else:
            print("❌ No intraday data returned")
    else:
        print("❌ Intraday API returned unexpected format")
except Exception as e:
    print(f"❌ Intraday data error: {e}")

# Test 4: Check API endpoint
print("\nTEST 4: Testing Flask API endpoint...")
try:
    response = urllib.request.urlopen('http://localhost:5000/api/stock/AAPL?interval=1d&period=1m', timeout=10)
    data = json.loads(response.read())
    
    if 'current_price' in data:
        print(f"✅ API endpoint working - Price: ${data['current_price']:.2f}")
        if data['current_price'] == 0:
            print("   ⚠️  WARNING: Price is 0 - data fetch may be failing")
    else:
        print("❌ API response missing expected fields")
        print("   Response keys:", list(data.keys())[:5])
except urllib.error.HTTPError as e:
    print(f"❌ API HTTP Error {e.code}: {e.reason}")
    if e.code == 404:
        print("   The endpoint /api/stock/<symbol> is not found")
        print("   Make sure you're using the correct backend file")
except Exception as e:
    print(f"❌ API error: {e}")

# Test 5: Check for common issues
print("\nTEST 5: Checking for common issues...")

# Check if port 5000 is in use
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5000))
if result == 0:
    print("✅ Port 5000 is active")
else:
    print("❌ Port 5000 is not responding")
    print("   Solution: Start the backend with: python app_finbert_complete_v3.2.py")
sock.close()

# Test 6: Quick fix attempt
print("\n" + "=" * 60)
print("ATTEMPTING QUICK FIX...")
print("=" * 60)

# Create a simple test endpoint
test_code = '''
import json
import urllib.request
from datetime import datetime

def test_yahoo_direct():
    """Direct test of Yahoo Finance"""
    try:
        symbol = 'AAPL'
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        if 'chart' in data and 'result' in data['chart']:
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return {"success": True, "price": price, "symbol": symbol}
        return {"success": False, "error": "Invalid response format"}
    except Exception as e:
        return {"success": False, "error": str(e)}

result = test_yahoo_direct()
print(json.dumps(result, indent=2))
'''

print("\nTesting direct Yahoo Finance access...")
import subprocess
try:
    result = subprocess.run([sys.executable, '-c', test_code], 
                          capture_output=True, text=True, timeout=10)
    if result.stdout:
        data = json.loads(result.stdout)
        if data.get('success'):
            print(f"✅ Direct access works - Price: ${data['price']:.2f}")
        else:
            print(f"❌ Direct access failed: {data.get('error')}")
    else:
        print("❌ No output from direct test")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}")
except Exception as e:
    print(f"❌ Test failed: {e}")

# Final recommendations
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY & RECOMMENDATIONS")
print("=" * 60)

print("""
Based on the tests above, here are the recommended actions:

1. If backend is not running:
   - Run: python app_finbert_complete_v3.2.py
   
2. If Yahoo Finance is blocked:
   - Check your firewall/antivirus settings
   - Try using a VPN
   - Yahoo may be rate-limiting your IP
   
3. If data shows as 0.00:
   - The market may be closed
   - Try a different symbol (MSFT, GOOGL)
   - Clear browser cache (Ctrl+Shift+Delete)
   
4. If charts won't load:
   - Open browser console (F12) and check for errors
   - Make sure JavaScript is enabled
   - Try a different browser
   
5. Common fix that often works:
   - Stop the backend (Ctrl+C)
   - Clear browser cache
   - Restart the backend
   - Use Incognito/Private mode
   - Access http://localhost:5000
""")

print("Diagnostic complete!")