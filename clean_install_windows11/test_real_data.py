#!/usr/bin/env python3
"""Test script to verify all services are using real data"""

import requests
import time
import sys

def test_endpoints():
    """Test all critical endpoints"""
    
    print("Testing Stock Tracker Endpoints...")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test main backend
    try:
        print("\n[1] Testing Main Backend (Port 8002)...")
        response = requests.get("http://localhost:8002/api/status", timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend is online")
            tests_passed += 1
        else:
            print(f"  ❌ Backend returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Backend is offline: {e}")
        tests_failed += 1
    
    # Test CBA.AX real price
    try:
        print("\n[2] Testing CBA.AX real price...")
        response = requests.get("http://localhost:8002/api/stock/CBA.AX", timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data.get('price', 0)
            if 150 < price < 200:  # CBA should be around $170
                print(f"  ✅ CBA.AX price is realistic: ${price:.2f}")
                tests_passed += 1
            else:
                print(f"  ⚠️  CBA.AX price seems wrong: ${price:.2f}")
                tests_failed += 1
        else:
            print(f"  ❌ Failed to fetch CBA.AX")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Error fetching CBA.AX: {e}")
        tests_failed += 1
    
    # Test ML backend
    try:
        print("\n[3] Testing ML Backend (Port 8003)...")
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ ML Backend is online")
            tests_passed += 1
        else:
            print(f"  ❌ ML Backend returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"  ⚠️  ML Backend might be offline: {e}")
        print("     (This is optional for basic functionality)")
    
    # Test historical data
    try:
        print("\n[4] Testing Historical Data API...")
        response = requests.get("http://localhost:8002/api/historical/CBA.AX?period=1mo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                print(f"  ✅ Historical data available: {len(data['data'])} records")
                tests_passed += 1
            else:
                print(f"  ⚠️  No historical data returned")
                tests_failed += 1
        else:
            print(f"  ❌ Failed to fetch historical data")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Error fetching historical data: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Tests Passed: {tests_passed}")
    print(f"  Tests Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ All critical tests passed! System is using real data.")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please check the services.")
        return 1

if __name__ == "__main__":
    print("Waiting 3 seconds for services to stabilize...")
    time.sleep(3)
    sys.exit(test_endpoints())
