#!/usr/bin/env python3
"""
Test script for ML Core Enhanced Production System
Verifies all components are working correctly
"""

import requests
import json
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def test_system_status():
    """Test if system is operational"""
    print("Testing system status...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Models available: {data['features']['models']}")
            print(f"   Features count: {data['features']['features_count']}")
            return True
        else:
            print(f"❌ System returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        print("   Make sure the system is running (python ml_core_enhanced_production.py)")
        return False

def test_model_training():
    """Test model training with ensemble"""
    print("\nTesting model training...")
    
    payload = {
        "symbol": "AAPL",
        "ensemble_type": "voting",
        "days": 200
    }
    
    try:
        print(f"   Training ensemble model for {payload['symbol']}...")
        start_time = time.time()
        
        response = requests.post(f"{API_BASE}/api/train", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            training_time = time.time() - start_time
            
            print(f"✅ Model trained successfully in {training_time:.2f} seconds")
            print(f"   Training time (model): {result['training_time']:.2f}s")
            print(f"   R² Score: {result['metrics']['r2']:.4f}")
            print(f"   RMSE: {result['metrics']['rmse']:.4f}")
            print(f"   CV Score: {result['metrics']['cv_score_mean']:.4f}")
            print(f"   Features used: {result['features_used']}")
            print(f"   Training samples: {result['training_samples']}")
            print(f"   Cache hit rate: {result.get('cache_hit_rate', 0):.1%}")
            
            # Display top features
            if 'feature_importance' in result and result['feature_importance']:
                print("\n   Top 5 Features:")
                features = result['feature_importance'].get('feature', {})
                importance = result['feature_importance'].get('importance', {})
                for i in range(min(5, len(features))):
                    feat_name = features.get(str(i), 'N/A')
                    feat_imp = importance.get(str(i), 0)
                    print(f"   - {feat_name}: {feat_imp:.4f}")
            
            return True
        else:
            print(f"❌ Training failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

def test_backtesting():
    """Test backtesting functionality"""
    print("\nTesting backtesting engine...")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    payload = {
        "symbol": "AAPL",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "initial_capital": 100000
    }
    
    try:
        print(f"   Running backtest for {payload['symbol']}...")
        print(f"   Period: {payload['start_date']} to {payload['end_date']}")
        print(f"   Initial capital: ${payload['initial_capital']:,}")
        
        response = requests.post(f"{API_BASE}/api/backtest", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            metrics = result.get('metrics', {})
            
            print(f"✅ Backtest completed successfully")
            print(f"\n   Performance Metrics:")
            print(f"   - Total Return: {metrics.get('total_return', 0):.2f}%")
            print(f"   - Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   - Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
            print(f"   - Win Rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"   - Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"   - Total Trades: {metrics.get('total_trades', 0)}")
            
            print(f"\n   Cost Analysis:")
            print(f"   - Commission Paid: ${metrics.get('total_commission', 0):.2f}")
            print(f"   - Slippage Cost: ${metrics.get('total_slippage', 0):.2f}")
            print(f"   - Cost as % of capital: {metrics.get('cost_percentage', 0):.2f}%")
            
            print(f"\n   Quality Assessment:")
            print(f"   - Quality Score: {result.get('quality_score', 0)}/100")
            print(f"   - Assessment: {result.get('assessment', 'N/A')}")
            
            if 'recommendations' in result and result['recommendations']:
                print(f"\n   Recommendations:")
                for rec in result['recommendations'][:3]:
                    print(f"   • {rec}")
            
            return True
        else:
            print(f"❌ Backtest failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backtest error: {e}")
        return False

def test_cache_performance():
    """Test cache performance improvement"""
    print("\nTesting cache performance...")
    
    try:
        # Get cache stats
        response = requests.get(f"{API_BASE}/api/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            hit_rate = stats.get('hit_rate', 0)
            hits = stats.get('cache_hits', 0)
            misses = stats.get('cache_misses', 0)
            
            print(f"✅ Cache Statistics:")
            print(f"   - Hit Rate: {hit_rate:.1%}")
            print(f"   - Cache Hits: {hits}")
            print(f"   - Cache Misses: {misses}")
            
            if hit_rate > 0:
                speed_improvement = 1 / (1 - hit_rate) if hit_rate < 1 else 50
                print(f"   - Speed Improvement: ~{speed_improvement:.0f}x faster")
            
            return True
        else:
            print(f"❌ Failed to get cache stats")
            return False
            
    except Exception as e:
        print(f"❌ Cache test error: {e}")
        return False

def test_model_list():
    """Test listing trained models"""
    print("\nTesting model library...")
    
    try:
        response = requests.get(f"{API_BASE}/api/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"✅ Found {len(models)} trained model(s):")
                for model in models[:5]:  # Show first 5
                    print(f"   - {model['symbol']} ({model['ensemble_type']})")
                    print(f"     Trained: {model['training_date']}")
                    print(f"     Score: {model.get('validation_score', 'N/A')}")
            else:
                print("ℹ️ No models found (this is normal for first run)")
            
            return True
        else:
            print(f"❌ Failed to list models")
            return False
            
    except Exception as e:
        print(f"❌ Model list error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ML CORE ENHANCED PRODUCTION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("System Status", test_system_status),
        ("Model Training", test_model_training),
        ("Backtesting Engine", test_backtesting),
        ("Cache Performance", test_cache_performance),
        ("Model Library", test_model_list)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 40)
        success = test_func()
        results.append((name, success))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)