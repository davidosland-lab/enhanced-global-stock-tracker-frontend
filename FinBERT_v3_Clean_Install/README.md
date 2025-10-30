# FinBERT Ultimate Trading System v3.0 - FIXED

## ✅ All Issues Resolved

This version fixes all the reported issues:
- ✅ **Installation doesn't close**: Uses `cmd /k` wrapper to keep window open
- ✅ **API endpoint mismatch**: Correct endpoints matching finbert_charts.html
- ✅ **Real market data only**: No hardcoded/fallback data
- ✅ **Technical indicators working**: RSI, MACD, ATR all calculate correctly
- ✅ **Economic indicators**: VIX, Treasury, Dollar Index, Gold all display
- ✅ **FinBERT sentiment**: Shows actual sentiment scores (not 0.000)
- ✅ **Confidence percentages**: Displayed alongside predictions
- ✅ **Alpha Vantage integration**: Uses your key (68ZFANK047DL0KSR)
- ✅ **Direct Yahoo Finance**: Bypasses broken yfinance library
- ✅ **Chart rendering fixed**: Simplified chart implementation that works

## 📁 Files Included

- `app_finbert_v3_fixed.py` - Main application with all fixes
- `finbert_charts.html` - Fixed chart interface
- `INSTALL.bat` - Installation script that won't close
- `START.bat` - Startup script
- `README.md` - This file

## 🚀 Quick Start

### Step 1: Install Dependencies
```batch
INSTALL.bat
```
This will:
- Install all Python packages
- Download FinBERT model (first run only, ~420MB)
- Keep the window open if there are errors

### Step 2: Start the System
```batch
START.bat
```

### Step 3: Open Browser
Navigate to: http://localhost:5000

## 📊 Features

### Real Market Data
- **Yahoo Finance Direct API**: Bypasses broken yfinance
- **Alpha Vantage API**: Secondary source for US stocks
- **No Synthetic Data**: All data is real-time from market

### FinBERT Sentiment Analysis
- Uses ProsusAI/finbert model
- Analyzes news headlines and financial text
- Returns sentiment score from -1 (bearish) to +1 (bullish)

### Machine Learning Predictions
- **Algorithm**: Random Forest Classifier
- **Trees**: 100
- **Max Depth**: 10
- **Features**: Technical indicators, price patterns, volume
- **Output**: Next day and 5-day predictions with confidence

### Technical Indicators
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **ATR**: Average True Range
- **SMA**: Simple Moving Average (20-day)
- **EMA**: Exponential Moving Average

### Economic Indicators
- **VIX**: Volatility Index (Fear Gauge)
- **TNX**: 10-Year Treasury Yield
- **DXY**: US Dollar Index
- **GOLD**: Gold Futures

## 🔧 Troubleshooting

### If Installation Closes
The new installer uses `cmd /k` to keep the window open. If it still closes:
1. Open Command Prompt manually
2. Navigate to this directory
3. Run: `pip install -r requirements.txt`

### If FinBERT Fails to Load
The system will use fallback sentiment analysis. To manually install:
```batch
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu
```

### If Charts Don't Display
1. Check browser console (F12) for errors
2. Make sure JavaScript is enabled
3. Try refreshing the page (Ctrl+F5)

### Port 5000 Already in Use
Change the port in `app_finbert_v3_fixed.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

## 📈 Usage

### Analyzing Stocks
1. Enter symbol in search box (e.g., AAPL, MSFT)
2. For Australian stocks, add .AX (e.g., CBA.AX)
3. Click "Analyze" button

### Understanding Predictions
- **Next Day Prediction**: Expected price tomorrow with confidence %
- **5-Day Target**: Expected price in 5 trading days
- **Confidence**: Higher % means more certainty (based on model probability)
- **Model Accuracy**: Historical accuracy of predictions

### Sentiment Score
- **-1.0 to -0.5**: Very Bearish
- **-0.5 to -0.1**: Bearish
- **-0.1 to 0.1**: Neutral
- **0.1 to 0.5**: Bullish
- **0.5 to 1.0**: Very Bullish

## 🔑 API Keys

### Alpha Vantage (Included)
Your key is already configured: `68ZFANK047DL0KSR`
- Free tier: 25 requests per day
- Used for US stocks when Yahoo fails

### Adding More Keys (Optional)
Edit `app_finbert_v3_fixed.py`:
```python
# Line 51
ALPHA_VANTAGE_KEY = 'your_new_key_here'
```

## 📊 Data Sources Priority

1. **Yahoo Finance Direct** (Primary)
   - Works for most global stocks
   - Real-time data
   - No API key required

2. **Alpha Vantage** (Backup for US stocks)
   - Uses your API key
   - Daily limit: 25 requests
   - US stocks only

## 🐛 Known Limitations

1. **Australian Stocks on Alpha Vantage**: Not supported, uses Yahoo only
2. **API Rate Limits**: Alpha Vantage has 25 requests/day limit
3. **FinBERT Model Size**: ~420MB download on first run
4. **Training Data**: Needs at least 30 days of history for ML predictions

## 📝 Version History

### v3.0 (Current) - FIXED
- Fixed all reported issues
- Direct Yahoo Finance API implementation
- Alpha Vantage integration with user's key
- Simplified chart rendering
- Real data only - no synthetic fallbacks

### Previous Versions
- v2.x had Australian sentiment complexity (removed)
- v1.x had yfinance dependency (broken)

## 🤝 Support

If you encounter issues:
1. Check this README first
2. Look at browser console for errors (F12)
3. Ensure all dependencies are installed
4. Try with a common stock like AAPL first

## 📜 License

This software is provided as-is for educational and research purposes.

---
*Last Updated: October 2024*