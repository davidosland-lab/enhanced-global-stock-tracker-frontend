# Pipeline-Enhanced Trading System v1.4.0
## Windows 11 Installation Guide

**Package**: `pipeline_enhanced_trading_v1.4.0_VERIFIED.zip`  
**Size**: 393 KB  
**Date**: January 4, 2026  
**Status**: ✅ VERIFIED & PRODUCTION READY

---

## 📋 Prerequisites

### Required Software
- **Windows 11** (Windows 10 also supported)
- **Python 3.8+** (Python 3.10 recommended)
  - Download from: https://www.python.org/downloads/
  - ⚠️ **Important**: Check "Add Python to PATH" during installation
- **Administrator Access** (for Task Scheduler setup)

### Verify Python Installation
Open Command Prompt or PowerShell and run:
```cmd
python --version
pip --version
```

You should see Python 3.8 or higher.

---

## 🚀 Installation Steps

### Step 1: Extract the ZIP File

1. **Download** `pipeline_enhanced_trading_v1.4.0_VERIFIED.zip` to your desired location
   - Recommended: `C:\Trading\` or `C:\Users\YourName\Trading\`

2. **Extract** the ZIP file
   - Right-click → "Extract All..."
   - Or use 7-Zip, WinRAR, etc.

3. **Navigate** into the extracted folder:
   ```
   temp_deploy_pipeline_v1.4.0\
   ```

4. **Optional**: Rename the folder to something simpler:
   ```
   Rename to: trading_system
   ```

### Step 2: Install Dependencies

1. **Open Command Prompt as Administrator**
   - Press `Win + X`
   - Select "Terminal (Admin)" or "Command Prompt (Admin)"

2. **Navigate to the installation directory**:
   ```cmd
   cd C:\Trading\temp_deploy_pipeline_v1.4.0
   ```
   (Adjust the path to match your installation location)

3. **Run the installation script**:
   ```cmd
   INSTALL.bat
   ```

   This will:
   - Install all Python dependencies
   - Install the scheduler library (schedule, pytz)
   - Create required directories (logs, state, reports)
   - Set up the folder structure

4. **Wait for completion** (typically 2-5 minutes depending on internet speed)

### Step 3: Configure Automated Scheduling

**⚠️ This step requires Administrator privileges**

1. **Navigate to the phase3_intraday_deployment folder**:
   ```cmd
   cd phase3_intraday_deployment
   ```

2. **Run the Task Scheduler setup** (as Administrator):
   ```cmd
   SETUP_WINDOWS_TASK.bat
   ```

   This creates three scheduled tasks:
   - **AU Pipeline**: Runs daily at 07:30 AEDT (before ASX opens at 10:00)
   - **US Pipeline**: Runs daily at 07:00 EST (before NYSE opens at 09:30)
   - **UK Pipeline**: Runs daily at 05:30 GMT (before LSE opens at 08:00)

3. **Verify tasks were created**:
   - Open Task Scheduler (search "Task Scheduler" in Start menu)
   - Look for tasks named:
     - `Pipeline_Trading_AU`
     - `Pipeline_Trading_US`
     - `Pipeline_Trading_UK`

### Step 4: Test the Installation

1. **Test the pipeline scheduler**:
   ```cmd
   TEST_PIPELINE_SCHEDULER.bat
   ```

   You should see output showing:
   - Current time in each timezone
   - Next pipeline run times
   - Market opening times
   - Lead times (should be 2.5 hours for each)

2. **Expected output**:
   ```
   AU Market: Pipeline runs 07:30 AEDT (opens 10:00)
   US Market: Pipeline runs 07:00 EST (opens 09:30)
   UK Market: Pipeline runs 05:30 GMT (opens 08:00)
   
   All pipelines: 2.5 hour lead time ✓
   ```

### Step 5: Run Your First Pipeline (Optional Test)

**Test the UK pipeline manually** (or AU/US depending on your timing):
```cmd
cd pipeline_trading
python scripts\run_uk_morning_report.py
```

This will:
- Fetch FTSE 100 sentiment
- Scan UK stocks
- Generate predictions
- Create a morning report in `reports/uk/`

---

## 📊 Usage

### Starting the Trading System

**Single Market (Recommended for testing)**:
```cmd
cd phase3_intraday_deployment
python run_pipeline_enhanced_trading.py --market AU
```

**With Custom Capital**:
```cmd
python run_pipeline_enhanced_trading.py --market US --capital 50000
```

**All Markets** (capital automatically split):
```cmd
python run_pipeline_enhanced_trading.py --market ALL --capital 150000
```

**Opportunity Mode** (up to 150% position sizing):
```cmd
python run_pipeline_enhanced_trading.py --market US --opportunity-mode
```

**Dry Run** (no actual trades, testing only):
```cmd
python run_pipeline_enhanced_trading.py --market UK --dry-run
```

### Manual Pipeline Execution

If you want to run pipelines manually instead of automated:

```cmd
cd pipeline_trading

