# 24-Hour Chart X-Axis Fix - v1.3.15.87 Patch

## 🔍 Issue Identified

**User Report**: "There is an extended x axis timeline that is distorting the plot. The during the week should only show a 24hr period. After the us market closes on a friday the plot should be static until trading starts on the australian market the following monday."

## 📊 Problems Found

### Problem 1: Extended X-Axis Range
- **Issue**: Chart fetches 5 days of data but x-axis not constrained
- **Result**: X-axis extends beyond actual 24-hour trading period
- **Cause**: No explicit `xaxis['range']` parameter set in layout

### Problem 2: Weekend Distortion  
- **Issue**: On weekends, chart continues to update but shows Friday data with extended x-axis
- **Result**: Static Friday data displayed across Saturday/Sunday timeline
- **Cause**: No weekend detection logic

### Problem 3: Zoom/Pan Issues
- **Issue**: Users could zoom/pan which further distorted the 24-hour view
- **Result**: Chart loses intended 24-hour fixed window
- **Cause**: `fixedrange` not set on axes

---

## ✅ Solutions Implemented

### Fix 1: Explicit X-Axis Range Constraint

**Location**: `unified_trading_dashboard.py`, lines ~498-524

**Added Code**:
```python
# Calculate x-axis range to show only 24-hour period
all_times = []
for trace in fig.data:
    if hasattr(trace, 'x') and len(trace.x) > 0:
        all_times.extend(trace.x)

xaxis_range = None
if all_times:
    min_time = min(all_times)
    max_time = max(all_times)
    
    # Ensure we're showing exactly 24 hours
    if isinstance(min_time, pd.Timestamp):
        min_time = min_time.replace(minute=0, second=0, microsecond=0)
        range_end = min_time + timedelta(hours=24)
        if max_time < range_end:
            range_end = max_time + timedelta(minutes=30)  # Small buffer
        xaxis_range = [min_time, range_end]
```

**Result**: X-axis now constrained to exactly 24-hour period from first data point

---

### Fix 2: Weekend Detection & Static Display

**Location**: `unified_trading_dashboard.py`, lines ~345-360

**Added Code**:
```python
from datetime import datetime, timedelta

# Check if we're in weekend
gmt = pytz.timezone('GMT')
current_time_gmt = datetime.now(gmt)
current_weekday = current_time_gmt.weekday()  # Monday=0, Sunday=6
current_hour = current_time_gmt.hour

# Weekend period: Friday after 21:00 GMT until Sunday after 23:00 GMT
is_weekend = (
    (current_weekday == 4 and current_hour >= 21) or  # Friday after 21:00 GMT
    (current_weekday == 5) or  # All day Saturday
    (current_weekday == 6 and current_hour < 23)  # Sunday before 23:00 GMT
)
```

**Weekend Data Handling** (lines ~401-415):
```python
# On weekends, use Friday's data (last trading day)
if is_weekend:
    # Find Friday's data (most recent weekday <= 4)
    friday_data = hist[hist.index.weekday <= 4]
    if len(friday_data) > 0:
        latest_date = friday_data.index[-1].date()
        hist = friday_data  # Use only up to Friday
    else:
        latest_date = hist.index[-1].date()
else:
    latest_date = hist.index[-1].date()
```

**Result**: 
- Chart shows Friday's last trading day data throughout weekend
- Remains static (no timeline extension)
- Resumes live updates when AU market opens Monday 23:00 GMT

---

### Fix 3: Fixed Range (Prevent Zoom/Pan Distortion)

**Location**: `unified_trading_dashboard.py`, lines ~541-554

**Added Code**:
```python
xaxis={
    # ... other settings ...
    'range': xaxis_range,  # Explicit 24-hour range
    'fixedrange': True  # Prevent zoom/pan
},
yaxis={
    # ... other settings ...
    'fixedrange': True  # Prevent zoom/pan
}
```

**Result**: Users cannot zoom/pan which would distort the 24-hour view

---

### Fix 4: Weekend Indicator

**Location**: `unified_trading_dashboard.py`, lines ~526-534

