# Dashboard Hot-Patch Installation Guide v1.3.15.41

## 🎯 What This Patch Fixes

**Issue**: ASX All Ordinaries chart displays incorrectly on the 24-Hour Market Performance panel
- Shows flat line or incorrect percentage
- Uses wrong reference price (current session instead of previous close)
- Missing last hour of trading data (05:00-05:59 GMT)

**Fix**: Correct ASX chart display with proper reference pricing and complete trading hours

---

## 📦 Patch Contents

**Files Modified**: 1
- `unified_trading_dashboard.py` (dashboard chart rendering)

**Files Added**: 1
- `ASX_CHART_FIX_v1.3.15.41.md` (technical documentation)

**Patch Size**: ~8 KB
**Installation Time**: 30 seconds
**Downtime Required**: Dashboard restart (~15 seconds)

---

## ✅ Prerequisites

- Trading platform v1.3.15.32 or later installed
- Dashboard currently running or stopped
- Admin/write access to installation directory

---

## 🚀 Installation Steps

### Step 1: Extract Patch
```batch
REM Extract v1.3.15.41_DASHBOARD_PATCH.zip to your installation directory
REM Example path:
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15

REM Extract and overwrite when prompted
REM This will update:
REM   unified_trading_dashboard.py
REM   ASX_CHART_FIX_v1.3.15.41.md
```

### Step 2: Restart Dashboard

**If Dashboard is Running:**
```batch
REM 1. Go to the terminal window running the dashboard
REM 2. Press Ctrl+C to stop
REM 3. Wait for "Shutting down..." message
REM 4. Restart:
python unified_trading_dashboard.py

REM Dashboard will start on http://localhost:8050
```

**If Dashboard is Stopped:**
```batch
REM Just start it:
python unified_trading_dashboard.py
```

### Step 3: Verify Fix

1. Open dashboard: `http://localhost:8050`
2. Navigate to **24-Hour Market Performance** panel
3. Check ASX All Ordinaries (cyan/turquoise line):
   - ✅ Should show intraday movement (not flat)
   - ✅ Percentage should match ASX website (±0.1%)
   - ✅ Line should be smooth with data points every 15 minutes
4. Other indices should remain correct:
   - ✅ S&P 500 (blue)
   - ✅ NASDAQ (green)
   - ✅ FTSE 100 (orange)

---

## 🔍 Technical Details

### What Changed

**Before (v1.3.15.40 and earlier):**
```python
# Wrong: Used current session as reference
current_data = session_data[session_data['Date'].dt.date == today]
previous_close = previous_day_data['Close'].iloc[-1]  # ❌ Wrong day
```

**After (v1.3.15.41):**
```python
# Correct: Uses true previous trading day (two days ago for ASX)
if spans_midnight:
    reference_date = today - pd.Timedelta(days=2)  # ✅ Correct
    previous_day = reference_date.date()
    previous_close = two_days_ago['Close'].iloc[-1]
```

**Time Filter Fix:**
```python
# Before: hour <= 5 (misses 05:00-05:59)
# After:  hour < 6  (includes full 05:xx hour)
```

### ASX Trading Hours Reference
- **Local Time (AEDT)**: 10:00 AM - 4:00 PM
- **GMT Time**: 23:00 (previous day) - 05:00 (current day)
- **Spans Midnight**: Yes (requires special handling)

### Debug Logging
The patch adds reference price logging:
```
INFO - ASX reference: Previous close from 2026-01-25 = 8350.20
```

---

## 📊 Expected Results

### Before Patch
- ASX line appears flat or at ~-0.2%
- Chart doesn't reflect actual market movement
- No correlation with ASX website data

### After Patch
- ASX line shows realistic intraday movement
- Percentage matches ASX official data
- Smooth line with 15-minute granularity
- Proper midnight-spanning session handling

---

## 🔧 Troubleshooting

### Issue: Dashboard won't restart
**Solution**: Check for port conflicts
```batch
netstat -ano | findstr :8050
REM If port is in use, kill the process:
taskkill /PID <process_id> /F
```

### Issue: Chart still shows old data
**Solution**: Clear browser cache
- Press `Ctrl+Shift+R` to hard refresh
- Or clear cache in browser settings

### Issue: No ASX data displayed
**Solution**: Check internet connection and data source
```batch
REM Test yfinance data fetch:
python -c "import yfinance as yf; print(yf.Ticker('^AORD').history(period='2d', interval='15m'))"
```

### Issue: Error on dashboard startup
**Solution**: Check unified_trading_dashboard.py syntax
```batch
python -m py_compile unified_trading_dashboard.py
```

---

## 📋 Compatibility

| Version | Compatible | Notes |
|---------|-----------|-------|
| v1.3.15.32 | ✅ Yes | Minimum version |
| v1.3.15.33-39 | ✅ Yes | All intermediate versions |
| v1.3.15.40 | ✅ Yes | Global sentiment release |
| v1.3.15.41 | ✅ Yes | This patch |

---

## 🎯 Impact on Trading

**Trading Operations**: No impact
- Paper trading continues during dashboard restart
- Overnight pipelines unaffected
- Position management unchanged

**Dashboard Downtime**: ~15 seconds
- Only while restarting dashboard process
- All data preserved in state.json
- Charts reload automatically

---

## 📝 Rollback Procedure

If you need to revert this patch:

```batch
REM 1. Stop dashboard (Ctrl+C)

REM 2. Restore from git (if using version control)
git checkout HEAD~1 unified_trading_dashboard.py

REM 3. Or restore from backup
copy unified_trading_dashboard.py.bak unified_trading_dashboard.py

REM 4. Restart dashboard
python unified_trading_dashboard.py
```

---

## 🔐 File Checksums

**Before modification:**
- `unified_trading_dashboard.py`: (original from v1.3.15.40)

**After modification:**
- `unified_trading_dashboard.py`: SHA-256 TBD after installation

---

## 📞 Support

**Issue**: Chart still incorrect after patch
**Action**: Check logs in `logs/uk_pipeline.log` for data fetch errors

**Issue**: Dashboard crash after restart
**Action**: Review stack trace and check Python dependencies

**Issue**: Other charts affected
**Action**: This patch only modifies ASX logic; other indices use unchanged code

---

## ✅ Installation Checklist

- [ ] Backup current `unified_trading_dashboard.py` (optional)
- [ ] Extract patch files to installation directory
- [ ] Stop dashboard (if running)
- [ ] Restart dashboard with `python unified_trading_dashboard.py`
- [ ] Open `http://localhost:8050` in browser
- [ ] Verify ASX All Ords chart displays correctly
- [ ] Check other charts (S&P 500, NASDAQ, FTSE) still work
- [ ] Confirm no errors in terminal output
- [ ] Test chart updates after 15 minutes

---

## 🎉 Completion

Once the checklist is complete, your dashboard is updated to **v1.3.15.41** with correct ASX chart display!

**Next Overnight Run**: Will use updated dashboard automatically
**Paper Trading**: Continues using corrected market data visualization
**Historical Data**: No impact; only affects real-time charting

---

**Patch Version**: v1.3.15.41  
**Release Date**: January 27, 2026  
**Patch Type**: Hot-fix (zero downtime)  
**Status**: PRODUCTION READY
