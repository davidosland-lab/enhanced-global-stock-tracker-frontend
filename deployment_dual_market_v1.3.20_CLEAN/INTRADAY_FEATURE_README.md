# Intraday Market Hours Detection Feature

## Overview

The pipeline now includes **automatic market hours detection** to provide awareness when running during trading hours.

## What's New?

### Market Hours Detector Module
- **File**: `models/screening/market_hours_detector.py`
- **Purpose**: Detects if ASX/US markets are currently open
- **Features**:
  - Real-time market status detection
  - Trading hours validation (ASX: 10 AM - 4 PM AEST, US: 9:30 AM - 4 PM EST)
  - Time until open/close calculations
  - Trading day verification (Monday-Friday)
  - Percentage of trading day elapsed

### Pipeline Integration
- **ASX Pipeline**: `overnight_pipeline.py` - Enhanced with market detection at start
- **US Pipeline**: `us_overnight_pipeline.py` - Enhanced with market detection at start
- **Behavior**: Automatically detects market status and logs warnings during intraday runs

---

## How It Works

### When You Run the Pipeline

#### Scenario 1: Market Closed (Overnight Mode) - **DEFAULT**
```
================================================================================
PHASE 0: MARKET HOURS DETECTION
================================================================================
🌙 ASX MARKET CLOSED (After-Hours)
   Current Time: 2025-11-26 22:00:00 AEST
   Next Open: 12h 0m

✓ OVERNIGHT MODE (Standard)
  • Market is closed
  • Using standard predictions
```

**Pipeline Behavior:**
- ✅ Standard operation
- ✅ SPI futures and US market analysis fully utilized
- ✅ Next-day opportunity predictions
- ✅ No warnings or alerts

---

#### Scenario 2: Market Open (Intraday Mode) - **WARNING**
```
================================================================================
PHASE 0: MARKET HOURS DETECTION
================================================================================
✅ ASX MARKET IS OPEN
   Current Time: 2025-11-26 14:30:00 AEST
   Trading Hours Elapsed: 75.0%
   Time Until Close: 1h 30m

⚠️  INTRADAY MODE ACTIVE
    • Market is currently open
    • Using recent/live prices
    • Consider running after market close for best results
```

