"""
LSTM Training Pipeline - Alpha Vantage Edition
FinBERT v4.4.4 - Train LSTM models on historical stock data using Alpha Vantage API
"""

import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Import Alpha Vantage fetcher from the screening module
try:
    from models.screening.alpha_vantage_fetcher import AlphaVantageDataFetcher
    HAS_ALPHA_VANTAGE = True
except ImportError:
    print("WARNING: Alpha Vantage fetcher not found. Will attempt fallback methods.")
    HAS_ALPHA_VANTAGE = False

# Import LSTM predictor
from models.lstm_predictor import StockLSTMPredictor

# Setup logging
log_dir = project_root / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'lstm_training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_training_data_alpha_vantage(symbol: str, fetcher: AlphaVantageDataFetcher) -> pd.DataFrame:
    """
    Fetch historical data for training using Alpha Vantage API
    
    Args:
        symbol: Stock symbol
        fetcher: Alpha Vantage data fetcher instance
    
    Returns:
        DataFrame with historical OHLCV data
    """
    try:
        logger.info(f"Fetching training data for {symbol} from Alpha Vantage...")
        
        # Fetch full historical data (up to 20 years)
        df = fetcher.fetch_daily_data(symbol, outputsize='full')
        
        if df is None or df.empty:
            logger.error(f"No data returned from Alpha Vantage for {symbol}")
            return pd.DataFrame()
        
        logger.info(f"Fetched {len(df)} days of data for {symbol}")
        
        # Ensure column names are lowercase for consistency
        df.columns = [col.lower() for col in df.columns]
        
        # Add technical indicators
        df = add_technical_indicators(df)
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the dataframe
    """
    if len(df) < 20:
        logger.warning("Insufficient data for technical indicators")
        return df
    
    try:
        # Simple Moving Averages
        df['sma_10'] = df['close'].rolling(window=10, min_periods=1).mean()
        df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df['close'].rolling(window=50, min_periods=1).mean()
        
        # Exponential Moving Average
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['sma_20']
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=10, min_periods=1).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price change percentages
        df['daily_return'] = df['close'].pct_change()
        df['volatility'] = df['daily_return'].rolling(window=20).std()
        
        # Fill any NaN values with forward fill, then zero
        df = df.fillna(method='ffill').fillna(0)
        
        logger.info(f"Added {len(df.columns)} total features including technical indicators")
        
    except Exception as e:
        logger.warning(f"Error adding technical indicators: {e}")
    
    return df

def train_model_for_symbol(symbol: str, fetcher: AlphaVantageDataFetcher, epochs: int = 50, sequence_length: int = 60):
    """
    Train LSTM model for a specific symbol using Alpha Vantage data
    
    Args:
        symbol: Stock symbol to train on
        fetcher: Alpha Vantage data fetcher
        epochs: Number of training epochs
        sequence_length: LSTM sequence length
    
    Returns:
        Training results dictionary
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Starting LSTM training for {symbol}")
    logger.info(f"{'='*70}")
    
    # Fetch training data from Alpha Vantage
    df = fetch_training_data_alpha_vantage(symbol, fetcher)
    
    if df.empty or len(df) < sequence_length + 10:
        error_msg = f"Insufficient data for {symbol}. Need at least {sequence_length + 10} data points, got {len(df)}."
        logger.error(error_msg)
        return {
            'symbol': symbol,
            'status': 'failed',
            'error': error_msg
        }
    
    # Initialize LSTM predictor with extended features
    # Use features that are most predictive and always available
    base_features = ['close', 'volume', 'high', 'low', 'open']
    technical_features = ['sma_20', 'rsi', 'macd', 'volatility', 'volume_ratio']
    all_features = base_features + technical_features
    
    # Filter features that exist in the dataframe
    available_features = [f for f in all_features if f in df.columns]
    
    logger.info(f"Training on {len(available_features)} features: {available_features}")
    
    try:
        predictor = StockLSTMPredictor(
            sequence_length=sequence_length,
            features=available_features
        )
        
        # Train the model
        logger.info(f"Training LSTM model with {epochs} epochs...")
        
        results = predictor.train(
            train_data=df,
            validation_split=0.2,
            epochs=epochs,
            batch_size=32,
            verbose=1
        )
        
        # Save model to lstm_models directory
        model_dir = project_root / 'finbert_v4.4.4' / 'lstm_models'
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = model_dir / f'{symbol}_lstm_model.h5'
        predictor.save_model(str(model_path))
        logger.info(f"Model saved to: {model_path}")
        
        # Save training metadata
        metadata = {
            'symbol': symbol,
            'training_date': datetime.now().isoformat(),
            'data_points': len(df),
            'features': available_features,
            'sequence_length': sequence_length,
            'epochs': epochs,
            'data_source': 'Alpha Vantage',
            'results': results,
            'model_path': str(model_path)
        }
        
        metadata_path = model_dir / f'{symbol}_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to: {metadata_path}")
        
        # Test prediction on recent data
        test_data = df.tail(100)
        test_prediction = predictor.predict(test_data)
        logger.info(f"Test prediction: {test_prediction}")
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        return convert_numpy_types({
            'symbol': symbol,
            'status': 'success',
            'training_results': results,
            'test_prediction': test_prediction,
            'model_path': str(model_path),
            'metadata_path': str(metadata_path)
        })
        
    except Exception as e:
        error_msg = f"Training failed for {symbol}: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return {
            'symbol': symbol,
            'status': 'failed',
            'error': error_msg
        }

