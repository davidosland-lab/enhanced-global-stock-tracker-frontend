# Integrated Manual Trading Platform - Multi-Module Setup

## Overview

This guide explains how to run the **Manual Trading Platform on PORT 5004** alongside other modules in your project without port conflicts.

---

## Port Allocation Strategy

### Default Port Assignments

| Module | Port | Purpose | File |
|--------|------|---------|------|
| **Unified Platform** | 5000 | Main automated trading dashboard | `unified_trading_platform.py` |
| **Manual Trading** | **5004** | Manual paper trading (YOU control) | `manual_paper_trading.py` |
| Live Coordinator | 5001 | Swing+Intraday coordination | `live_trading_coordinator.py` |
| Intraday Monitor | 5002 | Real-time market monitoring | `intraday_monitor.py` |
| Backend API | 5003 | RESTful API backend | `backend_fixed.py` |

**All modules can run simultaneously without conflicts!**

---

## Quick Start - Manual Trading on Port 5004

### Method 1: One-Click BAT File (Recommended)

1. **Download** `START_MANUAL_TRADING_PORT_5004.bat` from GitHub:
   ```
   https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
   Branch: market-timing-critical-fix
   Path: working_directory/START_MANUAL_TRADING_PORT_5004.bat
   ```

2. **Copy** to your project folder:
   ```
   C:\Users\david\AATelS\finbert_v4.4.4\
   ```

3. **Double-click** `START_MANUAL_TRADING_PORT_5004.bat`

4. **Browser opens automatically** to `http://localhost:5004`

5. **Start trading** in the Python console:
   ```python
   >>> buy('AAPL', 100)
   >>> status()
   >>> positions()
   ```

---

### Method 2: Command Line

```bash
cd C:\Users\david\AATelS\finbert_v4.4.4

# Install dependencies (first time only)
pip install flask flask-cors yfinance pandas numpy

# Start on port 5004
python manual_paper_trading.py --port 5004

# Or with custom capital
python manual_paper_trading.py --port 5004 --capital 50000
```

---

## Integration Scenarios

### Scenario 1: Manual Trading Only (Port 5004)

**Use Case:** You want full manual control over your paper trading

**Steps:**
```bash
# Start manual trading
START_MANUAL_TRADING_PORT_5004.bat

# Access dashboard
http://localhost:5004
```

**Commands:**
```python
>>> buy('NVDA', 50)
>>> buy('AAPL', 100)
>>> status()
>>> sell('NVDA')
```

---

### Scenario 2: Unified + Manual Trading (Ports 5000 + 5004)

**Use Case:** Run automated trading AND manual trading side-by-side

**Steps:**
```bash
# Terminal 1: Start unified platform (automated)
START_UNIFIED_PLATFORM.bat

# Terminal 2: Start manual trading (port 5004)
START_MANUAL_TRADING_PORT_5004.bat

# Access both dashboards
Automated: http://localhost:5000
Manual:    http://localhost:5004
```

**Result:** 
- Automated platform trades on its own schedule
- Manual platform waits for YOUR commands
- Both track separate portfolios
- Both have independent dashboards

---

### Scenario 3: Full Multi-Module Setup (All Ports)

**Use Case:** Complete trading system with all modules running

**Steps:**

```bash
# Terminal 1: Main Dashboard (Port 5000)
python unified_trading_platform.py --paper-trading

# Terminal 2: Manual Trading (Port 5004)
python manual_paper_trading.py --port 5004

# Terminal 3: Live Coordinator (Port 5001)
cd swing_intraday_integration_v1.0
python live_trading_coordinator.py --port 5001

# Terminal 4: Intraday Monitor (Port 5002)
cd phase3_intraday_deployment
python intraday_monitor.py --port 5002
```

**Access Points:**
- `http://localhost:5000` - Main automated dashboard
- `http://localhost:5004` - Manual trading dashboard
- `http://localhost:5001` - Live coordinator status
- `http://localhost:5002` - Intraday monitoring

---

## Features - Manual Trading on Port 5004

