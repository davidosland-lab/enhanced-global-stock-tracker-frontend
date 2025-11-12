#!/usr/bin/env python3
"""
Test yfinance with ASX stocks to confirm fixes work
"""

import sys
sys.path.insert(0, '/home/user/webapp/complete_deployment')

from models.screening.stock_scanner import StockScanner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*80)
print("Testing yfinance with ASX stocks")
print("="*80)

# Create scanner (will use yfinance fallback since Alpha Vantage doesn't support ASX)
scanner = StockScanner(use_batch_fetching=False, use_yfinance_fallback=True)

test_tickers = ['CBA', 'BHP', 'NAB', 'WBC', 'ANZ']

print("\n" + "="*80)
print("TEST 1: Ticker suffix validation")
print("="*80)
for ticker in test_tickers:
    yf_symbol = scanner._ensure_yf_symbol(ticker)
    print(f"  {ticker:6s} -> {yf_symbol}")

print("\n" + "="*80)
print("TEST 2: Fast info retrieval (no .info calls)")
print("="*80)
for ticker in test_tickers[:2]:  # Test first 2
    print(f"\nTesting {ticker}...")
    info = scanner._safe_fast_info(ticker)
    print(f"  Name: {info['longName']}")
    print(f"  Price: ${info.get('currentPrice', 'N/A')}")
    print(f"  Market Cap: ${info.get('marketCap', 0):,.0f}")
    print(f"  Avg Volume: {info.get('averageVolume', 0):,.0f}")

print("\n" + "="*80)
print("TEST 3: Stock validation (price-based, no .info)")
print("="*80)
for ticker in test_tickers[:3]:  # Test first 3
    print(f"\nValidating {ticker}...")
    is_valid = scanner.validate_stock(ticker)
    print(f"  Result: {'✅ PASS' if is_valid else '❌ FAIL'}")

print("\n" + "="*80)
print("TEST 4: Full stock analysis")
print("="*80)
ticker = 'CBA'
print(f"\nAnalyzing {ticker}...")
stock_data = scanner.analyze_stock(ticker, sector_weight=1.0)
if stock_data:
    print(f"  ✅ SUCCESS")
    print(f"  Symbol: {stock_data['symbol']}")
    print(f"  Price: ${stock_data['price']:.2f}")
    print(f"  Score: {stock_data['score']:.1f}")
    print(f"  RSI: {stock_data['technical']['rsi']:.1f}")
    print(f"  MA20: ${stock_data['technical']['ma_20']:.2f}")
    print(f"  MA50: ${stock_data['technical']['ma_50']:.2f}")
else:
    print(f"  ❌ FAILED")

print("\n" + "="*80)
print("ALL TESTS COMPLETE")
print("="*80)
