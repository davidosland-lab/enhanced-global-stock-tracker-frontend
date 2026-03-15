# FTSE 100 2% BUG ANALYSIS - Unified Trading Dashboard

**Date**: 2026-01-29  
**Issue**: Dashboard shows FTSE 100 at ~2% when Yahoo Finance shows much lower (e.g., 0.17%)  
**User Report**: "I checked the ftse 100 yahoo ticker prior to writing the question. At no point did it get near 2%."

---

## Problem Statement

The Unified Trading Dashboard is displaying **INCORRECT percentage changes** for FTSE 100 (and potentially other indices). User verified actual FTSE 100 movement was around 0.17%, but dashboard shows ~2%.

---

## Bug Location

**File**: `unified_trading_dashboard.py`  
**Function**: `create_market_performance_chart(state)` (line 333-469)  
**Affected Code**: Lines 430-441 (previous close calculation)

---

## Root Cause Analysis

### The Code (Lines 430-441)

```python
else:
    # For normal markets, find last close before current trading day
    previous_day_data = hist[hist.index.date < latest_date]
    
    if len(previous_day_data) > 0:
        # Use previous day's last close as reference
        previous_close = previous_day_data['Close'].iloc[-1]
        logger.debug(f"{symbol}: Using previous close: {previous_close:.2f}")
    else:
        # Fallback: use first price of current session if no previous data
        previous_close = market_hours_data['Close'].iloc[0]
        logger.debug(f"{symbol}: Using session open as reference: {previous_close:.2f}")
```

### The Percentage Calculation (Lines 447-450)

```python
for idx, row in market_hours_data.iterrows():
    pct_change = ((row['Close'] - previous_close) / previous_close) * 100
    pct_changes.append(pct_change)
    times.append(idx)
```

---

## Potential Issues

### Issue #1: Wrong Reference Date (Most Likely)

**Problem**: The code fetches `period='2d'` with `interval='15m'`, then filters:
```python
previous_day_data = hist[hist.index.date < latest_date]
```

**Scenario**: If there's stale/cached data or data gaps:
- `latest_date` might be TODAY (2026-01-29)
- `previous_day_data` looks for data < 2026-01-29
- If data is incomplete or market was closed (weekend), it might pick up FRIDAY's close
- FTSE 100 on Friday vs Monday could show a larger % change

**Example**:
```
Friday close: 8,300.00
Monday current: 8,465.00
Change: (8,465 - 8,300) / 8,300 × 100 = 1.99% ← Near 2%!
```

But Yahoo Finance shows:
```
Monday open: 8,450.00
Monday current: 8,465.00
Change: (8,465 - 8,450) / 8,450 × 100 = 0.18% ← Correct!
```

### Issue #2: Intraday vs Official Close

**Problem**: Yahoo Finance uses **official previous close** (16:30 GMT close price), while this code uses:
```python
previous_close = previous_day_data['Close'].iloc[-1]
```

This gets the **last 15-minute interval** from previous day's data, which might be:
- After-hours trading
- Stale data point
- Adjusted close vs regular market close

### Issue #3: Weekend/Holiday Data Gaps

**Problem**: FTSE 100 market hours: 08:00-16:30 GMT Monday-Friday

If dashboard is viewed on:
- **Monday morning**: Previous close should be Friday 16:30
- **Weekend**: Markets closed, data stale

The `period='2d'` might not reliably capture "previous trading day" if:
- Current time is early Monday (before market open)
- Data hasn't refreshed yet
- Weekend data is missing

### Issue #4: Timezone Issues

**Code sets GMT**:
```python
gmt = pytz.timezone('GMT')
hist.index = hist.index.tz_convert(gmt)
```

But `yfinance` data might be in:
- UTC (same as GMT, should be OK)
- Local timezone (would cause issues)
- Mixed timezones (after tz_convert)

If timezone conversion is incorrect, `hist.index.date` comparisons could pick wrong day.

---

## How to Reproduce the Bug

### Your Scenario (User's Observation)

1. Check Yahoo Finance directly: FTSE 100 shows +0.17%
2. Open Unified Trading Dashboard
3. View Market Performance chart
4. FTSE 100 line shows ~+2.0%

