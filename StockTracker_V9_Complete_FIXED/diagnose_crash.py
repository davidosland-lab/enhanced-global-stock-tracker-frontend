#!/usr/bin/env python3
"""
Diagnose the ACTUAL crash reason - NO MOCK DATA
"""

import sys
import os
import traceback

print("=" * 60)
print("DIAGNOSING ACTUAL ML BACKEND CRASH")
print("=" * 60)

# Set environment for SSL
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

# Try to run the actual ML backend and catch the real error
try:
    print("\nTrying to import and run enhanced_ml_backend.py...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import the actual backend
    import enhanced_ml_backend
    print("✓ Import successful")
    
except Exception as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TRYING enhanced_ml_backend_fixed.py...")
    try:
        import enhanced_ml_backend_fixed
        print("✓ Fixed version imports OK")
    except Exception as e2:
        print(f"❌ FIXED VERSION ALSO FAILS: {e2}")
        traceback.print_exc()

# Now test the actual components that might be failing
print("\n" + "=" * 60)
print("TESTING INDIVIDUAL COMPONENTS:")

# Test 1: Database creation
print("\n1. Testing SQLite database creation...")
try:
    import sqlite3
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
    conn.close()
    os.remove("test.db")
    print("✓ SQLite works")
except Exception as e:
    print(f"❌ SQLite failed: {e}")

# Test 2: FastAPI
print("\n2. Testing FastAPI...")
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
    print("✓ FastAPI works")
except Exception as e:
    print(f"❌ FastAPI failed: {e}")

# Test 3: Uvicorn
print("\n3. Testing Uvicorn...")
try:
    import uvicorn
    print(f"✓ Uvicorn version: {uvicorn.__version__}")
except Exception as e:
    print(f"❌ Uvicorn failed: {e}")

# Test 4: The actual issue - running uvicorn
print("\n4. Testing if we can start a simple FastAPI app...")
try:
    from fastapi import FastAPI
    import threading
    import time
    import uvicorn
    
    app = FastAPI()
    
    @app.get("/test")
    def test():
        return {"status": "ok"}
    
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8099, log_level="error")
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2)
    
    # Test if it's running
    import requests
    try:
        r = requests.get("http://localhost:8099/test", timeout=1)
        if r.status_code == 200:
            print("✓ Can start and access FastAPI server")
    except:
        print("❌ Server started but can't access it")
        
except Exception as e:
    print(f"❌ Can't start FastAPI server: {e}")
    traceback.print_exc()

# Test 5: The actual problem might be in yfinance
print("\n5. Testing yfinance with REAL data (NO MOCK)...")
try:
    import yfinance as yf
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1d")
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        print(f"✓ yfinance works - AAPL real price: ${price:.2f}")
    else:
        print("❌ yfinance returns empty data")
except Exception as e:
    print(f"❌ yfinance failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)