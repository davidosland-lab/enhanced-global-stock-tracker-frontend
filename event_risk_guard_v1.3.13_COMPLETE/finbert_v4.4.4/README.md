# FinBERT v4.4 - Complete Stock Prediction Platform

## 🚀 Overview

FinBERT v4.4 is a comprehensive stock market prediction platform that combines machine learning models with practical trading tools. This deployment package includes **ALL 5 PHASES** fully functional and tested.

### Key Features

- **4-Model Ensemble Prediction System**
  - LSTM Neural Network (45% weight)
  - Trend Analysis Model (25% weight)
  - Technical Indicators Model (15% weight)
  - FinBERT Sentiment Analysis (15% weight)

- **Paper Trading System** - Virtual $10,000 account for risk-free trading
- **Backtesting Engine** - Test strategies on historical data
- **Portfolio Analysis** - Multi-stock portfolio backtesting with correlation analysis
- **Parameter Optimization** - Grid and random search optimization
- **Prediction Hold System** - Multi-timezone support with automated validation

## 📋 System Requirements

- **Operating System**: Windows 11 (or Windows 10)
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended for TensorFlow)
- **Disk Space**: 5GB for dependencies
- **Internet**: Required for package installation and market data
- **Browser**: Chrome, Edge, or Firefox (latest version)

## 🔧 Installation

### Step 1: Extract Files

Extract the ZIP file to your preferred location (e.g., `C:\FinBERT`)

### Step 2: Run Installer

Double-click `INSTALL.bat`

The installer will:
1. Check Python installation
2. Create virtual environment
3. Install all dependencies from requirements.txt
4. Create necessary directories
5. Verify installation

**Installation time**: 5-20 minutes (depending on internet speed)

### Step 3: Verify Installation

Run `VERIFY_INSTALL.bat` to check all components are properly installed.

If you see any `[ERROR]` messages, refer to the Troubleshooting section below.

## 🎯 Quick Start

1. **Start the Server**
   - Double-click `START_FINBERT.bat`
   - Wait for "Running on http://127.0.0.1:5002" message
   - Keep the terminal window open

2. **Open Web Interface**
   - Open your browser
   - Navigate to: `http://localhost:5002`

3. **Get Your First Prediction**
   - Enter a stock symbol (e.g., `AAPL`, `TSLA`, `SPY`)
   - Click "Get Prediction"
   - View the ensemble prediction with technical indicators and sentiment

## 📚 Using the Features

### 1. Stock Predictions

**Input**: Stock symbol (e.g., AAPL, TSLA, GOOGL)

**Output**:
- Ensemble prediction (UP/DOWN/NEUTRAL)
- Individual model predictions
- Technical indicators (RSI, MACD, Bollinger Bands)
- FinBERT sentiment analysis from recent news
- Confidence scores

**Use Case**: Get AI-powered predictions for next trading day

### 2. Paper Trading

**Access**: Click "Paper Trading" button at top of page

**Features**:
- Start with $10,000 virtual capital
- Place market or limit orders
- Track positions with real-time P&L
- View order history
- Close positions anytime

**Use Case**: Practice trading without risk

### 3. Strategy Backtesting

**Access**: Click "Backtest" button

**Input**:
- Stock symbol
- Date range (start/end dates)
- Initial capital
- Commission rate

**Output**:
- Total return and annualized return
- Sharpe ratio and max drawdown
- Win rate and profit factor
- Equity curve visualization
- Complete trade log

**Use Case**: Test how the strategy would have performed historically

### 4. Portfolio Backtesting

**Access**: Click "Portfolio Backtest" button

**Input**:
- Multiple symbols (comma-separated: AAPL,MSFT,GOOGL)
- Date range
- Initial capital per stock
- Equal or custom allocation

**Output**:
- Portfolio-level metrics
- Individual stock performance
- Correlation matrix heatmap
- Combined equity curve

**Use Case**: Test diversified portfolio performance

### 5. Parameter Optimization

**Access**: Click "Optimize" button

**Input**:
- Stock symbol
- Date range
- Optimization method (grid/random)
- Number of iterations

**Output**:
- Top 10 parameter configurations
- Performance metrics for each
- Best performing parameters

**Use Case**: Find optimal strategy parameters for a specific stock

### 6. Prediction History

**Access**: Click "Prediction History" button

**Input**:
- Stock symbol
- Date range

**Output**:
- All historical predictions
- Actual market outcomes
- Accuracy comparison
- Prediction vs actual visualization

