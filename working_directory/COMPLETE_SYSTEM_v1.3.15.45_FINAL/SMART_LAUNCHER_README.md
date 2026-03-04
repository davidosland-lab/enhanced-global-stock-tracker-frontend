# Smart Launcher - Complete Global Market Intelligence System

## Overview

**LAUNCH_COMPLETE_SYSTEM.bat** is an intelligent Windows batch launcher that provides:

- ✅ **Automatic first-time vs restart detection**
- ✅ **Automatic dependency installation** (first run only)
- ✅ **Complete workflow integration** (overnight pipelines + live trading)
- ✅ **Multi-market support** (AU/US/UK)
- ✅ **Interactive menu system**
- ✅ **Environment validation**
- ✅ **System status monitoring**

---

## Quick Start

### First-Time Installation

1. **Double-click** `LAUNCH_COMPLETE_SYSTEM.bat`
2. The system will automatically:
   - Detect it's the first run
   - Check Python installation
   - Create virtual environment
   - Install all dependencies (may take 5-10 minutes)
   - Set up required directories
   - Create installation marker

### Subsequent Runs

1. **Double-click** `LAUNCH_COMPLETE_SYSTEM.bat`
2. The system will:
   - Detect previous installation
   - Activate virtual environment
   - Verify dependencies
   - Show main menu

---

## Main Menu Options

### 1. Run COMPLETE WORKFLOW ⭐ (Recommended)

**What it does:**
- Runs overnight pipelines for all 3 markets (AU, US, UK)
- Analyzes 720 stocks (240 per market)
- Generates morning sentiment reports
- Executes live trading based on signals
- Applies regime-aware opportunity scoring

**Time:** 30-60 minutes  
**Capital:** $300,000 (recommended)

**Usage:**
```
Select option: 1
Confirm: Y
```

**What you get:**
- Morning reports: `reports/screening/{market}_morning_report.json`
- CSV exports: `reports/csv_exports/`
- Trade logs: `logs/trading/`
- Portfolio state: `state/trading_state.json`

---

### 2. Run OVERNIGHT PIPELINES ONLY

**What it does:**
- Runs overnight analysis for all markets
- Does NOT execute trades
- Good for review before trading

**Time:** 20-40 minutes  
**Capital:** $100,000 per market

**Usage:**
```
Select option: 2
Confirm: Y
```

**Output:**
- Morning sentiment reports saved to `reports/screening/`
- Ready for manual review or Option 3

---

### 3. Run LIVE TRADING ONLY

**What it does:**
- Reads existing pipeline reports
- Executes trades based on signals
- Skips overnight analysis

**Requirements:**
- Must have existing reports from Option 2
- Reports should be recent (same day)

**Time:** 5-15 minutes  
**Capital:** $300,000 (total)

**Usage:**
```
Select option: 3
Confirm: Y
```

**Use case:**
- Already ran pipelines (Option 2)
- Want to execute trades after review
- Need to restart trading after interruption

---

### 4. Run SINGLE MARKET PIPELINE

**What it does:**
- Runs pipeline for one market only
- Faster testing/development

**Markets:**
- AU: Australia (ASX) - 240 stocks
- US: United States (NYSE/NASDAQ) - 240 stocks
- UK: United Kingdom (LSE) - 240 stocks

**Time:** 10-20 minutes per market  
**Capital:** $100,000

**Usage:**
```
Select option: 4
Select market: 1 (AU), 2 (US), or 3 (UK)
```

---

### 5. View System Status

**What it shows:**
- Python version
- Virtual environment status
- Installed dependencies
- Recent pipeline reports
- Trading state

**Usage:**
```
Select option: 5
```

**Example output:**
```
Python 3.12.0

Virtual Environment: Active
Location: C:\...\venv

Key Dependencies:
  yfinance: Installed
  pandas: Installed
  numpy: Installed
  flask: Installed
  scikit-learn: Installed

Recent Pipeline Reports:
  AU: Found
  US: Found
  UK: Not found

Trading State: Found
```

---

### 6. Open Trading Dashboard

**What it does:**
- Starts Flask web server
- Opens dashboard at `http://localhost:5002`
- Shows live portfolio, trades, performance

**Usage:**
```
Select option: 6
```

**Dashboard features:**
- Real-time portfolio value
- Open positions
- Trade history
- Performance metrics
- Market sentiment

**To stop:** Press `Ctrl+C`

---

### 7. Advanced Options

#### 7.1 Reinstall Dependencies
- Force reinstall all Python packages
- Use if packages corrupted or outdated

#### 7.2 Clear All Logs
- Deletes all log files
- Frees up disk space
- Use for clean slate

