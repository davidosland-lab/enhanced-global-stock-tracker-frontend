#!/usr/bin/env python3
"""
Custom LSTM Training Script - User-Defined Stock Selection
Allows users to specify which stocks to train
Expected time: 10-15 min per stock
"""

import os
import sys
import yfinance as yf
from datetime import datetime
import logging
import json
import argparse

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

# Suggested stock lists for quick selection
SUGGESTED_STOCKS = {
    'top10': [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('TSLA', 'Tesla Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('AMZN', 'Amazon.com Inc.'),
        ('META', 'Meta Platforms Inc.'),
        ('AMD', 'Advanced Micro Devices'),
        ('CBA.AX', 'Commonwealth Bank of Australia'),
        ('BHP.AX', 'BHP Group Limited'),
    ],
    'us_tech': [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('AMD', 'Advanced Micro Devices'),
        ('INTC', 'Intel Corporation'),
    ],
    'us_mega': [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('AMZN', 'Amazon.com Inc.'),
        ('META', 'Meta Platforms Inc.'),
        ('TSLA', 'Tesla Inc.'),
    ],
    'australian': [
        ('CBA.AX', 'Commonwealth Bank of Australia'),
        ('BHP.AX', 'BHP Group Limited'),
        ('WBC.AX', 'Westpac Banking Corporation'),
        ('ANZ.AX', 'Australia and New Zealand Banking Group'),
        ('NAB.AX', 'National Australia Bank'),
        ('CSL.AX', 'CSL Limited'),
        ('WES.AX', 'Wesfarmers Limited'),
        ('FMG.AX', 'Fortescue Metals Group'),
    ],
    'uk_ftse': [
        ('BP.L', 'BP plc'),
        ('SHEL.L', 'Shell plc'),
        ('HSBA.L', 'HSBC Holdings'),
        ('ULVR.L', 'Unilever'),
        ('AZN.L', 'AstraZeneca'),
    ]
}

def get_stock_name(symbol):
    """Fetch stock name from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('longName', info.get('shortName', symbol))
    except:
        return symbol

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

def get_user_stock_selection():
    """
    Interactive prompt for user to select stocks to train
    
    Returns:
        List of (symbol, name) tuples
    """
    print("\n" + "="*70)
    print("  📋 STOCK SELECTION")
    print("="*70)
    print()
    print("How would you like to select stocks?")
    print()
    print("  1. Use a pre-defined list")
    print("  2. Enter stock symbols manually")
    print("  3. Load from a file")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        # Pre-defined lists
        print("\n📋 Available pre-defined lists:")
        print()
        for i, (key, stocks) in enumerate(SUGGESTED_STOCKS.items(), 1):
            print(f"  {i}. {key.upper()} ({len(stocks)} stocks)")
            for symbol, name in stocks[:3]:
                print(f"     - {symbol}: {name}")
            if len(stocks) > 3:
                print(f"     ... and {len(stocks) - 3} more")
            print()
        
        list_choice = input(f"Select a list (1-{len(SUGGESTED_STOCKS)}): ").strip()
        try:
            list_index = int(list_choice) - 1
            list_key = list(SUGGESTED_STOCKS.keys())[list_index]
            selected_stocks = SUGGESTED_STOCKS[list_key]
            print(f"\n✓ Selected: {list_key.upper()} list ({len(selected_stocks)} stocks)")
            return selected_stocks
        except (ValueError, IndexError):
            print("❌ Invalid selection. Using top 10 stocks.")
            return SUGGESTED_STOCKS['top10']
    
    elif choice == '2':
        # Manual entry
        print("\n📝 Enter stock symbols (comma-separated)")
        print("   Examples: AAPL,MSFT,GOOGL or CBA.AX,BHP.AX")
        print()
        symbols_input = input("Stock symbols: ").strip()
        
        if not symbols_input:
            print("❌ No symbols entered. Using top 10 stocks.")
            return SUGGESTED_STOCKS['top10']
        
        # Parse symbols
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
        
        print(f"\n🔍 Validating {len(symbols)} symbols...")
        validated_stocks = []
        
        for symbol in symbols:
            if symbol:
                print(f"  Checking {symbol}...", end=' ')
                name = get_stock_name(symbol)
                validated_stocks.append((symbol, name))
                print(f"✓ {name}")
        
        if not validated_stocks:
            print("❌ No valid symbols. Using top 10 stocks.")
            return SUGGESTED_STOCKS['top10']
        
        print(f"\n✓ Validated {len(validated_stocks)} stocks")
        return validated_stocks
    
    elif choice == '3':
        # Load from file
        print("\n📁 File format options:")
        print("   - Plain text: One symbol per line (e.g., stocks.txt)")
        print("   - JSON: [{\"symbol\": \"AAPL\", \"name\": \"Apple Inc.\"}, ...]")
        print()
        filename = input("Enter filename: ").strip()
        
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}. Using top 10 stocks.")
            return SUGGESTED_STOCKS['top10']
        
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                
                # Try JSON first
                if content.startswith('['):
                    stocks_data = json.loads(content)
                    validated_stocks = []
                    for item in stocks_data:
                        if isinstance(item, dict):
                            symbol = item.get('symbol', '').upper()
                            name = item.get('name', get_stock_name(symbol))
                        else:
                            symbol = str(item).upper()
                            name = get_stock_name(symbol)
                        if symbol:
                            validated_stocks.append((symbol, name))
                    
                    print(f"✓ Loaded {len(validated_stocks)} stocks from JSON")
                    return validated_stocks
                
                # Plain text - one symbol per line
                else:
                    symbols = [s.strip().upper() for s in content.split('\n') if s.strip()]
                    validated_stocks = []
                    
                    print(f"🔍 Validating {len(symbols)} symbols from file...")
                    for symbol in symbols:
                        if symbol and not symbol.startswith('#'):  # Skip comments
                            name = get_stock_name(symbol)
                            validated_stocks.append((symbol, name))
                            print(f"  ✓ {symbol}: {name}")
                    
                    print(f"\n✓ Loaded {len(validated_stocks)} stocks")
                    return validated_stocks
        
        except Exception as e:
            print(f"❌ Error reading file: {e}. Using top 10 stocks.")
            return SUGGESTED_STOCKS['top10']
    
    else:
        print("❌ Invalid choice. Using top 10 stocks.")
        return SUGGESTED_STOCKS['top10']

def main():
    """
    Train LSTM models for user-selected stocks
    """
    parser = argparse.ArgumentParser(description='Train LSTM models for custom stock selection')
    parser.add_argument('--symbols', type=str, help='Comma-separated stock symbols (e.g., AAPL,MSFT,GOOGL)')
    parser.add_argument('--file', type=str, help='Load symbols from file (one per line or JSON)')
    parser.add_argument('--list', type=str, choices=list(SUGGESTED_STOCKS.keys()), 
                       help='Use a pre-defined stock list')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode (default)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  🚀 CUSTOM LSTM TRAINING")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Determine stock list based on arguments
    if args.symbols:
        # Command-line symbols
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
        all_stocks = [(s, get_stock_name(s)) for s in symbols if s]
        print(f"📋 Training {len(all_stocks)} stocks from command line:")
    
    elif args.file:
        # Load from file
        try:
            with open(args.file, 'r') as f:
                content = f.read().strip()
                if content.startswith('['):
                    stocks_data = json.loads(content)
                    all_stocks = [(item['symbol'], item.get('name', item['symbol'])) 
                                 for item in stocks_data]
                else:
                    symbols = [s.strip().upper() for s in content.split('\n') if s.strip()]
                    all_stocks = [(s, get_stock_name(s)) for s in symbols if s and not s.startswith('#')]
            print(f"📋 Training {len(all_stocks)} stocks from file '{args.file}':")
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    elif args.list:
        # Pre-defined list
        all_stocks = SUGGESTED_STOCKS[args.list]
        print(f"📋 Training {len(all_stocks)} stocks from '{args.list}' list:")
    
    else:
        # Interactive mode (default)
        all_stocks = get_user_stock_selection()
    
    # Display selected stocks
    print()
    for i, (symbol, name) in enumerate(all_stocks, 1):
        print(f"  {i:2d}. {symbol:8s} - {name}")
    print()
    
    print(f"⏱️  Estimated time: {len(all_stocks) * 10} minutes ({len(all_stocks) * 10 / 60:.1f} hours)")
    print()
    
    # Confirmation
    confirm = input("Press ENTER to start training (or 'q' to quit): ").strip().lower()
    if confirm == 'q':
        print("\n❌ Training cancelled by user")
        return False
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
    success_rate = len(successful) / len(all_stocks) * 100 if all_stocks else 0
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
