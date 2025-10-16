#!/usr/bin/env python3
"""
Debug Training Issue
Diagnoses the exact problem with ML training
"""

import requests
import json
import traceback

def debug_ml_training():
    """Debug the ML training endpoint"""
    
    print("=" * 60)
    print("ML TRAINING DEBUG")
    print("=" * 60)
    print()
    
    # Configuration
    ML_API = "http://localhost:8002"
    
    # Step 1: Check if ML backend is running
    print("1. Checking ML backend status...")
    try:
        response = requests.get(f"{ML_API}/health", timeout=5)
        print(f"   Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ ML backend is running")
        else:
            print(f"   ❌ Unexpected status: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ ML backend not accessible: {e}")
        print("   Please start ml_backend.py first!")
        return
    
    # Step 2: Check ML status endpoint
    print("\n2. Checking ML status endpoint...")
    try:
        response = requests.get(f"{ML_API}/api/ml/status", timeout=5)
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 3: Test training with detailed response
    print("\n3. Testing training endpoint...")
    
    training_data = {
        "symbol": "AAPL",
        "model_type": "random_forest",
        "days_back": 365
    }
    
    print(f"   Request data: {json.dumps(training_data, indent=2)}")
    print("\n   Sending request to /api/train...")
    
    try:
        response = requests.post(
            f"{ML_API}/api/train",
            json=training_data,
            timeout=120
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n   ✅ Training successful!")
            print("\n   Response data structure:")
            print("   " + "-" * 40)
            
            # Show all fields returned
            for key, value in result.items():
                value_type = type(value).__name__
                if isinstance(value, (int, float)):
                    print(f"   {key}: {value} ({value_type})")
                elif isinstance(value, str):
                    print(f"   {key}: '{value}' ({value_type})")
                else:
                    print(f"   {key}: {value} ({value_type})")
            
            print("\n   Key fields for UI:")
            print("   " + "-" * 40)
            print(f"   - model_id: {result.get('model_id', 'MISSING')}")
            print(f"   - train_score: {result.get('train_score', 'MISSING')}")
            print(f"   - test_score: {result.get('test_score', 'MISSING')}")
            print(f"   - feature_count: {result.get('feature_count', 'MISSING')}")
            print(f"   - training_time: {result.get('training_time', 'MISSING')}")
            print(f"   - training_time_seconds: {result.get('training_time_seconds', 'MISSING')}")
            print(f"   - mae: {result.get('mae', 'MISSING')}")
            print(f"   - rmse: {result.get('rmse', 'MISSING')}")
            
        else:
            print(f"\n   ❌ Training failed!")
            print(f"   Response body: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏱️ Request timed out (this might be normal for large datasets)")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - is ML backend running on port 8002?")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        traceback.print_exc()
    
    # Step 4: Check CORS headers
    print("\n4. Checking CORS configuration...")
    try:
        # Simulate browser request with Origin header
        headers = {
            'Origin': 'http://localhost:8000',
            'Content-Type': 'application/json'
        }
        
        response = requests.options(
            f"{ML_API}/api/train",
            headers=headers,
            timeout=5
        )
        
        print(f"   OPTIONS request status: {response.status_code}")
        print(f"   CORS headers:")
        for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 
                      'Access-Control-Allow-Headers', 'Access-Control-Allow-Credentials']:
            value = response.headers.get(header, 'NOT SET')
            print(f"   - {header}: {value}")
            
    except Exception as e:
        print(f"   Error checking CORS: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
    
    print("\nSUGGESTIONS:")
    print("1. If ML backend is not running: python ml_backend.py")
    print("2. Check that ML backend is on port 8002")
    print("3. Verify prediction_center.html has ML_API = 'http://localhost:8002'")
    print("4. Check browser console for additional errors")
    print("5. The UI expects 'training_time' not 'training_time_seconds'")

if __name__ == "__main__":
    debug_ml_training()