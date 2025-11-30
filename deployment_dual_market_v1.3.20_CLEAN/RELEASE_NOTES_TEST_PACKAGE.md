# Event Risk Guard v1.3.20 - Bug Fixes & Optimization Analysis
## Test Package Release Notes

**Package:** `Event_Risk_Guard_v1.3.20_BUGFIXES_AND_ANALYSIS.zip`  
**Size:** 1.1 MB  
**Date:** November 25, 2025  
**Branch:** finbert-v4.0-development  
**Status:** Ready for Testing

---

## 🔧 Bug Fixes Included

### Bug #1: US Stock Scanner Data Format (CRITICAL FIX)
**File:** `models/screening/us_stock_scanner.py`  
**Commit:** `74880b9`

**Problem:**
- US scanner returned flat data structure incompatible with batch_predictor
- Wrong key names (`ma20` vs `ma_20`)
- Missing fundamental data (market cap, beta, company name, sector)
- Result: US reports showed "None" signals, 0% confidence, $0.00B market cap

**Fix Applied:**
```python
# BEFORE (Broken):
return {
    'symbol': 'GOOGL',
    'price': 299.66,
    'ma20': 295.0,      # Wrong key
    'rsi': 50.0         # Flat structure
}

# AFTER (Fixed):
return {
    'symbol': 'GOOGL',
    'name': 'Alphabet Inc',
    'price': 299.66,
    'market_cap': 2100000000000,
    'beta': 1.12,
    'sector_name': 'Technology',
    'technical': {       # Nested structure
        'ma_20': 295.0,  # Correct key
        'rsi': 50.0
    }
}
```

**Expected Result:**
- ✅ US reports show BUY/SELL/HOLD signals (not "None")
- ✅ Confidence shows 45-85% (not 0%)
- ✅ Market cap shows real values (e.g., "$2.1T")
- ✅ Beta shows real values (e.g., "1.12")
- ✅ Company names display (e.g., "Alphabet Inc")

---

### Bug #2: Web UI Not Scanning US Reports Directory
**File:** `web_ui.py`  
**Commit:** `a6ef311`

**Problem:**
- US pipeline saves reports to `reports/us/`
- Web UI only scanned ASX directories:
  - `models/screening/reports/morning_reports/`
  - `reports/html/`
  - `reports/`
- Result: US reports invisible in dashboard even when generated

**Fix Applied:**
```python
# Added to all 3 report scanning locations:
report_locations = [
    REPORTS_PATH / 'morning_reports',  # ASX
    REPORTS_PATH / 'html',
    BASE_PATH / 'reports' / 'html',
    BASE_PATH / 'reports' / 'us',      # US ← NEW
    BASE_PATH / 'reports'
]
```

**Expected Result:**
- ✅ US reports appear in "Latest Report" section
- ✅ Both ASX and US reports visible in dashboard
- ✅ Reports clickable and viewable

---

## 📚 Documentation Added

### 1. Fix Summary & Testing Instructions
**File:** `FIX_SUMMARY_AND_INSTRUCTIONS.md` (6.8 KB)  
**Commit:** `1e453b2`

**Contents:**
- Detailed explanation of both bugs
- BEFORE/AFTER code comparisons
- Step-by-step testing instructions
- Troubleshooting guide
- Expected runtime: 15-20 minutes for US pipeline

### 2. How Stock Recommendations Work
**File:** `HOW_STOCK_RECOMMENDATIONS_WORK.md` (12.9 KB)  
**Commit:** `d2ed81f`

**Contents:**
- Complete explanation of 6-phase pipeline
- LSTM training details (Phase 4.5)
- Ensemble prediction weights breakdown
- Opportunity scoring formula (6 factors)
- ASX vs US pipeline differences
- Real example: GOOGL recommendation with actual numbers
- Selectivity: 240 stocks → 10 recommendations (4%)