### ✅ Full Manual Control
- YOU choose which stocks to trade
- YOU decide share quantities
- YOU control entry and exit timing
- Real-time prices via Yahoo Finance

### ✅ Live Dashboard
- Real-time portfolio monitoring
- Position tracking with P&L
- Performance charts
- Trade history and alerts

### ✅ Integration Benefits
- Runs alongside other modules
- No port conflicts (uses 5004)
- Separate from automated trading
- Independent portfolio tracking

### ✅ Simple Commands
```python
buy('SYMBOL', quantity)    # Buy shares
sell('SYMBOL')             # Sell all shares
status()                   # Portfolio summary
positions()                # Open positions with P&L
```

---

## File Structure

### Required Files

```
finbert_v4.4.4/
├── unified_trading_platform.py         # Core trading engine
├── manual_paper_trading.py             # Manual trading interface
├── START_MANUAL_TRADING_PORT_5004.bat  # One-click starter
├── templates/
│   └── dashboard.html                  # Dashboard UI
└── static/
    └── css/
        └── dashboard.css               # Dashboard styling
```

### Optional Module Files

```
swing_intraday_integration_v1.0/
├── live_trading_coordinator.py         # Swing+Intraday coordinator
└── config.json                         # Configuration

phase3_intraday_deployment/
├── intraday_monitor.py                 # Intraday monitoring
└── paper_trading_coordinator.py        # Paper trading engine
```

---

## Configuration Options

### Command-Line Arguments

```bash
# Basic usage
python manual_paper_trading.py

# Custom port (for integration)
python manual_paper_trading.py --port 5004

# Custom starting capital
python manual_paper_trading.py --capital 50000

# Both options
python manual_paper_trading.py --port 5004 --capital 200000
```

### Arguments Reference

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--port` | int | 5000 | Dashboard port number |
| `--capital` | float | 100000 | Initial capital ($) |

---

## Trading Commands Reference

### Buy Shares
```python
>>> buy('AAPL', 100)
✅ Bought 100 shares of AAPL @ $187.45
   Total cost: $18,745.00
   Remaining cash: $81,255.00
```

**Syntax:** `buy('SYMBOL', quantity [, price])`

**With manual price:**
```python
>>> buy('AAPL', 100, 185.00)  # Force price to $185
```

### Sell Shares
```python
>>> sell('AAPL')
✅ Sold 100 shares of AAPL @ $192.30
   P&L: +$485.00 (+2.59%)
   New cash balance: $100,485.00
```

**Syntax:** `sell('SYMBOL' [, price])`

### Portfolio Status
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

### Open Positions
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

---

## Dashboard Features (Port 5004)

### Real-Time Monitoring
- 📊 Portfolio value and returns
- 💰 Cash balance and invested capital
- 📈 Position tracking with live P&L
- 🎯 Win rate and trade statistics
- 📉 Performance charts
- ⚠️ Trade alerts and history

### Auto-Updates
- Position values refresh in real-time
- Charts update every 30 seconds
- Trade execution appears instantly
- P&L calculations update live

---

## Integration Best Practices

### 1. Port Management
```bash
# Check what's running on each port
netstat -ano | findstr ":5000"  # Main dashboard
netstat -ano | findstr ":5004"  # Manual trading
netstat -ano | findstr ":5001"  # Coordinator
netstat -ano | findstr ":5002"  # Intraday
```

### 2. Resource Allocation
- Each module runs in its own Python process
- Memory usage: ~100-200 MB per module
- CPU usage: Low when idle, spikes during scans
- Network: Only for data fetching (Yahoo Finance, etc.)

### 3. Stopping Modules
```bash
# Manual trading (in console)
Ctrl+C

# Or close the terminal window

# Check if port is free
netstat -ano | findstr ":5004"
```

### 4. Troubleshooting Conflicts

**Port Already in Use:**
```bash
# Find process using port 5004
netstat -ano | findstr ":5004"

