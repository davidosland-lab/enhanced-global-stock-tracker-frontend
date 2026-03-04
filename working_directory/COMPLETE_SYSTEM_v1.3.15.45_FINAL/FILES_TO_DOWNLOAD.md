# FILES TO DOWNLOAD FROM SANDBOX
## For Windows Deployment
**Date**: 2026-02-03
**Status**: Ready to copy

---

## 🎯 QUICK ANSWER

**You need to copy 3 core files from sandbox to Windows:**

1. `unified_trading_dashboard.py` (69K)
2. `paper_trading_coordinator.py` (73K)  
3. `sentiment_integration.py` (17K)

**Plus 2 data files:**

4. `state/paper_trading_state.json` (714 bytes)
5. `reports/screening/au_morning_report.json` (1.3K)

---

## 📂 FILE LOCATIONS

### In Sandbox (Source)
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/
```

### On Windows (Destination)
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
```

---

## 📋 DETAILED FILE LIST

### 1. unified_trading_dashboard.py ✅ ESSENTIAL
**Sandbox Path**:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/unified_trading_dashboard.py
```

**Windows Path**:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\unified_trading_dashboard.py
```

**Size**: 69 KB
**Version**: v1.3.15.86
**Contains**:
- ✅ Trading Controls Panel (Confidence, Stop Loss, Force Trade)
- ✅ State validation (prevents empty state)
- ✅ Morning report integration
- ✅ Live price updates every 5 seconds

**What Changed**:
- Lines 642-710: New Trading Controls Panel
- Lines 1547-1630: Callback functions for controls
- Added state validation in `load_state()`

---

### 2. paper_trading_coordinator.py ✅ ESSENTIAL
**Sandbox Path**:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/paper_trading_coordinator.py
```

**Windows Path**:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\paper_trading_coordinator.py
```

**Size**: 73 KB
**Version**: v1.3.15.85
**Contains**:
- ✅ Atomic state writes (crash-safe)
- ✅ Backup before save
- ✅ Error recovery

**What Changed**:
- `save_state()` now uses atomic writes
- Creates temporary file, then atomically replaces
- Prevents 0-byte corruption

---

### 3. sentiment_integration.py ✅ ESSENTIAL
**Sandbox Path**:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/sentiment_integration.py
```

**Windows Path**:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\sentiment_integration.py
```

**Size**: 17 KB
**Version**: v1.3.15.84
**Contains**:
- ✅ Smart morning report search
- ✅ Handles both dated and non-dated files
- ✅ Graceful fallback

**What Changed**:
- `load_morning_sentiment()` now searches:
  1. Canonical: `au_morning_report.json`
  2. Dated fallback: `au_morning_report_*.json`
- No more "report not found" errors

---

### 4. state/paper_trading_state.json 📊 DATA FILE
**Sandbox Path**:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/state/paper_trading_state.json
```

**Windows Path**:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\state\paper_trading_state.json
```

**Size**: 714 bytes
**Version**: v1.3.15.85
**Purpose**: 
- Initial valid state file (was 0 bytes!)
- Prevents empty state on first load

**Note**: This will be regenerated, but copying it ensures a valid starting state.

---

### 5. reports/screening/au_morning_report.json 📊 DATA FILE
**Sandbox Path**:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/reports/screening/au_morning_report.json
```

**Windows Path**:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\reports\screening\au_morning_report.json
```

**Size**: 1.3 KB
**Purpose**: 
- Fresh morning report (0.0 hours old)
- Market sentiment data

**Note**: Run `run_au_pipeline_v1.3.13.py` on Windows to generate fresh reports daily.

---

## 🎯 OPTIONAL DOCUMENTATION FILES

### Worth Copying (for reference):
```
COMPLETE_FIX_SUMMARY_v84_v85_v86.md     (14K) - Complete fix documentation
CURRENT_STATUS.md                        (6K)  - Current status
TRADING_CONTROLS_GUIDE_v86.md           (12K) - How to use controls
QUICKSTART_v85.md                        (8K)  - Quick start guide
```

### Sandbox Paths:
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/COMPLETE_FIX_SUMMARY_v84_v85_v86.md
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/CURRENT_STATUS.md
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/TRADING_CONTROLS_GUIDE_v86.md
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/QUICKSTART_v85.md
```

---

## 🚀 HOW TO COPY FILES

### Method 1: Using GenSpark File Download (Easiest)

1. In GenSpark, locate the file browser/download feature
2. Navigate to: `/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/`
3. Select and download each file
4. Copy to Windows destination

### Method 2: Git Pull (Fastest)

```batch
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
git fetch origin market-timing-critical-fix
git checkout market-timing-critical-fix
git pull origin market-timing-critical-fix
```

This gets ALL files at once.

### Method 3: Copy/Paste Contents

I can show you the contents of each file, and you can copy/paste into:
```
Notepad++, VSCode, or any text editor
```

Then save to the Windows paths.

---

## ✅ VERIFICATION AFTER COPYING

### Check File Sizes
```batch
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
dir unified_trading_dashboard.py    (should be ~69 KB)
dir paper_trading_coordinator.py    (should be ~73 KB)
dir sentiment_integration.py        (should be ~17 KB)
dir state\paper_trading_state.json  (should be 714 bytes, not 0!)
```

### Check Content
```batch
type state\paper_trading_state.json | findstr "timestamp"
```
Should show a timestamp, not empty.

### Start Dashboard
```batch
START.bat
```
OR
```batch
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000
```

### Access
```
http://localhost:8050
```

---

## 🎯 CRITICAL FILES CHECKLIST

Before starting dashboard, verify:

- [ ] `unified_trading_dashboard.py` exists (69K)
- [ ] `paper_trading_coordinator.py` exists (73K)
- [ ] `sentiment_integration.py` exists (17K)
- [ ] `state/paper_trading_state.json` exists (714 bytes, not 0!)
- [ ] `reports/screening/au_morning_report.json` exists (1.3K)

If all checked, you're ready to run!

---

## 📞 QUICK REFERENCE

### Sandbox Working Directory
```
/home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL/
```

### Windows Working Directory
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
```

### GitHub Branch
```
market-timing-critical-fix
```

### Dashboard URL (after starting)
```
http://localhost:8050
```

---

## 🎉 SUMMARY

**Minimum files needed**: 3 Python files + 2 data files = 5 files total

**Essential**:
1. unified_trading_dashboard.py
2. paper_trading_coordinator.py
3. sentiment_integration.py
4. state/paper_trading_state.json
5. reports/screening/au_morning_report.json

**Optional**: Documentation files (for reference)

**Fastest method**: Git pull

**Most reliable**: Copy files individually

---

**Ready to proceed?** Let me know which copy method you prefer, and I can assist! 🚀
