#!/usr/bin/env python3
"""
Quick Test: Verify ticker.history() Only Fix
Tests that stock_scanner.py works without Yahoo Finance blocking
"""

import sys
import time
from models.screening.stock_scanner import StockScanner

def test_single_stock():
    """Test single stock validation and analysis"""
    print("="*70)
    print("Test 1: Single Stock (CBA.AX)".center(70))
    print("="*70)
    
    scanner = StockScanner()
    symbol = 'CBA.AX'
    
    # Test validation
    print(f"\n1. Validating {symbol}...")
    is_valid = scanner.validate_stock(symbol)
    print(f"   Result: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    if not is_valid:
        print("   ⚠️  Stock failed validation (price/volume criteria)")
        return False
    
    # Test analysis
    print(f"\n2. Analyzing {symbol}...")
    stock_data = scanner.analyze_stock(symbol, sector_weight=1.0)
    
    if stock_data:
        print(f"   ✓ SUCCESS")
        print(f"   Symbol: {stock_data['symbol']}")
        print(f"   Name: {stock_data['name']}")
        print(f"   Price: ${stock_data['price']:.2f}")
        print(f"   Volume: {stock_data['volume']:,}")
        print(f"   Score: {stock_data['score']:.1f}/100")
        print(f"   RSI: {stock_data['technical']['rsi']:.1f}")
        return True
    else:
        print(f"   ✗ FAILED - No data returned")
        return False

def test_small_batch():
    """Test small batch of stocks from Technology sector"""
    print("\n" + "="*70)
    print("Test 2: Small Batch (5 Technology Stocks)".center(70))
    print("="*70)
    
    scanner = StockScanner()
    
    print("\nScanning Technology sector (top 5)...")
    start_time = time.time()
    
    results = scanner.scan_sector('Technology', top_n=5)
    
    elapsed = time.time() - start_time
    
    print(f"\n✓ Scan completed in {elapsed:.1f} seconds")
    print(f"✓ Found {len(results)} valid stocks")
    
    if results:
        print("\nTop Stocks:")
        for i, stock in enumerate(results[:3], 1):
            print(f"  {i}. {stock['symbol']:8s} - Score: {stock['score']:5.1f} - Price: ${stock['price']:7.2f}")
    
    return len(results) > 0

def test_blocking_detection():
    """Test if Yahoo Finance blocking still occurs"""
    print("\n" + "="*70)
    print("Test 3: Blocking Detection (10 stocks)".center(70))
    print("="*70)
    
    scanner = StockScanner()
    test_symbols = ['CBA.AX', 'BHP.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX',
                   'CSL.AX', 'WOW.AX', 'MQG.AX', 'TLS.AX', 'RIO.AX']
    
    success_count = 0
    fail_count = 0
    
    print(f"\nTesting {len(test_symbols)} stocks...")
    
    for i, symbol in enumerate(test_symbols, 1):
        try:
            # Small delay between requests
            if i > 1:
                time.sleep(0.5)
            
            result = scanner.validate_stock(symbol)
            if result:
                success_count += 1
                print(f"  {i:2d}. {symbol:8s} ✓")
            else:
                fail_count += 1
                print(f"  {i:2d}. {symbol:8s} ✗ (validation criteria)")
        except Exception as e:
            error_str = str(e).lower()
            if 'expecting value' in error_str or 'json' in error_str:
                print(f"  {i:2d}. {symbol:8s} ✗ BLOCKED!")
                return False
            else:
                fail_count += 1
                print(f"  {i:2d}. {symbol:8s} ✗ ({str(e)[:30]})")
    
    print(f"\n✓ No blocking detected!")
    print(f"  Validated: {success_count}/{len(test_symbols)}")
    print(f"  Failed criteria: {fail_count}/{len(test_symbols)}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TICKER.HISTORY() ONLY FIX - VERIFICATION TEST".center(70))
    print("="*70)
    print("\nThis test verifies the fix eliminates Yahoo Finance blocking")
    print("by using ONLY ticker.history() (no .info calls)")
    
    results = []
    
    # Test 1: Single stock
    try:
        results.append(("Single Stock", test_single_stock()))
    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        results.append(("Single Stock", False))
    
    time.sleep(1)
    
    # Test 2: Small batch
    try:
        results.append(("Small Batch", test_small_batch()))
    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        results.append(("Small Batch", False))
    
    time.sleep(1)
    
    # Test 3: Blocking detection
    try:
        results.append(("Blocking Detection", test_blocking_detection()))
    except Exception as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        results.append(("Blocking Detection", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - FIX SUCCESSFUL".center(70))
        print("Yahoo Finance blocking eliminated!".center(70))
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW NEEDED".center(70))
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
