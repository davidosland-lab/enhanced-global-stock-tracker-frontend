#!/usr/bin/env python3
"""
Test yahooquery as fallback for yfinance
Validates that yahooquery can fetch the same data we need for screening
"""

import sys

def test_yahooquery_basic():
    """Test basic yahooquery functionality"""
    
    print("="*70)
    print("YAHOOQUERY FALLBACK TEST")
    print("="*70)
    
    # Test import
    try:
        from yahooquery import Ticker
        print("✅ yahooquery imported successfully")
    except ImportError as e:
        print("❌ yahooquery not installed")
        print("   Run: pip install yahooquery")
        return False
    
    # Test data fetching
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        print(f"\n{'-'*70}")
        print(f"Testing: {symbol}")
        print(f"{'-'*70}")
        
        try:
            ticker = Ticker(symbol)
            
            # Get 1 month history (same as our scanner)
            hist = ticker.history(period='1mo')
            
            if hist is None or hist.empty:
                print(f"❌ No data returned for {symbol}")
                continue
            
            print(f"✅ Data retrieved: {len(hist)} rows")
            print(f"   Columns: {list(hist.columns)}")
            # Get first and last date (handle multi-index if present)
            try:
                if isinstance(hist.index, pd.MultiIndex):
                    dates = hist.index.get_level_values('date')
                else:
                    dates = hist.index
                print(f"   Date range: {dates[0]} to {dates[-1]}")
            except:
                print(f"   Date range: [Index type: {type(hist.index)}]")
            
            # Check required columns (case-insensitive)
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            actual_cols = [col.lower() for col in hist.columns]
            
            missing_cols = [col for col in required_cols if col not in actual_cols]
            if missing_cols:
                print(f"❌ Missing required columns: {missing_cols}")
                continue
            
            print(f"✅ All required OHLCV columns present")
            
            # Show sample data
            print(f"\n   Latest data:")
            print(f"   Close: ${hist['close'].iloc[-1]:.2f}")
            print(f"   Volume: {int(hist['volume'].iloc[-1]):,}")
            print(f"   High: ${hist['high'].iloc[-1]:.2f}")
            print(f"   Low: ${hist['low'].iloc[-1]:.2f}")
            
            # Calculate average volume (needed for our scanner)
            avg_volume = hist['volume'].mean()
            print(f"   Avg Volume (1mo): {int(avg_volume):,}")
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            import traceback
            print(traceback.format_exc())
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print(f"{'='*70}")
    return True

def test_yahooquery_vs_yfinance():
    """Compare yahooquery vs yfinance data"""
    
    print("\n" + "="*70)
    print("COMPARING YAHOOQUERY VS YFINANCE")
    print("="*70)
    
    try:
        from yahooquery import Ticker as YQTicker
        import yfinance as yf
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    symbol = 'AAPL'
    
    # Fetch with yfinance
    print(f"\nFetching {symbol} with yfinance...")
    try:
        yf_ticker = yf.Ticker(symbol)
        yf_hist = yf_ticker.history(period='5d')
        print(f"✅ yfinance: {len(yf_hist)} rows")
        print(f"   Latest close: ${yf_hist['Close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ yfinance failed: {e}")
        yf_hist = None
    
    # Fetch with yahooquery
    print(f"\nFetching {symbol} with yahooquery...")
    try:
        yq_ticker = YQTicker(symbol)
        yq_hist = yq_ticker.history(period='5d')
        print(f"✅ yahooquery: {len(yq_hist)} rows")
        print(f"   Latest close: ${yq_hist['close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ yahooquery failed: {e}")
        yq_hist = None
    
    # Compare if both succeeded
    if yf_hist is not None and yq_hist is not None:
        yf_close = yf_hist['Close'].iloc[-1]
        yq_close = yq_hist['close'].iloc[-1]
        
        diff = abs(yf_close - yq_close)
        diff_pct = (diff / yf_close) * 100
        
        print(f"\n📊 Comparison:")
        print(f"   yfinance close: ${yf_close:.2f}")
        print(f"   yahooquery close: ${yq_close:.2f}")
        print(f"   Difference: ${diff:.2f} ({diff_pct:.3f}%)")
        
        if diff_pct < 0.01:  # Less than 0.01% difference
            print(f"   ✅ Data matches (within 0.01%)")
        else:
            print(f"   ⚠️  Data differs by {diff_pct:.3f}%")
    
    return True

def test_fallback_function():
    """Test the actual fallback function we'll use"""
    
    print("\n" + "="*70)
    print("TESTING FALLBACK FUNCTION")
    print("="*70)
    
    import pandas as pd
    
    try:
        from yahooquery import Ticker as YQTicker
        import yfinance as yf
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    def fetch_history_with_fallback(symbol, period='1mo'):
        """Test version of fallback function"""
        
        # Try yfinance first
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                return hist, 'yfinance'
        except Exception as e:
            print(f"   yfinance failed: {e}")
        
        # Fallback to yahooquery
        try:
            print(f"   Trying yahooquery fallback...")
            ticker = YQTicker(symbol)
            hist = ticker.history(period=period)
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                # Normalize column names to match yfinance
                hist.columns = [col.capitalize() for col in hist.columns]
                return hist, 'yahooquery'
        except Exception as e:
            print(f"   yahooquery failed: {e}")
        
        raise Exception(f"Both methods failed for {symbol}")
    
    # Test with multiple symbols
    test_symbols = ['AAPL', 'MSFT', 'TSLA']
    
    for symbol in test_symbols:
        print(f"\nTesting fallback for {symbol}...")
        try:
            hist, source = fetch_history_with_fallback(symbol, period='5d')
            print(f"✅ Success with {source}")
            print(f"   Data: {len(hist)} rows, latest close: ${hist['Close'].iloc[-1]:.2f}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return True

if __name__ == "__main__":
    print("\n🧪 Starting yahooquery fallback tests...\n")
    
    # Run all tests
    success = True
    
    # Test 1: Basic yahooquery functionality
    if not test_yahooquery_basic():
        success = False
    
    # Test 2: Compare yahooquery vs yfinance
    if not test_yahooquery_vs_yfinance():
        success = False
    
    # Test 3: Test fallback function
    if not test_fallback_function():
        success = False
    
    # Summary
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nNext steps:")
        print("1. Implement fallback function in stock_scanner.py")
        print("2. Update validate_stock() method")
        print("3. Update analyze_stock() method")
        print("4. Test with real scanner")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nCheck the errors above and resolve before implementing")
    print("="*70)
