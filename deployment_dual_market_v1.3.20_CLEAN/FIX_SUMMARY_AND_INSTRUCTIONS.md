# US Market Pipeline - Bug Fixes and Testing Instructions

## Issues Fixed

### 1. ❌ US Stock Scanner Data Format (CRITICAL)
**Problem:** US scanner returned incompatible data format
- Flat structure instead of nested `technical` dict
- Wrong key names (`ma20` instead of `ma_20`)
- Missing fundamental data (market cap, beta, company name)

**Result:** Batch predictor couldn't process data
- Signal: "None"
- Confidence: 0.0%
- Market Cap: $0.00B
- Beta: 1.0 (default)

**Fix Applied:** ✅ Commit `74880b9`
- Restructured to nested `technical` dictionary
- Fixed key naming (`ma_20`, `ma_50` with underscores)
- Added fundamental data fetching via yahooquery
- Now fetches: company name, market cap, beta, sector

**File:** `models/screening/us_stock_scanner.py`

---

### 2. ❌ Web UI Not Scanning US Reports Directory
**Problem:** US pipeline saves to `reports/us/` but web UI only scanned:
- `models/screening/reports/morning_reports/` (ASX)
- `reports/html/`
- `reports/`

**Result:** US reports were invisible in dashboard even if generated

**Fix Applied:** ✅ Commit `a6ef311`
- Added `reports/us/` to all report scanning locations
- Updated 3 functions: `get_reports()`, `get_report()`, `get_latest_report()`

**File:** `web_ui.py`

---

## Testing Instructions

### Step 1: Restart Web UI (Required)
The web UI is currently running with OLD code. You must restart it to load the fixes:

```bash
# Stop current web UI (Ctrl+C in its terminal)
# Or close the window running START_WEB_UI.bat

# Start fresh web UI
START_WEB_UI.bat
```

### Step 2: Run US Pipeline
Now run the US market screening:

```bash
RUN_US_PIPELINE.bat
```

**Expected Behavior:**
```
================================================================================
US OVERNIGHT STOCK SCREENING PIPELINE - STARTING
================================================================================
Start Time: 2025-11-24 XX:XX:XX EST

PHASE 1: US MARKET SENTIMENT ANALYSIS
...

PHASE 2: US STOCK SCANNING
Scanning 8 US sectors...
Target: 30 stocks per sector

[1/8] Scanning Technology...
  ✓ Found 25 valid stocks
  
[2/8] Scanning Healthcare...
  ✓ Found 22 valid stocks
  
... (continues for all 8 sectors)

PHASE 3: BATCH PREDICTION
Starting batch prediction for 180 stocks...
✓ Predictions Generated: 180 stocks

PHASE 4: OPPORTUNITY SCORING
Scoring opportunities for 180 stocks...
✓ Scoring Complete: 35 high-quality opportunities (≥75)

PHASE 5: US MARKET REPORT GENERATION
Generating US market morning report...
✓ Report saved: reports/us/us_morning_report_20251124_XXXXXX.html

================================================================================
US PIPELINE COMPLETE
================================================================================
Total Time: 15.3 minutes
Stocks Processed: 180
Report Generated: reports/us/us_morning_report_20251124_XXXXXX.html
```

### Step 3: Check Dashboard
1. Open browser to http://localhost:5000
2. Click "Refresh" button
3. Look for **Latest Report** section

**You Should See:**
- Latest US report listed with timestamp
- Click to open report
- Top 10 opportunities with:
  - ✅ Company Name (e.g., "Alphabet Inc")
  - ✅ Signal (BUY/SELL/HOLD)
  - ✅ Confidence (45-85%)
  - ✅ Market Cap (e.g., "$2.1T")
  - ✅ Beta (e.g., "1.12")
  - ✅ Sector (e.g., "Technology")

---

## Troubleshooting

### Issue: Pipeline Runs But No Reports Appear

