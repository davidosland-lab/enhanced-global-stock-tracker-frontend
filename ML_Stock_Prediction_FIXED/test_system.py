#!/usr/bin/env python3
"""
Test that all components work correctly
"""

import sys
import warnings
warnings.filterwarnings('ignore')

def test_system():
    print("Testing ML Stock Prediction System...")
    print("="*50)
    
    # Test 1: Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 9):
        print("⚠️  Warning: Python 3.9+ recommended")
    print()
    
    # Test 2: Import critical packages
    print("Testing package imports...")
    
    packages = [
        ('numpy', '1.26.4', 'critical'),
        ('pandas', None, 'required'),
        ('scikit-learn', None, 'required'),
        ('yfinance', None, 'required'),
        ('fastapi', None, 'required'),
        ('ta', None, 'required')
    ]
    
    all_ok = True
    
    for package_name, expected_version, importance in packages:
        try:
            if package_name == 'scikit-learn':
                import sklearn
                version = sklearn.__version__
            else:
                module = __import__(package_name)
                version = module.__version__ if hasattr(module, '__version__') else 'unknown'
            
            # Check numpy version specifically
            if package_name == 'numpy':
                import numpy as np
                major_version = int(np.__version__.split('.')[0])
                if major_version >= 2:
                    print(f"  ❌ {package_name} {version} - WRONG VERSION (need 1.x)")
                    all_ok = False
                else:
                    print(f"  ✅ {package_name} {version} - OK")
            else:
                print(f"  ✅ {package_name} {version}")
                
        except ImportError as e:
            print(f"  ❌ {package_name} - NOT INSTALLED ({importance})")
            all_ok = False
    
    print()
    
    # Test 3: Test ML operations
    if all_ok:
        print("Testing ML operations...")
        try:
            from sklearn.preprocessing import StandardScaler
            from sklearn.ensemble import RandomForestRegressor
            import numpy as np
            import pandas as pd
            
            # Create dummy data
            X = np.random.randn(100, 5)
            y = np.random.randn(100)
            
            # Test scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Test model
            model = RandomForestRegressor(n_estimators=10)
            model.fit(X_scaled, y)
            pred = model.predict(X_scaled[:1])
            
            print("  ✅ ML operations work correctly")
            
        except Exception as e:
            print(f"  ❌ ML operations failed: {e}")
            all_ok = False
    
    print()
    
    # Test 4: Test Yahoo Finance
    print("Testing Yahoo Finance connection...")
    try:
        import yfinance as yf
        df = yf.download("AAPL", period="5d", progress=False, threads=False)
        
        if not df.empty:
            print(f"  ✅ Yahoo Finance works - got {len(df)} days of data")
            print(f"     Latest close: ${df['Close'].iloc[-1]:.2f}")
        else:
            print("  ❌ Yahoo Finance returned no data")
            all_ok = False
            
    except Exception as e:
        print(f"  ❌ Yahoo Finance error: {e}")
        all_ok = False
    
    print()
    print("="*50)
    
    if all_ok:
        print("✅ ALL TESTS PASSED!")
        print("System is ready to use.")
        print("\nRun 3_START.bat to start the ML system")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues above and try again")
    
    return all_ok

if __name__ == "__main__":
    test_system()
    input("\nPress Enter to exit...")