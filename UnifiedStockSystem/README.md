# Unified Stock Analysis System - FIXED VERSION

## ✅ Problem Solved

This version fixes the Yahoo Finance 404 errors that were caused by using problematic parameters in the API calls.

### The Fix:
- **BROKEN CODE**: `ticker.history(period='1mo', interval='1d', prepost=False, actions=False)`
- **FIXED CODE**: `ticker.history(period=period)` 
- Removed the `prepost` and `actions` parameters that cause 404 errors on Windows 11

## 🚀 Quick Start (Windows 11)

### Method 1: Simple Start (Recommended)
1. Double-click `START_FIXED.bat`
2. The window will stay open (uses `cmd /k`)
3. Open browser to http://localhost:8000

### Method 2: Full Installation
1. Double-click `INSTALL_AND_RUN_FIXED.bat`
2. Installs all dependencies automatically
3. Starts the server and keeps window open

### Method 3: PowerShell (Alternative)
1. Right-click `RUN_STOCK_ANALYSIS.ps1`
2. Select "Run with PowerShell"
3. If blocked, run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## 📋 Features

### Data Sources
- **Primary**: Yahoo Finance (simplified API calls that work)
- **Fallback**: Alpha Vantage (API key: 68ZFANK047DL0KSR integrated)
- **NO MOCK DATA**: 100% real market data only

### Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- ATR (Average True Range)
- Stochastic Oscillator
- Volume Analysis

### Machine Learning
- RandomForestRegressor with max_depth=5 (prevents overfitting)
- 5-day price predictions
- Feature engineering with technical indicators
- Train/test split validation

### Charting
- Candlestick charts (not line charts)
- Chart.js implementation
- Interactive tooltips
- Volume visualization

### Special Features
- Australian stocks automatic .AX suffix
- Backtesting with MA crossover strategy
- Real-time price updates
- Signal generation (Buy/Sell/Hold)

## 🔧 Manual Installation

If the batch files don't work:

```bash
# 1. Install Python packages
pip install flask flask-cors yfinance pandas numpy scikit-learn plotly requests ta

# 2. Set environment variable (Windows)
set FLASK_SKIP_DOTENV=1

# 3. Run the application
python stock_analysis_unified_fixed.py
```

## 📊 Supported Symbols

### US Stocks
- AAPL, GOOGL, MSFT, AMZN, TSLA, etc.

### Australian Stocks (auto .AX suffix)
- CBA, BHP, CSL, NAB, ANZ, WBC, WES, MQG, TLS, WOW
- RIO, FMG, TCL, ALL, REA, GMG, AMC, SUN, QBE, IAG

## 🎯 API Endpoints

- `GET /` - Main web interface
- `GET /api/stock/<symbol>?period=1mo` - Get stock data
- `POST /api/backtest` - Run backtesting

### Period Options
- 1d - 1 Day
- 5d - 5 Days  
- 1mo - 1 Month (default)
- 3mo - 3 Months
- 6mo - 6 Months
- 1y - 1 Year
- 5y - 5 Years

## ⚠️ Troubleshooting

### Window Closes Immediately
- Use `START_FIXED.bat` which includes `cmd /k` to keep window open
- Or run from PowerShell which naturally stays open

### Port 8000 Already in Use
```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Python Not Found
- Install Python 3.8+ from https://python.org
- Check "Add Python to PATH" during installation
- Restart command prompt after installation

### Package Installation Fails
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install packages one by one
pip install flask
pip install yfinance
pip install pandas
```

### Yahoo Finance Still Failing
- The system will automatically fallback to Alpha Vantage
- Check console for "Using Alpha Vantage" message
- Note: Alpha Vantage has rate limits (5 requests/minute)

## 📝 Version History

### v2.0 - FIXED (Current)
- Fixed Yahoo Finance 404 errors
- Removed problematic API parameters
- Added Alpha Vantage fallback
- Improved Windows 11 compatibility
- Added multiple batch file options

### v1.0 - Initial (Had Issues)
- Used complex Yahoo Finance parameters
- Caused 404 errors on Windows 11
- No fallback data source

## 💡 Tips

1. **For Australian stocks**: Just type "CBA" - the system adds .AX automatically
2. **Check data source**: Look at bottom of chart for "Data Source: Yahoo Finance" or "Alpha Vantage"
3. **ML Predictions**: Need at least 100 data points for training
4. **Best period for analysis**: 1mo or 3mo gives good balance of data

## 🐛 Known Issues & Solutions

1. **Charts not showing**: Clear browser cache (Ctrl+F5)
2. **Predictions missing**: Switch to longer period (1mo or more)
3. **Alpha Vantage rate limit**: Wait 1 minute between requests

## 📞 Support

If issues persist:
1. Check the console output for error messages
2. Verify Python version: `python --version` (need 3.8+)
3. Try manual installation steps
4. Use PowerShell script as alternative to batch files

---

**Last Updated**: October 2024
**Version**: 2.0-FIXED
**Status**: ✅ Working on Windows 11