#### 7.3 Reset Trading State
- ⚠️ **WARNING:** Deletes portfolio state
- Use to start fresh trading session
- Cannot be undone

#### 7.4 View Recent Logs
- Shows last entries from workflow log
- Useful for debugging

---

## System Architecture

### First-Time Detection Flow

```
Start
  ↓
Check for .system_installed marker
  ↓
┌─ YES → Normal Operation
│   ├─ Activate venv
│   ├─ Verify dependencies
│   └─ Show main menu
│
└─ NO → First-Time Setup
    ├─ Check Python
    ├─ Create venv
    ├─ Upgrade pip
    ├─ Install dependencies
    ├─ Create directories
    ├─ Create .system_installed marker
    └─ Continue to normal operation
```

### Complete Workflow Flow

```
Overnight Pipelines (AU/US/UK)
  ↓
Generate JSON Reports
  ↓
Pipeline Signal Adapter V2
  ↓
Convert Sentiment → Trading Signals
  ↓
Paper Trading Coordinator
  ↓
Execute Positions
  ↓
Intraday Monitoring (every 15 min)
  ↓
End-of-Day Save State
```

---

## File Structure

```
complete_backend_clean_install_v1.3.13/
│
├── LAUNCH_COMPLETE_SYSTEM.bat     ← Smart launcher (start here!)
├── complete_workflow.py            ← Workflow orchestrator
├── pipeline_signal_adapter_v2.py   ← Signal converter
├── run_us_full_pipeline.py         ← US pipeline
├── run_uk_full_pipeline.py         ← UK pipeline
├── run_au_pipeline_v1.3.13.py      ← AU pipeline
├── dashboard.py                    ← Web dashboard
├── requirements.txt                ← Python dependencies
│
├── .system_installed               ← Installation marker (auto-created)
├── venv/                           ← Virtual environment (auto-created)
│
├── config/
│   ├── live_trading_config.json
│   ├── screening_config.json
│   ├── us_sectors.json
│   ├── uk_sectors.json
│   └── asx_sectors.json
│
├── reports/
│   ├── screening/
│   │   ├── au_morning_report.json
│   │   ├── us_morning_report.json
│   │   └── uk_morning_report.json
│   └── csv_exports/
│
├── logs/
│   ├── complete_workflow.log
│   ├── screening/
│   └── trading/
│
└── state/
    └── trading_state.json
```

---

## Requirements

### System Requirements
- **OS:** Windows 10/11
- **Python:** 3.8 or higher (3.12 recommended)
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 2GB free space (for dependencies and data)
- **Internet:** Required for market data fetching

### Python Packages (Auto-Installed)
- **Core:** yfinance, pandas, numpy, flask, requests
- **ML:** scikit-learn, scipy
- **Visualization:** matplotlib, seaborn, plotly
- **Testing:** pytest (optional)
- **Development:** black, flake8 (optional)

---

## Typical Daily Workflow

### Morning (Before Market Open)

**Option A: Full Automation (Recommended)**
```
1. Double-click LAUNCH_COMPLETE_SYSTEM.bat
2. Select: 1 (Complete Workflow)
3. Confirm: Y
4. Wait 30-60 minutes
5. Review final summary
6. Check reports/screening/ for details
```

**Option B: Review Before Trading**
```
1. Double-click LAUNCH_COMPLETE_SYSTEM.bat
2. Select: 2 (Overnight Pipelines Only)
3. Wait 20-40 minutes
4. Review reports in reports/screening/
5. Select: 3 (Live Trading Only)
6. Confirm: Y
```

### During Trading Hours

**Monitor via Dashboard:**
```
1. Select: 6 (Open Dashboard)
2. Navigate to http://localhost:5002
3. Watch real-time portfolio updates
4. Review open positions
5. Check performance metrics
```

### End of Day

**Review Results:**
```
1. Check logs/trading/ for trade logs
2. Review state/trading_state.json for portfolio
3. Check reports/csv_exports/ for CSV data
4. View dashboard for performance summary
```

---

## Scheduling (Optional)

### Windows Task Scheduler Setup

**Schedule overnight pipelines to run automatically:**

1. Open Task Scheduler
2. Create Basic Task
3. **Trigger:** Daily at 2:00 AM (or preferred time)
4. **Action:** Start a program
   - Program: `C:\...\LAUNCH_COMPLETE_SYSTEM.bat`
   - Arguments: (leave blank - will use menu option 1)
5. **Conditions:**
   - Run only if computer is on AC power
   - Wake computer to run
6. Save

**Note:** For unattended execution, you may need to modify the batch file to auto-select menu options.

