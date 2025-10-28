#!/usr/bin/env python3
"""
Test script to demonstrate the SMA_50 fix
Shows the difference between old (broken) and new (fixed) prediction data fetching
"""

import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

def test_old_method(symbol="CBA.AX"):
    """Simulates the OLD broken method - only fetches 1 month"""
    print("\n" + "="*60)
    print("🔴 OLD METHOD (BROKEN) - Fetches only 1 month for prediction")
    print("="*60)
    
    # Old method: only fetch 1 month
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1mo")
    
    print(f"\nSymbol: {symbol}")
    print(f"Data fetched: 1 month")
    print(f"Data points available: {len(df)}")
    
    if len(df) >= 50:
        print("✅ Can calculate SMA_50: YES")
        sma_50 = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        print(f"   SMA_50 last value: {sma_50.iloc[-1]:.2f}")
    else:
        print(f"❌ Can calculate SMA_50: NO (need 50 days, have {len(df)})")
        print("   ERROR: This causes 'SMA_50 not in index' error!")
    
    return df

def test_new_method(symbol="CBA.AX"):
    """Simulates the NEW fixed method - fetches sufficient data"""
    print("\n" + "="*60)
    print("🟢 NEW METHOD (FIXED) - Fetches sufficient data for all features")
    print("="*60)
    
    # New method: determine required data based on features
    required_days = 50  # For SMA_50
    
    # Calculate appropriate period
    if required_days <= 30:
        period = "1mo"
    elif required_days <= 90:
        period = "3mo"
    elif required_days <= 180:
        period = "6mo"
    else:
        period = "1y"
    
    print(f"\nSymbol: {symbol}")
    print(f"Required days for SMA_50: {required_days}")
    print(f"Fetching period: {period}")
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    
    print(f"Data points available: {len(df)}")
    
    # If still not enough, try longer period
    if len(df) < required_days:
        print(f"⚠️  Not enough data with {period}, trying 6mo...")
        df = ticker.history(period="6mo")
        print(f"   Data points after retry: {len(df)}")
    
    if len(df) >= 50:
        print("✅ Can calculate SMA_50: YES")
        sma_50 = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        if not sma_50.empty and not sma_50.isna().iloc[-1]:
            print(f"   SMA_50 last value: {sma_50.iloc[-1]:.2f}")
        else:
            print("   SMA_50 calculated but has NaN values initially")
    else:
        print(f"⚠️  Still not enough data for SMA_50 (have {len(df)} days)")
        print("   Will use adaptive features instead")
    
    return df

def demonstrate_training_vs_prediction(symbol="CBA.AX"):
    """Show why training works but prediction fails"""
    print("\n" + "="*60)
    print("📊 TRAINING vs PREDICTION DATA COMPARISON")
    print("="*60)
    
    ticker = yf.Ticker(symbol)
    
    # Training typically uses 6 months or more
    print(f"\n📚 TRAINING PHASE:")
    train_df = ticker.history(period="6mo")
    print(f"   Period: 6 months")
    print(f"   Data points: {len(train_df)}")
    print(f"   Can calculate SMA_50: {'YES' if len(train_df) >= 50 else 'NO'}")
    
    # Old prediction only used 1 month
    print(f"\n🔮 PREDICTION PHASE (OLD):")
    pred_df_old = ticker.history(period="1mo")
    print(f"   Period: 1 month")
    print(f"   Data points: {len(pred_df_old)}")
    print(f"   Can calculate SMA_50: {'YES' if len(pred_df_old) >= 50 else 'NO'}")
    
    # New prediction uses sufficient data
    print(f"\n🔮 PREDICTION PHASE (FIXED):")
    pred_df_new = ticker.history(period="3mo")
    print(f"   Period: 3 months")
    print(f"   Data points: {len(pred_df_new)}")
    print(f"   Can calculate SMA_50: {'YES' if len(pred_df_new) >= 50 else 'NO'}")
    
    print("\n" + "="*60)
    print("💡 KEY INSIGHT:")
    print("="*60)
    print("The model was trained with SMA_50 as a feature (using 6 months of data)")
    print("But prediction only fetched 1 month, couldn't calculate SMA_50")
    print("SOLUTION: Prediction must fetch at least as much data as needed for all features!")

def test_multiple_symbols():
    """Test with various symbols to show the fix works universally"""
    print("\n" + "="*60)
    print("🌍 TESTING MULTIPLE SYMBOLS")
    print("="*60)
    
    symbols = [
        ("AAPL", "Apple - US Stock"),
        ("CBA.AX", "Commonwealth Bank - Australian Stock"),
        ("BTC-USD", "Bitcoin - Cryptocurrency"),
        ("^GSPC", "S&P 500 - Index"),
    ]
    
    for symbol, description in symbols:
        print(f"\n📈 {description}")
        print(f"   Symbol: {symbol}")
        
        try:
            # Test with new method
            ticker = yf.Ticker(symbol)
            
            # Old method (1 month)
            df_old = ticker.history(period="1mo")
            old_can_sma = len(df_old) >= 50
            
            # New method (3 months)
            df_new = ticker.history(period="3mo")
            new_can_sma = len(df_new) >= 50
            
            print(f"   OLD (1mo): {len(df_old)} days - SMA_50: {'✅' if old_can_sma else '❌'}")
            print(f"   NEW (3mo): {len(df_new)} days - SMA_50: {'✅' if new_can_sma else '❌'}")
            
            if not old_can_sma and new_can_sma:
                print(f"   🎉 FIX SUCCESSFUL - Now can calculate SMA_50!")
            
        except Exception as e:
            print(f"   ⚠️ Error testing {symbol}: {e}")

def main():
    """Run all tests"""
    print("\n" + "🔬"*30)
    print("  SMA_50 PREDICTION FIX - DEMONSTRATION")
    print("🔬"*30)
    
    # Test with CBA.AX (the user's problematic symbol)
    symbol = "CBA.AX"
    
    print(f"\nTesting with {symbol} (user's reported issue)")
    
    # Show old broken method
    old_df = test_old_method(symbol)
    
    # Show new fixed method
    new_df = test_new_method(symbol)
    
    # Demonstrate why the issue occurs
    demonstrate_training_vs_prediction(symbol)
    
    # Test with multiple symbols
    test_multiple_symbols()
    
    # Final summary
    print("\n" + "="*60)
    print("📋 SUMMARY OF THE FIX")
    print("="*60)
    print("""
The SMA_50 error was caused by a mismatch between training and prediction:

1. TRAINING: Used 6 months of data → Had enough for SMA_50 ✅
2. PREDICTION: Only fetched 1 month → Not enough for SMA_50 ❌

THE FIX:
- Prediction now fetches at least 3 months of data
- Dynamically calculates required period based on features
- Falls back to longer periods if needed
- Uses adaptive features if data still insufficient

This fix is implemented in app_finbert_ultimate.py
""")
    print("="*60)

if __name__ == "__main__":
    main()