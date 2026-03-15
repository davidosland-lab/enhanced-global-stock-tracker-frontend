# Real Historical Backtesting Module

**Location**: `core/backtesting/`  
**Source**: Copied from FinBERT v4.4.4 (original code untouched)  
**Version**: 1.0.0  
**Date**: February 28, 2026

---

## Overview

This module provides **real historical backtesting** using Yahoo Finance data, walk-forward validation, and multiple prediction models. It replaces the synthetic/random backtest with honest, actionable performance metrics.

---

## Key Features

✅ **Real Data** - Yahoo Finance historical prices (no synthetic/random data)  
✅ **Walk-Forward Validation** - No look-ahead bias, predictions use only past data  
✅ **Three Prediction Models**:
- LSTM-like (pattern recognition, trend continuation)
- Technical Analysis (RSI, MACD, Bollinger Bands, Moving Averages)
- Momentum (rate of change, trend strength, acceleration)
- Ensemble (weighted 40%/35%/25%)

✅ **Portfolio Management** - Multi-stock portfolios with allocation strategies  
✅ **Realistic Execution** - Commission (0.1%) and slippage (0.05%) modeling  
✅ **Comprehensive Metrics** - Sharpe, Sortino, drawdown, win rate, profit factor

---

## Quick Start

### Single Stock Backtest

```bash
cd unified_trading_system_v188_COMPLETE_PATCHED/core

python run_real_backtest.py \
    --symbol AAPL \
    --start 2024-02-27 \
    --end 2025-02-27 \
    --capital 100000 \
    --model ensemble \
    --confidence 0.48
```

### Portfolio Backtest (Multiple Stocks)

```bash
python run_real_backtest.py \
    --symbols AAPL,MSFT,GOOGL,CBA.AX,BHP.AX \
    --start 2024-02-27 \
    --end 2025-02-27 \
    --capital 100000 \
    --model ensemble \
    --confidence 0.48 \
    --allocation equal
```

### 30-Stock Portfolio (Preset)

```bash
python run_real_backtest.py \
    --preset 30stocks \
    --start 2024-02-27 \
    --end 2025-02-27 \
    --capital 100000
```

---

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--symbol` | Single stock ticker (e.g., AAPL) | - |
| `--symbols` | Multiple tickers, comma-separated | - |
| `--preset` | Stock preset (30stocks, us_tech, au_banks, uk_blue_chip) | - |
| `--start` | Start date (YYYY-MM-DD) | **Required** |
| `--end` | End date (YYYY-MM-DD) | **Required** |
| `--capital` | Initial capital | 100,000 |
| `--model` | Prediction model (lstm, technical, momentum, ensemble) | ensemble |
| `--confidence` | Confidence threshold (0-1) | 0.48 |
| `--allocation` | Portfolio allocation (equal, risk_parity, custom) | equal |
| `--output` | Output directory | backtest_results |

---

## Stock Presets

### `30stocks` (Global Diversified)
- **Australia (10)**: CBA.AX, BHP.AX, NAB.AX, WBC.AX, ANZ.AX, WES.AX, CSL.AX, RIO.AX, TLS.AX, WOW.AX
- **UK (10)**: BP.L, HSBA.L, SHEL.L, ULVR.L, AZN.L, GSK.L, DGE.L, VOD.L, BATS.L, RIO.L
- **US (10)**: AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, JNJ

### `us_tech` (US Technology)
AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA

### `au_banks` (Australian Banks)
CBA.AX, NAB.AX, WBC.AX, ANZ.AX

### `uk_blue_chip` (UK Blue Chips)
BP.L, HSBA.L, SHEL.L, ULVR.L, AZN.L

---

## Python API Usage

### Basic Backtest

```python
from core.backtesting import (
    HistoricalDataLoader,
    BacktestPredictionEngine,
    TradingSimulator
)

# Load real historical data
loader = HistoricalDataLoader(
    symbol='AAPL',
    start_date='2024-02-27',
    end_date='2025-02-27',
    use_cache=True
)
data = loader.load_price_data()

# Generate predictions
predictor = BacktestPredictionEngine(
    model_type='ensemble',
    confidence_threshold=0.48
)
predictions = predictor.walk_forward_backtest(
    data=data,
    start_date='2024-02-27',
    end_date='2025-02-27'
)

