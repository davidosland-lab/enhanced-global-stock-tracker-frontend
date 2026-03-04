# 🪟 WINDOWS BATCH FILES - FIRST TIME STARTUP SEQUENCE

**Date**: January 3, 2026  
**Project**: Phase 3 Intraday Trading System v1.3.11  
**Platform**: Windows  
**Location**: `phase3_intraday_deployment/`

---

## 📋 BATCH FILES AVAILABLE

Based on your screenshot and file analysis, here are all the `.bat` files:

### Setup & Installation
1. `APPLY_INTEGRATION.bat` - First-time setup and installation

### Trading System
2. `START_UNIFIED_DASHBOARD.bat` - Main dashboard (recommended)
3. `START_PAPER_TRADING.bat` - Paper trading only
4. `START_DASHBOARD.bat` - Dashboard only (legacy)

### Market Pipelines
5. `RUN_AU_PIPELINE.bat` - Australia/ASX stocks
6. `RUN_US_PIPELINE.bat` - US NYSE/NASDAQ stocks
7. `RUN_UK_PIPELINE.bat` - UK LSE stocks
8. `RUN_PIPELINES_ONCE.bat` - Run all pipelines manually

### Scheduling
9. `START_PIPELINE_SCHEDULER.bat` - Automated scheduling
10. `TEST_PIPELINE_SCHEDULER.bat` - Test scheduler
11. `START_SCHEDULER_BACKGROUND.bat` - Background scheduler
12. `STOP_PIPELINE_SCHEDULER.bat` - Stop scheduler
13. `SETUP_WINDOWS_TASK.bat` - Windows Task Scheduler setup

---

## 🚀 FIRST TIME STARTUP SEQUENCE

### **STEP 1: Initial Setup** (Run ONCE)

#### ✅ **`APPLY_INTEGRATION.bat`** - MUST RUN FIRST

**Purpose**: First-time installation and dependency setup

**What it does**:
- ✅ Checks Python version (requires 3.8+)
- ✅ Creates virtual environment (optional but recommended)
- ✅ Installs all dependencies from `requirements.txt`
- ✅ Creates necessary directories (logs, state, reports, data)
- ✅ Runs quick integration test
- ✅ Displays next steps

**How to run**:
```batch
1. Navigate to: phase3_intraday_deployment/
2. Double-click: APPLY_INTEGRATION.bat
3. When asked "Create virtual environment?": Type Y and press Enter
4. Wait for installation (2-5 minutes)
5. When test completes, press any key
```

**Expected output**:
```
==========================================
Phase 3 Intraday Integration - Installer
==========================================

1. Checking Python version...
√ Python 3.10.x found

2. Creating virtual environment...
√ Virtual environment created and activated

3. Installing dependencies...
√ Dependencies installed successfully

4. Creating directories...
√ Directories created

5. Configuration...
Please edit config\live_trading_config.json

6. Testing installation...
√ Installation test passed

==========================================
Installation Complete!
==========================================
```

**⚠️ If this fails**: Install Python 3.8+ from https://www.python.org/downloads/

---

### **STEP 2: Configuration** (Optional but Recommended)

**Before running the system**, you may want to configure:

#### Edit Configuration File
```batch
notepad config\live_trading_config.json
```

**Key settings to review**:
- `initial_capital`: Set your starting capital (default: $100,000)
- `max_positions`: Maximum concurrent positions (default: 3)
- `position_size_pct`: Position size as % of portfolio (default: 25%)
- `alerts.threshold`: Alert sensitivity (default: 70)

**💡 TIP**: You can use defaults for first run and adjust later

---

### **STEP 3: Choose Your Trading Mode**

You have **TWO** main options for first-time run:

---

## 🎯 OPTION A: UNIFIED DASHBOARD (Recommended for Beginners)

### ✅ **`START_UNIFIED_DASHBOARD.bat`** - EASIEST START

**Purpose**: All-in-one solution with web interface

**What it does**:
- ✅ Starts unified dashboard server on http://localhost:8050
- ✅ Opens web interface for stock selection
- ✅ Runs paper trading in background
- ✅ Shows live results in real-time
- ✅ Auto-refreshes every 5 seconds

