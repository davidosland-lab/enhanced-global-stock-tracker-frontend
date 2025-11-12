#!/usr/bin/env python3
"""
Quick diagnostic to test Alpha Vantage API with different ticker formats
"""

import requests
import json
import time

# Alpha Vantage API Key from deployment package
API_KEY = "68ZFANK047DL0KSR"

def test_ticker(ticker, description):
    """Test a single ticker with Alpha Vantage GLOBAL_QUOTE"""
    print(f"\n{'='*80}")
    print(f"Testing: {ticker}")
    print(f"Description: {description}")
    print(f"{'='*80}")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            if quote.get('01. symbol'):
                print(f"\n✅ SUCCESS!")
                print(f"   Symbol: {quote.get('01. symbol')}")
                print(f"   Price: ${quote.get('05. price')}")
                print(f"   Volume: {quote.get('06. volume')}")
                print(f"   Latest Trading Day: {quote.get('07. latest trading day')}")
                return True
        
        print(f"\n❌ FAILED - No valid quote data")
        
        # Check for error messages
        if "Note" in data:
            print(f"   API Note: {data['Note']}")
        if "Error Message" in data:
            print(f"   Error: {data['Error Message']}")
        if "Information" in data:
            print(f"   Info: {data['Information']}")
            
        return False
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False

print("="*80)
print("ALPHA VANTAGE TICKER FORMAT DIAGNOSTIC")
print("="*80)
print(f"API Key: {API_KEY[:8]}...")
print(f"Testing different ticker formats to determine Alpha Vantage support")
print("="*80)

# Test cases - order matters for rate limiting
test_cases = [
    # US Stocks (guaranteed to work)
    ("AAPL", "US - Apple Inc. (baseline test)"),
    ("MSFT", "US - Microsoft (baseline test)"),
    
    # ASX with .AUS suffix (Alpha Vantage format according to docs)
    ("CBA.AUS", "ASX - Commonwealth Bank with .AUS suffix"),
    ("BHP.AUS", "ASX - BHP Group with .AUS suffix"),
    ("NAB.AUS", "ASX - National Australia Bank with .AUS suffix"),
    
    # ASX with .AX suffix (Yahoo Finance format)
    ("CBA.AX", "ASX - Commonwealth Bank with .AX suffix"),
    ("BHP.AX", "ASX - BHP Group with .AX suffix"),
    
    # ASX with no suffix
    ("CBA", "ASX - Commonwealth Bank with no suffix"),
    ("BHP", "ASX - BHP Group with no suffix"),
]

results = {}
for i, (ticker, description) in enumerate(test_cases):
    success = test_ticker(ticker, description)
    results[ticker] = success
    
    # Rate limiting - 12 seconds between calls
    if i < len(test_cases) - 1:
        print(f"\n⏱️  Waiting 12 seconds for rate limiting...")
        time.sleep(12)

# Summary
print("\n\n" + "="*80)
print("SUMMARY")
print("="*80)

us_tickers = [t for t in results.keys() if t in ['AAPL', 'MSFT']]
aus_tickers = [t for t in results.keys() if '.AUS' in t]
ax_tickers = [t for t in results.keys() if '.AX' in t]
no_suffix = [t for t in results.keys() if t in ['CBA', 'BHP', 'NAB']]

print("\n📊 US Stocks (Baseline):")
for ticker in us_tickers:
    status = "✅" if results[ticker] else "❌"
    print(f"   {status} {ticker}")

print("\n📊 ASX Stocks with .AUS suffix:")
for ticker in aus_tickers:
    status = "✅" if results[ticker] else "❌"
    print(f"   {status} {ticker}")

print("\n📊 ASX Stocks with .AX suffix:")
for ticker in ax_tickers:
    status = "✅" if results[ticker] else "❌"
    print(f"   {status} {ticker}")

print("\n📊 ASX Stocks with no suffix:")
for ticker in no_suffix:
    status = "✅" if results[ticker] else "❌"
    print(f"   {status} {ticker}")

# Conclusion
print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

us_working = any(results[t] for t in us_tickers)
aus_working = any(results[t] for t in aus_tickers)
ax_working = any(results[t] for t in ax_tickers)
no_suffix_working = any(results.get(t, False) for t in no_suffix)

if not us_working:
    print("❌ CRITICAL: US stocks not working - API key may be invalid or rate limited")
    print("   Please check API key and rate limits")
else:
    print("✅ US stocks working - Alpha Vantage API is functional")
    
    if aus_working:
        print("✅ ASX stocks work with .AUS suffix - use this format")
        print("   Recommendation: Keep .AUS conversion in code")
    elif ax_working:
        print("✅ ASX stocks work with .AX suffix - use this format")
        print("   Recommendation: Change code to keep .AX suffix")
    elif no_suffix_working:
        print("✅ ASX stocks work with no suffix - use this format")
        print("   Recommendation: Change code to strip suffix entirely")
    else:
        print("❌ CRITICAL: NO ASX ticker formats work")
        print("   Alpha Vantage free tier may NOT support Australian stocks")
        print("   Options:")
        print("   1. Use US stocks only (switch to us_sectors_test.json)")
        print("   2. Upgrade to Alpha Vantage paid plan")
        print("   3. Find alternative data source for ASX stocks")

print("\n" + "="*80)