**Pipeline Behavior:**
- ⚠️  Warning logged (market is open)
- ✅ Pipeline continues to run
- ✅ Uses most recent data (includes today's partial trading)
- ⚠️  SPI gap predictions less relevant (market already open)
- ⚠️  Predictions are less reliable (incomplete trading day)

---

## Testing the Feature

### Test Market Hours Detection
```bash
# Run test script
python TEST_MARKET_HOURS.py
```

**Expected Output:**
```
================================================================================
MARKET HOURS DETECTION TEST
================================================================================

🇦🇺 AUSTRALIAN MARKET (ASX)
--------------------------------------------------------------------------------
✅ ASX MARKET IS OPEN
   Current Time: 2025-11-27 15:43:06 AEDT
   Trading Hours Elapsed: 95.3%
   Time Until Close: 16m 53s

✅ ASX is OPEN - Pipeline will use INTRADAY mode
   • 95.3% of trading day completed
   • Market closes in: 0:16:53.056214

================================================================================

🇺🇸 US MARKET
--------------------------------------------------------------------------------
🌙 US MARKET CLOSED (After-Hours)
   Current Time: 2025-11-26 23:43:06 EST
   Next Open: 9h 46m

🌙 US Market is CLOSED
   • Market phase: AFTER_HOURS

================================================================================

📊 RECOMMENDATION:
--------------------------------------------------------------------------------
⚡ Run AUS pipeline in INTRADAY mode
   • Use real-time/recent prices
   • Focus on momentum indicators
   • De-emphasize overnight gap predictions

================================================================================
✅ Test completed successfully!
================================================================================
```

---

## Configuration

### No Configuration Required! 🎉

The market hours detector:
- ✅ Automatically enabled
- ✅ Zero configuration needed
- ✅ Zero cost (no API calls)
- ✅ Works out of the box

### Market Hours (Hard-Coded)
```python
ASX:
  - Timezone: Australia/Sydney (AEST/AEDT)
  - Open: 10:00 AM
  - Close: 4:00 PM
  - Trading Days: Monday-Friday
  - Session: 6 hours

US:
  - Timezone: America/New_York (EST/EDT)
  - Open: 9:30 AM
  - Close: 4:00 PM
  - Trading Days: Monday-Friday
  - Session: 6.5 hours
```

---

## Current Limitations (Phase 1 Implementation)

### ✅ What It Does
- ✅ Detects market open/closed status
- ✅ Logs warnings during intraday runs
- ✅ Tracks pipeline mode (overnight vs. intraday)
- ✅ Calculates time until open/close
- ✅ Verifies trading days

### ⚠️  What It Doesn't Do (Yet - Future Phases)
- ❌ Adjust opportunity scorer weights for intraday
- ❌ Fetch real-time 1-minute price data
- ❌ De-emphasize SPI predictions during market hours
- ❌ Generate intraday-specific reports
- ❌ Auto-rescan every 15-30 minutes
- ❌ Provide push notifications for breakouts

These features are planned for **Phase 2-4** (see `INTRADAY_ENHANCEMENT_PLAN.md`).

---

## When to Run the Pipeline

### ✅ Best Times (Overnight Mode)
1. **After ASX Close** (after 4:00 PM AEST)
   - All day's data available
   - SPI futures are trading
   - US market data available
   
2. **Before ASX Open** (before 10:00 AM AEST)
   - Overnight gap predictions most accurate
   - US market closes analyzed

### ⚠️  Acceptable Times (Intraday Mode)
1. **During ASX Hours** (10:00 AM - 4:00 PM AEST)
   - Pipeline will run with warnings
   - Uses partial-day data
   - Less predictive accuracy

### ❌ Not Recommended
1. **Weekends** (Saturday/Sunday)
   - Markets closed
   - Limited new data
   - SPI futures inactive (mostly)

---

## FAQs

### Q: Will the pipeline fail if I run it during market hours?
**A:** No! The pipeline will:
- ✅ Run successfully
- ⚠️  Log warnings about intraday mode
- ✅ Use the most recent data available
- ⚠️  Produce less accurate predictions

### Q: Should I wait for Phase 2-4 intraday features?
**A:** It depends:
- **For daily runs**: Current Phase 1 is sufficient (just be aware of warnings)
- **For intraday trading**: Wait for Phase 2+ (better momentum indicators, real-time data)
- **For cost savings**: Phase 1 has zero additional cost

### Q: Does this affect AI scoring costs?
**A:** No! AI costs remain the same:
- Same ~$0.033 per run
- No extra API calls for market detection
- Market hours detection is free (local timezone math)

### Q: What if I want to force overnight mode?
**A:** Currently automatic. To disable:
```python
# In overnight_pipeline.py or us_overnight_pipeline.py __init__:
self.market_detector = None  # Force disable
```

### Q: Can I run the pipeline every 30 minutes during market hours?
**A:** Not recommended yet:
- Current implementation doesn't optimize for frequent runs
- Would cost ~$0.33 in AI fees (10 runs × $0.033)
- Wait for Phase 3 (auto-rescan feature)

---

## Files Modified

### New Files
- `models/screening/market_hours_detector.py` (market hours detection module)
- `TEST_MARKET_HOURS.py` (test script)
- `INTRADAY_FEATURE_README.md` (this file)
- `INTRADAY_ENHANCEMENT_PLAN.md` (future roadmap)

### Modified Files
- `models/screening/overnight_pipeline.py` (ASX pipeline - added Phase 0)
- `models/screening/us_overnight_pipeline.py` (US pipeline - added Phase 0)

---

## Next Steps

### Immediate Use
```bash
# Test market detection
python TEST_MARKET_HOURS.py

# Run pipelines normally (market detection automatic)
python RUN_PIPELINE.bat        # ASX
python RUN_US_PIPELINE.bat     # US
```

### Future Enhancement (Optional)
See `INTRADAY_ENHANCEMENT_PLAN.md` for:
- **Phase 2**: Real-time data fetching (1-minute bars)
- **Phase 3**: Intraday momentum scoring
- **Phase 4**: Auto-rescan and push notifications

---

## Benefits Summary

### Phase 1 (Current Implementation)
✅ **Zero Cost**: No additional API calls
✅ **Zero Risk**: Doesn't break existing functionality
✅ **Awareness**: Clear warnings during intraday runs
✅ **Tracking**: Logs market status in pipeline state
✅ **Foundation**: Ready for Phase 2-4 enhancements

### Phase 2-4 (Future, Optional)
⚡ **Better Intraday Accuracy**: Momentum-based scoring
⚡ **Real-Time Data**: 1-minute price bars
⚡ **Adaptive Weights**: Different scoring for intraday
⚡ **Auto-Rescan**: Every 15-30 minutes
⚡ **Cost**: +$0.30 per day for frequent rescans

---

## Conclusion

The **Market Hours Detection** feature (Phase 1) provides:
1. ✅ Automatic detection of market open/closed status
2. ✅ Clear warnings when running during trading hours
3. ✅ Zero cost and zero risk
4. ✅ Foundation for future intraday optimizations

**Recommendation**: 
- Use it as-is for standard overnight runs
- Be aware of warnings during intraday runs
- Wait for Phase 2-4 if you need advanced intraday features

---

**Ready to Test?**
```bash
python TEST_MARKET_HOURS.py
python RUN_PIPELINE.bat
```

**Questions?** See `INTRADAY_ENHANCEMENT_PLAN.md` for the full roadmap! 🚀
