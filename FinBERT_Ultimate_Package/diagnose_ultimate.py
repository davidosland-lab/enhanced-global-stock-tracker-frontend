#!/usr/bin/env python3
"""
FinBERT Ultimate - Diagnostic Tool
Checks system setup and identifies common issues
"""

import sys
import os
import json
from datetime import datetime

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Check Python version"""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python Version: {sys.version}")
    
    if version.major == 3 and version.minor >= 12:
        print("✅ Python 3.12+ detected - OPTIMAL")
        return True
    elif version.major == 3 and version.minor >= 10:
        print("⚠️  Python 3.10-3.11 detected - Should work but 3.12 recommended")
        return True
    else:
        print("❌ Python version too old - Requires 3.10+")
        return False

def check_numpy():
    """Check NumPy installation and version"""
    print_header("NumPy Check")
    
    try:
        import numpy as np
        print(f"NumPy Version: {np.__version__}")
        
        major, minor = map(int, np.__version__.split('.')[:2])
        
        if major >= 1 and minor >= 26:
            print("✅ NumPy 1.26+ detected - Perfect for Python 3.12")
            return True
        elif major >= 1 and minor >= 24:
            print("⚠️  NumPy 1.24-1.25 - May have issues with Python 3.12")
            print("   Run: pip install --upgrade numpy>=1.26.0")
            return False
        else:
            print("❌ NumPy version too old")
            print("   Run: pip install --upgrade numpy>=1.26.0")
            return False
            
    except ImportError:
        print("❌ NumPy not installed")
        print("   Run: pip install numpy>=1.26.0")
        return False

def check_core_packages():
    """Check core required packages"""
    print_header("Core Packages Check")
    
    packages = {
        'pandas': '2.0.0',
        'sklearn': '1.3.0',
        'yfinance': '0.2.28',
        'ta': '0.10.2',
        'flask': '2.3.0',
        'flask_cors': '4.0.0',
        'requests': '2.31.0',
        'feedparser': '6.0.10'
    }
    
    all_good = True
    
    for package, min_version in packages.items():
        try:
            if package == 'sklearn':
                import sklearn
                version = sklearn.__version__
            elif package == 'flask_cors':
                import flask_cors
                version = getattr(flask_cors, '__version__', 'unknown')
            else:
                module = __import__(package)
                version = module.__version__
            
            print(f"✅ {package:15} {version:10} (minimum: {min_version})")
            
        except ImportError:
            print(f"❌ {package:15} NOT INSTALLED")
            all_good = False
    
    return all_good

def check_finbert():
    """Check FinBERT components"""
    print_header("FinBERT Components Check")
    
    finbert_available = False
    
    try:
        import torch
        print(f"✅ PyTorch installed: {torch.__version__}")
        
        try:
            import transformers
            print(f"✅ Transformers installed: {transformers.__version__}")
            
            # Try to load tokenizer (quick test)
            from transformers import AutoTokenizer
            print("✅ FinBERT components available")
            finbert_available = True
            
        except ImportError:
            print("⚠️  Transformers not installed")
            print("   Run: pip install transformers>=4.30.0")
            
    except ImportError:
        print("⚠️  PyTorch not installed (FinBERT will use fallback)")
        print("   To install: pip install torch transformers")
        print("   Note: This is optional - system has fallback sentiment")
    
    return finbert_available

def check_directories():
    """Check required directories"""
    print_header("Directory Check")
    
    dirs = ['cache', 'models', 'logs', 'data']
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name:10} exists")
        else:
            print(f"⚠️  {dir_name:10} missing - creating...")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"   Created {dir_name}")
            except Exception as e:
                print(f"   ❌ Failed to create: {e}")
                all_exist = False
    
    return all_exist

def check_data_fetch():
    """Test data fetching"""
    print_header("Data Fetching Test")
    
    try:
        import yfinance as yf
        
        # Test with a reliable symbol
        print("Testing Yahoo Finance with AAPL...")
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print(f"✅ Data fetch successful - Got {len(hist)} days of data")
            print(f"   Latest close: ${hist['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Data fetch returned empty")
            return False
            
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        return False

def test_prediction_data():
    """Test the critical prediction data fetch issue"""
    print_header("Prediction Data Fetch Test")
    
    try:
        import yfinance as yf
        import pandas as pd
        
        symbol = "AAPL"
        
        # Test different periods
        periods = ["1mo", "3mo", "6mo"]
        
        for period in periods:
            print(f"\nTesting {period} data fetch for {symbol}...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if not df.empty:
                data_points = len(df)
                print(f"  ✅ {period}: {data_points} days fetched")
                
                # Check if enough for SMA_50
                if data_points >= 50:
                    print(f"     Can calculate SMA_50: YES")
                else:
                    print(f"     Can calculate SMA_50: NO (need 50, have {data_points})")
            else:
                print(f"  ❌ {period}: Failed to fetch data")
        
        print("\n📌 IMPORTANT: Predictions should use at least 3mo for SMA_50!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_api_keys():
    """Check for optional API keys"""
    print_header("API Keys Check (Optional)")
    
    api_keys = {
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
        'IEX_TOKEN': 'IEX Cloud',
        'FINNHUB_API_KEY': 'Finnhub',
        'POLYGON_API_KEY': 'Polygon.io',
        'FRED_API_KEY': 'FRED (Federal Reserve)'
    }
    
    found_any = False
    
    for key, service in api_keys.items():
        value = os.getenv(key)
        if value and value != 'demo':
            print(f"✅ {service:20} API key configured")
            found_any = True
        else:
            print(f"⚠️  {service:20} Not configured (optional)")
    
    if not found_any:
        print("\n📌 No API keys configured - System will use Yahoo Finance only")
        print("   This is fine for most use cases!")
    
    return True

def main():
    """Run all diagnostics"""
    print("\n" + "🔍"*30)
    print("  FINBERT ULTIMATE - SYSTEM DIAGNOSTICS")
    print("🔍"*30)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Run checks
    checks = [
        ('Python', check_python()),
        ('NumPy', check_numpy()),
        ('Core Packages', check_core_packages()),
        ('FinBERT', check_finbert()),
        ('Directories', check_directories()),
        ('Data Fetch', check_data_fetch()),
        ('Prediction Data', test_prediction_data()),
        ('API Keys', check_api_keys())
    ]
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    critical_pass = True
    optional_pass = True
    
    for name, passed in checks:
        results['checks'][name] = passed
        
        if name in ['Python', 'NumPy', 'Core Packages', 'Directories', 'Data Fetch']:
            # Critical checks
            if passed:
                print(f"✅ {name:20} PASSED")
            else:
                print(f"❌ {name:20} FAILED (CRITICAL)")
                critical_pass = False
        else:
            # Optional checks
            if passed:
                print(f"✅ {name:20} PASSED")
            else:
                print(f"⚠️  {name:20} WARNING (Optional)")
                optional_pass = False
    
    # Final verdict
    print("\n" + "="*60)
    
    if critical_pass:
        if optional_pass:
            print("🎉 SYSTEM FULLY OPERATIONAL - All checks passed!")
        else:
            print("✅ SYSTEM OPERATIONAL - Core features working")
            print("   Some optional features unavailable")
    else:
        print("❌ SYSTEM NOT READY - Critical issues found")
        print("   Please fix the issues above and run again")
    
    print("="*60)
    
    # Save results
    try:
        with open('diagnostic_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\n📄 Full results saved to: diagnostic_results.json")
    except:
        pass
    
    return critical_pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)