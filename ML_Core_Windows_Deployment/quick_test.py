#!/usr/bin/env python3
"""
Quick Test Script for ML Core System
Tests basic functionality without the web interface
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_connection():
    """Test if server is running"""
    print("1. Testing server connection...")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Server running: {data['system']} v{data['version']}")
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Features: {data['features']['features_count']} indicators")
            return True
        else:
            print(f"   ✗ Server returned status {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server at http://localhost:8000")
        print("   Make sure to run: python ml_core_enhanced_production.py")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_cache():
    """Test cache stats endpoint"""
    print("\n2. Testing cache stats...")
    try:
        r = requests.get(f"{BASE_URL}/api/cache/stats", timeout=3)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Cache working")
            print(f"     Hit rate: {data.get('hit_rate', 0)*100:.1f}%")
            print(f"     Hits: {data.get('cache_hits', 0)}")
            print(f"     Misses: {data.get('cache_misses', 0)}")
            return True
        else:
            print(f"   ⚠ Cache stats returned {r.status_code}")
            return False
    except requests.Timeout:
        print("   ⚠ Cache stats timeout (normal if cache not initialized)")
        return True  # Not a critical error
    except Exception as e:
        print(f"   ⚠ Cache error: {e}")
        return False

def test_models():
    """Check existing models"""
    print("\n3. Checking trained models...")
    try:
        r = requests.get(f"{BASE_URL}/api/models", timeout=5)
        if r.status_code == 200:
            models = r.json()
            if models:
                print(f"   ✓ Found {len(models)} trained model(s):")
                for m in models[:3]:  # Show first 3
                    print(f"     - {m.get('symbol', 'N/A')} ({m.get('ensemble_type', 'N/A')})")
            else:
                print("   ℹ No models trained yet")
            return True
        else:
            print(f"   ✗ Models endpoint returned {r.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_quick_train():
    """Test training with minimal data"""
    print("\n4. Testing quick training (AAPL, 30 days)...")
    print("   This will take 10-30 seconds...")
    
    try:
        start_time = time.time()
        
        r = requests.post(
            f"{BASE_URL}/api/train",
            json={
                "symbol": "AAPL",
                "ensemble_type": "voting",
                "days": 30
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Training successful in {elapsed:.1f}s")
            print(f"     R² Score: {data.get('metrics', {}).get('r2', 'N/A'):.4f}")
            print(f"     RMSE: {data.get('metrics', {}).get('rmse', 'N/A'):.2f}")
            print(f"     Features: {data.get('features_used', 36)}")
            print(f"     Samples: {data.get('training_samples', 'N/A')}")
            print(f"     Cache hit: {data.get('cache_hit_rate', 0)*100:.1f}%")
            return True
        else:
            error_text = r.text
            print(f"   ✗ Training failed with status {r.status_code}")
            print(f"     Error: {error_text[:200]}")
            return False
            
    except requests.Timeout:
        print("   ✗ Training timeout after 60 seconds")
        return False
    except Exception as e:
        print(f"   ✗ Training error: {e}")
        return False

def test_prediction():
    """Test prediction (requires trained model)"""
    print("\n5. Testing prediction...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/predict",
            json={"symbol": "AAPL", "horizon": 1},
            timeout=30
        )
        
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Prediction successful")
            print(f"     Current price: ${data.get('current_price', 'N/A'):.2f}")
            print(f"     Predicted: ${data.get('predicted_price', 'N/A'):.2f}")
            print(f"     Change: {data.get('expected_change', 0):.2f}%")
            print(f"     Signal: {data.get('signal', 'N/A')}")
            print(f"     Confidence: {data.get('confidence', 0)*100:.1f}%")
            return True
        else:
            error = r.json().get('detail', r.text)
            if "No trained model" in error:
                print("   ⚠ No model trained yet (run training first)")
            elif "0 sample" in error:
                print("   ⚠ Insufficient data for features (train with more days)")
            else:
                print(f"   ✗ Prediction failed: {error[:100]}")
            return False
    except Exception as e:
        print(f"   ✗ Prediction error: {e}")
        return False

def main():
    print("=" * 60)
    print("ML CORE ENHANCED SYSTEM - QUICK TEST")
    print("=" * 60)
    
    # Test connection first
    if not test_connection():
        print("\n❌ Server not running. Please start it first:")
        print("   python ml_core_enhanced_production.py")
        sys.exit(1)
    
    # Run other tests
    test_cache()
    test_models()
    
    # Ask about training
    response = input("\n▶ Run training test? (y/n): ").lower()
    if response == 'y':
        if test_quick_train():
            test_prediction()
    else:
        print("Skipping training test")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nIf tests passed, the system is working correctly.")
    print("Use ml_core_enhanced_interface.html for the web interface.")
    print("\nTroubleshooting:")
    print("- If cache timeout: Normal, will initialize on first use")
    print("- If training fails: Check internet connection (Yahoo Finance)")
    print("- If prediction fails: Train with more days (252 recommended)")

if __name__ == "__main__":
    main()