---

## Troubleshooting

### Problem: "Python not found"
**Solution:**
1. Download Python from https://python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart command prompt
4. Run launcher again

### Problem: Dependencies fail to install
**Solution:**
```bat
1. Open command prompt as Administrator
2. cd C:\path\to\complete_backend_clean_install_v1.3.13
3. python -m pip install --upgrade pip
4. pip install wheel setuptools
5. pip install -r requirements.txt
```

### Problem: "Pipeline reports not found"
**Solution:**
- Run Option 2 (Overnight Pipelines) first
- Or check if previous run completed successfully
- Check logs/complete_workflow.log for errors

### Problem: Virtual environment issues
**Solution:**
```bat
1. Delete venv folder
2. Delete .system_installed marker
3. Run launcher again (will recreate everything)
```

### Problem: Trading state corruption
**Solution:**
```
1. Select: 7 (Advanced Options)
2. Select: 3 (Reset Trading State)
3. Confirm: Y
```

---

## Advanced Configuration

### Custom Capital Allocation

**Edit complete_workflow.py:**
```python
# Line ~298 (in run_complete_workflow)
capital_per_market = capital / len(markets)  # Change allocation logic here
```

### Custom Market Selection

**Edit LAUNCH_COMPLETE_SYSTEM.bat:**
```bat
REM Line ~200+ (in :complete_workflow)
python complete_workflow.py --run-pipelines --execute-trades --markets AU,US --capital 200000
REM Remove UK if desired
```

### Custom Scheduling Times

**For automated runs, modify config/live_trading_config.json:**
```json
{
  "trading_hours": {
    "AU": {"start": "10:00", "end": "16:00"},
    "US": {"start": "09:30", "end": "16:00"},
    "UK": {"start": "08:00", "end": "16:30"}
  }
}
```

---

## Performance Benchmarks

### Tested Configuration
- **System:** Windows 11, Intel i7, 16GB RAM, SSD
- **Python:** 3.12.0
- **Markets:** AU, US, UK (720 stocks total)

### Execution Times
- **First-time setup:** 10-15 minutes (dependency installation)
- **Complete workflow:** 35-45 minutes
- **Overnight pipelines only:** 25-35 minutes
- **Live trading only:** 5-10 minutes
- **Single market pipeline:** 12-18 minutes

### Resource Usage
- **RAM:** 2-4 GB during pipeline execution
- **CPU:** 30-70% utilization
- **Disk I/O:** Moderate (logging, reports)
- **Network:** Intermittent (market data fetching)

---

## Version History

### v1.3.13.10 (2026-01-08)
- ✅ Smart launcher with first-time detection
- ✅ Automatic dependency installation
- ✅ Interactive menu system
- ✅ Complete workflow integration
- ✅ Multi-market support
- ✅ System status monitoring
- ✅ Advanced options menu

### v1.3.13 (2026-01-06)
- Regime intelligence integration
- US/UK pipeline additions
- Enhanced signal adapter

---

## Support & Documentation

### Documentation Files
- `COMPLETE_PIPELINE_GUIDE.md` - Pipeline documentation
- `INTEGRATION_COMPLETE_SUMMARY_V2.md` - Integration architecture
- `PIPELINE_TRADING_INTEGRATION.md` - Original trading integration
- `README.md` - General system overview

### Logs for Debugging
- `logs/complete_workflow.log` - Workflow execution
- `logs/screening/*.log` - Pipeline logs
- `logs/trading/*.log` - Trading logs

### Contact
- GitHub: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- Branch: market-timing-critical-fix

---

## License

This system is part of the Enhanced Global Stock Tracker project.

---

## Quick Reference Card

| Action | Menu Option | Time | Capital |
|--------|-------------|------|---------|
| Full workflow (overnight + trading) | 1 | 30-60 min | $300k |
| Pipelines only (no trading) | 2 | 20-40 min | $100k |
| Trading only (use existing reports) | 3 | 5-15 min | $300k |
| Single market (AU/US/UK) | 4 | 10-20 min | $100k |
| System status | 5 | Instant | - |
| Dashboard | 6 | Instant | - |
| Advanced options | 7 | Varies | - |

---

## Next Steps

1. **First run:** Double-click `LAUNCH_COMPLETE_SYSTEM.bat`
2. **Wait for setup:** Let it install dependencies (10-15 min)
3. **Select Option 1:** Run complete workflow
4. **Review results:** Check reports/screening/ and logs/
5. **Open dashboard:** Use Option 6 to view portfolio
6. **Schedule daily:** Set up Windows Task Scheduler for automation

**Ready to trade globally? Start now!** 🚀
