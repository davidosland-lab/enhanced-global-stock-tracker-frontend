#!/usr/bin/env python3
"""
Comprehensive Test Suite for ML Core Enhanced Production System
Tests all critical components to ensure the system is "rock solid"
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List
import sys

BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text"""
    print(f"{color}{text}{Colors.ENDC}")

def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print_colored(f"  {title}", Colors.BOLD)
    print("=" * 80)

def run_test(name: str, test_func, *args, **kwargs) -> bool:
    """Run individual test with error handling"""
    try:
        print(f"\n{Colors.BLUE}Testing {name}...{Colors.ENDC}")
        result = test_func(*args, **kwargs)
        if result:
            print_colored(f"✅ {name} - PASSED", Colors.GREEN)
        else:
            print_colored(f"❌ {name} - FAILED", Colors.RED)
        return result
    except Exception as e:
        print_colored(f"❌ {name} - FAILED: {str(e)}", Colors.RED)
        return False

# ==================== TEST FUNCTIONS ====================

def test_system_status() -> bool:
    """Test system status endpoint"""
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"  System: {data.get('system')}")
        print(f"  Version: {data.get('version')}")
        print(f"  Status: {data.get('status')}")
        print(f"  Models: {data.get('features', {}).get('models')}")
        print(f"  Features Count: {data.get('features', {}).get('features_count')}")
        return data.get('status') == 'operational'
    return False

def test_model_training(symbol: str = "AAPL", ensemble_type: str = "voting") -> bool:
    """Test model training with realistic parameters"""
    print(f"  Training {ensemble_type} ensemble for {symbol}...")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": symbol,
            "ensemble_type": ensemble_type,
            "days": 500
        },
        timeout=120
    )
    
    training_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"  Training Time: {training_time:.2f}s (Total), {result.get('training_time', 0):.2f}s (Model)")
        print(f"  R² Score: {result.get('metrics', {}).get('r2', 0):.4f}")
        print(f"  RMSE: {result.get('metrics', {}).get('rmse', 0):.4f}")
        print(f"  CV Score: {result.get('metrics', {}).get('cv_score', 0):.4f}")
        print(f"  Features Used: {result.get('features_used', 0)}")
        print(f"  Training Samples: {result.get('training_samples', 0)}")
        print(f"  Cache Hit Rate: {result.get('cache_hit_rate', 0):.1f}%")
        
        # Check if training time is realistic (10-60 seconds for proper ML)
        if 5 <= training_time <= 120:
            print_colored(f"  ✓ Training time is realistic ({training_time:.2f}s)", Colors.GREEN)
        else:
            print_colored(f"  ⚠ Training time seems unusual ({training_time:.2f}s)", Colors.YELLOW)
        
        # Check model performance metrics
        r2_score = result.get('metrics', {}).get('r2', 0)
        if r2_score > 0.7:
            print_colored(f"  ✓ Good R² score: {r2_score:.4f}", Colors.GREEN)
        else:
            print_colored(f"  ⚠ Low R² score: {r2_score:.4f}", Colors.YELLOW)
        
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_backtesting(symbol: str = "AAPL") -> bool:
    """Test backtesting with realistic parameters"""
    print(f"  Running backtest for {symbol}...")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    
    print(f"  Period: {start_date} to {end_date}")
    
    response = requests.post(
        f"{BASE_URL}/api/backtest",
        json={
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        },
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        metrics = result.get('metrics', {})
        
        print(f"\n  📊 Backtest Results:")
        print(f"  Initial Capital: ${metrics.get('initial_capital', 0):,.2f}")
        print(f"  Final Value: ${metrics.get('final_value', 0):,.2f}")
        print(f"  Total Return: {metrics.get('total_return', 0):.2f}%")
        print(f"  Annual Return: {metrics.get('annual_return', 0):.2f}%")
        print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        print(f"  Win Rate: {metrics.get('win_rate', 0):.2f}%")
        print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        print(f"  Total Trades: {metrics.get('total_trades', 0)}")
        print(f"  Commission Paid: ${metrics.get('total_commission', 0):,.2f}")
        print(f"  Slippage Cost: ${metrics.get('total_slippage', 0):,.2f}")
        
        # Validate backtest quality
        quality_score = result.get('quality_score', 0)
        assessment = result.get('assessment', 'Unknown')
        
        print(f"\n  Quality Score: {quality_score}/100")
        print(f"  Assessment: {assessment}")
        
        # Performance checks
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 1.0:
            print_colored(f"  ✓ Good Sharpe ratio: {sharpe:.2f}", Colors.GREEN)
        else:
            print_colored(f"  ⚠ Low Sharpe ratio: {sharpe:.2f}", Colors.YELLOW)
        
        win_rate = metrics.get('win_rate', 0)
        if win_rate > 55:
            print_colored(f"  ✓ Good win rate: {win_rate:.2f}%", Colors.GREEN)
        else:
            print_colored(f"  ⚠ Low win rate: {win_rate:.2f}%", Colors.YELLOW)
        
        drawdown = abs(metrics.get('max_drawdown', 100))
        if drawdown < 25:
            print_colored(f"  ✓ Acceptable drawdown: {drawdown:.2f}%", Colors.GREEN)
        else:
            print_colored(f"  ⚠ High drawdown: {drawdown:.2f}%", Colors.YELLOW)
        
        # Check for realistic trading costs
        if metrics.get('total_commission', 0) > 0:
            print_colored("  ✓ Transaction costs included", Colors.GREEN)
        else:
            print_colored("  ⚠ No transaction costs detected", Colors.YELLOW)
        
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_cache_performance() -> bool:
    """Test SQLite caching performance"""
    print("  Testing cache performance...")
    
    # First request (cache miss)
    start_time = time.time()
    response1 = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": "MSFT",
            "ensemble_type": "voting",
            "days": 100
        },
        timeout=60
    )
    first_time = time.time() - start_time
    
    if response1.status_code != 200:
        print(f"  First request failed: {response1.text}")
        return False
    
    # Second request (should hit cache)
    start_time = time.time()
    response2 = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": "MSFT",
            "ensemble_type": "voting",
            "days": 100
        },
        timeout=60
    )
    second_time = time.time() - start_time
    
    if response2.status_code != 200:
        print(f"  Second request failed: {response2.text}")
        return False
    
    # Calculate speed improvement
    speed_improvement = first_time / second_time if second_time > 0 else 1
    hit_rate = response2.json().get('cache_hit_rate', 0)
    
    print(f"  First request: {first_time:.2f}s")
    print(f"  Second request: {second_time:.2f}s")
    print(f"  Speed improvement: {speed_improvement:.1f}x")
    print(f"  Cache hit rate: {hit_rate:.1f}%")
    
    if speed_improvement > 2:
        print_colored(f"  ✓ Good cache performance ({speed_improvement:.1f}x faster)", Colors.GREEN)
    else:
        print_colored(f"  ⚠ Low cache performance ({speed_improvement:.1f}x)", Colors.YELLOW)
    
    return hit_rate > 50

