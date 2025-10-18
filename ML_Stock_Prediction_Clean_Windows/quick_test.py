#!/usr/bin/env python3
"""
Quick test script to verify the ML system is working
"""

import sys
import importlib.util

def test_imports():
    """Test if all required packages can be imported"""
    packages = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'numpy',
        'yfinance',
        'sklearn',
        'xgboost',
        'lightgbm',
        'ta',
        'aiohttp',
        'aiofiles',
        'aiosqlite',
        'psutil'
    ]
    
    print("Testing package imports...")
    failed = []
    
    for package in packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                failed.append(package)
                print(f"  ❌ {package} - NOT INSTALLED")
            else:
                print(f"  ✅ {package} - OK")
        except ImportError:
            failed.append(package)
            print(f"  ❌ {package} - NOT INSTALLED")
    
    return failed

def test_ml_core():
    """Test if ML core can be imported"""
    print("\nTesting ML core import...")
    try:
        import ml_core
        print("  ✅ ML core imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ ML core import failed: {e}")
        return False

def test_data_fetch():
    """Test if we can fetch real data"""
    print("\nTesting data fetch...")
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        if not hist.empty:
            print(f"  ✅ Successfully fetched {len(hist)} days of AAPL data")
            print(f"     Latest close: ${hist['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("  ❌ No data returned")
            return False
    except Exception as e:
        print(f"  ❌ Data fetch failed: {e}")
        return False

def main():
    print("=" * 50)
    print("ML Stock Prediction System - Quick Test")
    print("=" * 50)
    print()
    
    # Test Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 9):
        print("  ⚠️  Warning: Python 3.9+ recommended")
    print()
    
    # Test imports
    failed = test_imports()
    
    if failed:
        print("\n❌ MISSING PACKAGES")
        print("Please run: pip install -r requirements.txt")
        print(f"Missing: {', '.join(failed)}")
        return
    
    # Test ML core
    if not test_ml_core():
        print("\n❌ ML CORE ERROR")
        print("Check error messages above")
        return
    
    # Test data
    if not test_data_fetch():
        print("\n❌ DATA FETCH ERROR")
        print("Check internet connection")
        return
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("System is ready to use")
    print("Run: python ml_core.py")
    print("=" * 50)

if __name__ == "__main__":
    main()