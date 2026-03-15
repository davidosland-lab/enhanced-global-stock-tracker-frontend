# Complete Patch v1.3.15.43 - Release Notes

**Release Date**: January 27, 2026  
**Patch Name**: `COMPLETE_PATCH_v1.3.15.43.zip`  
**Status**: PRODUCTION READY

---

## 📦 What's Included

This is a **combined patch** that includes ALL updates from v1.3.15.40 through v1.3.15.43:

### **v1.3.15.40 - Global Sentiment Enhancement**
- Expanded global news sources (18 → 50+ keywords)
- Added Reuters US, BBC US, White House news feeds
- Increased macro sentiment weight from 20% to 35%
- Enhanced coverage of US political uncertainty (tariffs, trade wars, immigration)
- Applied to all three markets: UK, US, AU

### **v1.3.15.41 - ASX Chart Fix**
- Fixed ASX All Ordinaries chart display on dashboard
- Corrected midnight-spanning session handling (23:00 prev day - 05:00)
- Fixed reference price calculation (now uses true previous close)
- Extended time filter to include full 05:00-05:59 GMT hour
- Added debug logging for reference price

### **v1.3.15.42 - UK Pipeline KeyError Fix**
- Fixed crash: `KeyError: 'opportunity_score'`
- Changed direct dictionary access to safe `.get()` method with fallbacks
- Gracefully handles missing keys (opportunity_score, signal, confidence)
- Pipeline now completes successfully without errors

### **v1.3.15.43 - Bank of England RSS Scraper**
- Added RSS feed scraper for Bank of England news
- More reliable than HTML scraping (website structure independent)
- Scrapes from: `https://www.bankofengland.co.uk/news.rss`
- Filters for relevance (interest rates, MPC, inflation, governor speeches)
- Falls back to HTML scraping if feedparser not available
- Includes BoE speeches feed as backup

---

## 📊 Files Modified

| File | Changes | Version |
|------|---------|---------|
| `run_uk_full_pipeline.py` | KeyError fix (safe dict access) | v1.3.15.42 |
| `unified_trading_dashboard.py` | ASX chart fix (midnight handling) | v1.3.15.41 |
| `models/screening/macro_news_monitor.py` | Global + BoE RSS scraper | v1.3.15.40 + v1.3.15.43 |
| `models/screening/uk_overnight_pipeline.py` | UK macro integration (35% weight) | v1.3.15.40 |
| `models/screening/us_overnight_pipeline.py` | US macro integration (35% weight) | v1.3.15.40 |
| `models/screening/overnight_pipeline.py` | AU macro integration (35% weight) | v1.3.15.40 |

**Total**: 6 Python files updated

---

## 🚀 Installation

### **Method 1: Automated (Recommended)**

1. Extract `COMPLETE_PATCH_v1.3.15.43.zip` to any location
2. Open Command Prompt in extracted folder
3. Run: `INSTALL_PATCH.bat`
4. Follow on-screen instructions

The script will:
- ✅ Auto-detect your installation directory
- ✅ Create automatic backup
- ✅ Install all updated files
- ✅ Install required dependencies (feedparser)
- ✅ Verify installation
- ✅ Show next steps

**Installation time**: ~30 seconds

---

### **Method 2: Manual**

```bash
# 1. Backup existing files
mkdir backup
copy run_uk_full_pipeline.py backup\
copy unified_trading_dashboard.py backup\
copy models\screening\*.py backup\

# 2. Install feedparser
pip install feedparser

# 3. Copy patch files
copy COMPLETE_PATCH_v1.3.15.43\run_uk_full_pipeline.py .
copy COMPLETE_PATCH_v1.3.15.43\unified_trading_dashboard.py .
copy COMPLETE_PATCH_v1.3.15.43\models\screening\*.py models\screening\

# 4. Restart dashboard (if running)
# Press Ctrl+C, then:
python unified_trading_dashboard.py
```

---

## ✅ Verification

### **1. Check UK Pipeline**
```bash
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
```

**Expected**:
- ✅ No KeyError crash
- ✅ Pipeline completes successfully
- ✅ Top opportunities display correctly
- ✅ Report generated in `reports/uk/`

### **2. Verify BoE News**
```bash
# Check logs for BoE articles
type logs\uk_pipeline.log | findstr "Bank of England"
```

**Expected output**:
```
Bank of England News (RSS): 4-6 articles
Macro Sentiment: X/100 (BoE impact included)
```

### **3. Check ASX Chart**
1. Open dashboard: `http://localhost:8050`
2. Navigate to "24-Hour Market Performance" panel
3. ASX All Ords (cyan line) should show realistic movement (not flat)
4. Percentage should match ASX website (±0.1%)

### **4. Test BoE RSS Scraper**
```python
python -c "from models.screening.macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); r = m.get_macro_sentiment(); print(f'BoE articles: {len([a for a in r[\"top_articles\"] if \"BoE\" in a[\"source\"]])}')"
```

**Expected**: `BoE articles: 4` (or similar)

---

## 📋 Requirements

