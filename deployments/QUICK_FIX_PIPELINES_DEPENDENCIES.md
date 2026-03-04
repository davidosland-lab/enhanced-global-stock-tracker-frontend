# QUICK FIX - Missing Dependencies for Overnight Pipelines

## ❌ Problem

When running `RUN_UK_PIPELINE.bat` (or any pipeline), you get:
```
ModuleNotFoundError: No module named 'yahooquery'
```

## ✅ Solution

The overnight pipelines require additional packages that aren't in the base FinBERT venv. Install them:

### Option 1: Automated Install (Recommended)

```batch
INSTALL_PIPELINES.bat
```

This will install:
- yahooquery (market data)
- statsmodels (regime analysis)
- dash + plotly (dashboard)
- beautifulsoup4 (news scraping)
- All other dependencies

**Time:** 2-5 minutes  
**Disk:** ~500 MB

---

### Option 2: Manual Install

```batch
cd finbert_v4.4.4
venv\Scripts\activate
pip install yahooquery>=2.3.0 yfinance>=0.2.30 statsmodels>=0.13.0 dash>=2.11.0 plotly>=5.15.0 beautifulsoup4>=4.12.0 lxml>=4.9.0
```

---

### Option 3: Install from requirements.txt

```batch
cd finbert_v4.4.4
venv\Scripts\activate
pip install -r ..\pipelines\requirements.txt
```

---

## 🧪 Test After Install

### Test 1: Check packages installed
```batch
finbert_v4.4.4\venv\Scripts\python.exe -c "import yahooquery; import statsmodels; print('OK')"
```

Expected output: `OK`

### Test 2: Run UK pipeline
```batch
cd pipelines
RUN_UK_PIPELINE.bat
```

Expected: Pipeline starts successfully

---

## 📦 What Gets Installed

| Package | Purpose | Size |
|---------|---------|------|
| yahooquery | Market data (primary) | ~50 MB |
| yfinance | Market data (backup) | ~10 MB |
| statsmodels | Regime analysis, time series | ~100 MB |
| dash | Dashboard framework | ~80 MB |
| plotly | Interactive charts | ~120 MB |
| beautifulsoup4 | News scraping | ~5 MB |
| lxml | HTML parsing | ~20 MB |
| scipy | Scientific computing | ~80 MB |
| feedparser | RSS feeds | ~5 MB |

**Total:** ~470 MB

---

## 🎯 Why This Happened

The initial `INSTALL.bat` installs core dependencies:
- transformers (FinBERT)
- torch (LSTM)
- ta (technical analysis)
- pandas, numpy

But the **overnight pipelines** need additional packages for:
- Multi-source market data (yahooquery + yfinance)
- Regime detection (statsmodels)
- News scraping (beautifulsoup4)
- Dashboard (dash + plotly)

These are now installed by `INSTALL_PIPELINES.bat`.

---

## 🚀 After Installing

You can now run:

**Single Market:**
```batch
cd pipelines
RUN_AU_PIPELINE.bat  # Australian market
RUN_US_PIPELINE.bat  # US market
RUN_UK_PIPELINE.bat  # UK market
```

**All Markets:**
```batch
cd pipelines
RUN_ALL_PIPELINES.bat  # All 3 markets (50-80 min)
```

---

## 🆘 Still Having Issues?

### Issue: pip upgrade fails
**Solution:** Ignore - not critical

### Issue: statsmodels fails to install
**Symptoms:** Regime analysis won't work (US pipeline only)  
**Solution:** 
```batch
finbert_v4.4.4\venv\Scripts\pip.exe install --upgrade setuptools wheel
finbert_v4.4.4\venv\Scripts\pip.exe install statsmodels
```

### Issue: dash fails to install
**Symptoms:** Dashboard won't work  
**Solution:** Pipeline will still run, reports will be generated (JSON/CSV)

### Issue: All packages fail
**Solution:** Recreate venv:
```batch
rd /s /q finbert_v4.4.4\venv
cd finbert_v4.4.4
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r ..\pipelines\requirements.txt
```

---

## 📝 Updated Installation Flow

**First Time Setup:**

1. Extract package ✅
2. Run `INSTALL.bat` ✅ (base dependencies)
3. **Run `INSTALL_PIPELINES.bat`** ⬅️ NEW STEP
4. Test: `cd pipelines && RUN_UK_PIPELINE.bat`

**You're Done!** 🎉

---

**Version:** v1.3.15.87 ULTIMATE  
**Fix Date:** 2026-02-03  
**Status:** ✅ Tested & Working
