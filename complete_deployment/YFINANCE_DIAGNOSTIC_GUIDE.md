# yfinance Diagnostic Guide

## Problem Overview

Your FinBERT v4.4.4 overnight screener is experiencing **100% yfinance validation failures** with the error:

```
yfinance - ERROR - Failed to get ticker 'CBA.AX' reason: Expecting value: line 1 column 1 (char 0)
yfinance - ERROR - CBA.AX: No price data found, symbol may be delisted (period=380d)
```

This error means **Yahoo Finance is returning empty responses or HTML instead of JSON data**.

---

## Root Cause Analysis

Based on your logs and our previous successful run, the most likely causes are:

### 1. **Yahoo Finance Rate Limiting / IP Blocking** ⚠️ MOST LIKELY

**Evidence:**
- System worked perfectly in our previous test (7/7 stocks validated)
- Now failing for ALL stocks (0/40 validation success)
- Same error pattern across all tickers (ASX, US indices)
- Error "Expecting value: line 1 column 1" = Yahoo returning empty/HTML instead of JSON

**What happened:**
Yahoo Finance has sophisticated bot detection. When it detects automated scraping patterns, it:
1. Returns empty responses (causing the JSON parse error)
2. Returns HTML error pages (causing the JSON parse error)
3. Blocks requests from your IP temporarily (15 min - 24 hours)

**Why it happened:**
- Running the screener multiple times in quick succession
- Parallel processing with 4 workers making simultaneous requests
- No delays between yfinance calls
- Yahoo's anti-scraping algorithms detected the pattern

---

### 2. **curl_cffi Not Properly Installed** 🔧 POSSIBLE

**Context:**
yfinance 0.2.x+ **requires** `curl_cffi` for browser impersonation to avoid detection.

**If curl_cffi is missing/broken:**
- yfinance cannot impersonate a real browser
- Yahoo Finance easily identifies requests as automated
- Requests get blocked immediately

---

### 3. **Network/Firewall Issues** 🌐 LESS LIKELY

- Corporate firewall blocking Yahoo Finance
- VPN/proxy interfering with requests
- ISP-level blocking (rare for Yahoo Finance)

---

## The Diagnostic Tool

I've created a comprehensive diagnostic script that will identify the exact cause.

### Files Created:

1. **`diagnose_yfinance.py`** - Python diagnostic script (21 KB)
2. **`DIAGNOSE_YFINANCE.bat`** - Windows launcher

### What It Tests:

| Test # | Component | What It Checks |
|--------|-----------|----------------|
| 1 | **Library Imports** | yfinance, curl_cffi, requests, pandas installed |
| 2 | **Network Connectivity** | Can reach Yahoo Finance servers |
| 3 | **DNS Resolution** | Can resolve yahoo.com domains |
| 4 | **Environment Variables** | Proxy/SSL settings that might interfere |
| 5 | **curl_cffi Browser Impersonation** | Browser spoofing working correctly |
| 6 | **Direct Yahoo API Calls** | Raw HTTP requests to Yahoo endpoints |
| 7 | **yfinance Ticker Creation** | Can create Ticker objects |
| 8 | **yfinance fast_info** | Lightweight API method |
| 9 | **yfinance history** | Historical data fetching |
| 10 | **yfinance info** | Comprehensive data fetching |

---

## How to Run the Diagnostic

### Windows:
```batch
cd C:\Users\david\AOSS\complete_deployment
DIAGNOSE_YFINANCE.bat
```

### Linux/Mac:
```bash
cd /path/to/complete_deployment
python3 diagnose_yfinance.py
```

**Expected Duration:** 30-60 seconds

**Output:** 
- Console output with color-coded test results
- `yfinance_diagnostic_results.json` - Detailed results file

---

## Interpreting Results

### ✅ ALL TESTS PASS

**Meaning:** yfinance is working NOW, but Yahoo may have temporarily blocked earlier.

