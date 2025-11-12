# Yahoo Finance Block Test Guide

## Quick Test

### Windows:
```bash
cd C:\Users\david\AOSS\complete_deployment
TEST_YAHOO_BLOCKING.bat
```

### Linux/Mac:
```bash
cd /path/to/complete_deployment
python test_yahoo_blocking.py
```

**Duration:** ~10 seconds

---

## What It Tests

The script performs 4 quick tests:

1. **yfinance import** - Checks library is installed
2. **CBA.AX price** - Tests ASX stock fetch
3. **^GSPC price** - Tests US index fetch  
4. **BHP.AX history** - Tests historical data fetch

---

## Understanding Results

### ✅ NOT BLOCKED (All tests pass)

```
Test 1: Importing yfinance...
  ✓ yfinance imported successfully

Test 2: Fetching CBA.AX (ASX stock)...
  ✓ SUCCESS - Got price: $142.35
  Response time: 0.45s

Test 3: Fetching ^GSPC (S&P 500)...
  ✓ SUCCESS - Got price: $5891.23
  Response time: 0.38s

Test 4: Fetching historical data for BHP.AX...
  ✓ SUCCESS - Got 5 days of data
  Latest close: $41.23
  Response time: 0.52s

✅ RESULT: Yahoo Finance is WORKING
```

**What this means:**
- Your IP is NOT blocked
- Yahoo Finance is responding normally
- You can run the stock screener now

**Next step:**
```bash
cd C:\Users\david\AOSS\complete_deployment
RUN_STOCK_SCREENER.bat
```

---

### ❌ BLOCKED (Tests fail)

```
Test 1: Importing yfinance...
  ✓ yfinance imported successfully

Test 2: Fetching CBA.AX (ASX stock)...
  ✗ BLOCKED - JSONDecodeError
  Error: Expecting value: line 1 column 1 (char 0)

  This is the classic Yahoo Finance blocking error.

❌ RESULT: Yahoo Finance is BLOCKING you
```

**What this means:**
- Your IP is currently blocked
- Yahoo is returning HTML instead of JSON
- You need to wait before running the screener

**What to do:**

1. **Wait 1-2 hours**
   - Block is temporary
   - Don't make any more yfinance requests during this time

2. **Test again in 1 hour:**
   ```bash
   TEST_YAHOO_BLOCKING.bat
   ```

3. **Once unblocked, run screener:**
   ```bash
   RUN_STOCK_SCREENER.bat
   ```

---

## Why You Got Blocked

Common causes:
- Ran screener multiple times in short period
- Had 4 parallel workers (now fixed to 2)
- No delays between requests (now fixed - 0.5-1s delays)
- Yahoo detected automated scraping pattern

---

## Block Duration

Typical block durations:

| Type | Duration | Cause |
|------|----------|-------|
| **Soft block** | 15-30 min | First offense |
| **Moderate block** | 1-2 hours | Repeated requests |
| **Hard block** | 24 hours | Aggressive scraping (rare) |

Most users experience **moderate blocks (1-2 hours)**.

---

## Testing Schedule

If blocked, test again on this schedule:

```
Blocked at:     10:00 AM
Test again at:  11:00 AM (1 hour later)
If still blocked: 12:00 PM (2 hours later)
If still blocked: 2:00 PM (4 hours later - unusual)
```

---

## Manual Test (No Script)

If you prefer to test manually:

### Python:
```python
import yfinance as yf

# Test 1: Fast info
ticker = yf.Ticker('CBA.AX')
info = ticker.fast_info
print(f"Price: {info.last_price}")

# Test 2: History
hist = ticker.history(period='5d')
print(f"Got {len(hist)} days")
```

### Expected if NOT blocked:
```
Price: 142.35
Got 5 days
```

### Expected if BLOCKED:
```
Error: Expecting value: line 1 column 1 (char 0)
```

---

## Alternative: Check with curl

Test Yahoo Finance API directly:

