═══════════════════════════════════════════════════════════════════════════
 UNIFIED TRADING SYSTEM v193.11.7 - DEPLOYMENT PACKAGE
 Trading Loop Crash Fix - Critical Update
 Date: 2026-03-10
═══════════════════════════════════════════════════════════════════════════

## 🔥 CRITICAL FIX INCLUDED

This deployment includes a **CRITICAL BUG FIX** that prevents the trading 
loop from crashing when transient errors occur.

**What Was Fixed:**
- Trading loop now survives network timeouts
- API rate limits handled gracefully
- Missing data doesn't stop trading
- Automatic error recovery every 60 seconds
- No manual intervention needed for common errors

═══════════════════════════════════════════════════════════════════════════
## 📦 PACKAGE CONTENTS
═══════════════════════════════════════════════════════════════════════════

### Core Trading System
```
core/
├── unified_trading_dashboard.py       (Dashboard UI with Force Trade fixes)
├── paper_trading_coordinator.py       (Trading loop with exception handling)
├── auth.py                            (Authentication system)
├── sentiment_integration.py           (FinBERT integration)
├── macro_risk_gates.py                (Risk gatekeeper)
├── market_entry_strategy.py           (Entry timing)
├── pre_market_strategy.py             (Gap prediction)
└── ... (all other core modules)
```

### Pipeline Scripts
```
scripts/
├── run_au_pipeline_v1.3.13.py        (AU overnight pipeline)
├── run_uk_full_pipeline.py            (UK overnight pipeline)
├── run_us_full_pipeline.py            (US overnight pipeline)
└── pipeline_signal_adapter_v3.py      (Signal integration)
```

### Startup Scripts
```
START.bat                               (Windows startup - UPDATED)
START.sh                                (Linux startup - UPDATED)
```

### Configuration
```
config/
├── system_config.yaml                 (Main configuration)
├── market_config.yaml                 (Market hours & symbols)
└── risk_config.yaml                   (Risk management)
```

### Documentation
```
TRADING_LOOP_CRASH_FIX_v193.11.7.txt   (This fix documentation)
CAPITAL_TRACKING_FIX_SUMMARY_v193.11.6.txt  (Previous fix)
README.md                               (Installation guide)
QUICK_START.md                          (Quick start guide)
```

═══════════════════════════════════════════════════════════════════════════
## 🚀 QUICK START
═══════════════════════════════════════════════════════════════════════════

### Windows

1. **Extract** the zip file to a folder (e.g., `C:\Trading`)
2. **Open Command Prompt** in the extracted folder
3. **Install dependencies** (first time only):
   ```
   pip install -r requirements.txt
   ```
4. **Run the dashboard**:
   ```
   START.bat
   ```
5. **Open browser**: http://localhost:8050
6. **Configure trading**:
   - Enter symbols (e.g., BHP.AX, CBA.AX, RIO.AX)
   - Set initial capital (e.g., 100000)
   - Set confidence threshold (default: 53%)
   - Set stop loss % (default: 5%)
7. **Click "Start Trading"**

### Linux/Mac

1. **Extract** the zip file:
   ```bash
   unzip unified_trading_system_v193.11.7_FINAL.zip
   cd unified_trading_system_v193.11.7
   ```
2. **Install dependencies** (first time only):
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Run the dashboard**:
   ```bash
   ./START.sh
   ```
4. **Open browser**: http://localhost:8050
5. **Configure and start trading** (same as Windows)

═══════════════════════════════════════════════════════════════════════════
## 🔧 WHAT'S NEW IN v193.11.7
═══════════════════════════════════════════════════════════════════════════

### Critical Fixes

1. **Trading Loop Crash Fix** ⭐ CRITICAL
   - Added exception handling to `run_trading_cycle()`
   - Loop now survives transient errors
   - Automatic recovery after 60 seconds
   - No manual restart needed
   - Full error logging with tracebacks

2. **Force Trade Capital Tracking Fix** (v193.11.6)
   - Force Trade buttons now update capital correctly
   - State file saved after manual trades
   - Total capital calculation verified

### Features Included

✅ **Multi-Market Support**: AU, US, UK markets
✅ **Gap Prediction**: Pre-market gap forecasting
✅ **Sentiment Integration**: FinBERT v4.4.4 sentiment analysis
✅ **Macro Risk Gates**: World events & VIX-based trading gates
✅ **Market Entry Strategy**: Avoid buying at tops with pullback detection
✅ **Tax Audit Trail**: ATO-compliant transaction records
✅ **LSTM Training**: Individual stock ML model training
✅ **Real-time Dashboard**: Live portfolio tracking
✅ **Paper Trading**: Risk-free testing with realistic simulation

═══════════════════════════════════════════════════════════════════════════
## ⚙️ CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

