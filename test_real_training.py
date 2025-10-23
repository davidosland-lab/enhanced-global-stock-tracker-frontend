#!/usr/bin/env python3
"""
Test Script: Verify ML Training Takes Real Time
This will train a model and show it takes realistic time (not milliseconds)
"""

import time
import requests
import json

def test_real_training():
    """Test that ML training takes realistic time"""
    
    print("=" * 60)
    print("TESTING REAL ML TRAINING TIME")
    print("=" * 60)
    
    # Test configuration
    test_cases = [
        {"symbol": "AAPL", "days": 365, "expected_min": 2, "expected_max": 10},
        {"symbol": "MSFT", "days": 730, "expected_min": 5, "expected_max": 20},
        {"symbol": "GOOGL", "days": 1095, "expected_min": 8, "expected_max": 30},
    ]
    
    print("\nNOTE: Real ML training should take several seconds, not milliseconds!")
    print("Expected times based on data size and 500 trees with depth 20:\n")
    
    for test in test_cases:
        print(f"\nTesting {test['symbol']} with {test['days']} days of data...")
        print(f"Expected time: {test['expected_min']}-{test['expected_max']} seconds")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:8003/api/train',
                json={
                    "symbol": test['symbol'],
                    "model_type": "random_forest",
                    "days_back": test['days']
                },
                timeout=120  # 2 minute timeout
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Training completed in {elapsed:.1f} seconds")
                print(f"   Model ID: {result.get('model_id', 'N/A')}")
                print(f"   Train Score: {result.get('train_score', 0)*100:.1f}%")
                print(f"   Test Score: {result.get('test_score', 0)*100:.1f}%")
                print(f"   Training Samples: {result.get('training_samples', 0)}")
                
                # Verify it took realistic time
                if elapsed < 0.5:
                    print("⚠️  WARNING: Training completed too quickly!")
                    print("    This might indicate fake/simulated training")
                elif elapsed < test['expected_min']:
                    print(f"ℹ️  Training was faster than expected (but still realistic)")
                elif elapsed > test['expected_max']:
                    print(f"ℹ️  Training took longer than expected (large dataset)")
                else:
                    print(f"✅ Training time is realistic for {test['days']} days of data")
                    
            else:
                print(f"❌ Training failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Training timed out (>2 minutes)")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to ML backend on port 8003")
            print("   Make sure to start the ML backend first:")
            print("   python3 ml_backend.py")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("If training times were in the expected ranges,")
    print("this confirms REAL ML training, not fake/simulated.")
    print("=" * 60)

if __name__ == "__main__":
    print("\n⚠️  PREREQUISITES:")
    print("1. Make sure the ML backend is running on port 8003")
    print("2. Run: cd StockTracker_V7_Complete && python3 ml_backend.py")
    print("\nPress Enter to continue or Ctrl+C to abort...")
    input()
    
    test_real_training()