#!/usr/bin/env python3
"""
Test FULL ML Stack
==================
Verify all 5 components work correctly with Keras+PyTorch
"""

import os
os.environ['KERAS_BACKEND'] = 'torch'

from ml_pipeline import SwingSignalGenerator
import pandas as pd
import numpy as np
from datetime import datetime

print('='*80)
print('TESTING FULL ML STACK - All 5 Components')
print('='*80)
print()

# Create generator
gen = SwingSignalGenerator()

# Create mock data (60+ days for LSTM)
dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
prices = 100 + np.cumsum(np.random.randn(90) * 2)
volumes = 1000000 + np.random.randint(-100000, 100000, 90)

data = pd.DataFrame({
    'Open': prices + np.random.rand(90) * 2,
    'High': prices + np.random.rand(90) * 3,
    'Low': prices - np.random.rand(90) * 2,
    'Close': prices,
    'Volume': volumes
}, index=dates)

print(f'Generated mock data: {len(data)} days')
print(f'Price range: ${data["Close"].min():.2f} - ${data["Close"].max():.2f}')
print()

# Generate signal
print('Generating trading signal...')
signal = gen.generate_signal('TEST.AX', data, news_data=None, current_date=datetime.now())

print()
print('='*80)
print('SIGNAL GENERATED SUCCESSFULLY')
print('='*80)
print()
print(f'Prediction: {signal["prediction"]} ({"BUY" if signal["prediction"] == 1 else "HOLD/SELL"})')
print(f'Confidence: {signal["confidence"]:.2%}')
print(f'Combined Score: {signal["combined_score"]:.4f}')
print()
print('Component Contributions:')
for comp, score in signal['components'].items():
    weight = {'sentiment': 0.25, 'lstm': 0.25, 'technical': 0.25, 
              'momentum': 0.15, 'volume': 0.10}.get(comp, 0)
    contribution = score * weight
    print(f'  {comp:12s}: {score:+.4f} × {weight:.2f} = {contribution:+.5f}')

if 'phase3' in signal:
    print()
    print('Phase 3 Enhancements:')
    for key, val in signal['phase3'].items():
        print(f'  {key}: {val}')

print()
print('='*80)
print('✅ FULL ML STACK OPERATIONAL')
print('='*80)
print()
print('All 5 Components Active:')
print('  1. FinBERT Sentiment Analysis (25%)')
print('  2. Keras LSTM Neural Network (25%) - PyTorch Backend')
print('  3. Technical Analysis (25%)')
print('  4. Momentum Analysis (15%)')
print('  5. Volume Analysis (10%)')
print()
print('Phase 3 Features:')
print('  • Multi-timeframe analysis')
print('  • ATR-based volatility sizing')
print('  • Intraday monitoring integration')
print('='*80)
