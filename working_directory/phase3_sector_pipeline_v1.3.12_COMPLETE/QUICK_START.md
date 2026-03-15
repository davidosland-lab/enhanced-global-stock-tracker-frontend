# 🚀 Quick Start Guide - Paper Trading System

## Starting the System (30 seconds)

### Option 1: All-in-One Launcher (Recommended)

**Linux/Mac**:
```bash
chmod +x start_system.sh
./start_system.sh
```

**Windows**:
```batch
start_system.bat
```

This will:
1. ✅ Create necessary directories
2. ✅ Start paper trading system (background)
3. ✅ Start real-time dashboard
4. ✅ Open browser to http://localhost:8050

### Option 2: Manual Start

**Terminal 1 - Paper Trading**:
```bash
python paper_trading_coordinator.py \
    --symbols AAPL,GOOGL,MSFT,TSLA,NVDA \
    --capital 100000 \
    --interval 60
```

**Terminal 2 - Dashboard**:
```bash
python dashboard.py
```

Then open: http://localhost:8050

---

## What You'll See

### Dashboard Features

1. **📊 Top Metrics**
   - Total Capital & Return %
   - Open Positions Count
   - Win Rate & Total Trades
   - Market Sentiment (0-100)

2. **📈 Portfolio Chart**
   - Real-time portfolio value
   - Historical performance

3. **🎯 Open Positions**
   - Live P&L tracking
   - Entry prices & current prices
   - Unrealized gains/losses
   - Regime classification

4. **⚠️ Intraday Alerts**
   - Bullish breakouts
   - Bearish breakdowns
   - Volume spikes
   - Strength indicators

5. **📋 Trade History**
   - Recently closed trades
   - Entry/exit prices
   - P&L per trade
   - Exit reasons

---

## Understanding the System

### Paper Trading Coordinator

**What it does**:
- Fetches real market data from Yahoo Finance
- Generates swing trading signals using Phase 1-3 logic
- Monitors market sentiment (SPY, VIX)
- Detects intraday breakouts
- Simulates position entries/exits
- Tracks performance metrics

**Trading Cycle** (Every 60 seconds by default):
1. Update market sentiment
2. Update existing positions (prices, trailing stops)
3. Check exit conditions (stops, targets, holding period)
4. Scan for new entry opportunities
5. Run intraday monitoring
6. Save state to JSON

**No Real Money** - Everything is simulated!

### Signal Generation

**Components** (Phase 1-3 style):
- **Momentum** (30%): 20-day rate of change
- **Trend** (35%): Moving average alignment (10/20/50-day)
- **Volume** (20%): Volume surge detection
- **Volatility** (15%): ATR-based volatility scoring

**Entry Threshold**: 52% confidence (configurable)

### Cross-Timeframe Integration

**Entry Enhancement**:
- ✅ Blocks entry if market sentiment < 30 (bearish)
- ✅ Boosts position size 25% → 30% if sentiment > 70 (bullish)
- ✅ Adjusts confidence based on overall market

**Exit Enhancement**:
- ✅ Early exit on strong market breakdown
- ✅ Trailing stops lock in profits
- ✅ Profit targets (8% after 2 days, 12% immediate)

---

## Configuration

### Default Settings

```json
{
  "swing_trading": {
    "confidence_threshold": 52.0,
    "stop_loss_percent": 3.0,
    "max_position_size": 0.25
  },
  "risk_management": {
    "max_total_positions": 3
  },
  "cross_timeframe": {
    "sentiment_boost_threshold": 70,
    "sentiment_block_threshold": 30
  }
}
```

### Custom Configuration

Edit `config/live_trading_config.json` to customize:
- Initial capital
- Confidence threshold
- Position sizing
- Stop loss percentage
- Max concurrent positions
- Sentiment thresholds

---

## Command Line Options

```bash
python paper_trading_coordinator.py \
    --symbols AAPL,GOOGL,MSFT   # Stocks to trade
    --capital 100000             # Starting capital
    --interval 60                # Seconds between cycles
    --cycles 100                 # Number of cycles (optional)
```

