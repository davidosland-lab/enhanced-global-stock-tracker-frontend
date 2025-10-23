# Stock Tracker Pro v8.0 - Clean Install

## 🚀 Quick Start

### One-Click Installation and Launch:

1. **Extract this folder** to any location (e.g., `C:\StockTracker`)
2. **Double-click `START.bat`**
3. **That's it!** The browser will open automatically

The START.bat file will:
- ✅ Check Python installation
- ✅ Install all required packages
- ✅ Start the backend server
- ✅ Open the dashboard in your browser

## 📋 What's Included

### Core Files
- **START.bat** - One-click launcher
- **backend.py** - Complete backend server (unified)
- **index.html** - Main dashboard
- **README.md** - This file

### Features
- Real Yahoo Finance data integration
- Stock search with real-time prices
- Market indices tracking (S&P 500, NASDAQ, DOW, ASX)
- ML predictions for any stock
- Clean, modern UI
- No configuration needed

## 🛠️ System Requirements

- **Windows 11** (also works on Windows 10)
- **Python 3.8+** installed
- **Internet connection** for market data
- **4GB RAM** minimum
- **Modern web browser** (Chrome, Edge, Firefox)

## 📊 API Endpoints

Once running, these endpoints are available:

- `http://localhost:8002/` - Main dashboard
- `http://localhost:8002/api/status` - API status
- `http://localhost:8002/api/stock/AAPL` - Get stock data
- `http://localhost:8002/api/predict/CBA.AX` - Get predictions
- `http://localhost:8002/api/indices` - Market indices
- `http://localhost:8002/api/historical/AAPL?period=1mo` - Historical data

## 🔧 Troubleshooting

### Python Not Found
If you get "Python is not installed":
1. Download Python from https://python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart your computer
4. Try again

### Port Already in Use
If port 8002 is busy:
1. Close any other Python applications
2. Or edit backend.py and change port 8002 to another number (e.g., 8080)

### Packages Won't Install
Try manual installation:
```cmd
pip install --user flask flask-cors yfinance pandas numpy cachetools
```

### Browser Doesn't Open
Manually open: http://localhost:8002

## 📈 Using the Application

### Quick Stock Search
1. Enter any stock symbol (e.g., AAPL, MSFT, CBA.AX)
2. Click Search or press Enter
3. View real-time price and details

### Market Overview
The dashboard shows live updates for:
- S&P 500
- NASDAQ
- DOW Jones
- ASX All Ordinaries

### Available Modules
Click any module card to access:
- Technical Analysis
- ML Predictions
- Market Tracker
- Portfolio Analysis
- Backtesting
- API Dashboard

## 🔍 Verified Features

### ✅ Real Data
- All stock prices from Yahoo Finance
- No hardcoded or synthetic data
- Real-time market updates

### ✅ CBA.AX Fix
- Shows real price (~$170)
- Not the buggy $100.10
- Proper ML predictions

### ✅ Clean Architecture
- Single backend file
- No complex configuration
- Works out of the box

## 💡 Tips

### Performance
- Data is cached for 5 minutes to reduce API calls
- Refresh the page to get latest data
- Best performance with Chrome or Edge

### Symbols
- US Stocks: AAPL, MSFT, GOOGL, AMZN
- Australian: CBA.AX, BHP.AX, WBC.AX
- Indices: ^GSPC, ^IXIC, ^DJI, ^FTSE

## 📝 Version History

### v8.0 (Current)
- Completely rebuilt from scratch
- Single unified backend
- One-click installation
- Fixed all CBA.AX pricing issues
- Clean, minimal codebase

### Previous Issues (All Fixed)
- ❌ Hardcoded $100 prices → ✅ Real Yahoo Finance data
- ❌ Complex multi-file setup → ✅ Single backend file
- ❌ Manual dependency installation → ✅ Automatic in START.bat
- ❌ Configuration needed → ✅ Works immediately

## 🤝 Support

### Getting Help
1. Check the Troubleshooting section above
2. Verify Python is installed: `python --version`
3. Check backend is running: Look for the command window
4. Test API: Open http://localhost:8002/api/status

### Known Working On
- Windows 11 (all versions)
- Windows 10 (1909 and later)
- Python 3.8, 3.9, 3.10, 3.11, 3.12

## 📄 License

Free to use for personal and educational purposes.

---

**Enjoy Stock Tracker Pro v8.0!** 🚀

*Clean, Simple, Working*