**Use Case**: Analyze model accuracy over time

## 🌍 Multi-Timezone Support

FinBERT supports predictions for **3 major markets**:

### US Market (e.g., AAPL, TSLA, MSFT)
- **Trading Hours**: 9:30 AM - 4:00 PM Eastern Time
- **Prediction Lock**: 8:00 AM Eastern (90 min before open)
- **Auto-Validation**: 4:15 PM Eastern (15 min after close)

### Australian Market (e.g., CBA.AX, BHP.AX, WBC.AX)
- **Trading Hours**: 10:00 AM - 4:00 PM Sydney Time
- **Prediction Lock**: 8:30 AM Sydney
- **Auto-Validation**: 4:15 PM Sydney

### UK Market (e.g., BARC.L, BP.L, LLOY.L)
- **Trading Hours**: 8:00 AM - 4:30 PM London Time
- **Prediction Lock**: 6:30 AM London
- **Auto-Validation**: 4:45 PM London

**Prediction Locking**: Once the market opens, predictions are locked to ensure consistency. This prevents generating different predictions throughout the trading day.

**Automated Validation**: At market close, the system automatically validates predictions against actual outcomes and stores results in the database for analysis.

## 🛠️ Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'flask_cors'

**Solution**: Run `FIX_FLASK_CORS.bat`

This installs the missing Flask-CORS package.

**Root Cause**: Earlier versions of INSTALL.bat had a bug where dependencies were hardcoded instead of reading from requirements.txt. This has been fixed in v4.4.

#### 2. Server won't start

**Diagnosis**:
1. Run `VERIFY_INSTALL.bat` to check setup
2. Check if another program is using port 5002
3. Verify Python 3.8+ is installed: `python --version`

**Solution**:
- If port conflict: Edit `config_dev.py` and change the port number
- If Python not found: Install Python from https://www.python.org/
- If packages missing: Re-run `INSTALL.bat`

#### 3. Can't get predictions

**Possible Causes**:
- No internet connection (needs to fetch market data)
- Invalid stock symbol
- Market data not available for the symbol

**Solution**:
1. Check internet connection
2. Verify symbol exists on Yahoo Finance
3. Try a well-known symbol like AAPL to test

#### 4. Installation takes too long

**This is normal!**

- TensorFlow and PyTorch are large packages (1-2 GB)
- Installation can take 10-20 minutes on slow connections
- Optional packages (TensorFlow, PyTorch, Transformers) can be skipped if only basic features are needed

#### 5. ImportError or dependency conflicts

**Solution**:
1. Delete the `venv` folder
2. Re-run `INSTALL.bat`
3. This creates a fresh virtual environment

### Getting Help

1. Check `TROUBLESHOOTING_FLASK_CORS.md` for detailed diagnostics
2. Review `ROOT_CAUSE_ANALYSIS.md` for known issues
3. Run `VERIFY_INSTALL.bat` to diagnose your setup

## 📊 Database Storage

FinBERT stores data in two SQLite databases:

### 1. trading.db (Paper Trading)

**Tables**:
- `trades` - Order history
- `positions` - Current positions
- `account` - Account balance

**Location**: Created automatically in the application directory

### 2. predictions.db (Prediction History)

**Tables**:
- `predictions` - All predictions with 42 columns including:
  - Prediction details (symbol, date, direction, confidence)
  - All 4 model predictions
  - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
  - Sentiment scores
  - Actual outcomes for validation

**Location**: Created automatically in the application directory

## 🔍 API Endpoints

FinBERT provides RESTful APIs for integration:

### Prediction APIs

- `GET /api/predictions/<symbol>` - Get latest prediction
- `GET /api/predictions/<symbol>/history` - Get prediction history
- `POST /api/predictions/validate` - Trigger validation

### Paper Trading APIs

- `GET /api/trading/account` - Get account info
- `POST /api/trading/orders` - Place order
- `GET /api/trading/positions` - Get positions
- `POST /api/trading/positions/<symbol>/close` - Close position
- `GET /api/trading/orders/history` - Get order history

### Backtesting APIs

- `POST /api/backtest/run` - Run single stock backtest
- `POST /api/backtest/portfolio` - Run portfolio backtest
- `POST /api/backtest/optimize` - Run parameter optimization

## 🎓 Advanced Usage

### Running on Different Port

1. Open `config_dev.py`
2. Find: `app.run(port=5002)`
3. Change to your desired port
4. Restart server

### Training Custom Models

