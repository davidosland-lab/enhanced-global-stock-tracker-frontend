"""
LSTM Training Pipeline
FinBERT v4.0 - Train LSTM models on historical stock data
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
import urllib.request
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.lstm_predictor import StockLSTMPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_training_data(symbol: str, period: str = '2y') -> pd.DataFrame:
    """
    Fetch historical data for training
    
    Args:
        symbol: Stock symbol
        period: Time period (1y, 2y, 5y, etc.)
    
    Returns:
        DataFrame with historical data
    """
    try:
        logger.info(f"Fetching training data for {symbol} (period: {period})")
        
        # Build Yahoo Finance URL
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        logger.debug(f"Requesting data from: {url}")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'chart' not in data or 'result' not in data['chart']:
            logger.error(f"Invalid response structure for {symbol}")
            logger.debug(f"Response keys: {list(data.keys())}")
            return pd.DataFrame()
        
        if not data['chart']['result']:
            logger.error(f"No data returned for {symbol}")
            return pd.DataFrame()
        
        result = data['chart']['result'][0]
        
        # Check if there's an error in the response
        if 'error' in result:
            error_msg = result['error']
            logger.error(f"API error for {symbol}: {error_msg}")
            return pd.DataFrame()
        
        timestamps = result.get('timestamp', [])
        if not timestamps:
            logger.error(f"No timestamps found for {symbol}")
            return pd.DataFrame()
        
        indicators = result.get('indicators', {})
        quote = indicators.get('quote', [{}])[0]
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(timestamps, unit='s'),
            'open': quote.get('open', []),
            'high': quote.get('high', []),
            'low': quote.get('low', []),
            'close': quote.get('close', []),
            'volume': quote.get('volume', [])
        })
        
        logger.debug(f"Raw data shape for {symbol}: {df.shape}")
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        if len(df) == 0:
            logger.error(f"All data was NaN for {symbol}")
            return pd.DataFrame()
        
        # Add technical indicators
        df = add_technical_indicators(df)
        
        logger.info(f"✓ Successfully fetched {len(df)} days of data for {symbol}")
        return df
        
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP Error fetching data for {symbol}: {e.code} - {e.reason}")
        return pd.DataFrame()
    except urllib.error.URLError as e:
        logger.error(f"URL Error fetching data for {symbol}: {e.reason}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {symbol}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {symbol}: {type(e).__name__}: {e}")
        return pd.DataFrame()

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the dataframe
    """
    if len(df) < 20:
        return df
    
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
    
    # Fill any NaN values (pandas 2.x compatible)
    df = df.ffill().fillna(0)
    
    return df