**Check 1: Did pipeline complete successfully?**
```bash
# Look at the end of pipeline output
# Should say "US PIPELINE COMPLETE"
```

**Check 2: Does reports/us/ directory exist?**
```bash
cd deployment_dual_market_v1.3.20_CLEAN
dir reports\us
# Should list HTML files
```

**Check 3: Is web UI using NEW code?**
```bash
# Restart web UI after pulling latest fixes
# Stop current instance, then run START_WEB_UI.bat again
```

### Issue: Pipeline Crashes or Hangs

**Symptom:** Pipeline stops during scanning phase
**Cause:** yahooquery API rate limiting or timeout
**Solution:** 
- Wait a few minutes between retry attempts
- Check internet connection
- Some stocks may fail validation (this is normal)

**Symptom:** "No valid stocks found"
**Cause:** All stocks failed validation (price/volume filters)
**Solution:**
- Check `models/config/us_sectors.json` filters
- Default filters:
  - min_price: $5.00
  - max_price: $1000.00
  - min_avg_volume: 1,000,000 shares
  - min_market_cap: $2 billion

### Issue: Still Seeing "None" Signals

**This means the OLD code is still running.**

**Fix:**
1. Download latest package: `Event_Risk_Guard_v1.3.20_DUAL_MARKET_FIXED.zip`
2. Extract to fresh directory
3. Run `INSTALL.bat`
4. Run `RUN_US_PIPELINE.bat`

**OR if using Git:**
```bash
cd deployment_dual_market_v1.3.20_CLEAN
git pull origin finbert-v4.0-development
# Clear Python cache
del /S /Q models\__pycache__
del /S /Q models\screening\__pycache__
```

---

## Performance Notes

**US Pipeline Runtime:**
- Sentiment Analysis: ~1 minute
- Stock Scanning: ~8-12 minutes (8 sectors × 30 stocks)
  - Validation: ~0.3s per stock
  - Analysis: ~0.5s per stock (includes fundamental fetch)
  - Technical calculation: fast
- Batch Prediction: ~3-5 minutes (180 stocks)
- Opportunity Scoring: ~30 seconds
- Report Generation: ~10 seconds

**Total: ~15-20 minutes for complete US pipeline**

**Fundamental Data Impact:**
- Adding market cap, beta, sector, name adds ~0.3s per stock
- For 180 stocks: ~1 minute additional time
- **Trade-off is worth it** for complete, useful reports

---

## Files Modified

| File | Commit | Change |
|------|--------|--------|
| `models/screening/us_stock_scanner.py` | `74880b9` | Fixed data format, added fundamentals |
| `web_ui.py` | `a6ef311` | Added US reports directory scan |

---

## Download Latest Package

**Latest Fixed Version:**
```
Event_Risk_Guard_v1.3.20_DUAL_MARKET_FIXED.zip
Location: /home/user/webapp/
Size: 1.1MB
```

**Includes:**
- ✅ Fixed US stock scanner data format
- ✅ Fixed web UI report scanning
- ✅ Working ASX pipeline (unchanged v1.3.20)
- ✅ Complete dual market system

---

## Expected Final Result

After running both pipelines, you should have:

**ASX Reports:** `reports/morning_reports/`
- Full regime analysis
- SPI futures sentiment
- ASX sector scanning
- Top 10 ASX opportunities

**US Reports:** `reports/us/`
- S&P 500 / VIX sentiment
- US sector scanning
- Top 10 US opportunities
- Complete fundamental data

**Both visible in web dashboard at http://localhost:5000**

---

## Next Steps

1. ✅ Restart web UI (to load fixes)
2. ✅ Run US pipeline: `RUN_US_PIPELINE.bat`
3. ✅ Wait ~15-20 minutes for completion
4. ✅ Check dashboard for US reports
5. ✅ Verify data shows correctly (not "None")

If issues persist, provide:
- Pipeline console output (last 50 lines)
- Any error messages
- Contents of `reports/us/` directory
