#!/usr/bin/env python3
"""
Quick Yahoo Finance Block Test

Tests if your IP is currently blocked by Yahoo Finance.
Takes ~10 seconds to run.

Usage:
    python test_yahoo_blocking.py
"""

import sys
import time
from datetime import datetime

def test_yahoo_blocking():
    """Test if Yahoo Finance is blocking your requests"""
    
    print("="*70)
    print("Yahoo Finance Block Test".center(70))
    print("="*70)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Import yfinance
    print("Test 1: Importing yfinance...")
    try:
        import yfinance as yf
        print("  ✓ yfinance imported successfully")
        version = getattr(yf, '__version__', 'unknown')
        print(f"  Version: {version}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    # Test 2: Simple ticker fetch
    print("\nTest 2: Fetching CBA.AX (ASX stock)...")
    try:
        start = time.time()
        ticker = yf.Ticker('CBA.AX')
        info = ticker.fast_info
        elapsed = time.time() - start
        
        if hasattr(info, 'last_price') and info.last_price:
            print(f"  ✓ SUCCESS - Got price: ${info.last_price:.2f}")
            print(f"  Response time: {elapsed:.2f}s")
        else:
            print("  ✗ BLOCKED - No price data returned")
            print("  Yahoo Finance is likely blocking your requests")
            return False
            
    except Exception as e:
        error_str = str(e).lower()
        if 'expecting value' in error_str or 'json' in error_str:
            print(f"  ✗ BLOCKED - JSONDecodeError")
            print(f"  Error: {str(e)[:100]}")
            print("\n  This is the classic Yahoo Finance blocking error.")
            return False
        else:
            print(f"  ✗ ERROR: {str(e)[:100]}")
            return False
    
    # Test 3: US index
    print("\nTest 3: Fetching ^GSPC (S&P 500)...")
    try:
        start = time.time()
        ticker = yf.Ticker('^GSPC')
        info = ticker.fast_info
        elapsed = time.time() - start
        
        if hasattr(info, 'last_price') and info.last_price:
            print(f"  ✓ SUCCESS - Got price: ${info.last_price:.2f}")
            print(f"  Response time: {elapsed:.2f}s")
        else:
            print("  ✗ BLOCKED - No price data returned")
            return False
            
    except Exception as e:
        error_str = str(e).lower()
        if 'expecting value' in error_str or 'json' in error_str:
            print(f"  ✗ BLOCKED - JSONDecodeError")
            print(f"  Error: {str(e)[:100]}")
            return False
        else:
            print(f"  ✗ ERROR: {str(e)[:100]}")
            return False
    
    # Test 4: Historical data
    print("\nTest 4: Fetching historical data for BHP.AX...")
    try:
        start = time.time()
        ticker = yf.Ticker('BHP.AX')
        hist = ticker.history(period='5d')
        elapsed = time.time() - start
        
        if not hist.empty and len(hist) > 0:
            print(f"  ✓ SUCCESS - Got {len(hist)} days of data")
            print(f"  Latest close: ${hist['Close'].iloc[-1]:.2f}")
            print(f"  Response time: {elapsed:.2f}s")
        else:
            print("  ✗ BLOCKED - No historical data returned")
            return False
            
    except Exception as e:
        error_str = str(e).lower()
        if 'expecting value' in error_str or 'json' in error_str:
            print(f"  ✗ BLOCKED - JSONDecodeError")
            print(f"  Error: {str(e)[:100]}")
            return False
        else:
            print(f"  ✗ ERROR: {str(e)[:100]}")
            return False
    
    return True


def main():
    """Main entry point"""
    
    result = test_yahoo_blocking()
    
    print("\n" + "="*70)
    if result:
        print("✅ RESULT: Yahoo Finance is WORKING".center(70))
        print("="*70)
        print("\nYour IP is NOT blocked. You can run the screener now.")
        print("\nNext step:")
        print("  cd C:\\Users\\david\\AOSS\\complete_deployment")
        print("  RUN_STOCK_SCREENER.bat")
    else:
        print("❌ RESULT: Yahoo Finance is BLOCKING you".center(70))
        print("="*70)
        print("\nYour IP is currently blocked by Yahoo Finance.")
        print("\nWhat to do:")
        print("  1. Wait 1-2 hours for the block to expire")
        print("  2. Don't run any more yfinance requests during this time")
        print("  3. Run this test again in 1 hour")
        print("  4. Once unblocked, run the screener")
        print("\nWhy this happened:")
        print("  - Too many requests in short time")
        print("  - Yahoo detected automated scraping pattern")
        print("  - Block is temporary (typically 1-2 hours)")
        print("\nTo check block status in 1 hour:")
        print("  python test_yahoo_blocking.py")
    
    print("\n" + "="*70)
    print()
    
    return 0 if result else 1


if __name__ == '__main__':
    sys.exit(main())
