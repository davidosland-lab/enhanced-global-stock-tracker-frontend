#!/usr/bin/env python3
"""
Fix NumPy compatibility issue
The problem: NumPy 2.x is incompatible with many ML libraries
The solution: Downgrade to NumPy 1.x
"""

import subprocess
import sys

def fix_numpy():
    print("="*60)
    print("Fixing NumPy Compatibility Issue")
    print("="*60)
    print()
    print("Problem: You have NumPy 2.3.4 which breaks scikit-learn")
    print("Solution: Downgrade to NumPy 1.26.4 (compatible version)")
    print()
    
    commands = [
        # Step 1: Uninstall current numpy
        {
            'name': 'Uninstalling NumPy 2.x',
            'cmd': [sys.executable, '-m', 'pip', 'uninstall', '-y', 'numpy']
        },
        # Step 2: Install compatible numpy
        {
            'name': 'Installing NumPy 1.26.4',
            'cmd': [sys.executable, '-m', 'pip', 'install', 'numpy==1.26.4']
        },
        # Step 3: Reinstall scipy with compatible version
        {
            'name': 'Reinstalling scipy',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'scipy==1.11.4']
        },
        # Step 4: Reinstall scikit-learn
        {
            'name': 'Reinstalling scikit-learn',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'scikit-learn==1.3.2']
        },
        # Step 5: Verify pandas compatibility
        {
            'name': 'Checking pandas compatibility',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'pandas==2.1.3']
        }
    ]
    
    for step in commands:
        print(f"\n{step['name']}...")
        try:
            result = subprocess.run(step['cmd'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Success")
            else:
                print(f"⚠️ Warning: {result.stderr[:100] if result.stderr else 'Check output'}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Testing the fix...")
    print("="*60)
    
    # Test if it works now
    test_code = """
import warnings
warnings.filterwarnings('ignore')

print("Testing imports...")

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__} imported")
except Exception as e:
    print(f"❌ NumPy failed: {e}")
    exit(1)

try:
    import pandas as pd
    print(f"✅ Pandas {pd.__version__} imported")
except Exception as e:
    print(f"❌ Pandas failed: {e}")
    exit(1)

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    print(f"✅ Scikit-learn imported successfully")
except Exception as e:
    print(f"❌ Scikit-learn failed: {e}")
    exit(1)

try:
    import scipy
    print(f"✅ Scipy {scipy.__version__} imported")
except Exception as e:
    print(f"❌ Scipy failed: {e}")
    exit(1)

# Test actual ML operations
try:
    print("\\nTesting ML operations...")
    import yfinance as yf
    
    # Get data
    df = yf.download("AAPL", period="1mo", progress=False, threads=False)
    
    # Create simple features
    X = df[['Close', 'Volume', 'High', 'Low']].values
    y = df['Close'].shift(-1).fillna(method='ffill').values
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_scaled[:-1], y[:-1])
    
    # Predict
    pred = model.predict(X_scaled[-1:])
    
    print(f"✅ ML operations work! Prediction: {pred[0]:.2f}")
    
except Exception as e:
    print(f"❌ ML operations failed: {e}")
    exit(1)

print("\\n✅ All tests passed! The system should work now.")
exit(0)
"""
    
    # Write and run test
    with open('test_ml.py', 'w') as f:
        f.write(test_code)
    
    result = subprocess.run([sys.executable, 'test_ml.py'], capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n" + "="*60)
        print("🎉 SUCCESS! The ML system should work now!")
        print("="*60)
        print("\nYou can now run:")
        print("1. START_MINIMAL.bat - For simple version")
        print("2. 3_start_REAL_DATA_ONLY.bat - For full version")
        return True
    else:
        print("\n" + "="*60)
        print("Additional fixes needed")
        print("="*60)
        return False

if __name__ == "__main__":
    fix_numpy()
    input("\nPress Enter to exit...")