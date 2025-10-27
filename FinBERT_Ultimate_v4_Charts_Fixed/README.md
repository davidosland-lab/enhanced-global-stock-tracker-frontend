# FinBERT Ultimate Trading System v4.0 - FIXED
### Complete AI-Powered Stock Analysis with Fixed Predictions & Charts

## 🎯 What's Fixed in v4.0

### 1. **Prediction Service (PRIMARY FIX)**
- ✅ **Auto-training**: Models automatically train when requesting predictions for new symbols
- ✅ **Next-day predictions**: Accurate next-day price predictions with confidence scores
- ✅ **5-10 day targets**: Price targets for 5 and 10 day horizons
- ✅ **SMA_50 calculation**: Fixed the SMA_50 KeyError during predictions
- ✅ **Real-time training**: No need to pre-train models

### 2. **Chart Rendering (SECONDARY FIX)**
- ✅ **Candlestick charts**: Fixed overlapping blocks issue - now renders proper candlesticks
- ✅ **OHLC charts**: Properly configured OHLC chart type
- ✅ **Technical indicators**: SMA, EMA, Bollinger Bands overlay correctly

### 3. **Data Integrity**
- ✅ **Real data only**: No synthetic or hardcoded fallback data
- ✅ **Live market data**: All data fetched from yfinance in real-time
- ✅ **Proper error handling**: Graceful degradation when data unavailable

## 📋 System Requirements

- **Python**: 3.10, 3.11, or 3.12
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 3GB for dependencies and models
- **OS**: Windows 10/11, macOS, Linux
- **Internet**: Required for market data and FinBERT model download

## 🚀 Quick Start

### 1. Install the System
```batch
INSTALL.bat
```
This will:
- Install all Python dependencies
- Configure NumPy for Python 3.12
- Install PyTorch and Transformers
- Set up FinBERT (downloads on first use)
- Create required directories

### 2. Start the System
```batch
START.bat
```
This will:
- Start the API server on port 5000
- Open the charts interface in your browser
- Initialize the prediction service

### 3. Use the System
- Open browser to: `http://localhost:5000` (API dashboard)
- Or open: `finbert_charts.html` (Charts interface)
- Enter any stock symbol (e.g., AAPL, MSFT, GOOGL)
- System will auto-train models as needed

## 🔧 Key Features

### AI Predictions
- **Random Forest Classifier**: 100 trees, max_depth=10
- **Auto-training**: Models train automatically on first prediction request
- **Features used**:
  - Price movements and returns
  - Technical indicators (RSI, MACD, ATR)
  - Moving averages (SMA_20, SMA_50)
  - Bollinger Bands position
  - Volume patterns
  - Volatility metrics

### FinBERT Sentiment Analysis
- **Model**: ProsusAI/finbert (downloads ~2GB on first use)
- **News sources**: Yahoo Finance, Google News
- **Sentiment range**: -1 (bearish) to +1 (bullish)
- **Fallback**: Basic sentiment if FinBERT unavailable

### Technical Indicators
- **Moving Averages**: SMA (20, 50), EMA (20)
- **Momentum**: RSI (14), MACD (12, 26, 9)
- **Volatility**: Bollinger Bands, ATR (14)
- **Volume**: Volume ratio, average volume

### Charts
- **Types**: Candlestick, OHLC, Line
- **Timeframes**: 1D, 5D, 1M, 3M, 6M, 1Y
- **Features**: Zoom, pan, technical overlays
- **Sub-charts**: RSI, MACD indicators

## 📊 API Endpoints

### Get Stock Data
```
GET /api/stock/{symbol}
```
Returns current price, technical indicators, SMA_50

### Get AI Prediction (Auto-trains)
```
GET /api/predict/{symbol}
```
Returns:
- Next-day price prediction
- 5-day and 10-day targets
- Confidence score
- Sentiment analysis
- Model accuracy

### Get Historical Data
```
GET /api/historical/{symbol}?period=1mo&interval=1d
```
Returns OHLCV data for charts

### Get News & Sentiment
```
GET /api/news/{symbol}
```
Returns latest news with FinBERT sentiment scores

### Force Retrain Model
```
POST /api/train
Body: {"symbol": "AAPL", "period": "6mo"}
```
Forces model retraining with specified period

## 🐛 Troubleshooting

### Installation Issues

#### "Batch file closes during FinBERT installation"
- **Fixed in v4.0**: Added error handling and verification steps
- Installation continues even if some components fail
- System uses fallback sentiment if FinBERT unavailable

#### "NumPy compatibility error"
- **Fixed in v4.0**: Installs NumPy 1.26.4 for Python 3.12
- Automatically handles version conflicts

### Runtime Issues

#### "SMA_50 KeyError"
- **Fixed in v4.0**: Properly calculates SMA_50 even with limited data
- Uses available data if less than 50 days

#### "No prediction available"
- **Fixed in v4.0**: Auto-trains model on first request
- No need to manually train models

#### "Charts show overlapping blocks"
- **Fixed in v4.0**: Correct candlestick chart configuration
- Proper type specification in Chart.js

#### "Cannot connect to server"
- Ensure no other service is using port 5000
- Check Windows Firewall settings
- Try running as Administrator

## 📁 File Structure

```
FinBERT_Ultimate_v4_Charts_Fixed/
├── app_finbert_ultimate.py     # Main trading model
├── app_finbert_api_fixed.py    # Fixed API server (v4.0)
├── finbert_charts.html          # Fixed charts interface
├── INSTALL.bat                  # Enhanced installer
├── START.bat                    # Server starter
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── directories/
    ├── cache/                   # Model cache
    ├── models/                  # Trained models
    ├── logs/                    # System logs
    └── data/                    # Data storage
```

## 🔄 Version History

### v4.0 (Current)
- Fixed prediction service with auto-training
- Fixed next-day and target price predictions
- Fixed SMA_50 calculation error
- Fixed candlestick chart rendering
- Enhanced error handling in installer

### v3.0
- Added FinBERT sentiment analysis
- Added charting interface
- Python 3.12 compatibility

### v2.0
- Random Forest predictions
- Technical indicators
- Basic API server

## 💡 Tips for Best Results

1. **First Run**: Let FinBERT download completely (~2GB)
2. **Training**: Models improve with more historical data
3. **Symbols**: Use standard tickers (AAPL, not Apple Inc.)
4. **Updates**: Predictions update when market data changes
5. **Performance**: Close other applications for faster processing

## 🆘 Support

If you encounter issues:
1. Check the server window for error messages
2. Verify all dependencies installed correctly
3. Ensure Python 3.10+ is in PATH
4. Try running INSTALL.bat again
5. Check if port 5000 is available

## 📜 License

This system is for educational and research purposes. 
Always verify predictions with your own analysis before making investment decisions.

---
*FinBERT Ultimate Trading System v4.0 - Real Data, Real Predictions, Real Results*