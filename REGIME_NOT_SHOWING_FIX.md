# 🔍 Market Regime Not Showing - Quick Fix Guide

## Problem
The Market Regime Analysis section is **NOT appearing** in:
- ❌ HTML Morning Report
- ❌ Web UI Dashboard

## Root Cause
You're likely using the **OLD code** that was generated BEFORE the regime UI integration and bug fix were applied.

---

## ✅ Solution

### Step 1: Verify Your Current Version

Run the diagnostic script:
```bash
cd C:\Users\david\AASS\event_risk_guard_v1.3.20_CLEAN
python CHECK_REGIME_STATUS.py
```

This will tell you:
- ✓ If you have the regime integration code
- ✓ If the bug fix is applied
- ✓ If the regime engine is available
- ✓ If your reports contain regime data

### Step 2: Extract the FIXED Package

**Download and extract**: `event_risk_guard_v1.3.20_REGIME_UI_FIXED_20251121_030620.zip`

**IMPORTANT**: Extract to the SAME location as your current installation, **overwriting** all files.

```
Your current location appears to be:
C:\Users\david\AASS\event_risk_guard_v1.3.20_CLEAN\

Extract the ZIP to:
C:\Users\david\AASS\

This will overwrite the files in event_risk_guard_v1.3.20_CLEAN\
```

### Step 3: Re-run the Pipeline

After extracting the fixed package:

```bash
cd C:\Users\david\AASS\event_risk_guard_v1.3.20_CLEAN
python models\screening\overnight_pipeline.py
```

### Step 4: Check the New Report

Open the newly generated report:
- Location: `reports\html\` or `models\screening\reports\morning_reports\`
- Look for: **"🎯 Market Regime Analysis"** section
- Should appear: Right after "📈 Market Overview" section

### Step 5: Start Web UI

```bash
cd C:\Users\david\AASS\event_risk_guard_v1.3.20_CLEAN
python web_ui.py
```

Then access: http://localhost:5000

Look for the **"🎯 Market Regime Analysis"** card at the top of the dashboard.

---

## What You Should See

### In HTML Report:
```
📈 Market Overview
(existing market data)

🎯 Market Regime Analysis        ← NEW SECTION
├─ Current Regime: 🔴 High Volatility
├─ Crash Risk: 62.6% [HIGH RISK]
├─ Daily Vol: 0.75% | Annual Vol: 12.0%
└─ Probabilities: (visual bars)

🎯 Top 5 Opportunities
(existing opportunities list)
```

### On Web Dashboard:
```
[System Status Cards]

🎯 Market Regime Analysis [🔄 Refresh]  ← NEW CARD
├─ Current Regime: 🔴 High Volatility
├─ Crash Risk: 62.6% [HIGH RISK]
├─ Daily Vol: 0.75%
├─ Annual Vol: 12.0%
└─ Probability Bars (3 states)

📄 Latest Report
(existing sections)
```

---

## Troubleshooting

### Issue: "Still not showing after extracting package"

**Check 1**: Did you extract to the correct location?
```bash
# Run this in your terminal:
cd C:\Users\david\AASS\event_risk_guard_v1.3.20_CLEAN
python CHECK_REGIME_STATUS.py
```

If CHECK 1 or CHECK 2 shows ❌, you haven't extracted the fixed package correctly.

**Check 2**: Did you re-run the pipeline AFTER extracting?
- The old report (from 02:18 PM) doesn't have regime data
- You need to generate a NEW report with the FIXED code

**Check 3**: Is the Market Regime Engine initialized?
```bash
python DIAGNOSE_CRASH.py
```

Look for:
```
✓ Market Regime Engine initialization successful
```

If you see errors about hmmlearn, install it:
```bash
pip install hmmlearn scikit-learn
```

### Issue: "Regime engine not available"

This means hmmlearn is not installed. Install it:
```bash
pip install hmmlearn scikit-learn
```

Then re-run the pipeline.

### Issue: "Pipeline crashes with NameError"

This means you're using the OLD code with the bug. Extract the FIXED package:
- `event_risk_guard_v1.3.20_REGIME_UI_FIXED_20251121_030620.zip`

Make sure to **overwrite** the old files.

---

## Files That Should Be Updated

After extracting the FIXED package, these files should have the regime code:

1. **models/screening/report_generator.py**
   - Should have: `_build_market_regime_section()` method
   - Line ~829-926

2. **models/screening/overnight_pipeline.py**
   - Line 274: `report_path = self._generate_report(scored_stocks, spi_sentiment, event_risk_data)`
   - Line 658: `def _generate_report(self, stocks: List[Dict], spi_sentiment: Dict, event_risk_data: Dict = None)`

3. **web_ui.py**
   - Should have: `/api/regime` endpoint
   - Line ~320-394

4. **templates/dashboard.html**
   - Should have: Market Regime Section
   - Before the "Main Content" section

5. **static/css/dashboard.css**
   - Should have: `.market-regime-section` styles
   - At the end of file

6. **static/js/dashboard.js**
   - Should have: `loadRegimeData()` function
   - At the end of file

---

## Quick Verification Commands

### 1. Check if report_generator.py has regime code:
```bash
findstr /C:"_build_market_regime_section" models\screening\report_generator.py
```

Should return line numbers where the method is defined.

### 2. Check if overnight_pipeline.py passes event_risk_data:
```bash
findstr /C:"event_risk_data" models\screening\overnight_pipeline.py
```

Should show multiple lines including the method call and parameter.

### 3. Check if web_ui.py has regime endpoint:
```bash
findstr /C:"@app.route('/api/regime')" web_ui.py
```

Should show the route definition.

---

## Expected Timeline

1. **Extract package**: 30 seconds
2. **Run pipeline**: 5-10 minutes (depending on stock count)
3. **View report**: Immediate
4. **Start web UI**: 5 seconds
5. **See regime data**: Immediate

**Total time**: ~10-15 minutes

---

## Still Not Working?

Run the full diagnostic:
```bash
python CHECK_REGIME_STATUS.py
```

And share the output. The script will tell you exactly what's missing.

---

## Package Location

The fixed package should be in:
- **Your system**: `/home/user/webapp/event_risk_guard_v1.3.20_REGIME_UI_FIXED_20251121_030620.zip`
- **Filename**: `event_risk_guard_v1.3.20_REGIME_UI_FIXED_20251121_030620.zip`
- **Size**: 1.1 MB

If you don't have this file, let me know and I'll create it again.

---

**Summary**: Extract the FIXED package → Overwrite old files → Re-run pipeline → Check new report ✅
