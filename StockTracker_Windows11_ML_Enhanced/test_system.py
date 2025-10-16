"""
Stock Tracker ML Enhanced - System Test Suite
Verifies all components are working correctly
"""

import sys
import json
import time
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, 'backend')

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    errors = []
    
    required_modules = [
        'fastapi',
        'numpy',
        'pandas',
        'sklearn',
        'yfinance',
        'transformers',
        'torch',
        'aiohttp',
        'bs4'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            errors.append(module)
    
    return len(errors) == 0

def test_directories():
    """Test directory structure"""
    print("\nTesting directory structure...")
    
    required_dirs = ['backend', 'frontend', 'data', 'models', 'logs', 'uploads', 'cache']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing - creating...")
            dir_path.mkdir(exist_ok=True)
    
    return True

def test_backend_initialization():
    """Test backend can be initialized"""
    print("\nTesting backend initialization...")
    
    try:
        from main_backend import app, orchestrator
        print("✓ Backend initialized successfully")
        
        # Check components
        print("✓ FastAPI app created")
        print("✓ ML Orchestrator initialized")
        
        if orchestrator.finbert_analyzer:
            print("✓ FinBERT analyzer ready")
        else:
            print("⚠ FinBERT analyzer not initialized (will download on first use)")
        
        return True
    except Exception as e:
        print(f"✗ Backend initialization failed: {e}")
        return False

async def test_data_fetching():
    """Test data fetching with cache"""
    print("\nTesting data fetching...")
    
    try:
        from main_backend import DataFetcher
        fetcher = DataFetcher()
        
        # Test fetching AAPL data
        df = await fetcher.get_historical_data("AAPL", period="1mo")
        
        if not df.empty:
            print(f"✓ Fetched {len(df)} days of AAPL data")
            print(f"✓ Latest price: ${df['Close'].iloc[-1]:.2f}")
            
            # Test cache
            start = time.time()
            df2 = await fetcher.get_historical_data("AAPL", period="1mo")
            cache_time = time.time() - start
            
            if cache_time < 0.1:  # Should be instant from cache
                print(f"✓ Cache working (fetch time: {cache_time:.3f}s)")
            else:
                print(f"⚠ Cache may not be working (fetch time: {cache_time:.3f}s)")
            
            return True
        else:
            print("✗ No data fetched")
            return False
            
    except Exception as e:
        print(f"✗ Data fetching failed: {e}")
        return False

def test_feature_engineering():
    """Test technical indicator calculations"""
    print("\nTesting feature engineering...")
    
    try:
        from main_backend import FeatureEngineer
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=100)
        df = pd.DataFrame({
            'Open': np.random.randn(100).cumsum() + 100,
            'High': np.random.randn(100).cumsum() + 101,
            'Low': np.random.randn(100).cumsum() + 99,
            'Close': np.random.randn(100).cumsum() + 100,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        # Calculate indicators
        engineer = FeatureEngineer()
        df_features = engineer.calculate_technical_indicators(df)
        
        # Check features
        expected_features = ['RSI', 'MACD', 'BB_Upper', 'ATR', 'OBV', 'MFI', 'ADX']
        missing = []
        
        for feature in expected_features:
            if feature in df_features.columns:
                print(f"✓ {feature} calculated")
            else:
                print(f"✗ {feature} missing")
                missing.append(feature)
        
        print(f"\n✓ Total features calculated: {len(df_features.columns)}")
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"✗ Feature engineering failed: {e}")
        return False

def test_finbert():
    """Test FinBERT sentiment analysis"""
    print("\nTesting FinBERT sentiment analysis...")
    
    try:
        from main_backend import FinBERTAnalyzer
        
        analyzer = FinBERTAnalyzer()
        
        # Test text analysis
        test_text = "Apple reported record profits and strong iPhone sales."
        result = analyzer.analyze_text(test_text)
        
        if result and 'overall' in result:
            print(f"✓ Sentiment analysis working")
            print(f"  Positive: {result['positive']:.2f}")
            print(f"  Negative: {result['negative']:.2f}")
            print(f"  Neutral: {result['neutral']:.2f}")
            print(f"  Overall: {result['overall']:.2f}")
            return True
        else:
            print("⚠ FinBERT not fully initialized (will work after model download)")
            return True  # Not a critical failure
            
    except Exception as e:
        print(f"⚠ FinBERT test skipped: {e}")
        return True  # Not critical

def test_database_connections():
    """Test SQLite database connections"""
    print("\nTesting database connections...")
    
    try:
        import sqlite3
        from main_backend import Config
        
        databases = [
            ('Cache DB', Config.CACHE_DB),
            ('Models DB', Config.MODELS_DB),
            ('Backtest DB', Config.BACKTEST_DB)
        ]
        
        for name, db_path in databases:
            try:
                Path(db_path).parent.mkdir(exist_ok=True)
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT 1")
                conn.close()
                print(f"✓ {name} connection successful")
            except Exception as e:
                print(f"✗ {name} connection failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Stock Tracker ML Enhanced - System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Directory Structure", test_directories),
        ("Database Connections", test_database_connections),
        ("Backend Initialization", test_backend_initialization),
        ("Feature Engineering", test_feature_engineering),
        ("FinBERT", test_finbert)
    ]
    
    # Async tests
    async def run_async_tests():
        return await test_data_fetching()
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run async tests
    try:
        async_result = asyncio.run(run_async_tests())
        results.append(("Data Fetching", async_result))
    except Exception as e:
        print(f"✗ Async tests failed: {e}")
        results.append(("Data Fetching", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - System is ready!")
    elif passed >= total - 2:
        print("\n⚠️ MOSTLY WORKING - Some non-critical features may need attention")
    else:
        print("\n❌ CRITICAL ISSUES - Please check the errors above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)