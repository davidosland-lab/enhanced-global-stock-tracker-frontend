# yfinance Crumb/Cookie Authentication Issue

**Your Error**: `Failed to resolve 'query1.finance.yahoo.com'` and `/v1/test/getcrumb` failures

**NOT** a network issue - This is Yahoo Finance blocking the **authentication handshake**

---

## 🎯 What's Really Happening

### The Error Message is Misleading:
```
Failed to get ticker 'CBA.AX' reason: 
HTTPSConnectionPool(host='query1.finance.yahoo.com', port=443): 
Max retries exceeded with url: /v1/test/getcrumb
(Caused by NameResolutionError: Failed to resolve 'query1.finance.yahoo.com')
```

**What it looks like**: DNS resolution failure (network issue)  
**What it really is**: Yahoo Finance blocking the crumb request (authentication failure)

### How yfinance Works (0.2.x):
1. First request: Get "crumb" (authentication token) from `/v1/test/getcrumb`
2. Yahoo validates: Check if request looks like a browser
3. If pass: Yahoo returns crumb → all subsequent requests work
4. If fail: Yahoo blocks → returns error that looks like DNS failure

### Why You're Blocked:
- Yahoo detects automated pattern in crumb request
- Blocks the authentication handshake
- yfinance cannot get crumb → all requests fail
- Error message is cryptic (looks like network issue)

---

## 🔍 Evidence This Is The Problem

### From Your Error Log:

**Index Fetches (Failed on Crumb Request)**:
```
^AXJO: Expecting value: line 1 column 1 (char 0)
^GSPC: Expecting value: line 1 column 1 (char 0)
^IXIC: Expecting value: line 1 column 1 (char 0)
^DJI:  Expecting value: line 1 column 1 (char 0)
```

**Stock Fetches (Failed on Crumb Request)**:
```
CBA.AX: Failed to resolve 'query1.finance.yahoo.com'
BHP.AX: Failed to resolve 'query1.finance.yahoo.com'
WBC.AX: Failed to resolve 'query1.finance.yahoo.com'
... (all stocks)
```

**Pattern**: ALL failures happen at `/v1/test/getcrumb` stage

---

## ✅ Solutions to Try

### Solution 1: Clear yfinance Cache (Quick Fix)

**On Windows**:
```cmd
# Delete yfinance cache folders:
rmdir /s /q "%USERPROFILE%\AppData\Local\py-yfinance"
rmdir /s /q "%USERPROFILE%\.cache\py-yfinance"

# Then test:
python FIX_YFINANCE_CRUMB_ISSUE.py
```

**Or use our script**:
```cmd
python FIX_YFINANCE_CRUMB_ISSUE.py
```

### Solution 2: Downgrade yfinance (Most Reliable)

The crumb system was introduced in yfinance 0.2.x. Version 0.1.x works differently:

```cmd
# Uninstall current version
pip uninstall yfinance -y

# Install older version (no crumb required)
pip install yfinance==0.1.96

# Test
python test_scanner_direct.py
```

**Trade-off**: 
- ✅ No crumb issues
- ❌ May have different blocking patterns
- ❌ Missing some 0.2.x features

### Solution 3: Use requests_cache (Moderate)

Add session caching to help with authentication:

```python
# Install requests-cache
pip install requests-cache

# In your script, before importing yfinance:
import requests_cache
requests_cache.install_cache('yfinance_cache', expire_after=300)

import yfinance as yf
```

### Solution 4: Wait and Retry (Temporary Fix)

Sometimes Yahoo's blocking is temporary (15-30 minutes):

```cmd
# Wait 30 minutes
# Clear cache
python FIX_YFINANCE_CRUMB_ISSUE.py

# Try again
python test_scanner_direct.py
```

### Solution 5: Use Different User-Agent (Advanced)

Modify yfinance to use different browser signature:

```python
# Create file: fix_user_agent.py
import yfinance as yf
from unittest.mock import patch

# Use Chrome 120 User-Agent (latest)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Patch yfinance
with patch('yfinance.utils.get_user_agent', return_value=USER_AGENT):
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    print(hist)
```

---

## 🎯 Recommended Approach

### Step 1: Clear Cache (Try First)
```cmd
python FIX_YFINANCE_CRUMB_ISSUE.py
```

### Step 2: If Still Fails - Downgrade yfinance
```cmd
pip uninstall yfinance -y
pip install yfinance==0.1.96
python test_scanner_direct.py
```

### Step 3: If Downgrade Works - Stick With It
Version 0.1.96 doesn't have the crumb requirement and may be more stable for your use case.

---

## 🔍 Why This Happens

### Yahoo's Multi-Layer Blocking:

**Layer 1**: Rate limiting (requests per minute)  
→ We fixed this with delays and reduced workers

**Layer 2**: HTML scraping detection (`.info` calls)  
→ We fixed this with `ticker.history()` only

**Layer 3**: Authentication handshake blocking (crumb request)  
→ **This is what you're hitting now**

**Layer 4**: IP blocking (after too many Layer 3 failures)  
→ Not there yet, but could happen

### The Crumb System:
- yfinance 0.2.x requires a "crumb" token from Yahoo
- Request to `/v1/test/getcrumb` must look like a real browser
- Yahoo has gotten stricter about this in recent months
- Many users report crumb failures even with correct User-Agent

---

## 📊 Success Indicators

### After Fix, You Should See:
```
Testing fresh yfinance connection...
  Creating new ticker object...
  Fetching data (this will get new crumb)...
  ✓ SUCCESS! AAPL: $175.23
  ✓ Got 5 days of data

✅ yfinance is working - crumb obtained successfully
```

### Then Run Screener:
```cmd
python test_scanner_direct.py
# All tests should pass

RUN_STOCK_SCREENER.bat
# Should complete successfully
```

---

## 🆘 If Nothing Works

### Nuclear Option: Use Alpha Vantage Only

Your screener has Alpha Vantage fallback. Force it to use that:

```python
# Edit: models/screening/stock_scanner.py
# Line ~230, replace:
hist = stock.history(start=start_date, end=end_date)

# With Alpha Vantage fetch:
from models.screening.alpha_vantage_fetcher import AlphaVantageDataFetcher
fetcher = AlphaVantageDataFetcher()
hist = fetcher.fetch_daily_data(symbol, outputsize="full")
```

**Trade-off**:
- ✅ No Yahoo Finance blocking
- ❌ Limited to 500 requests/day (should be enough for 40 stocks)
- ❌ Slower (12 second delay between requests)

---

## 📝 Summary

**Your Issue**: yfinance cannot get authentication crumb from Yahoo Finance

**Why It Happens**: Yahoo's blocking has multiple layers - you've hit Layer 3

**Best Fix**: Clear cache, or downgrade to yfinance 0.1.96

**Long-term**: Consider Alpha Vantage or paid data provider

---

## 🚀 Try This Right Now

```cmd
# On your Windows machine:
cd C:\Users\david\AOSS

# Clear cache
rmdir /s /q "%USERPROFILE%\AppData\Local\py-yfinance"

# Test with US stock (usually less blocked)
python -c "import yfinance as yf; print(yf.Ticker('AAPL').history(period='5d'))"

# If that works, try ASX stock
python -c "import yfinance as yf; print(yf.Ticker('CBA.AX').history(period='5d'))"

# If both work, run screener
python test_scanner_direct.py
```

If **AAPL works but CBA.AX fails** → Yahoo is blocking ASX requests specifically  
If **both fail** → Crumb request is blocked entirely

Let me know the results!
