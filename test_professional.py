#!/usr/bin/env python3
"""Test script for the professional unified stock system with TradingView charts"""

import requests
import json
import time
import sys

def test_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("=" * 70)
    print("TESTING PROFESSIONAL UNIFIED STOCK SYSTEM")
    print("=" * 70)
    
    # 1. Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")
    
    # 2. Test Yahoo Finance for CBA
    print("\n2. Testing Yahoo Finance for CBA.AX...")
    try:
        payload = {
            "symbol": "CBA",
            "period": "1mo",
            "dataSource": "yahoo"
        }
        response = requests.post(f"{base_url}/api/fetch", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Yahoo Finance successful:")
            print(f"  - Symbol: {data.get('symbol')}")
            print(f"  - Current Price: ${data.get('current_price', 0):.2f}")
            print(f"  - Data Points: {len(data.get('prices', []))}")
            print(f"  - Has OHLC: {bool(data.get('open') and data.get('high') and data.get('low'))}")
            print(f"  - Has Volume: {bool(data.get('volume'))}")
        else:
            print(f"✗ Yahoo Finance failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Yahoo Finance error: {e}")
    
    # 3. Test indicators
    print("\n3. Testing Technical Indicators...")
    try:
        # Create sample data if fetch failed
        test_prices = [100, 101, 102, 101, 103, 104, 103, 105, 106, 104, 105, 107, 106, 108, 109]
        test_volumes = [1000000] * len(test_prices)
        
        payload = {
            "prices": test_prices,
            "volumes": test_volumes
        }
        response = requests.post(f"{base_url}/api/indicators", json=payload, timeout=10)
        if response.status_code == 200:
            indicators = response.json()
            print(f"✓ Indicators calculated:")
            for key, value in indicators.items():
                if value is not None:
                    print(f"  - {key}: {value:.2f if isinstance(value, (int, float)) else value}")
        else:
            print(f"✗ Indicators failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Indicators error: {e}")
    
    # 4. Test ML predictions
    print("\n4. Testing ML Predictions...")
    try:
        test_data = {
            "symbol": "TEST",
            "prices": test_prices,
            "dates": ["2024-01-01"] * len(test_prices),
            "current_price": test_prices[-1]
        }
        
        payload = {"data": test_data}
        response = requests.post(f"{base_url}/api/predict", json=payload, timeout=10)
        if response.status_code == 200:
            predictions = response.json()
            print(f"✓ Predictions generated:")
            print(f"  - Ensemble: ${predictions.get('ensemble', 0):.2f}")
            print(f"  - Confidence: {predictions.get('confidence', 0)*100:.0f}%")
            print(f"  - Recommendation: {predictions.get('recommendation', 'N/A')}")
        else:
            print(f"✗ Predictions failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Predictions error: {e}")
    
    # 5. Test UI
    print("\n5. Testing Web Interface...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            html = response.text
            # Check for key UI elements
            checks = [
                ("TradingView Charts", "TradingView Lightweight Charts"),
                ("Professional UI", "Professional Trading Chart"),
                ("Chart Types", "Candlestick"),
                ("Quick Access", "Quick Access"),
                ("Australian Stocks", "CBA 🇦🇺"),
            ]
            
            all_passed = True
            for name, text in checks:
                if text in html:
                    print(f"  ✓ {name} found")
                else:
                    print(f"  ✗ {name} missing")
                    all_passed = False
            
            if all_passed:
                print("✓ Web interface fully loaded")
            else:
                print("⚠ Some UI elements missing")
        else:
            print(f"✗ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Web interface error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nProfessional features to verify manually:")
    print("1. Open http://localhost:8000 in browser")
    print("2. Check TradingView chart loads with real data")
    print("3. Try switching between Candlestick, Line, and Area charts")
    print("4. Toggle volume on/off")
    print("5. Test with Australian stocks (CBA, BHP, CSL)")
    print("6. Verify technical indicators display")
    print("7. Check ML predictions appear")

if __name__ == "__main__":
    test_endpoints()