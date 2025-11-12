# FinBERT Ultimate Trading System

## 🚀 Complete Solution with All Fixes

### ✅ All Issues Fixed

1. **Python 3.12 Compatibility** ✓
   - Uses numpy>=1.26.0 (not the incompatible 1.24.3)
   - All dependencies updated for Python 3.12

2. **SMA_50 Error in Predictions** ✓
   - Prediction now fetches sufficient historical data
   - Dynamically calculates required data period based on features
   - Minimum 3 months fetched for predictions (was only 1 month)

3. **Insufficient Data Errors** ✓
   - Adaptive feature selection based on available data
   - Only uses SMA_50 if 50+ days available
   - Falls back to shorter indicators for newer stocks

4. **Real Data Only** ✓
   - NO synthetic data generation
   - Multiple data source fallbacks
   - Uses actual market data exclusively

5. **Enhanced Data Sources** ✓
   - Yahoo Finance (primary)
   - Alpha Vantage (with API key)
   - IEX Cloud (with API key)
   - Finnhub (with API key)
   - Polygon.io (with API key)
   - FRED economic indicators
   - Government RSS feeds

## 📋 System Requirements

- **Python**: 3.12 recommended (3.10+ compatible)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space (5GB if installing FinBERT)
- **OS**: Windows 10/11, Linux, macOS

## 🛠️ Installation

### Quick Install (Windows)

```batch
# Run the complete installer
INSTALL_ULTIMATE.bat
```

### Manual Install

```bash
# 1. Install Python 3.12 dependencies
pip install numpy>=1.26.0
pip install -r requirements_ultimate.txt

# 2. Optional: Install FinBERT components
pip install torch transformers

# 3. Create directories
mkdir cache models logs data
```

## 🏃 Running the System

### Windows
```batch
RUN_ULTIMATE.bat
```

### Linux/Mac
```bash
python app_finbert_ultimate.py
```

Then open browser to: http://localhost:5000

## 🔑 API Keys (Optional)

Set these environment variables for additional data sources:

```bash
# Windows
set ALPHA_VANTAGE_API_KEY=your_key_here
set IEX_TOKEN=your_token_here
set FINNHUB_API_KEY=your_key_here
set POLYGON_API_KEY=your_key_here
set FRED_API_KEY=your_key_here

# Linux/Mac
export ALPHA_VANTAGE_API_KEY=your_key_here
export IEX_TOKEN=your_token_here
export FINNHUB_API_KEY=your_key_here
export POLYGON_API_KEY=your_key_here
export FRED_API_KEY=your_key_here
```

**Note**: System works without API keys using Yahoo Finance

## 📊 Key Features

### 1. FinBERT Sentiment Analysis
- Uses ProsusAI/finbert model for financial sentiment
- Fallback to rule-based sentiment if FinBERT unavailable
- Analyzes news articles and market sentiment

### 2. Random Forest Classifier
- 100 trees with max_depth=10
- Optimized hyperparameters for stock prediction
- Adaptive feature engineering

### 3. Technical Indicators
- **Momentum**: RSI, Stochastic
- **Trend**: MACD, Moving Averages (SMA 5/10/20/50)
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, Volume Ratio

### 4. Adaptive Features
- Automatically adjusts based on data availability
- Only uses indicators with sufficient data
- Prevents "insufficient data" errors

### 5. Economic Integration
- Federal Reserve data (interest rates)
- Treasury yields
- Unemployment data
- CPI and inflation metrics
- VIX volatility index

## 🎯 Usage Examples

### Training a Model

1. **Quick Test (1 month)**
   - Symbol: AAPL
   - Period: 1mo
   - Good for testing setup

2. **Recommended (6 months)**
   - Symbol: AAPL
   - Period: 6mo
   - Balanced accuracy and speed

3. **Comprehensive (2 years)**
   - Symbol: SPY
   - Period: 2y
   - Best for long-term patterns

### Making Predictions

The system automatically:
1. Checks if model exists for symbol
2. Auto-trains if no model found
3. Fetches sufficient data (3+ months)
4. Calculates all features
5. Returns prediction with confidence

## 🐛 Troubleshooting

### "SMA_50 not in index" Error
**Fixed!** The prediction method now fetches enough data. If you still see this:
1. Check that you're using `app_finbert_ultimate.py`
2. Ensure the symbol has 50+ days of history
3. Try training with a longer period

### "Insufficient data" Error
**Fixed!** Adaptive features handle this. If you still see this:
1. Verify the symbol exists and is traded
2. Check your internet connection
3. Try a different data period

### NumPy Compatibility Error
**Fixed!** If you see numpy errors:
```bash
pip uninstall numpy
pip install numpy>=1.26.0
```

### FinBERT Not Loading
This is optional. The system has fallback sentiment analysis.
To install FinBERT:
```bash
pip install torch transformers
```

## 📈 Performance Tips

1. **Data Period Selection**
   - 1mo: Quick tests, volatile predictions
   - 3mo: Good balance
   - 6mo: Recommended for most stocks
   - 1y+: Better for stable predictions

2. **Best Practices**
   - Train during market hours for latest data
   - Retrain models weekly for accuracy
   - Use multiple timeframes for validation

3. **API Performance**
   - Yahoo Finance: Fast, no key needed
   - Alpha Vantage: Good for historical data
   - IEX Cloud: Real-time data
   - Finnhub: International markets

## 🔍 Understanding Predictions

### Prediction Output
- **Direction**: UP or DOWN
- **Confidence**: 0-100% certainty
- **Probabilities**: Exact up/down chances
- **Top Features**: What's driving the prediction
- **Data Points**: How much data was analyzed

### Confidence Levels
- **>80%**: Strong signal
- **60-80%**: Moderate confidence
- **<60%**: Weak signal, use caution

## 📊 Supported Markets

### US Stocks
- AAPL, MSFT, GOOGL, AMZN, TSLA
- All NYSE and NASDAQ symbols

### ETFs
- SPY, QQQ, DIA, IWM
- Sector and international ETFs

### Crypto (via Yahoo)
- BTC-USD, ETH-USD
- Major cryptocurrencies

### International (with suffix)
- Australian: .AX (CBA.AX, BHP.AX)
- UK: .L (BP.L, HSBA.L)
- German: .DE (BMW.DE)
- Japanese: .T (7203.T)

### Indices
- ^GSPC (S&P 500)
- ^DJI (Dow Jones)
- ^VIX (Volatility Index)

## 🔐 Security Notes

- API keys are never logged or transmitted
- Models are saved locally in `models/` directory
- No user data is collected or shared
- All processing happens locally

## 📝 Change Log

### Version 2.0 - Ultimate Edition
- Fixed Python 3.12 numpy compatibility
- Fixed SMA_50 prediction error
- Fixed insufficient data issues
- Added adaptive feature selection
- Added multiple data sources
- Added economic indicators
- Added government announcements
- Removed all synthetic data generation
- Enhanced error handling
- Improved prediction accuracy

## 🤝 Credits

- **FinBERT Model**: ProsusAI/finbert
- **Random Forest**: scikit-learn
- **Technical Indicators**: ta library
- **Data**: Yahoo Finance, Alpha Vantage, etc.

## 📧 Support

For issues or questions:
1. Check this README first
2. Verify you're using Python 3.12
3. Ensure numpy >= 1.26.0
4. Try the Quick Install

## ⚖️ License

MIT License - Use freely for personal and commercial projects.

---

**Remember**: This is a prediction tool, not financial advice. Always do your own research before trading!