**Actions:**
1. **Wait 1-2 hours** before running screener again
2. **Add delays** between API calls (see Solutions below)
3. **Reduce parallel workers** from 4 to 2
4. **Implement exponential backoff** (system should already have this)

---

### ❌ curl_cffi Tests FAIL

**Meaning:** Critical dependency missing/broken.

**Solutions:**

```bash
# Option 1: Install curl_cffi
pip install curl_cffi

# Option 2: Reinstall (if already installed)
pip uninstall curl_cffi
pip install curl_cffi

# Option 3: Force reinstall with upgraded dependencies
pip install curl_cffi --force-reinstall --upgrade

# Option 4: Install specific version
pip install curl_cffi==0.7.0

# Verify installation
python -c "import curl_cffi; print(curl_cffi.__version__)"
```

**Why curl_cffi matters:**
- yfinance 0.2.x+ uses curl_cffi internally
- curl_cffi makes requests look IDENTICAL to real Chrome browser
- Without it, Yahoo Finance blocks requests immediately

---

### ❌ Network/DNS Tests FAIL

**Meaning:** Cannot reach Yahoo Finance at all.

**Solutions:**

1. **Check Firewall:**
   ```
   - Windows Firewall blocking Python?
   - Corporate firewall blocking finance.yahoo.com?
   - Antivirus blocking network requests?
   ```

2. **Check VPN/Proxy:**
   ```
   - Disconnect VPN and retry
   - Check proxy settings: Control Panel → Internet Options → Connections → LAN Settings
   - Ensure "Automatically detect settings" is enabled
   ```

3. **Check Hosts File:**
   ```
   - Open: C:\Windows\System32\drivers\etc\hosts
   - Ensure no entries blocking yahoo.com
   ```

---

### ❌ yfinance Methods FAIL (but curl_cffi passes)

**Meaning:** Yahoo Finance is blocking your IP/region.

**Solutions:**

1. **Wait** (IP block is temporary):
   - 15 minutes (soft block)
   - 1-2 hours (moderate block)
   - 24 hours (hard block - rare)

2. **Change IP Address:**
   ```
   - Restart router (dynamic IP)
   - Use mobile hotspot
   - Use VPN (with caution - may worsen blocking)
   ```

3. **Reduce Request Rate:**
   ```python
   # Add to your code:
   import time
   
   for ticker in tickers:
       data = yf.Ticker(ticker).history(period='5d')
       time.sleep(1.0)  # 1 second delay between calls
   ```

4. **Contact Your Network Admin:**
   - If on corporate network, Yahoo Finance may be blocked
   - Request whitelisting for finance.yahoo.com

---

## Preventive Measures

To avoid future blocks, implement these changes:

### 1. Add Delays Between Requests

**File:** `models/screening/alpha_vantage_fetcher.py`

```python
def _validate_asx_with_yfinance(self, tickers: List[str]) -> List[str]:
    import yfinance as yf
    import time
    
    valid = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            if hasattr(info, 'last_price') and info.last_price > 0:
                valid.append(ticker)
            
            # ADD THIS: Delay between requests
            time.sleep(0.5)  # 500ms delay
            
        except Exception as e:
            logger.debug(f"✗ {ticker}: {str(e)[:50]}")
    
    return valid
```

---

### 2. Reduce Parallel Workers

**File:** `config/screening_config.yaml`

```yaml
performance:
  parallel_processing: true
  max_workers: 2  # CHANGE FROM 4 to 2
```

Or disable parallel processing entirely:

```yaml
performance:
  parallel_processing: false
  max_workers: 1
```

---

### 3. Implement Request Throttling

**File:** `models/screening/spi_monitor.py`

```python
def _fetch_index_data(self, symbol: str) -> pd.DataFrame:
    import time
    
    # Check cache first
    if symbol in _MARKET_INDICES_CACHE:
        # ... cache logic ...
    
    # ADD THIS: Throttle requests
    if hasattr(self, '_last_request_time'):
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.0:  # Minimum 1 second between requests
            time.sleep(1.0 - elapsed)
    
    # Fetch data
    df = yf.Ticker(symbol).history(period="6mo", interval="1d")
    
    # ADD THIS: Track request time
    self._last_request_time = time.time()
    
    return df
```

