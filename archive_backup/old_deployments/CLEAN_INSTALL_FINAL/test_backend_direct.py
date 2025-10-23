#!/usr/bin/env python3
"""Test backend endpoints directly"""

import requests
import json

BASE_URL = "http://localhost:8082"

print("Testing Backend Endpoints")
print("=" * 50)

# Test root
print("\n1. Testing root endpoint:")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Message: {data.get('message', 'N/A')}")
        print(f"Endpoints: {list(data.get('endpoints', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")

# Test statistics
print("\n2. Testing statistics endpoint:")
try:
    response = requests.get(f"{BASE_URL}/api/historical/statistics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test batch download
print("\n3. Testing batch download:")
try:
    payload = {
        "symbols": ["AAPL"],
        "period": "5d",
        "intervals": ["1d"]
    }
    response = requests.post(
        f"{BASE_URL}/api/historical/batch-download",
        json=payload
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Symbols: {data.get('symbols')}")
except Exception as e:
    print(f"Error: {e}")

# Check historical data directory
print("\n4. Checking historical_data directory:")
import os
import glob
if os.path.exists('historical_data'):
    files = glob.glob('historical_data/*.csv')
    print(f"Found {len(files)} CSV files:")
    for f in files[:5]:  # Show first 5
        size = os.path.getsize(f) / 1024
        print(f"  - {os.path.basename(f)} ({size:.1f} KB)")
else:
    print("Directory doesn't exist!")