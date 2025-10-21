#!/usr/bin/env python3
"""Test fetching 1 year of data - NO FALLBACK"""

import yfinance as yf

print("="*60)
print("TESTING 1 YEAR DATA FETCH - REAL DATA ONLY")
print("="*60)

# Test AAPL
print("\n1. Testing AAPL (1 year)...")
try:
    data = yf.download('AAPL', period='1y', progress=False)
    if data is not None and not data.empty:
        print(f"✅ SUCCESS: Got {len(data)} days of REAL AAPL data")
        print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
    else:
        print("❌ FAILED: No data returned")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test CBA.AX
print("\n2. Testing CBA.AX (1 year)...")
try:
    data = yf.download('CBA.AX', period='1y', progress=False)
    if data is not None and not data.empty:
        print(f"✅ SUCCESS: Got {len(data)} days of REAL CBA.AX data")
        print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"   Latest close: AUD ${data['Close'].iloc[-1]:.2f}")
    else:
        print("❌ FAILED: No data returned")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test training requirement (need 50+ data points)
print("\n3. Checking training requirements...")
print(f"   Minimum required: 50 data points")
print(f"   AAPL 1y: {len(data) if 'data' in locals() else 0} points")
if len(data) >= 50:
    print("   ✅ SUFFICIENT for training")
else:
    print("   ❌ INSUFFICIENT for training")

print("\n" + "="*60)
print("CONCLUSION: Using REAL Yahoo Finance data ONLY")
print("NO fallback, NO demo, NO simulated data")
print("="*60)