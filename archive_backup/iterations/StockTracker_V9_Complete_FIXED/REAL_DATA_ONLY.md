# Stock Tracker V9 - REAL DATA ONLY Policy

## ⚠️ CRITICAL REQUIREMENT

**This project MUST use REAL DATA ONLY:**
- ❌ NO mock data
- ❌ NO simulations  
- ❌ NO synthetic data
- ❌ NO fake predictions
- ❌ NO Math.random()
- ✅ ONLY real data from Yahoo Finance
- ✅ ONLY real ML models trained on real data
- ✅ ONLY real predictions from real models

## 🔍 The Real Issue

The ML Backend was crashing because:

1. **Import conflicts** between different versions of the ML backend
2. **SSL certificate errors** on Windows with yfinance
3. **Missing error handling** when Yahoo Finance fails
4. **Attempted fallback to mock data** (which is NOT allowed)

## ✅ The Solution: ml_backend_real.py

Created `ml_backend_real.py` that:
- **Uses ONLY real data** from Yahoo Finance
- **Returns errors** if data can't be fetched (doesn't fake it)
- **Handles SSL issues** properly for Windows
- **Provides clear error messages** when things fail

## 📋 Diagnostic Tools

### diagnose_crash.py
Run this FIRST to see what's actually failing:
```batch
python diagnose_crash.py
```

This will show:
- Which imports are failing
- Whether FastAPI can start
- Whether yfinance can fetch real data
- The exact error messages

## 🚀 How to Run (REAL DATA ONLY)

### Method 1: With Diagnostics
```batch
START_REAL.bat
```
This will:
1. Run diagnostics first
2. Show you any issues
3. Ask if you want to continue
4. Start with REAL data only

### Method 2: Direct Start
```batch
venv\Scripts\activate.bat
set REQUESTS_CA_BUNDLE=
python ml_backend_real.py
```

## ⚙️ How It Works

### Data Fetching
```python
def fetch_real_stock_data(symbol: str, days: int = 365):
    # Tries to fetch REAL data
    df = yf.download(symbol, start=start_date, end=end_date)
    
    if df.empty:
        # Raises ERROR - doesn't return fake data
        raise ValueError(f"No real data for {symbol}")
```

### Training
- Fetches REAL historical data
- Creates REAL technical indicators
- Trains REAL RandomForest model
- Returns REAL accuracy metrics

### Prediction
- Uses REAL current price
- Applies REAL trained model
- Returns REAL prediction
- NO synthetic data ever

## 🛑 What Happens When Data Fails

If Yahoo Finance can't fetch data:
```json
{
    "status_code": 400,
    "detail": "Cannot fetch real data for XYZ. Error: No data found. Please check the symbol and try again."
}
```

**IT DOES NOT RETURN FAKE DATA**

## 📊 Feature Set (REAL)

The system uses these REAL features calculated from REAL data:
- Price returns (daily % change)
- Log returns (logarithmic returns)
- Moving averages (5, 20, 50 day)
- High/Low ratio
- Close/Open ratio
- Volume ratio (current vs average)
- Volatility (20-day rolling std)
- RSI (Relative Strength Index)

All calculated from REAL market data.

## 🔧 Troubleshooting

### "Cannot fetch real data"
- Check internet connection
- Verify the stock symbol exists
- Try a known symbol like AAPL or MSFT
- Check if Yahoo Finance is accessible

### "Training failed"
- Not enough historical data (needs 100+ days)
- Invalid symbol
- Network issues

### Server crashes on startup
1. Run `diagnose_crash.py`
2. Check which component fails
3. Fix that specific issue
4. Try again with `START_REAL.bat`

## 💡 Important Notes

1. **Training takes time** - 5-30 seconds with REAL data
2. **Not all symbols work** - Only valid stock symbols
3. **Internet required** - Can't work offline (no fake data)
4. **Markets closed** - Data might be delayed on weekends

## 🎯 Testing with REAL Symbols

### US Stocks (work best)
- AAPL - Apple
- MSFT - Microsoft  
- GOOGL - Google
- AMZN - Amazon

### Australian Stocks (use .AX suffix)
- CBA.AX - Commonwealth Bank
- BHP.AX - BHP Group
- WBC.AX - Westpac

### Indices
- ^GSPC - S&P 500
- ^DJI - Dow Jones
- ^IXIC - NASDAQ

## ❌ What NOT to Do

Never modify the code to:
- Add mock data as fallback
- Generate synthetic prices
- Use random predictions
- Simulate training
- Fake success responses

**If real data fails, the system should fail with a clear error message.**

---

**Remember: REAL DATA ONLY - No exceptions!**