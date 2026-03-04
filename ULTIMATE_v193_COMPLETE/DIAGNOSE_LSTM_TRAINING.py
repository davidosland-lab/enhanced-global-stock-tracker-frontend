"""
LSTM Training Diagnostic Tool - v1.3.15.87
==========================================

Tests LSTM training components to identify the issue.

Usage:
    python DIAGNOSE_LSTM_TRAINING.py AAPL
"""

import sys
import os

def test_imports():
    """Test if required libraries can be imported"""
    print("=" * 80)
    print("  TESTING IMPORTS")
    print("=" * 80)
    print()
    
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'tensorflow': 'tensorflow/keras (LSTM)',
        'urllib': 'urllib.request (data fetching)'
    }
    
    results = {}
    for module, description in required.items():
        try:
            __import__(module)
            print(f"[OK] {description}")
            results[module] = True
        except ImportError as e:
            print(f"[ERROR] {description}: {e}")
            results[module] = False
    
    print()
    return all(results.values())


def test_data_fetch(symbol):
    """Test if we can fetch training data"""
    print("=" * 80)
    print("  TESTING DATA FETCH")
    print("=" * 80)
    print()
    
    try:
        import urllib.request
        import json
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        print(f"Fetching data for {symbol}...")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            print(f"[OK] Fetched {len(timestamps)} data points")
            return True
        else:
            print(f"[ERROR] Invalid response format")
            return False
            
    except Exception as e:
        print(f"[ERROR] Data fetch failed: {e}")
        return False


def test_lstm_predictor():
    """Test if LSTM predictor can be initialized"""
    print()
    print("=" * 80)
    print("  TESTING LSTM PREDICTOR")
    print("=" * 80)
    print()
    
    try:
        # Add parent directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'finbert_v4.4.4'))
        
        from models.lstm_predictor import StockLSTMPredictor
        
        print("Initializing LSTM predictor...")
        predictor = StockLSTMPredictor(
            sequence_length=60,
            features=['close', 'volume']
        )
        
        print("[OK] LSTM predictor initialized successfully")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Cannot import LSTM predictor: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] LSTM predictor initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_training_module():
    """Test if training module can be imported"""
    print()
    print("=" * 80)
    print("  TESTING TRAINING MODULE")
    print("=" * 80)
    print()
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'finbert_v4.4.4'))
        
        from models.train_lstm import train_model_for_symbol
        
        print("[OK] Training module imported successfully")
        print()
        print("Training function signature:")
        print(f"  train_model_for_symbol(symbol, epochs=50, sequence_length=60)")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Cannot import training module: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[ERROR] Training module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print()
    print("=" * 80)
    print("  LSTM TRAINING DIAGNOSTIC - v1.3.15.87")
    print("=" * 80)
    print()
    
    # Check if symbol provided
    if len(sys.argv) < 2:
        symbol = "AAPL"
        print(f"No symbol provided, using default: {symbol}")
    else:
        symbol = sys.argv[1]
        print(f"Testing with symbol: {symbol}")
    
    print()
    
    # Run tests
    test_results = []
    
    test_results.append(("Imports", test_imports()))
    test_results.append(("Data Fetch", test_data_fetch(symbol)))
    test_results.append(("LSTM Predictor", test_lstm_predictor()))
    test_results.append(("Training Module", test_training_module()))
    
    # Summary
    print()
    print("=" * 80)
    print("  DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print()
    
    all_passed = True
    for test_name, result in test_results:
        status = "[OK]" if result else "[FAILED]"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("[OK] All diagnostic tests passed!")
        print()
        print("LSTM training should work. If it's still failing:")
        print("1. Check Flask server logs for detailed error messages")
        print("2. Try training from command line:")
        print(f"   cd finbert_v4.4.4")
        print(f"   python models/train_lstm.py --symbol {symbol} --epochs 30")
        print()
    else:
        print("[ERROR] Some tests failed. Common issues:")
        print()
        print("If 'tensorflow/keras' failed:")
        print("  - Install: pip install tensorflow keras")
        print("  - Or: conda install tensorflow keras")
        print()
        print("If 'Data Fetch' failed:")
        print("  - Check internet connection")
        print("  - Yahoo Finance might be temporarily unavailable")
        print("  - Try a different symbol")
        print()
        print("If 'LSTM Predictor' failed:")
        print("  - Make sure you're in the correct directory")
        print("  - Check if finbert_v4.4.4/models/lstm_predictor.py exists")
        print()
    
    print("=" * 80)
    print()
    input("Press Enter to exit...")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
