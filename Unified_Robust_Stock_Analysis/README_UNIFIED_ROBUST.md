# Unified Robust Stock Analysis System

## 🚀 Overview

A comprehensive, production-ready stock analysis system that provides **100% REAL market data** with NO synthetic or demo data. The system combines multiple data sources, technical analysis, market sentiment indicators, and machine learning predictions into a unified, robust platform.

## ✨ Key Features

### 1. **Real Market Data Only**
- **Yahoo Finance** (Primary source) with intelligent rate limiting
- **Alpha Vantage** (Fallback) with included API key: `68ZFANK047DL0KSR`
- Automatic failover between data sources
- Australian stock support with .AX suffix handling

### 2. **Technical Indicators**
- RSI (Relative Strength Index) with overbought/oversold signals
- MACD with crossover detection
- Bollinger Bands with position analysis
- Simple Moving Averages (SMA 10, 20, 50)
- Exponential Moving Averages (EMA)
- Volume analysis and ratios

### 3. **Market Sentiment Analysis**
- **VIX Fear Index** - Market volatility gauge
- **Market Breadth** - S&P 500 advance/decline analysis
- **Treasury Yields** - 10-year bond yield tracking
- **Dollar Index** - USD strength indicator
- **Sector Rotation** - Analysis of leading/lagging sectors
- **Overall Sentiment Score** - Combined market mood indicator

### 4. **Machine Learning Predictions**
- RandomForest model for price predictions
- 1, 3, 5, and 7-day forecasts
- Feature importance analysis
- Confidence scores for each prediction
- Automatic model training on historical data

### 5. **Advanced Charting**
- Line, Candlestick, and Volume charts
- **Zoom functionality** (mouse wheel, pinch, pan)
- No date parsing errors (uses index-based approach)
- Responsive design for all screen sizes
- Real-time data updates

### 6. **Data Sources & Rate Limiting**
- Yahoo Finance: 3-second delay between requests
- Alpha Vantage: 5 requests per minute (0.2s delay)
- Automatic fallback on rate limit errors (429)
- Connection error handling and retries

## 📦 Installation

### Windows 11 Quick Start

1. **Fastest Method - Quick Start:**
   ```batch
   QUICK_START_UNIFIED.bat
   ```
   This will install dependencies and start the app immediately.

2. **Standard Installation:**
   ```batch
   INSTALL_UNIFIED_ROBUST.bat
   RUN_UNIFIED_ROBUST.bat
   ```

3. **Debug Mode (if issues occur):**
   ```batch
   DEBUG_UNIFIED.bat
   ```

### Manual Installation

```bash
# Install Python 3.8+ if not already installed
# Then install dependencies:
pip install flask flask-cors pandas numpy yfinance requests

# Optional (for ML predictions):
pip install scikit-learn

# Run the application:
python app_unified_robust.py
```

## 🎯 Usage

### Basic Usage

1. **Start the application** using one of the batch files
2. **Open browser** to http://localhost:5000
3. **Enter stock symbol** (e.g., AAPL, MSFT, GOOGL, CBA)
4. **Click "Get Data"** to fetch real-time market data

### Australian Stocks
The system automatically handles Australian stock symbols:
- Enter `CBA` → System fetches `CBA.AX` from Yahoo
- Enter `BHP` → System fetches `BHP.AX` from Yahoo
- Automatic fallback to Alpha Vantage if Yahoo fails

### Chart Controls
- **Chart Types:** Line, Candlestick, Volume
- **Zoom In:** Mouse scroll up or click "Zoom In"
- **Zoom Out:** Mouse scroll down or click "Zoom Out"
- **Pan:** Click and drag on chart
- **Reset:** Click "Reset Zoom"

### Market Sentiment
Click "Market Sentiment" to view:
- Overall market mood (Bullish/Bearish/Neutral)
- VIX fear gauge
- Treasury yield trends
- Dollar strength
- Sector rotation patterns

### ML Predictions
Click "ML Predictions" to generate:
- Multi-day price forecasts
- Confidence scores
- Feature importance analysis
- Expected returns

## 🔧 Configuration

### API Keys
- **Alpha Vantage Key:** `68ZFANK047DL0KSR` (included)
- To use your own key, edit `app_unified_robust.py`:
  ```python
  ALPHA_VANTAGE_KEY = "YOUR_KEY_HERE"
  ```

### Rate Limiting
Adjust delays in `app_unified_robust.py`:
```python
YAHOO_REQUEST_DELAY = 3  # seconds
AV_REQUEST_DELAY = 0.2   # seconds
```

