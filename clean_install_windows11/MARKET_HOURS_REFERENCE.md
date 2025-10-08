# Global Market Trading Hours Reference

## Australian Daylight Saving Time (ADST) = UTC+11

### Market Trading Hours in ADST

#### 🇦🇺 ASX (Australian Securities Exchange)
- **Symbol**: ^AORD (All Ordinaries)
- **Local Time**: 10:00 - 16:00 AEDT
- **ADST Time**: 10:00 - 16:00 ADST (same as local)
- **Trading Days**: Monday - Friday
- **No lunch break**

#### 🇬🇧 FTSE 100 (London Stock Exchange)
- **Symbol**: ^FTSE
- **Local Time**: 08:00 - 16:30 GMT (UK time)
- **ADST Time**: 19:00 - 03:30 (+1 day) ADST
- **Trading Days**: Monday - Friday
- **Opens in the evening, closes early next morning**

#### 🇺🇸 S&P 500 (New York Stock Exchange)
- **Symbol**: ^GSPC
- **Local Time**: 09:30 - 16:00 EST (US Eastern)
- **ADST Time**: 01:30 - 08:00 (+1 day) ADST
- **Trading Days**: Monday - Friday
- **Opens after midnight, closes in the morning**

## Example Timeline (ADST)

### Tuesday, 8th October 2025 → Wednesday, 9th October 2025

```
Time (ADST)    Market Status
──────────────────────────────────────
00:00          All markets closed
01:30          S&P 500 OPENS (Tue US session)
03:30          FTSE 100 CLOSES (Mon UK session)
08:00          S&P 500 CLOSES
10:00          ASX OPENS (Tue AU session)
16:00          ASX CLOSES
19:00          FTSE 100 OPENS (Tue UK session)
23:59          Day ends
──────────────────────────────────────
00:00          Wednesday begins
01:30          S&P 500 OPENS (Wed US session)
03:30          FTSE 100 CLOSES (Tue UK session)
...
```

## Chart Display Logic

### X-Axis Time Display
The fixed version now correctly:
1. **Shows all times in ADST** (UTC+11)
2. **Breaks lines when markets close** (inserts null points)
3. **Labels key market hours** on the axis:
   - 10:00 - ASX Open
   - 16:00 - ASX Close
   - 19:00 - FTSE Open
   - 03:30 - FTSE Close
   - 01:30 - S&P Open
   - 08:00 - S&P Close

### Data Point Conversion
All data points from Yahoo Finance are converted to ADST for display:
- Original timestamps preserved from API
- Converted to ADST for chart plotting
- Market gaps detected based on actual trading hours

## Time Zone Conversions

### During Australian Daylight Saving Time (Oct - Apr)
- **Sydney/Melbourne**: AEDT = UTC+11 (same as ADST)
- **London**: GMT = UTC+0 → ADST = GMT+11
- **New York**: EST = UTC-5 → ADST = EST+16

### During Australian Standard Time (Apr - Oct)
- **Sydney/Melbourne**: AEST = UTC+10
- **London**: BST = UTC+1 → AEST = BST+9
- **New York**: EDT = UTC-4 → AEST = EDT+14

## Implementation Details

### Code Changes in indices_tracker_fixed_times.html

1. **ADST Time Function**:
```javascript
function getADSTTime(date = new Date()) {
    const utcTime = date.getTime() + (date.getTimezoneOffset() * 60000);
    return new Date(utcTime + (11 * 3600000)); // UTC+11
}
```

2. **Market Hours Check**:
```javascript
function isMarketOpen(market) {
    const now = getADSTTime();
    const hour = now.getHours() + now.getMinutes() / 60;
    
    if (market === MARKETS.asx) {
        return hour >= 10 && hour < 16;
    } else if (market === MARKETS.ftse) {
        return hour >= 19 || hour < 3.5; // Crosses midnight
    } else if (market === MARKETS.sp500) {
        return hour >= 1.5 && hour < 8;
    }
}
```

3. **Gap Detection**:
Markets are shown as continuous lines during trading hours, with breaks (null points) inserted when closed.

## Files Modified
- `modules/indices_tracker_fixed_times.html` - New fixed version with correct ADST times
- `FIX_INDICES_TRACKER_TIMES.bat` - Script to apply the fix

## Testing
After applying the fix:
1. Run `FIX_INDICES_TRACKER_TIMES.bat`
2. Refresh browser at http://localhost:8000
3. Navigate to the Global Indices Tracker module
4. Verify:
   - X-axis shows ADST times
   - Lines break when markets are closed
   - Market status badges show correct OPEN/CLOSED state
   - Tooltips show times in ADST format