def train_multiple_symbols(symbols: list, epochs: int = 50):
    """
    Train models for multiple symbols using Alpha Vantage
    """
    if not HAS_ALPHA_VANTAGE:
        logger.error("Alpha Vantage fetcher not available. Cannot proceed with training.")
        return {}
    
    # Initialize Alpha Vantage fetcher with extended cache for training
    fetcher = AlphaVantageDataFetcher(cache_ttl_minutes=1440)  # 24 hour cache
    logger.info(f"Alpha Vantage fetcher initialized with 24-hour cache")
    logger.info(f"Rate limit: 5 calls/minute, Daily limit: 500 requests")
    
    results = {}
    total_symbols = len(symbols)
    
    for idx, symbol in enumerate(symbols, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"Training Progress: {idx}/{total_symbols} - {symbol}")
        logger.info(f"{'='*70}")
        
        # Rate limiting: Wait 12 seconds between stocks (5 calls per minute limit)
        if idx > 1:
            logger.info("Waiting 12 seconds for Alpha Vantage rate limit...")
            time.sleep(12)
        
        result = train_model_for_symbol(symbol, fetcher, epochs)
        results[symbol] = result
        
        # Save intermediate results after each stock
        results_file = project_root / 'finbert_v4.4.4' / 'lstm_models' / 'training_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Intermediate results saved to: {results_file}")
    
    return results

def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description='Train LSTM models for stock prediction using Alpha Vantage')
    
    # Accept both --tickers (batch file format) and --symbols (legacy format)
    parser.add_argument('--tickers', type=str, nargs='+', help='Space-separated list of stock tickers')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of symbols (legacy)')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs (default: 50)')
    parser.add_argument('--sequence-length', type=int, default=60, help='Sequence length (default: 60)')
    parser.add_argument('--test', action='store_true', help='Run quick test with 5 epochs and 1 stock')
    
    args = parser.parse_args()
    
    # Check if Alpha Vantage fetcher is available
    if not HAS_ALPHA_VANTAGE:
        logger.error("="*70)
        logger.error("ERROR: Alpha Vantage fetcher not found!")
        logger.error("="*70)
        logger.error("The file 'models/screening/alpha_vantage_fetcher.py' is missing.")
        logger.error("Please ensure the package is complete and re-extract if necessary.")
        return 1
    
    # Create models directory if it doesn't exist
    model_dir = project_root / 'finbert_v4.4.4' / 'lstm_models'
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which stocks to train
    if args.test:
        # Quick test mode
        logger.info("="*70)
        logger.info("TEST MODE: Training 1 stock with 5 epochs")
        logger.info("="*70)
        symbols = ['CBA.AX']
        epochs = 5
    elif args.tickers:
        # Batch file format: --tickers CBA.AX BHP.AX CSL.AX
        symbols = args.tickers
        epochs = args.epochs
    elif args.symbols:
        # Legacy format: --symbols CBA.AX,BHP.AX,CSL.AX
        symbols = args.symbols.split(',')
        epochs = args.epochs
    else:
        # Default: Quick training with 3 ASX stocks
        logger.info("No tickers specified. Using default ASX stocks for quick training.")
        symbols = ['CBA.AX', 'BHP.AX', 'CSL.AX']
        epochs = args.epochs
    
    # Clean up symbols (remove whitespace)
    symbols = [s.strip() for s in symbols]
    
    logger.info("="*70)
    logger.info("LSTM TRAINING CONFIGURATION")
    logger.info("="*70)
    logger.info(f"Stocks to train: {len(symbols)}")
    logger.info(f"Tickers: {', '.join(symbols)}")
    logger.info(f"Epochs per stock: {epochs}")
    logger.info(f"Sequence length: {args.sequence_length}")
    logger.info(f"Estimated time: {len(symbols) * 10}-{len(symbols) * 30} minutes")
    logger.info(f"Data source: Alpha Vantage API")
    logger.info(f"Model output: {model_dir}")
    logger.info("="*70)
    
    # Train models
    results = train_multiple_symbols(symbols, epochs)
    
    # Print summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    
    success_count = 0
    failed_count = 0
    
    for symbol, result in results.items():
        status = result.get('status', 'unknown')
        
        if status == 'success':
            success_count += 1
            print(f"\n✓ {symbol}: SUCCESS")
            if 'training_results' in result:
                train_res = result['training_results']
                final_loss = train_res.get('final_loss', 'N/A')
                final_val_loss = train_res.get('final_val_loss', 'N/A')
                
                if isinstance(final_loss, (int, float)):
                    print(f"    Final Loss: {final_loss:.4f}")
                if isinstance(final_val_loss, (int, float)):
                    print(f"    Val Loss: {final_val_loss:.4f}")
            
            if 'test_prediction' in result:
                pred = result['test_prediction']
                print(f"    Test Prediction: {pred.get('prediction', 'N/A')}")
                print(f"    Confidence: {pred.get('confidence', 'N/A')}%")
            
            if 'model_path' in result:
                print(f"    Model: {result['model_path']}")
        else:
            failed_count += 1
            print(f"\n✗ {symbol}: FAILED")
            if 'error' in result:
                print(f"    Error: {result['error']}")
    
    print("\n" + "="*70)
    print(f"Training complete!")
    print(f"  Success: {success_count}/{len(symbols)}")
    print(f"  Failed: {failed_count}/{len(symbols)}")
    print(f"  Models saved to: {model_dir}")
    print(f"  Results saved to: {model_dir / 'training_results.json'}")
    print("="*70)
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
