#!/usr/bin/env python3
"""
Test Parameter Optimization Feature
"""

import sys
import os
from datetime import datetime, timedelta

# Add models to path
sys.path.insert(0, os.path.join(os.getcwd(), 'models'))

from backtesting.parameter_optimizer import (
    ParameterOptimizer, 
    DEFAULT_PARAMETER_GRID, 
    QUICK_PARAMETER_GRID
)
from backtesting import HistoricalDataLoader, BacktestPredictionEngine, TradingSimulator

print("="*70)
print("Testing Parameter Optimization Feature")
print("="*70)
print()

# Test parameters
symbol = 'AAPL'
start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')  # 6 months
end_date = datetime.now().strftime('%Y-%m-%d')
model_type = 'ensemble'
initial_capital = 10000

print(f"Symbol: {symbol}")
print(f"Period: {start_date} to {end_date}")
print(f"Model: {model_type}")
print(f"Capital: ${initial_capital:,}")
print()

# Create backtest wrapper
def backtest_wrapper(**params):
    """Wrapper function for backtesting"""
    try:
        conf_threshold = params.get('confidence_threshold', 0.60)
        lookback = params.get('lookback_days', 60)
        max_pos_size = params.get('max_position_size', 0.20)
        
        # Load historical data
        loader = HistoricalDataLoader(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        historical_data = loader.load_price_data()
        
        if historical_data.empty:
            return {'total_return_pct': -999, 'sharpe_ratio': -999, 'max_drawdown_pct': -999}
        
        # Generate predictions
        engine = BacktestPredictionEngine(
            model_type=model_type,
            confidence_threshold=conf_threshold
        )
        predictions = engine.walk_forward_backtest(
            data=historical_data,
            start_date=start_date,
            end_date=end_date,
            prediction_frequency='daily',
            lookback_days=lookback
        )
        
        if predictions.empty:
            return {'total_return_pct': -999, 'sharpe_ratio': -999, 'max_drawdown_pct': -999}
        
        # Simulate trading
        simulator = TradingSimulator(
            initial_capital=initial_capital,
            commission_rate=0.001,
            slippage_rate=0.0005,
            max_position_size=max_pos_size
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
        
        # Calculate performance
        metrics = simulator.calculate_performance_metrics()
        return metrics
    except Exception as e:
        print(f"Error in backtest: {e}")
        return {'total_return_pct': -999, 'sharpe_ratio': -999, 'max_drawdown_pct': -999}

# Use minimal parameter grid for quick test
test_grid = {
    'confidence_threshold': [0.60, 0.65],  # 2 values
    'lookback_days': [45, 60],             # 2 values
    'max_position_size': [0.15, 0.20]      # 2 values
}
# Total: 2 x 2 x 2 = 8 combinations

print("Parameter Grid (Quick Test):")
for param, values in test_grid.items():
    print(f"  {param}: {values}")
print(f"  Total combinations: {len(test_grid['confidence_threshold']) * len(test_grid['lookback_days']) * len(test_grid['max_position_size'])}")
print()

# Create optimizer
print("Creating optimizer...")
optimizer = ParameterOptimizer(
    backtest_function=backtest_wrapper,
    parameter_grid=test_grid,
    optimization_metric='total_return_pct',
    train_test_split=0.75
)
print("✓ Optimizer created")
print()

# Run random search (faster than grid search for testing)
print("Running Random Search (5 iterations)...")
print("-"*70)
best_params, results_df = optimizer.random_search(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date,
    n_iterations=5,  # Quick test with just 5 iterations
    model_type=model_type,
    initial_capital=initial_capital
)
print("-"*70)
print()

# Display results
print("="*70)
print("OPTIMIZATION RESULTS")
print("="*70)
print()

print("Best Parameters Found:")
for param, value in best_params.items():
    print(f"  {param}: {value}")
print()

# Generate summary report
summary = optimizer.generate_summary_report()

print("Summary Statistics:")
print(f"  Configurations tested: {summary['total_configurations_tested']}")
print(f"  Average train return: {summary['avg_train_return']:.2f}%")
print(f"  Average test return: {summary['avg_test_return']:.2f}%")
print(f"  Best train return: {summary['best_train_return']:.2f}%")
print(f"  Best test return: {summary['best_test_return']:.2f}%")
print(f"  Average overfit score: {summary['avg_overfit_score']:.2f}")
print(f"  Low overfit configs: {summary['configurations_with_low_overfit']}")
print()

print("Top 3 Configurations:")
top_configs = summary['top_10_configs'][:3]
for i, config in enumerate(top_configs, 1):
    print(f"\n  #{i}:")
    print(f"    Parameters: {config['parameters']}")
    print(f"    Train Return: {config['train_metrics']['total_return_pct']:.2f}%")
    print(f"    Test Return: {config['test_metrics']['total_return_pct']:.2f}%")
    print(f"    Overfit Score: {config['overfit_score']:.2f}")

print()
print("="*70)
print("✓ PARAMETER OPTIMIZATION TEST COMPLETED SUCCESSFULLY!")
print("="*70)
