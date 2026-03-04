# Automated Pipeline Scheduler - Windows 11 Deployment

**Date**: January 3, 2026  
**Platform**: Windows 11  
**Status**: ✅ PRODUCTION READY  

---

## 🎯 OVERVIEW

Automatically runs overnight pipeline reports **2.5 hours before each market opens**, ensuring fresh sentiment analysis is available for your automated trading system.

### **Execution Schedule**

| Market | Opens At | Pipeline Runs At | Lead Time |
|--------|----------|------------------|-----------|
| **Australia (AU)** | 10:00 AEDT | **07:30 AEDT** | 2.5 hours |
| **United States (US)** | 09:30 EST | **07:00 EST** | 2.5 hours |
| **United Kingdom (UK)** | 08:00 GMT | **05:30 GMT** | 2.5 hours |

---

## 📁 FILES PROVIDED

### **Core Scheduler**
- `pipeline_scheduler.py` - Main scheduler daemon (Python)

### **Windows Batch Scripts**
1. **START_PIPELINE_SCHEDULER.bat** - Start scheduler (console visible)
2. **START_SCHEDULER_BACKGROUND.bat** - Start scheduler (hidden, background)
3. **STOP_PIPELINE_SCHEDULER.bat** - Stop scheduler
4. **SETUP_WINDOWS_TASK.bat** - Setup Windows Task Scheduler (auto-start)
5. **TEST_PIPELINE_SCHEDULER.bat** - Test schedule without execution
6. **RUN_PIPELINES_ONCE.bat** - Manual one-time execution

---

## 🚀 QUICK START

### **Option 1: Run Manually (Visible Console)**

**Best for**: Testing, monitoring, manual control

```batch
# Double-click or run from Command Prompt:
START_PIPELINE_SCHEDULER.bat

# Or for specific markets:
START_PIPELINE_SCHEDULER.bat UK          # UK only
START_PIPELINE_SCHEDULER.bat AU,US       # AU and US
```

**What happens**:
- Console window opens and stays visible
- Shows real-time logs
- Press Ctrl+C to stop
- Logs saved to `logs\pipeline_scheduler.log`

---

### **Option 2: Run in Background (Hidden)**

**Best for**: Daily use, background operation

```batch
# Double-click or run:
START_SCHEDULER_BACKGROUND.bat

# Or for specific markets:
START_SCHEDULER_BACKGROUND.bat UK
```

**What happens**:
- Runs silently in background (no console window)
- Uses `pythonw.exe` (windowless Python)
- Logs saved to `logs\pipeline_scheduler.log`

**To Stop**:
```batch
STOP_PIPELINE_SCHEDULER.bat
```

---

### **Option 3: Windows Task Scheduler (Auto-Start)**

**Best for**: Production use, automatic startup with Windows

#### **Setup (One-Time)**

1. **Run as Administrator**:
   - Right-click `SETUP_WINDOWS_TASK.bat`
   - Select "Run as administrator"

2. **Follow prompts**:
   - Creates task named: `PipelineScheduler_AutoTrading`
   - Trigger: At system startup
   - Runs in background automatically

3. **Done!**
   - Scheduler starts automatically when Windows boots
   - No manual intervention needed

#### **Management**

**View Task**:
```batch
# Open Task Scheduler
taskschd.msc

# Find task: PipelineScheduler_AutoTrading
```

**Start/Stop Manually**:
```batch
# Start
schtasks /run /tn "PipelineScheduler_AutoTrading"

# Stop
STOP_PIPELINE_SCHEDULER.bat
```

**Remove Task**:
```batch
schtasks /delete /tn "PipelineScheduler_AutoTrading" /f
```

---

## 🧪 TESTING

### **Test Schedule (No Execution)**

```batch
# Double-click:
TEST_PIPELINE_SCHEDULER.bat
```

**Output Example**:
```
================================================================================
TESTING SCHEDULE (NO EXECUTION)
================================================================================

Australia (AU):
  Timezone: Australia/Sydney
  Current Time: 2026-01-04 09:21:51 AEDT
  Market Opens: 10:00:00 (in 0h 38m)
  Pipeline Runs: 07:30:00 (in 22h 8m)
  Lead Time: 2.5 hours
  Script: run_au_morning_report.py
  Script Exists: ✓

United States (US):
  Timezone: America/New_York
  Current Time: 2026-01-03 17:21:51 EST
  Market Opens: 09:30:00 (in 16h 8m)
  Pipeline Runs: 07:00:00 (in 13h 38m)
  Lead Time: 2.5 hours
  Script: run_us_morning_report.py
  Script Exists: ✓

United Kingdom (UK):
  Timezone: Europe/London
  Current Time: 2026-01-03 22:21:51 GMT
  Market Opens: 08:00:00 (in 9h 38m)
  Pipeline Runs: 05:30:00 (in 7h 8m)
  Lead Time: 2.5 hours
  Script: run_uk_morning_report.py
  Script Exists: ✓
```

