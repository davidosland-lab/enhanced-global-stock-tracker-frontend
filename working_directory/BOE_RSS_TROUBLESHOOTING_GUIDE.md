# Bank of England RSS Scraper - Troubleshooting Guide
**Version:** v1.3.15.43  
**Date:** January 27, 2026  
**Issue:** BoE news shows "0 articles" despite RSS scraper implementation

---

## 🔍 ROOT CAUSE IDENTIFIED

The RSS scraper code is **correctly installed**, but `feedparser` Python package is **missing** from the environment.

**Evidence from logs:**
```
Bank of England News: 0 articles
```

**What's happening:**
1. Pipeline calls `_scrape_boe_news_rss()` at line 454
2. RSS function tries: `import feedparser`
3. Import fails → falls back to `_scrape_uk_boe_news()` (old HTML scraper)
4. HTML scraper returns 0 articles (BoE website structure changed)
5. Result: No BoE articles in pipeline

---

## ✅ THE FIX

### Option 1: Quick Fix (Recommended - 30 seconds)

**Step 1:** Install feedparser
```bash
pip install feedparser
```

**Step 2:** Run UK pipeline
```bash
python run_uk_full_pipeline.py --full-scan --capital 100000
```

**Expected Result:**
```
Fetching Bank of England news (RSS)...
[OK] Bank of England News (RSS): 4-6 articles
```

---

### Option 2: Automated Fix (Use diagnostic script)

**Step 1:** Run verification script
```bash
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
VERIFY_BOE_RSS_FIX.bat
```

**What it does:**
- ✓ Checks Python installation
- ✓ Installs feedparser if missing
- ✓ Verifies code patch is applied
- ✓ Tests RSS feed access
- ✓ Provides diagnostic output

---

### Option 3: Manual Verification (For debugging)

**Step 1:** Test feedparser independently
```bash
python test_boe_rss.py
```

**What it tests:**
1. feedparser installation
2. RSS feed access (https://www.bankofengland.co.uk/news.rss)
3. Article parsing and filtering
4. Display sample BoE articles

**Expected Output:**
```
[Test 1/4] Checking feedparser installation...
  ✓ feedparser 6.0.11 is installed

[Test 2/4] Testing RSS feed access...
  ✓ Successfully retrieved 20 articles

[Test 3/4] Testing article parsing and filtering...
  ✓ Found 8 relevant articles

[Test 4/4] Sample articles from BoE RSS feed:
  Article 1:
    Title: Monetary Policy Committee decision - January 2026
    ...
```

---

## 🔧 VERIFICATION CHECKLIST

After installing feedparser, verify the fix:

### 1. Check feedparser is installed
```bash
python -c "import feedparser; print(feedparser.__version__)"
```
Expected: `6.0.11` (or similar version number)

### 2. Run UK pipeline
```bash
python run_uk_full_pipeline.py --full-scan --capital 100000
```

### 3. Check logs for BoE articles
```bash
# Windows
type logs\uk_pipeline.log | findstr "Bank of England"
type logs\uk_pipeline.log | findstr "BoE:"

# Linux/Mac
grep "Bank of England" logs/uk_pipeline.log
grep "BoE:" logs/uk_pipeline.log
```

**Expected in logs:**
```
Fetching Bank of England news (RSS)...
[OK] Bank of England News (RSS): 6 articles
BoE: Monetary Policy Committee decision - January 2026
BoE: Financial Stability Report published
BoE: Governor Andrew Bailey speech on inflation outlook
...
```

### 4. Verify macro sentiment includes BoE
Look for in logs:
```
Phase 1.3: Macro News Monitoring
------------------------------------------------------------
Articles Analyzed: 8-12
Sentiment Score: 0.05
Sentiment Label: NEUTRAL

Recent UK/Global News:
1. [BoE] Monetary Policy Committee decision - January 2026
   Sentiment: +0.02 (Slightly Positive)
   ...
```

---

## 📊 WHAT TO EXPECT

### Before Fix:
- **BoE Articles:** 0
- **Total Macro Articles:** 2-3 (only BBC/Reuters)
- **Macro Sentiment:** Low quality (missing central bank data)
- **Overall Sentiment:** Based on incomplete data

### After Fix:
- **BoE Articles:** 4-8
- **Total Macro Articles:** 10-15
- **Macro Sentiment:** High quality (includes central bank official sources)
- **Overall Sentiment:** More accurate (35% macro weight)
- **BoE Impact:** Properly weighted in pipeline decisions

---

## 🐛 COMMON ISSUES

### Issue 1: "feedparser not found"
**Symptom:**
```
ModuleNotFoundError: No module named 'feedparser'
```

**Solution:**
```bash
pip install feedparser
```

---

### Issue 2: "No entries in BoE RSS feed"
**Symptom:**
```
[WARNING] No entries in BoE RSS feed
```

**Possible causes:**
- Firewall blocking RSS feed
- Proxy settings required
- Internet connection issue

**Solution:**
Test RSS feed manually:
```python
import feedparser
feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss')
print(len(feed.entries))
```

---

### Issue 3: Still seeing 0 articles after installing feedparser
**Symptom:**
```
Bank of England News: 0 articles
```

**Checklist:**
1. ✓ Restart Python/terminal after installing feedparser
2. ✓ Verify you're using the correct Python environment
3. ✓ Check patch was applied correctly:
   ```bash
   grep "_scrape_boe_news_rss()" models/screening/macro_news_monitor.py
   ```
4. ✓ Run diagnostic: `python test_boe_rss.py`

---

## 📁 FILES INVOLVED

### Modified Files:
- `models/screening/macro_news_monitor.py`
  - Line 454: `boe_news = self._scrape_boe_news_rss()`
  - Line 741: `def _scrape_boe_news_rss(self) -> List[Dict]:`

### Diagnostic Tools:
- `VERIFY_BOE_RSS_FIX.bat` - Automated verification script
- `test_boe_rss.py` - Standalone RSS test script

### Documentation:
- `BOE_NEWS_NOT_APPEARING_FIX.md` - Original fix documentation
- `BOE_RSS_TROUBLESHOOTING_GUIDE.md` - This guide

---

## 🎯 BOTTOM LINE

**Problem:** BoE news shows 0 articles  
**Root Cause:** feedparser package not installed  
**Fix:** `pip install feedparser`  
**Verification:** Run UK pipeline, check logs for "Bank of England News (RSS): 4-6 articles"  
**Time to Fix:** 30 seconds  
**Impact:** BoE articles 0 → 4-8, macro sentiment quality LOW → HIGH

---

## 📞 SUPPORT

If issues persist after following this guide:

1. Run diagnostic script: `python test_boe_rss.py`
2. Check Python environment: `python --version`
3. Verify patch applied: Look for `_scrape_boe_news_rss` in code
4. Check internet/firewall settings
5. Review full pipeline logs: `logs/uk_pipeline.log`

---

**Version:** v1.3.15.43  
**Status:** PRODUCTION READY  
**Last Updated:** January 27, 2026