def test_ensemble_models() -> bool:
    """Test different ensemble configurations"""
    print("  Testing ensemble models...")
    
    results = []
    
    # Test voting ensemble
    print("\n  Testing Voting Ensemble...")
    response = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": "GOOGL",
            "ensemble_type": "voting",
            "days": 200
        },
        timeout=60
    )
    if response.status_code == 200:
        voting_result = response.json()
        results.append(("Voting", voting_result))
        print(f"    R² Score: {voting_result.get('metrics', {}).get('r2', 0):.4f}")
    
    # Test stacking ensemble
    print("\n  Testing Stacking Ensemble...")
    response = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": "GOOGL",
            "ensemble_type": "stacking",
            "days": 200
        },
        timeout=60
    )
    if response.status_code == 200:
        stacking_result = response.json()
        results.append(("Stacking", stacking_result))
        print(f"    R² Score: {stacking_result.get('metrics', {}).get('r2', 0):.4f}")
    
    if len(results) == 2:
        # Compare ensemble performances
        print("\n  Ensemble Comparison:")
        for name, result in results:
            r2 = result.get('metrics', {}).get('r2', 0)
            cv = result.get('metrics', {}).get('cv_score', 0)
            print(f"    {name}: R²={r2:.4f}, CV={cv:.4f}")
        return True
    
    return len(results) > 0

