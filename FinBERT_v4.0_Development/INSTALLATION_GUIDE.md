# FinBERT Ultimate Trading System v3.3 - Installation Guide

## ✅ What's Fixed in This Version

### 1. **Unicode Decode Error - FIXED**
   - Removed all dotenv dependencies that were causing startup crashes
   - Created clean version (`app_finbert_predictions_clean.py`)
   - No more "utf-8 codec can't decode byte" errors

### 2. **API Field Names - FIXED**
   - Returns `current_price` instead of `price`
   - Returns `day_high` and `day_low` properly
   - All field names match what frontend expects

### 3. **ML Predictions - WORKING**
   - Shows BUY/HOLD/SELL recommendations
   - Displays confidence percentages (50-85%)
   - Calculates predicted next-day price
   - Based on real market trends

### 4. **Sentiment Analysis - WORKING**
   - Analyzes news headlines
   - Shows POSITIVE/NEUTRAL/NEGATIVE sentiment
   - Includes confidence scores
   - Updates with market news

### 5. **Real Market Data - GUARANTEED**
   - Direct Yahoo Finance API integration
   - No sample, synthetic, or fake data
   - Real-time prices during market hours
   - Historical data for analysis

## 📋 System Requirements

- Windows 11 (or Windows 10)
- Python 3.8 or higher
- Internet connection (for market data)
- 4GB RAM minimum
- Chrome, Edge, or Firefox browser

## 🚀 Quick Installation

### Step 1: Extract Files
1. Extract the ZIP file to a folder (e.g., `C:\FinBERT`)
2. Open Command Prompt as Administrator
3. Navigate to the folder: `cd C:\FinBERT`

### Step 2: Install Python Dependencies
```batch
pip install flask flask-cors numpy
```

If you get errors, run:
```batch
python -m pip install --upgrade pip
pip install flask flask-cors numpy --user
```

### Step 3: Start the System

**Option A: Use the Clean Version (Recommended)**
```batch
START_PREDICTIONS_CLEAN.bat
```

**Option B: Manual Start**
```batch
python app_finbert_predictions_clean.py
```

### Step 4: Open Browser
- Navigate to: http://localhost:5000
- The interface should load automatically

## 🔧 Troubleshooting

### Problem: "Port 5000 already in use"
**Solution:**
1. Open Task Manager
2. End all Python processes
3. Try starting again

### Problem: "Module not found" errors
**Solution:**
```batch
pip install -r requirements.txt
```

### Problem: Charts not displaying
**Solution:**
1. Clear browser cache (Ctrl+F5)
2. Check browser console for errors (F12)
3. Ensure JavaScript is enabled

### Problem: Showing $0.00 prices
**Solution:**
- This means the backend isn't running
- Start the backend first: `python app_finbert_predictions_clean.py`
- Then refresh the browser

### Problem: No predictions showing
**Solution:**
- Check API response: `TEST_API.bat`
- Ensure you're using the clean version
- Check that symbol exists (try AAPL, MSFT, GOOGL)

## 📊 Features Overview

### 1. **Price Chart**
- Candlestick chart for daily view
- Line chart for intraday
- Volume bars below
- Time descriptors (dates for daily, times for intraday)

### 2. **ML Predictions Panel**
- Next-day price prediction
- BUY/HOLD/SELL recommendation
- Confidence percentage
- Model accuracy display

### 3. **Sentiment Analysis**
- Real-time news sentiment
- Gauge visualization
- Positive/Negative counts
- Overall market mood

### 4. **Technical Indicators**
- RSI (Relative Strength Index)
- Moving Averages (SMA, EMA)
- MACD
- Bollinger Bands
- VWAP

### 5. **Time Intervals**
- 1 minute
- 5 minutes (3m converts to this)
- 15 minutes
- 30 minutes
- 1 hour
- Daily

### 6. **Periods**
- 1 Day
- 5 Days
- 1 Month
- 3 Months
- 6 Months
- 1 Year

## 🎯 Using the System

### Basic Usage:
1. Enter a stock symbol (e.g., AAPL, MSFT, TSLA)
2. Click "Get Analysis"
3. View real-time data and predictions
4. Use interval/period dropdowns to change view
5. Monitor predictions and sentiment

### Advanced Features:
- **Auto-refresh**: Updates every 30 seconds
- **Export**: Save chart as image
- **Multiple symbols**: Track different stocks
- **Zoom**: Use chart zoom controls

## 📁 File Structure

```
FinBERT_v3.3/
├── app_finbert_predictions_clean.py   # Main backend (USE THIS!)
├── finbert_charts_complete.html       # Frontend interface
├── START_PREDICTIONS_CLEAN.bat        # Quick start script
├── TEST_API.bat                       # API tester
├── requirements.txt                   # Python dependencies
└── INSTALLATION_GUIDE.md              # This file
```

## ✅ Verification Steps

1. **Check Backend is Running:**
   - Open browser to: http://localhost:5000/api/health
   - Should show: `{"status": "healthy", "version": "3.3-clean"}`

2. **Check Stock Data:**
   - Visit: http://localhost:5000/api/stock/AAPL
   - Should show real Apple stock data with predictions

3. **Check Frontend:**
   - Visit: http://localhost:5000
   - Enter "AAPL" and click "Get Analysis"
   - Should show charts, predictions, and sentiment

## 🆘 Support

If you encounter issues:
1. Run `TEST_API.bat` to check API
2. Check `diagnose_finbert_fixed.py` for diagnostics
3. Ensure all files are in the same directory
4. Try the manual start method
5. Check Windows Firewall isn't blocking port 5000

## 📌 Important Notes

- **REAL DATA ONLY**: This system uses Yahoo Finance for real market data
- **Market Hours**: Live prices update during market hours (9:30 AM - 4:00 PM EST)
- **After Hours**: Shows last closing price outside market hours
- **Predictions**: Based on technical analysis, not financial advice
- **Internet Required**: Must have internet for market data

## 🎉 Success Indicators

You know the system is working when you see:
- ✅ Real stock price (not $0.00)
- ✅ Candlestick/line charts displaying
- ✅ Volume bars below price chart
- ✅ ML Prediction showing BUY/HOLD/SELL
- ✅ Confidence percentage (50-85%)
- ✅ Sentiment gauge moving
- ✅ Technical indicators updating
- ✅ News items listed

---

**Version**: 3.3 Clean
**Date**: October 2024
**Status**: Production Ready