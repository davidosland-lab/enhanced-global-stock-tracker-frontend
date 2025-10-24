#!/usr/bin/env python3
"""
Debug script to test ML predictions directly
"""

import requests
import json
import time

def test_ml_predictions(symbol='AAPL'):
    """Test ML predictions endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing ML Predictions for {symbol}")
    print('='*60)
    
    # Test health first
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get('http://localhost:5000/health')
        health = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   ML Available: {health.get('ml_available', 'Unknown')}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # Test stock data
    print(f"\n2. Testing /api/stock/{symbol} endpoint...")
    try:
        response = requests.get(f'http://localhost:5000/api/stock/{symbol}')
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Source: {data.get('source')}")
            print(f"   Current Price: ${data.get('current_price', 0):.2f}")
        else:
            print(f"   ERROR: Status {response.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test ML predictions
    print(f"\n3. Testing /api/predict/{symbol} endpoint...")
    print("   Sending request...")
    
    try:
        start_time = time.time()
        
        # Make request with headers similar to browser
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'http://localhost:5000',
            'Referer': 'http://localhost:5000/'
        }
        
        response = requests.get(
            f'http://localhost:5000/api/predict/{symbol}',
            headers=headers
        )
        
        elapsed = time.time() - start_time
        print(f"   Response Time: {elapsed:.2f} seconds")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('available'):
                print("   ✓ ML Predictions Available!")
                
                # Show predictions
                if data.get('predictions'):
                    print("\n   Predictions:")
                    for pred in data['predictions']:
                        symbol = '+' if pred['return'] >= 0 else ''
                        print(f"     {pred['days']} day: ${pred['price']:.2f} ({symbol}{pred['return']:.2f}%) - Confidence: {pred['confidence']}%")
                
                # Show model info
                if data.get('model_info'):
                    print(f"\n   Model Info:")
                    print(f"     Symbol: {data['model_info'].get('symbol')}")
                    print(f"     Features: {data['model_info'].get('features_used')}")
            else:
                print(f"   ✗ ML Not Available: {data.get('error')}")
        else:
            print(f"   ✗ ERROR: Status {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Test with different symbols
    for symbol in ['AAPL', 'MSFT', 'CBA']:
        test_ml_predictions(symbol)
        time.sleep(2)  # Small delay between tests