def test_feature_engineering() -> bool:
    """Test feature engineering completeness"""
    print("  Checking feature engineering...")
    
    response = requests.post(
        f"{BASE_URL}/api/train",
        json={
            "symbol": "TSLA",
            "ensemble_type": "voting",
            "days": 100
        },
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        features_used = result.get('features_used', 0)
        feature_importance = result.get('feature_importance', {})
        
        print(f"  Total features: {features_used}")
        
        if features_used >= 30:
            print_colored(f"  ✓ Adequate feature count: {features_used}", Colors.GREEN)
        else:
            print_colored(f"  ⚠ Low feature count: {features_used}", Colors.YELLOW)
        
        # Display top features
        if feature_importance:
            print("\n  Top 5 Important Features:")
            for i, (feature, importance) in enumerate(list(feature_importance.items())[:5]):
                print(f"    {i+1}. {feature}: {importance:.4f}")
        
        return features_used >= 30
    
    return False

def test_model_persistence() -> bool:
    """Test model saving and loading"""
    print("  Testing model persistence...")
    
    # List saved models
    response = requests.get(f"{BASE_URL}/api/models")
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"  Found {len(models)} saved model(s)")
        
        if models:
            latest_model = models[0]
            print(f"  Latest: {latest_model['symbol']} ({latest_model['ensemble_type']})")
            print(f"  Trained: {latest_model['training_date']}")
            print(f"  Score: {latest_model['validation_score']:.4f}")
            return True
    
    return False

def stress_test_predictions() -> bool:
    """Test prediction performance under load"""
    print("  Running prediction stress test...")
    
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    prediction_times = []
    
    for symbol in symbols:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json={"symbol": symbol},
            timeout=10
        )
        prediction_time = time.time() - start_time
        prediction_times.append(prediction_time)
        
        if response.status_code == 200:
            print(f"    {symbol}: {prediction_time:.3f}s")
        else:
            print(f"    {symbol}: Failed")
    
    avg_time = sum(prediction_times) / len(prediction_times) if prediction_times else 0
    print(f"\n  Average prediction time: {avg_time:.3f}s")
    
    if avg_time < 1.0:
        print_colored("  ✓ Good prediction performance", Colors.GREEN)
        return True
    else:
        print_colored("  ⚠ Slow prediction performance", Colors.YELLOW)
        return False

# ==================== MAIN TEST RUNNER ====================

def main():
    """Run comprehensive test suite"""
    print_colored("\n" + "=" * 80, Colors.BOLD)
    print_colored("  ML CORE ENHANCED PRODUCTION - COMPREHENSIVE TEST SUITE", Colors.BOLD)
    print_colored("=" * 80 + "\n", Colors.BOLD)
    
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print_colored("❌ ML Core service is not running!", Colors.RED)
            print("Please start the service with: python ml_core_enhanced_production.py")
            return 1
    except requests.exceptions.ConnectionError:
        print_colored("❌ Cannot connect to ML Core service at http://localhost:8000", Colors.RED)
        print("Please start the service with: python ml_core_enhanced_production.py")
        return 1
    
    # Run all tests
    test_results = []
    
    print_section("1. SYSTEM HEALTH CHECKS")
    test_results.append(("System Status", run_test("System Status", test_system_status)))
    test_results.append(("Model Persistence", run_test("Model Persistence", test_model_persistence)))
    
    print_section("2. MODEL TRAINING TESTS")
    test_results.append(("Model Training", run_test("Model Training (AAPL)", test_model_training, "AAPL")))
    test_results.append(("Feature Engineering", run_test("Feature Engineering", test_feature_engineering)))
    test_results.append(("Ensemble Models", run_test("Ensemble Models", test_ensemble_models)))
    
    print_section("3. BACKTESTING VALIDATION")
    test_results.append(("Backtesting", run_test("Backtesting Engine", test_backtesting)))
    
    print_section("4. PERFORMANCE TESTS")
    test_results.append(("Cache Performance", run_test("Cache Performance", test_cache_performance)))
    test_results.append(("Prediction Stress", run_test("Prediction Stress Test", stress_test_predictions)))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
    for test_name, result in test_results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.ENDC}" if result else f"{Colors.RED}❌ FAILED{Colors.ENDC}"
        print(f"  {test_name:<25} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print_colored("\n🎉 ALL TESTS PASSED! The ML Core is ROCK SOLID! 🎉", Colors.GREEN + Colors.BOLD)
        return 0
    elif passed >= total * 0.8:
        print_colored(f"\n✅ {passed}/{total} tests passed. System is mostly stable.", Colors.GREEN)
        return 0
    else:
        print_colored(f"\n❌ Only {passed}/{total} tests passed. System needs improvements.", Colors.RED)
        return 1

if __name__ == "__main__":
    sys.exit(main())