### **Run Pipelines Once (Manual)**

```batch
# Double-click:
RUN_PIPELINES_ONCE.bat

# Or specific markets:
RUN_PIPELINES_ONCE.bat UK
RUN_PIPELINES_ONCE.bat AU,US,UK
```

**Use Cases**:
- Testing pipeline execution
- Running outside scheduled times
- Forcing a fresh report

---

## 📊 MONITORING & LOGS

### **Log File Location**
```
logs\pipeline_scheduler.log
```

### **View Logs (Real-Time)**
```batch
# Command Prompt:
type logs\pipeline_scheduler.log

# Or use Notepad++, VSCode, etc.
```

### **Log Contents**
```
2026-01-04 07:30:00 - INFO - SCHEDULED EXECUTION: Australia
2026-01-04 07:30:00 - INFO - RUNNING Australia (AU) PIPELINE
2026-01-04 07:30:05 - INFO - ✓ Australia pipeline completed successfully
2026-01-04 07:30:05 - INFO - Pipeline output (last 10 lines):
2026-01-04 07:30:05 - INFO -   Total Stocks Scanned: 100
2026-01-04 07:30:05 - INFO -   Top Opportunities: 15
2026-01-04 07:30:05 - INFO -   Report Location: reports/au/morning_report_20260104.html
```

### **Check If Running**
```batch
# Command Prompt:
tasklist | findstr pythonw.exe
tasklist | findstr python.exe
```

---

## ⚙️ CONFIGURATION

### **Modify Schedule Times**

Edit `pipeline_scheduler.py`:

```python
# Line ~90-110: MarketSchedule configurations

'AU': MarketSchedule(
    name='Australia',
    code='AU',
    timezone='Australia/Sydney',
    market_open=dt_time(10, 0),       # 10:00 AEDT
    pipeline_offset_hours=2.5,        # Run 2.5 hours before
    script_path=scripts_path / 'run_au_morning_report.py'
),
```

**Change `pipeline_offset_hours`**:
- `2.5` = 2 hours 30 minutes before open (default)
- `3.0` = 3 hours before open
- `2.0` = 2 hours before open
- `1.5` = 1 hour 30 minutes before open

### **Enable/Disable Markets**

```python
# Add to MarketSchedule:
enabled: bool = True  # Change to False to disable
```

### **Customize Retry Logic**

Currently: If pipeline fails, it logs the error and waits until next scheduled time.

To add retries, modify `_run_pipeline()` method in `pipeline_scheduler.py`.

---

## 🔧 TROUBLESHOOTING

### **Problem: Task doesn't start automatically**

**Solution**:
1. Open Task Scheduler (`taskschd.msc`)
2. Find `PipelineScheduler_AutoTrading`
3. Right-click → Properties
4. Check "Run whether user is logged on or not"
5. Check "Run with highest privileges"
6. Triggers tab: Verify "At startup" is enabled

### **Problem: Python not found**

**Solution**:
```batch
# Add Python to PATH or use full path in batch file
# Edit START_PIPELINE_SCHEDULER.bat:
"C:\Python311\python.exe" pipeline_scheduler.py --daemon
```

### **Problem: Schedule package not installed**

**Solution**:
```batch
pip install schedule
```

### **Problem: Pipeline fails to run**

**Check**:
1. Script paths correct: `pipeline_trading/scripts/run_*_morning_report.py`
2. Pipeline_trading project exists
3. Dependencies installed (yfinance, pandas, etc.)
4. Check logs: `logs\pipeline_scheduler.log`

### **Problem: Can't stop scheduler**

**Solution**:
```batch
# Force kill all Python processes
taskkill /f /im python.exe
taskkill /f /im pythonw.exe

# Or reboot Windows
```

---

## 🌐 INTEGRATION WITH TRADING SYSTEM

The scheduler automatically runs pipeline reports before market open. The trading system can then use these results:

### **Workflow**

```
05:30 GMT → UK Pipeline runs
            └─ Generates sentiment score (0-100)
            └─ Creates morning report
            └─ Saves to reports/uk/

07:00 EST → US Pipeline runs
            └─ Generates sentiment score
            └─ Creates morning report
            └─ Saves to reports/us/

07:30 AEDT → AU Pipeline runs
             └─ Generates sentiment score
             └─ Creates morning report
             └─ Saves to reports/au/

08:00 GMT → UK Market opens
            └─ Trading system reads sentiment
            └─ Generates signals via pipeline_signal_adapter
            └─ Opens positions via run_pipeline_enhanced_trading.py

09:30 EST → US Market opens
            └─ Trading system reads sentiment
            └─ Generates signals
            └─ Opens positions

10:00 AEDT → AU Market opens
             └─ Trading system reads sentiment
             └─ Generates signals
             └─ Opens positions
```

### **Manual Override**

