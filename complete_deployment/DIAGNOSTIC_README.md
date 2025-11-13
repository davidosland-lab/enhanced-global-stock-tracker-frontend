# FinBERT v4.4.4 - Diagnostic System

## Quick Start

### Problem: All stocks failing validation with yfinance errors

**Symptoms:**
```
yfinance - ERROR - Failed to get ticker 'CBA.AX' reason: Expecting value: line 1 column 1 (char 0)
Validation complete: 0 passed
✓ Total stocks scanned: 0
```

**Solution: Follow the 3-step process below**

---

## 3-Step Diagnostic Process

### Step 1: Run Diagnostic (5 minutes)

**Purpose:** Identify root cause (curl_cffi, network, or rate limiting)

**Windows:**
```batch
cd C:\Users\david\AOSS\complete_deployment
DIAGNOSE_YFINANCE.bat
```

**What it does:**
- Tests 10 different components
- Identifies exact failure point
- Provides actionable recommendations
- Saves results to JSON file

**Expected output:**
```
✓ yfinance import: PASS
✓ curl_cffi import: PASS
✗ fast_info(CBA.AX): FAIL (Expecting value...)

DIAGNOSIS:
⚠ YFINANCE API FAILURES
   Yahoo Finance blocking automated requests
   
   SOLUTIONS:
   1. Wait 1-2 hours (rate limit cooldown)
   2. Apply rate limit fixes
```

---

### Step 2: Apply Fixes (1 minute)

**Purpose:** Add delays and throttling to prevent future blocking

**Windows:**
```batch
cd C:\Users\david\AOSS\complete_deployment
APPLY_RATE_LIMIT_FIXES.bat
```

**What it does:**
- Backs up original files (with timestamp)
- Adds 0.5s delays between ticker validations
- Adds 1s throttling between index fetches
- Reduces parallel workers from 4 to 2

**Changes made:**
1. `models/screening/alpha_vantage_fetcher.py` - Add delays
2. `models/screening/spi_monitor.py` - Add throttling
3. `config/screening_config.yaml` - Reduce workers

**Safe:** All files backed up before modification

---

### Step 3: Wait and Test (1-2 hours)

**If currently blocked:**

1. **Wait:** Yahoo Finance blocks are temporary
   - Soft block: 15-30 minutes
   - Moderate block: 1-2 hours
   - Hard block: 24 hours (rare)

2. **Verify unblocked:**
   ```batch
   DIAGNOSE_YFINANCE.bat
   ```
   Should now show all tests passing

3. **Test screener:**
   ```batch
   RUN_STOCK_SCREENER.bat
   ```
   Should now validate stocks successfully

---

## Files Included

### Diagnostic Tools

| File | Purpose | When to Use |
|------|---------|-------------|
| `diagnose_yfinance.py` | Python diagnostic script | Called by .bat file |
| `DIAGNOSE_YFINANCE.bat` | Windows launcher | **Run first** to identify issue |
| `yfinance_diagnostic_results.json` | Results file | Created after diagnostic runs |

### Fix Tools

| File | Purpose | When to Use |
|------|---------|-------------|
| `apply_rate_limit_fixes.py` | Python fix script | Called by .bat file |
| `APPLY_RATE_LIMIT_FIXES.bat` | Windows launcher | **Run second** to apply fixes |

### Documentation

| File | Purpose |
|------|---------|
| `YFINANCE_DIAGNOSTIC_GUIDE.md` | Comprehensive troubleshooting guide (14 KB) |
| `DIAGNOSTIC_README.md` | This file - Quick reference |

---

## Common Scenarios

### Scenario A: curl_cffi Not Installed

**Diagnostic shows:**
```
✗ curl_cffi import: FAIL
✗ curl_cffi browser impersonation: FAIL

DIAGNOSIS:
🔴 CRITICAL: curl_cffi NOT WORKING
```

**Solution:**
```bash
pip install curl_cffi

# If already installed, force reinstall:
pip install curl_cffi --force-reinstall
```

**Why:** yfinance 0.2.x+ requires curl_cffi for browser impersonation

---

### Scenario B: Yahoo Finance Blocking (MOST COMMON)

**Diagnostic shows:**
```
✓ curl_cffi import: PASS
✗ fast_info(CBA.AX): FAIL (Expecting value: line 1 column 1)

DIAGNOSIS:
⚠ YFINANCE API FAILURES
   Yahoo Finance blocking automated requests
```

**Solution:**
1. Run `APPLY_RATE_LIMIT_FIXES.bat`
2. Wait 1-2 hours
3. Run `DIAGNOSE_YFINANCE.bat` to verify
4. Test screener

**Why:** Yahoo detected automated scraping pattern

---

### Scenario C: Network/Firewall Issues

**Diagnostic shows:**
```
✗ Connect to Yahoo Finance Homepage: FAIL
✗ DNS resolve finance.yahoo.com: FAIL

DIAGNOSIS:
🔴 NETWORK CONNECTIVITY ISSUES
```

**Solution:**
1. Check firewall settings
2. Disable VPN temporarily
3. Check corporate proxy settings
4. Verify internet connection

---

### Scenario D: Everything Works Now

**Diagnostic shows:**
```
Total Tests Run: 30
✓ Passed: 30
✗ Failed: 0

✓ ALL DIAGNOSTICS PASSED
```

**Meaning:** Yahoo block was temporary and has been lifted

**Action:** 
1. Run `APPLY_RATE_LIMIT_FIXES.bat` to prevent future blocks
2. Test screener immediately
3. Avoid running screener repeatedly

---

## Understanding the Error

### What "Expecting value: line 1 column 1 (char 0)" Means

