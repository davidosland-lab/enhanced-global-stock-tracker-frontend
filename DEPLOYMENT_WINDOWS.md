# Professional Stock Analysis System - Windows 11 Deployment Guide

## 🚀 System Overview

This is a **professional-grade stock analysis system** with:
- **TradingView Lightweight Charts** for professional financial visualization  
- **Real-time data** from Yahoo Finance and Alpha Vantage
- **Australian stock support** with automatic .AX suffix detection
- **Machine Learning predictions** using Random Forest and Gradient Boosting
- **12 Technical Indicators** including RSI, MACD, Bollinger Bands, SMA, EMA, ATR
- **Interactive charts** with Candlestick, Line, and Area views
- **Volume histograms** and professional trading UI

## 📊 Live Demo

**Access the live system here:** https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

## 🎯 Key Features Implemented

### ✅ Professional Financial Charts
- **TradingView Lightweight Charts** integration (industry standard)
- **Candlestick charts** with OHLC data
- **Line and Area charts** with smooth transitions
- **Volume histograms** with color-coded bars
- **Responsive design** that adapts to screen size

### ✅ Data Sources
- **Yahoo Finance** primary data source (100% real data, NO MOCKS)
- **Alpha Vantage** backup with your API key: `68ZFANK047DL0KSR`
- **Auto-fallback** mechanism if one source fails
- **Australian stocks** auto-detection (.AX suffix)

### ✅ Technical Analysis
All 12 indicators working with minimal data:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- ATR (Average True Range)
- Stochastic Oscillator
- Williams %R
- CCI (Commodity Channel Index)
- OBV (On Balance Volume)
- MFI (Money Flow Index)
- ADX (Average Directional Index)

### ✅ Machine Learning
- Random Forest Regressor
- Gradient Boosting Regressor
- Ensemble predictions with confidence scores
- BUY/HOLD/SELL recommendations

## 💻 Windows 11 Installation

### Prerequisites
```bash
# Ensure Python 3.8+ is installed
python --version

# Install required packages
pip install flask flask-cors yfinance pandas numpy scikit-learn requests
```

### Deployment Steps

1. **Download the main file:** `unified_stock_professional.py`

2. **Set environment variable to prevent UTF-8 errors:**
```bash
set FLASK_SKIP_DOTENV=1
```

3. **Run the application:**
```bash
python unified_stock_professional.py
```

4. **Access in browser:**
```
http://localhost:8000
```

## 🔧 Configuration

### Alpha Vantage API Key
Your API key is already embedded: `68ZFANK047DL0KSR`

To change it, edit line 61 in `unified_stock_professional.py`:
```python
ALPHA_VANTAGE_KEY = "YOUR_NEW_KEY_HERE"
```

### Port Configuration
Default port is 8000. To change, edit the last line:
```python
app.run(host="0.0.0.0", port=8000)  # Change 8000 to your preferred port
```

## 📈 Usage Guide

### Quick Start
1. Open http://localhost:8000
2. Enter a stock symbol (e.g., CBA for Commonwealth Bank)
3. Select time period (1 Day to 1 Year)
4. Click "Analyze Stock"

### Chart Controls
- **Candlestick**: Professional OHLC candlestick chart
- **Line**: Simple line chart for price trends
- **Area**: Filled area chart for visual impact
- **Volume**: Toggle volume histogram on/off

### Australian Stocks
The system automatically adds .AX suffix:
- CBA → CBA.AX
- BHP → BHP.AX
- CSL → CSL.AX
- NAB → NAB.AX
- WBC → WBC.AX

### Quick Access Buttons
Pre-configured for popular stocks:
- 🇦🇺 Australian: CBA, BHP, CSL, NAB, WBC
- 🇺🇸 US: AAPL, MSFT, GOOGL, TSLA, AMZN

## 🛠️ Troubleshooting

### Windows 11 Specific Fixes

1. **UTF-8 Encoding Issues**
   - Always set: `set FLASK_SKIP_DOTENV=1`
   - Run with explicit encoding: `python -X utf8 unified_stock_professional.py`

2. **Port Already in Use**
   ```bash
   # Find process using port 8000
   netstat -ano | findstr :8000
   # Kill the process
   taskkill /PID <process_id> /F
   ```

3. **Missing Dependencies**
   ```bash
   pip install --upgrade pip
   pip install flask flask-cors yfinance pandas numpy scikit-learn requests
   ```

4. **Yahoo Finance 404 Errors**
   - The system uses `yf.download()` with proper parameters
   - Auto-fallback to Alpha Vantage if Yahoo fails
   - All 404 issues have been resolved

## 📊 API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Fetch Stock Data
```
POST http://localhost:8000/api/fetch
Content-Type: application/json

{
    "symbol": "CBA",
    "period": "1mo",
    "dataSource": "auto"
}
```

### Calculate Indicators
```
POST http://localhost:8000/api/indicators
Content-Type: application/json

{
    "prices": [100, 101, 102, ...],
    "volumes": [1000000, ...]
}
```

### Get Predictions
```
POST http://localhost:8000/api/predict
Content-Type: application/json

{
    "data": {
        "symbol": "CBA.AX",
        "prices": [...],
        "current_price": 173.56
    }
}
```

## ✨ What Makes This Professional

1. **Industry-Standard Charts**: TradingView Lightweight Charts (used by major trading platforms)
2. **Real-Time Data**: No mock data, 100% live market information
3. **Comprehensive Analysis**: 12 technical indicators + ML predictions
4. **Professional UI**: Clean, responsive design with gradient backgrounds
5. **Error Handling**: Graceful fallbacks and clear error messages
6. **Performance**: 5-minute cache to reduce API calls
7. **Extensibility**: Clean code structure for easy modifications

## 📝 Version History

- **v3.0** (Current): TradingView Lightweight Charts integration
- **v2.0**: Added ML predictions and technical indicators
- **v1.0**: Basic Yahoo Finance integration

## 🎉 Success Checklist

- [x] Yahoo Finance connectivity fixed (no 404 errors)
- [x] ALL mock/demo data removed (100% real)
- [x] Unified system at localhost:8000
- [x] Alpha Vantage API integrated
- [x] Australian stocks with .AX suffix
- [x] Windows 11 UTF-8 issues resolved
- [x] ML predictions working
- [x] 12 technical indicators functional
- [x] Professional TradingView charts
- [x] Interactive chart types (Candlestick/Line/Area)
- [x] Volume histogram display

## 💡 Tips

- Use 1-month or 3-month periods for best ML prediction accuracy
- Australian market data updates after ASX trading hours (4:00 PM AEST)
- Alpha Vantage has a 5 calls/minute limit on free tier
- Chart automatically falls back to line chart if OHLC data unavailable

## 🚀 Ready to Trade!

Your professional stock analysis system is now ready. The TradingView charts provide institutional-grade visualization, while the ML predictions and technical indicators offer comprehensive market analysis.

**Remember**: This is for educational/analytical purposes. Always do your own research before making investment decisions.

---

**Created with 💜 by Your AI Assistant**
*Professional-grade financial analysis at your fingertips*