### Port Configuration
Default port is 5000. To change:
```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=False)
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

1. **"Python not found" error:**
   - Install Python 3.8+ from python.org
   - Ensure "Add Python to PATH" is checked during installation

2. **Dependencies installation fails:**
   - Run: `python -m pip install --upgrade pip`
   - Try: `pip install --user flask pandas yfinance`

3. **Port 5000 already in use:**
   - Close other applications using port 5000
   - Or change port in `app_unified_robust.py`

4. **Yahoo Finance 429 errors:**
   - The system automatically handles rate limiting
   - Falls back to Alpha Vantage if Yahoo is unavailable

5. **Charts not displaying:**
   - Ensure JavaScript is enabled in browser
   - Try refreshing the page (F5)
   - Check browser console for errors (F12)

6. **ML predictions not working:**
   - Install scikit-learn: `pip install scikit-learn`
   - System will work without ML (other features remain)

### Debug Mode
Run `DEBUG_UNIFIED.bat` to see:
- Python version and path
- Installed packages
- Network connectivity
- Port availability
- Detailed error messages

## 📊 Technical Details

### Architecture
```
┌─────────────────────────────────────┐
│         Web Interface (HTML/JS)      │
│    - Chart.js for visualization      │
│    - Responsive tabbed interface     │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│         Flask Backend (Python)       │
│    - RESTful API endpoints           │
│    - CORS enabled                    │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│        Data Layer                    │
├─────────────────────────────────────┤
│  UnifiedDataFetcher                 │
│  - Yahoo Finance (primary)          │
│  - Alpha Vantage (fallback)         │
├─────────────────────────────────────┤
│  TechnicalAnalysis                  │
│  - RSI, MACD, Bollinger Bands      │
│  - Moving Averages                  │
├─────────────────────────────────────┤
│  MarketSentimentAnalyzer            │
│  - VIX, Treasury, Dollar Index     │
│  - Sector Rotation                  │
├─────────────────────────────────────┤
│  MLPredictor                        │
│  - RandomForest model               │
│  - Feature engineering              │
└─────────────────────────────────────┘
```

### API Endpoints

- `GET /` - Main web interface
- `GET /api/stock/<symbol>` - Fetch stock data
- `GET /api/sentiment` - Market sentiment analysis
- `GET /api/predict/<symbol>` - ML predictions
- `GET /api/sectors` - Sector rotation analysis
- `GET /health` - Health check endpoint

### Data Flow
1. User requests stock data
2. System checks Yahoo Finance (with rate limiting)
3. If Yahoo fails, fallback to Alpha Vantage
4. Calculate technical indicators
5. Generate ML predictions (if available)
6. Return comprehensive data package
7. Frontend renders charts and displays

## 📝 Windows Batch Files

### Batch Files That Don't Close Prematurely

All batch files include:
- `pause` commands to keep window open
- Error checking with appropriate messages
- Clear status updates
- Detailed instructions

**Available Batch Files:**
- `QUICK_START_UNIFIED.bat` - One-click install and run
- `INSTALL_UNIFIED_ROBUST.bat` - Full installation with virtual environment
- `RUN_UNIFIED_ROBUST.bat` - Start application with checks
- `DEBUG_UNIFIED.bat` - Diagnostic information and verbose output

## 🔒 Security & Privacy

- **No data storage** - All data is fetched in real-time
- **No user tracking** - Complete privacy
- **API keys** - Stored locally, never transmitted
- **CORS enabled** - Secure cross-origin requests

## 📈 Performance

- **Rate limiting** prevents API bans
- **Caching** with LRU cache for repeated requests
- **Efficient data structures** for fast processing
- **Responsive design** for smooth user experience
- **Background processing** for heavy computations

## 🎉 Success Confirmation

The system is working correctly when you see:
1. "Server running at: http://localhost:5000" in console
2. Web interface loads with gradient purple background
3. Stock data displays after entering symbol
4. Charts render without "Invalid time value" errors
5. All tabs (Chart, Indicators, Sentiment, Predictions) function

## 💡 Tips & Best Practices

1. **Start with major stocks** (AAPL, MSFT) to test
2. **Use daily intervals** for technical analysis
3. **Check sentiment** during market hours for best results
4. **ML predictions** work best with 6+ months of data
5. **Australian stocks** - just enter base symbol (CBA, not CBA.AX)

## 🚨 Important Notes

- **100% REAL DATA** - No synthetic or demo data ever
- **Rate limits respected** - Automatic delays prevent bans
- **Fallback system** - Always tries multiple data sources
- **Windows optimized** - Batch files handle all setup
- **Production ready** - Error handling and recovery built-in

## 📞 Support

If you encounter issues:
1. Run `DEBUG_UNIFIED.bat` first
2. Check the Troubleshooting section above
3. Ensure all dependencies are installed
4. Verify network connectivity
5. Try with a well-known stock symbol (AAPL)

## 🎯 Quick Test

After starting the application:
1. Enter `AAPL` in the symbol field
2. Click "Get Data"
3. You should see current Apple stock price
4. Try the zoom controls on the chart
5. Click "Market Sentiment" tab
6. Click "ML Predictions" button

If all these work, your system is fully operational!

---

**Version:** 1.0.0  
**Last Updated:** October 2024  
**Status:** Production Ready