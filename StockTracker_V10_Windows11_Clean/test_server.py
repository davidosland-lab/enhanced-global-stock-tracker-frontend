"""
Test if the unified backend is running correctly
"""

import requests
import json
import time

def test_server():
    """Test server endpoints"""
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("TESTING STOCK TRACKER SERVER")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   FinBERT: {data.get('finbert')}")
            print(f"   XGBoost: {data.get('xgboost')}")
        else:
            print("❌ Health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running! Please run START_SIMPLE.bat first")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Services status
    print("\n2. Testing services status...")
    try:
        response = requests.get(f"{base_url}/api/services/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Services status check passed")
            for service, info in data.items():
                status = info.get('status', 'unknown')
                symbol = "✅" if status == "online" else "❌"
                print(f"   {symbol} {service}: {status}")
        else:
            print("❌ Services status check failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Train a model
    print("\n3. Testing model training (this takes 10-60 seconds)...")
    try:
        response = requests.post(f"{base_url}/train", json={
            "symbol": "AAPL",
            "model_type": "random_forest",
            "use_sentiment": True
        })
        if response.status_code == 200:
            data = response.json()
            print("✅ Model training passed")
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Accuracy: {data.get('accuracy_score', 0)*100:.1f}%")
            print(f"   Training time: {data.get('training_time', 0):.1f}s")
        else:
            print("❌ Model training failed")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Make prediction
    print("\n4. Testing prediction...")
    try:
        response = requests.post(f"{base_url}/predict", json={
            "symbol": "AAPL",
            "days": 7,
            "model_type": "random_forest",
            "use_sentiment": True
        })
        if response.status_code == 200:
            data = response.json()
            print("✅ Prediction passed")
            print(f"   Current price: ${data.get('current_price', 0):.2f}")
            print(f"   Predicted change: {data.get('predicted_change', 0):.2f}%")
            print(f"   Recommendation: {data.get('recommendation', 'N/A')}")
        else:
            print("❌ Prediction failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get sentiment
    print("\n5. Testing sentiment analysis...")
    try:
        response = requests.get(f"{base_url}/api/sentiment/AAPL")
        if response.status_code == 200:
            data = response.json()
            print("✅ Sentiment analysis passed")
            sentiment = data.get('sentiment', {})
            print(f"   Positive: {sentiment.get('positive', 0)*100:.1f}%")
            print(f"   Negative: {sentiment.get('negative', 0)*100:.1f}%")
            print(f"   Neutral: {sentiment.get('neutral', 0)*100:.1f}%")
        else:
            print("❌ Sentiment analysis failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nIf all tests passed, you can access the UI at:")
    print("http://localhost:8000/prediction_center_fixed.html")
    print("\nIf tests failed, make sure to:")
    print("1. Run START_SIMPLE.bat first to start the server")
    print("2. Install all required packages")
    print("3. Check that port 8000 is not in use")
    
    return True

if __name__ == "__main__":
    test_server()
    input("\nPress Enter to exit...")