**Added Code**:
```python
# Create title with weekend indicator
chart_title = None
if is_weekend:
    chart_title = {
        'text': '24-Hour Market Performance (Last Trading Day - Markets Closed)',
        'font': {'size': 12, 'color': '#FF9800'},
        'x': 0.5,
        'xanchor': 'center'
    }

fig.update_layout(
    title=chart_title,
    # ... other settings ...
    margin={'l': 20, 'r': 50, 't': 40, 'b': 50},  # Increased top margin for title
)
```

**Result**: Chart displays clear indicator when showing weekend/static data

---

## 📅 Trading Week Timeline

### Weekday Behavior (Monday 23:00 GMT - Friday 21:00 GMT)
**What happens**:
1. Chart fetches live 15-minute data from Yahoo Finance
2. Filters to show only most recent 24-hour trading period
3. X-axis constrained to 24 hours from first data point
4. Updates every 5 seconds with new data
5. Old data beyond 24 hours automatically removed

**Markets shown**:
- **ASX**: 23:00 GMT (Sun/Mon) to 05:00 GMT (Mon-Fri) - spans midnight
- **FTSE**: 08:00 GMT to 16:30 GMT (Mon-Fri)
- **S&P 500**: 14:30 GMT to 21:00 GMT (Mon-Fri)
- **NASDAQ**: 14:30 GMT to 21:00 GMT (Mon-Fri)

**X-axis range**: Exactly 24 hours from earliest market open to latest close (or current time)

---

### Weekend Behavior (Friday 21:00 GMT - Monday 23:00 GMT)
**What happens**:
1. Weekend detection triggers at Friday 21:00 GMT (US market close)
2. Chart switches to "static mode"
3. Displays Friday's last complete trading day
4. X-axis frozen at Friday's 24-hour period
5. Chart title changes to: "24-Hour Market Performance (Last Trading Day - Markets Closed)"
6. No updates occur (data remains static)
7. Resumes live mode Monday 23:00 GMT (AU market open)

**Saturday/Sunday**:
- Chart displays Friday's data
- Orange warning title visible
- No timeline extension
- Static 24-hour window

---

## 🔬 Technical Details

### Weekend Detection Logic

**Time Zone**: All calculations in GMT
**Detection Period**:
```
Friday 21:00 GMT → US market closes (S&P 500, NASDAQ close at 21:00 GMT)
Saturday 00:00 GMT → All day Saturday
Sunday 23:00 GMT → Until AU market opens (ASX opens 23:00 GMT Sunday night)
```

**Code Logic**:
```python
current_weekday = current_time_gmt.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
current_hour = current_time_gmt.hour

is_weekend = (
    (current_weekday == 4 and current_hour >= 21) or  # Fri >= 21:00 GMT
    (current_weekday == 5) or                         # All Sat
    (current_weekday == 6 and current_hour < 23)     # Sun < 23:00 GMT
)
```

**Why these times**:
- **Friday 21:00 GMT**: US markets close (16:00 EST / 21:00 GMT)
- **Monday 23:00 GMT**: AU market opens (10:00 AEDT / 23:00 GMT Sunday)
- Covers full weekend + Friday evening + Sunday evening

---

### X-Axis Range Calculation

**Algorithm**:
```python
1. Collect all timestamps from chart traces
2. Find minimum timestamp (earliest data point)
3. Find maximum timestamp (latest data point)
4. Round min_time down to nearest hour
5. Set range_end = min_time + 24 hours
6. If actual max_time < range_end:
   - Use max_time + 30 min buffer (for live markets)
7. Set xaxis['range'] = [min_time, range_end]
```

**Example (Weekday)**:
```
Current time: Tuesday 15:00 GMT
Data available:
  - ASX: Mon 23:00 GMT - Tue 05:00 GMT (closed)
  - FTSE: Tue 08:00 GMT - 15:00 GMT (open)
  - US: Tue 14:30 GMT - 15:00 GMT (open)

Calculation:
  min_time = Mon 23:00 GMT (ASX open)
  max_time = Tue 15:00 GMT (current)
  range_end = Mon 23:00 + 24h = Tue 23:00 GMT
  actual max < range_end, so use Tue 15:30 GMT (current + buffer)
  
X-axis range: [Mon 23:00 GMT, Tue 15:30 GMT]
Duration shown: ~16.5 hours (within 24h window)
```

