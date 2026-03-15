# Troubleshooting Guide - Critical Fixes Installer

**Version**: v1.3.15.118.8  
**Date**: 2026-02-12

---

## 🔍 Common Issues & Solutions

### Issue #1: Installer Window Closes Immediately

**Symptoms**:
- Double-click `INSTALL_FIXES.bat`
- Window flashes briefly and closes
- Cannot see installation progress or test results

**Root Cause**:
Windows runs batch files in a temporary console that closes when the script completes.

**Solution #1: Run from Command Prompt (Recommended)**
```cmd
1. Press Win + R
2. Type: cmd
3. Press Enter
4. Navigate to installer:
   cd C:\Temp\critical_fixes_installer
5. Run installer:
   INSTALL_FIXES.bat
```

**Solution #2: Use Standalone Test Script**
```cmd
1. Install fixes first (double-click INSTALL_FIXES.bat)
2. Then run test separately:
   cd C:\Temp\critical_fixes_installer
   RUN_TEST.bat
```
The `RUN_TEST.bat` script keeps the window open so you can see all results.

**Solution #3: Add Extra Pause**
Edit `INSTALL_FIXES.bat` and add `pause` at the very end before `exit /b 0`.

---

### Issue #2: Cannot See Test Results

**Symptoms**:
- Installer completes but test output scrolls too fast
- Cannot verify if fixes are working
- Window closes before reading results

**Solution #1: Run Standalone Test**
```cmd
cd C:\Temp\critical_fixes_installer
RUN_TEST.bat
```
This will pause after test completion.

**Solution #2: Run Test Manually**
```cmd
cd "C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"
python scripts\run_us_full_pipeline.py --mode test
```
This keeps the console open.

**Solution #3: Check Log File**
Test results are saved to:
```
logs\us_full_pipeline.log
```
Open this file in Notepad to see full test output.

---

### Issue #3: "Permission Denied" or "Access Denied"

**Symptoms**:
```
[ERROR] Failed to copy batch_predictor.py
Access is denied.
```

**Root Cause**:
- Files are read-only
- Dashboard is running (files in use)
- Insufficient permissions

**Solution #1: Stop Dashboard**
```cmd
tasklist | findstr python.exe
taskkill /F /PID <pid_number>
```

**Solution #2: Run as Administrator**
```cmd
1. Right-click INSTALL_FIXES.bat
2. Select "Run as administrator"
3. Click Yes on UAC prompt
```

**Solution #3: Check File Properties**
```cmd
1. Navigate to installation directory
2. Right-click the file (e.g., batch_predictor.py)
3. Select Properties
4. Uncheck "Read-only"
5. Click Apply
```

---

### Issue #4: "Directory Does Not Exist"

**Symptoms**:
```
[ERROR] Directory does not exist:
C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED
```

**Root Cause**:
- Path has spaces (not properly quoted)
- Wrong directory path
- Typo in path

**Solution #1: Use Quotes**
When prompted, enter path with quotes:
```
"C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"
```

**Solution #2: Copy-Paste Path**
```cmd
1. Open File Explorer
2. Navigate to dashboard directory
3. Click address bar
4. Ctrl + C to copy path
5. Paste into installer prompt
```

**Solution #3: Use Short Path**
```cmd
dir /x "C:\Users\david\Regime Trading V2"
```
This shows the short (8.3) path without spaces.

---

### Issue #5: "Python Is Not Recognized"

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Root Cause**:
Python not in system PATH

**Solution #1: Use Full Python Path**
```cmd
"C:\Python311\python.exe" scripts\run_us_full_pipeline.py --mode test
```

**Solution #2: Activate Virtual Environment**
```cmd
cd "C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"
venv\Scripts\activate
python scripts\run_us_full_pipeline.py --mode test
```

**Solution #3: Add Python to PATH**
```cmd
1. Win + R → sysdm.cpl
2. Advanced → Environment Variables
3. System Variables → Path → Edit
4. Add: C:\Python311
5. Add: C:\Python311\Scripts
6. OK → OK → OK
7. Restart Command Prompt
```

---

### Issue #6: Still Seeing KeyError 'technical'

**Symptoms**:
```
KeyError: 'technical'
File: pipelines\models\screening\batch_predictor.py, line 411
```

**Root Cause**:
Fix #1 was not installed correctly