def train_model_for_symbol(symbol: str, epochs: int = 50, sequence_length: int = 60):
    """
    Train LSTM model for a specific symbol
    
    Args:
        symbol: Stock symbol to train on
        epochs: Number of training epochs
        sequence_length: LSTM sequence length
    
    Returns:
        Training results dict with status and details
    """
    logger.info(f"="*60)
    logger.info(f"Starting LSTM training for {symbol}")
    logger.info(f"Parameters: epochs={epochs}, sequence_length={sequence_length}")
    logger.info(f"="*60)
    
    # Fetch training data
    try:
        df = fetch_training_data(symbol, period='2y')
    except Exception as e:
        error_msg = f"Failed to fetch data: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'symbol': symbol,
            'step': 'data_fetch'
        }
    
    if len(df) == 0:
        error_msg = f"No data available for {symbol}. Symbol may be invalid or delisted."
        logger.error(error_msg)
        return {
            'error': error_msg,
            'symbol': symbol,
            'step': 'data_validation',
            'suggestion': 'Check if the symbol is correct and active on the exchange'
        }
    
    min_required = sequence_length + 10
    if len(df) < min_required:
        error_msg = f"Insufficient data for {symbol}. Need at least {min_required} data points, got {len(df)}."
        logger.error(error_msg)
        return {
            'error': error_msg,
            'symbol': symbol,
            'data_points': len(df),
            'required': min_required,
            'step': 'data_validation'
        }
    
    logger.info(f"✓ Data validation passed: {len(df)} data points available")
    
    # Initialize LSTM predictor with extended features
    features = ['close', 'volume', 'high', 'low', 'open', 'sma_20', 'rsi', 'macd']
    
    # Filter features that exist in the dataframe
    available_features = [f for f in features if f in df.columns]
    
    if len(available_features) == 0:
        error_msg = f"No valid features found in data for {symbol}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'symbol': symbol,
            'step': 'feature_preparation',
            'available_columns': list(df.columns)
        }
    
    logger.info(f"✓ Features prepared: {len(available_features)} features")
    logger.info(f"  Features: {available_features}")
    
    try:
        predictor = StockLSTMPredictor(
            sequence_length=sequence_length,
            features=available_features
        )
    except Exception as e:
        error_msg = f"Failed to initialize LSTM predictor: {str(e)}"
        logger.error(error_msg)
        return {
            'error': error_msg,
            'symbol': symbol,
            'step': 'model_initialization'
        }
    
    # Train the model
    logger.info(f"Starting training on {len(available_features)} features...")
    
    try:
        results = predictor.train(
            train_data=df,
            validation_split=0.2,
            epochs=epochs,
            batch_size=32,
            verbose=1
        )
    except Exception as e:
        import traceback
        error_msg = f"Training failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return {
            'error': error_msg,
            'symbol': symbol,
            'step': 'model_training',
            'traceback': traceback.format_exc()
        }
    
    logger.info(f"✓ Training completed successfully")
    
    # Save training metadata
    try:
        metadata = {
            'symbol': symbol,
            'training_date': datetime.now().isoformat(),
            'data_points': len(df),
            'features': available_features,
            'sequence_length': sequence_length,
            'epochs': epochs,
            'results': results
        }
        
        metadata_path = f'models/lstm_{symbol}_metadata.json'
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✓ Metadata saved to {metadata_path}")
    except Exception as e:
        logger.warning(f"Failed to save metadata: {e}")
        metadata_path = None
    
    # Test prediction on recent data
    try:
        test_data = df.tail(100)
        test_prediction = predictor.predict(test_data)
        logger.info(f"✓ Test prediction: {test_prediction}")
    except Exception as e:
        logger.warning(f"Failed to generate test prediction: {e}")
        test_prediction = None
    
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
    
    logger.info(f"="*60)
    logger.info(f"✓ LSTM training complete for {symbol}")
    logger.info(f"="*60)
    
    return convert_numpy_types({
        'symbol': symbol,
        'status': 'success',
        'training_results': results,
        'test_prediction': test_prediction,
        'metadata_path': metadata_path,
        'data_points': len(df),
        'features_used': available_features,
        'epochs_completed': epochs
    })

def train_multiple_symbols(symbols: list, epochs: int = 50):
    """
    Train models for multiple symbols
    """
    results = {}
    
    for symbol in symbols:
        logger.info(f"\n{'='*50}")
        logger.info(f"Training {symbol}")
        logger.info(f"{'='*50}")
        
        result = train_model_for_symbol(symbol, epochs)
        results[symbol] = result
        
        # Save intermediate results
        with open('models/training_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    return results

def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description='Train LSTM models for stock prediction')
    parser.add_argument('--symbol', type=str, help='Stock symbol to train on')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of symbols')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--sequence-length', type=int, default=60, help='Sequence length')
    parser.add_argument('--test', action='store_true', help='Run quick test with fewer epochs')
    
    args = parser.parse_args()
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    if args.test:
        # Quick test mode
        logger.info("Running in test mode with reduced epochs")
        args.epochs = 5
        symbols = ['AAPL']
    elif args.symbols:
        symbols = args.symbols.split(',')
    elif args.symbol:
        symbols = [args.symbol]
    else:
        # Default symbols for training
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    logger.info(f"Training LSTM models for: {symbols}")
    logger.info(f"Epochs: {args.epochs}, Sequence Length: {args.sequence_length}")
    
    results = train_multiple_symbols(symbols, args.epochs)
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    
    for symbol, result in results.items():
        if 'error' not in result:
            print(f"\n{symbol}:")
            print(f"  Status: {result.get('status', 'Unknown')}")
            if 'training_results' in result:
                train_res = result['training_results']
                final_loss = train_res.get('final_loss', 'N/A')
                final_val_loss = train_res.get('final_val_loss', 'N/A')
                if isinstance(final_loss, (int, float)):
                    print(f"  Final Loss: {final_loss:.4f}")
                else:
                    print(f"  Final Loss: {final_loss}")
                if isinstance(final_val_loss, (int, float)):
                    print(f"  Final Val Loss: {final_val_loss:.4f}")
                else:
                    print(f"  Final Val Loss: {final_val_loss}")
            if 'test_prediction' in result:
                pred = result['test_prediction']
                print(f"  Test Prediction: {pred.get('prediction')} ({pred.get('confidence')}% confidence)")
        else:
            print(f"\n{symbol}: ERROR - {result['error']}")
    
    print("\n" + "="*60)
    print("Training complete!")
    print(f"Results saved to: models/training_results.json")

if __name__ == "__main__":
    main()