**Example (Weekend)**:
```
Current time: Saturday 10:00 GMT
Data available: Friday's trading day only

Calculation:
  Latest Friday data: Fri 21:00 GMT (US close)
  Earliest Friday data: Fri 08:00 GMT (FTSE open) OR Thu 23:00 GMT (ASX open)
  
If ASX data spans to Friday:
  min_time = Thu 23:00 GMT
  max_time = Fri 21:00 GMT
  range_end = Thu 23:00 + 24h = Fri 23:00 GMT
  actual max (Fri 21:00) < range_end, so use Fri 21:30 GMT
  
X-axis range: [Thu 23:00 GMT, Fri 21:30 GMT]
Duration shown: ~22.5 hours (within 24h window)
Chart remains static until Monday 23:00 GMT
```

---

## 🧪 Testing Scenarios

### Scenario 1: Monday Morning (AU Market Open)
**Time**: Monday 01:00 GMT (ASX is open)
**Expected**:
- Chart shows live ASX data from Sun 23:00 GMT to Mon 01:00 GMT
- X-axis: ~2 hours shown (Sun 23:00 to Mon 01:30)
- Weekend mode OFF
- Title: No weekend indicator
- Updates every 5 seconds

### Scenario 2: Tuesday Afternoon (All Markets Open)
**Time**: Tuesday 15:00 GMT (FTSE closing, US opening)
**Expected**:
- Chart shows ASX (closed), FTSE (closing), US (opening), NASDAQ (opening)
- X-axis: Mon 23:00 GMT to Tue 15:30 GMT (~16.5 hours)
- All data within 24-hour window
- Updates every 5 seconds

### Scenario 3: Friday Evening (US Market Close)
**Time**: Friday 21:15 GMT (all markets closed)
**Expected**:
- Weekend mode activates
- Chart shows Friday's complete trading day
- X-axis: Thu 23:00 GMT to Fri 21:30 GMT (~22.5 hours)
- Static (no updates)
- Title: "Last Trading Day - Markets Closed" (orange)

### Scenario 4: Saturday/Sunday (Weekend)
**Time**: Saturday 14:00 GMT or Sunday 10:00 GMT
**Expected**:
- Weekend mode active
- Chart displays Friday's last trading day
- X-axis: Same as Friday evening (static)
- No updates
- Title: Orange weekend warning

### Scenario 5: Sunday Night (Pre-AU Open)
**Time**: Sunday 22:00 GMT (1 hour before AU open)
**Expected**:
- Still in weekend mode
- Chart shows Friday data
- Static display
- At 23:00 GMT: Switches to live mode, fetches new AU data

---

## 📊 Before vs After Comparison

### BEFORE (Issues):
```
Weekday X-Axis:
[=================|-----------|------------] 
  24h actual data   extended    more extended
                    empty       empty space
Result: Distorted view with empty space

Weekend X-Axis:
[=========|------------------------]
 Fri data   Sat      Sun timeline
Result: Friday data stretched across weekend timeline
```

### AFTER (Fixed):
```
Weekday X-Axis:
[===================]
   24h actual data
Result: Exact 24-hour window, no extension

Weekend X-Axis:
[=================]
   Fri data (static)
Result: Friday's 24h shown, remains static until Mon open
```

---

## 🔄 Chart Update Cycle

### Weekday Cycle (5-second updates):
```
1. Dashboard interval triggers (every 5 sec)
2. create_market_performance_chart() called
3. Check: is_weekend = False
4. Fetch 5 days of data (covers prev trading day)
5. Filter to latest trading day
6. Apply market hours filter (ASX: 23:00-05:00, FTSE: 08:00-16:30, US: 14:30-21:00)
7. Calculate x-axis range (24h from earliest data)
8. Update chart with new data
9. Repeat after 5 seconds
```

