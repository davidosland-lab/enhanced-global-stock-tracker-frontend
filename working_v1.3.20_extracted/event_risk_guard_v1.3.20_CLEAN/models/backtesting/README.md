# FinBERT v4.0 - Backtesting Framework

A comprehensive backtesting framework for testing FinBERT, LSTM, and ensemble prediction models with realistic trading conditions.

## 📁 Directory Structure

```
models/backtesting/
├── __init__.py                 # Package initialization
├── cache_manager.py            # SQLite cache for historical data
├── data_validator.py           # Data quality validation
├── data_loader.py              # Historical data loading
├── prediction_engine.py        # Walk-forward prediction engine
├── trading_simulator.py        # Trading simulation with costs
├── example_backtest.py         # Integration examples
└── README.md                   # This file
```

## 🎯 Three-Phase Architecture

### Phase 1: Foundation (Data Loading & Caching)
- **HistoricalDataLoader**: Fetches stock data from Yahoo Finance
- **CacheManager**: SQLite-based caching to minimize API calls
- **DataValidator**: Quality checks and anomaly detection

### Phase 2: Prediction Engine
- **BacktestPredictionEngine**: Generates predictions with walk-forward validation
- **CRITICAL**: No look-ahead bias - only uses data available before prediction time
- Supports three models: FinBERT, LSTM, Ensemble

### Phase 3: Trading Simulator
- **TradingSimulator**: Realistic trading simulation
- Commission modeling (default 0.1%)
- Slippage modeling (default 0.05%)
- Confidence-based position sizing (5-20% of capital)
- Comprehensive performance metrics

## 🚀 Quick Start

### Basic Usage

```python
from data_loader import HistoricalDataLoader
from prediction_engine import BacktestPredictionEngine
from trading_simulator import TradingSimulator

# 1. Load historical data
loader = HistoricalDataLoader(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    use_cache=True
)
data = loader.load_price_data()

# 2. Generate predictions
engine = BacktestPredictionEngine(model_type='ensemble')
predictions = engine.walk_forward_backtest(
    data=data,
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# 3. Simulate trading
simulator = TradingSimulator(initial_capital=10000)
for _, pred in predictions.iterrows():
    simulator.execute_signal(
        timestamp=pred['timestamp'],
        signal=pred['prediction'],
        price=pred['actual_price'],
        confidence=pred['confidence']
    )

# 4. Get performance metrics
metrics = simulator.calculate_performance_metrics()
print(f"Total Return: {metrics['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
```

### Using the Example Script

```bash
cd models/backtesting
python example_backtest.py
```

This will run three examples:
1. Single model backtest (AAPL, Ensemble)
2. Model comparison (FinBERT vs LSTM vs Ensemble)
3. Australian stock backtest (CBA.AX)

## 📊 Performance Metrics

The framework calculates comprehensive performance metrics:

### Returns
- Total Return (%)
- Initial/Final Capital
- Daily Returns

### Trade Statistics
- Total Trades
- Winning/Losing Trades
- Win Rate (%)
- Average Win/Loss
- Profit Factor

### Risk Metrics
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Peak-to-trough decline

### Cost Analysis
- Total Commission Paid
- Average Holding Time
- Slippage Impact

## 🔍 Model Types

### 1. FinBERT Model
- Uses price momentum and volatility as sentiment proxy
- 5-day and 20-day momentum analysis
- Trend strength calculation
- Volatility adjustment

### 2. LSTM Model
- Price sequence pattern matching
- Technical indicator analysis
- Moving average crossovers
- Momentum signals

### 3. Ensemble Model (Recommended)
- Combines FinBERT (60%) + LSTM (40%)
- Weighted voting system
- More robust predictions
- Better risk management

## ⚙️ Configuration Options

### Data Loader
```python
loader = HistoricalDataLoader(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    use_cache=True,          # Enable caching
    validate_data=True       # Enable validation
)
```

### Prediction Engine
```python
engine = BacktestPredictionEngine(
    model_type='ensemble',     # 'finbert', 'lstm', or 'ensemble'
    confidence_threshold=0.6   # Minimum confidence for signals
)
```

### Trading Simulator
```python
simulator = TradingSimulator(
    initial_capital=10000.0,
    commission_rate=0.001,     # 0.1%
    slippage_rate=0.0005,      # 0.05%
    max_position_size=0.20     # 20% max
)
```

## 📈 Walk-Forward Validation

The framework implements **strict walk-forward validation** to prevent look-ahead bias:

1. **Time-Based Splitting**: Data is split by time, not randomly
2. **No Future Data**: Each prediction uses ONLY data available before that timestamp
3. **Rolling Window**: Uses configurable lookback period (default: 60 days)
4. **Realistic Simulation**: Predictions are made as they would be in real-time

