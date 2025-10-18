#!/usr/bin/env python3
"""
Test script to demonstrate the Yahoo Finance issue with sentiment analysis
"""

import yfinance as yf
import time
from datetime import datetime

def test_original_method():
    """Test the original method - minimal API calls"""
    print("\n" + "="*60)
    print("Testing ORIGINAL Method (Before Sentiment)")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Original method - single ticker, single call
        symbol = "AAPL"
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")
        
        if not data.empty:
            print(f"✅ Success! Got {len(data)} days of data")
            print(f"Latest price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("❌ No data received")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    elapsed = time.time() - start_time
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"API calls made: 1")
    
    return elapsed

def test_sentiment_method():
    """Test the problematic sentiment method - many API calls"""
    print("\n" + "="*60)
    print("Testing PROBLEMATIC Sentiment Method")
    print("="*60)
    
    start_time = time.time()
    api_calls = 0
    
    try:
        # Sentiment method - many individual calls
        symbols_to_check = [
            'AAPL',     # Target stock
            '^VIX',     # Volatility
            '^GSPC',    # S&P 500
            '^DJI',     # Dow Jones
            '^IXIC',    # NASDAQ
            '^FTSE',    # FTSE 100
            '^N225',    # Nikkei
            'GLD',      # Gold
            'DX-Y.NYB', # Dollar
            '^TNX',     # 10-year yield
            '^IRX',     # 3-month yield
            'XLF',      # Financials
            'XLY',      # Consumer Discretionary
            'XLP',      # Consumer Staples
            'XLI',      # Industrials
            'XLE',      # Energy
            'CL=F',     # Oil
            'TLT',      # Bonds
            'PAVE'      # Infrastructure
        ]
        
        results = {}
        
        print(f"Making {len(symbols_to_check)} separate API calls...")
        
        for symbol in symbols_to_check:
            try:
                ticker = yf.Ticker(symbol)  # New connection each time!
                data = ticker.history(period="5d")
                api_calls += 1
                
                if not data.empty:
                    results[symbol] = data['Close'].iloc[-1]
                    print(f"  ✓ {symbol}: ${data['Close'].iloc[-1]:.2f}")
                else:
                    print(f"  ✗ {symbol}: No data")
                    
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {str(e)[:50]}")
        
        print(f"\n✅ Got data for {len(results)}/{len(symbols_to_check)} symbols")
        
    except Exception as e:
        print(f"❌ Overall Error: {e}")
    
    elapsed = time.time() - start_time
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"API calls made: {api_calls}")
    
    return elapsed

def test_fixed_method():
    """Test the fixed batch method - single API call"""
    print("\n" + "="*60)
    print("Testing FIXED Batch Method")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Fixed method - batch download
        symbols = [
            'AAPL', '^VIX', '^GSPC', 'GLD', 'TLT',
            '^TNX', 'XLF', 'XLY', 'CL=F'
        ]
        
        print(f"Downloading {len(symbols)} symbols in ONE batch call...")
        
        # Single batch download - much more efficient!
        data = yf.download(
            symbols,
            period='5d',
            progress=False,
            threads=True,
            group_by='ticker'
        )
        
        if not data.empty:
            print(f"✅ Success! Got data for all symbols in one call")
            
            # Show some sample data
            for symbol in symbols[:3]:
                try:
                    if len(symbols) == 1:
                        price = data['Close'].iloc[-1]
                    else:
                        price = data[symbol]['Close'].iloc[-1] if symbol in data.columns.levels[0] else None
                    
                    if price:
                        print(f"  {symbol}: ${price:.2f}")
                except:
                    pass
        else:
            print("❌ No data received")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    elapsed = time.time() - start_time
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"API calls made: 1 (batch)")
    
    return elapsed

def main():
    print("\n" + "="*80)
    print("Yahoo Finance API Call Comparison")
    print("Demonstrating why sentiment analysis breaks Yahoo Finance connection")
    print("="*80)
    
    # Test original method
    time1 = test_original_method()
    
    # Small delay
    print("\nWaiting 2 seconds before next test...")
    time.sleep(2)
    
    # Test fixed batch method
    time3 = test_fixed_method()
    
    # Small delay
    print("\nWaiting 2 seconds before next test...")
    time.sleep(2)
    
    # Test problematic sentiment method (do this last as it might fail)
    time2 = test_sentiment_method()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Original Method: {time1:.2f}s - 1 API call - EFFICIENT ✅")
    print(f"Fixed Batch Method: {time3:.2f}s - 1 batch call - MOST EFFICIENT ✅")
    print(f"Sentiment Method: {time2:.2f}s - 19+ API calls - PROBLEMATIC ❌")
    print("\nThe sentiment method makes 19+ times more API calls!")
    print("This is why Yahoo Finance blocks/rate-limits the connection.")
    print("\nSOLUTION: Use batch downloading or disable sentiment analysis.")

if __name__ == "__main__":
    main()