### **Python Packages**
- `feedparser` (new requirement for BoE RSS)
  - Installed automatically by `INSTALL_PATCH.bat`
  - Manual install: `pip install feedparser`

### **Existing Requirements** (unchanged)
- Python 3.8+
- yfinance
- yahooquery
- pandas
- numpy
- beautifulsoup4
- requests

---

## 🔧 What Changed

### **Before Patch**

| Issue | Status |
|-------|--------|
| UK pipeline crashes at end | ❌ KeyError |
| ASX chart displays incorrectly | ❌ Flat/wrong |
| BoE news in pipeline | ❌ 0 articles |
| Global news sources | Limited (2 sources) |
| Macro sentiment weight | 20% |

### **After Patch**

| Issue | Status |
|-------|--------|
| UK pipeline crashes at end | ✅ Fixed |
| ASX chart displays correctly | ✅ Fixed |
| BoE news in pipeline | ✅ 4-6 articles |
| Global news sources | Expanded (6+ sources) |
| Macro sentiment weight | 35% |

---

## 📈 Performance Impact

### **UK Pipeline**
- **Before**: Crashes with KeyError, 0 BoE articles
- **After**: Completes successfully, 4-6 BoE articles, macro impact visible

### **Dashboard**
- **Before**: ASX chart flat or incorrect (-0.2%)
- **After**: ASX chart shows realistic movement, matches ASX website

### **Sentiment Quality**
- **Before**: 2 articles (BBC only), 20% macro weight
- **After**: 8-10 articles (BBC + BoE + Reuters), 35% macro weight

### **Trading Impact**
```
Example: BoE announces rate hike

Before patch:
  UK Sentiment: 58.0 (no BoE news)
  Trades: 4 positions

After patch:
  UK Sentiment: 52.9 (BoE impact -5.1)
  Trades: 2 positions (more cautious)
```

---

## 🛠️ Troubleshooting

### **Issue: Installation script can't find directory**

**Solution**: Run from installation directory or specify path when prompted

### **Issue: feedparser not installed**

**Solution**:
```bash
pip install feedparser
```

### **Issue: UK pipeline still shows 0 BoE articles**

**Checks**:
1. Verify feedparser installed: `pip list | findstr feedparser`
2. Test BoE RSS manually: `curl https://www.bankofengland.co.uk/news.rss`
3. Check logs for errors: `type logs\uk_pipeline.log`

### **Issue: Dashboard ASX chart still wrong**

**Solution**: 
1. Restart dashboard (Ctrl+C, then restart)
2. Hard refresh browser (Ctrl+Shift+R)
3. Verify file updated: `type unified_trading_dashboard.py | findstr "two_days_ago"`

### **Issue: Want to rollback**

**Solution**:
```bash
# Restore from backup (created automatically)
xcopy /Y /S backup_YYYYMMDD_HHMMSS\*.* .
```

---

## 📚 Documentation Files Included

1. **GLOBAL_SENTIMENT_ENHANCEMENT_v1.3.15.40.md**
   - Global news expansion details
   - Keyword lists (50+)
   - US political coverage

2. **ASX_CHART_FIX_v1.3.15.41.md**
   - ASX chart technical details
   - Midnight-spanning logic
   - Reference price calculation

3. **UK_PIPELINE_KEYERROR_FIX_v1.3.15.42.md**
   - KeyError root cause
   - Safe dictionary access patterns
   - BoE news source confirmation

4. **BOE_NEWS_NOT_APPEARING_FIX.md**
   - Diagnostic findings
   - RSS vs HTML scraping comparison
   - BoE RSS feed implementation

5. **README_v1.3.15.43.md** (this file)
   - Complete patch overview
   - Installation instructions
   - Verification steps

---

## 🎯 Summary

### **Patch Name**
**COMPLETE_PATCH_v1.3.15.43.zip**

### **Size**
~150 KB (6 Python files + 5 documentation files + installer)

### **Installation Time**
30 seconds (automated) | 2 minutes (manual)

### **Downtime**
15 seconds (dashboard restart only)

### **Compatibility**
Compatible with v1.3.15.32 and later

### **Status**
✅ PRODUCTION READY

### **Git Commits Included**
- d2674e4 (v1.3.15.40 - Global sentiment)
- 259e7b8 (v1.3.15.41 - ASX chart)
- ade9844 (v1.3.15.42 - UK KeyError)
- 5b0b5a1 (v1.3.15.43 - BoE RSS)

---

## ✅ Installation Checklist

- [ ] Extract COMPLETE_PATCH_v1.3.15.43.zip
- [ ] Run INSTALL_PATCH.bat (or manual install)
- [ ] Verify feedparser installed
- [ ] Restart dashboard
- [ ] Test UK pipeline (no KeyError)
- [ ] Check BoE news in logs (4-6 articles)
- [ ] Verify ASX chart (realistic movement)
- [ ] Confirm macro sentiment (35% weight)

---

**Version**: v1.3.15.43  
**Release Date**: January 27, 2026  
**Patch Type**: Combined cumulative patch  
**Status**: PRODUCTION READY ✅

Run `INSTALL_PATCH.bat` to install all updates automatically! 🚀