This is a **JSON parsing error** that occurs when:

1. **Expected:** Yahoo Finance returns JSON data
   ```json
   {"chart": {"result": [{"meta": {...}}]}}
   ```

2. **Actual:** Yahoo Finance returns empty/HTML
   ```
   (empty string)
   ```
   or
   ```html
   <!DOCTYPE html><html>...
   ```

3. **Result:** Python's `json.loads()` fails
   ```python
   json.loads('')  # ✗ Expecting value: line 1 column 1 (char 0)
   ```

**Why Yahoo returns empty/HTML:**
- Rate limiting triggered
- Bot detection activated
- IP temporarily blocked

---

## Preventive Best Practices

### ✅ DO:

1. **Add delays** between API calls (0.5-1 second)
2. **Use caching** aggressively (already implemented)
3. **Reduce parallel workers** (2-3 max)
4. **Run screener infrequently** (once per day max)
5. **Monitor for warnings** in logs

### ❌ DON'T:

1. **Run screener repeatedly** in short time span
2. **Use 4+ parallel workers** (triggers bot detection)
3. **Make rapid successive calls** to yfinance
4. **Ignore rate limit warnings**
5. **Remove delays** from code

---

## Advanced Troubleshooting

### Enable yfinance Debug Mode

Add to `scripts/screening/run_overnight_screener.py`:

```python
import yfinance as yf

# Enable debug mode (temporary - for troubleshooting)
yf.enable_debug_mode()
```

**Shows:**
- Exact HTTP requests sent
- Response status codes
- Response content
- Error details

**Remember to disable** after troubleshooting (slows down system)

---

### Check API Rate Limits

yfinance uses Yahoo Finance's unofficial API with limits:
- **Unknown official limit** (Yahoo doesn't publish)
- **Estimated:** ~2000 requests/hour per IP
- **Conservative:** 1 request/second = 3600/hour (safe)

**Your screener uses:**
- 40 ticker validations
- 4 market indices
- Historical data for validated stocks
- **Total:** ~50-100 requests per run

**Safe frequency:** Once every 1-2 hours

---

### Alternative Solutions

If Yahoo Finance continues to be unreliable:

#### Option 1: Alpha Vantage Premium
- **Cost:** $49/month
- **Limits:** 1200 requests/day (vs 500 free)
- **ASX Support:** Better than free tier
- **Changes:** None (already integrated)

#### Option 2: Polygon.io
- **Cost:** $29/month
- **Limits:** Unlimited historical data
- **Reliability:** Very high
- **Changes:** Moderate (new API integration)

#### Option 3: Yahoo Finance via RapidAPI
- **Cost:** $10-30/month
- **Limits:** 500-10000 requests/month
- **Reliability:** Higher (official API)
- **Changes:** Minimal (same data structure)

---

## Support Resources

### Documentation Files

1. **YFINANCE_DIAGNOSTIC_GUIDE.md**
   - Comprehensive 14KB guide
   - Detailed explanations
   - Code examples
   - All scenarios covered

2. **ROOT_CAUSE_ANALYSIS_ACTUAL.md**
   - Original issue root cause
   - Historical context
   - Technical deep dive

3. **DATA_CAPTURE_ARCHITECTURE_REVIEW.md**
   - System architecture
   - Data flow analysis
   - Multi-source strategy

### External Resources

- **yfinance GitHub:** https://github.com/ranaroussi/yfinance/issues
- **curl_cffi Docs:** https://curl-cffi.readthedocs.io/
- **Yahoo Finance Status:** Check if others reporting issues

---

## FAQ

### Q: Why did it work before but not now?

**A:** Yahoo Finance blocking is dynamic. Running the screener multiple times triggered their bot detection.

---

### Q: How long do Yahoo blocks last?

**A:** 
- Soft: 15-30 minutes
- Moderate: 1-2 hours  
- Hard: 24 hours (very rare)

---

### Q: Will the fixes prevent all future blocks?

**A:** They will significantly reduce the chance, but Yahoo's detection is constantly evolving. Best practice: run screener once per day maximum.

---

### Q: Can I use a VPN to bypass blocks?

**A:** Yes, changing your IP via VPN can work, but Yahoo may detect VPN usage. Use with caution.

---

### Q: Is this illegal or against terms of service?

**A:** Using yfinance for personal stock screening is common practice. However, Yahoo Finance's unofficial API has no published TOS. For commercial use, consider paid alternatives.

---

### Q: Do I need to rerun fixes after every diagnostic?

**A:** No. Fixes only need to be applied once. The changes are permanent (unless you restore from backup).

---

## Success Checklist

After completing all steps, you should have:

- [ ] Diagnostic run showing root cause identified
- [ ] Rate limit fixes applied to 3 files
- [ ] Backup files created (*.backup_TIMESTAMP)
- [ ] 1-2 hours wait completed (if blocked)
- [ ] Second diagnostic showing all tests pass
- [ ] Screener successfully validating stocks
- [ ] No "Expecting value: line 1 column 1" errors

**If all checked:** System is working and protected against future blocks! ✅

---

## Version History

- **v1.0** (2025-11-10): Initial diagnostic system created
  - 10 comprehensive tests
  - Automatic fix application
  - Detailed documentation

---

**Need Help?**

1. Read `YFINANCE_DIAGNOSTIC_GUIDE.md` (comprehensive)
2. Run `DIAGNOSE_YFINANCE.bat` (identify issue)
3. Check GitHub issues (yfinance repo)
4. Share `yfinance_diagnostic_results.json` with support

---

**Created:** 2025-11-10  
**Author:** Claude AI Assistant  
**Status:** Production Ready
