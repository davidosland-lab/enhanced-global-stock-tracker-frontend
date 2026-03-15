# Manual Paper Trading Platform - Complete Guide

## Overview

**Full control over your paper trading** - YOU choose the stocks, quantities, and timing.

- ✅ Real-time stock prices via Yahoo Finance
- ✅ Live dashboard at http://localhost:5000
- ✅ Simple Python commands
- ✅ No auto-trading - manual control only
- ✅ Risk-free paper trading

---

## Quick Start (Windows)

### Method 1: One-Click Starter (Recommended)

1. **Download** `START_MANUAL_TRADING.bat` from:
   ```
   https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
   Branch: market-timing-critical-fix
   Path: working_directory/START_MANUAL_TRADING.bat
   ```

2. **Copy** to your `finbert_v4.4.4` folder:
   ```
   C:\Users\david\AATelS\finbert_v4.4.4\
   ```

3. **Double-click** `START_MANUAL_TRADING.bat`

4. **Wait** for the Python console to appear

5. **Start trading** using the commands below

---

### Method 2: Manual Setup

```bash
cd C:\Users\david\AATelS\finbert_v4.4.4

# Download required files
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py' -OutFile 'manual_paper_trading.py'"

# Install dependencies
pip install flask flask-cors yfinance pandas numpy

# Start
python manual_paper_trading.py
```

---

## Trading Commands

### Buy Shares

```python
>>> buy('AAPL', 100)
✅ Bought 100 shares of AAPL @ $187.45
   Total cost: $18,745.00
   Remaining cash: $81,255.00
```

**Syntax:** `buy('SYMBOL', quantity)`

**Examples:**
```python
buy('NVDA', 50)    # Buy 50 shares of NVIDIA
buy('TSLA', 25)    # Buy 25 shares of Tesla
buy('MSFT', 75)    # Buy 75 shares of Microsoft
buy('AAPL', 100)   # Buy 100 shares of Apple
```

---

### Sell Shares

```python
>>> sell('AAPL')
✅ Sold 100 shares of AAPL @ $192.30
   P&L: +$485.00 (+2.59%)
   New cash balance: $100,485.00
```

**Syntax:** `sell('SYMBOL')`

**Examples:**
```python
sell('NVDA')    # Sell all NVIDIA shares
sell('TSLA')    # Sell all Tesla shares
sell('MSFT')    # Sell all Microsoft shares
```

---

### Check Portfolio Status

```python
>>> status()

======================================================================
PORTFOLIO STATUS
======================================================================
Total Value:    $      105,250.00
Cash:           $       25,500.00
Invested:       $       79,750.00
Total Return:            +5.25%

Open Positions:                 3
Total Trades:                  12
Win Rate:                    75.0%
Total P&L:      $       +5,250.00
Max Drawdown:               -2.50%
======================================================================
```

**Syntax:** `status()`

---

### View Open Positions

```python
>>> positions()

======================================================================
OPEN POSITIONS
======================================================================
Symbol   Shares   Entry $      Current $    P&L         
----------------------------------------------------------------------
NVDA     50       $425.30      $445.80      +$1,025.00 (+4.82%)
TSLA     25       $245.60      $238.90      -$167.50 (-2.73%)
MSFT     75       $375.20      $382.50      +$547.50 (+1.95%)
======================================================================
```

**Syntax:** `positions()`

---

## Complete Trading Example

```python
# Start with $100,000

>>> status()
# Shows: Cash: $100,000.00, Open Positions: 0

>>> buy('AAPL', 100)
✅ Bought 100 shares of AAPL @ $187.45
   Total cost: $18,745.00
   Remaining cash: $81,255.00

>>> buy('NVDA', 50)
✅ Bought 50 shares of NVDA @ $425.30
   Total cost: $21,265.00
   Remaining cash: $59,990.00

>>> positions()
# Shows both positions with current P&L

>>> sell('AAPL')
✅ Sold 100 shares of AAPL @ $192.30
   P&L: +$485.00 (+2.59%)
   New cash balance: $78,720.00

>>> status()
# Shows updated portfolio with realized gains
```

---

## Dashboard Features

**Open in browser:** http://localhost:5000

### Real-Time Monitoring:
- 📊 Portfolio value and returns
- 📈 Open positions with live P&L
- 💰 Cash balance
- 🎯 Win rate and trade statistics
- 📉 Performance charts
- ⚠️ Trade alerts and activity log

### Updates Automatically:
- Position values update in real-time
- Charts refresh every 30 seconds
- New trades appear instantly

---

## How It Works

### 1. Real-Time Prices
- Fetches current market prices via Yahoo Finance
- Uses live data for buy/sell transactions
- Updates position values in real-time

### 2. Position Management
- Tracks entry price, shares, and current value
- Calculates P&L automatically
- Records all trades with timestamps

### 3. Risk Management
- Validates sufficient capital before buying
- Prevents over-leveraging
- Tracks max drawdown

### 4. Dashboard Integration
- All trades sync to dashboard instantly
- API endpoints provide real-time data
- Charts visualize performance

---

## Common Use Cases

### Day Trading Practice
```python
# Quick trades on volatile stocks
buy('TSLA', 25)
# Wait for price movement
sell('TSLA')
```

### Position Sizing Test
```python
# Test different position sizes
buy('AAPL', 50)   # Small position
buy('NVDA', 100)  # Medium position
buy('MSFT', 150)  # Large position
```

