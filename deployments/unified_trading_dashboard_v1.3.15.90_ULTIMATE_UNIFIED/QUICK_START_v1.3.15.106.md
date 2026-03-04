# 🚀 QUICK START - v1.3.15.106

**All Pipelines Working!** ✅ AU | ✅ US | ✅ UK

---

## ⚡ Quick Installation (5 Minutes)

### Step 1: Extract Package
```
Extract: unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED.zip
To: C:\Users\[YourUsername]\Regime_trading\
```

### Step 2: Install Dependencies (First Time Only)
```batch
cd unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED
INSTALL_COMPLETE.bat
```
⏱️ Takes ~20-25 minutes

### Step 3: Start System
```batch
START.bat
```

---

## 🎯 Menu Options

```
1. Complete System (FinBERT + Dashboard + Pipelines)
2. FinBERT Only (Sentiment + LSTM)
3. Dashboard Only (Paper Trading + Live Charts)
4. All Pipelines (AU + US + UK) - ~60 minutes
5. AU Pipeline Only (ASX) - ~20 minutes        ← NEW! ✅
6. US Pipeline Only (NYSE/NASDAQ) - ~20 minutes ← NEW! ✅
7. UK Pipeline Only (LSE) - ~20 minutes        ← NEW! ✅
8. Exit
```

---

## ⏰ Best Times to Run

| Pipeline | Best Time (UTC) | Market Opens | Report Location |
|----------|----------------|--------------|-----------------|
| **AU** | 23:30 UTC | 00:00 UTC (ASX) | `reports/au_morning_report.json` |
| **US** | 14:00 UTC | 14:30 UTC (NYSE) | `reports/us_morning_report.json` |
| **UK** | 07:30 UTC | 08:00 UTC (LSE) | `reports/uk_morning_report.json` |

---

## ✅ What's Fixed

- ✅ Import paths consistent across all pipelines
- ✅ Market-hours filtering (30-70% efficiency)
- ✅ Strategic timing menu
- ✅ Dependencies (yahooquery, feedparser)
- ✅ Sentiment path resolution
- ✅ ASX market display

---

## 🧪 Quick Test

```batch
# Test imports work
python -c "from core.paper_trading_coordinator import PaperTradingCoordinator; print('✅ OK')"

# Run pipeline
python scripts/run_au_pipeline_v1.3.13.py --full-scan --ignore-market-hours
```

**Expected:** `[OK] Stock Scanner imported` → Pipeline starts

---

## 📦 Package Info

- **Version:** v1.3.15.106
- **Size:** 706 KB
- **Status:** ✅ PRODUCTION READY
- **Git:** 23efbac, e46add0

---

## 📚 Full Documentation

- `ALL_PIPELINES_WORKING_v1.3.15.106.md` - Complete guide
- `HOTFIX_IMPORT_CONSISTENCY_v1.3.15.106.md` - Import fix details
- `STRATEGIC_PIPELINE_TIMING.md` - Timing recommendations
- `VERSION.md` - Full version history

---

## 🆘 Need Help?

**Issue:** Import errors?  
**Fix:** Verify `core.` prefix in imports (see HOTFIX docs)

**Issue:** Missing dependencies?  
**Fix:** Run `FIX_YAHOOQUERY.bat` or `INSTALL_COMPLETE.bat`

**Issue:** Pipeline fails?  
**Fix:** Add `--ignore-market-hours` flag for testing

---

## 🎉 Success!

You'll see:
```
[OK] Stock Scanner imported
[OK] Keras LSTM available
[CALENDAR] Market calendar initialized
[OK] Starting pipeline...
[OK] PIPELINE COMPLETED SUCCESSFULLY
```

**Download:** `/home/user/webapp/deployments/unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED.zip`

**STATUS: READY TO USE!** 🚀
