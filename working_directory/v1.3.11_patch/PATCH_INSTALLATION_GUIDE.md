# v1.3.11 Calibration Fix - Patch Installation Guide

**Version:** v1.3.11 PATCH  
**Date:** January 2, 2026  
**Patch Type:** Critical Calibration Fix  
**Estimated Installation Time:** 2 minutes

---

## 📋 What This Patch Fixes

### Critical Issue Resolved:
Market performance charts were calculating percentage change from **market open** instead of **previous day's close**, causing discrepancies with official market figures.

### Before (v1.3.10):
- ❌ NASDAQ showed incorrect % at close
- ❌ S&P 500 showed incorrect % at close
- ❌ FTSE 100 showed incorrect % at close

### After (v1.3.11 Patch):
- ✅ NASDAQ shows accurate daily % (e.g., -0.03%)
- ✅ S&P 500 shows accurate daily % (e.g., +0.66%)
- ✅ FTSE 100 shows accurate daily % (e.g., +0.2%)

---

## 📦 What's Included

```
v1.3.11_patch/
├── PATCH_INSTALLATION_GUIDE.md (this file)
├── V1.3.11_CALIBRATION_FIX.md (detailed documentation)
└── phase3_intraday_deployment/
    └── unified_trading_dashboard.py (updated file)
```

---

## ⚙️ Prerequisites

### Required:
- ✅ Existing installation of v1.3.10 (or v1.3.8, v1.3.9)
- ✅ Dashboard must be stopped before applying patch

### Optional:
- Backup of current installation (recommended)

---

## 🚀 Installation Steps

### Step 1: Stop the Dashboard

**Windows:**
```batch
REM Close the dashboard window or press Ctrl+C
```

**Linux/Mac:**
```bash
# Find and stop the dashboard process
pkill -f unified_trading_dashboard
```

### Step 2: Backup Current File (Recommended)

**Navigate to your installation directory:**
```batch
cd C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
```

**Backup the current file:**
```batch
copy unified_trading_dashboard.py unified_trading_dashboard.py.v1.3.10.backup
```

### Step 3: Extract Patch Package

**Extract the patch ZIP file:**
```
v1.3.11_calibration_patch.zip
```

**You should see:**
```
v1.3.11_patch/
├── PATCH_INSTALLATION_GUIDE.md
├── V1.3.11_CALIBRATION_FIX.md
└── phase3_intraday_deployment/
    └── unified_trading_dashboard.py
```

### Step 4: Copy Updated File

**Copy the updated file to your installation:**

**Windows:**
```batch
REM From the extracted patch folder
copy phase3_intraday_deployment\unified_trading_dashboard.py C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment\
```

**When prompted "Overwrite existing file?"**
```
Type: Y (Yes)
```

**Linux/Mac:**
```bash
cp phase3_intraday_deployment/unified_trading_dashboard.py ~/Trading/phase3_trading_system_v1.3.10/phase3_intraday_deployment/
```

### Step 5: Verify File Replacement

**Check file size/date:**
```batch
dir unified_trading_dashboard.py
```

**Should show:**
- Modified date: January 2, 2026
- File size: ~37 KB

### Step 6: Restart Dashboard

**Windows:**
```batch
cd C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
START_UNIFIED_DASHBOARD.bat
```

**Linux/Mac:**
```bash
cd ~/Trading/phase3_trading_system_v1.3.10/phase3_intraday_deployment
python unified_trading_dashboard.py
```

### Step 7: Verify Dashboard Startup

**Open browser:**
```
http://localhost:8050
```

**Check console/logs for:**
```
✅ Dash is running on http://0.0.0.0:8050/
✅ No errors in startup
✅ Dashboard loads successfully
```

---

## ✅ Verification Steps

### 1. Check Market Performance Chart

**Look for:**
- ✅ Chart shows 4 indices (ASX, S&P 500, NASDAQ, FTSE)
- ✅ Lines show intraday movement
- ✅ GMT time axis (00:00 - 24:00)
- ✅ % axis on right side

### 2. Verify Hover Tooltip

**Hover over any line:**
```
Expected tooltip:
-----------------
NASDAQ
Time (GMT): 14:30
Change from Prev Close: -0.03%  ✅ (New in v1.3.11)
```

### 3. Check Daily % at Market Close

**Compare dashboard figures with official sources:**