**Solution #1: Verify File Date**
```cmd
dir pipelines\models\screening\batch_predictor.py
```
File date should be **2026-02-12** (today)

**Solution #2: Check File Content**
Open `batch_predictor.py` and search for:
```python
if 'technical' not in stock_data:
```
This line should exist at lines 412 and 473.

**Solution #3: Reinstall Fix #1**
```cmd
copy /Y C:\Temp\critical_fixes_installer\fixes\batch_predictor.py pipelines\models\screening\
```

---

### Issue #7: Still Seeing PyTorch Tensor Error

**Symptoms**:
```
RuntimeError: Can't call numpy() on Tensor that requires grad
```

**Root Cause**:
Fix #2 was not installed correctly

**Solution #1: Verify File Date**
```cmd
dir finbert_v4.4.4\models\lstm_predictor.py
```

**Solution #2: Check File Content**
Open `lstm_predictor.py` and search for:
```python
if hasattr(y_pred, 'detach'):
```
This should exist at line 347.

**Solution #3: Reinstall Fix #2**
```cmd
copy /Y C:\Temp\critical_fixes_installer\fixes\lstm_predictor.py finbert_v4.4.4\models\
```

---

### Issue #8: Mobile Launcher Still Crashes

**Symptoms**:
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f
```

**Root Cause**:
Fix #3 was not installed correctly

**Solution #1: Verify Batch File**
Open `START_MOBILE_ACCESS.bat` and check for:
```batch
with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
```

**Solution #2: Reinstall Fix #3**
```cmd
copy /Y C:\Temp\critical_fixes_installer\fixes\START_MOBILE_ACCESS.bat .
```

---

### Issue #9: Still Seeing KeyError 'signal'

**Symptoms**:
```
KeyError: 'signal'
File: scripts\run_us_full_pipeline.py, line 496
```

**Root Cause**:
Fix #4 was not installed correctly

**Solution #1: Verify File Date**
```cmd
dir scripts\run_us_full_pipeline.py
```
File date should be **2026-02-12**

**Solution #2: Check File Content**
Open `run_us_full_pipeline.py` and search for:
```python
signal = opp.get('prediction', opp.get('signal', 'N/A'))
```
This should exist at line 497.

**Solution #3: Reinstall Fix #4**
```cmd
copy /Y C:\Temp\critical_fixes_installer\fixes\run_us_full_pipeline.py scripts\
```

---

### Issue #10: Test Shows "Prediction: None"

**Symptoms**:
```
[1/5] Processed JPM - Prediction: None (Confidence: 0.0%)
[2/5] Processed BAC - Prediction: None (Confidence: 0.0%)
...
```

**Root Cause**:
One or more fixes are not installed, or data fetching is failing

**Solution #1: Verify All Fixes Installed**
```cmd
findstr /C:"if 'technical' not in stock_data" pipelines\models\screening\batch_predictor.py
```
Should return a match.

**Solution #2: Check Internet Connection**
The pipeline needs to fetch stock data from Yahoo Finance.
```cmd
ping finance.yahoo.com
```

**Solution #3: Run with Verbose Logging**
```cmd
python scripts\run_us_full_pipeline.py --mode test --verbose
```

---

### Issue #11: Still Seeing UnicodeEncodeError

**Symptoms**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**Root Cause**:
Windows console encoding is CP1252, not UTF-8

**Solution #1: Enable UTF-8 Console**
```cmd
chcp 65001
python scripts\run_us_full_pipeline.py --mode test
```

**Solution #2: Check if safe_log() Function Exists**
Open `run_us_full_pipeline.py` and search for:
```python
def safe_log(level, message):
```
This should exist at line 150.

**Solution #3: Set Console Font**
```cmd
1. Right-click Command Prompt title bar
2. Properties → Font
3. Select "Consolas" or "Lucida Console"
4. OK
```

---

### Issue #12: Backup Directory Already Exists

**Symptoms**:
```
Cannot create directory: backup_before_fix_20260212_171530
A subdirectory or file already exists.
```

**Root Cause**:
Installer was run multiple times on the same day

**Solution #1: Delete Old Backup**
```cmd
rmdir /S /Q backup_before_fix_20260212_*
```
Then rerun installer.

**Solution #2: Rename Old Backup**
```cmd
ren backup_before_fix_20260212_171530 backup_before_fix_20260212_171530_old
```

**Solution #3: Manual Backup**
```cmd
mkdir backup_manual
copy pipelines\models\screening\batch_predictor.py backup_manual\
copy finbert_v4.4.4\models\lstm_predictor.py backup_manual\
copy START_MOBILE_ACCESS.bat backup_manual\
copy scripts\run_us_full_pipeline.py backup_manual\
```

---

### Issue #13: Test Takes Too Long

**Symptoms**:
- Test is running for more than 5 minutes
- Seems stuck on one stock
- No progress shown

**Root Cause**:
- Slow internet connection
- Yahoo Finance API throttling
- Large historical data download

**Solution #1: Be Patient**
First run may take 3-5 minutes to download data.

**Solution #2: Check Progress in Log**
Open another Command Prompt:
```cmd
tail -f logs\us_full_pipeline.log
```
(or use `type logs\us_full_pipeline.log` repeatedly)

**Solution #3: Cancel and Retry**
```cmd
Ctrl + C
python scripts\run_us_full_pipeline.py --mode test
```

---

### Issue #14: How to Rollback Fixes

**Symptoms**:
- Want to restore original files
- Fixes caused new issues
- Need to revert changes

**Solution #1: Use Automatic Backup**
```cmd
cd "C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"

