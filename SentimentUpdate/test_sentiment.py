import os
import sys
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Test if imports work
try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except ImportError as e:
    print(f"✗ yfinance import failed: {e}")
    
try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")
    
try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")
    
try:
    from sklearn.ensemble import RandomForestRegressor
    print("✓ scikit-learn imported successfully")
except ImportError as e:
    print(f"✗ scikit-learn import failed: {e}")

# Test Yahoo Finance connection
print("\nTesting Yahoo Finance connection...")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1d")
    if not hist.empty:
        print("✓ Yahoo Finance working - AAPL data retrieved")
        print(f"  Latest price: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("✗ Yahoo Finance returned empty data")
except Exception as e:
    print(f"✗ Yahoo Finance error: {e}")

# Test VIX
print("\nTesting VIX data...")
try:
    vix = yf.Ticker("^VIX")
    hist = vix.history(period="1d")
    if not hist.empty:
        print("✓ VIX data retrieved")
        print(f"  VIX level: {hist['Close'].iloc[-1]:.2f}")
    else:
        print("✗ VIX returned empty data")
except Exception as e:
    print(f"✗ VIX error: {e}")

print("\nTest complete!")