REM Australian market
python scripts\run_au_morning_report.py

REM US market
python scripts\run_us_morning_report.py

REM UK market
python scripts\run_uk_morning_report.py
```

### Scheduler Management

**Start the scheduler** (runs in background):
```cmd
cd phase3_intraday_deployment
START_SCHEDULER_BACKGROUND.bat
```

**Stop the scheduler**:
```cmd
STOP_PIPELINE_SCHEDULER.bat
```

**Force run all pipelines now** (for testing):
```cmd
RUN_PIPELINES_ONCE.bat
```

---

## 📁 Folder Structure

```
temp_deploy_pipeline_v1.4.0/
│
├── INSTALL.bat                          # Main installation script
├── requirements.txt                     # Python dependencies
├── QUICK_START.md                       # Quick reference guide
├── DEPLOYMENT_v1.4.0_SUMMARY.md        # Complete documentation
│
├── phase3_intraday_deployment/         # Trading system
│   ├── run_pipeline_enhanced_trading.py  # Main trading script
│   ├── pipeline_signal_adapter.py        # Signal conversion
│   ├── pipeline_scheduler.py             # Automated scheduler
│   ├── paper_trading_coordinator.py      # Paper trading engine
│   │
│   ├── SETUP_WINDOWS_TASK.bat           # ⭐ Run as Admin
│   ├── TEST_PIPELINE_SCHEDULER.bat       # Test timing
│   ├── START_SCHEDULER_BACKGROUND.bat    # Start scheduler
│   ├── STOP_PIPELINE_SCHEDULER.bat       # Stop scheduler
│   ├── RUN_PIPELINES_ONCE.bat           # Manual run
│   │
│   ├── WINDOWS_SCHEDULER_GUIDE.md        # Scheduling docs
│   ├── PIPELINE_TRADING_INTEGRATION.md   # Integration guide
│   └── config/                          # Configuration files
│
└── pipeline_trading/                    # Pipeline system
    ├── models/screening/                # Pipeline components
    │   ├── overnight_pipeline.py         # AU pipeline
    │   ├── us_overnight_pipeline.py      # US pipeline
    │   ├── uk_overnight_pipeline.py      # UK pipeline
    │   ├── spi_monitor.py                # SPI 200 monitoring
    │   ├── us_market_monitor.py          # US market monitoring
    │   ├── uk_market_monitor.py          # UK market monitoring
    │   └── ...                           # Other components
    │
    ├── scripts/                         # Pipeline runners
    │   ├── run_au_morning_report.py      # Run AU pipeline
    │   ├── run_us_morning_report.py      # Run US pipeline
    │   └── run_uk_morning_report.py      # Run UK pipeline
    │
    └── config/                          # Pipeline configuration