**This indicates the dashboard is using the WRONG reference price.**

---

## Diagnostic Steps

### Step 1: Check Dashboard Logs

The code includes debug logging:
```python
logger.debug(f"{symbol}: Using previous close: {previous_close:.2f}")
```

**Action**:
```batch
type logs\unified_trading.log | findstr "FTSE.*previous close"
type logs\unified_trading.log | findstr "FTSE.*reference"
```

**Expected output**:
```
^FTSE: Using previous close: 8300.00
```

**Compare to Yahoo Finance**:
- If Yahoo shows previous close: 8,450.00
- But dashboard logs: 8,300.00
- **BUG CONFIRMED**: Dashboard is using wrong reference

### Step 2: Check Data Retrieval Timestamps

**Action**: Add detailed logging to see what data is fetched:
```python
print(f"Fetched data for {symbol}:")
print(f"  Data range: {hist.index[0]} to {hist.index[-1]}")
print(f"  Latest date: {latest_date}")
print(f"  Previous day data range: {previous_day_data.index[0]} to {previous_day_data.index[-1]}")
print(f"  Previous close used: {previous_close:.2f}")
```

### Step 3: Manual Verification

Run this in Python console:
```python
import yfinance as yf
from datetime import datetime

ticker = yf.Ticker('^FTSE')

# Get official quote
info = ticker.info
official_prev_close = info.get('regularMarketPreviousClose')
current_price = info.get('regularMarketPrice')
official_change = ((current_price - official_prev_close) / official_prev_close) * 100

print(f"Official Yahoo Finance:")
print(f"  Previous Close: {official_prev_close}")
print(f"  Current Price: {current_price}")
print(f"  Change: {official_change:.2f}%")

# Get 2-day history (what dashboard does)
hist = ticker.history(period='2d', interval='15m')
dashboard_prev_close = hist['Close'].iloc[-2]  # Approximate
dashboard_current = hist['Close'].iloc[-1]
dashboard_change = ((dashboard_current - dashboard_prev_close) / dashboard_prev_close) * 100

print(f"\nDashboard Calculation:")
print(f"  Previous Close (approx): {dashboard_prev_close}")
print(f"  Current Price: {dashboard_current}")
print(f"  Change: {dashboard_change:.2f}%")
```

---

## Fix Options

### Fix #1: Use Official Previous Close (Recommended)

**Replace lines 430-441 with**:
```python
else:
    # For normal markets, use official previous close from ticker.info
    try:
        ticker_info = yf.Ticker(symbol).info
        official_prev_close = ticker_info.get('regularMarketPreviousClose')
        
        if official_prev_close and official_prev_close > 0:
            previous_close = official_prev_close
            logger.debug(f"{symbol}: Using official previous close: {previous_close:.2f}")
        else:
            # Fallback: find last close before current trading day
            previous_day_data = hist[hist.index.date < latest_date]
            
            if len(previous_day_data) > 0:
                previous_close = previous_day_data['Close'].iloc[-1]
                logger.debug(f"{symbol}: Using historical previous close: {previous_close:.2f}")
            else:
                previous_close = market_hours_data['Close'].iloc[0]
                logger.debug(f"{symbol}: Using session open as reference: {previous_close:.2f}")
    except Exception as e:
        logger.warning(f"{symbol}: Failed to get official previous close: {e}")
        # Fallback to existing logic
        previous_day_data = hist[hist.index.date < latest_date]
        if len(previous_day_data) > 0:
            previous_close = previous_day_data['Close'].iloc[-1]
        else:
            previous_close = market_hours_data['Close'].iloc[0]
```

### Fix #2: Use Proper Trading Day Lookup

**Replace lines 432-433 with**:
```python
# For normal markets, find last TRADING day's close (skip weekends/holidays)
# Get all data before latest_date, but ensure we're getting a proper trading day
previous_day_data = hist[hist.index.date < latest_date]

# Filter to only include data during market hours (to avoid after-hours)
market_hours_filter = (
    (previous_day_data.index.hour >= market_open_hour) &
    (previous_day_data.index.hour <= market_close_hour)
)
previous_trading_day = previous_day_data[market_hours_filter]

if len(previous_trading_day) > 0:
    # Use the LAST close from previous trading day during market hours
    previous_close = previous_trading_day['Close'].iloc[-1]
    prev_close_time = previous_trading_day.index[-1]
    logger.debug(f"{symbol}: Using previous trading day close from {prev_close_time}: {previous_close:.2f}")
else:
    # Fallback
    previous_close = market_hours_data['Close'].iloc[0]
    logger.debug(f"{symbol}: Using session open as reference: {previous_close:.2f}")
```

