#!/usr/bin/env python3
"""
UK Stock Price Fetching Debug Script
=====================================

This script specifically tests UK stock (.L suffix) price fetching
to diagnose why BP.L and LGEN.L are not updating.
"""

import sys
from datetime import datetime

try:
    from yahooquery import Ticker
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False
    print("ERROR: yahooquery not available")
    sys.exit(1)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

def test_uk_stock(symbol):
    """Test UK stock price fetching with detailed output"""
    print(f"\n{'='*70}")
    print(f"Testing: {symbol}")
    print(f"Time: {datetime.now()}")
    print(f"{'='*70}\n")
    
    # Test yahooquery
    print("[1] Testing yahooquery Ticker.price...")
    try:
        ticker = Ticker(symbol)
        quote = ticker.price
        
        print(f"   Raw response type: {type(quote)}")
        print(f"   Raw response: {quote}\n")
        
        if isinstance(quote, dict) and symbol in quote:
            stock_data = quote[symbol]
            print(f"   Stock data keys: {stock_data.keys()}\n")
            
            fields = [
                'regularMarketPrice',
                'postMarketPrice',
                'preMarketPrice',
                'regularMarketPreviousClose',
                'regularMarketOpen',
                'regularMarketDayHigh',
                'regularMarketDayLow',
                'regularMarketVolume',
                'marketState'
            ]
            
            print("   Available price fields:")
            for field in fields:
                value = stock_data.get(field, 'NOT FOUND')
                print(f"      {field:30} = {value}")
        else:
            print(f"   ERROR: Unexpected response format or symbol not in response")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test yfinance
    print(f"\n[2] Testing yfinance...")
    try:
        ticker = yf.Ticker(symbol)
        
        # Get info
        print("   Fetching ticker.info...")
        info = ticker.info
        print(f"   Info keys available: {len(info.keys() if info else 0)}")
        
        if info:
            price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose', 'open']
            print("\n   Price fields from info:")
            for field in price_fields:
                value = info.get(field, 'NOT FOUND')
                print(f"      {field:25} = {value}")
        
        # Get history
        print("\n   Fetching ticker.history(period='1d')...")
        hist = ticker.history(period="1d")
        print(f"   History shape: {hist.shape if not hist.empty else 'EMPTY'}")
        
        if not hist.empty:
            print(f"\n   Last row:")
            last_row = hist.iloc[-1]
            print(f"      Open:   ${last_row['Open']:.2f}")
            print(f"      High:   ${last_row['High']:.2f}")
            print(f"      Low:    ${last_row['Low']:.2f}")
            print(f"      Close:  ${last_row['Close']:.2f}")
            print(f"      Volume: {last_row['Volume']:,}")
        
        # Get 5-day history
        print("\n   Fetching ticker.history(period='5d')...")
        hist_5d = ticker.history(period="5d")
        print(f"   5-day history shape: {hist_5d.shape if not hist_5d.empty else 'EMPTY'}")
        
        if not hist_5d.empty:
            print(f"   Latest 3 closes:")
            for i in range(min(3, len(hist_5d))):
                row = hist_5d.iloc[-(i+1)]
                date = row.name.strftime('%Y-%m-%d')
                print(f"      {date}: ${row['Close']:.2f}")
                
    except Exception as e:
        print(f"   ERROR: {e}")

def main():
    """Test UK stocks that are frozen in the dashboard"""
    print(f"\n{'#'*70}")
    print("UK STOCK PRICE FETCHING DEBUG")
    print("Testing BP.L and LGEN.L (frozen in dashboard)")
    print(f"{'#'*70}")
    
    test_symbols = [
        ('BP.L', 'BP - British Petroleum'),
        ('LGEN.L', 'Legal & General'),
    ]
    
    for symbol, name in test_symbols:
        test_uk_stock(symbol)
    
    print(f"\n{'#'*70}")
    print("SUMMARY")
    print(f"{'#'*70}")
    print("""
Expected findings:
- If regularMarketPrice is None → Market closed, need fallback
- If regularMarketPreviousClose exists → Should use that
- If yfinance history has data → Should use that
- If ALL methods fail → API issue or symbol format problem

Next steps based on findings:
1. If regularMarketPreviousClose is available → Fix is correct
2. If all fields are None → Symbol format issue
3. If API returns error → Yahoo Finance API problem
4. If data exists but not used → Logic bug in update_positions()
    """)

if __name__ == "__main__":
    main()
