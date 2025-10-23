#!/usr/bin/env python3
"""
Test script to verify CBA.AX real market price from Yahoo Finance
"""

import yfinance as yf
import json
from datetime import datetime

def test_cba_price():
    """Test CBA.AX price fetching"""
    print("=" * 60)
    print("TESTING CBA.AX REAL MARKET PRICE")
    print("=" * 60)
    
    try:
        # Create ticker object
        ticker = yf.Ticker("CBA.AX")
        
        # Get info
        info = ticker.info
        
        print("\n1. TICKER INFO:")
        print("-" * 40)
        
        # Extract key price information
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose', 0)
        
        print(f"Symbol: {info.get('symbol', 'CBA.AX')}")
        print(f"Name: {info.get('longName', 'Commonwealth Bank of Australia')}")
        print(f"Current Price: ${current_price:.2f}")
        print(f"Previous Close: ${previous_close:.2f}")
        print(f"Day High: ${info.get('dayHigh', 0):.2f}")
        print(f"Day Low: ${info.get('dayLow', 0):.2f}")
        print(f"52 Week High: ${info.get('fiftyTwoWeekHigh', 0):.2f}")
        print(f"52 Week Low: ${info.get('fiftyTwoWeekLow', 0):.2f}")
        
        # Get historical data
        print("\n2. RECENT HISTORICAL DATA (Last 5 Days):")
        print("-" * 40)
        
        hist = ticker.history(period="5d")
        if not hist.empty:
            for date, row in hist.iterrows():
                print(f"{date.strftime('%Y-%m-%d')}: Close=${row['Close']:.2f}, Volume={row['Volume']:,}")
        
        # Get latest price from history if current price is 0
        if current_price == 0 and not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            print(f"\nUsing latest historical close as current price: ${current_price:.2f}")
        
        # Final assessment
        print("\n3. PRICE ASSESSMENT:")
        print("-" * 40)
        
        if current_price > 150:
            print(f"✅ CORRECT: CBA.AX price is ${current_price:.2f} (Expected ~$170)")
        elif current_price > 0 and current_price < 120:
            print(f"❌ ISSUE: CBA.AX price is ${current_price:.2f} (Should be ~$170)")
        else:
            print(f"⚠️ WARNING: Unable to get valid price. Returned: ${current_price:.2f}")
        
        # Test API endpoint format
        print("\n4. API RESPONSE FORMAT TEST:")
        print("-" * 40)
        
        api_response = {
            "symbol": "CBA.AX",
            "name": info.get('longName', 'Commonwealth Bank of Australia'),
            "price": round(current_price, 2) if current_price else 0,
            "change": round(current_price - previous_close, 2) if current_price and previous_close else 0,
            "changePercent": round(((current_price - previous_close) / previous_close) * 100, 2) if current_price and previous_close else 0,
            "volume": info.get('volume', 0),
            "marketCap": info.get('marketCap', 0),
            "dayHigh": info.get('dayHigh', 0),
            "dayLow": info.get('dayLow', 0),
            "yearHigh": info.get('fiftyTwoWeekHigh', 0),
            "yearLow": info.get('fiftyTwoWeekLow', 0),
            "pe_ratio": info.get('forwardPE', 0),
            "dividend_yield": info.get('dividendYield', 0),
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(api_response, indent=2))
        
    except Exception as e:
        print(f"ERROR: Failed to fetch CBA.AX data: {str(e)}")
        print("\nPossible reasons:")
        print("1. Network connection issue")
        print("2. Yahoo Finance API temporarily unavailable")
        print("3. Rate limiting")
        print("\nTry running the script again in a few moments.")

if __name__ == "__main__":
    test_cba_price()