#!/usr/bin/env python3
"""
Test Yahoo Finance directly to see what's happening
"""

import yfinance as yf
import pandas as pd
import numpy as np

def test_yahoo():
    print("="*60)
    print("Testing Yahoo Finance Directly")
    print("="*60)
    print()
    
    symbol = "AAPL"
    
    # Test 1: Basic download
    print(f"Test 1: Downloading {symbol} data...")
    try:
        df = yf.download(symbol, period="6mo", progress=False, threads=False)
        print(f"✅ Success! Got {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Latest data:\n{df.tail(2)}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: Check data quality
    print("Test 2: Checking data quality...")
    if df.empty:
        print("❌ DataFrame is empty")
        return False
    
    # Check for NaN values
    nan_counts = df.isna().sum()
    if nan_counts.sum() > 0:
        print(f"⚠️  Warning: NaN values found:\n{nan_counts[nan_counts > 0]}")
    else:
        print("✅ No NaN values")
    
    # Check column names
    expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if all(col in df.columns for col in expected_cols):
        print("✅ All expected columns present")
    else:
        print(f"❌ Missing columns. Have: {df.columns.tolist()}")
        return False
    
    print()
    
    # Test 3: Calculate simple features
    print("Test 3: Calculating basic features...")
    try:
        features = pd.DataFrame(index=df.index)
        features['returns'] = df['Close'].pct_change()
        features['sma_20'] = df['Close'].rolling(window=20).mean()
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        print(f"✅ Features calculated successfully")
        print(f"Feature sample:\n{features.tail(2)}")
        print()
    except Exception as e:
        print(f"❌ Feature calculation failed: {e}")
        return False
    
    # Test 4: Try sklearn operations
    print("Test 4: Testing sklearn operations...")
    try:
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        
        # Prepare data
        X = features.fillna(0).values[-100:]  # Last 100 rows
        y = np.random.randn(100)  # Dummy target
        
        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        print("✅ StandardScaler works")
        
        # Train simple model
        rf = RandomForestRegressor(n_estimators=10, random_state=42)
        rf.fit(X_scaled[:80], y[:80])
        score = rf.score(X_scaled[80:], y[80:])
        print(f"✅ RandomForest works (score: {score:.4f})")
        
    except Exception as e:
        print(f"❌ sklearn failed: {e}")
        return False
    
    print()
    print("="*60)
    print("✅ All tests passed! Yahoo Finance is working correctly")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_yahoo()
    
    if not success:
        print("\nYahoo Finance has issues. Trying to diagnose...")
        
        # Additional diagnostics
        print("\nChecking yfinance version:")
        import yfinance
        print(f"Version: {yfinance.__version__}")
        
        print("\nChecking pandas version:")
        import pandas
        print(f"Version: {pandas.__version__}")
        
        print("\nChecking numpy version:")
        import numpy
        print(f"Version: {numpy.__version__}")
    
    input("\nPress Enter to exit...")