### Trading Parameters

Edit `config/system_config.yaml` to customize:

```yaml
trading:
  trade_mode: "strict"              # strict/balanced/aggressive
  min_confidence: 53.0              # Minimum confidence for entry
  max_positions: 5                  # Maximum concurrent positions
  position_size: 0.2                # 20% of capital per position
  
risk_management:
  stop_loss_percent: 5.0            # Stop loss percentage
  take_profit_percent: 8.0          # Take profit percentage
  max_drawdown: 15.0                # Maximum portfolio drawdown
  
sentiment:
  enabled: true                     # Use FinBERT sentiment
  weight: 0.4                       # Sentiment weight in signals
  
macro_risk:
  world_risk_threshold: 80          # Trading stops above 80
  vix_threshold: 30.0               # Trading stops above VIX 30
  us_market_threshold: -1.5         # Stop if S&P500 < -1.5%
```

### Market Configuration

Edit `config/market_config.yaml`:

```yaml
markets:
  AU:
    timezone: "Australia/Sydney"
    symbols: [BHP.AX, CBA.AX, RIO.AX, WBC.AX, NAB.AX]
  US:
    timezone: "America/New_York"
    symbols: [AAPL, GOOGL, MSFT, AMZN, TSLA]
  UK:
    timezone: "Europe/London"
    symbols: [BP.L, HSBA.L, GSK.L, SHEL.L]
```

═══════════════════════════════════════════════════════════════════════════
## 📊 MONITORING & LOGS
═══════════════════════════════════════════════════════════════════════════

### Log Files

All logs are stored in the `logs/` directory:

```
logs/
├── paper_trading.log              (Trading activity)
├── unified_trading.log            (Dashboard activity)
├── au_pipeline.log                (AU overnight pipeline)
├── us_full_pipeline.log           (US overnight pipeline)
├── uk_full_pipeline.log           (UK overnight pipeline)
└── screening/
    ├── stock_scanner.log          (Stock screening)
    └── lstm_training.log          (LSTM training)
```

### Monitoring Trading Loop

**Watch for cycle messages:**
```bash
tail -f logs/paper_trading.log | grep CYCLE
```

**Expected output:**
```
[CYCLE] Trading cycle 1
[CYCLE] Trading cycle 2
[CYCLE] Trading cycle 3
```

**Check for errors (should continue after errors now):**
```bash
tail -f logs/paper_trading.log | grep -E "CYCLE|ERROR|WARN"
```

**New behavior with v193.11.7:**
```
[CYCLE] Trading cycle 5
[ERROR] Exception in trading cycle: Network timeout
[ERROR] Traceback: ...
[WARN] Trading cycle failed but loop will continue
[CYCLE] Trading cycle 6  ← Continues automatically!
```

═══════════════════════════════════════════════════════════════════════════
## 🛡️ PORTFOLIO MANAGEMENT
═══════════════════════════════════════════════════════════════════════════

### Dashboard Features

Access the dashboard at http://localhost:8050 to:

- **Start/Stop Trading**: Control loop execution
- **View Positions**: Live position tracking with P&L
- **Monitor Sentiment**: FinBERT sentiment scores
- **Market Status**: 24-hour market performance chart
- **ML Signals**: Live machine learning predictions
- **Portfolio Chart**: Capital allocation visualization
- **Performance Chart**: Win/loss breakdown
- **Force Trade**: Manual position entry/exit (FIXED in this version)

### State Persistence

Portfolio state is saved to `state/paper_trading_state.json`:

```json
{
  "timestamp": "2026-03-10T10:00:00",
  "version": "v193.11.7",
  "capital": {
    "total": 102500.00,
    "cash": 80000.00,
    "invested": 22500.00,
    "total_return_pct": 2.5
  },
  "positions": {
    "count": 2,
    "open": [...]
  }
}
```

═══════════════════════════════════════════════════════════════════════════
## 🔍 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

### Dashboard Won't Start

