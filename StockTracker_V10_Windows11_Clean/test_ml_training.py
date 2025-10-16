#!/usr/bin/env python3
"""
Test ML Training Endpoint
Tests the ML backend training functionality
"""

import requests
import json
import time

def test_ml_training():
    """Test ML training endpoint"""
    
    # Configuration
    ML_API = "http://localhost:8002"
    
    print("=" * 60)
    print("ML TRAINING ENDPOINT TEST")
    print("=" * 60)
    print()
    
    # Step 1: Check ML backend health
    print("1. Checking ML backend health...")
    try:
        response = requests.get(f"{ML_API}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ ML backend is running")
        else:
            print(f"   ❌ ML backend returned status {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ ML backend not accessible: {e}")
        print("   Make sure ml_backend.py is running on port 8002")
        return
    
    # Step 2: Check ML status
    print("\n2. Checking ML status...")
    try:
        response = requests.get(f"{ML_API}/api/ml/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ML status OK")
            print(f"   • Trained models: {data.get('trained_models', 0)}")
            print(f"   • Status: {data.get('status', 'unknown')}")
        else:
            print(f"   ❌ ML status returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ ML status error: {e}")
    
    # Step 3: Train a model
    print("\n3. Training a RandomForest model for AAPL...")
    print("   This should take 10-60 seconds for realistic training...")
    
    training_data = {
        "symbol": "AAPL",
        "model_type": "random_forest",
        "days_back": 365
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{ML_API}/api/train",
            json=training_data,
            timeout=120  # 2 minute timeout for training
        )
        
        training_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Training successful in {training_time:.1f} seconds!")
            print("\n   Training Results:")
            print(f"   • Model ID: {result.get('model_id', 'N/A')}")
            print(f"   • Train Score (R²): {result.get('train_score', 0):.4f}")
            print(f"   • Test Score (R²): {result.get('test_score', 0):.4f}")
            print(f"   • Features Used: {result.get('feature_count', 0)}")
            print(f"   • Training Time: {result.get('training_time_seconds', 0):.1f}s")
            print(f"   • MAE: ${result.get('mae', 0):.2f}")
            print(f"   • RMSE: ${result.get('rmse', 0):.2f}")
            
            # Step 4: Test prediction with the trained model
            print("\n4. Testing prediction with trained model...")
            
            prediction_data = {
                "symbol": "AAPL",
                "model_id": result.get('model_id'),
                "horizon": 5
            }
            
            response = requests.post(
                f"{ML_API}/api/predict",
                json=prediction_data,
                timeout=30
            )
            
            if response.status_code == 200:
                pred_result = response.json()
                print("   ✅ Prediction successful!")
                print(f"   • Current Price: ${pred_result.get('current_price', 0):.2f}")
                print(f"   • Predicted Price: ${pred_result.get('predicted_price', 0):.2f}")
                print(f"   • Confidence: {pred_result.get('confidence', 0):.1%}")
                print(f"   • Expected Change: {pred_result.get('expected_change_percent', 0):.2f}%")
            else:
                print(f"   ❌ Prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        else:
            print(f"   ❌ Training failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Training timed out after {training_time:.1f} seconds")
        print("   This might be normal for large datasets. Try increasing timeout.")
    except Exception as e:
        print(f"   ❌ Training error: {e}")
    
    # Step 5: List all models
    print("\n5. Listing all trained models...")
    try:
        response = requests.get(f"{ML_API}/api/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"   ✅ Found {len(models)} trained model(s)")
            for model in models[:5]:  # Show first 5 models
                print(f"   • {model.get('symbol')} - {model.get('model_type')} (R²: {model.get('test_score', 0):.3f})")
        else:
            print(f"   ❌ Failed to list models: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error listing models: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_ml_training()