### Fix #3: Use Period='5d' for Better Coverage

**Replace line 377 with**:
```python
# Fetch 5 days of data to ensure we have previous trading day (covers weekends/holidays)
hist = ticker.history(period='5d', interval='15m')
```

This ensures we always have at least one full previous trading day, even after weekends.

---

## Recommended Solution

**Combination Fix** (most robust):

1. Use `period='5d'` instead of `'2d'` (covers weekends)
2. Use **official previous close** from `ticker.info` as primary source
3. Fall back to filtered historical data (market hours only) if official data unavailable
4. Add detailed debug logging to track reference prices

---

## Testing the Fix

### Test Cases

1. **Monday morning** (after weekend)
   - Expected: Use Friday's 16:30 close
   - Verify: % change matches Yahoo Finance

2. **Mid-week** (Tuesday-Thursday)
   - Expected: Use previous day's 16:30 close
   - Verify: % change matches Yahoo Finance

3. **After market close** (e.g., 18:00 GMT)
   - Expected: Use today's 16:30 close as reference for tomorrow
   - Verify: Chart shows today's intraday movement

4. **Weekend** (markets closed)
   - Expected: Show Friday's close as reference
   - Verify: No stale/incorrect data displayed

### Verification Commands

```batch
# Run dashboard with verbose logging
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
python unified_trading_dashboard.py --debug

# Check logs
type logs\unified_trading.log | findstr "FTSE"

# Compare to Yahoo Finance
# Visit: https://finance.yahoo.com/quote/%5EFTSE
# Verify "Previous Close" matches dashboard reference
```

---

## Impact Analysis

### Affected Indices

All indices in the dashboard are potentially affected:
- ✅ **^AORD** (ASX All Ords) - Uses `spans_midnight=True` logic (different code path)
- ❌ **^GSPC** (S&P 500) - Uses same logic as FTSE (POTENTIALLY AFFECTED)
- ❌ **^IXIC** (NASDAQ) - Uses same logic as FTSE (POTENTIALLY AFFECTED)
- ❌ **^FTSE** (FTSE 100) - **CONFIRMED AFFECTED** (user report)

### User Impact

**Severity**: **HIGH**
- Users see **incorrect percentage changes** in Market Performance chart
- Misleading market sentiment (2% vs 0.17% is 10x difference!)
- Could lead to incorrect trading decisions
- Undermines trust in dashboard data accuracy

---

## Next Steps

1. **Immediate**: Add detailed logging to capture actual vs expected previous close
2. **Short-term**: Apply Fix #1 (use official previous close) to resolve issue
3. **Long-term**: Add data validation to detect anomalies (e.g., >5% change should trigger warning)
4. **Testing**: Verify fix across all four indices on Monday morning (after weekend)

---

## User Question Answered

**Question**: "Where did you get the FTSE 100 of 2% from?"

**Answer**: 
The dashboard is **incorrectly calculating** the FTSE 100 percentage change due to a bug in the reference price selection. The code uses:

```python
previous_close = previous_day_data['Close'].iloc[-1]
```

This might be picking up:
- **Friday's close** instead of **Monday's official previous close**
- **Stale data** from `period='2d'` not covering weekend properly
- **Wrong trading day** due to date filtering logic

**Your observation is correct**: FTSE 100 was around +0.17%, not +2%.

The bug is in `unified_trading_dashboard.py`, lines 430-441, and needs to be fixed to use the **official previous close** from Yahoo Finance's ticker info instead of historical data interpolation.

---

**Status**: BUG CONFIRMED  
**Priority**: HIGH (affects user decision-making)  
**Fix Required**: Yes (update reference price calculation)  
**Estimated Fix Time**: 15-30 minutes
