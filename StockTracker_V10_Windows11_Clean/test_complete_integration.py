#!/usr/bin/env python3
"""
Complete Integration Test for Stock Tracker V10
Tests all services and features to ensure everything works together
"""

import requests
import json
import time
import sys
from datetime import datetime

# Service endpoints
SERVICES = {
    "Main Backend": "http://localhost:8000",
    "Historical Backend": "http://localhost:8001",
    "ML Backend": "http://localhost:8002",
    "FinBERT Backend": "http://localhost:8003",
    "Backtesting Backend": "http://localhost:8005",
    "Web Scraper Backend": "http://localhost:8006"
}

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_service_health(name, url):
    """Test if a service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: Running on {url}")
            return True
        else:
            print(f"❌ {name}: Returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Not accessible - {str(e)[:50]}")
        return False

def test_ml_training():
    """Test ML training functionality"""
    print_header("ML TRAINING TEST")
    
    # Test training
    print("Training RandomForest model for AAPL...")
    print("This should take 10-60 seconds for realistic training...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{SERVICES['ML Backend']}/api/train",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest",
                "days_back": 365
            },
            timeout=120
        )
        
        training_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Training completed in {training_time:.1f} seconds")
            print(f"   Model ID: {result.get('model_id', 'N/A')}")
            print(f"   R² Score: {result.get('test_score', 0):.4f}")
            print(f"   MAE: ${result.get('mae', 0):.2f}")
            print(f"   RMSE: ${result.get('rmse', 0):.2f}")
            print(f"   Features: {result.get('feature_count', 0)}")
            return True
        else:
            print(f"❌ Training failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

def test_prediction():
    """Test ML prediction"""
    print_header("ML PREDICTION TEST")
    
    print("Generating prediction for AAPL...")
    
    try:
        response = requests.post(
            f"{SERVICES['ML Backend']}/api/predict",
            json={
                "symbol": "AAPL",
                "horizon": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction successful!")
            print(f"   Current Price: ${result.get('current_price', 0):.2f}")
            print(f"   Predicted Price: ${result.get('predicted_price', 0):.2f}")
            print(f"   Confidence: {result.get('confidence', 0):.1%}")
            print(f"   Change: {result.get('expected_change_percent', 0):.2f}%")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

def test_historical_data():
    """Test historical data retrieval"""
    print_header("HISTORICAL DATA TEST")
    
    print("Fetching historical data for MSFT...")
    
    try:
        response = requests.get(
            f"{SERVICES['Historical Backend']}/api/historical/MSFT",
            params={"days": 30},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data.get('data', []))} days of data")
            if data.get('cached'):
                print(f"   Data served from cache (50x faster!)")
            return True
        else:
            print(f"❌ Failed to retrieve data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Historical data error: {e}")
        return False

def test_finbert_sentiment():
    """Test FinBERT sentiment analysis"""
    print_header("FINBERT SENTIMENT TEST")
    
    print("Analyzing sentiment...")
    
    try:
        response = requests.post(
            f"{SERVICES['FinBERT Backend']}/api/analyze",
            json={
                "text": "Apple reported record-breaking quarterly earnings with strong iPhone sales.",
                "symbol": "AAPL"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment analysis complete!")
            print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
            print(f"   Score: {result.get('score', 0):.4f}")
            print(f"   Confidence: {result.get('confidence', 0):.2%}")
            return True
        else:
            print(f"❌ Sentiment analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FinBERT error: {e}")
        return False

def test_backtesting():
    """Test backtesting functionality"""
    print_header("BACKTESTING TEST")
    
    print("Running backtest with $100,000 capital...")
    
    try:
        response = requests.post(
            f"{SERVICES['Backtesting Backend']}/api/backtest",
            json={
                "symbol": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-10-01",
                "initial_capital": 100000,
                "strategy": "momentum"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backtest complete!")
            print(f"   Total Return: {result.get('total_return', 0):.2%}")
            print(f"   Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
            print(f"   Max Drawdown: {result.get('max_drawdown', 0):.2%}")
            print(f"   Win Rate: {result.get('win_rate', 0):.1%}")
            return True
        else:
            print(f"❌ Backtest failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backtesting error: {e}")
        return False

def test_web_scraper():
    """Test web scraper"""
    print_header("WEB SCRAPER TEST")
    
    print("Scraping sentiment for TSLA...")
    
    try:
        response = requests.post(
            f"{SERVICES['Web Scraper Backend']}/api/scrape",
            json={
                "symbol": "TSLA",
                "sources": ["yahoo", "reddit"]
            },
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scraping complete!")
            print(f"   Articles found: {result.get('total_articles', 0)}")
            print(f"   Overall Sentiment: {result.get('aggregate_sentiment', 'N/A')}")
            print(f"   Average Score: {result.get('average_score', 0):.3f}")
            return True
        else:
            print(f"❌ Scraping failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web scraper error: {e}")
        return False

def main():
    """Run complete integration test"""
    print_header("STOCK TRACKER V10 - COMPLETE INTEGRATION TEST")
    print(f"Test started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    results = {}
    
    # Test 1: Service Health
    print_header("SERVICE HEALTH CHECK")
    for name, url in SERVICES.items():
        results[name] = test_service_health(name, url)
    
    # Only continue if core services are running
    if not results.get("ML Backend"):
        print("\n❌ ML Backend not running - cannot continue tests")
        print("Please start services with: START_WITH_SCRAPER.bat")
        return
    
    # Test 2: ML Training
    results["ML Training"] = test_ml_training()
    
    # Test 3: ML Prediction
    if results["ML Training"]:
        results["ML Prediction"] = test_prediction()
    
    # Test 4: Historical Data
    if results.get("Historical Backend"):
        results["Historical Data"] = test_historical_data()
    
    # Test 5: FinBERT Sentiment
    if results.get("FinBERT Backend"):
        results["FinBERT Sentiment"] = test_finbert_sentiment()
    
    # Test 6: Backtesting
    if results.get("Backtesting Backend"):
        results["Backtesting"] = test_backtesting()
    
    # Test 7: Web Scraper
    if results.get("Web Scraper Backend"):
        results["Web Scraper"] = test_web_scraper()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test:25} {status}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Check failed services.")
    else:
        print("❌ Multiple failures detected. Please check your setup.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()