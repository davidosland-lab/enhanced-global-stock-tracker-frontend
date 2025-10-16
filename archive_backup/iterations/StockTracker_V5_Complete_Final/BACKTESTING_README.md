# Backtesting Module - Complete Documentation

## Overview
The backtesting module allows you to test trading strategies on historical data with a simulated $100,000 starting capital. It provides comprehensive performance metrics and visual analysis tools.

## Features

### 1. Trading Strategies

#### Moving Average Crossover
- **Logic**: Buy when 20-day SMA crosses above 50-day SMA (Golden Cross)
- **Sell Signal**: When 20-day SMA crosses below 50-day SMA (Death Cross)
- **Best For**: Trending markets
- **Risk Level**: Medium

#### RSI (Relative Strength Index)
- **Buy Signal**: RSI < 30 (Oversold)
- **Sell Signal**: RSI > 70 (Overbought)
- **Best For**: Range-bound markets
- **Risk Level**: Low-Medium

#### MACD (Moving Average Convergence Divergence)
- **Buy Signal**: MACD histogram turns positive
- **Sell Signal**: MACD histogram turns negative
- **Best For**: Momentum trading
- **Risk Level**: Medium

#### Mean Reversion
- **Buy Signal**: Price drops 3% in a day
- **Sell Signal**: Price rises 3% in a day
- **Best For**: Volatile stocks
- **Risk Level**: High

#### Breakout Strategy
- **Buy Signal**: Price breaks above average range by 50%
- **Sell Signal**: Price falls below 20-day SMA by 2%
- **Best For**: High volatility periods
- **Risk Level**: High

### 2. Configuration Parameters

#### Starting Capital
- Default: $100,000
- Range: $1,000 - $10,000,000
- Used to calculate position sizes and returns

#### Timeframes
- **1 Week**: Quick strategy testing
- **1 Month**: Short-term validation
- **3 Months**: Quarterly performance
- **6 Months**: Semi-annual testing
- **1 Year**: Annual performance
- **2 Years**: Long-term validation

#### Position Sizing
- **10%**: Conservative (low risk)
- **25%**: Moderate
- **50%**: Aggressive
- **75%**: Very Aggressive
- **100%**: All-in (highest risk)

#### Risk Management
- **Stop Loss**: 1-10% (protects downside)
- **Take Profit**: 1-20% (locks in gains)
- **Commission**: $5 per trade (realistic costs)

### 3. Performance Metrics

#### Primary Metrics
- **Final Capital**: Ending portfolio value
- **Total Return**: Percentage gain/loss
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
  - < 0: Poor performance
  - 0-1: Acceptable
  - 1-2: Good
  - > 2: Excellent

#### Trade Statistics
- **Total Trades**: Number of buy/sell operations
- **Winning Trades**: Profitable positions closed
- **Losing Trades**: Loss-making positions closed
- **Max Drawdown**: Largest peak-to-trough decline

#### Average Performance
- **Avg Profit**: Mean profit per trade
- **Avg Win**: Mean profit on winning trades
- **Avg Loss**: Mean loss on losing trades

### 4. Visual Analytics

#### Portfolio Value Chart
- Shows capital growth over time
- Green line indicates portfolio value
- Helps identify drawdown periods

#### Strategy Comparison
- Bar chart comparing multiple strategies
- Shows relative performance
- Maximum 4 strategies for clarity

#### Trade History Table
- Date of each trade
- Buy/Sell indicators
- Price and quantity
- Profit/Loss per trade

## Usage Guide

### Step 1: Prepare Your Model
1. Go to Training tab
2. Enter stock symbol (e.g., AAPL)
3. Select model type (Random Forest recommended)
4. Train model (wait for completion)

### Step 2: Configure Backtest
1. Switch to Backtest tab
2. Select trained model
3. Choose strategy
4. Set timeframe
5. Adjust risk parameters

### Step 3: Run Backtest
1. Click "Run Backtest"
2. Wait for analysis (10-30 seconds)
3. Review performance metrics
4. Check portfolio chart

### Step 4: Compare Strategies
1. Run multiple backtests
2. Different strategies appear in comparison chart
3. Identify best performer
4. Note market conditions

## Best Practices

### For Beginners
1. Start with 1-month timeframe
2. Use 25% position sizing
3. Set 5% stop loss
4. Try Moving Average strategy first

### For Advanced Users
1. Test all strategies
2. Use 1-2 year timeframes
3. Adjust parameters based on volatility
4. Compare multiple symbols

### Risk Management
1. Never skip stop losses
2. Include commission costs
3. Test in different market conditions
4. Don't over-optimize

## Interpreting Results

### Good Performance Indicators
- Positive total return
- Win rate > 50%
- Sharpe ratio > 1
- Low max drawdown (< 20%)
- Consistent profits

### Warning Signs
- Negative returns
- Win rate < 40%
- Sharpe ratio < 0
- High drawdown (> 30%)
- Few trades (< 10)

## Technical Details

### Data Sources
- **Yahoo Finance**: Real-time and historical prices
- **FinBERT**: Sentiment analysis
- **Technical Indicators**: Calculated in real-time

### Calculation Methods
- **SMA**: Simple moving average
- **EMA**: Exponential moving average
- **RSI**: 14-period relative strength
- **MACD**: 12/26/9 standard settings

### Limitations
1. Historical data may be limited for new stocks
2. Does not account for:
   - Slippage in real trading
   - Market impact of large orders
   - Overnight gaps
   - Dividends/splits (partially handled)

## Troubleshooting

### No Results Showing
- Check if model is trained
- Verify stock has enough history
- Ensure services are running

### Unexpected Results
- Verify data quality
- Check for data gaps
- Review strategy parameters
- Consider market conditions

### Performance Issues
- Reduce timeframe
- Use cached data
- Close other applications
- Check system resources

## Advanced Features

### Custom Strategy Development
To add your own strategy, edit the `getSignal` function in ml_unified.html:

```javascript
case 'my_strategy':
    // Your custom logic
    if (myCondition) {
        return 'BUY';
    } else if (myOtherCondition) {
        return 'SELL';
    }
    break;
```

### Batch Testing
Use the browser console to test all strategies:
```javascript
compareStrategies();
```

### Export Results
Right-click on charts to save images
Trade history can be copied from the table

## FAQ

**Q: Why does my backtest show no trades?**
A: The strategy conditions were never met. Try a different strategy or timeframe.

**Q: How accurate is backtesting?**
A: Backtesting shows historical performance. Past results don't guarantee future returns.

**Q: Can I test options or futures?**
A: Currently supports stock trading only.

**Q: What's the best strategy?**
A: It depends on market conditions, stock behavior, and risk tolerance. Test multiple strategies.

**Q: How is commission calculated?**
A: $5 per trade (buy or sell), deducted from capital.

## Support
- Logs are in the `logs/` directory
- Models saved in `model_checkpoints/`
- Historical data cached in `historical_data/`

---
Version 5.0 - With ML Integration & FinBERT Sentiment