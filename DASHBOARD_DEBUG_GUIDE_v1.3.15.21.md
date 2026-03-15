# 🔍 Dashboard Debugging Guide - v1.3.15.21

**Version:** v1.3.15.21  
**Date:** January 17, 2026  
**Status:** Enhanced Error Handling + Debugging Tools  
**Package:** complete_backend_clean_install_v1.3.15.10_FINAL.zip (860 KB)

---

## 🚨 Current Status

The dashboard is **loading** but showing HTTP 500 errors in console. These errors are now **caught and logged** instead of crashing the dashboard.

### ✅ What's Fixed:
- Market calendar API (Exchange enum support)
- News fetching (method validation)
- Tax audit trail (record_transaction method)
- **NEW:** Comprehensive error handling in dashboard callbacks
- **NEW:** Detailed debug logging

### 🔧 What Needs Investigation:
- HTTP 500 errors in dashboard update cycle
- Specific component causing the failure

---

## 📋 Step-by-Step Debugging

### Step 1: Check the Logs

The dashboard now logs **every step** of the update cycle. Check the log file:

```bash
# Windows
type logs\unified_trading.log | findstr "DASHBOARD"

# Linux/Mac
grep "DASHBOARD" logs/unified_trading.log | tail -20
```

**Look for:**
```
[DASHBOARD] Update cycle X starting...
[DASHBOARD] State loaded successfully
[DASHBOARD] Creating market status panel...
[DASHBOARD] Market status panel created
[DASHBOARD] Creating ML signals panel...
[DASHBOARD] ML signals panel created
[DASHBOARD] Creating market performance chart...
[DASHBOARD] Market performance chart created
```

**If you see an error at any step, that's where it's failing!**

---

### Step 2: Identify the Failing Component

The logs will show exactly which component fails:

#### Example 1: Market Status Panel Fails
```
[DASHBOARD] Creating market status panel...
Error creating market status panel: [error message]
```

**Fix:** Check `ml_pipeline/market_calendar.py`

#### Example 2: ML Signals Panel Fails
```
[DASHBOARD] Creating ML signals panel...
Error creating ML signals panel: [error message]
```

**Fix:** Check ML signal generation logic

#### Example 3: Market Performance Chart Fails
```
[DASHBOARD] Creating market performance chart...
Error creating market performance chart: [error message]
```

**Fix:** Check data fetching for price history

---

### Step 3: Run with Debug Logging

Enable **verbose logging** to see everything:

**Edit:** `unified_trading_dashboard.py`

Find line 48:
```python
logging.basicConfig(
    level=logging.INFO,
```

Change to:
```python
logging.basicConfig(
    level=logging.DEBUG,
```

**Restart dashboard** and check logs again.

---

### Step 4: Test Individual Components

Test each component in isolation:

#### Test Market Calendar:
```python
python -c "
from ml_pipeline.market_calendar import MarketCalendar, Exchange
mc = MarketCalendar()
info = mc.get_market_status(Exchange.ASX)
print(f'Status: {info.status}')
print(f'Exchange: {info.exchange}')
print(f'Time: {info.current_time}')
print('SUCCESS!')
"
```

Expected output:
```
Status: MarketStatus.WEEKEND
Exchange: Exchange.ASX
Time: 2026-01-17 [time]
SUCCESS!
```

#### Test News Fetching:
```python
python -c "
from yahooquery import Ticker
ticker = Ticker('CBA.AX')
news = ticker.news if callable(ticker.news) == False else None
print(f'News available: {news is not None}')
if news and hasattr(news, '__len__'):
    print(f'News count: {len(news)}')
print('SUCCESS!')
"
```

#### Test Tax Audit Trail:
```python
python -c "
from ml_pipeline.tax_audit_trail import TaxAuditTrail
from datetime import datetime
tax = TaxAuditTrail()
tax.record_transaction('BUY', 'CBA.AX', 100, 105.50, datetime.now())
print('SUCCESS!')
"
```

---

## 🔧 Common Issues & Fixes

### Issue 1: Dashboard Shows Blank Charts

**Symptom:** Charts load but show no data

**Debug:**
```python
# Check if state file exists
import json
from pathlib import Path

state_file = Path('state/trading_state.json')
if state_file.exists():
    with open(state_file) as f:
        state = json.load(f)
    print(f"Symbols: {state.get('symbols', [])}")
    print(f"Capital: {state.get('capital', {})}")
else:
    print("State file missing!")
```

**Fix:** Click "Start Trading" button to initialize state

---

### Issue 2: Market Status Shows "Unavailable"

**Symptom:** Market status panel empty or shows error

**Possible Causes:**
1. Market calendar import failed
2. Timezone configuration issue
3. Exchange enum error