**How to run**:
```batch
1. Double-click: START_UNIFIED_DASHBOARD.bat
2. Wait for "Dash is running on http://127.0.0.1:8050/"
3. Browser will open automatically (or manually go to http://localhost:8050)
4. Select stocks from dropdown or enter custom symbols
5. Set capital (default: $100,000)
6. Click "Start Trading"
7. Watch live dashboard updates
```

**Dashboard features**:
- 📊 Live portfolio value and P/L
- 📈 Open positions with real-time updates
- 🔔 Intraday alerts feed
- 📉 Performance metrics
- 📜 Trade history
- 🎯 Market sentiment gauge

**To stop**: Close the command window or press Ctrl+C

---

## 🎯 OPTION B: MARKET PIPELINE RUNNERS (Recommended for Experienced Users)

### Choose ONE market to start:

#### **Australia (ASX)**
✅ **`RUN_AU_PIPELINE.bat`**

**How to run**:
```batch
1. Double-click: RUN_AU_PIPELINE.bat
2. Select an option:
   [1] ASX Blue Chips (CBA, BHP, RIO, WOW, CSL, WES, NAB, ANZ)
   [2] ASX Banks (CBA, NAB, WBC, ANZ, MQG, BOQ)
   [3] ASX Mining (BHP, RIO, FMG, NCM, S32, IGO, MIN)
   [4] ASX Tech (WTC, XRO, CPU, APX, TNE)
   [5] ASX Top 20
   [6] Custom symbols
   [7] List all presets
3. Enter choice (1-7): 1
4. Enter capital in AUD (default: 100000): [Press Enter for default]
5. Ignore market hours? (y/N): N
```

**What happens**:
- Runs AU pipeline with selected stocks
- Shows ML signals and sentiment
- Generates trading recommendations
- Logs to `logs/au/`

---

#### **United States (NYSE/NASDAQ)**
✅ **`RUN_US_PIPELINE.bat`**

**How to run**:
```batch
1. Double-click: RUN_US_PIPELINE.bat
2. Select an option:
   [1] US Tech Giants (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD)
   [2] US Blue Chips (AAPL, MSFT, JPM, JNJ, WMT, PG, UNH, V)
   [3] FAANG (META, AAPL, AMZN, NFLX, GOOGL)
   [4] Magnificent 7 (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA)
   [5] US Financials (JPM, BAC, WFC, GS, MS, C, USB, PNC)
   [6] US Growth (TSLA, NVDA, AMD, PLTR, SQ, COIN, SNOW, NET)
   [7] Custom symbols
   [8] List all presets
3. Enter choice (1-8): 1
4. Enter capital in USD (default: 100000): [Press Enter for default]
5. Ignore market hours? (y/N): N
```

---

#### **United Kingdom (LSE)**
✅ **`RUN_UK_PIPELINE.bat`**

**How to run**:
```batch
1. Double-click: RUN_UK_PIPELINE.bat
2. Select an option:
   [1] FTSE 100 Top 10 (SHEL, AZN, HSBA, ULVR, BP, GSK, DGE, RIO, REL, NG)
   [2] FTSE 100 Banks (HSBA, LLOY, BARC, NWG, STAN)
   [3] FTSE 100 Energy (SHEL, BP, SSE, CNA, NG)
   [4] FTSE 100 Pharma (AZN, GSK, HLMA)
   [5] UK Blue Chips (HSBA, SHEL, BP, AZN, ULVR, GSK, DGE, RIO)
   [6] UK Dividend (SHEL, BP, HSBA, GSK, VOD, IMB, SSE, NG)
   [7] Custom symbols
   [8] List all presets
3. Enter choice (1-8): 1
4. Enter capital in GBP (default: 100000): [Press Enter for default]
5. Ignore market hours? (y/N): N
```

---

## 📊 RECOMMENDED FIRST-TIME SEQUENCE

### **Quick Start (5 minutes)** ⚡

