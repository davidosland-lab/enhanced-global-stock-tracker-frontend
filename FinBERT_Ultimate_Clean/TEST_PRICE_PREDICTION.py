#!/usr/bin/env python3
"""
Test Price Prediction Feature
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_price_estimation(symbol="AAPL"):
    """Test price estimation logic"""
    
    print(f"\n{'='*60}")
    print(f"Testing Price Estimation for {symbol}")
    print('='*60)
    
    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="3mo")
    
    if df.empty:
        print("No data available")
        return
    
    current_price = float(df['Close'].iloc[-1])
    print(f"\nCurrent Price: ${current_price:.2f}")
    
    # Calculate volatility
    returns = df['Close'].pct_change().dropna()
    volatility = returns.tail(20).std() if len(returns) >= 20 else returns.std()
    print(f"20-day Volatility: {volatility*100:.2f}%")
    
    # Calculate ATR
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.tail(14).mean() if len(true_range) >= 14 else true_range.mean()
    atr_percent = (atr / current_price) * 100
    print(f"14-day ATR: ${atr:.2f} ({atr_percent:.2f}%)")
    
    # Simulate different confidence levels
    print("\n" + "-"*60)
    print("Price Targets at Different Confidence Levels:")
    print("-"*60)
    
    for confidence in [0.55, 0.65, 0.75, 0.85]:
        # Calculate price movement
        base_movement = (volatility * 2 + atr_percent / 100) / 2
        confidence_multiplier = 0.5 + (confidence * 0.5)
        price_movement_percent = base_movement * confidence_multiplier * 100
        
        # UP prediction
        up_target = current_price * (1 + price_movement_percent / 100)
        up_range_low = current_price * (1 + price_movement_percent * 0.3 / 100)
        up_range_high = current_price * (1 + price_movement_percent * 1.5 / 100)
        
        # DOWN prediction
        down_target = current_price * (1 - price_movement_percent / 100)
        down_range_high = current_price * (1 - price_movement_percent * 0.3 / 100)
        down_range_low = current_price * (1 - price_movement_percent * 1.5 / 100)
        
        # Timeframe
        if volatility > 0.03:
            timeframe = "3-5 trading days"
        elif volatility > 0.02:
            timeframe = "1-2 weeks"
        elif volatility > 0.01:
            timeframe = "2-4 weeks"
        else:
            timeframe = "1-2 months"
        
        print(f"\n{confidence*100:.0f}% Confidence:")
        print(f"  📈 UP Target: ${up_target:.2f} (+{price_movement_percent:.1f}%)")
        print(f"     Range: ${up_range_low:.2f} - ${up_range_high:.2f}")
        print(f"  📉 DOWN Target: ${down_target:.2f} (-{price_movement_percent:.1f}%)")
        print(f"     Range: ${down_range_low:.2f} - ${down_range_high:.2f}")
        print(f"  ⏱️  Timeframe: {timeframe}")
    
    print("\n" + "="*60)
    print("Note: These are estimates based on volatility and confidence")
    print("Actual results will vary based on market conditions")
    print("="*60)

# Test with different symbols
test_symbols = ["AAPL", "TSLA", "SPY"]

for symbol in test_symbols:
    try:
        test_price_estimation(symbol)
    except Exception as e:
        print(f"Error testing {symbol}: {e}")

print("\nPress Enter to exit...")
input()