| Index | Dashboard | Yahoo Finance | Status |
|-------|-----------|---------------|--------|
| NASDAQ | -0.03% | -0.03% | ✅ MATCH |
| S&P 500 | +0.66% | +0.66% | ✅ MATCH |
| FTSE 100 | +0.2% | +0.2% | ✅ MATCH |

### 4. Check Auto-Refresh

**Wait 5-10 seconds:**
- ✅ Chart updates automatically
- ✅ New data points appear
- ✅ No errors in console

---

## 🔧 Troubleshooting

### Issue: "File not found" error

**Solution:**
```batch
REM Verify you're in the correct directory
cd C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
dir unified_trading_dashboard.py
```

### Issue: Dashboard won't start

**Solution:**
```batch
REM Check if old process is still running
tasklist | findstr python

REM If found, kill it
taskkill /F /IM python.exe
```

### Issue: Chart still shows wrong percentages

**Solution:**
1. **Clear browser cache** (Ctrl+F5)
2. **Restart dashboard** completely
3. **Verify file was replaced** (check file date)

### Issue: Import errors on startup

**Solution:**
```batch
REM Reinstall dependencies
pip install --upgrade yfinance plotly dash pytz
```

---

## 📊 What Changed Technically

### Code Changes (Lines 374-413):

**Before (v1.3.10):**
```python
# WRONG - calculated from market open
first_price = market_hours_data['Close'].iloc[0]
pct_change = ((row['Close'] - first_price) / first_price) * 100
```

**After (v1.3.11):**
```python
# CORRECT - calculated from previous close
previous_day_data = hist[hist.index.date < latest_date]
previous_close = previous_day_data['Close'].iloc[-1]
pct_change = ((row['Close'] - previous_close) / previous_close) * 100
```

### Hover Tooltip Update:
```python
# Updated hover template
"Change from Prev Close: %{y:.2f}%<br>"
```

---

## 📝 Rollback Instructions (If Needed)

### If you need to revert to v1.3.10:

**Step 1: Stop dashboard**
```batch
REM Press Ctrl+C in dashboard window
```

**Step 2: Restore backup**
```batch
cd C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
copy unified_trading_dashboard.py.v1.3.10.backup unified_trading_dashboard.py
```

**Step 3: Restart dashboard**
```batch
START_UNIFIED_DASHBOARD.bat
```

---

## 📚 Additional Documentation

### Included Files:
- **V1.3.11_CALIBRATION_FIX.md** - Detailed technical documentation
  - Problem analysis
  - Solution implementation
  - Testing results
  - Verification steps

### Online Resources:
- Live Dashboard: https://8050-ii2gw7ksw18yooppf5y8p-6532622b.e2b.dev
- GitHub Repository: (if available)

---

## ✅ Post-Installation Checklist

After installing the patch, verify:

- [ ] Dashboard starts without errors
- [ ] Market performance chart displays 4 indices
- [ ] Hover tooltip shows "Change from Prev Close"
- [ ] Daily % matches official market close figures
- [ ] Auto-refresh works (updates every 5 seconds)
- [ ] GMT time axis displays correctly
- [ ] ML Signals panel still works
- [ ] Trading functionality unaffected

---

## 🎯 Support

### If you encounter issues:

1. **Check logs:**
   ```
   logs/unified_trading.log
   ```

2. **Review documentation:**
   ```
   V1.3.11_CALIBRATION_FIX.md
   ```

3. **Verify prerequisites:**
   - Python 3.8+
   - All dependencies installed
   - Previous version was v1.3.10 or compatible

---

## 📋 Summary

### What This Patch Does:
✅ Fixes market performance percentage calculations  
✅ Changes reference from market open to previous close  
✅ Ensures accuracy with official market figures  
✅ Updates hover tooltips for clarity  

### Installation Time:
⏱️ **2 minutes** (stop, backup, copy, restart)

### Risk Level:
🟢 **LOW** - Only updates chart calculation logic

### Required Downtime:
⏸️ **30 seconds** (stop and restart dashboard)

### Compatibility:
✅ Works with v1.3.10, v1.3.9, v1.3.8 installations

---

## ✅ Installation Complete

After following these steps, your dashboard will show accurate market performance percentages matching official figures from Bloomberg, Yahoo Finance, and exchange websites.

**Welcome to v1.3.11!** 🎉

---

**Created:** January 2, 2026  
**Patch Version:** v1.3.11  
**Type:** Calibration Fix  
**Status:** Production Ready ✅