If you want to force a fresh report:
```batch
# Run pipeline manually
RUN_PIPELINES_ONCE.bat UK

# Then immediately start trading
python run_pipeline_enhanced_trading.py --market UK --capital 100000
```

---

## 📋 COMMAND REFERENCE

### **Start Scheduler**
```batch
START_PIPELINE_SCHEDULER.bat              # All markets, visible console
START_PIPELINE_SCHEDULER.bat UK           # UK only
START_PIPELINE_SCHEDULER.bat AU,US        # AU and US only

START_SCHEDULER_BACKGROUND.bat            # All markets, hidden
START_SCHEDULER_BACKGROUND.bat UK         # UK only, hidden
```

### **Stop Scheduler**
```batch
STOP_PIPELINE_SCHEDULER.bat               # Stop gracefully
taskkill /f /im pythonw.exe               # Force stop
```

### **Test & Manual Run**
```batch
TEST_PIPELINE_SCHEDULER.bat               # Test schedule (no execution)
RUN_PIPELINES_ONCE.bat                    # Run all markets once
RUN_PIPELINES_ONCE.bat UK                 # Run UK once
```

### **Windows Task Setup**
```batch
SETUP_WINDOWS_TASK.bat                    # Create auto-start task (run as admin)
schtasks /run /tn "PipelineScheduler_AutoTrading"     # Start task
schtasks /delete /tn "PipelineScheduler_AutoTrading"  # Remove task
```

### **Python Direct Commands**
```batch
python pipeline_scheduler.py --test       # Test schedule
python pipeline_scheduler.py --once       # Run all once
python pipeline_scheduler.py --once --market UK       # Run UK once
python pipeline_scheduler.py --daemon     # Start scheduler
python pipeline_scheduler.py --daemon --markets AU,US # Specific markets
```

---

## 🎯 RECOMMENDED SETUP FOR WINDOWS 11

### **For Daily Trading (Production)**

1. **One-Time Setup**:
   ```batch
   # Right-click → Run as administrator
   SETUP_WINDOWS_TASK.bat
   ```

2. **Verify**:
   ```batch
   TEST_PIPELINE_SCHEDULER.bat
   ```

3. **Done!**
   - Scheduler starts automatically when Windows boots
   - Runs in background (no console window)
   - Executes pipelines 2.5 hours before market open
   - Logs all activity

### **For Testing/Development**

```batch
# Manual control with visible console
START_PIPELINE_SCHEDULER.bat

# Watch logs in real-time
# Press Ctrl+C to stop when done
```

### **For Quick Manual Reports**

```batch
# Force run a fresh report anytime
RUN_PIPELINES_ONCE.bat UK
```

---

## 📊 SUCCESS CRITERIA

**Scheduler is working correctly when**:
- ✅ Scripts execute at scheduled times (check logs)
- ✅ Pipeline reports generated in `pipeline_trading/reports/`
- ✅ No errors in `logs/pipeline_scheduler.log`
- ✅ Market sentiment available before trading starts
- ✅ Task runs automatically after Windows restart (if using Task Scheduler)

---

## 🔐 SECURITY NOTES

**Windows Task Scheduler**:
- Task runs with your user account privileges
- No password stored if "Run only when user is logged on" is selected
- For "Run whether user is logged on or not", Windows will prompt for password once

**Background Execution**:
- Uses standard Windows processes (python.exe/pythonw.exe)
- No elevated privileges required for normal operation
- Logs stored in user directory (not system-wide)

---

## 📝 SUMMARY

**Implementation**: ✅ Complete  
**Platform**: Windows 11  
**Automation**: Fully automated with Task Scheduler  
**Manual Control**: Multiple batch scripts for flexibility  
**Monitoring**: Comprehensive logging  
**Integration**: Seamless with pipeline trading system  

**Files Delivered**:
1. `pipeline_scheduler.py` (Python daemon)
2. `START_PIPELINE_SCHEDULER.bat` (Manual start)
3. `START_SCHEDULER_BACKGROUND.bat` (Background start)
4. `STOP_PIPELINE_SCHEDULER.bat` (Stop scheduler)
5. `SETUP_WINDOWS_TASK.bat` (Auto-start setup)
6. `TEST_PIPELINE_SCHEDULER.bat` (Test mode)
7. `RUN_PIPELINES_ONCE.bat` (Manual execution)

**Next Steps**:
1. Run `SETUP_WINDOWS_TASK.bat` as administrator
2. Verify with `TEST_PIPELINE_SCHEDULER.bat`
3. Let it run automatically each morning
4. Check logs occasionally: `logs\pipeline_scheduler.log`

---

**Your pipeline reports will now run automatically 2.5 hours before each market opens!** 🚀

---

**Document**: `WINDOWS_SCHEDULER_GUIDE.md`  
**Version**: 1.0.0  
**Date**: 2026-01-03  
**Platform**: Windows 11
