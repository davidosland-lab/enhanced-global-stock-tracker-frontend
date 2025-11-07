import sys
import os
from datetime import datetime, timedelta

# Add models to path
sys.path.insert(0, os.path.join(os.getcwd(), 'models'))

# Test the exact code path from the Flask endpoint
from backtesting import HistoricalDataLoader, BacktestPredictionEngine, TradingSimulator

# Use the same date calculation as the UI
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
symbol = 'AAPL'

print(f'Testing backtest flow for {symbol}')
print(f'Dates: {start_date} to {end_date}')
print('=' * 60)

# Phase 1: Load historical data
print('Phase 1: Loading historical data...')
loader = HistoricalDataLoader(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date,
    use_cache=True
)

historical_data = loader.load_price_data()

if historical_data.empty:
    print('ERROR: historical_data is EMPTY!')
    sys.exit(1)
else:
    print(f'✓ Loaded {len(historical_data)} rows')
    print(f'  Columns: {list(historical_data.columns)}')

# Phase 2: Generate predictions  
print('\nPhase 2: Generating predictions...')
engine = BacktestPredictionEngine(
    model_type='ensemble',
    confidence_threshold=0.6
)

predictions = engine.walk_forward_backtest(
    data=historical_data,
    start_date=start_date,
    end_date=end_date,
    prediction_frequency='daily',
    lookback_days=60
)

if predictions.empty:
    print('ERROR: predictions is EMPTY!')
    sys.exit(1)
else:
    print(f'✓ Generated {len(predictions)} predictions')

# Phase 3: Simulate trading
print('\nPhase 3: Simulating trading...')
simulator = TradingSimulator(
    initial_capital=10000,
    commission_rate=0.001,
    slippage_rate=0.0005,
    max_position_size=0.20
)

for idx, row in predictions.iterrows():
    simulator.execute_signal(
        timestamp=row['timestamp'],
        signal=row['prediction'],
        price=row.get('actual_price', row['current_price']),
        confidence=row['confidence']
    )

# Close remaining positions
if simulator.positions:
    last_price = predictions.iloc[-1].get('actual_price', predictions.iloc[-1]['current_price'])
    last_timestamp = predictions.iloc[-1]['timestamp']
    simulator._close_positions(last_timestamp, last_price)

# Get performance metrics
metrics = simulator.calculate_performance_metrics()

print(f'✓ Backtest complete')
print(f'  Total Return: {metrics.get("total_return_pct", 0):.2f}%')
print(f'  Total Trades: {metrics.get("total_trades", 0)}')
print(f'  Win Rate: {metrics.get("win_rate", 0):.1f}%')

print('\nSUCCESS: All phases completed without error!')
