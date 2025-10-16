#!/usr/bin/env python3
"""
System Test Script - Verify all components are working
"""

import requests
import time
import json
from datetime import datetime

def test_service(url, name):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: ONLINE")
            return True
        else:
            print(f"❌ {name}: ERROR (Status {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: OFFLINE (Connection refused)")
        return False
    except Exception as e:
        print(f"❌ {name}: ERROR ({str(e)})")
        return False

def test_stock_data():
    """Test stock data retrieval"""
    try:
        response = requests.get("http://localhost:8002/api/stock/CBA.AX")
        if response.status_code == 200:
            data = response.json()
            price = data.get('price', 0)
            
            if 150 < price < 200:  # Expected range for CBA
                print(f"✅ CBA.AX Price: ${price:.2f} (Correct range)")
            else:
                print(f"⚠️ CBA.AX Price: ${price:.2f} (Unexpected - should be ~$170)")
            
            if data.get('data_source') == 'yahoo_finance_real':
                print("✅ Data Source: Yahoo Finance (Real data)")
            else:
                print("❌ Data Source: Not using real Yahoo Finance data")
            
            return True
    except Exception as e:
        print(f"❌ Stock Data Test Failed: {e}")
        return False

def test_market_summary():
    """Test market summary with ADST support"""
    try:
        response = requests.get("http://localhost:8002/api/market-summary")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('timezone') == 'ADST':
                print("✅ Timezone: ADST (Correct)")
            else:
                print(f"❌ Timezone: {data.get('timezone')} (Should be ADST)")
            
            market_status = data.get('market_status', {})
            print(f"   Market Status: ASX={market_status.get('ASX', {}).get('status', 'unknown')}, "
                  f"FTSE={market_status.get('FTSE', {}).get('status', 'unknown')}, "
                  f"S&P500={market_status.get('SP500', {}).get('status', 'unknown')}")
            
            return True
    except Exception as e:
        print(f"❌ Market Summary Test Failed: {e}")
        return False

def test_finbert_status():
    """Check if FinBERT is available"""
    try:
        response = requests.get("http://localhost:8002/api/status")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('finbert_available'):
                print("✅ FinBERT: Available (Document analysis ready)")
            else:
                print("⚠️ FinBERT: Not installed (Document analysis limited)")
                print("   To enable: pip install transformers torch")
            
            if data.get('pdf_support'):
                print("✅ PDF Support: Available")
            else:
                print("⚠️ PDF Support: Not available")
                print("   To enable: pip install PyPDF2 python-docx")
            
            return True
    except Exception as e:
        print(f"❌ Status Check Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("STOCK TRACKER PRO - SYSTEM TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test services
    print("1. TESTING SERVICES")
    print("-" * 40)
    
    frontend_ok = test_service("http://localhost:8000", "Frontend (Port 8000)")
    backend_ok = test_service("http://localhost:8002/api/health", "Backend API (Port 8002)")
    ml_ok = test_service("http://localhost:8003/health", "ML Backend (Port 8003)")
    
    print()
    
    if not backend_ok:
        print("⚠️ Backend not running. Start with: python backend.py")
        return
    
    # Test functionality
    print("2. TESTING FUNCTIONALITY")
    print("-" * 40)
    
    test_stock_data()
    print()
    test_market_summary()
    print()
    test_finbert_status()
    
    print()
    print("3. SUMMARY")
    print("-" * 40)
    
    if frontend_ok and backend_ok and ml_ok:
        print("✅ All services are running")
    else:
        print("⚠️ Some services are not running")
        print("   Run: START_ALL_SERVICES.bat")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")