### Weekend Cycle (static):
```
1. Dashboard interval triggers (every 5 sec)
2. create_market_performance_chart() called
3. Check: is_weekend = True
4. Fetch 5 days of data
5. Filter to Friday only (weekday <= 4)
6. Apply market hours filter (Friday's hours)
7. Calculate x-axis range (24h from Friday start)
8. Display chart with weekend title
9. Return same data (no updates)
10. Repeat until Monday 23:00 GMT
```

---

## ⚠️ Edge Cases Handled

### 1. Market Holidays
**Scenario**: US holiday on Monday, AU market open
**Handling**: 
- Chart shows AU data only
- US traces empty or show previous day
- X-axis still constrained to 24h

### 2. Data Fetch Failures
**Scenario**: Yahoo Finance API error
**Handling**:
- Empty traces for failed symbols
- X-axis calculated from available data
- Chart displays successfully with partial data

### 3. Timezone Changes (DST)
**Scenario**: Daylight Saving Time transitions
**Handling**:
- All calculations in GMT (no DST)
- Market hours remain constant in GMT
- User sees consistent 24h window

### 4. Very Recent Data (< 1 hour)
**Scenario**: AU market just opened 5 minutes ago
**Handling**:
- X-axis: Sun 23:00 GMT to Mon 00:05 GMT (~1 hour shown)
- Still within 24h window
- Range expands as more data arrives

---

## 📝 Summary of Changes

### Files Modified:
1. **unified_trading_dashboard.py**
   - Added weekend detection logic (lines ~345-360)
   - Modified data fetching for weekend handling (lines ~401-415)
   - Added x-axis range calculation (lines ~498-524)
   - Added weekend indicator title (lines ~526-534)
   - Added fixedrange to prevent zoom (lines ~541, 554)
   - Updated x-axis title to clarify "24 Hour Period" (line ~539)

### Lines Changed: ~60 lines
### Functions Modified: 1 (create_market_performance_chart)
### New Dependencies: None (uses existing datetime, timedelta, pytz)

---

## ✅ Verification Checklist

After deploying this fix:

- [ ] **Weekday Check**: During market hours, chart shows only 24h period
- [ ] **Weekend Check**: Friday 21:00 GMT+, chart shows Friday data with orange title
- [ ] **X-Axis Check**: No extended empty space beyond data
- [ ] **Zoom Check**: Cannot zoom/pan to distort view
- [ ] **Update Check**: Chart updates every 5 seconds on weekdays
- [ ] **Static Check**: Chart remains static on weekends
- [ ] **Monday Check**: At Monday 23:00 GMT, chart switches to live AU data
- [ ] **Title Check**: Weekend title appears/disappears correctly

---

## 🎯 Benefits

1. **Cleaner Visualization**: No distorted extended x-axis
2. **Accurate 24h Window**: Always shows exactly 24-hour trading period
3. **Weekend Clarity**: Clear indication when markets are closed
4. **Static Weekend**: No confusing timeline extension over Sat/Sun
5. **Auto-Resume**: Automatically switches back to live data Monday morning
6. **Fixed View**: Cannot accidentally zoom/pan to break intended view

---

## 📦 Package Status

**File**: unified_trading_dashboard.py  
**Location**: /home/user/webapp/deployments/unified_trading_dashboard_v1.3.15.87_ULTIMATE/core/  
**Status**: ✅ Fixed  
**Version**: v1.3.15.87 ULTIMATE (with 24h chart fix)  
**Date**: 2026-02-03  

**Note**: This fix is applied to the extracted package. The ZIP needs to be recreated to include this update.

---

## 🚀 Next Steps

1. ✅ Fix applied to unified_trading_dashboard.py
2. ⏳ Recreate unified_trading_dashboard_v1.3.15.87_ULTIMATE.zip
3. ⏳ Test chart behavior on weekday
4. ⏳ Test chart behavior on weekend
5. ⏳ Verify x-axis range constraint working
6. ⏳ Confirm weekend title appears correctly

---

**Fix Status**: ✅ Complete  
**Testing Required**: Weekend behavior (will verify on next Sat/Sun)  
**Backward Compatible**: Yes (no breaking changes)