---

### 4. Enable yfinance Debug Mode (Temporary)

For troubleshooting, add to top of `run_overnight_screener.py`:

```python
import yfinance as yf

# Enable debug logging
yf.enable_debug_mode()
```

This will show detailed HTTP requests and responses.

---

### 5. Implement Exponential Backoff

**File:** `models/screening/alpha_vantage_fetcher.py`

```python
def _validate_asx_with_yfinance(self, tickers: List[str]) -> List[str]:
    import yfinance as yf
    import time
    
    valid = []
    for ticker in tickers:
        retries = 3
        for attempt in range(retries):
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info
                if hasattr(info, 'last_price') and info.last_price > 0:
                    valid.append(ticker)
                break  # Success - exit retry loop
                
            except Exception as e:
                if attempt < retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** attempt
                    logger.debug(f"Retry {attempt+1}/{retries} for {ticker} in {delay}s")
                    time.sleep(delay)
                else:
                    logger.debug(f"✗ {ticker}: {str(e)[:50]}")
    
    return valid
```

---

## Immediate Actions (Priority Order)

### 🔴 Priority 1: Run Diagnostic

```batch
cd C:\Users\david\AOSS\complete_deployment
DIAGNOSE_YFINANCE.bat
```

**Purpose:** Identify exact cause (curl_cffi vs network vs rate limiting)

---

### 🟠 Priority 2: Wait and Retry

If diagnostic shows Yahoo blocking:

1. **Wait 2 hours**
2. **Run diagnostic again** to confirm block lifted
3. **Run screener once** to validate

---

### 🟡 Priority 3: Implement Preventive Measures

Once working again:

1. Add 0.5-1 second delays between yfinance calls
2. Reduce parallel workers from 4 to 2
3. Test with smaller stock list (10 stocks instead of 40)

---

### 🟢 Priority 4: Consider Alternatives

If Yahoo Finance remains unreliable:

**Option A: Alpha Vantage Premium**
- $49/month for 1200 requests/day
- More reliable for ASX stocks
- Already integrated in your system

**Option B: Polygon.io**
- $29/month for real-time data
- Excellent API reliability
- Requires code changes

**Option C: Yahoo Finance via RapidAPI**
- $10-30/month
- Official API (less blocking)
- Minimal code changes

---

## Expected Diagnostic Output

### Scenario 1: curl_cffi Missing

```
TEST 1: Basic Library Imports
✓ yfinance import: PASS (Version: 0.2.66)
✗ curl_cffi import: FAIL (curl_cffi not found)
✓ requests import: PASS (Version: 2.32.4)
✓ pandas import: PASS (Version: 2.3.2)

TEST 7: curl_cffi Browser Impersonation
✗ curl_cffi browser impersonation: FAIL (curl_cffi not installed)

DIAGNOSIS:
🔴 CRITICAL: curl_cffi NOT WORKING
   This is the most likely cause of your issues.
   
   SOLUTION:
   1. Install curl_cffi: pip install curl_cffi
```

---

### Scenario 2: Yahoo Finance Blocking

```
TEST 1: Basic Library Imports
✓ yfinance import: PASS (Version: 0.2.66)
✓ curl_cffi import: PASS (Version: 0.13.0)

TEST 7: curl_cffi Browser Impersonation
✓ curl_cffi Chrome impersonation: PASS

TEST 8: yfinance fast_info Method
✗ fast_info(CBA.AX): FAIL (Expecting value: line 1 column 1)
✗ fast_info(^AXJO): FAIL (Expecting value: line 1 column 1)

DIAGNOSIS:
⚠ YFINANCE API FAILURES
   yfinance methods failing despite curl_cffi working.
   
   POSSIBLE CAUSES:
   - Yahoo Finance API rate limiting
   - Yahoo Finance blocking automated requests
   
   SOLUTIONS:
   1. Wait 5-10 minutes (rate limit cooldown)
   2. Try using VPN to change IP address
```

