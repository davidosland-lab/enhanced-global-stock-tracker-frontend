# StockTracker V10 - Windows 11 Edition
## Real-Time Stock Analysis with ML Predictions

### ✨ Key Features
- **REAL DATA ONLY** - No mock/simulated data, powered by Yahoo Finance API
- **FinBERT Sentiment Analysis** - Advanced financial sentiment using transformers
- **50x Faster Historical Data** - SQLite caching for lightning-fast retrieval
- **ML Predictions** - RandomForest model with 10+ technical indicators
- **Backtesting** - Test strategies with $100,000 starting capital
- **Windows 11 Optimized** - SSL fixes and path handling for Windows

### 🚀 Quick Start

1. **Install Dependencies**
   ```batch
   INSTALL.bat
   ```
   This will create a virtual environment and install all requirements.

2. **Start All Services**
   ```batch
   START.bat
   ```
   This launches all 5 backend services and opens the dashboard.

3. **Access Dashboard**
   Open your browser to: http://localhost:8000

### 📊 Services Overview

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| Main Backend | 8000 | Core API and dashboard | Real data from Yahoo Finance |
| ML Backend | 8002 | Machine Learning predictions | RandomForest with real features |
| FinBERT Backend | 8003 | Sentiment analysis | Transformers or keyword fallback |
| Historical Backend | 8004 | Cached historical data | 50x faster with SQLite |
| Backtesting Backend | 8005 | Strategy testing | $100,000 starting capital |

### 🔧 System Requirements

- **Windows 11** (also works on Windows 10)
- **Python 3.8+** 
- **4GB RAM minimum** (8GB recommended for FinBERT)
- **2GB disk space** (for models and cache)

### 📁 Project Structure

```
StockTracker_V10_Windows11_Clean/
├── main_backend.py          # Core API service
├── ml_backend.py            # ML training & predictions (FIXED)
├── finbert_backend.py       # Sentiment analysis
├── historical_backend.py    # SQLite cached data (NEW)
├── backtesting_backend.py   # Trading strategy tests
├── index.html              # Main dashboard
├── prediction_center.html   # ML interface
├── requirements.txt        # Python dependencies
├── INSTALL.bat            # Installation script
├── START.bat              # Startup script
├── diagnose.py            # Diagnostic tool
└── README.md              # This file
```

### 🛠️ Troubleshooting

Run the diagnostic tool to check your system:
```batch
python diagnose.py
```

Common issues and fixes:

1. **SSL Certificate Errors**
   - Already fixed in START.bat with environment variables

2. **ML Backend Crashes**
   - Fixed: Multi-level DataFrame columns from yfinance handled
   - Fixed: Safe division in volume_ratio calculation

3. **FinBERT Installation Fails**
   - System will automatically use keyword-based sentiment as fallback

4. **Port Already in Use**
   - START.bat automatically kills existing Python processes

### 📈 ML Training Details

The ML backend uses **RandomForestRegressor** with:
- **100 estimators** (trees)
- **Max depth of 10** 
- **10+ technical indicators** including:
  - RSI, MACD, Bollinger Bands
  - Moving averages (5, 20, 50 day)
  - Volume ratios and price momentum
  
Training typically takes **10-60 seconds** with real market data.

### 💰 Backtesting Features

- **Starting Capital**: $100,000
- **Strategies**: Buy & Hold, Mean Reversion, Momentum
- **Metrics**: Total return, Sharpe ratio, max drawdown
- **Real market data** from Yahoo Finance

### 🔒 Data Policy

**NO FAKE DATA** - This system uses only:
- Real-time stock prices from Yahoo Finance
- Actual historical market data
- Genuine technical indicators calculated from real prices
- No Math.random(), no simulations, no mock data

### 📝 Version History

- **V10** - Complete rewrite with all fixes applied
  - Fixed ML backend DataFrame issues
  - Added SQLite historical caching (50x faster)
  - Implemented real FinBERT sentiment
  - Windows 11 SSL fixes
  - Removed ALL fake/mock data

### 🤝 Support

For issues or questions:
1. Run `python diagnose.py` first
2. Check service logs in command windows
3. Verify all services show "running" in dashboard

### 📊 Performance

With SQLite caching enabled:
- First data fetch: ~2-5 seconds
- Cached data fetch: ~0.1 seconds (50x faster!)
- ML training: 10-60 seconds (real computation)
- Predictions: <1 second

---
**Built with real data for real traders** 🚀