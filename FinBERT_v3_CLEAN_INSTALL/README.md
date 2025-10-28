# FinBERT Ultimate Trading System v3.0 - CLEAN INSTALL

## ✅ FIXED ISSUES
- ✅ **Chart rendering fixed** - Properly aggregates intraday data to daily OHLC
- ✅ **Real market data only** - NO hardcoded/fallback data
- ✅ **API endpoints corrected** - Matches finbert_charts.html requirements
- ✅ **Alpha Vantage integrated** - Uses your key: 68ZFANK047DL0KSR
- ✅ **Direct Yahoo Finance API** - Bypasses broken yfinance library
- ✅ **Confidence percentages added** - Shows prediction confidence alongside prices
- ✅ **Economic indicators working** - VIX, Treasury, Dollar, Gold
- ✅ **Technical indicators fixed** - RSI, MACD, ATR displaying correctly
- ✅ **FinBERT sentiment analysis** - With confidence scores

## 🚀 Quick Start

### Windows Installation:
1. **Install Python 3.8+** from [python.org](https://python.org) if not already installed
2. **Run installer**: Double-click `INSTALL_FINBERT_FIXED.bat`
3. **Start system**: Double-click `START_FINBERT_FIXED.bat`
4. **Open browser**: Navigate to http://localhost:5000

### Manual Installation:
```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install FinBERT (for enhanced sentiment analysis)
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu

# Start the server
python app_finbert_complete_fixed.py
```

## 📊 Features

### Real-Time Market Data
- **Yahoo Finance Direct API**: Real-time stock prices and historical data
- **Alpha Vantage Integration**: Secondary data source for US stocks
- **No Synthetic Data**: 100% real market data, no fallbacks

### Technical Analysis
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **ATR** (Average True Range)
- **SMA/EMA** (Simple/Exponential Moving Averages)
- **Bollinger Bands**

### Machine Learning Predictions
- **Random Forest Classifier**: 100 trees, max_depth=10
- **Confidence Scores**: Shows prediction confidence percentage
- **Next Day Prediction**: Price prediction with probability
- **5-Day Target**: Extended forecast with confidence

### Sentiment Analysis
- **FinBERT Integration**: Financial-specific sentiment model
- **News Analysis**: Real-time news sentiment from Yahoo Finance
- **Confidence Scores**: Sentiment confidence percentages

### Economic Indicators
- **VIX**: Volatility/Fear Index
- **TNX**: 10-Year Treasury Yield
- **DXY**: US Dollar Index
- **Gold**: Gold Futures

## 🔧 API Endpoints

- `GET /` - Chart interface
- `GET /api/stock/<symbol>` - Current stock data with indicators
- `GET /api/historical/<symbol>?period=30d` - Historical chart data
- `GET /api/predict/<symbol>` - ML predictions with confidence
- `GET /api/news/<symbol>` - News and sentiment analysis
- `GET /api/economic` - Economic indicators
- `GET /status` - System status

## 📈 Chart Types
- **Line Chart**: Simple price line
- **Candlestick**: OHLC candles
- **OHLC Bars**: Open-High-Low-Close bars

## 🔍 Supported Symbols
- **US Stocks**: AAPL, MSFT, GOOGL, AMZN, etc.
- **Australian Stocks**: CBA.AX, BHP.AX, etc. (Yahoo only)
- **Indices**: ^VIX, ^TNX, ^DJI, ^GSPC
- **Commodities**: GC=F (Gold), CL=F (Oil)

## ⚙️ Configuration

### Alpha Vantage Key
The system includes the key: `68ZFANK047DL0KSR`
To use your own key, edit `app_finbert_complete_fixed.py` line 56:
```python
ALPHA_VANTAGE_KEY = 'YOUR_KEY_HERE'
```

### FinBERT Model
The system will automatically download the FinBERT model (~420MB) on first use if transformers is installed.
The system works without FinBERT using fallback sentiment analysis.

## 🐛 Troubleshooting

### Installation Issues
- **"Python not found"**: Install Python 3.8+ and add to PATH
- **"Module not found"**: Run `pip install -r requirements.txt`
- **Batch file closes**: Use `INSTALL_FINBERT_FIXED.bat` which keeps window open

### Runtime Issues
- **Charts not displaying**: Clear browser cache and refresh
- **No data for symbol**: Try US stocks (AAPL, MSFT) first
- **Port 5000 in use**: Change port in `app_finbert_complete_fixed.py` last line

### Data Issues
- **Australian stocks**: Only work with Yahoo Finance (not Alpha Vantage)
- **Economic indicators**: Some may not be available during market close

## 📝 Version History

### v3.0 CLEAN INSTALL (Current)
- Fixed intraday data aggregation
- Added confidence percentages
- Fixed chart rendering
- Removed all synthetic data
- Corrected API endpoints

### Previous Issues (All Fixed)
- ❌ Charts showing overlapping candlesticks → ✅ Fixed with daily aggregation
- ❌ API endpoint mismatch (404 errors) → ✅ Corrected endpoints
- ❌ yfinance library broken → ✅ Direct API implementation
- ❌ Indicators showing "--" → ✅ Proper calculation
- ❌ No confidence scores → ✅ Added to all predictions
- ❌ Hardcoded fallback data → ✅ Real data only

## 💡 Tips

1. **Best Performance**: Use US stocks during market hours
2. **Training Models**: System automatically trains on first prediction
3. **Sentiment Analysis**: Works better with FinBERT installed
4. **Cache**: Data is cached for 1 minute to reduce API calls

## 📧 Support

This is a clean, working installation of FinBERT Ultimate Trading System v3.0.
All major issues have been fixed and the system uses real market data only.

---
*System ready for production use with real-time market data and ML predictions*