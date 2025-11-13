# FinBERT v4.0 - Prediction Caching & Multi-Timezone System

## 🎯 Overview

This is the complete FinBERT v4.0 Trading System with **Prediction Caching** and **Multi-Timezone Support** for Windows 11.

### ✨ Key Features

- **🔒 Prediction Locking**: Predictions are cached in database and locked once market opens
- **🌍 Multi-Timezone Support**: Automatic detection for US, Australian, and UK markets
- **📊 Accuracy Tracking**: Complete historical prediction tracking with validation
- **⏰ Automated Scheduler**: Background jobs validate predictions at market close
- **📈 Real-Time Charts**: Interactive candlestick and volume charts
- **🤖 AI-Powered**: LSTM + Technical Analysis + FinBERT Sentiment ensemble predictions

## 📦 What's Included

```
FinBERT_v4.0_Windows11_Prediction_System/
├── app_finbert_v4_dev.py          # Main Flask application
├── finbert_v4_enhanced_ui.html    # Frontend UI with prediction dashboard
├── config_dev.py                   # Configuration settings
├── requirements.txt                # Python dependencies
├── models/
│   ├── lstm_predictor.py          # LSTM neural network predictor
│   ├── finbert_sentiment.py       # FinBERT sentiment analyzer
│   ├── news_sentiment_real.py     # Real-time news sentiment
│   ├── prediction_manager.py      # Prediction lifecycle manager
│   ├── market_timezones.py        # Multi-timezone market detection
│   ├── prediction_scheduler.py    # Automated validation scheduler
│   └── trading/
│       ├── prediction_database.py # Prediction storage & retrieval
│       ├── order_manager.py       # Trading order management
│       ├── portfolio_manager.py   # Portfolio tracking
│       └── risk_manager.py        # Risk management system
├── MULTI_TIMEZONE_PREDICTIONS.md  # Technical documentation
├── README_PREDICTION_SYSTEM.md    # This file
└── INSTALLATION_GUIDE.md          # Step-by-step installation

📁 Auto-Created on First Run:
├── trading.db                     # SQLite prediction database
├── news_sentiment_cache.db        # Sentiment analysis cache
└── trained_models/                # LSTM model storage
```

## 🚀 Quick Start (Windows 11)

### 1. Prerequisites

- **Python 3.8+** installed
- **Internet connection** for stock data
- **Windows 11** (tested and optimized)

### 2. Installation

```powershell
# Extract the ZIP file to your desired location
# Open PowerShell or Command Prompt in the extracted folder

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies for full features
pip install tensorflow transformers torch
```

### 3. Run the Application

```powershell
# Start the server
python app_finbert_v4_dev.py

# Server will start on http://localhost:5001
# Open your browser to: http://localhost:5001
```

### 4. Test the System

```powershell
# Test US stocks
http://localhost:5001/api/predictions/AAPL
http://localhost:5001/api/predictions/TSLA

# Test Australian stocks
http://localhost:5001/api/predictions/BHP.AX
http://localhost:5001/api/predictions/CBA.AX

# Test UK stocks
http://localhost:5001/api/predictions/BP.L
http://localhost:5001/api/predictions/HSBA.L
```

## 🌍 Supported Markets

### 1. **United States (NYSE/NASDAQ)**
- **Timezone**: US/Eastern (EST/EDT)
- **Trading Hours**: 9:30 AM - 4:00 PM EST
- **Prediction Window**: 8:00 AM - 9:30 AM EST (90 minutes before open)
- **Validation Time**: 4:15 PM EST (15 minutes after close)
- **Symbol Format**: No suffix (e.g., AAPL, TSLA, MSFT)

### 2. **Australia (ASX)**
- **Timezone**: Australia/Sydney (AEDT/AEST)
- **Trading Hours**: 10:00 AM - 4:00 PM AEDT
- **Prediction Window**: 8:30 AM - 10:00 AM AEDT (90 minutes before open)
- **Validation Time**: 4:15 PM AEDT (15 minutes after close)
- **Symbol Format**: .AX suffix (e.g., BHP.AX, CBA.AX)

