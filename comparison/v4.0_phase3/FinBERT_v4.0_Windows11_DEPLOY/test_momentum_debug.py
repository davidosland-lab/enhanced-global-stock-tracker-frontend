"""Debug momentum model issue"""
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, 'models')
from backtesting import BacktestPredictionEngine, HistoricalDataLoader

# Test with real data
symbol = "AAPL"
start_date = "2024-01-01"
end_date = "2024-10-01"

print(f"Testing Momentum Model for {symbol}")
print("=" * 60)

# Load data
loader = HistoricalDataLoader(symbol)
data = loader.load_price_data(start_date, end_date)

print(f"✓ Loaded {len(data)} days of data")

# Test momentum model
engine = BacktestPredictionEngine(model_type='momentum', confidence_threshold=0.6)

# Get prediction at a specific point
test_date = pd.to_datetime("2024-06-15")
training_window = data[data.index < test_date].tail(60)

print(f"\n📊 Testing prediction at {test_date}")
print(f"Training window: {len(training_window)} days")
print(f"Current price: ${training_window['Close'].iloc[-1]:.2f}")

# Generate prediction
pred = engine._predict_momentum(training_window, training_window['Close'].iloc[-1])

print("\n🎯 Momentum Prediction Result:")
print(f"Prediction: {pred['prediction']}")
print(f"Confidence: {pred['confidence']:.3f}")
print(f"Momentum Score: {pred.get('momentum_score', 0):.4f}")
print(f"Recent Return (5d): {pred.get('recent_return', 0):.4f}")
print(f"Medium Return (20d): {pred.get('medium_return', 0):.4f}")
print(f"Trend Strength: {pred.get('trend_strength', 0):.6f}")
print(f"ROC-20: {pred.get('roc_20', 0):.4f}")
print(f"Acceleration: {pred.get('acceleration', 0):.6f}")
print(f"Volatility: {pred.get('volatility', 0):.4f}")

# Run full backtest
print(f"\n🔄 Running full backtest with Momentum model...")
predictions = engine.walk_forward_backtest(data, start_date, end_date)

print(f"✓ Generated {len(predictions)} predictions")

# Analyze predictions
buy_signals = len(predictions[predictions['prediction'] == 'BUY'])
sell_signals = len(predictions[predictions['prediction'] == 'SELL'])
hold_signals = len(predictions[predictions['prediction'] == 'HOLD'])

print(f"\n📈 Signal Distribution:")
print(f"BUY:  {buy_signals:3d} ({buy_signals/len(predictions)*100:.1f}%)")
print(f"SELL: {sell_signals:3d} ({sell_signals/len(predictions)*100:.1f}%)")
print(f"HOLD: {hold_signals:3d} ({hold_signals/len(predictions)*100:.1f}%)")

# Check confidence levels
avg_confidence = predictions['confidence'].mean()
print(f"\nAverage Confidence: {avg_confidence:.3f}")
print(f"Max Confidence: {predictions['confidence'].max():.3f}")
print(f"Min Confidence: {predictions['confidence'].min():.3f}")

# Check for errors
if 'error' in predictions.columns:
    errors = predictions[predictions['error'].notna()]
    if len(errors) > 0:
        print(f"\n⚠️ Errors found: {len(errors)}")
        print(errors[['timestamp', 'error']].head())

print("\n" + "=" * 60)
print("✅ Debug complete")
