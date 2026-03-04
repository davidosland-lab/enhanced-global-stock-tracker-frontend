#!/usr/bin/env python3
"""
FinBERT System Diagnostic Tool - FIXED VERSION
Identifies issues and stays open for reading
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

def pause():
    """Pause and wait for user input"""
    input("\nPress Enter to continue...")

print("=" * 60)
print("FinBERT v3.3 DIAGNOSTIC TOOL")
print("=" * 60)
print()

# Test 1: Check if backend is running
print("TEST 1: Checking backend server at localhost:5000...")
try:
    # First try the health endpoint (v3.3)
    try:
        response = urllib.request.urlopen('http://localhost:5000/health', timeout=5)
        data = json.loads(response.read())
        print("✅ Backend v3.3 is running:", data)
    except:
        # If health fails, try the root endpoint
        response = urllib.request.urlopen('http://localhost:5000/', timeout=5)
        if response.getcode() == 200:
            print("✅ Backend is running (v3.2 or earlier)")
        else:
            print("⚠️ Backend responded but may have issues")
except Exception as e:
    print("❌ Backend not accessible:", str(e)[:100])
    print("   Solution: Make sure app_finbert_complete_v3.2.py is running")
    print("   From your logs, the server IS running on port 5000")

# Test 2: Test the API endpoint that's working in your logs
print("\nTEST 2: Testing API endpoint (same as your browser)...")
try:
    response = urllib.request.urlopen('http://localhost:5000/api/stock/AAPL?interval=1d&period=1m', timeout=10)
    data = json.loads(response.read())
    
    print(f"✅ API endpoint working!")
    print(f"   Symbol: {data.get('symbol', 'N/A')}")
    print(f"   Current Price: ${data.get('current_price', 0):.2f}")
    print(f"   Price Change: {data.get('price_change', 0):.2f}")
    print(f"   Chart Data Points: {len(data.get('chart_data', []))}")
    
    if data.get('current_price', 0) == 0:
        print("\n⚠️ WARNING: Price is 0 - Possible issues:")
        print("   1. Market may be closed (check market hours)")
        print("   2. Yahoo Finance may be blocking requests")
        print("   3. Invalid symbol or data not available")
        
        # Check the actual chart data
        chart_data = data.get('chart_data', [])
        if chart_data and len(chart_data) > 0:
            last_point = chart_data[-1]
            print(f"\n   Last data point:")
            print(f"   Date: {last_point.get('date', 'N/A')}")
            print(f"   Close: ${last_point.get('close', 0):.2f}")
            
except urllib.error.HTTPError as e:
    print(f"❌ API HTTP Error {e.code}: {e.reason}")
except Exception as e:
    print(f"❌ API error: {str(e)[:200]}")

# Test 3: Direct Yahoo Finance test
print("\nTEST 3: Testing direct Yahoo Finance access...")
try:
    url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read())
    
    if 'chart' in data and 'result' in data['chart']:
        result = data['chart']['result'][0]
        meta = result.get('meta', {})
        price = meta.get('regularMarketPrice', 0)
        
        if price > 0:
            print(f"✅ Yahoo Finance API working - AAPL: ${price:.2f}")
        else:
            print("⚠️ Yahoo Finance returned 0 price")
            print("   Possible reasons:")
            print("   - Market is closed (after hours)")
            print("   - API temporarily unavailable")
            print("   - Rate limiting in effect")
            
            # Try to get previous close
            prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
            if prev_close > 0:
                print(f"   Previous close available: ${prev_close:.2f}")
    else:
        print("❌ Yahoo Finance returned unexpected format")
        
except Exception as e:
    print(f"❌ Yahoo Finance error: {str(e)[:200]}")

# Test 4: Check for 3m interval issue
print("\nTEST 4: Testing problematic 3m interval...")
try:
    response = urllib.request.urlopen('http://localhost:5000/api/stock/AAPL?interval=3m&period=1d', timeout=10)
    data = json.loads(response.read())
    
    if data.get('chart_data'):
        print(f"✅ 3m interval working - {len(data['chart_data'])} data points")
    else:
        print("❌ 3m interval returns no data")
        print("   Note: Yahoo doesn't support 3m, should convert to 5m")
        
except Exception as e:
    print(f"❌ 3m interval error: {str(e)[:100]}")

# Test 5: Browser cache check
print("\nTEST 5: Common browser issues...")
print("   If data loads in logs but shows 0.00 in browser:")
print("   1. Clear browser cache (Ctrl+Shift+Delete)")
print("   2. Open Developer Tools (F12)")
print("   3. Go to Network tab")
print("   4. Check 'Disable cache' checkbox")
print("   5. Refresh the page (F5)")

# Test 6: Check your specific stock
print("\nTEST 6: Testing CBA.AX (from your logs)...")
try:
    response = urllib.request.urlopen('http://localhost:5000/api/stock/CBA.AX?interval=1d&period=1m', timeout=10)
    data = json.loads(response.read())
    
    print(f"✅ CBA.AX data retrieved")
    print(f"   Current Price: ${data.get('current_price', 0):.2f}")
    
    if data.get('current_price', 0) == 0:
        print("   ⚠️ Price is 0 - ASX market may be closed")
        
except Exception as e:
    print(f"❌ CBA.AX error: {str(e)[:100]}")

# Summary and recommendations
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

print("""
Based on your server logs, the backend IS working correctly:
- Server is running on port 5000 ✅
- API requests are returning 200 OK ✅
- Both AAPL and CBA.AX requests successful ✅

The issue appears to be:
1. The frontend is showing 0.00 even when data is returned
2. This is likely a JavaScript/display issue

RECOMMENDED FIXES:
==================

1. IMMEDIATE FIX - Use the HOTFIX version:
   python app_finbert_v3.3_hotfix.py
   
   This version handles 0 prices better and has fallback data.

2. BROWSER FIX - Clear everything:
   - Press Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Select "Cookies and other site data"
   - Clear data
   - Restart browser
   - Try Incognito/Private mode

3. CHECK CONSOLE - In browser:
   - Press F12 for Developer Tools
   - Click Console tab
   - Look for red error messages
   - Take a screenshot if errors appear

4. TEST WITH CURL - Check raw API response:
   Open Command Prompt and run:
   curl http://localhost:5000/api/stock/AAPL?interval=1d
   
   This will show the actual data being returned.

5. MARKET HOURS CHECK:
   - US Market: 9:30 AM - 4:00 PM EST
   - ASX (CBA.AX): 10:00 AM - 4:00 PM AEST
   - Outside these hours, current price may be 0

Your backend is WORKING. The issue is likely in the frontend
display or browser caching. Try the HOTFIX version for best results.
""")

print("\n" + "=" * 60)
pause()  # Keep window open