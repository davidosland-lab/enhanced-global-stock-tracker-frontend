#!/usr/bin/env python3
"""
Test ML Backend to diagnose startup issues
"""

import sys
import traceback

print("=" * 60)
print("ML Backend Diagnostic Test")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    print("  - numpy...", end=" ")
    import numpy as np
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  - pandas...", end=" ")
    import pandas as pd
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  - yfinance...", end=" ")
    import yfinance as yf
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  - sklearn...", end=" ")
    from sklearn.ensemble import RandomForestRegressor
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  - fastapi...", end=" ")
    from fastapi import FastAPI
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  - joblib...", end=" ")
    import joblib
    print("✓")
except Exception as e:
    print(f"✗ Error: {e}")

# Test yfinance with SSL fix
print("\n2. Testing yfinance data fetch...")
try:
    import os
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['CURL_CA_BUNDLE'] = ''
    
    # Try to fetch data
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="1d")
    if not data.empty:
        print(f"  ✓ Successfully fetched AAPL data: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("  ⚠ Data fetch returned empty")
except Exception as e:
    print(f"  ✗ Error fetching data: {e}")
    traceback.print_exc()

# Test database creation
print("\n3. Testing database creation...")
try:
    import sqlite3
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    print("  ✓ SQLite works")
    conn.close()
except Exception as e:
    print(f"  ✗ Error with SQLite: {e}")

# Test FastAPI app creation
print("\n4. Testing FastAPI app...")
try:
    app = FastAPI()
    @app.get("/test")
    def test():
        return {"status": "ok"}
    print("  ✓ FastAPI app created")
except Exception as e:
    print(f"  ✗ Error creating FastAPI app: {e}")

print("\n" + "=" * 60)
print("Diagnostic complete!")
print("=" * 60)