```

---

## 📈 Monitoring

### Log Files

**Pipeline Scheduler**:
```
logs\pipeline_scheduler.log
```

**Trading System**:
```
phase3_intraday_deployment\logs\paper_trading.log
```

**Individual Pipelines**:
```
pipeline_trading\logs\screening\au\pipeline_YYYYMMDD.log
pipeline_trading\logs\screening\us\pipeline_YYYYMMDD.log
pipeline_trading\logs\screening\uk\pipeline_YYYYMMDD.log
```

### Morning Reports

HTML reports are generated daily at:
```
pipeline_trading\reports\au\morning_report_YYYYMMDD.html
pipeline_trading\reports\us\morning_report_YYYYMMDD.html
pipeline_trading\reports\uk\morning_report_YYYYMMDD.html
```

Open these in your web browser to view detailed analysis.

---

## ⚙️ Configuration

### Trading Configuration

Edit `phase3_intraday_deployment\config\live_trading_config.json` to adjust:
- Capital allocation
- Stop-loss/take-profit defaults
- Risk parameters
- Position sizing limits

### Pipeline Configuration

Edit `pipeline_trading\config\screening_config.json` to adjust:
- Sentiment thresholds
- Correlation factors
- Stock selection criteria
- Scanning parameters

---

## 🔍 Troubleshooting

### Python not found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**: 
1. Reinstall Python with "Add to PATH" checked
2. Or use `py` instead of `python` in commands

### Import errors
**Error**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Run `INSTALL.bat` again as Administrator

### Task Scheduler issues
**Error**: Tasks not running automatically

**Solution**:
1. Open Task Scheduler
2. Find the task (e.g., `Pipeline_Trading_AU`)
3. Right-click → Properties
4. Check "Run whether user is logged on or not"
5. Enter your Windows password when prompted

### Permission errors
**Error**: `Access Denied` or `Permission Error`

**Solution**: Run Command Prompt as Administrator

### Timezone issues
**Error**: Pipelines running at wrong times

**Solution**: 
1. Verify your system timezone is correct
2. Run `TEST_PIPELINE_SCHEDULER.bat` to check times
3. Pipelines automatically adjust for:
   - AEDT (Australian Eastern Daylight Time)
   - EST (Eastern Standard Time)
   - GMT (Greenwich Mean Time)

---

## 🎯 Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed and in PATH
- [ ] All dependencies installed (run `INSTALL.bat`)
- [ ] Directories created (logs, state, reports)
- [ ] Windows Task Scheduler tasks created (3 tasks)
- [ ] Test scheduler shows correct times (`TEST_PIPELINE_SCHEDULER.bat`)
- [ ] Pipeline scripts exist and are executable
- [ ] Configuration files present in config folders

---

## 📚 Additional Documentation

Once installed, review these documents for detailed information:

1. **QUICK_START.md** - Quick reference guide
2. **DEPLOYMENT_v1.4.0_SUMMARY.md** - Complete system overview
3. **SCHEDULE_VERIFICATION_REPORT.md** - Pipeline timing details
4. **PIPELINE_TRADING_INTEGRATION.md** - Integration architecture
5. **WINDOWS_SCHEDULER_GUIDE.md** - Scheduler management
6. **OVERNIGHT_INDICATORS_FINAL_SUMMARY.md** - Indicator methodology

---

## ⚠️ Important Notes

### Market Hours Verified ✅

All pipeline schedules are **verified correct** as of January 4, 2026:

| Market | Opens | Pipeline Runs | Lead Time | Verified |
|--------|-------|---------------|-----------|----------|
| AU (ASX) | 10:00 AEDT | 07:30 AEDT | 2.5 hours | ✅ |
| US (NYSE) | 09:30 EST | 07:00 EST | 2.5 hours | ✅ |
| UK (LSE) | 08:00 GMT | 05:30 GMT | 2.5 hours | ✅ |

**No conflicts**: Pipelines run at different times with 6-9 hour gaps.

### Paper Trading Only

This system is configured for **paper trading** (simulated trades). 
No real money is at risk. Use for learning and testing strategies.

### System Requirements

- **Minimum**: 4GB RAM, 1GB disk space
- **Recommended**: 8GB RAM, 2GB disk space
- **Internet**: Required for market data

### Support

For issues, refer to:
1. Log files (check for error messages)
2. Documentation files included in package
3. Test scripts to verify configuration

---

## 🎉 You're Ready!

Your Pipeline-Enhanced Trading System is now installed and ready to use.

**Next Steps**:
1. Start the trading system with your chosen market
2. Monitor the logs for pipeline execution
3. Review morning reports for trading signals
4. Adjust configuration as needed

**Happy Trading!** 📈

---

**Version**: 1.4.0  
**Date**: January 4, 2026  
**Status**: Production Ready  
**Platform**: Windows 11 (Windows 10 compatible)
