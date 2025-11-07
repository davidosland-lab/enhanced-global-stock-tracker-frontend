#!/usr/bin/env python3
"""
Check what data is ACTUALLY being returned by the backend
"""

import urllib.request
import json
from datetime import datetime

print("Checking ACTUAL API response...\n")

try:
    # Test the exact same call from your logs
    response = urllib.request.urlopen('http://localhost:5000/api/stock/AAPL?interval=1d&period=1m')
    data = json.loads(response.read())
    
    print("RAW RESPONSE:")
    print("-" * 50)
    
    # Show key fields
    print(f"current_price: {data.get('current_price')}")
    print(f"price_change: {data.get('price_change')}")
    print(f"day_high: {data.get('day_high')}")
    print(f"day_low: {data.get('day_low')}")
    print(f"volume: {data.get('volume')}")
    
    # Check chart data
    chart_data = data.get('chart_data', [])
    print(f"\nChart data points: {len(chart_data)}")
    
    if chart_data:
        # Show last 3 data points
        print("\nLast 3 data points:")
        for point in chart_data[-3:]:
            print(f"  {point.get('date', 'N/A')}: Close=${point.get('close', 0)}")
    
    # Show full response for debugging
    print("\nFULL RESPONSE (first 500 chars):")
    print(json.dumps(data, indent=2)[:500])
    
except Exception as e:
    print(f"Error: {e}")

input("\nPress Enter to exit...")