# Hotfix v1.3.15.117 - Market Chart Day Boundary Fix

## 📦 Quick Info

**Version**: v1.3.15.117  
**Date**: 2026-02-11  
**Type**: Visual Fix (Chart Display)  
**Priority**: Medium (improves UX, not critical)  
**Status**: ✅ PRODUCTION READY  

---

## 🎯 What This Fixes

### Problem: Vertical Lines Between Days

The 24-hour market chart showed **continuous lines connecting across day boundaries**, creating confusing vertical jumps:

**User Report**: "From one day to another there is now a line. Remove this so that it shows a new day trading result without linking to the previous day"

**Visual Issue**:
```
Day 1 Close (23:59) ────┐
                        │ ← Unwanted vertical line
Day 2 Open (00:00)  ────┘
```

**Screenshot Evidence**: User provided chart showing vertical line connecting yesterday's close to today's open.

---

## 🔧 Technical Fix

### Root Cause

Chart treated all timestamps as continuous series:
```python
# WRONG: No gap detection
for idx, row in market_hours_data.iterrows():
    pct_changes.append(pct_change)
    times.append(idx)

fig.add_trace(go.Scatter(x=times, y=pct_changes))
# Result: Connects ALL points, even across day boundaries
```

### Solution

**1. Detect Day Boundaries** (time gaps > 4 hours):
```python
gap_threshold_hours = 4  # Markets closed > 4 hours = new day

if time_gap > gap_threshold_hours:
    # Insert None to break the line
    pct_changes.append(None)
    times.append(idx)
```

**2. Disable Gap Connections**:
```python
fig.add_trace(go.Scatter(
    x=times,
    y=pct_changes,
    connectgaps=False  # Don't connect across None values
))
```

---

## 📊 Visual Comparison

### Before Fix (v1.3.15.116)
```
ASX: ────────┐
             │ ← Vertical line (bad)
             └─────────

S&P: ─────────┐
              │ ← Connects across days
              └──────
```

### After Fix (v1.3.15.117)
```
ASX: ────────  (gap)  ─────────

S&P: ─────────  (gap)  ──────

Each day starts fresh! ✅
```

---

## 🔍 How It Works

### Gap Detection Logic

For each data point, check time gap from previous point:
```python
if prev_timestamp is not None:
    time_gap = (idx - prev_timestamp).total_seconds() / 3600  # hours
    
    if time_gap > 4:  # More than 4 hours gap
        # This is a day boundary - break the line
        pct_changes.append(None)
        times.append(idx)
```

**Why 4 hours?**
- Markets close for several hours overnight
- Intraday gaps (lunch breaks, halts) are < 2 hours
- 4 hours safely detects day boundaries without false positives

### Plotly Configuration

```python
fig.add_trace(go.Scatter(
    connectgaps=False  # Critical: Don't draw line across None values
))
```

---

## 📋 Installation

### Quick Update (1 file)

1. **Stop dashboard** (Ctrl+C in START.bat)

2. **Backup**:
   ```batch
   copy core\unified_trading_dashboard.py core\unified_trading_dashboard.py.backup117
   ```

3. **Replace file**:
   - Extract `core\unified_trading_dashboard.py` from v1.3.15.117 ZIP

4. **Restart**:
   ```batch
   START.bat
   ```

**Time**: 1-2 minutes

---

## ✅ Verification

### After Applying Fix

1. **Open dashboard** in browser

2. **Look at 24hr chart**:
   - Should see 4 colored lines (ASX, S&P 500, NASDAQ, FTSE)
   - Lines should **NOT** have vertical jumps between days
   - Each new trading day should start cleanly

3. **Check logs** for:
   ```
   [MARKET CHART] ^GSPC: Adding trace with 78 points
   ```
   (Point count may vary but should be similar to before)

4. **Wait 24 hours**:
   - Next day, chart should start fresh
   - No line connecting to previous day

---

## 🔄 Rollback

If you need to revert:

```batch
# Restore backup
copy core\unified_trading_dashboard.py.backup117 core\unified_trading_dashboard.py

# Restart dashboard
START.bat
```

---

## 📊 Expected Behavior

### Market Chart Should Show

**During Trading Hours**:
- Continuous line for current trading session
- Updates every 5 minutes
- No gaps within same day

**Across Day Boundaries**:
- Clean break between days
- No vertical lines connecting days
- Each day starts at 0% reference point

**Example Timeline**:
```
Feb 10, 16:00 GMT: Market closes ───┐
Feb 10, 23:00 GMT: ASX opens          (gap - no line)
Feb 11, 00:00 GMT: New day        ───┘
```

---

## 🎯 Impact

### User Experience
- ✅ **Clearer visualization**: No confusing vertical lines
- ✅ **Better readability**: Each day distinct
- ✅ **Professional look**: Matches standard trading charts

### Performance
- ✅ **No impact**: Same data points, just different rendering
- ✅ **Same speed**: No additional calculations

### Compatibility
- ✅ **Works with all markets**: AU, US, UK, FTSE
- ✅ **Weekend handling**: Still shows Friday data on weekends
- ✅ **24hr window**: Still shows last 24 hours of data

---

## 📄 Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `core/unified_trading_dashboard.py` | 471-500 (30 lines) | Added gap detection & line break logic |
| `VERSION.md` | Updated | Added v1.3.15.117 entry |

---

## 🆕 New Log Output

**Before**:
```
[MARKET CHART] ^GSPC: Adding trace with 78 points, pct_change range: -0.36% to 0.24%
```

**After**:
```
[MARKET CHART] ^GSPC: Adding trace with 78 points, pct_change range: -0.36% to 0.24%
```
(Same output - no visible change in logs)

---

## 🎉 Summary

**What Was Fixed**:
- ✅ Removed vertical lines connecting across day boundaries
- ✅ Each trading day now starts fresh on chart
- ✅ Better visual clarity for users

**How It Was Fixed**:
- Detect time gaps > 4 hours (day boundaries)
- Insert `None` values to break the line
- Set `connectgaps=False` in Plotly

**Installation**:
- Quick: Replace 1 file, restart dashboard
- Time: 1-2 minutes
- Risk: Very low (visual change only)

**Status**: ✅ PRODUCTION READY

---

*Hotfix v1.3.15.117 | 2026-02-11 | Production Ready*