1. **Check Python version** (3.8+ required):
   ```
   python --version
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Check port 8050** is not in use:
   ```
   netstat -an | find "8050"      (Windows)
   lsof -i :8050                  (Linux/Mac)
   ```

### Trading Loop Stops (OLD BEHAVIOR - SHOULD NOT HAPPEN NOW!)

With v193.11.7, the loop should **NOT stop** from transient errors.

If it still stops, check logs:
```bash
tail -100 logs/paper_trading.log | grep -E "ERROR|Exception"
```

Look for the new error handling message:
```
[WARN] Trading cycle failed but loop will continue
```

If you DON'T see this message, the old code is still running. 
Make sure you restarted the dashboard after updating.

### No Trades Executing

Check these settings:

1. **Trade Mode**: Set to "balanced" or "aggressive" for more signals
2. **Min Confidence**: Lower to 50% for more opportunities
3. **Market Hours**: Ensure markets are open for your symbols
4. **Sentiment Gates**: Check if macro risk gates are blocking trades

View logs:
```bash
tail -f logs/paper_trading.log | grep -E "Entry signal|POSITION OPENED"
```

### Capital Not Updating

This was fixed in v193.11.6 and is included in this package.

Verify the fix:
```bash
grep -n "def enter_position" core/paper_trading_coordinator.py
```

Should see the proper capital deduction logic.

═══════════════════════════════════════════════════════════════════════════
## 📁 FILE STRUCTURE
═══════════════════════════════════════════════════════════════════════════

```
unified_trading_system_v193.11.7/
│
├── START.bat                           ← Run this on Windows
├── START.sh                            ← Run this on Linux/Mac
├── README.md                           ← Installation guide
├── QUICK_START.md                      ← Quick start guide
├── requirements.txt                    ← Python dependencies
├── TRADING_LOOP_CRASH_FIX_v193.11.7.txt  ← This fix docs
│
├── core/                               ← Core trading system
│   ├── unified_trading_dashboard.py
│   ├── paper_trading_coordinator.py   ← FIXED: Exception handling added
│   ├── auth.py
│   ├── sentiment_integration.py
│   ├── macro_risk_gates.py
│   ├── market_entry_strategy.py
│   ├── pre_market_strategy.py
│   └── ... (other core modules)
│
├── scripts/                            ← Pipeline scripts
│   ├── run_au_pipeline_v1.3.13.py
│   ├── run_uk_full_pipeline.py
│   ├── run_us_full_pipeline.py
│   └── pipeline_signal_adapter_v3.py
│
├── pipelines/                          ← Pipeline modules
│   ├── screening/
│   └── ... (pipeline components)
│
├── ml_models/                          ← Machine learning models
│   ├── lstm_trainer_individual.py
│   └── ... (ML modules)
│
├── config/                             ← Configuration files
│   ├── system_config.yaml
│   ├── market_config.yaml
│   └── risk_config.yaml
│
├── logs/                               ← Log files (created on first run)
├── state/                              ← State persistence
├── reports/                            ← Pipeline reports
└── data/                               ← Market data cache
```

═══════════════════════════════════════════════════════════════════════════
## 🔐 SECURITY & BEST PRACTICES
═══════════════════════════════════════════════════════════════════════════

### Paper Trading Mode

This system runs in **paper trading mode** by default:
- ✅ No real money at risk
- ✅ Realistic simulation with live data
- ✅ Test strategies safely
- ✅ Full portfolio tracking

### Transition to Live Trading

To transition to live trading:
1. Thoroughly backtest with paper trading (minimum 3 months)
2. Verify win rate meets targets (>75%)
3. Review all closed trades for quality
4. Start with minimal capital in live mode
5. Gradually scale up as confidence builds

**⚠️ WARNING:** This software is for educational purposes. Past performance 
does not guarantee future results. Always trade responsibly and never risk 
more than you can afford to lose.

═══════════════════════════════════════════════════════════════════════════
## 📞 SUPPORT & UPDATES
═══════════════════════════════════════════════════════════════════════════

### Documentation

- Full documentation: See README.md
- Quick start: See QUICK_START.md
- Bug fix details: See TRADING_LOOP_CRASH_FIX_v193.11.7.txt
- Capital fix: See CAPITAL_TRACKING_FIX_SUMMARY_v193.11.6.txt

### Version History

- **v193.11.7** (2026-03-10): Trading loop crash fix - CRITICAL
- **v193.11.6** (2026-03-10): Capital tracking fix + comprehensive improvements
- **v193.11.5** (2026-03-07): Unicode logging fix for Windows
- **v193.11.4** (2026-03-04): All pipelines working + HOLD signal fix

### System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **Network**: Stable internet connection for market data

═══════════════════════════════════════════════════════════════════════════
## ✅ VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════════════════════

After installation, verify everything works:

□ Python 3.8+ installed
□ Dependencies installed (pip install -r requirements.txt)
□ Dashboard starts without errors (START.bat or START.sh)
□ Dashboard accessible at http://localhost:8050
□ Can enter symbols and capital
□ "Start Trading" button works
□ Logs show [CYCLE] messages every 60 seconds
□ Portfolio displays correctly
□ State file created in state/ directory
□ Force Trade buttons work (optional test)

═══════════════════════════════════════════════════════════════════════════

**Version:** v193.11.7
**Release Date:** 2026-03-10
**Package:** unified_trading_system_v193.11.7_FINAL.zip
**Critical Fix:** Trading loop crash prevention
**Status:** PRODUCTION READY

═══════════════════════════════════════════════════════════════════════════