### Portfolio Building
```python
# Build diversified portfolio
buy('AAPL', 75)   # Tech
buy('JPM', 100)   # Finance
buy('JNJ', 60)    # Healthcare
buy('XOM', 80)    # Energy
status()          # Check allocation
```

### Strategy Testing
```python
# Test entry/exit strategies
buy('NVDA', 50)
positions()       # Monitor performance
sell('NVDA')      # Exit when satisfied
status()          # Review results
```

---

## File Requirements

### Required Files:
1. **unified_trading_platform.py** (29 KB)
   - Core trading engine
   - Dashboard server
   - Position tracking

2. **manual_paper_trading.py** (7 KB)
   - Manual trading interface
   - Command handlers
   - Real-time price fetching

3. **templates/dashboard.html**
   - Dashboard UI
   - Charts and visualizations

4. **static/css/dashboard.css**
   - Dashboard styling

### Download Location:
```
https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
Branch: market-timing-critical-fix
Path: working_directory/
```

---

## Dependencies

```bash
pip install flask flask-cors yfinance pandas numpy
```

### What Each Does:
- **flask** - Web dashboard server
- **flask-cors** - API access for dashboard
- **yfinance** - Real-time stock prices from Yahoo Finance
- **pandas** - Data handling and analysis
- **numpy** - Numerical calculations

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
pip install flask flask-cors
```

### Error: "ModuleNotFoundError: No module named 'yfinance'"
**Solution:**
```bash
pip install yfinance
```

### Error: "Could not fetch price for AAPL"
**Solutions:**
- Check internet connection
- Verify stock symbol is correct
- Try again (Yahoo Finance may be temporarily down)
- Use manual price: `buy('AAPL', 100, 187.45)`

### Error: "Insufficient capital!"
**Solution:**
- Check available cash: `status()`
- Sell existing positions: `sell('SYMBOL')`
- Reduce share quantity

### Dashboard shows "No positions"
**Solution:**
- Make sure you've bought shares: `buy('AAPL', 100)`
- Hard refresh dashboard: Ctrl+F5
- Check console for errors

### Console encoding errors (emojis not showing)
**Solution:**
```bash
set PYTHONIOENCODING=utf-8
python manual_paper_trading.py
```
Or use `START_MANUAL_TRADING.bat` which handles this automatically.

---

## Advanced Features

### Manual Price Override
If Yahoo Finance is down, specify price manually:
```python
buy('AAPL', 100, 187.45)  # Buy at $187.45
sell('AAPL', 192.30)      # Sell at $192.30
```

### View Trade History
Access via dashboard:
```
http://localhost:5000/api/trades
```

### Check Portfolio JSON
```
http://localhost:5000/api/summary
```

### Stop/Start Dashboard
```python
# Dashboard runs automatically
# To stop: Ctrl+C in console
# To restart: Run START_MANUAL_TRADING.bat again
```

---

## Tips & Best Practices

### 1. Start Small
```python
# Begin with smaller positions
buy('AAPL', 25)  # Instead of 100
```

### 2. Check Status Frequently
```python
status()      # Before and after trades
positions()   # Monitor P&L
```

### 3. Use Dashboard for Analysis
- Open http://localhost:5000 in browser
- Monitor multiple positions visually
- Review performance charts

### 4. Practice Discipline
```python
# Set mental stop-losses
# If position is down 5%, consider exiting
positions()  # Check current losses
sell('TSLA') # Cut losses if needed
```

### 5. Keep Records
- Dashboard logs all trades automatically
- Review trade history for learning
- Analyze win rate and P&L patterns

---

## Comparison: Manual vs Unified Platform

| Feature | Manual Trading | Unified Platform |
|---------|---------------|------------------|
| **Control** | Full control | Automated |
| **Stock Selection** | You choose | Auto-scanned |
| **Timing** | You decide | Every 5 minutes |
| **Quantity** | You specify | Position size % |
| **Learning** | Hands-on practice | Observe strategies |
| **Best For** | Practice, testing | Automated backtesting |

---

## Support & Documentation

### Files Created:
- `START_MANUAL_TRADING.bat` - One-click starter
- `manual_paper_trading.py` - Trading interface
- `MANUAL_TRADING_GUIDE.md` - This guide

### GitHub Repository:
```
https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
Branch: market-timing-critical-fix
```

### Previous Guides:
- `UNIFIED_PLATFORM_GUIDE.md` - Unified platform docs
- `BAT_FILES_README.md` - Batch file documentation
- `START_DASHBOARD_GUIDE.md` - Dashboard setup

---

## Exit Instructions

To stop the platform:
1. Press **Ctrl+C** in the Python console
2. Type `exit()` or close the window
3. Dashboard will stop automatically

---

## Quick Reference Card

```
COMMANDS:
  buy('SYMBOL', qty)  - Buy shares
  sell('SYMBOL')      - Sell shares
  status()            - Portfolio summary
  positions()         - Open positions

DASHBOARD:
  http://localhost:5000

START:
  Double-click START_MANUAL_TRADING.bat
  
STOP:
  Ctrl+C in console
```

---

**🎯 You now have complete control over your paper trading!**

Start with `status()`, buy your first position with `buy('AAPL', 50)`, and watch the dashboard at http://localhost:5000.

Happy Trading! 📈
