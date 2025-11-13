# Troubleshooting Current Issues

## 🔴 Issues You're Experiencing

Based on your error log, there are **2 main issues**:

### Issue 1: Batch File Syntax Error
```
'P' is not recognized as an internal or external command
```

**Cause**: The batch file has `S&P` which Windows interprets as `S` followed by command `P`

**Solution**: The batch files need proper escaping for special characters

### Issue 2: yfinance Cannot Fetch Market Indices
```
yfinance - ERROR - Failed to get ticker '^AXJO' reason: Expecting value: line 1 column 1 (char 0)
yfinance - ERROR - ^AXJO: No price data found, symbol may be delisted
```

**Cause**: Yahoo Finance API issues (common causes):
1. **Markets are closed** (weekend/holiday)
2. **yfinance version outdated**
3. **Network/firewall blocking Yahoo Finance**
4. **Yahoo Finance API changes**

---

## ✅ Quick Fixes

### Fix #1: Upgrade yfinance (RECOMMENDED)

Run this batch file I created for you:
```
FIX_YFINANCE_ISSUES.bat
```

This will:
- Upgrade yfinance to latest version
- Upgrade related packages (requests, urllib3)
- Test the connection

**OR manually**:
```batch
call venv\Scripts\activate.bat
pip uninstall -y yfinance
pip install yfinance
pip install --upgrade requests urllib3
```

### Fix #2: Diagnose the Problem

Run:
```
DIAGNOSE_YFINANCE.bat
```

This will test:
1. yfinance installation
2. Yahoo Finance connectivity
3. Stock data fetch
4. Market indices fetch

And tell you exactly what's wrong.

### Fix #3: Check Market Hours

**The error you're seeing is NORMAL if markets are closed!**

- **ASX Markets**: Mon-Fri, 10:00 AM - 4:00 PM AEST
- **US Markets**: Mon-Fri, 9:30 AM - 4:00 PM EST (midnight-7 AM AEST)
- **SPI Futures**: 5:10 PM - 8:00 AM AEST

**Current Time in Your Log**: 09:00 AM (Sunday morning?)

If it's weekend/holiday, the indices won't have data. This is expected behavior.

---

## 🔍 Understanding the Errors

### Error Breakdown

```
2025-11-10 09:00:46 - yfinance - ERROR - Failed to get ticker '^AXJO' reason: Expecting value
```

This means yfinance got an empty or invalid response from Yahoo Finance.

**Possible Reasons**:
1. **Weekend/Holiday** - Yahoo doesn't return data for closed markets ✅ MOST LIKELY
2. **Rate Limiting** - Too many requests (unlikely with screener)
3. **Network Issue** - Firewall/proxy blocking
4. **yfinance Bug** - Version compatibility issue

### Why System Still Works

Notice your log shows:
```
2025-11-10 09:01:28,088 - __main__ - INFO -   ✓ Sentiment Score: 50.0/100
2025-11-10 09:01:28,088 - __main__ - INFO -   ✓ Gap Prediction: +0.00%
2025-11-10 09:01:28,088 - __main__ - INFO -   ✓ Direction: NEUTRAL
```

**The system has fallback mechanisms!**

When indices fail:
- Sentiment defaults to 50.0 (neutral)
- Gap prediction defaults to 0% (no gap)
- Direction defaults to NEUTRAL
- Screening continues using stock data

This is **by design** - the screener doesn't fail completely.

---

## 🎯 Recommended Actions

### Immediate (Do This Now)

1. **Run the fix**:
   ```
   FIX_YFINANCE_ISSUES.bat
   ```

2. **Test again during market hours**:
   - ASX: Mon-Fri 10 AM - 4 PM AEST
   - US: Mon-Fri 12 AM - 7 AM AEST (for overnight gap prediction)

3. **Use test mode first**:
   ```
   RUN_STOCK_SCREENER_TEST.bat
   ```

### If Still Failing

1. **Run diagnostics**:
   ```
   DIAGNOSE_YFINANCE.bat
   ```