### Windows PowerShell:
```powershell
$url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=CBA.AX"
$response = Invoke-WebRequest -Uri $url -UseBasicParsing
$response.Content
```

### Expected if NOT blocked:
```json
{"quoteResponse":{"result":[{"symbol":"CBA.AX","regularMarketPrice":142.35,...}]}}
```

### Expected if BLOCKED:
```html
<!DOCTYPE html><html>...
```

---

## After Block Expires

Once the test shows you're unblocked:

1. ✅ **Run the screener immediately**
   ```bash
   RUN_STOCK_SCREENER.bat
   ```

2. ✅ **Don't run it again for 24 hours**
   - Once per day maximum
   - Overnight runs are safest

3. ✅ **Check the fixes are applied**
   - Should see delays between requests in logs
   - Should see "Using cached..." messages
   - Should see lower validation rates initially (cache warming)

---

## Monitoring During Screener Run

Watch the logs for these good signs:

```
✓ Using cached RBA data (age: 0.1 min)
✓ Using cached ^AXJO (age: 15s)
Validation complete: 5 passed
```

**Good indicators:**
- Cache hits
- Reasonable validation rates (60-90%)
- No "Expecting value" errors

**Bad indicators:**
```
Failed to get ticker ... Expecting value: line 1 column 1
Validation complete: 0 passed
```

If you see these during a run, **stop immediately** and wait another hour.

---

## Prevention Tips

To avoid future blocks:

### ✅ DO:
- Run screener **once per day maximum**
- Run during **off-peak hours** (10 PM - 7 AM)
- Test with `TEST_YAHOO_BLOCKING.bat` **before** running screener
- Keep the fixes applied (delays, reduced workers)

### ❌ DON'T:
- Run screener multiple times per day
- Test yfinance manually while screener is running
- Remove delays from code
- Increase workers back to 4+

---

## FAQ

### Q: How often can I run the block test?

**A:** As often as you want - it only makes 4 quick requests. Safe to run every 30 minutes if waiting for unblock.

### Q: Can I speed up the unblock?

**A:** No. Yahoo's block is server-side based on your IP. Only options:
- Wait it out (recommended)
- Change IP (restart router, VPN, mobile hotspot)

### Q: Will VPN help?

**A:** Maybe. If you switch to VPN with different IP, block may be bypassed. But Yahoo may detect VPN and block that IP too.

### Q: Is this normal?

**A:** Yes, very normal with yfinance. Yahoo Finance actively fights automated scraping. The fixes we applied should prevent future blocks.

### Q: What if I'm blocked for 24+ hours?

**A:** Very rare. Usually means:
- Multiple aggressive scraping attempts
- IP previously flagged
- Consider alternative data source (Alpha Vantage Premium, Polygon.io)

---

## Support

If test continues to fail after 4 hours:

1. **Try different network:**
   - Mobile hotspot
   - Different WiFi
   - VPN (use with caution)

2. **Check firewall/antivirus:**
   - May be interfering with requests
   - Temporarily disable and test

3. **Install yahooquery fallback:**
   ```bash
   pip install yahooquery
   ```
   - Provides alternative data source
   - System will automatically use it

4. **Run full diagnostic:**
   ```bash
   DIAGNOSE_YFINANCE.bat
   ```
   - Comprehensive 10-test suite
   - Identifies other potential issues

---

## Summary

**Purpose:** Quick 10-second test to check if Yahoo Finance is blocking your IP

**Usage:** Run `TEST_YAHOO_BLOCKING.bat` before running the stock screener

**Interpretation:**
- ✅ All tests pass → Run screener now
- ❌ Tests fail → Wait 1-2 hours, test again

**Prevention:** The fixes applied (delays, reduced workers, session management) should prevent future blocks

---

**Created:** 2025-11-10  
**Files:** 
- `test_yahoo_blocking.py` (5 KB Python script)
- `TEST_YAHOO_BLOCKING.bat` (2 KB Windows launcher)
- `BLOCK_TEST_GUIDE.md` (This guide)