### 3. **United Kingdom (LSE)**
- **Timezone**: Europe/London (GMT/BST)
- **Trading Hours**: 8:00 AM - 4:30 PM GMT
- **Prediction Window**: 6:30 AM - 8:00 AM GMT (90 minutes before open)
- **Validation Time**: 4:45 PM GMT (15 minutes after close)
- **Symbol Format**: .L suffix (e.g., BP.L, HSBA.L)

## 📊 How It Works

### Prediction Lifecycle

```
1. PRE-MARKET (90 min before open)
   ↓
   Generate Prediction → Store in Database
   ↓
2. MARKET OPEN
   ↓
   Lock Prediction (cannot regenerate)
   ↓
3. TRADING HOURS
   ↓
   Serve Cached Prediction (consistent all day)
   ↓
4. MARKET CLOSE
   ↓
5. POST-MARKET (+15 minutes)
   ↓
   Automatic Validation → Calculate Accuracy
```

### Prediction Status Indicators

- 🟢 **Cached** (Green Check): Prediction from database, consistent
- 🔒 **Locked** (Red Lock): Market open, prediction cannot change
- ✨ **Fresh** (Yellow Sparkle): Newly generated prediction

## 🎯 API Endpoints

### Prediction Endpoints

```
GET /api/predictions/<symbol>
    - Get cached daily prediction
    - Returns: prediction with status indicators

GET /api/predictions/<symbol>/history?days=30
    - Get historical predictions with outcomes
    - Returns: list of past predictions + accuracy summary

GET /api/predictions/<symbol>/accuracy?period=month
    - Get detailed accuracy statistics
    - Returns: comprehensive accuracy metrics

POST /api/predictions/validate
    - Manually trigger prediction validation
    - Returns: validation results

GET /api/predictions/scheduler/status
    - Get scheduler status and next run times
    - Returns: scheduler info for all markets
```

### Stock Data Endpoints

```
GET /api/stock/<symbol>?period=1y&interval=1d
    - Get stock data with charts and ML prediction
    - Returns: OHLCV data + technical analysis + sentiment

GET /api/sentiment/<symbol>
    - Get FinBERT sentiment analysis
    - Returns: sentiment scores and news articles

GET /api/health
    - System health check
    - Returns: server status and feature availability
```

## 📈 Frontend Features

### 1. Prediction Panel
- Live prediction display (BUY/SELL/HOLD)
- Predicted price with confidence percentage
- Status indicator (Cached/Locked/Fresh)
- Market timing information
- Current price vs predicted price comparison

### 2. Accuracy Dashboard
- **Summary Stats**: Total predictions, accuracy %, direction accuracy, avg error
- **Prediction History Table**: Last 10 predictions with results
- **Color-Coded Results**: Green (correct), Red (wrong), Gray (pending)
- **Refresh Button**: Manual accuracy data reload

### 3. Interactive Charts
- Candlestick price charts
- Volume bar charts
- Multiple timeframes (1D, 5D, 1M, 3M, 1Y)
- Technical indicators overlay

### 4. Sentiment Analysis
- FinBERT sentiment scores
- Recent news articles
- Sentiment breakdown (Positive/Neutral/Negative)
- Article count and confidence

## 🔧 Configuration

Edit `config_dev.py` to customize:

```python
# Server Settings
HOST = '0.0.0.0'
PORT = 5001
DEBUG = True

# Prediction Settings
PREDICTION_CACHE_HOURS = 24  # Cache predictions for 24 hours
ENABLE_SCHEDULER = True      # Auto-validate at market close

# Market Hours (already configured for US/AU/UK)
# See market_timezones.py for details
```

## 🗄️ Database Schema

### Predictions Table (30 columns)
```sql
- prediction_id (Primary Key)
- symbol, prediction_date, target_date
- timeframe (DAILY_EOD, WEEKLY_EOD, etc.)
- prediction (BUY/SELL/HOLD)
- predicted_price, current_price, confidence
- LSTM/Trend/Technical components
- Sentiment data
- Actual outcomes (price, change, correctness)
- Status (ACTIVE/COMPLETED/EXPIRED)
```