```
Step 1: APPLY_INTEGRATION.bat          (Run once - 2 min)
        ↓
Step 2: START_UNIFIED_DASHBOARD.bat    (Main system)
        ↓
Step 3: Select stocks in web browser
        ↓
Step 4: Click "Start Trading"
        ↓
Step 5: Watch live dashboard
```

---

### **Complete Start (15 minutes)** 🎯

```
Step 1: APPLY_INTEGRATION.bat          (Run once - 2 min)
        ↓
Step 2: Edit config\live_trading_config.json (Optional - 2 min)
        ↓
Step 3: RUN_AU_PIPELINE.bat            (Test AU - 3 min)
        ↓
Step 4: RUN_US_PIPELINE.bat            (Test US - 3 min)
        ↓
Step 5: RUN_UK_PIPELINE.bat            (Test UK - 3 min)
        ↓
Step 6: START_UNIFIED_DASHBOARD.bat    (Main system - 2 min)
```

---

### **Advanced Start (30 minutes)** 🚀

```
Step 1: APPLY_INTEGRATION.bat          (Setup)
        ↓
Step 2: Edit config\live_trading_config.json (Configure)
        ↓
Step 3: RUN_PIPELINES_ONCE.bat         (Test all pipelines)
        ↓
Step 4: START_UNIFIED_DASHBOARD.bat    (Start main system)
        ↓
Step 5: SETUP_WINDOWS_TASK.bat         (Schedule automation)
        ↓
Step 6: START_PIPELINE_SCHEDULER.bat   (Enable scheduler)
```

---

## ⚠️ DO NOT RUN THESE ON FIRST STARTUP

These are for **advanced use** only:

❌ **`START_PAPER_TRADING.bat`** - Use `START_UNIFIED_DASHBOARD.bat` instead  
❌ **`START_DASHBOARD.bat`** - Use `START_UNIFIED_DASHBOARD.bat` instead  
❌ **`START_PIPELINE_SCHEDULER.bat`** - Only after testing pipelines manually  
❌ **`SETUP_WINDOWS_TASK.bat`** - Only for automation (optional)  
❌ **`START_SCHEDULER_BACKGROUND.bat`** - Advanced scheduling  
❌ **`STOP_PIPELINE_SCHEDULER.bat`** - Only if scheduler is running  

---

## 🎯 FINAL RECOMMENDED SEQUENCE FOR FIRST TIME

### **THE SIMPLEST PATH** (Recommended)

```batch
1. APPLY_INTEGRATION.bat              ✅ MUST RUN FIRST
   └─> Creates environment, installs dependencies

2. START_UNIFIED_DASHBOARD.bat        ✅ RECOMMENDED NEXT
   └─> All-in-one solution with web interface
```

### **What You'll See**

#### After Step 1 (APPLY_INTEGRATION.bat):
```
==========================================
Installation Complete!
==========================================

Next Steps:

1. Configure your settings:
   notepad config\live_trading_config.json

2. Run full test:
   python test_integration.py

3. Start paper trading:
   python live_trading_coordinator.py --paper-trading

4. View dashboard (if installed):
   http://localhost:8050

Happy Trading! 🚀
```

#### After Step 2 (START_UNIFIED_DASHBOARD.bat):
```
================================================================
  UNIFIED PAPER TRADING DASHBOARD
================================================================

Starting all-in-one trading system...

[1/3] Checking Python installation...
Python 3.10.11

[2/3] Verifying required packages...
[OK] All packages available

[3/3] Starting Unified Dashboard...

================================================================
  DASHBOARD STARTING
================================================================

  URL: http://localhost:8050

  Actions:
  1. Select stocks from dropdown or enter custom symbols
  2. Set your initial capital (default: $100,000)
  3. Click "Start Trading" button
  4. Watch live dashboard updates every 5 seconds

  To stop: Close this window or press Ctrl+C

================================================================

Dash is running on http://127.0.0.1:8050/
```

---

## 📁 EXPECTED DIRECTORY STRUCTURE AFTER FIRST RUN