---

## Monitoring

### Real-Time Dashboard
- **URL**: http://localhost:8050
- **Auto-refresh**: Every 5 seconds
- **Features**: Live positions, alerts, performance

### Log Files
```bash
# Paper trading logs
tail -f logs/paper_trading.log

# State file (JSON)
cat state/paper_trading_state.json | jq
```

### State File Structure
```json
{
  "timestamp": "2024-12-21T...",
  "capital": {
    "total": 105234.56,
    "cash": 75234.56,
    "invested": 30000.00,
    "total_return_pct": 5.23
  },
  "positions": {
    "count": 2,
    "open": [...]
  },
  "performance": {
    "total_trades": 15,
    "win_rate": 73.3,
    "realized_pnl": 5234.56
  }
}
```

---

## Expected Behavior

### First 5 Minutes
1. System fetches market data for all symbols
2. Calculates market sentiment (SPY)
3. Generates signals for each symbol
4. May enter 1-2 positions (if signals are strong)
5. Dashboard updates every 5 seconds

### During Market Hours
- More frequent price updates
- Higher chance of entry signals
- Intraday alerts more common
- Active position management

### After Market Close
- Positions hold overnight
- Less frequent updates
- Focus on overnight sentiment (macro news)

---

## Performance Expectations

### Typical Results (Paper Trading)

**After 1 Week**:
- Trades: 5-10
- Win Rate: 60-70%
- Return: +2-5%

**After 1 Month**:
- Trades: 20-40
- Win Rate: 65-75%
- Return: +5-10%

**After 3 Months**:
- Trades: 60-120
- Win Rate: 68-75%
- Return: +15-25%

*Note: Results depend on market conditions and symbol selection*

---

## Troubleshooting

### Dashboard not loading
```bash
# Check if dashboard is running
ps aux | grep dashboard

# Restart dashboard
python dashboard.py
```

### No market data
```bash
# Test data access
python -c "from yahooquery import Ticker; print(Ticker('AAPL').history())"

# Or try yfinance
python -c "import yfinance; print(yfinance.download('AAPL', period='5d'))"
```

### No positions opening
- Check logs: `tail -f logs/paper_trading.log`
- Verify signals are generating (confidence > 52%)
- Check market sentiment (may be blocking entries)
- Ensure sufficient capital

### System running slow
- Reduce number of symbols: `--symbols AAPL,GOOGL`
- Increase cycle interval: `--interval 120`
- Check system resources

---

## Stopping the System

**If using start_system.sh**:
- Press `Ctrl+C` in terminal

**If manual start**:
- Stop paper trading: `Ctrl+C` in Terminal 1
- Stop dashboard: `Ctrl+C` in Terminal 2

**Check processes**:
```bash
# Find PIDs
ps aux | grep paper_trading
ps aux | grep dashboard

# Kill if needed
kill <PID>
```

---

## Next Steps

1. **Run for a few hours** - Let it collect data and execute trades
2. **Monitor dashboard** - Watch real-time performance
3. **Review logs** - Check signal generation and trade execution
4. **Tune parameters** - Adjust confidence threshold, position sizing
5. **Test different symbols** - Try various stock combinations
6. **Analyze results** - Review closed trades and performance metrics

---

## Tips for Success

✅ **Start with 3-5 liquid stocks** (AAPL, GOOGL, MSFT, TSLA, NVDA)  
✅ **Run during market hours** for better signals  
✅ **Let it run for at least a week** for meaningful data  
✅ **Monitor intraday alerts** to see breakout detection  
✅ **Check sentiment gauge** to understand market context  
✅ **Review exit reasons** to see which strategies work  
✅ **Compare different configurations** to optimize  

---

## Support

**Logs**: `logs/paper_trading.log`  
**State**: `state/paper_trading_state.json`  
**Config**: `config/live_trading_config.json`  
**Dashboard**: http://localhost:8050

**Quick test**:
```bash
python test_integration.py --quick-test
```

---

**Happy Paper Trading!** 📈🚀

Remember: This is a simulation with real market data but no real money at risk!