**Debug:**
```python
python -c "
try:
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
    print('✅ Market calendar imported')
    
    mc = MarketCalendar()
    print('✅ Calendar initialized')
    
    info = mc.get_market_status(Exchange.NYSE)
    print(f'✅ Status retrieved: {info.status}')
    print(f'   Exchange: {info.exchange.value}')
    print(f'   Time: {info.current_time}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

---

### Issue 3: ML Signals Not Generating

**Symptom:** ML signals panel shows "Loading..." forever

**Possible Causes:**
1. Paper trading coordinator not running
2. ML models not loaded
3. Data fetch failing

**Debug:**
1. Check if paper trading started:
   ```bash
   # Check logs
   type logs\paper_trading.log | findstr "ML"
   ```

2. Test ML signal generation:
   ```python
   python -c "
   from paper_trading_coordinator import PaperTradingCoordinator
   coord = PaperTradingCoordinator(['CBA.AX'], 100000)
   signal = coord.generate_ml_signal('CBA.AX')
   print(f'Signal: {signal}')
   "
   ```

---

### Issue 4: HTTP 500 Errors Persist

**Symptom:** Console shows INTERNAL_SERVER_ERROR

**What's Happening:**
- Dashboard callbacks are failing
- Now caught and logged (won't crash dashboard)
- Check logs to see exact error

**Debug Steps:**

1. **Stop Dashboard:**
   ```
   Ctrl+C in terminal
   ```

2. **Check Last Error:**
   ```bash
   # Windows
   type logs\unified_trading.log | findstr "ERROR" | more

   # Linux/Mac  
   grep "ERROR" logs/unified_trading.log | tail -10
   ```

3. **Fix Component:**
   - See error message in logs
   - Fix corresponding file
   - Restart dashboard

4. **Restart Dashboard:**
   ```bash
   LAUNCH_COMPLETE_SYSTEM.bat → Option 7
   ```

---

## 📊 Expected Log Output (Healthy Dashboard)

```
[DASHBOARD] Update cycle 1 starting...
[DASHBOARD] State loaded successfully
[DASHBOARD] Creating market status panel...
[DASHBOARD] Market status panel created
[DASHBOARD] Creating ML signals panel...
[DASHBOARD] ML signals panel created
[DASHBOARD] Creating market performance chart...
[DASHBOARD] Market performance chart created
[DASHBOARD] Update cycle 1 complete
```

**If you see this pattern repeating every 5 seconds, the dashboard is healthy!**

---

## 🐛 Reporting Issues

When reporting issues, include:

1. **Log Excerpt:**
   ```
   Copy last 50 lines from logs/unified_trading.log
   ```

2. **Browser Console:**
   ```
   F12 → Console tab → Copy errors
   ```

3. **Steps to Reproduce:**
   ```
   1. Started dashboard
   2. Selected ASX Blue Chips
   3. Clicked Start Trading
   4. Error appeared after X minutes
   ```

4. **Environment:**
   ```
   - Python version: python --version
   - Operating System: Windows/Linux/Mac
   - Package version: v1.3.15.21
   ```

---

## ✅ Verification Checklist

After applying fixes:

- [ ] Dashboard loads without crashing
- [ ] No HTTP 500 errors in console
- [ ] Market status panel shows exchange info
- [ ] Stock selection dropdown works
- [ ] Start Trading button functions
- [ ] Charts populate with data
- [ ] Real-time updates every 5 seconds
- [ ] Positions list appears
- [ ] P&L tracking works

---

## 🚀 Next Steps

1. **Extract updated package** (860 KB)
2. **Replace existing files**
3. **Restart dashboard**
4. **Monitor logs** for 5 minutes
5. **Identify failing component** from logs
6. **Apply specific fix** based on error
7. **Test again**

---

## 📞 Quick Reference

### Important Files:
- **Dashboard:** `unified_trading_dashboard.py`
- **Market Calendar:** `ml_pipeline/market_calendar.py`
- **Paper Trading:** `paper_trading_coordinator.py`
- **Tax Trail:** `ml_pipeline/tax_audit_trail.py`

### Important Logs:
- **Dashboard:** `logs/unified_trading.log`
- **Paper Trading:** `logs/paper_trading.log`

### Key Commands:
```bash
# View dashboard logs
type logs\unified_trading.log

# Test market calendar
python -c "from ml_pipeline.market_calendar import MarketCalendar, Exchange; mc = MarketCalendar(); print(mc.get_market_status(Exchange.ASX))"

# Check Python environment
CHECK_PYTHON_ENV.bat

# Start dashboard
LAUNCH_COMPLETE_SYSTEM.bat → Option 7
```

---

**Remember:** The dashboard now **handles errors gracefully** instead of crashing. Use the logs to identify the exact issue!

---

*Last Updated: January 17, 2026*  
*Package Version: v1.3.15.21*  
*Status: Ready for Debugging 🔍*
