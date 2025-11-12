#!/usr/bin/env python3
"""
Diagnostic script to test Alpha Vantage API responses for different ticker formats.
Tests ASX stocks with various formats (.AX, .AUS, no suffix) and US stocks.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to load API key
from models.config.config import Config
config = Config()
API_KEY = config.alpha_vantage_api_key

if not API_KEY or API_KEY == "your_alpha_vantage_api_key_here":
    print("ERROR: No valid Alpha Vantage API key found in config.py")
    print("Please set your API key in models/config/config.py")
    sys.exit(1)

print(f"Using API Key: {API_KEY[:8]}...")
print("=" * 80)

def test_ticker(ticker: str, description: str):
    """Test a single ticker and print detailed response"""
    print(f"\n{'='*80}")
    print(f"Testing: {ticker} ({description})")
    print(f"{'='*80}")
    
    # Test GLOBAL_QUOTE endpoint (used for validation)
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": API_KEY
    }
    
    print(f"URL: {url}")
    print(f"Params: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"\nHTTP Status: {response.status_code}")
        
        data = response.json()
        print(f"\nFull Response:")
        print(json.dumps(data, indent=2))
        
        # Check for success
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            print(f"\n✅ SUCCESS - Found quote data:")
            print(f"   Symbol: {quote.get('01. symbol', 'N/A')}")
            print(f"   Price: {quote.get('05. price', 'N/A')}")
            print(f"   Volume: {quote.get('06. volume', 'N/A')}")
            print(f"   Latest Trading Day: {quote.get('07. latest trading day', 'N/A')}")
            return True
        else:
            print(f"\n❌ FAILED - No quote data returned")
            
            # Check for specific error messages
            if "Note" in data:
                print(f"   API Note: {data['Note']}")
            if "Error Message" in data:
                print(f"   Error Message: {data['Error Message']}")
            if "Information" in data:
                print(f"   Information: {data['Information']}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False

# Test cases
test_cases = [
    # US Stocks (should work)
    ("AAPL", "US - Apple Inc."),
    ("MSFT", "US - Microsoft Corporation"),
    
    # ASX Stocks - Different formats
    ("CBA.AUS", "ASX - Commonwealth Bank (.AUS format)"),
    ("CBA.AX", "ASX - Commonwealth Bank (.AX format)"),
    ("CBA", "ASX - Commonwealth Bank (no suffix)"),
    
    ("BHP.AUS", "ASX - BHP Group (.AUS format)"),
    ("BHP.AX", "ASX - BHP Group (.AX format)"),
    ("BHP", "ASX - BHP Group (no suffix)"),
    
    ("NAB.AUS", "ASX - National Australia Bank (.AUS format)"),
    ("NAB.AX", "ASX - National Australia Bank (.AX format)"),
    ("NAB", "ASX - National Australia Bank (no suffix)"),
    
    # Try London format as reference
    ("BP.LON", "London - BP (.LON format)"),
    ("BP", "London/US - BP (no suffix)"),
]

# Run tests
results = {}
for ticker, description in test_cases:
    success = test_ticker(ticker, description)
    results[ticker] = success
    
    # Rate limiting - wait 12 seconds between calls
    if ticker != test_cases[-1][0]:  # Don't wait after last test
        print("\n⏱️  Waiting 12 seconds for rate limiting...")
        time.sleep(12)

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY OF RESULTS")
print("=" * 80)

us_stocks = [(t, r) for t, r in results.items() if not any(x in t for x in ['.AUS', '.AX', '.LON', 'CBA', 'BHP', 'NAB'])]
asx_aus = [(t, r) for t, r in results.items() if '.AUS' in t]
asx_ax = [(t, r) for t, r in results.items() if '.AX' in t]
asx_none = [(t, r) for t, r in results.items() if t in ['CBA', 'BHP', 'NAB']]
london = [(t, r) for t, r in results.items() if '.LON' in t or t == 'BP']

print("\n📊 US Stocks:")
for ticker, success in us_stocks:
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {ticker}: {status}")

print("\n📊 ASX Stocks (.AUS format):")
for ticker, success in asx_aus:
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {ticker}: {status}")

print("\n📊 ASX Stocks (.AX format):")
for ticker, success in asx_ax:
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {ticker}: {status}")

print("\n📊 ASX Stocks (no suffix):")
for ticker, success in asx_none:
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {ticker}: {status}")

print("\n📊 London Stocks:")
for ticker, success in london:
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"   {ticker}: {status}")

# Conclusion
print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

us_success = any(r for _, r in us_stocks)
asx_aus_success = any(r for _, r in asx_aus)
asx_ax_success = any(r for _, r in asx_ax)
asx_none_success = any(r for _, r in asx_none)

if us_success:
    print("✅ Alpha Vantage API is working correctly for US stocks")
else:
    print("❌ Alpha Vantage API is NOT working for US stocks (check API key)")

if asx_aus_success:
    print("✅ .AUS format works for ASX stocks - use this format")
elif asx_ax_success:
    print("✅ .AX format works for ASX stocks - use this format")
elif asx_none_success:
    print("✅ No suffix works for ASX stocks - use this format")
else:
    print("❌ NONE of the ASX ticker formats work")
    print("   Alpha Vantage free tier likely does NOT support ASX stocks")
    print("   Recommendation: Use US stocks only, or upgrade to paid plan")

print("\n" + "=" * 80)
