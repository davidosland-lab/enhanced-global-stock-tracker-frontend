# Swing API Hotfix

## 🔴 Error Fixed

```
HistoricalDataLoader.__init__() missing 3 required positional arguments: 
'symbol', 'start_date', and 'end_date'
```

## 🚀 Quick Fix (30 Seconds)

### Step 1: Extract Hotfix
Extract `swing_api_hotfix.zip` to any location

### Step 2: Run Hotfix
```batch
cd swing_api_hotfix
APPLY_HOTFIX.bat
```

### Step 3: Enter Path
```
C:\Users\david\AATelS
```

### Step 4: Restart Server
```batch
cd C:\Users\david\AATelS
python finbert_v4.4.4\app_finbert_v4_dev.py
```

### Step 5: Test Swing Trading
Click the rose/pink "Swing Trading" button and run a backtest!

## ✅ What It Fixes

### Before (BROKEN)
```python
# Line 1666 - Missing required arguments
data_loader = HistoricalDataLoader()
price_data = data_loader.load_price_data(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date,
    interval='1d'
)
```
❌ **Error**: Missing 3 required arguments

### After (FIXED)
```python
# Lines 1666-1672 - Correct initialization
data_loader = HistoricalDataLoader(
    symbol=symbol,
    start_date=start_date,
    end_date=end_date
)
price_data = data_loader.load_price_data(interval='1d')
```
✅ **Works**: Swing backtest runs successfully!

## 🔒 Safety

- **Automatic backup** created before applying fix
- **Backup location**: `app_finbert_v4_dev.py.backup.YYYYMMDD_HHMMSS`
- **Easy rollback**: Just copy backup file back

## 📦 Package Contents

```
swing_api_hotfix/
├── fixes/
│   └── fix_swing_endpoint.py    # Python fix script
├── APPLY_HOTFIX.bat              # Windows installer
└── README.md                     # This file
```

## 🆘 Manual Fix (If Script Fails)

If the automated fix doesn't work, edit manually:

1. Open: `C:\Users\david\AATelS\finbert_v4.4.4\app_finbert_v4_dev.py`
2. Find line ~1666:
   ```python
   data_loader = HistoricalDataLoader()
   ```
3. Replace with:
   ```python
   data_loader = HistoricalDataLoader(
       symbol=symbol,
       start_date=start_date,
       end_date=end_date
   )
   ```
4. Find the next line:
   ```python
   price_data = data_loader.load_price_data(
       symbol=symbol,
       start_date=start_date,
       end_date=end_date,
       interval='1d'
   )
   ```
5. Replace with:
   ```python
   price_data = data_loader.load_price_data(interval='1d')
   ```
6. Save file
7. Restart server

## ✅ Verification

After applying the hotfix and restarting:

1. Open browser: `http://localhost:5001`
2. Click "Swing Trading" button (rose/pink)
3. Configure: AAPL, dates 2024-01-01 to 2024-11-01
4. Click "Run Swing Trading Backtest"
5. Wait 1-2 minutes
6. **Expected**: Results displayed with metrics, charts, trade history
7. **No error**: "HistoricalDataLoader" error is gone!

## 📊 Summary

| Item | Value |
|------|-------|
| **Install Time** | 30 seconds |
| **Files Modified** | 1 (app_finbert_v4_dev.py) |
| **Lines Changed** | ~8 lines |
| **Backup** | Automatic |
| **Rollback** | Easy |
| **Server Restart** | Required |

---

**🎉 This hotfix resolves the Swing Trading API error. Apply it, restart your server, and the swing backtest will work!**
