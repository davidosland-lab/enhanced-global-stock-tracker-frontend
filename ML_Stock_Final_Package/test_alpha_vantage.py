#!/usr/bin/env python3
"""
Test Alpha Vantage Connection
Tests your API key and data fetching
"""

from config import ALPHA_VANTAGE_API_KEY
from alpha_vantage_fetcher import AlphaVantageDataFetcher, AlphaVantageMLDataFetcher
import time

print("="*60)
print("ALPHA VANTAGE CONNECTION TEST")
print("="*60)

print(f"\n✅ API Key loaded: {ALPHA_VANTAGE_API_KEY[:8]}...")
print("\nNote: Free tier limits:")
print("  • 5 API requests per minute")
print("  • 500 requests per day")

# Test 1: Basic connection with quote
print("\n" + "-"*40)
print("Test 1: Getting current quote for AAPL")
print("-"*40)

try:
    fetcher = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
    quote = fetcher.get_quote_endpoint("AAPL")
    
    print(f"✅ SUCCESS!")
    print(f"   Symbol: {quote['symbol']}")
    print(f"   Price: ${quote['price']:.2f}")
    print(f"   Change: {quote['change_percent']}")
    print(f"   Volume: {quote['volume']:,}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Wait for rate limit
print("\n⏳ Waiting 12 seconds for rate limit...")
time.sleep(12)

# Test 2: Historical data
print("\n" + "-"*40)
print("Test 2: Getting 1 month of historical data")
print("-"*40)

try:
    ml_fetcher = AlphaVantageMLDataFetcher(ALPHA_VANTAGE_API_KEY)
    data = ml_fetcher.fetch_stock_data("AAPL", period="1mo")
    
    print(f"✅ SUCCESS!")
    print(f"   Records: {len(data)} days")
    print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 3: Check Australian stock conversion
print("\n⏳ Waiting 12 seconds for rate limit...")
time.sleep(12)

print("\n" + "-"*40)
print("Test 3: Testing Australian stock (CBA.AX)")
print("-"*40)

try:
    # Note: Alpha Vantage uses .AUS for Australian stocks
    quote = fetcher.get_quote_endpoint("CBA.AX")  # Will auto-convert to CBA.AUS
    
    print(f"✅ SUCCESS!")
    print(f"   Symbol: CBA.AX (converted to CBA.AUS)")
    print(f"   Price: ${quote['price']:.2f}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("   Note: Some international stocks may not be available")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

print("\n📊 To use Alpha Vantage as primary source:")
print("   python start_server.py --alpha")
print("\n🔄 To use both Yahoo and Alpha Vantage:")
print("   python start_server.py --multi")