**Key Insight:** LSTM training DOES occur!
- Max 100 models per night
- 50 epochs, 32 batch size
- 7-day cache, models reused
- Training after scoring (doesn't block reporting)

### 3. Pipeline Optimization Analysis
**File:** `PIPELINE_OPTIMIZATION_ANALYSIS.md` (11.3 KB)  
**Commit:** `b35ec2d`

**Contents:**
- Analysis of current process order (80% optimal)
- 6 identified optimization opportunities
- 3 implementation options (A/B/C)
- Recommended hybrid approach
- Implementation priority (high/medium/low)
- Expected improvements: 30% speed, 15-25% accuracy

---

## 🚀 Testing Instructions

### Prerequisites
1. **Download Package:** `Event_Risk_Guard_v1.3.20_BUGFIXES_AND_ANALYSIS.zip`
2. **Extract** to fresh directory
3. **Install dependencies:** Run `INSTALL.bat`

### Step 1: Test Web UI Fix
```bash
# Start web UI
START_WEB_UI.bat

# Open browser: http://localhost:5000
# Expected: UI starts successfully, shows dashboard
```

### Step 2: Test ASX Pipeline (Baseline - Should Work)
```bash
# Run ASX pipeline
RUN_PIPELINE.bat

# Expected runtime: 20-30 minutes
# Expected output: HTML report in reports/morning_reports/
# Check dashboard: Should show ASX report with regime data
```

### Step 3: Test US Pipeline (Bug Fixes)
```bash
# Run US pipeline
RUN_US_PIPELINE.bat

# Expected runtime: 15-20 minutes
# Expected output: HTML report in reports/us/
```

**What to Verify:**
1. Pipeline completes without errors
2. Console shows: "US PIPELINE COMPLETE"
3. Report generated: `reports/us/us_morning_report_YYYYMMDD_HHMMSS.html`
4. Dashboard shows US report in "Latest Report" section

### Step 4: Verify US Report Data Quality
**Open the US report and check Top 10 Opportunities:**

| Field | OLD (Broken) | NEW (Fixed) | Status |
|-------|--------------|-------------|--------|
| Signal | "None" | "BUY" / "SELL" / "HOLD" | ✅ |
| Confidence | 0.0% | 45-85% | ✅ |
| Company Name | "Unknown" | "Alphabet Inc" | ✅ |
| Market Cap | $0.00B | $2.1T | ✅ |
| Beta | 1.00 | 1.12 | ✅ |
| Sector | "Unknown" | "Technology" | ✅ |
| Price | $299.66 | $299.66 | ✅ (always worked) |
| RSI | 50.0 | 52.3 | ✅ (always worked) |

**If ANY field shows OLD values, the fix is NOT working!**

### Step 5: Performance Benchmarks
**Record actual runtimes:**
```
ASX Pipeline:
  Phase 1 (Sentiment): _____ min
  Phase 2 (Scanning): _____ min
  Phase 3 (Prediction): _____ min
  Phase 4 (Scoring): _____ min
  Phase 5 (Reporting): _____ min
  Total: _____ min

US Pipeline:
  Phase 1 (Sentiment): _____ min
  Phase 2 (Scanning): _____ min
  Phase 3 (Prediction): _____ min
  Phase 4 (Scoring): _____ min
  Phase 5 (Reporting): _____ min
  Total: _____ min
```

**Expected Totals:**
- ASX: 20-30 minutes (scanning + prediction + scoring + reporting)
- US: 15-20 minutes (same process, no LSTM training phase)

---

## 🔍 Troubleshooting

### Issue: "No reports available yet" in dashboard
**Cause:** Web UI not restarted after fix  
**Fix:**
1. Stop web UI (Ctrl+C or close window)
2. Run `START_WEB_UI.bat` again
3. Refresh browser

### Issue: Still seeing "None" signals in US report
**Cause:** Running old code (Python cache)  
**Fix:**
```bash
# Delete Python cache
del /S /Q models\__pycache__
del /S /Q models\screening\__pycache__

# Run pipeline again
RUN_US_PIPELINE.bat
```

### Issue: Pipeline crashes during US scanning
**Cause:** yahooquery API rate limiting  
**Fix:**
- Wait 5 minutes between retry attempts
- Check internet connection
- Some stocks failing validation is NORMAL (not a bug)

### Issue: Fundamental data still showing $0.00B
**Cause:** yahooquery fetch failing for specific stocks  
**Expected:** This is NORMAL for some stocks (delisted, data unavailable)
- If ALL stocks show $0.00B → Bug not fixed
- If SOME stocks show $0.00B → Expected behavior

---

## 📊 Known Limitations (Not Bugs)

1. **US Pipeline No LSTM Training**
   - US pipeline does NOT have Phase 4.5 (LSTM training)
   - ASX pipeline DOES train models
   - This is by design (ASX is primary market)

2. **Fundamental Data Fetch Time**
   - Fetching market cap, beta, name adds ~0.3s per stock
   - For 180 stocks: ~1 minute additional time
   - Trade-off for complete data is acceptable

3. **Some Stocks May Fail Validation**
   - Not all 30 stocks per sector will pass
   - Typical: 20-25 stocks per sector validate
   - 180-200 total stocks is NORMAL (not 240)

4. **LSTM Models Not Used on First Run**
   - First run: no trained models exist
   - Uses trend-based fallback
   - Second run (next day): uses trained models
   - This is expected behavior

---

## 🎯 Success Criteria

**Test PASSES if:**
- ✅ ASX pipeline completes and generates report
- ✅ US pipeline completes and generates report
- ✅ US report shows in dashboard "Latest Report" section
- ✅ US report shows valid signals (not "None")
- ✅ US report shows confidence >0% (typically 45-85%)
- ✅ US report shows real market caps (billions/trillions)
- ✅ US report shows real beta values (not 1.00 default)
- ✅ US report shows company names (not "Unknown")
- ✅ Both pipelines complete in expected time

**Test FAILS if:**
- ❌ US reports not visible in dashboard
- ❌ US reports show "None" signals
- ❌ US reports show 0% confidence
- ❌ US reports show $0.00B for ALL stocks
- ❌ Pipeline crashes with errors
- ❌ Reports not generated

---

## 📝 Feedback Needed

After testing, please provide:

1. **Did both pipelines complete successfully?** (Yes/No)
2. **Are US reports visible in dashboard?** (Yes/No)
3. **Does US report show correct data?** (Yes/No)
   - Signals: BUY/SELL/HOLD (not "None")
   - Confidence: 45-85% (not 0%)
   - Market caps: Real values (not $0.00B)
   - Names: Company names (not "Unknown")
4. **Actual runtimes:**
   - ASX: _____ minutes
   - US: _____ minutes
5. **Any errors or issues encountered?**
6. **Screenshots of:**
   - Dashboard showing both reports
   - US report Top 10 Opportunities section

---

## 🔄 Next Phase: Optimization Implementation

Once testing confirms fixes work, we can move to **Phase 2: Optimization**:

**High Priority Optimizations (1-2 weeks):**
1. Move fundamental fetch AFTER validation (30% speed gain)
2. Dynamic ensemble weights based on model freshness
3. Regime-adaptive scoring weights

**Expected Improvements:**
- ⚡ 30% faster pipeline runtime
- 📈 15-20% more accurate opportunity scores
- 🎯 Better risk management in HIGH_VOL regimes

See `PIPELINE_OPTIMIZATION_ANALYSIS.md` for full details.

---

## 📦 Package Contents

```
deployment_dual_market_v1.3.20_CLEAN/
├── RELEASE_NOTES_TEST_PACKAGE.md          (this file)
├── FIX_SUMMARY_AND_INSTRUCTIONS.md         (bug fix details)
├── HOW_STOCK_RECOMMENDATIONS_WORK.md       (complete pipeline explanation)
├── PIPELINE_OPTIMIZATION_ANALYSIS.md       (future improvements)
├── DUAL_MARKET_README.md                   (installation guide)
│
├── RUN_PIPELINE.bat                        (ASX launcher)
├── RUN_US_PIPELINE.bat                     (US launcher)
├── START_WEB_UI.bat                        (dashboard launcher)
├── INSTALL.bat                             (dependency installer)
│
├── models/
│   ├── config/
│   │   ├── sectors.json                    (ASX sectors)
│   │   └── us_sectors.json                 (US sectors)
│   └── screening/
│       ├── overnight_pipeline.py           (ASX - unchanged)
│       ├── us_overnight_pipeline.py        (US - unchanged)
│       ├── us_stock_scanner.py             (FIXED - Bug #1)
│       ├── batch_predictor.py              (unchanged)
│       ├── opportunity_scorer.py           (unchanged)
│       └── report_generator.py             (unchanged)
│
├── web_ui.py                               (FIXED - Bug #2)
└── templates/
    └── dashboard.html                      (unchanged)
```

---

## 🚀 Ready to Test!

**Next Steps:**
1. Extract package
2. Run `INSTALL.bat`
3. Follow testing instructions above
4. Report results

**Questions or Issues?**
- Check `FIX_SUMMARY_AND_INSTRUCTIONS.md` for detailed troubleshooting
- Review `HOW_STOCK_RECOMMENDATIONS_WORK.md` to understand pipeline
- See `PIPELINE_OPTIMIZATION_ANALYSIS.md` for future improvements

Good luck testing! 🎯