---

### Scenario 3: Everything Working

```
TEST 1: Basic Library Imports
✓ yfinance import: PASS (Version: 0.2.66)
✓ curl_cffi import: PASS (Version: 0.13.0)

TEST 8: yfinance fast_info Method
✓ fast_info(CBA.AX): PASS (Price: 142.35)
✓ fast_info(^AXJO): PASS (Price: 8234.10)

DIAGNOSIS:
✓ ALL DIAGNOSTICS PASSED
   The yfinance library appears to be working correctly.
   
   POSSIBLE CAUSES OF YOUR ORIGINAL FAILURE:
   1. Timing issue - Yahoo may have been temporarily blocking
   2. Concurrent requests triggering rate limits
   
   RECOMMENDATIONS:
   1. Try running your screener again (issue may be resolved)
   2. Add delays between yfinance calls (0.5-1 second)
```

---

## Technical Details: Why "Expecting value: line 1 column 1"?

This error occurs when Python's `json.loads()` receives invalid JSON:

```python
import json

# Normal Yahoo Finance response (JSON):
response = '{"chart": {"result": [{"meta": {...}}]}}'
json.loads(response)  # ✓ Works

# Empty response (Yahoo blocking):
response = ''
json.loads(response)  # ✗ Expecting value: line 1 column 1 (char 0)

# HTML error page (Yahoo blocking):
response = '<!DOCTYPE html><html>...'
json.loads(response)  # ✗ Expecting value: line 1 column 1 (char 0)
```

When yfinance gets these empty/HTML responses, it tries to parse them as JSON and fails with this error.

---

## Success Criteria

After running diagnostic and implementing fixes, you should see:

### ✅ Diagnostic Output:
```
Total Tests Run: 30+
✓ Passed: 28+
✗ Failed: 0
⚠ Warnings: 0-2

✓ ALL DIAGNOSTICS PASSED
```

### ✅ Screener Output:
```
Step 3: Scanning stocks...
  Using parallel processing with 2 workers

models.screening.alpha_vantage_fetcher - INFO - Validation complete: 5 passed
models.screening.stock_scanner - INFO -   Validation: 5/5 passed
__main__ - INFO -   ✓ Financials: 5 valid stocks

✓ Total stocks scanned: 40
```

---

## Support and Troubleshooting

### If Diagnostic Fails:

1. **Share Results File:**
   - Email: `yfinance_diagnostic_results.json`
   - Include: Full console output from diagnostic

2. **Check GitHub Issues:**
   - yfinance: https://github.com/ranaroussi/yfinance/issues
   - Search for: "Expecting value: line 1 column 1"

3. **Alternative Data Sources:**
   - If Yahoo Finance unreliable, consider Premium APIs
   - Alpha Vantage Premium: $49/month
   - Polygon.io: $29/month

---

## Summary

**Problem:** Yahoo Finance returning empty responses instead of JSON

**Most Likely Cause:** Rate limiting / IP blocking due to repeated automated requests

**Solution:** 
1. Run diagnostic to confirm
2. Wait 1-2 hours if blocked
3. Add delays between requests (0.5-1s)
4. Reduce parallel workers (4→2)
5. Implement exponential backoff

**Prevention:**
- Never run screener more than once per hour
- Always include delays between API calls
- Use caching aggressively (already implemented)
- Monitor for rate limit warnings

---

## Next Steps

1. **Run** `DIAGNOSE_YFINANCE.bat` 
2. **Review** the console output and diagnosis
3. **Follow** the recommended solutions for any failures
4. **Implement** preventive measures (delays, reduced workers)
5. **Test** screener with small stock list (5-10 stocks)
6. **Scale up** gradually if successful

---

**Created:** 2025-11-10  
**Version:** 1.0  
**Status:** Ready for Use