The LSTM training component is included but requires:
- TensorFlow/Keras installation
- 16GB+ RAM recommended
- Historical data for training

**Note**: Training integration UI will be added in the next phase.

### Using with Real-Time Data

- FinBERT uses yfinance (Yahoo Finance) for market data
- Data is typically delayed 15-20 minutes
- For real-time data, consider upgrading to paid data feeds

### Customizing Predictions

Edit `config_dev.py` to customize:
- Model weights (default: LSTM 45%, Trend 25%, Technical 15%, Sentiment 15%)
- Confidence thresholds
- Trading parameters (stop-loss, take-profit)

## 📈 Performance Metrics

### Backtesting Metrics Explained

- **Total Return**: Overall % gain/loss
- **Annualized Return**: Return normalized to per-year basis
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: % of profitable trades
- **Profit Factor**: Gross profit / Gross loss ratio

### Portfolio Metrics

- **Portfolio Return**: Combined return across all stocks
- **Correlation Matrix**: Shows diversification effectiveness
- **Individual Performance**: Per-stock metrics
- **Risk Metrics**: Portfolio-level risk indicators

## 🔐 Security Notes

- **Paper Trading Only**: This system is for simulation only
- **No Real Money**: No integration with real brokerage accounts
- **Data Privacy**: All data stored locally in SQLite databases
- **API Keys**: No API keys required for basic functionality

## 📦 What's Included

```
FinBERT_v4.4_COMPLETE_DEPLOYMENT/
├── Startup Scripts
│   ├── INSTALL.bat ...................... One-time setup installer
│   ├── START_FINBERT.bat ................ Server startup
│   ├── FIX_FLASK_CORS.bat ............... Emergency flask-cors fix
│   └── VERIFY_INSTALL.bat ............... Installation checker
│
├── Application Files
│   ├── app_finbert_v4_dev.py ............ Main Flask application
│   ├── config_dev.py .................... Configuration
│   └── requirements.txt ................. Python dependencies
│
├── Backend Modules
│   └── models/
│       ├── backtesting/ ................. Backtesting framework
│       ├── trading/ ..................... Paper trading system
│       ├── market_timezones.py .......... Multi-timezone support
│       ├── prediction_manager.py ........ Prediction orchestration
│       └── prediction_scheduler.py ...... Automated validation
│
├── Frontend
│   └── templates/
│       └── finbert_v4_enhanced_ui.html .. Complete UI with 5 modals
│
└── Documentation
    ├── README.md ........................ This file
    ├── QUICK_START.txt .................. Quick start guide
    ├── VERSION.txt ...................... Version information
    ├── ALL_PHASES_COMPLETE.md ........... Detailed phase documentation
    ├── PREDICTION_HOLD_SYSTEM_COMPLETE.md  Multi-timezone guide
    ├── TROUBLESHOOTING_FLASK_CORS.md .... Flask-CORS troubleshooting
    └── ROOT_CAUSE_ANALYSIS.md ........... Known issues analysis
```

## 🚀 Next Steps

1. **Get Familiar**: Try all 5 features with different stocks
2. **Run Backtests**: Test the strategy on historical data
3. **Paper Trade**: Practice trading without risk
4. **Optimize**: Find the best parameters for your favorite stocks
5. **Analyze**: Review prediction history to understand model accuracy

## 📝 Version History

### v4.4.0 (November 5, 2025) - CURRENT

- ✅ All 5 phases complete and fully functional
- ✅ Fixed INSTALL.bat to use requirements.txt correctly
- ✅ Fixed LSTM training script
- ✅ Multi-timezone support (US, AU, UK)
- ✅ Automated prediction validation
- ✅ Complete deployment package for Windows 11

### What's Next

- Training component UI integration
- Real-time data feed integration
- Additional ML models
- Mobile-responsive design improvements

## 📞 Support

For issues:
1. Run `VERIFY_INSTALL.bat`
2. Check `TROUBLESHOOTING_FLASK_CORS.md`
3. Review `ROOT_CAUSE_ANALYSIS.md`

## ⚖️ License & Disclaimer

**Educational Purpose Only**

This software is provided for educational and research purposes only. It is NOT intended for real trading or investment decisions.

**No Financial Advice**: The predictions generated by this system are not financial advice. Past performance does not guarantee future results.

**No Warranty**: This software is provided "as is" without warranty of any kind.

**Use at Your Own Risk**: The developers are not responsible for any financial losses incurred from using this software.

---

**FinBERT v4.4** - Built with Flask, TensorFlow, FinBERT, and ❤️