### Accuracy Stats Table (23 columns)
```sql
- stat_id (Primary Key)
- symbol, timeframe, period
- total_predictions, correct_predictions
- Direction accuracy (BUY/SELL/HOLD rates)
- Price accuracy (RMSE, MAE, avg error)
- Confidence statistics
- Last updated timestamp
```

## 📝 Usage Examples

### Generate and View Prediction

```python
# In Python
import requests

# Get prediction for AAPL
response = requests.get('http://localhost:5001/api/predictions/AAPL')
data = response.json()

print(f"Symbol: {data['prediction']['symbol']}")
print(f"Prediction: {data['prediction']['prediction']}")
print(f"Price: ${data['prediction']['predicted_price']:.2f}")
print(f"Cached: {data['is_cached']}")
```

### Get Prediction History

```python
# Get 30-day history
response = requests.get('http://localhost:5001/api/predictions/AAPL/history?days=30')
data = response.json()

print(f"Total Predictions: {data['accuracy_summary']['total_predictions']}")
print(f"Accuracy: {data['accuracy_summary']['accuracy_percent']:.1f}%")

for pred in data['predictions'][:5]:
    print(f"{pred['prediction_date']}: {pred['prediction']} @ ${pred['predicted_price']:.2f}")
```

### Frontend Usage

1. **Open Browser**: Navigate to `http://localhost:5001`
2. **Enter Symbol**: Type stock symbol (e.g., AAPL, BHP.AX, BP.L)
3. **Click Analyze**: View prediction, charts, and sentiment
4. **Scroll Down**: See accuracy dashboard with history
5. **Refresh**: Click refresh button to update accuracy stats

## 🧪 Testing

### Test All Markets

```powershell
# Test US market
curl http://localhost:5001/api/predictions/AAPL

# Test AU market
curl http://localhost:5001/api/predictions/BHP.AX

# Test UK market
curl http://localhost:5001/api/predictions/BP.L

# Check scheduler
curl http://localhost:5001/api/predictions/scheduler/status
```

### Expected Results
- ✅ First request: `is_cached: false` (generates new prediction)
- ✅ Second request: `is_cached: true` (uses cached prediction)
- ✅ Scheduler: Shows 3 jobs (US, AU, UK validations)

## 🐛 Troubleshooting

### Issue: Predictions not caching
**Solution**: Check database file permissions and ensure `trading.db` is created

### Issue: Scheduler not running
**Solution**: Install APScheduler: `pip install apscheduler`

### Issue: Market detection wrong
**Solution**: Check symbol suffix (.AX for AU, .L for UK, none for US)

### Issue: Port 5001 already in use
**Solution**: Change PORT in `config_dev.py` or kill existing process

### Issue: Missing LSTM model
**Solution**: Train model: `python models/train_lstm.py --symbol AAPL --epochs 50`

## 📚 Documentation

- **MULTI_TIMEZONE_PREDICTIONS.md**: Complete technical documentation
- **INSTALLATION_GUIDE.md**: Detailed installation steps
- **models/README.md**: Model architecture details

## 🔄 Version History

### v4.0 - Prediction Caching System (November 2025)
- ✅ Multi-timezone support (US/AU/UK)
- ✅ Prediction caching in SQLite database
- ✅ Automated scheduler for validation
- ✅ Frontend accuracy dashboard
- ✅ Prediction locking at market open
- ✅ Historical accuracy tracking

### v3.3 - Enhanced Sentiment Analysis
- FinBERT sentiment integration
- Real-time news article analysis
- Improved ensemble predictions

### v3.2 - Technical Analysis
- LSTM neural network predictor
- Advanced technical indicators
- Volume analysis

## 👥 Support

For issues, questions, or feature requests:
- Check troubleshooting section above
- Review documentation files
- Test with provided examples

## 📄 License

This software is provided as-is for trading analysis purposes.
Not financial advice. Use at your own risk.

---

**Built with ❤️ for Windows 11**

**Last Updated**: November 3, 2025
**Version**: 4.0.0
**Status**: Production Ready ✅
