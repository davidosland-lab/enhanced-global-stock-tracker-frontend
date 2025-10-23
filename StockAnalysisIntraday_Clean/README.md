# Stock Analysis System with Intraday Support - CHARTS FIXED

## 🚀 Quick Start

### Windows Users:
1. **First Time**: Double-click `QUICK_START.bat`
2. **Regular Use**: Double-click `START.bat`
3. Open your browser to: **http://localhost:5000**

### Manual Installation:
```bash
# Install Python 3.8+ from python.org first, then:
pip install -r requirements.txt
python app.py
```

## 🔧 CHART FIXES APPLIED
- ✅ Fixed JavaScript TypeError with Chart.js
- ✅ Reverted to stable Chart.js configuration
- ✅ Added line chart option alongside candlesticks
- ✅ Chart type selector in UI
- ✅ Both chart types working with all intervals

## ✨ Features

### Intraday Intervals
- **1 minute** - Ultra high-frequency trading
- **2 minutes** - High-frequency analysis  
- **5 minutes** - Standard day trading
- **15 minutes** - Swing trading
- **30 minutes** - Position entry
- **1 hour** - Trend analysis
- **90 minutes** - Extended intervals
- **Daily/Weekly/Monthly** - Long-term analysis

### Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA/EMA)
- Support & Resistance Levels
- Volume Analysis

### Machine Learning
- RandomForest predictions
- 5-period forecasting
- Confidence scoring
- Automatic model training

### Additional Features
- Real-time candlestick charts
- Auto-refresh (30s, 1m, 5m, 10m)
- Quick interval buttons
- Export to CSV
- Australian stocks (.AX suffix)
- Alpha Vantage fallback

## 📊 Usage Guide

### Basic Operation
1. Enter a stock symbol (e.g., AAPL, TSLA, MSFT)
2. Select time period (1 day to 5 years)
3. Choose interval (1 minute to 1 month)
4. Click "Analyze"

### Quick Interval Buttons
Click any button for instant timeframe switching:
- **1m, 5m, 15m** - Intraday trading
- **30m, 1H** - Short-term analysis
- **1D, 1W, 1M** - Long-term trends

### Auto-Refresh
Set automatic updates:
- Manual (default)
- 30 seconds (scalping)
- 1 minute (active trading)
- 5 minutes (monitoring)
- 10 minutes (casual tracking)

### Export Data
Click "Export" to download CSV with:
- Date/Time stamps
- OHLC (Open, High, Low, Close)
- Volume data

## 🔧 Requirements

- Python 3.8 or higher
- Windows 10/11 (batch files provided)
- Internet connection for market data
- Modern web browser

## 📈 Data Sources

- **Primary**: Yahoo Finance
- **Fallback**: Alpha Vantage
- **Coverage**: US, International, Crypto

## ⚠️ Troubleshooting

### Port 8000 Already in Use
```bash
# Windows - Find and kill process:
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F
```

### Missing Dependencies
```bash
# Reinstall packages:
pip install -r requirements.txt
```

### No Data Showing
- Check internet connection
- Verify stock symbol is correct
- Try different time period
- Markets may be closed

## 📝 API Endpoints

- `GET /` - Web interface
- `GET /api/stock/{symbol}?period={period}&interval={interval}`
- `GET /favicon.ico` - Handled (no 404)

## 🎯 Trading Tips

### Day Trading
- Use 5-minute charts for trends
- Switch to 1-minute for entry/exit
- Enable 30-second refresh
- Watch volume spikes

### Swing Trading
- Focus on 15-30 minute charts
- Check daily for confirmation
- Set 5-minute refresh
- Monitor support/resistance

### Long-term Investing
- Use daily/weekly charts
- Check monthly for trends
- Manual refresh is fine
- Focus on moving averages

## 📞 Support

For issues or questions:
1. Check console output for errors
2. Verify Python version: `python --version`
3. Ensure all packages installed: `pip list`
4. Try manual start: `python app.py`

## 📄 Files Included

- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `INSTALL.bat` - Package installer
- `START.bat` - Application launcher
- `QUICK_START.bat` - One-click setup & run
- `README.md` - This documentation

## 🔒 Security Note

This is a development server. For production use:
- Deploy behind a reverse proxy
- Use environment variables for API keys
- Enable HTTPS
- Implement authentication

## 📊 Version

- **Version**: 2.2
- **Status**: Production Ready
- **Updated**: October 2024

---

**Enjoy trading with real-time intraday data!** 📈