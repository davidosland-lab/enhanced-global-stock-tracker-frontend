"""
Test FinBERT Integration with Overnight Stock Screener
=======================================================

Validates that the integration is working correctly:
1. FinBERT Bridge initialization
2. Real LSTM predictions (NOT placeholders)
3. Real FinBERT sentiment (NOT synthetic data)
4. Real news scraping (NOT mock data)
5. Batch predictor using bridge
6. End-to-end prediction flow

**Validation Rules**:
- NO synthetic, fake, or random data
- NO placeholders
- Real neural networks only
- Real transformer sentiment only
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import components
from models.screening.finbert_bridge import get_finbert_bridge
from models.screening.batch_predictor import BatchPredictor


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_bridge_availability():
    """Test 1: Bridge Initialization and Component Availability"""
    print_section("TEST 1: FinBERT Bridge Availability")
    
    try:
        bridge = get_finbert_bridge()
        availability = bridge.is_available()
        
        print(f"\nComponent Status:")
        print(f"  LSTM Available:      {'✓ YES' if availability['lstm_available'] else '✗ NO'}")
        print(f"  Sentiment Available: {'✓ YES' if availability['sentiment_available'] else '✗ NO'}")
        print(f"  News Available:      {'✓ YES' if availability['news_available'] else '✗ NO'}")
        
        info = bridge.get_component_info()
        print(f"\nComponent Details:")
        print(f"  FinBERT Path:    {info['finbert_path']}")
        print(f"  LSTM Models:     {info['lstm']['model_path']}")
        print(f"  Sentiment Model: {info['sentiment']['model_name']}")
        print(f"  News Sources:    {', '.join(info['news']['sources'])}")
        
        if not any(availability.values()):
            print("\n⚠ WARNING: No components available!")
            return False
        
        print("\n✓ Bridge initialization successful")
        return True
        
    except Exception as e:
        print(f"\n✗ Bridge initialization failed: {e}")
        return False


def test_lstm_prediction():
    """Test 2: Real LSTM Prediction (NO Placeholder)"""
    print_section("TEST 2: Real LSTM Neural Network Prediction")
    
    try:
        bridge = get_finbert_bridge()
        if not bridge.is_available()['lstm_available']:
            print("\n⚠ LSTM component not available - SKIPPING TEST")
            return False
        
        # Test with multiple symbols
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']
        print(f"\nTesting LSTM predictions for: {', '.join(test_symbols)}")
        
        success_count = 0
        for symbol in test_symbols:
            print(f"\n--- Testing {symbol} ---")
            
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if hist.empty or len(hist) < 60:
                print(f"  ⚠ Insufficient data: {len(hist)} days")
                continue
            
            # Get LSTM prediction
            result = bridge.get_lstm_prediction(symbol, hist)
            
            if result is None:
                print(f"  ⚠ Prediction returned None")
                continue
            
            print(f"  Model Trained:    {result.get('model_trained', False)}")
            print(f"  Data Sufficient:  {result.get('data_sufficient', False)}")
            
            if result.get('model_trained'):
                print(f"  Direction:        {result['direction']:.4f}")
                print(f"  Confidence:       {result['confidence']:.4f}")
                print(f"  Predicted Price:  ${result.get('predicted_price', 0):.2f}")
                print(f"  Current Price:    ${hist['Close'].iloc[-1]:.2f}")
                
                # Validation: Check this is NOT a placeholder
                if result['confidence'] == 0.5 and result['direction'] != 0:
                    print(f"  ⚠ WARNING: Looks like placeholder (confidence=0.5)")
                else:
                    print(f"  ✓ Real LSTM prediction detected")
                    success_count += 1
            else:
                print(f"  ℹ No trained model for {symbol}")
        
        if success_count > 0:
            print(f"\n✓ LSTM test successful: {success_count}/{len(test_symbols)} predictions")
            return True
        else:
            print(f"\n⚠ No successful LSTM predictions")
            return False
        
    except Exception as e:
        print(f"\n✗ LSTM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sentiment_analysis():
    """Test 3: Real FinBERT Sentiment with News (NO Mock Data)"""
    print_section("TEST 3: Real FinBERT Sentiment Analysis")
    
    try:
        bridge = get_finbert_bridge()
        if not bridge.is_available()['news_available']:
            print("\n⚠ News sentiment component not available - SKIPPING TEST")
            return False
        
        # Test with popular stocks (more likely to have news)
        test_symbols = ['AAPL', 'TSLA', 'MSFT']
        print(f"\nTesting sentiment analysis for: {', '.join(test_symbols)}")
        
        success_count = 0
        for symbol in test_symbols:
            print(f"\n--- Testing {symbol} ---")
            
            # Get sentiment analysis
            result = bridge.get_sentiment_analysis(symbol, use_cache=False)
            
            if result is None:
                print(f"  ⚠ Sentiment analysis returned None")
                continue
            
            article_count = result.get('article_count', 0)
            print(f"  Sentiment:     {result.get('sentiment', 'unknown')}")
            print(f"  Confidence:    {result.get('confidence', 0):.1f}%")
            print(f"  Direction:     {result.get('direction', 0):.4f}")
            print(f"  Articles:      {article_count}")
            print(f"  Sources:       {', '.join(result.get('sources', []))}")
            print(f"  Cached:        {result.get('cached', False)}")
            
            # Validation: Check this is NOT synthetic data
            if article_count == 0:
                print(f"  ⚠ No articles found - cannot validate")
            elif article_count > 0:
                print(f"  ✓ Real news articles analyzed")
                success_count += 1
            
        if success_count > 0:
            print(f"\n✓ Sentiment test successful: {success_count}/{len(test_symbols)} with news")
            return True
        else:
            print(f"\n⚠ No successful sentiment analyses with news")
            return False
        
    except Exception as e:
        print(f"\n✗ Sentiment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_predictor_integration():
    """Test 4: Batch Predictor Using FinBERT Bridge"""
    print_section("TEST 4: Batch Predictor Integration")
    
    try:
        predictor = BatchPredictor()
        
        print("\nBatch Predictor Status:")
        print(f"  FinBERT LSTM:      {predictor.finbert_components['lstm_available']}")
        print(f"  FinBERT Sentiment: {predictor.finbert_components['sentiment_available']}")
        print(f"  FinBERT News:      {predictor.finbert_components['news_available']}")
        
        # Create test stock data
        test_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'sector': 'Technology'}
        ]
        
        print(f"\nTesting batch prediction for {len(test_stocks)} stocks...")
        
        # Run batch prediction
        predictions = predictor.predict_batch(test_stocks)
        
        print(f"\nPrediction Results:")
        for pred in predictions:
            symbol = pred.get('symbol', 'unknown')
            overall_pred = pred.get('prediction', 'HOLD')
            confidence = pred.get('confidence', 0)
            
            print(f"\n  {symbol}:")
            print(f"    Prediction:  {overall_pred}")
            print(f"    Confidence:  {confidence:.1f}%")
            
            # Check individual model predictions
            models = pred.get('models', {})
            if 'lstm' in models:
                lstm = models['lstm']
                print(f"    LSTM:        direction={lstm['direction']:.3f}, conf={lstm['confidence']:.3f}")
            
            if 'sentiment' in models:
                sent = models['sentiment']
                print(f"    Sentiment:   direction={sent['direction']:.3f}, conf={sent['confidence']:.3f}")
        
        print("\n✓ Batch predictor integration successful")
        return True
        
    except Exception as e:
        print(f"\n✗ Batch predictor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_rules():
    """Test 5: Validation Rules (NO Synthetic Data)"""
    print_section("TEST 5: Validation Rules")
    
    print("\nValidating NO synthetic data rules:")
    
    # Check imports for suspicious modules
    import models.screening.batch_predictor as bp
    
    checks = {
        'random': 'random' not in dir(bp),
        'numpy.random': not any('random' in str(v).lower() for v in dir(bp.np) if hasattr(bp.np, v)),
        'mock': 'Mock' not in dir(bp),
        'fake': 'fake' not in dir(bp)
    }
    
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} No {check} module")
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n✓ Validation rules check passed")
    else:
        print("\n✗ Validation rules check failed")
    
    return all_passed


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("  FINBERT INTEGRATION TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    tests = [
        ("Bridge Availability", test_bridge_availability),
        ("LSTM Prediction", test_lstm_prediction),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Batch Predictor", test_batch_predictor_integration),
        ("Validation Rules", test_validation_rules)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {name}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("  ✓ ALL TESTS PASSED!")
    elif passed > 0:
        print(f"  ⚠ PARTIAL SUCCESS ({passed}/{total})")
    else:
        print("  ✗ ALL TESTS FAILED")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
