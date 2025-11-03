# Stock Analysis ML System - Windows 11

## 🚀 Complete Stock Analysis with Machine Learning

A professional stock analysis system featuring:
- **Machine Learning predictions** using RandomForest
- **Yahoo Finance primary data** with Alpha Vantage fallback
- **All timeframes working**: 1 day, 5 days, 1 month, 3 months, 6 months, 1 year, 5 years
- **Accurate current prices** from multiple sources
- **Technical indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Australian stocks** auto-detection (.AX suffix)

## 📦 Quick Start

### One-Click Installation & Run:
1. **Extract** this ZIP to any folder (e.g., `C:\StockAnalysis`)
2. **Double-click** `install_and_run.bat`
3. **Wait** for installation (first time only, 2-3 minutes)
4. **Browser opens automatically** at http://localhost:8000

## ✅ What's Fixed

### From Your Issues:
- ✅ **ML Component Reinstated**: Full RandomForest predictions with confidence bands
- ✅ **All Timeframes Working**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y all functional
- ✅ **Yahoo Finance Primary**: Uses Yahoo first, Alpha Vantage as fallback
- ✅ **Accurate Current Prices**: Fetches real-time prices from ticker.info
- ✅ **Candlestick Charts**: Proper OHLC rendering with green/red colors

## 📊 Features

### Machine Learning:
- **5-day price predictions** with confidence bands
- **RandomForest model** with feature engineering
- **Technical indicators** as ML features
- **Confidence scores** for prediction accuracy

### Data Sources (Priority Order):
1. **Yahoo Finance** - Primary source for all data
2. **Alpha Vantage** - Automatic fallback (API key included)
3. **Test Data** - Emergency fallback if both APIs fail

### Chart Types:
- **Candlestick**: Full OHLC with proper coloring
- **Line Chart**: Simple closing prices
- **Area Chart**: Filled area visualization

### Technical Indicators:
- **RSI** (Relative Strength Index)
- **MACD** with signal line and histogram
- **Bollinger Bands** (on candlestick)
- **Moving Averages** (SMA 20, 50)
- **Volume** analysis with color coding

## 🎯 How to Use

### Basic Usage:
1. Enter a stock symbol (AAPL, MSFT, CBA, etc.)
2. Select time period:
   - **1 Day**: 5-minute intervals
   - **5 Days**: 30-minute intervals
   - **1 Month to 5 Years**: Daily/Weekly data
3. Choose chart type (Candlestick recommended)
4. Click **Generate Chart**

### ML Predictions:
- Enable "Show ML Predictions" checkbox
- Predictions appear as purple dashed line
- Confidence band shows prediction uncertainty
- Stats panel shows predicted % change

### Quick Access Stocks:
- **US**: AAPL, GOOGL, MSFT, TSLA
- **Australian**: CBA, BHP, CSL (auto-adds .AX)

## 🔧 Troubleshooting

### Python Not Found:
```
1. Download Python from https://www.python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart computer after installation
```

### Installation Fails:
```
1. Run as Administrator
2. Check internet connection
3. Disable antivirus temporarily
4. Try: pip install --user -r requirements.txt
```

### No Data Loading:
```
1. Check internet connection
2. Wait a moment and retry (API limits)
3. Try different stock symbol
4. System will use test data if APIs fail
```

## 📁 Files Included

- `app.py` - Main application with ML and data fetching
- `requirements.txt` - Python dependencies including scikit-learn
- `install_and_run.bat` - One-click installer and launcher
- `README.md` - This documentation

## 🔬 Technical Details

### ML Model:
- **Algorithm**: RandomForestRegressor
- **Features**: Price returns, volatility, RSI, MACD, volume ratios
- **Max Depth**: 5 (prevents overfitting)
- **Predictions**: Limited to ±5% daily to maintain realism

### API Configuration:
- **Alpha Vantage Key**: 68ZFANK047DL0KSR (included)
- **Yahoo Finance**: No key required
- **Fallback Logic**: Automatic switching between sources

## 📈 Version Info

**Version 2.0 - ML Complete Edition**
- Machine Learning predictions reinstated
- Fixed all timeframe issues
- Yahoo Finance prioritized
- Accurate current prices
- Full technical analysis

---

Enjoy professional stock analysis with ML predictions on Windows 11!