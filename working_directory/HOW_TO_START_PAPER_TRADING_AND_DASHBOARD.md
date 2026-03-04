# 🚀 HOW TO START PAPER TRADING & DASHBOARD

## 📊 **YES! There is a Dashboard Component**

The system includes **two separate components** that work together:

1. **Paper Trading Coordinator** - Generates signals & manages trades
2. **Dashboard** - Visualizes results in real-time (http://localhost:8050)

---

## 🎯 **Recommended Setup: Run Both Components**

### Step 1: Start Paper Trading (Terminal 1)

**Open Command Prompt or PowerShell:**

```batch
cd C:\Users\david\Trading\phase3_intraday_deployment
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals --cycles 100 --interval 60
```

**What this does:**
- ✅ Fetches real market data
- ✅ Generates ML signals every 60 seconds
- ✅ Opens/closes positions automatically
- ✅ Saves state to `state/paper_trading_state.json`
- ✅ Logs to `logs/paper_trading.log`
- ✅ Runs for 100 cycles (~100 minutes)

**Keep this terminal open!**

---

### Step 2: Start Dashboard (Terminal 2)

**Open a NEW Command Prompt or PowerShell:**

```batch
cd C:\Users\david\Trading\phase3_intraday_deployment
python dashboard.py
```

**Then open your browser to:**
```
http://localhost:8050
```

**Dashboard Features:**
- 📊 Live portfolio value & P&L
- 💼 Open positions with real-time updates
- 🔔 Intraday alerts feed
- 📈 Performance metrics (win rate, Sharpe, etc.)
- 📜 Trade history
- 🌡️ Market sentiment gauge
- 🔄 Auto-refreshes every 5 seconds

---

## 🖥️ **Visual Workflow**

```
Terminal 1 (Paper Trading)          Terminal 2 (Dashboard)
┌─────────────────────────┐        ┌──────────────────────────┐
│                         │        │                          │
│ python paper_trading_   │───────▶│ python dashboard.py      │
│   coordinator.py        │ writes │                          │
│                         │ state  │ Reads state every 5s     │
│ Generates signals       │ to     │ Displays in browser      │
│ Opens/closes positions  │ JSON   │                          │
│ Saves to state/         │        │ http://localhost:8050    │
│   paper_trading_state.  │        │                          │
│   json                  │        │ 📊 Live charts           │
│                         │        │ 💼 Open positions        │
│ Logs to logs/paper_     │        │ 📈 Performance metrics   │
│   trading.log           │        │ 🔔 Alerts                │
└─────────────────────────┘        └──────────────────────────┘
```

---

## ⚡ **Quick Start Options**

### Option A: Paper Trading Only (No Dashboard)
```batch
cd phase3_intraday_deployment
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
```

**Monitor via:**
- State file: `state/paper_trading_state.json`
- Logs: `logs/paper_trading.log`

---

### Option B: Paper Trading + Dashboard (Recommended)
```batch
# Terminal 1:
cd phase3_intraday_deployment
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals

# Terminal 2:
cd phase3_intraday_deployment
python dashboard.py

# Browser:
Open http://localhost:8050
```

---

### Option C: Using Batch Files (Windows)

**For Paper Trading:**
```batch
Double-click: phase3_intraday_deployment\START_PAPER_TRADING.bat
```

**For Dashboard (create this file):**
```batch
@echo off
echo ════════════════════════════════════════════════════════════
echo   Phase 3 Paper Trading Dashboard
echo ════════════════════════════════════════════════════════════
echo.
echo Starting dashboard server...
echo Open browser to: http://localhost:8050
echo.
echo Press Ctrl+C to stop the dashboard
echo ════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"
python dashboard.py
pause
```

Save as: `phase3_intraday_deployment\START_DASHBOARD.bat`

---

## 📋 **Paper Trading Coordinator Parameters**

```batch
python paper_trading_coordinator.py [OPTIONS]
```

### Required Options:
- `--symbols` - Comma-separated list of symbols (e.g., `RIO.AX,CBA.AX,BHP.AX`)
- `--capital` - Initial capital (e.g., `100000`)

### Optional Options:
- `--real-signals` - Use real ML signals (recommended)
- `--cycles` - Number of trading cycles (default: 100)
- `--interval` - Seconds between cycles (default: 60)
- `--max-positions` - Max concurrent positions (default: 3)
- `--position-size` - Position size as % (default: 0.25 = 25%)

### Examples:

**Basic (Australian stocks):**
```batch
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
```

**US stocks:**
```batch
python paper_trading_coordinator.py --symbols AAPL,GOOGL,MSFT,TSLA --capital 100000 --real-signals
```

**Fast testing (5-second intervals):**
```batch
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX --capital 50000 --real-signals --cycles 20 --interval 5
```

**Conservative (smaller positions):**
```batch
python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals --position-size 0.15
```

---

## 📊 **Dashboard Features Explained**

### 1. Portfolio Overview (Top)
- **Total Value:** Current portfolio value
- **Cash:** Available cash
- **Invested:** Value in open positions
- **P&L:** Total profit/loss
- **Return %:** Percentage return

### 2. Open Positions Table
- Symbol, Entry Date, Entry Price
- Current Price, Shares, Position Value
- Unrealized P&L, P&L %
- Stop Loss, Profit Target
- Confidence Score, Days Held

### 3. Performance Metrics
- **Total Trades:** Number of closed trades
- **Win Rate:** % of winning trades
- **Avg Win:** Average winning trade size
- **Avg Loss:** Average losing trade size
- **Profit Factor:** Gross profit / Gross loss
- **Sharpe Ratio:** Risk-adjusted returns
- **Max Drawdown:** Largest peak-to-trough decline

### 4. Market Sentiment Gauge
- Real-time market sentiment (0-100)
- SPY momentum + VIX analysis
- Sentiment class (Bearish/Neutral/Bullish)

### 5. Intraday Alerts
- Breakout alerts
- Volume surge alerts
- Stop loss hits
- Profit target hits
- Position opens/closes

### 6. Trade History
- All closed trades with entry/exit details
- P&L per trade
- Exit reasons (target, stop, time)

### 7. Charts (if implemented)
- Portfolio value over time
- P&L curve
- Win rate trend
- Position distribution

---

## 🔍 **Monitoring Without Dashboard**

If you don't want to use the dashboard, you can monitor via files:

### View Current State:
```batch
type state\paper_trading_state.json
```

Or prettified:
```batch
python -m json.tool state\paper_trading_state.json
```

### View Logs (Real-time):
```batch
powershell Get-Content logs\paper_trading.log -Wait -Tail 20
```

Or in CMD:
```batch
type logs\paper_trading.log
```

### Check Specific Data:

**Open Positions:**
```batch
python -c "import json; data=json.load(open('state/paper_trading_state.json')); print('Open Positions:', len(data.get('positions', {}).get('open', [])))"
```

**Current Capital:**
```batch
python -c "import json; data=json.load(open('state/paper_trading_state.json')); print('Total:', data['capital']['total'], '| Cash:', data['capital']['cash'], '| Invested:', data['capital']['invested'])"
```

**Win Rate:**
```batch
python -c "import json; data=json.load(open('state/paper_trading_state.json')); perf=data.get('performance', {}); print('Win Rate:', perf.get('win_rate', 0), '| Trades:', perf.get('total_trades', 0))"
```

---

## 🛠️ **Troubleshooting**

### Issue: Dashboard won't start
**Error:** `ModuleNotFoundError: No module named 'dash'`

**Solution:**
```batch
pip install dash plotly
```

### Issue: Port 8050 already in use
**Solution:**
1. Stop the existing dashboard (Ctrl+C)
2. Or change port in dashboard.py (line 480): `port=8051`

### Issue: Paper trading won't start
**Error:** `No module named 'yahooquery'`

**Solution:**
```batch
pip install -r phase3_intraday_deployment\requirements.txt
```

### Issue: Dashboard shows no data
**Solution:**
1. Ensure paper trading coordinator is running
2. Wait for first signal cycle (60 seconds)
3. Check `state/paper_trading_state.json` exists
4. Refresh dashboard in browser

### Issue: Can't access dashboard from browser
**Solution:**
1. Check terminal for "Starting Paper Trading Dashboard..."
2. Verify URL: http://localhost:8050 (not 127.0.0.1:8050)
3. Try http://127.0.0.1:8050 instead
4. Check firewall isn't blocking port 8050

---

## 📝 **Example Session**

```batch
C:\Users\david\Trading> cd phase3_intraday_deployment

C:\Users\david\Trading\phase3_intraday_deployment> python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals

Starting Phase 3 Paper Trading Coordinator
==========================================
Capital: $100,000
Symbols: RIO.AX, CBA.AX, BHP.AX
ML Signals: Enabled
Max Positions: 3
Interval: 60 seconds

Cycle 1/100:
  Fetching data for RIO.AX, CBA.AX, BHP.AX...
  Analyzing signals...
  RIO.AX: BUY (conf=66.3%) - Opening position: 203 shares @ $147.50
  CBA.AX: HOLD (conf=50.1%)
  BHP.AX: BUY (conf=64.3%) - Opening position: 460 shares @ $45.62
  
  Open Positions: 2
  Total Capital: $99,949.07
  Cash: $49,021.37
  Invested: $50,927.70

Cycle 2/100:
  Fetching data...
  Analyzing signals...
  RIO.AX: Price $147.80 (+0.20%) - HOLD
  BHP.AX: Price $45.70 (+0.18%) - HOLD
  
  Open Positions: 2
  Unrealized P&L: +$97.60 (+0.19%)
```

**Meanwhile in browser (http://localhost:8050):**
- Live updates every 5 seconds
- Charts showing portfolio value
- Position table with RIO.AX and BHP.AX
- Performance metrics updating

---

## ✅ **Summary**

| Component | Purpose | Command | Output |
|-----------|---------|---------|--------|
| **Paper Trading** | Generate signals & trade | `python paper_trading_coordinator.py ...` | Terminal + JSON state |
| **Dashboard** | Visualize results | `python dashboard.py` | http://localhost:8050 |

**Recommendation:** Run BOTH for the best experience!

---

## 🎯 **Next Steps**

1. ✅ Start paper trading coordinator in Terminal 1
2. ✅ Start dashboard in Terminal 2
3. ✅ Open browser to http://localhost:8050
4. ✅ Watch signals generate and positions open
5. ✅ Monitor performance metrics
6. ✅ Let it run for 10-20 trades to validate win rate

---

**Questions?**
- Check WINDOWS_TROUBLESHOOTING.md
- Check DEPLOYMENT_README.md
- Check logs/paper_trading.log for detailed activity

**Ready to trade!** 🚀