```
phase3_intraday_deployment/
├── venv/                          ← Virtual environment (created)
├── logs/                          ← Log files (created)
│   ├── au/
│   ├── us/
│   └── uk/
├── state/                         ← State files (created)
├── reports/                       ← Report files (created)
│   ├── au/
│   ├── us/
│   └── uk/
├── data/                          ← Data cache (created)
├── config/
│   └── live_trading_config.json  ← Configuration file
├── APPLY_INTEGRATION.bat          ← Step 1: Setup
├── START_UNIFIED_DASHBOARD.bat    ← Step 2: Main system
├── RUN_AU_PIPELINE.bat            ← Optional: AU trading
├── RUN_US_PIPELINE.bat            ← Optional: US trading
├── RUN_UK_PIPELINE.bat            ← Optional: UK trading
└── [other .bat files]
```

---

## 🔧 TROUBLESHOOTING

### Problem 1: Python Not Found

**Error**:
```
ERROR: Python not found!
Please install Python 3.8+ and try again.
```

**Solution**:
1. Download Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Restart command prompt
4. Try again

---

### Problem 2: Dependencies Installation Failed

**Error**:
```
X Failed to install dependencies
```

**Solution**:
```batch
REM Option 1: Upgrade pip first
python -m pip install --upgrade pip

REM Option 2: Install manually
pip install pandas numpy yfinance yahooquery pytz
pip install dash plotly
pip install torch keras transformers
pip install xgboost lightgbm catboost scikit-learn

REM Then run APPLY_INTEGRATION.bat again
```

---

### Problem 3: Port 8050 Already in Use

**Error**:
```
OSError: [Errno 98] Address already in use
```

**Solution**:
```batch
REM Option 1: Kill existing process
taskkill /F /IM python.exe

REM Option 2: Change port in unified_trading_dashboard.py
notepad unified_trading_dashboard.py
REM Change: app.run_server(debug=False, host='0.0.0.0', port=8050)
REM To:     app.run_server(debug=False, host='0.0.0.0', port=8051)
```

---

### Problem 4: Module Not Found Errors

**Error**:
```
ModuleNotFoundError: No module named 'dash'
```

**Solution**:
```batch
REM Install missing package
pip install dash

REM Or install all at once
pip install -r requirements.txt
```

---

## 📞 QUICK REFERENCE CARD

### Essential Commands (Copy & Paste)

```batch
REM First time setup (run once)
APPLY_INTEGRATION.bat

REM Start main system (recommended)
START_UNIFIED_DASHBOARD.bat

REM Test individual markets (optional)
RUN_AU_PIPELINE.bat
RUN_US_PIPELINE.bat
RUN_UK_PIPELINE.bat

REM Stop any running process
taskkill /F /IM python.exe

REM View logs
notepad logs\unified_trading.log

REM Edit configuration
notepad config\live_trading_config.json
```

---

## ✅ SUCCESS CHECKLIST

After first startup, you should have:

- [x] ✅ Python 3.8+ installed
- [x] ✅ Virtual environment created
- [x] ✅ Dependencies installed (pandas, numpy, dash, etc.)
- [x] ✅ Directories created (logs, state, reports, data)
- [x] ✅ Configuration file exists
- [x] ✅ Installation test passed
- [x] ✅ Dashboard accessible at http://localhost:8050
- [x] ✅ Can select stocks and start trading
- [x] ✅ Dashboard updates every 5 seconds

---

## 🎯 FINAL ANSWER

### **BATCH FILES TO RUN ON FIRST STARTUP (IN ORDER)**

```
1. APPLY_INTEGRATION.bat              ← RUN THIS FIRST (mandatory)
2. START_UNIFIED_DASHBOARD.bat        ← RUN THIS NEXT (recommended)

Optional (for testing individual markets):
3. RUN_AU_PIPELINE.bat                ← Test AU market
4. RUN_US_PIPELINE.bat                ← Test US market  
5. RUN_UK_PIPELINE.bat                ← Test UK market
```

**That's it!** Just TWO batch files for a complete working system.

---

**Document Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Status**: Production Ready ✅