```python
predictions = engine.walk_forward_backtest(
    data=historical_data,
    start_date='2023-01-01',
    end_date='2024-01-01',
    prediction_frequency='daily',  # 'daily', 'weekly', or 'monthly'
    lookback_days=60               # Days of history for each prediction
)
```

## 💾 Caching System

The cache manager uses SQLite to store historical data:

```python
from cache_manager import CacheManager

cache = CacheManager(cache_dir='cache')

# Get cache statistics
stats = cache.get_cache_stats()
print(f"Total records: {stats['total_records']}")
print(f"Unique symbols: {stats['unique_symbols']}")
print(f"Database size: {stats['database_size_mb']:.2f} MB")

# Invalidate cache (force refresh)
cache.invalidate_cache(symbol='AAPL')  # Specific symbol
cache.invalidate_cache()               # All data
```

## 🎨 Position Sizing Strategy

The simulator uses **confidence-based position sizing**:

| Confidence | Position Size | Description |
|------------|---------------|-------------|
| 50-60%     | 5% of capital | Low confidence |
| 60-80%     | 5-15% of capital | Medium confidence |
| 80-100%    | 15-20% of capital | High confidence |

This approach:
- Allocates more capital to high-confidence signals
- Limits exposure to uncertain signals
- Improves risk-adjusted returns

## 📊 Output Files

The example script generates three CSV files:

1. **backtest_predictions.csv**: All predictions with confidence scores
2. **backtest_trades.csv**: Complete trade history with P&L
3. **backtest_equity_curve.csv**: Daily equity values

```python
# Access data programmatically
predictions_df = result['predictions']
trades_df = result['trades']
equity_df = result['equity_curve']
```

## 🧪 Model Comparison

Compare all three models side-by-side:

```python
from example_backtest import compare_models

results = compare_models(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    initial_capital=10000.0
)

# Results include comparison table:
#                  finbert    lstm    ensemble
# Total Return %     12.5%   10.3%      15.2%
# Win Rate %         58.0%   55.0%      60.5%
# Sharpe Ratio        1.2     1.0        1.4
# Max Drawdown %    -8.5%   -9.2%      -7.8%
```

## 🔧 Advanced Features

### Technical Indicators

Load data with built-in technical indicators:

```python
data = loader.load_with_indicators(interval='1d')

# Available indicators:
# - SMA (20, 50, 200)
# - EMA (12, 26)
# - MACD
# - RSI
# - Bollinger Bands
# - Volume indicators
# - Volatility
```

### Multiple Symbols

Load data for multiple symbols at once:

```python
from data_loader import HistoricalDataLoader

symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
data_dict = HistoricalDataLoader.load_multiple_symbols(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2024-01-01'
)

for symbol, data in data_dict.items():
    print(f"{symbol}: {len(data)} records")
```

### Data Validation

Validate data quality before backtesting:

```python
from data_validator import DataValidator

validator = DataValidator(outlier_threshold=3.0)
validation_result = validator.validate_data_quality(data, 'AAPL')

if validation_result['is_valid']:
    print("Data quality: PASSED")
else:
    print(f"Issues: {validation_result['issues']}")
    print(f"Warnings: {validation_result['warnings']}")
```

## 🚨 Important Notes

### No Look-Ahead Bias
The prediction engine **guarantees** no look-ahead bias by:
- Only using data with timestamps < prediction time
- Slicing historical data correctly for each prediction
- Implementing strict time-based validation

### Commission & Slippage
Realistic costs are applied to all trades:
- **Commission**: 0.1% (adjustable) on entry and exit
- **Slippage**: 0.05% (adjustable) simulates market impact

### Historical News Limitation
Since historical news is not available:
- FinBERT model uses **price momentum as sentiment proxy**
- Combines short-term and medium-term momentum
- Adjusts for volatility
- Still provides realistic sentiment-like signals

## 📝 Logging

The framework includes comprehensive logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs include:
# - Data loading progress
# - Prediction generation status
# - Trade executions
# - Performance metrics
```

## 🔮 Future Enhancements (Phases 4-6)

### Phase 4: Analytics & Metrics
- Model comparison tools
- Performance visualization
- Statistical analysis

### Phase 5: UI Integration
- Web-based backtesting interface
- Interactive charts
- Real-time monitoring

### Phase 6: Optimization
- Parameter optimization
- Strategy refinement
- Performance tuning

## 📚 Dependencies

Required packages:
```
pandas
numpy
yfinance
sqlite3 (built-in)
logging (built-in)
dataclasses (built-in)
```

## 🤝 Contributing

This backtesting framework is part of FinBERT v4.0. For questions or suggestions, refer to the main project documentation.

## 📄 License

Same license as FinBERT v4.0 project.

---

**Author**: FinBERT v4.0 Development Team  
**Date**: October 2024  
**Version**: 1.0.0
