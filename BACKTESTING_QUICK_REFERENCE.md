# FinBERT v4.0 - Backtesting Framework Quick Reference

## 🚀 One-Minute Setup

```bash
cd /home/user/webapp/models/backtesting
python example_backtest.py
```

## 📁 Files Overview

| File | Size | Purpose |
|------|------|---------|
| `__init__.py` | 1 KB | Package initialization |
| `cache_manager.py` | 9 KB | SQLite caching system |
| `data_validator.py` | 10 KB | Data quality checks |
| `data_loader.py` | 10 KB | Historical data loading |
| `prediction_engine.py` | 19 KB | Walk-forward predictions |
| `trading_simulator.py` | 17 KB | Trading simulation |
| `example_backtest.py` | 11 KB | Integration examples |
| `README.md` | 10 KB | Full documentation |

**Total**: 2,593 lines of code, ~87 KB

## 🎯 Three-Phase Architecture

### Phase 1: Foundation
```python
from data_loader import HistoricalDataLoader

loader = HistoricalDataLoader('AAPL', '2023-01-01', '2024-01-01')
data = loader.load_price_data()
```

### Phase 2: Predictions
```python
from prediction_engine import BacktestPredictionEngine

engine = BacktestPredictionEngine(model_type='ensemble')
predictions = engine.walk_forward_backtest(data, '2023-01-01', '2024-01-01')
```

### Phase 3: Trading
```python
from trading_simulator import TradingSimulator

simulator = TradingSimulator(initial_capital=10000)
for _, pred in predictions.iterrows():
    simulator.execute_signal(
        pred['timestamp'], pred['prediction'], 
        pred['actual_price'], pred['confidence']
    )
metrics = simulator.calculate_performance_metrics()
```

## 📊 Key Metrics

- **Total Return** - Overall profit/loss percentage
- **Sharpe Ratio** - Risk-adjusted return (>1 is good, >2 is excellent)
- **Sortino Ratio** - Downside risk-adjusted return
- **Max Drawdown** - Worst peak-to-trough decline
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Gross wins / gross losses (>1.5 is good)

## 🎨 Model Types

| Model | Description | Best For |
|-------|-------------|----------|
| `finbert` | Sentiment-based (momentum proxy) | Trending markets |
| `lstm` | Pattern recognition | Range-bound markets |
| `ensemble` | Combined (60/40 split) | **Recommended - Most robust** |

## ⚙️ Configuration

### Data Loader
```python
loader = HistoricalDataLoader(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    use_cache=True,        # ← Speed boost
    validate_data=True     # ← Quality assurance
)
```

### Prediction Engine
```python
engine = BacktestPredictionEngine(
    model_type='ensemble',      # finbert/lstm/ensemble
    confidence_threshold=0.6    # 0-1 scale
)
```

### Trading Simulator
```python
simulator = TradingSimulator(
    initial_capital=10000.0,
    commission_rate=0.001,      # 0.1%
    slippage_rate=0.0005,       # 0.05%
    max_position_size=0.20      # 20% max
)
```

## 🔍 Position Sizing

| Confidence | Position Size | Example ($10k capital) |
|------------|---------------|------------------------|
| 50-60%     | 5%            | $500 |
| 60-80%     | 5-15%         | $500 - $1,500 |
| 80-100%    | 15-20%        | $1,500 - $2,000 |

## 📈 Example Output

```
BACKTEST RESULTS
================================================================================

Capital:
  Initial: $10,000.00
  Final:   $11,523.50
  Return:  15.24%

Trades:
  Total:   42
  Winners: 26 (61.90%)
  Losers:  16
  Avg Win: $127.35
  Avg Loss: -$83.21
  Profit Factor: 1.89

Risk Metrics:
  Sharpe Ratio:  1.42
  Sortino Ratio: 1.98
  Max Drawdown:  -7.82%

Costs:
  Total Commission: $23.15
  Avg Hold Time:    5.3 days
```

## 🚨 Critical Features

### ✅ No Look-Ahead Bias
```python
# Each prediction uses ONLY data available BEFORE timestamp
available_data = historical_data[historical_data.index < timestamp]
```

### ✅ Realistic Costs
- Commission: 0.1% per trade (entry + exit)
- Slippage: 0.05% per trade
- Total cost per round-trip: ~0.3%

### ✅ Smart Caching
- First load: ~5-10 seconds (API call)
- Cached loads: ~0.5 seconds (SQLite)
- 90% completeness threshold

## 🔧 Common Tasks

### Run Single Backtest
```python
from example_backtest import run_complete_backtest

result = run_complete_backtest(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    model_type='ensemble',
    initial_capital=10000.0
)
```

### Compare All Models
```python
from example_backtest import compare_models

results = compare_models('AAPL', '2023-01-01', '2024-01-01')
```

### Export Results
```python
result['predictions'].to_csv('predictions.csv')
result['trades'].to_csv('trades.csv')
result['equity_curve'].to_csv('equity_curve.csv')
```

### Check Cache Stats
```python
from cache_manager import CacheManager

cache = CacheManager()
stats = cache.get_cache_stats()
print(f"Cached: {stats['total_records']} records")
print(f"Symbols: {stats['unique_symbols']}")
print(f"Size: {stats['database_size_mb']} MB")
```

### Invalidate Cache
```python
cache.invalidate_cache(symbol='AAPL')  # One symbol
cache.invalidate_cache()               # All data
```

## 📊 Output Files

The example script creates:
1. `backtest_predictions.csv` - All predictions with metadata
2. `backtest_trades.csv` - Complete trade history with P&L
3. `backtest_equity_curve.csv` - Daily equity values

## 🎯 Recommended Settings

### Conservative
```python
simulator = TradingSimulator(
    commission_rate=0.002,      # 0.2% (higher cost)
    slippage_rate=0.001,        # 0.1% (higher slippage)
    max_position_size=0.10      # 10% max (lower risk)
)
```

### Aggressive
```python
simulator = TradingSimulator(
    commission_rate=0.0005,     # 0.05% (lower cost)
    slippage_rate=0.0002,       # 0.02% (lower slippage)
    max_position_size=0.30      # 30% max (higher risk)
)
```

## 🐛 Troubleshooting

### "No data returned"
- Check symbol format (use '.AX' for Australian stocks)
- Verify dates are valid trading days
- Try `force_refresh=True`

### "Insufficient historical data"
- Increase lookback period
- Start backtest later in date range
- Ensure enough data before start_date

### "Cache miss"
- Normal on first load
- Cache builds automatically
- Check cache stats to verify

## 📚 Full Documentation

See `README.md` for:
- Complete API reference
- Advanced features
- Technical indicators
- Multi-symbol loading
- Data validation details

## 🎓 Learning Path

1. **Start**: Run `example_backtest.py` to see it in action
2. **Explore**: Try different symbols and date ranges
3. **Compare**: Test all three models side-by-side
4. **Optimize**: Adjust parameters and observe effects
5. **Integrate**: Use framework in your own projects

## 🔮 Future Phases (Not Yet Implemented)

- **Phase 4**: Analytics & visualization dashboard
- **Phase 5**: Web UI integration
- **Phase 6**: Parameter optimization

## ✅ Status

**All three requested phases are COMPLETE and ready for use.**

---

**Quick Help**: See `README.md` for full documentation  
**Examples**: Run `python example_backtest.py`  
**Version**: 1.0.0  
**Date**: October 31, 2024
