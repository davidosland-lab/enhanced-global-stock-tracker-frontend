#!/usr/bin/env python3
"""
Verify that the Yahoo Finance fix is working
"""

import sys
import time

def check_sentiment_status():
    """Check if sentiment is enabled or disabled"""
    try:
        from ml_config import USE_SENTIMENT_ANALYSIS
        return USE_SENTIMENT_ANALYSIS
    except:
        return None

def test_yahoo_connection():
    """Test Yahoo Finance with minimal calls"""
    print("Testing Yahoo Finance connection...")
    try:
        import yfinance as yf
        
        # Single test call
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="5d")
        
        if not data.empty:
            latest_price = data['Close'].iloc[-1]
            print(f"✅ Yahoo Finance working! AAPL: ${latest_price:.2f}")
            return True
        else:
            print("❌ No data received from Yahoo Finance")
            return False
    except Exception as e:
        print(f"❌ Yahoo Finance error: {e}")
        return False

def verify_system():
    """Main verification"""
    print("="*60)
    print("ML Stock Prediction System - Fix Verification")
    print("="*60)
    print()
    
    # Check sentiment status
    sentiment_enabled = check_sentiment_status()
    if sentiment_enabled is None:
        print("⚠️  Could not determine sentiment status")
    elif sentiment_enabled:
        print("⚠️  WARNING: Sentiment is ENABLED")
        print("   This may cause Yahoo Finance issues!")
        print("   Run: python toggle_sentiment.py off")
    else:
        print("✅ Sentiment is DISABLED (Safe mode)")
        print("   System will use 35 technical features")
    
    print()
    
    # Test Yahoo
    if test_yahoo_connection():
        print()
        print("✅ System is ready to use!")
        print("   Run 3_START.bat to begin")
    else:
        print()
        print("⚠️  Yahoo Finance may have issues")
        print("   Try again in a few minutes")
    
    print()
    print("="*60)

if __name__ == "__main__":
    verify_system()
    input("\nPress Enter to exit...")