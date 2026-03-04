# 🔧 ASX Chart Fix Patch - v1.3.15.24

**Quick patch to fix ASX All Ordinaries chart issue**

---

## 🎯 What This Fixes

**Issue:** ASX All Ords line shows flat at 0% after 21:00 GMT instead of showing actual performance (e.g., 0.7% gain)

**Fix:** Updates ASX market hours from 00:00-06:00 GMT to 23:00-05:00 GMT to correctly capture Sydney trading session

---

## 📦 What's Included

```
patch_v1.3.15.24/
├── unified_trading_dashboard.py  (51 KB) - Fixed file
├── APPLY_PATCH.bat                       - Windows installer
├── APPLY_PATCH.sh                        - Linux/Mac installer
└── README.md                             - This file
```

**Total patch size:** ~60 KB (vs 881 KB for full package!)

---

## 🚀 Quick Installation

### Windows:

1. **Extract patch ZIP** to a temporary folder
2. **Copy patch files** to your installation directory:
   ```
   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\
   ```
3. **Stop the dashboard** if it's running (Ctrl+C)
4. **Run:** `APPLY_PATCH.bat`
5. **Restart dashboard:** `LAUNCH_COMPLETE_SYSTEM.bat` → Option 7

### Linux/Mac:

1. **Extract patch ZIP**
2. **Copy to installation directory**
3. **Stop dashboard** if running
4. **Run:** `chmod +x APPLY_PATCH.sh && ./APPLY_PATCH.sh`
5. **Restart dashboard**

---

## 📋 Manual Installation (If Scripts Don't Work)

If the automatic scripts don't work, you can apply the patch manually:

### Step 1: Backup Current File
```bash
# Windows
copy unified_trading_dashboard.py unified_trading_dashboard.py.backup

# Linux/Mac
cp unified_trading_dashboard.py unified_trading_dashboard.py.backup
```

### Step 2: Replace File
```bash
# Copy the new file from patch folder
copy patch_v1.3.15.24\unified_trading_dashboard.py .
```

### Step 3: Verify Syntax
```bash
python -m py_compile unified_trading_dashboard.py
```

Should complete without errors.

### Step 4: Restart Dashboard
```bash
LAUNCH_COMPLETE_SYSTEM.bat → Option 7
```

---

## ✅ How to Verify the Fix

After applying patch and restarting:

1. **Open dashboard:** http://localhost:8050
2. **Check the 24-Hour Market Performance chart**
3. **Look for ASX All Ords (cyan line)**

**Before patch:**
- Activity shown 15:00-20:00 GMT (wrong)
- Flat line at 0% after 21:00 GMT

**After patch:**
- Activity shown 23:00-05:00 GMT (correct Sydney hours)
- Proper % change displayed (e.g., +0.7%)
- No flat lines!

---

## 🔧 Technical Details

### Changes Made

**File:** `unified_trading_dashboard.py`

**Lines changed:** ~20 lines in the `create_market_performance_chart()` function

**Specific changes:**
1. ASX market_open: `0` → `23` (23:00 GMT)
2. ASX market_close: `6` → `5` (05:00 GMT)
3. Added `'spans_midnight': True` flag
4. Updated filter logic to handle midnight-spanning sessions

### Why This Was Needed

**Sydney Trading Hours:**
- Local time: 10:00 AM - 4:00 PM AEDT (UTC+11)
- GMT equivalent: 23:00 (prev day) - 05:00 (current day)

The old code used 00:00-06:00 GMT which:
- Missed the evening session (23:00-00:00)
- Included an extra hour after close (05:00-06:00)
- Caused incorrect % calculations

---

## 🔄 Rollback Instructions

If you need to undo the patch:

```bash
# Windows
copy unified_trading_dashboard.py.backup unified_trading_dashboard.py

# Linux/Mac
cp unified_trading_dashboard.py.backup unified_trading_dashboard.py
```

Then restart the dashboard.

---

## 📊 Expected Results

### ASX All Ords Chart Timeline (GMT)

```
Before Patch:
15:00 ──▲──▲─── 21:00 ────────── 08:00
        Wrong timing   Flat at 0%

After Patch:
23:00 ──▲──▲──▲─── 05:00
   Full Sydney Session
   Correct % change
```

### Other Markets (Unchanged)

- **S&P 500:** 14:30-21:00 GMT ✅
- **NASDAQ:** 14:30-21:00 GMT ✅
- **FTSE 100:** 08:00-16:30 GMT ✅

---

## 🆘 Troubleshooting

### Issue: Script won't run
**Solution:** Run manually (see Manual Installation above)

### Issue: Syntax error after patch
**Solution:** 
1. Check you extracted the correct file
2. Run: `python -m py_compile unified_trading_dashboard.py`
3. If error persists, restore backup

### Issue: Dashboard won't start
**Solution:**
1. Check logs: `type logs\unified_trading.log`
2. Restore backup
3. Re-extract patch and try again

### Issue: Chart still shows flat line
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Restart dashboard completely

---

## 📞 Support

**Patch Version:** v1.3.15.24  
**Patch Size:** ~60 KB  
**Full Package:** complete_backend_clean_install_v1.3.15.22_CRITICAL_FIXES.zip (881 KB)

If patch doesn't work, you can always download the full package.

---

## 🎉 Summary

- ✅ **Tiny patch:** Only 60 KB (vs 881 KB full package)
- ✅ **Quick install:** 1 minute (vs 5 minutes full reinstall)
- ✅ **Automatic backup:** Your original file is preserved
- ✅ **Easy rollback:** Restore backup if needed
- ✅ **Fixes ASX chart:** No more flat lines, correct market hours

**Apply this patch to fix the ASX All Ords chart without reinstalling everything!**

---

*Patch Version: v1.3.15.24*  
*Date: January 22, 2026*  
*Fixes: ASX All Ordinaries market hours and chart display*
