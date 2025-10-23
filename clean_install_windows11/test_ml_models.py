#!/usr/bin/env python3
"""
Test script to verify ML model training and listing functionality
"""

import requests
import json
import time
import sys

ML_BACKEND_URL = "http://localhost:8003"

def test_ml_backend():
    """Test ML backend connectivity and model operations"""
    
    print("Testing ML Backend...")
    print("-" * 50)
    
    # 1. Check health
    try:
        response = requests.get(f"{ML_BACKEND_URL}/health")
        if response.status_code == 200:
            print("✓ ML Backend is running")
        else:
            print("✗ ML Backend health check failed")
            return False
    except Exception as e:
        print(f"✗ ML Backend not reachable: {e}")
        print("Please start the ML backend with: python ml_backend_v2.py")
        return False
    
    # 2. List existing models
    print("\nChecking existing models...")
    try:
        response = requests.get(f"{ML_BACKEND_URL}/api/ml/models")
        data = response.json()
        print(f"Found {data.get('count', 0)} models")
        if data.get('models'):
            for model in data['models']:
                print(f"  - {model['name']} ({model['symbol']}): {model['accuracy']*100:.1f}% accuracy")
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # 3. Start a quick training session
    print("\nStarting test training session...")
    try:
        training_data = {
            "symbol": "TEST.AX",
            "model_type": "lstm",
            "sequence_length": 30,
            "epochs": 5,  # Very short for testing
            "batch_size": 32,
            "learning_rate": 0.001
        }
        
        response = requests.post(
            f"{ML_BACKEND_URL}/api/ml/train",
            json=training_data
        )
        
        if response.status_code == 200:
            result = response.json()
            training_id = result.get('training_id', result.get('model_id', result.get('id')))
            print(f"✓ Training started with ID: {training_id}")
            
            # Monitor training
            print("Monitoring training progress...")
            for i in range(10):  # Check for up to 20 seconds
                time.sleep(2)
                status_response = requests.get(f"{ML_BACKEND_URL}/api/ml/training/status/{training_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    progress = status.get('progress', 0)
                    print(f"  Progress: {progress}% - {status.get('status', 'unknown')}")
                    
                    if status.get('status') == 'completed':
                        print("✓ Training completed!")
                        break
                    elif status.get('status') == 'failed':
                        print("✗ Training failed")
                        break
            
            # Check models again
            print("\nChecking models after training...")
            response = requests.get(f"{ML_BACKEND_URL}/api/ml/models")
            data = response.json()
            print(f"Now have {data.get('count', 0)} models")
            if data.get('models'):
                for model in data['models']:
                    print(f"  - {model['name']} ({model['symbol']}): {model['accuracy']*100:.1f}% accuracy")
                    
        else:
            print(f"✗ Failed to start training: {response.text}")
            
    except Exception as e:
        print(f"Error during training test: {e}")
        
    print("\n" + "-" * 50)
    print("Test complete!")
    return True

if __name__ == "__main__":
    test_ml_backend()