# Kill process (if needed)
taskkill /PID <process_id> /F
```

**Dependencies Missing:**
```bash
# Reinstall all
pip install flask flask-cors yfinance pandas numpy --upgrade
```

---

## Comparison: Automated vs Manual Trading

| Feature | Automated (Port 5000) | Manual (Port 5004) |
|---------|----------------------|-------------------|
| **Control** | System decides | YOU decide |
| **Stock Selection** | Auto-scanned | YOU choose |
| **Timing** | Every 5 minutes | On YOUR command |
| **Quantity** | Position % | Exact shares |
| **Entry** | Auto-triggered | Manual `buy()` |
| **Exit** | Auto stop/target | Manual `sell()` |
| **Learning** | Observe | Hands-on practice |
| **Best For** | Backtesting strategies | Testing ideas |

---

## Use Cases

### 1. Practice Manual Trading
```python
# Learn without risk
buy('AAPL', 50)
positions()
sell('AAPL')
status()
```

### 2. Test Position Sizing
```python
# Try different sizes
buy('AAPL', 25)   # Small
buy('NVDA', 50)   # Medium
buy('MSFT', 100)  # Large
```

### 3. Strategy Development
```python
# Test entry/exit strategies
buy('NVDA', 50)
# Monitor performance
positions()
# Exit when satisfied
sell('NVDA')
```

### 4. Compare with Automated
```bash
# Run both systems
Terminal 1: Automated (port 5000)
Terminal 2: Manual (port 5004)

# See which performs better!
```

---

## Advanced Integration

### Running Multiple Instances

You can run manual trading on different ports with different capital:

```bash
# Instance 1: Conservative ($50k, port 5004)
python manual_paper_trading.py --port 5004 --capital 50000

# Instance 2: Aggressive ($200k, port 5005)
python manual_paper_trading.py --port 5005 --capital 200000
```

Access:
- `http://localhost:5004` - Conservative portfolio
- `http://localhost:5005` - Aggressive portfolio

---

## Troubleshooting

### Error: "Port 5004 already in use"
**Solution:**
```bash
# Check what's using port
netstat -ano | findstr ":5004"

# Kill the process
taskkill /PID <pid> /F

# Or use different port
python manual_paper_trading.py --port 5005
```

### Error: "Could not fetch price for AAPL"
**Solution:**
```python
# Use manual price
buy('AAPL', 100, 187.45)
```

### Dashboard not loading
**Solution:**
```bash
# Check if server started
# Look for: "Running on http://0.0.0.0:5004"

# Clear browser cache
Ctrl+Shift+R

# Try different browser
```

### Commands not working
**Solution:**
```python
# Ensure platform is initialized
# Check console for startup messages

# Try importing manually
from manual_paper_trading import *
```

---

## GitHub Repository

**Repository:** https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend

**Branch:** `market-timing-critical-fix`

**Files:**
- `working_directory/manual_paper_trading.py`
- `working_directory/START_MANUAL_TRADING_PORT_5004.bat`
- `working_directory/INTEGRATION_GUIDE.md`

---

## Quick Reference Card

```
START:
  Double-click: START_MANUAL_TRADING_PORT_5004.bat
  Or: python manual_paper_trading.py --port 5004

DASHBOARD:
  http://localhost:5004

COMMANDS:
  buy('SYMBOL', qty)  - Buy shares
  sell('SYMBOL')      - Sell all shares
  status()            - Portfolio summary
  positions()         - Open positions

PORTS:
  5000 - Automated trading
  5004 - Manual trading (this)
  5001 - Live coordinator
  5002 - Intraday monitor

STOP:
  Ctrl+C in console
```

---

## Summary

✅ **Manual Trading on PORT 5004** - No conflicts with other modules  
✅ **Auto-opens browser** - Instant access to dashboard  
✅ **Full manual control** - YOU choose stocks and quantities  
✅ **Real-time prices** - Live data from Yahoo Finance  
✅ **Simple commands** - `buy()`, `sell()`, `status()`, `positions()`  
✅ **Runs alongside** - Works with unified platform and other modules  
✅ **One-click start** - `START_MANUAL_TRADING_PORT_5004.bat`  

**Ready to trade manually while other modules run automatically!** 🚀📈
