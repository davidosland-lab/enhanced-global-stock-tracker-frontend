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

# Import LSTM training function
try:
    from models.train_lstm import train_model_for_symbol
except ImportError as e:
    print(f"Error importing LSTM training module: {e}")
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
        print(f"   Using last close price: ${data['Close'].iloc[-1]:.2f}")
        
        # Train LSTM using the train_model_for_symbol function
        print(f"🧠 Training LSTM (this may take 5-15 minutes)...")
        print(f"   Epochs: 50, Sequence Length: 60")
        
        # Train the model (this includes data preparation and model saving)
        result = train_model_for_symbol(
            symbol=symbol,
            epochs=50,  # More epochs for better accuracy
            sequence_length=60  # 60 days lookback
        )
        
        if 'error' in result:
            print(f"❌ {symbol}: Training failed - {result['error']}")
            return False
        
        # Training successful
        print(f"✅ {symbol}: Training COMPLETE!")
        
        if 'training_results' in result:
            train_res = result['training_results']
            final_loss = train_res.get('final_loss', 'N/A')
            final_val_loss = train_res.get('final_val_loss', 'N/A')
            
            if isinstance(final_loss, (int, float)):
                print(f"   Final Loss: {final_loss:.4f}")
            else:
                print(f"   Final Loss: {final_loss}")
                
            if isinstance(final_val_loss, (int, float)):
                print(f"   Final Val Loss: {final_val_loss:.4f}")
            else:
                print(f"   Final Val Loss: {final_val_loss}")
        
        print(f"   Model saved to: models/lstm_{symbol}_model.keras")
        print(f"   Metadata saved to: {result.get('metadata_path', 'N/A')}")
        return True
        
    except Exception as e:
        logger.error(f"❌ {symbol}: Training error - {str(e)}")
        import traceback
        print(f"   Error details: {traceback.format_exc()}")
        return False

def main():
    """
    Train LSTM models for top stocks
    Expected total time: 1-2 hours
    
    TIP: For custom stock selection, use train_lstm_custom.py instead
    """
    
    print("="*70)
    print("  🚀 BATCH LSTM TRAINING FOR ASX STOCKS")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("ℹ️  Training ASX stocks (Event Risk Guard focus)")
    print("   Prioritizing stocks from event_calendar.csv")
    print("   For custom stock selection, use: train_lstm_custom.py")
    print()
    
    # Top ASX stocks to train (aligned with Event Risk Guard focus)
    # Prioritizing stocks from event_calendar.csv (Basel III, earnings, dividends)
    australian_stocks = [
        ('CBA.AX', 'Commonwealth Bank of Australia'),
        ('ANZ.AX', 'Australia and New Zealand Banking Group'),
        ('NAB.AX', 'National Australia Bank'),
        ('WBC.AX', 'Westpac Banking Corporation'),
        ('MQG.AX', 'Macquarie Group Limited'),
        ('BHP.AX', 'BHP Group Limited'),
        ('RIO.AX', 'Rio Tinto Limited'),
        ('CSL.AX', 'CSL Limited'),
        ('WES.AX', 'Wesfarmers Limited'),
        ('BOQ.AX', 'Bank of Queensland Limited'),
    ]
    
    all_stocks = australian_stocks
    
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
