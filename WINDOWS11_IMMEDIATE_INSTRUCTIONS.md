# 🚀 GET RUNNING IN 2 MINUTES - Windows 11

## Your Current Situation:
You're in `C:\StockTrack` with Python 3.12.9 installed but no project files.

## IMMEDIATE SOLUTION - Copy & Run This:

### Step 1: Create the Complete Setup File

1. Open Notepad
2. Copy ALL the content from the `COMPLETE_WINDOWS_SETUP.py` file (the long Python script above)
3. Save it as `COMPLETE_WINDOWS_SETUP.py` in `C:\StockTrack`

### Step 2: Run It

In your PowerShell window (still in C:\StockTrack), run:

```powershell
python COMPLETE_WINDOWS_SETUP.py
```

That's it! The script will:
- ✅ Install all required packages automatically
- ✅ Create the web interface
- ✅ Start both backend servers
- ✅ Open your browser to http://localhost:8002

## What This Complete Setup Includes:

1. **Automatic Package Installation** - No need for requirements.txt
2. **Main Backend Server** (Port 8002) with:
   - Real Yahoo Finance data
   - Stock search
   - Market indices tracking
   - Historical data
   
3. **ML Backend Server** (Port 8004) with:
   - 8 ML models
   - Prediction endpoints
   - Model status

4. **Web Dashboard** with:
   - Stock search interface
   - Live market indices
   - Popular stocks display
   - ML model status

## Alternative: Super Quick Test

If you want to test even faster, just run these commands directly in PowerShell:

```powershell
# Install minimal packages
pip install --user flask flask-cors yfinance

# Create and run a test server
python -c "
from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return '<h1>Stock Tracker Running!</h1><p>Test: <a href=\"/api/stock/AAPL\">/api/stock/AAPL</a></p>'

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return jsonify({'symbol': symbol, 'price': info.get('regularMarketPrice', 'N/A'), 'name': info.get('longName', 'N/A')})

print('Server running on http://localhost:8002')
app.run(host='0.0.0.0', port=8002)
"
```

## If You Get Any Errors:

### "Module not found" error:
```powershell
pip install --user flask flask-cors yfinance pandas numpy
```

### "Permission denied" error:
```powershell
python -m pip install --user flask flask-cors yfinance
```

### "Port already in use" error:
```powershell
# Find and kill the process
Get-Process -Name python | Stop-Process -Force
```

## What You'll See:

Once running, you'll see:
- Console output showing servers starting
- Browser opens automatically
- Dashboard with:
  - Stock search box
  - Market indices (S&P 500, Dow Jones, NASDAQ, FTSE, ASX)
  - Popular stocks (AAPL, MSFT, GOOGL, AMZN)
  - ML model status

## Files Created:

Just ONE file needed: `COMPLETE_WINDOWS_SETUP.py`

This single file:
- Installs dependencies
- Creates the entire application
- Runs both servers
- Serves the web interface

## Success Indicators:

✅ You'll see: "Yahoo Finance connection successful!"
✅ Browser opens to http://localhost:8002
✅ Stock search returns real prices
✅ Market indices show live data

---

**SUMMARY: Just save the COMPLETE_WINDOWS_SETUP.py file and run it with Python. Everything else is automatic!**