# Simulate trading
simulator = TradingSimulator(
    initial_capital=100000,
    commission_rate=0.001,
    max_position_size=0.25
)
performance = simulator.simulate_trades(predictions, data)

print(f"Total Return: {performance['total_return_pct']:.2f}%")
print(f"Win Rate: {performance['win_rate']:.2f}%")
```

### Portfolio Backtest

```python
from core.backtesting import PortfolioBacktester

backtester = PortfolioBacktester(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2024-02-27',
    end_date='2025-02-27',
    initial_capital=100000,
    model_type='ensemble',
    allocation_strategy='equal',
    confidence_threshold=0.48
)

results = backtester.run_backtest()
print(results['portfolio_metrics'])
```

---

## Output Files

Backtest results are saved to `backtest_results/` directory:

### Single Stock
- `backtest_{SYMBOL}_{TIMESTAMP}_predictions.csv` - All predictions with timestamps
- `backtest_{SYMBOL}_{TIMESTAMP}_performance.json` - Performance metrics

### Portfolio
- `portfolio_backtest_{TIMESTAMP}.json` - Full results including:
  - Portfolio metrics
  - Per-symbol performance
  - Correlation matrix
  - Diversification metrics
  - Target allocations

---

## Performance Metrics

### Basic Metrics
- **Total Return %** - Overall portfolio return
- **Total Trades** - Number of trades executed
- **Win Rate %** - Percentage of profitable trades
- **Profit Factor** - Gross profit / gross loss

### Risk Metrics
- **Sharpe Ratio** - Risk-adjusted return (annualized)
- **Sortino Ratio** - Downside risk-adjusted return
- **Max Drawdown %** - Largest peak-to-trough decline

### Trade Metrics
- **Average Win $** - Average profit per winning trade
- **Average Loss $** - Average loss per losing trade
- **Win/Loss Ratio** - Average win / average loss
- **Commission Paid** - Total transaction costs

### Portfolio Metrics (Multi-Stock)
- **Average Correlation** - Inter-stock correlation
- **Diversification Ratio** - Effective diversification
- **Effective Stocks** - Portfolio concentration measure
- **Per-Symbol Performance** - Individual stock contributions

---

## Module Structure

```
core/backtesting/
├── __init__.py                  # Module initialization
├── data_loader.py               # Yahoo Finance data fetching
├── prediction_engine.py         # Walk-forward prediction engine
├── backtest_engine.py           # Single-stock backtesting
├── portfolio_engine.py          # Multi-stock portfolio management
├── portfolio_backtester.py      # Complete portfolio backtesting
├── trading_simulator.py         # Trade execution simulation
├── cache_manager.py             # Data caching
├── data_validator.py            # Data quality validation
├── parameter_optimizer.py       # Parameter optimization
├── example_backtest.py          # Usage examples
└── quick_test.py                # Quick testing
```

---

## How It Works

### Walk-Forward Validation

```python
# CRITICAL: No look-ahead bias
available_data = historical_data[historical_data.index < timestamp]
```

For each prediction timestamp:
1. Use **only** data available before that timestamp
2. Generate prediction using 60-day lookback window
3. Execute trade at next available price
4. Move to next timestamp and repeat

This ensures predictions use only information available at trading time.

---

## Model Details

### 1. LSTM-like Model
- Pattern recognition in price sequences
- Trend continuation signals
- Moving average divergence
- Momentum indicators

### 2. Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving averages (SMA 20, 50, 200)

### 3. Momentum Model
- Short/medium/long-term momentum
- Rate of change (ROC)
- Trend strength (linear regression slope)
- Acceleration (momentum derivative)

### 4. Ensemble (Default)
Weighted combination:
- LSTM: 40%
- Technical: 35%
- Momentum: 25%

**Consensus Bonus**: When all three agree, confidence increases by 15%

---

## Configuration

### Confidence Threshold
```python
--confidence 0.48  # Default: 48% (matches unified system)
```
- Higher = fewer trades, higher quality signals
- Lower = more trades, more false positives
- Recommended: 0.45-0.55 for swing trading

### Commission & Slippage
```python
commission_rate = 0.001   # 0.1% per trade
slippage_rate = 0.0005    # 0.05% per trade
```
- Commission: Broker fees (typical 0.05-0.2%)
- Slippage: Price difference between signal and execution

### Position Sizing
```python
max_position_size = 0.25  # 25% max per stock
```
- Limits maximum capital allocation per position
- Prevents over-concentration

---

## Limitations

### What This Module Doesn't Have

1. **No Actual FinBERT Sentiment**
   - Uses technical indicators instead
   - Can be integrated later

2. **No Pre-Trained LSTM**
   - Uses LSTM-like pattern matching
   - Not a trained deep learning model

3. **No ML Exit Logic**
   - Doesn't include unified system's ML exit feature
   - Can be ported separately

4. **No Real-Time Support**
   - Historical backtesting only
   - Not for live trading

---

## Comparison: Synthetic vs Real Backtest

| Aspect | Synthetic Backtest | Real Backtest (This Module) |
|--------|-------------------|------------------------------|
| Data Source | 100% Random/Synthetic | Real Yahoo Finance |
| AI Models | None (random signals) | 3 Real Models |
| Look-Ahead Bias | N/A (random) | Properly Prevented |
| Execution Costs | Not Modeled | Commission + Slippage |
| Results Validity | ❌ Meaningless | ✅ Realistic & Actionable |

---

## Troubleshooting

### Error: "No data loaded for {symbol}"
- **Cause**: Symbol invalid or Yahoo Finance issue
- **Fix**: Verify symbol ticker, check internet connection

### Error: "Insufficient historical data"
- **Cause**: Date range too short (< 60 days)
- **Fix**: Use longer date range (minimum 90 days recommended)

### Warning: "Data validation failed"
- **Cause**: Missing prices, gaps in data
- **Effect**: May affect backtest accuracy
- **Fix**: Check data quality, consider different date range

### Error: "Failed to generate predictions"
- **Cause**: Insufficient data or calculation error
- **Fix**: Check logs for detailed error, verify data quality

---

## Best Practices

### 1. Use Adequate History
- Minimum: 90 days (60-day lookback + 30-day buffer)
- Recommended: 1 year for meaningful results
- Optimal: 2-3 years for statistical significance

### 2. Match Live Trading Config
- Use same confidence threshold (0.48 for unified system)
- Apply same position sizing rules
- Include realistic commission/slippage

### 3. Validate Results
- Compare to buy-and-hold benchmark
- Check win rate (expect 45-65% realistic)
- Verify profit factor (1.5-3.0 good, >5 suspicious)
- Review max drawdown (20-40% normal for aggressive)

### 4. Beware of Overfitting
- Don't optimize parameters on same data
- Use out-of-sample testing
- Validate on different time periods

---

## Next Steps

After running real backtest:

1. **Review Results**
   - Is system profitable?
   - What's the realistic win rate?
   - How much drawdown can you tolerate?

2. **Compare to Expectations**
   - Previous synthetic backtest: $100K → $10M (meaningless)
   - Real backtest: $100K → $??? (honest result)

3. **Decision Point**
   - **If profitable**: Proceed to paper trading
   - **If breakeven**: Refine parameters, test longer period
   - **If unprofitable**: Revisit strategy, consider improvements

4. **Paper Trading**
   - Run live paper trading for 2-4 weeks
   - Collect real-time performance data
   - Validate backtest predictions

5. **Live Deployment**
   - Start with small capital ($10-25K)
   - Use fixed position sizing
   - Monitor closely for first 20-30 trades

---

## Support

For issues or questions:
1. Check logs: `logs/real_backtest.log`
2. Review backtest results in `backtest_results/`
3. Refer to FinBERT v4.4.4 documentation
4. Check unified system documentation

---

## Version History

- **v1.0.0** (2026-02-28) - Initial release
  - Copied from FinBERT v4.4.4 backtesting module
  - Integrated into unified trading system
  - Added command-line runner script
  - Created documentation

---

**Ready to use!** Run your first real backtest:

```bash
python run_real_backtest.py --preset 30stocks --start 2024-02-27 --end 2025-02-27
```
