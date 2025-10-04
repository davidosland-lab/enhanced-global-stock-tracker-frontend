# 📊 Stock Market Dashboard - Clean Installation v6.0

## ✨ What's Included
A complete, working stock market analysis dashboard with:
- **Real Yahoo Finance data** (no synthetic/mock data)
- **High-frequency trading data** (1-minute intervals)
- **Multiple analysis modules** (Technical, Market Tracking, CBA, Predictions)
- **Windows 11 optimized** (localhost:8002 hardcoded)
- **All known issues fixed**

## 📁 Directory Structure
```
StockTracker/
│
├── backend.py              # Yahoo Finance API backend server
├── start_backend.bat       # One-click backend starter
├── requirements.txt        # Python dependencies
├── index.html             # Main dashboard
├── diagnostic_tool.html   # System diagnostics
├── verify_setup.html      # Setup verification tool
│
└── modules/
    ├── technical_analysis_enhanced_v5.3.html    # Technical analysis with 1-min data
    ├── technical_analysis_desktop_fixed.html    # Desktop charts (4 libraries)
    ├── analysis/
    │   └── cba_analysis_enhanced_fixed.html    # CBA.AX analysis
    ├── market-tracking/
    │   └── market_tracker_final.html           # Global market tracker
    └── predictions/
        └── prediction_centre_advanced.html      # ML predictions

```

## 🚀 Installation Steps

### Prerequisites
1. **Python 3.7+** installed ([Download Python](https://www.python.org/downloads/))
2. **Modern browser** (Chrome, Edge, Firefox)
3. **Windows 11** (optimized for, but works on Windows 10)

### Step 1: Extract Files
1. Create a folder: `C:\StockTracker` (or your preferred location)
2. Extract all files from this package to that folder
3. Ensure the folder structure matches above

### Step 2: Install Python Dependencies

#### Option A: Automatic (Recommended)
1. Double-click `start_backend.bat`
2. It will auto-install all required packages
3. Skip to Step 3 if successful

#### Option B: Manual Installation
1. Open Command Prompt as Administrator
2. Navigate to your installation folder:
   ```
   cd C:\StockTracker
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Step 3: Start the Backend Server
1. **Double-click** `start_backend.bat`
2. Wait for message: `Uvicorn running on http://0.0.0.0:8002`
3. **Keep this window open** (minimize it)

### Step 4: Open the Dashboard
1. Open your browser
2. Navigate to: `http://localhost:8002`
3. Or open `index.html` directly

### Step 5: Verify Installation
1. Open `verify_setup.html` in your browser
2. All tests should show "✓ Success"
3. Live data should display current stock prices

## 📱 Module Descriptions

### 1. Technical Analysis Enhanced (v5.3)
- **Real-time candlestick charts** with 1-minute data
- **Technical indicators**: MA, EMA, RSI, MACD, Bollinger Bands
- **Multiple timeframes**: 1m, 5m, 15m, 30m, 1h, 1d
- **Auto-refresh** every 30 seconds

### 2. Technical Analysis Desktop
- **4 Chart Libraries**: TradingView, ApexCharts, Chart.js, Plotly
- **Side-by-side comparison** views
- **Desktop optimized** layout
- All libraries fully functional

### 3. Market Tracker Final
- **Global markets**: ASX, FTSE, S&P 500
- **Real-time updates** with market hours
- **Timezone aware** (AEST display)
- **Performance charts** for each market

### 4. CBA Analysis
- **Commonwealth Bank** (CBA.AX) focused analysis
- **Historical data** and trends
- **Volume analysis**
- **Price predictions**

### 5. Prediction Centre
- **ML-based predictions**
- **Backtesting capabilities**
- **Performance metrics**
- **Learning algorithms**

## 🔧 Troubleshooting

### "Failed to fetch" Error
1. **Check backend is running** (Python window should be open)
2. **Clear browser cache**: Ctrl+Shift+Delete → Clear cached files
3. **Hard refresh**: Ctrl+F5 on the page

### Backend Won't Start
1. **Check Python installation**: Open CMD and type `python --version`
2. **Install missing packages**: `pip install -r requirements.txt`
3. **Run as Administrator**: Right-click start_backend.bat → Run as administrator

### Port 8002 Already in Use
1. **Find the process**: Open CMD as admin
   ```
   netstat -ano | findstr :8002
   ```
2. **Kill the process**: Note the PID and run
   ```
   taskkill /PID [PID_NUMBER] /F
   ```

### Module Not Loading
1. **Check file paths**: Ensure all files are in correct folders
2. **Use Chrome/Edge**: Some features work better in Chromium browsers
3. **Disable ad blockers**: May interfere with API calls

## 🛡️ Security Notes
- Backend runs locally only (localhost)
- No external server dependencies
- Your data stays on your machine
- API calls go directly to Yahoo Finance

## 📊 Data Sources
- **Yahoo Finance API**: All market data
- **Real-time quotes**: During market hours
- **Historical data**: Up to 2 years
- **No synthetic data**: 100% real market data

## 🎯 Quick Test
After installation, test with these symbols:
- **US Stocks**: AAPL, GOOGL, MSFT, TSLA
- **ASX Stocks**: CBA.AX, BHP.AX, CSL.AX
- **Crypto**: BTC-USD, ETH-USD
- **Forex**: AUDUSD=X, EURUSD=X

## 📝 Important Notes
1. **Keep backend running**: Don't close the Python window
2. **Internet required**: For Yahoo Finance data
3. **Market hours**: Some features limited outside trading hours
4. **Browser cache**: Clear if experiencing issues

## 🚦 System Status Check
Open `diagnostic_tool.html` to verify:
- ✅ Backend API connectivity
- ✅ Yahoo Finance data access
- ✅ All endpoints responding
- ✅ Real-time data flow

## 📞 Support
If issues persist after following this guide:
1. Run `verify_setup.html` and note any failures
2. Check `diagnostic_tool.html` for specific errors
3. Ensure all files are in correct locations
4. Try a different browser or incognito mode

---
**Version**: 6.0 Clean Install
**Date**: October 2024
**Status**: Production Ready - All Issues Fixed