REM Find backup directory
dir backup_before_fix_*

REM Restore files (replace YYYYMMDD_HHMMSS with actual timestamp)
copy backup_before_fix_YYYYMMDD_HHMMSS\batch_predictor.py.bak pipelines\models\screening\batch_predictor.py
copy backup_before_fix_YYYYMMDD_HHMMSS\lstm_predictor.py.bak finbert_v4.4.4\models\lstm_predictor.py
copy backup_before_fix_YYYYMMDD_HHMMSS\START_MOBILE_ACCESS.bat.bak START_MOBILE_ACCESS.bat
copy backup_before_fix_YYYYMMDD_HHMMSS\run_us_full_pipeline.py.bak scripts\run_us_full_pipeline.py
```

**Solution #2: Use Git (if available)**
```cmd
git status
git checkout pipelines\models\screening\batch_predictor.py
git checkout finbert_v4.4.4\models\lstm_predictor.py
git checkout START_MOBILE_ACCESS.bat
git checkout scripts\run_us_full_pipeline.py
```

---

## 📞 Need More Help?

### Step 1: Gather Information
```cmd
REM Check Python version
python --version

REM Check installed packages
pip list | findstr "torch numpy pandas"

REM Check log file
type logs\us_full_pipeline.log | more
```

### Step 2: Check Documentation
- `docs\ALL_FOUR_BUGS_FIXED_COMPLETE_SUMMARY.md` - Complete overview
- `docs\BATCH_PREDICTOR_FIX_v1.3.15.118.5.md` - Fix #1 details
- `docs\LSTM_PYTORCH_TENSOR_FIX_v1.3.15.118.6.md` - Fix #2 details
- `docs\MOBILE_LAUNCHER_UNICODE_FIX_v1.3.15.118.7.md` - Fix #3 details
- `docs\PIPELINE_DISPLAY_FIX_v1.3.15.118.8.md` - Fix #4 details

### Step 3: Verify Installation
Run comprehensive verification:
```cmd
cd "C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"

echo === Checking Fix #1 ===
findstr /C:"if 'technical' not in stock_data" pipelines\models\screening\batch_predictor.py
if errorlevel 1 (echo [X] Fix #1 NOT installed) else (echo [✓] Fix #1 installed)

echo === Checking Fix #2 ===
findstr /C:"if hasattr(y_pred, 'detach')" finbert_v4.4.4\models\lstm_predictor.py
if errorlevel 1 (echo [X] Fix #2 NOT installed) else (echo [✓] Fix #2 installed)

echo === Checking Fix #3 ===
findstr /C:"with open('unified_trading_dashboard.py', 'r', encoding='utf-8')" START_MOBILE_ACCESS.bat
if errorlevel 1 (echo [X] Fix #3 NOT installed) else (echo [✓] Fix #3 installed)

echo === Checking Fix #4 ===
findstr /C:"signal = opp.get('prediction'" scripts\run_us_full_pipeline.py
if errorlevel 1 (echo [X] Fix #4 NOT installed) else (echo [✓] Fix #4 installed)
```

---

**Version**: v1.3.15.118.8  
**Last Updated**: 2026-02-12  
**Status**: ✅ Production Ready
