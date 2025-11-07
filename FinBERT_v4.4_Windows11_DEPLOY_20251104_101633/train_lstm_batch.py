#!/usr/bin/env python3
"""
Batch LSTM Training Script for Top Stocks
Trains LSTM models overnight for most-traded stocks
Expected time: 1-2 hours total (10-15 min per stock)
"""

import os
import sys
import yfinance as yf
from datetime import datetime
import logging

# Add models directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import LSTM predictor
try:
    from models.lstm_predictor import lstm_predictor
except ImportError as e:
    print(f"Error importing LSTM predictor: {e}")
    print("Make sure you're in the correct directory and models exist")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_lstm_for_stock(symbol):
    """
    Train and save LSTM model for a single stock
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'CBA.AX')
    
    Returns:
        bool: True if training successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"  Training LSTM for {symbol}")
    print(f"{'='*70}")
    
    try:
        # Download 2 years of data for better training
        print(f"📊 Downloading {symbol} data (2 years)...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='2y')
        
        if len(data) < 100:
            print(f"❌ {symbol}: Not enough data ({len(data)} days)")
            print(f"   Minimum required: 100 days")
            return False
        
        print(f"✓ Downloaded {len(data)} days of data")
        
        # Prepare data for LSTM
        print(f"🔧 Preparing data for training...")
        
        # Convert to format expected by LSTM predictor
        chart_data = []
        for idx, row in data.iterrows():
            chart_data.append({
                'timestamp': int(idx.timestamp()),
                'date': idx.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
        
        # Train LSTM
        print(f"🧠 Training LSTM (this may take 5-15 minutes)...")
        print(f"   Using last close price: ${data['Close'].iloc[-1]:.2f}")
        
        # Train the model
        result = lstm_predictor.train_model(
            chart_data=chart_data,
            symbol=symbol,
            epochs=50,  # More epochs for better accuracy
            sequence_length=60  # 60 days lookback
        )
        
        if 'error' in result:
            print(f"❌ {symbol}: Training failed - {result['error']}")
            return False
        
        # Save the model
        print(f"💾 Saving trained model...")
        save_result = lstm_predictor.save_model(symbol)
        
        if save_result:
            print(f"✅ {symbol}: Training COMPLETE!")
            print(f"   Loss: {result.get('final_loss', 'N/A')}")
            print(f"   Model saved to: models/lstm_{symbol}_model.keras")
            return True
        else:
            print(f"⚠️  {symbol}: Training succeeded but save failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ {symbol}: Training error - {str(e)}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False

def main():
    """
    Train LSTM models for top stocks
    Expected total time: 1-2 hours
    """
    
    print("="*70)
    print("  🚀 BATCH LSTM TRAINING FOR TOP STOCKS")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Top stocks to train
    us_stocks = [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('AMZN', 'Amazon.com Inc.'),
        ('META', 'Meta Platforms Inc.'),
        ('AMD', 'Advanced Micro Devices'),
    ]
    
    australian_stocks = [
        ('CBA.AX', 'Commonwealth Bank of Australia'),
        ('BHP.AX', 'BHP Group Limited'),
    ]
    
    all_stocks = us_stocks + australian_stocks
    
    print(f"📋 Will train LSTM for {len(all_stocks)} stocks:")
    print()
    for i, (symbol, name) in enumerate(all_stocks, 1):
        print(f"  {i:2d}. {symbol:8s} - {name}")
    print()
    
    print(f"⏱️  Estimated time: {len(all_stocks) * 10} minutes ({len(all_stocks) * 10 / 60:.1f} hours)")
    print()
    
    input("Press ENTER to start training (or Ctrl+C to cancel)...")
    print()
    
    # Train each stock
    results = {}
    start_time = datetime.now()
    
    for i, (symbol, name) in enumerate(all_stocks, 1):
        stock_start = datetime.now()
        print(f"\n[{i}/{len(all_stocks)}] Processing {symbol} ({name})...")
        
        success = train_lstm_for_stock(symbol)
        results[symbol] = success
        
        stock_duration = (datetime.now() - stock_start).total_seconds()
        print(f"   Time taken: {stock_duration:.1f} seconds ({stock_duration/60:.1f} minutes)")
        
        if i < len(all_stocks):
            remaining = len(all_stocks) - i
            avg_time = (datetime.now() - start_time).total_seconds() / i
            eta_seconds = remaining * avg_time
            print(f"   ETA for remaining {remaining} stocks: {eta_seconds/60:.1f} minutes")
    
    # Summary
    total_duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("  📊 TRAINING SUMMARY")
    print("="*70)
    
    successful = [s for s, success in results.items() if success]
    failed = [s for s, success in results.items() if not success]
    
    print(f"\n✅ Successfully trained: {len(successful)}/{len(all_stocks)}")
    for symbol in successful:
        name = next((n for s, n in all_stocks if s == symbol), "")
        print(f"  ✓ {symbol:8s} - {name}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(all_stocks)}")
        for symbol in failed:
            name = next((n for s, n in all_stocks if s == symbol), "")
            print(f"  ✗ {symbol:8s} - {name}")
    
    print(f"\n⏱️  Total time: {total_duration/60:.1f} minutes ({total_duration/3600:.1f} hours)")
    print(f"   Average per stock: {total_duration/len(all_stocks):.1f} seconds")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Success rate
    success_rate = len(successful) / len(all_stocks) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 Perfect! All models trained successfully!")
    elif success_rate >= 80:
        print("👍 Great! Most models trained successfully!")
    elif success_rate >= 50:
        print("⚠️  Some models failed. Check errors above.")
    else:
        print("❌ Many models failed. Review errors and try again.")
    
    print("\n💡 Next Steps:")
    print("   1. Restart the FinBERT server to load trained models")
    print("   2. Test predictions on trained stocks (should be more accurate)")
    print("   3. Monitor accuracy improvements over time")
    print()
    print("   To start server:")
    print("   python app_finbert_v4_dev.py")
    print()
    
    return len(successful) == len(all_stocks)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
