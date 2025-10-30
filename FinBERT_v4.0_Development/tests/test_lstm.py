"""
Test LSTM Model Implementation
FinBERT v4.0
"""

import sys
import os
import json
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.lstm_predictor import StockLSTMPredictor, get_lstm_prediction

def test_lstm_initialization():
    """Test LSTM model initialization"""
    print("Testing LSTM initialization...")
    
    predictor = StockLSTMPredictor(sequence_length=30)
    assert predictor.sequence_length == 30
    assert not predictor.is_trained
    
    print("✓ LSTM initialization successful")
    return True

def test_data_preparation():
    """Test data preparation for LSTM"""
    print("\nTesting data preparation...")
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100)
    data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(100) * 10 + 100,
        'high': np.random.randn(100) * 10 + 105,
        'low': np.random.randn(100) * 10 + 95,
        'close': np.random.randn(100) * 10 + 100,
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    predictor = StockLSTMPredictor(sequence_length=20)
    X, y = predictor.prepare_data(data)
    
    print(f"  Input shape: {X.shape}")
    print(f"  Output shape: {y.shape}")
    
    assert len(X) > 0, "No sequences created"
    assert X.shape[1] == 20, "Incorrect sequence length"
    
    print("✓ Data preparation successful")
    return True

def test_simple_prediction():
    """Test simple fallback prediction"""
    print("\nTesting simple prediction...")
    
    # Create sample chart data
    chart_data = [
        {'close': 100 + i * 0.5, 'volume': 1000000} 
        for i in range(20)
    ]
    
    predictor = StockLSTMPredictor()
    df = pd.DataFrame(chart_data)
    result = predictor._simple_prediction(df)
    
    print(f"  Prediction: {result['prediction']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Predicted price: ${result['predicted_price']}")
    
    assert 'prediction' in result
    assert result['prediction'] in ['BUY', 'SELL', 'HOLD']
    assert 0 <= result['confidence'] <= 100
    
    print("✓ Simple prediction successful")
    return True

def test_lstm_with_tensorflow():
    """Test LSTM with TensorFlow if available"""
    print("\nTesting LSTM with TensorFlow...")
    
    try:
        import tensorflow as tf
        print(f"  TensorFlow version: {tf.__version__}")
        
        # Create more substantial test data
        dates = pd.date_range('2023-01-01', periods=200)
        trend = np.linspace(100, 120, 200)  # Upward trend
        noise = np.random.randn(200) * 2
        
        data = pd.DataFrame({
            'timestamp': dates,
            'close': trend + noise,
            'open': trend + noise + np.random.randn(200),
            'high': trend + noise + abs(np.random.randn(200)) * 2,
            'low': trend + noise - abs(np.random.randn(200)) * 2,
            'volume': np.random.randint(1000000, 10000000, 200)
        })
        
        # Initialize and build model
        predictor = StockLSTMPredictor(sequence_length=30)
        
        # Quick training test (minimal epochs)
        print("  Training LSTM model (test mode)...")
        result = predictor.train(
            train_data=data,
            epochs=2,  # Just 2 epochs for testing
            batch_size=16,
            verbose=0
        )
        
        print(f"  Training status: {result.get('status')}")
        print(f"  Final loss: {result.get('final_loss', 'N/A')}")
        
        # Test prediction
        prediction = predictor.predict(data.tail(50))
        print(f"  LSTM Prediction: {prediction['prediction']}")
        print(f"  Confidence: {prediction['confidence']}%")
        print(f"  Model type: {prediction['model_type']}")
        
        print("✓ LSTM with TensorFlow successful")
        return True
        
    except ImportError:
        print("  ⚠ TensorFlow not installed - skipping LSTM tests")
        print("  To enable LSTM, run: pip install tensorflow")
        return False

def test_get_lstm_prediction_function():
    """Test the convenience function"""
    print("\nTesting get_lstm_prediction function...")
    
    # Create sample data
    chart_data = [
        {
            'close': 100 + i * np.random.randn() * 0.5,
            'volume': np.random.randint(1000000, 10000000),
            'high': 102 + i * np.random.randn() * 0.3,
            'low': 98 + i * np.random.randn() * 0.3,
            'open': 100 + i * np.random.randn() * 0.4
        }
        for i in range(50)
    ]
    
    current_price = 105.50
    
    result = get_lstm_prediction(chart_data, current_price)
    
    print(f"  Result keys: {list(result.keys())}")
    print(f"  Prediction: {result.get('prediction')}")
    print(f"  Model: {result.get('model_type')}")
    
    assert 'prediction' in result
    assert 'predicted_price' in result
    assert 'confidence' in result
    
    print("✓ get_lstm_prediction function successful")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running LSTM Model Tests for FinBERT v4.0")
    print("=" * 60)
    
    tests = [
        test_lstm_initialization,
        test_data_preparation,
        test_simple_prediction,
        test_lstm_with_tensorflow,
        test_get_lstm_prediction_function
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"⚠ {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)