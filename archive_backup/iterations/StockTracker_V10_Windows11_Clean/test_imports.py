"""
Test script to verify all imports and dependencies
"""

import sys
import traceback
from typing import Tuple, List

def test_import(module_name: str) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return True, f"✓ {module_name}"
    except ImportError as e:
        return False, f"✗ {module_name}: {str(e)}"
    except Exception as e:
        return False, f"✗ {module_name}: {type(e).__name__}: {str(e)}"

def test_service_imports(service_file: str) -> Tuple[bool, List[str]]:
    """Test all imports for a service"""
    errors = []
    try:
        # Try to import the service module
        module = __import__(service_file.replace('.py', ''))
        return True, []
    except ImportError as e:
        errors.append(f"Import error: {str(e)}")
        # Try to identify missing dependencies
        import re
        missing = re.findall(r"No module named ['\"]([^'\"]+)['\"]", str(e))
        if missing:
            errors.append(f"Missing module: {missing[0]}")
    except Exception as e:
        errors.append(f"{type(e).__name__}: {str(e)}")
        traceback.print_exc()
    return False, errors

def main():
    print("="*60)
    print("StockTracker V10 - Import Test")
    print("="*60)
    print()
    
    # Test core dependencies
    print("Testing Core Dependencies:")
    core_deps = [
        'fastapi', 'uvicorn', 'pandas', 'numpy', 
        'yfinance', 'sklearn', 'requests', 'joblib'
    ]
    
    all_ok = True
    for dep in core_deps:
        ok, msg = test_import(dep)
        print(f"  {msg}")
        if not ok:
            all_ok = False
    print()
    
    # Test optional dependencies
    print("Testing Optional Dependencies:")
    optional_deps = ['transformers', 'torch', 'sqlite3']
    for dep in optional_deps:
        ok, msg = test_import(dep)
        print(f"  {msg}")
    print()
    
    # Test each service
    print("Testing Service Modules:")
    services = [
        ('main_backend', 8000),
        ('ml_backend', 8002),
        ('finbert_backend', 8003),
        ('historical_backend', 8004),
        ('backtesting_backend', 8005)
    ]
    
    for service, port in services:
        ok, errors = test_service_imports(service)
        if ok:
            print(f"  ✓ {service}.py (Port {port})")
        else:
            print(f"  ✗ {service}.py (Port {port})")
            for error in errors:
                print(f"      {error}")
    print()
    
    # Test specific issues
    print("Testing Specific Configurations:")
    
    # Test yfinance
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        if not hist.empty:
            print("  ✓ Yahoo Finance API connection")
        else:
            print("  ⚠ Yahoo Finance returned no data")
    except Exception as e:
        print(f"  ✗ Yahoo Finance test failed: {e}")
    
    # Test SQLite
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        conn.close()
        print("  ✓ SQLite database")
    except Exception as e:
        print(f"  ✗ SQLite test failed: {e}")
    
    # Test FastAPI
    try:
        from fastapi import FastAPI
        app = FastAPI()
        print("  ✓ FastAPI initialization")
    except Exception as e:
        print(f"  ✗ FastAPI test failed: {e}")
    
    print()
    print("="*60)
    if all_ok:
        print("✓ All core dependencies are properly installed")
    else:
        print("✗ Some dependencies are missing or have issues")
        print("  Run INSTALL.bat to reinstall dependencies")
    print("="*60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")