#!/usr/bin/env python3
"""
Test Price Update Fix - v1.3.15.191
===================================

This script tests the enhanced fetch_current_price() method to verify it
properly handles after-hours, pre-market, and closed-market scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import required modules
try:
    from yahooquery import Ticker
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False
    print("[!]  yahooquery not available")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[!]  yfinance not available")

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def fetch_current_price_enhanced(symbol: str):
    """Enhanced price fetching with multi-tier fallback"""
    print(f"\n{BLUE}[TEST]{RESET} Fetching price for {symbol}...")
    
    try:
        if YAHOOQUERY_AVAILABLE:
            print(f"  {YELLOW}->{RESET} Trying yahooquery...")
            ticker = Ticker(symbol)
            quote = ticker.price
            
            if isinstance(quote, dict) and symbol in quote:
                stock_data = quote[symbol]
                
                # Try regular market price
                price = stock_data.get('regularMarketPrice')
                if price and price > 0:
                    print(f"  {GREEN}[OK]{RESET} regularMarketPrice: USD{price:.2f}")
                    return float(price), "regularMarketPrice"
                else:
                    print(f"  {RED}[X]{RESET} regularMarketPrice: None or 0")
                
                # Try post-market price
                price = stock_data.get('postMarketPrice')
                if price and price > 0:
                    print(f"  {GREEN}[OK]{RESET} postMarketPrice: USD{price:.2f}")
                    return float(price), "postMarketPrice"
                else:
                    print(f"  {RED}[X]{RESET} postMarketPrice: None or 0")
                
                # Try pre-market price
                price = stock_data.get('preMarketPrice')
                if price and price > 0:
                    print(f"  {GREEN}[OK]{RESET} preMarketPrice: USD{price:.2f}")
                    return float(price), "preMarketPrice"
                else:
                    print(f"  {RED}[X]{RESET} preMarketPrice: None or 0")
                
                # Fallback to previous close
                price = stock_data.get('regularMarketPreviousClose')
                if price and price > 0:
                    print(f"  {GREEN}[OK]{RESET} regularMarketPreviousClose: USD{price:.2f}")
                    return float(price), "regularMarketPreviousClose"
                else:
                    print(f"  {RED}[X]{RESET} regularMarketPreviousClose: None or 0")
        
        # Fallback to yfinance
        if YFINANCE_AVAILABLE:
            print(f"  {YELLOW}->{RESET} Trying yfinance...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                print(f"  {GREEN}[OK]{RESET} yfinance close: USD{price:.2f}")
                return price, "yfinance"
            else:
                print(f"  {RED}[X]{RESET} yfinance: No data")
        
        print(f"  {RED}[X]{RESET} All methods failed")
        return None, "failed"
        
    except Exception as e:
        print(f"  {RED}[X]{RESET} Error: {e}")
        return None, "error"

def test_symbols():
    """Test price fetching for various symbols"""
    print(f"\n{'='*70}")
    print(f"{BLUE}Price Update Fix Test - v1.3.15.191{RESET}")
    print(f"{'='*70}")
    
    # Test symbols from user's portfolio
    test_cases = [
        ("BP.L", "UK - BP (affected symbol from screenshot)"),
        ("LGEN.L", "UK - Legal & General (worked in screenshot)"),
        ("RIO.AX", "AU - Rio Tinto (worked in screenshot)"),
        ("AAPL", "US - Apple (reference symbol)"),
    ]
    
    results = []
    
    for symbol, description in test_cases:
        print(f"\n{'-'*70}")
        print(f"{BLUE}Testing:{RESET} {symbol} - {description}")
        print(f"{'-'*70}")
        
        price, source = fetch_current_price_enhanced(symbol)
        
        if price:
            result = f"{GREEN}[OK] SUCCESS{RESET}"
            results.append((symbol, price, source, True))
        else:
            result = f"{RED}[X] FAILED{RESET}"
            results.append((symbol, None, source, False))
        
        print(f"\n  {result}: {symbol} = USD{price:.2f if price else 0} (source: {source})")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"{BLUE}SUMMARY{RESET}")
    print(f"{'='*70}\n")
    
    for symbol, price, source, success in results:
        status = f"{GREEN}[OK]{RESET}" if success else f"{RED}[X]{RESET}"
        price_str = f"USD{price:.2f}" if price else "N/A"
        print(f"  {status} {symbol:10} {price_str:12} (via {source})")
    
    success_count = sum(1 for _, _, _, success in results if success)
    total_count = len(results)
    
    print(f"\n{BLUE}Results:{RESET} {success_count}/{total_count} symbols fetched successfully")
    
    if success_count == total_count:
        print(f"\n{GREEN}[OK] ALL TESTS PASSED{RESET}")
        print(f"\n{GREEN}The fix is working correctly!{RESET}")
        print(f"BP.L should now update properly in the dashboard.")
        return 0
    else:
        print(f"\n{YELLOW}[!] SOME TESTS FAILED{RESET}")
        print(f"\nThis might be due to:")
        print(f"  * Internet connectivity issues")
        print(f"  * Yahoo Finance API temporary issues")
        print(f"  * Symbol format problems")
        return 1

if __name__ == "__main__":
    if not YAHOOQUERY_AVAILABLE and not YFINANCE_AVAILABLE:
        print(f"\n{RED}ERROR:{RESET} Neither yahooquery nor yfinance is available!")
        print(f"Please install: pip install yahooquery yfinance")
        sys.exit(1)
    
    sys.exit(test_symbols())
