#!/usr/bin/env python3
"""
Test script to verify FinBERT system is working correctly
"""

import sys
import json
import urllib.request
import time

def test_data_sources():
    """Test both Yahoo and Alpha Vantage data sources"""
    
    print("="*60)
    print("Testing Data Sources")
    print("="*60)
    
    # Test 1: Direct Yahoo Finance API
    print("\n1. Testing Direct Yahoo Finance API...")
    try:
        symbol = "AAPL"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            price = result['meta'].get('regularMarketPrice', 0)
            print(f"   ✓ Yahoo Direct works: {symbol} price ${price:.2f}")
        else:
            print("   ✗ Yahoo Direct failed: Invalid response")
    except Exception as e:
        print(f"   ✗ Yahoo Direct error: {e}")
    
    # Test 2: Alpha Vantage API with user's key
    print("\n2. Testing Alpha Vantage API...")
    try:
        import requests
        symbol = "MSFT"
        api_key = "68ZFANK047DL0KSR"
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            price = float(quote.get('05. price', 0))
            print(f"   ✓ Alpha Vantage works: {symbol} price ${price:.2f}")
        else:
            print(f"   ✗ Alpha Vantage failed: {data.get('Note', 'Invalid response')}")
    except Exception as e:
        print(f"   ✗ Alpha Vantage error: {e}")
    
    # Test 3: Australian stock on Yahoo
    print("\n3. Testing Australian stock (CBA.AX) on Yahoo...")
    try:
        symbol = "CBA.AX"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            price = result['meta'].get('regularMarketPrice', 0)
            currency = result['meta'].get('currency', 'AUD')
            print(f"   ✓ Australian stock works: {symbol} price {currency} ${price:.2f}")
        else:
            print("   ✗ Australian stock failed: Invalid response")
    except Exception as e:
        print(f"   ✗ Australian stock error: {e}")

def test_server():
    """Test if the Flask server is running"""
    print("\n" + "="*60)
    print("Testing Flask Server")
    print("="*60)
    
    try:
        import requests
        
        # Test status endpoint
        print("\n1. Testing /status endpoint...")
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Server is running")
            print(f"   - FinBERT: {data.get('finbert', False)}")
            print(f"   - Alpha Vantage: {data.get('alpha_vantage_key', False)}")
            print(f"   - Version: {data.get('version', 'Unknown')}")
        else:
            print(f"   ✗ Server returned status {response.status_code}")
        
        # Test stock endpoint
        print("\n2. Testing /api/stock/AAPL endpoint...")
        response = requests.get("http://localhost:5000/api/stock/AAPL", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Stock endpoint works")
            print(f"   - Symbol: {data.get('symbol', 'N/A')}")
            print(f"   - Price: ${data.get('price', 0):.2f}")
            print(f"   - Change: {data.get('changePercent', 0):.2f}%")
            
            # Check indicators
            indicators = data.get('indicators', {})
            if indicators:
                print(f"   - RSI: {indicators.get('RSI', 'N/A')}")
                print(f"   - MACD: {indicators.get('MACD', 'N/A')}")
        else:
            print(f"   ✗ Stock endpoint returned status {response.status_code}")
        
        # Test prediction endpoint
        print("\n3. Testing /api/predict/AAPL endpoint...")
        response = requests.get("http://localhost:5000/api/predict/AAPL", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                print(f"   ✓ Prediction endpoint works")
                if 'next_day_prediction' in data:
                    ndp = data['next_day_prediction']
                    print(f"   - Next day: ${ndp.get('price', 0):.2f} ({ndp.get('confidence', 0):.1f}% confidence)")
                if 'sentiment_score' in data:
                    print(f"   - Sentiment: {data['sentiment_score']:.3f}")
            else:
                print(f"   ⚠ Prediction endpoint returned error: {data['error']}")
        else:
            print(f"   ✗ Prediction endpoint returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n   ✗ Cannot connect to server")
        print("   Make sure the server is running: python app_finbert_v3_fixed.py")
    except Exception as e:
        print(f"\n   ✗ Server test error: {e}")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("FinBERT Ultimate Trading System v3.0 - System Test")
    print("="*60)
    
    # Test data sources first (doesn't require server)
    test_data_sources()
    
    # Ask if user wants to test server
    print("\n" + "="*60)
    response = input("\nDo you want to test the Flask server? (y/n): ").lower()
    if response == 'y':
        test_server()
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)

if __name__ == "__main__":
    main()