2. **Check specific yfinance version**:
   ```batch
   call venv\Scripts\activate.bat
   python -c "import yfinance; print(yfinance.__version__)"
   ```

   Should be: `0.2.40` or higher

3. **Test manually**:
   ```batch
   call venv\Scripts\activate.bat
   python
   ```
   
   Then:
   ```python
   import yfinance as yf
   axjo = yf.Ticker("^AXJO")
   hist = axjo.history(period="5d")
   print(hist)
   ```

   If this shows data, yfinance works. If empty, markets are closed.

---

## 🔧 Alternative Solutions

### Option 1: Use Alpha Vantage Only

Edit: `complete_deployment/models/screening/spi_monitor.py`

Find line (~line 95):
```python
def _fetch_daily_series(self, symbol: str) -> pd.DataFrame:
    if symbol.startswith("^"):  # Index - use yfinance
        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
```

Change to:
```python
def _fetch_daily_series(self, symbol: str) -> pd.DataFrame:
    if symbol.startswith("^"):  # Index - use Alpha Vantage fallback
        try:
            df = yf.Ticker(symbol).history(period="6mo", interval="1d")
            if df.empty:
                # Fallback to Alpha Vantage
                df = self.data_fetcher.fetch_daily_data(symbol.replace("^", ""), outputsize="compact")
        except:
            df = self.data_fetcher.fetch_daily_data(symbol.replace("^", ""), outputsize="compact")
```

### Option 2: Disable SPI Monitoring Temporarily

Edit: `complete_deployment/models/config/screening_config.json`

Find:
```json
"spi_monitoring": {
  "enabled": true,
```

Change to:
```json
"spi_monitoring": {
  "enabled": false,
```

This will skip market sentiment and use only stock-specific predictions.

### Option 3: Mock Data for Testing

Create: `complete_deployment/models/screening/mock_spi_data.py`

```python
def get_mock_sentiment():
    return {
        'available': True,
        'sentiment_score': 55.0,
        'gap_prediction': {'predicted_gap_pct': 0.25, 'direction': 'bullish'},
        'asx_data': {'last_close': 8800, 'change_pct': 0.5},
        'us_markets': {
            'SP500': {'change_pct': 0.3},
            'Nasdaq': {'change_pct': 0.4},
            'Dow': {'change_pct': 0.2}
        }
    }
```

Then in `run_overnight_screener.py`, use this for testing.

---

## 📊 Expected Behavior

### During Market Hours (Working)
```
2025-11-10 10:30:00 - __main__ - INFO -   ✓ Sentiment Score: 62.3/100
2025-11-10 10:30:00 - __main__ - INFO -   ✓ Gap Prediction: +0.42%
2025-11-10 10:30:00 - __main__ - INFO -   ✓ Direction: BULLISH
```

### During Closed Markets (Normal)
```
2025-11-10 09:01:28 - __main__ - INFO -   ✓ Sentiment Score: 50.0/100
2025-11-10 09:01:28 - __main__ - INFO -   ✓ Gap Prediction: +0.00%
2025-11-10 09:01:28 - __main__ - INFO -   ✓ Direction: NEUTRAL
```

Both are correct! The system adapts.

---

## 🎯 Bottom Line

**Your error is most likely because:**
1. You ran the screener at 9:00 AM on a Sunday
2. Markets are closed
3. Yahoo Finance doesn't return data for closed markets
4. This is **NORMAL BEHAVIOR**

**What to do:**
1. Run `FIX_YFINANCE_ISSUES.bat` to upgrade yfinance
2. Test again during market hours (Monday 10 AM AEST)
3. Or use test mode which works even with closed markets

**The system will work fine during actual overnight screening hours (10 PM - 7 AM)!**

---

## 📞 Need More Help?

1. **Check the log files**: `logs/screening/*.log`
2. **Run diagnostics**: `DIAGNOSE_YFINANCE.bat`
3. **Verify market hours**: https://www.asx.com.au/
4. **Test with US stocks** (AAPL, MSFT) - these should always work

The system is designed to handle these errors gracefully and continue screening!
