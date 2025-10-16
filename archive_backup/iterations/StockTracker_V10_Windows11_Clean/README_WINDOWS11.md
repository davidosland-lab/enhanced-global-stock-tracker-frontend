# Stock Tracker Enhanced - Windows 11 Edition
## Real ML + Global Sentiment Analysis + FinBERT

### ✨ Key Features
- **Real FinBERT Sentiment Analysis** - No fake data, actual transformer-based financial sentiment
- **Global Sentiment Integration** - Politics, wars, economic indicators, government reports
- **SQLite Caching** - 50x faster data retrieval and ML training
- **Multiple ML Models** - RandomForest, GradientBoost, XGBoost
- **$100,000 Backtesting** - Realistic trading simulation with commission and slippage
- **Enhanced Web Scraping** - Multiple sources including global news and market data
- **NO FAKE DATA** - All real market data from Yahoo Finance and live news sources

### 📋 Requirements
- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for FinBERT)
- 2GB free disk space
- Internet connection for real-time data

### 🚀 Quick Installation

1. **Extract the package** to a folder on your Windows 11 machine (e.g., `C:\StockTracker`)

2. **Run the installer:**
   ```batch
   INSTALL_WINDOWS11.bat
   ```
   This will:
   - Check Python installation
   - Create virtual environment
   - Install all required packages
   - Download FinBERT model
   - Set up databases and configuration

3. **Start all services:**
   ```batch
   START_ALL_SERVICES.bat
   ```
   This launches all 6 microservices:
   - Main Backend (Port 8000)
   - ML Backend with FinBERT (Port 8002)
   - Document Analyzer (Port 8003)
   - Historical Data Service (Port 8004)
   - Backtesting Service (Port 8005)
   - Global Sentiment Scraper (Port 8006)

4. **Access the application:**
   - Browser will auto-open to: http://localhost:8000/prediction_center_fixed.html
   - Or manually navigate to: http://localhost:8000

### 📁 Project Structure
```
StockTracker_V10_Windows11_Clean/
├── INSTALL_WINDOWS11.bat          # One-click installer
├── START_ALL_SERVICES.bat         # Start all services
├── STOP_ALL_SERVICES.bat          # Stop all services
├── requirements.txt               # Python dependencies
│
├── main_backend_integrated.py     # Main orchestrator service
├── ml_backend_enhanced_finbert.py # ML with FinBERT integration
├── enhanced_global_scraper.py     # Global news & sentiment
├── historical_backend_sqlite.py   # Fast cached historical data
├── backtesting_enhanced.py        # $100k backtesting engine
├── finbert_backend.py             # Document analysis
│
├── prediction_center_fixed.html   # Main UI interface
├── index.html                     # Dashboard
│
├── models/                        # Trained ML models
├── cache/                         # SQLite cache files
└── data/                          # Data storage
```

### 🎯 How to Use

#### Training a Model
1. Enter a stock symbol (e.g., AAPL)
2. Select model type (RandomForest, GradientBoost, or XGBoost)
3. Click "Train" - takes 10-60 seconds for real training
4. View accuracy metrics and feature importance

#### Making Predictions
1. Enter stock symbol
2. Choose prediction days (1-30)
3. Click "Predict"
4. View:
   - Price predictions with confidence scores
   - Global sentiment analysis (politics, wars, economics)
   - Market risk assessment
   - Technical indicators
   - Buy/Sell/Hold recommendations

#### Running Backtests
1. Select strategy:
   - ML + Sentiment (uses predictions and news)
   - Momentum
   - Mean Reversion
   - Buy & Hold
2. Set initial capital ($100,000 default)
3. Click "Run Backtest"
4. View performance metrics:
   - Total return
   - Sharpe ratio
   - Win rate
   - Maximum drawdown

### 🔧 Configuration

Edit `config.json` to customize:
- Service ports
- Cache duration
- Initial capital
- Database paths

### 📊 Service Endpoints

| Service | Port | Description |
|---------|------|-------------|
| Main API | 8000 | Central orchestrator |
| ML Backend | 8002 | Predictions & training |
| Document Analyzer | 8003 | FinBERT analysis |
| Historical Data | 8004 | Cached market data |
| Backtesting | 8005 | Strategy testing |
| Web Scraper | 8006 | Global sentiment |

### 🌍 Global Sentiment Sources
- **Reuters** - Global politics
- **BBC World** - International news
- **Federal Reserve** - Economic policy
- **ECB** - European economics
- **IMF/World Bank** - Global economic indicators
- **UN News** - Geopolitical events
- **Bloomberg/FT** - Market news
- **Reddit** - Social sentiment

### 🧠 ML Features
- **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Sentiment Features**: FinBERT scores, global sentiment, market risk
- **Price Features**: Returns, volatility, volume patterns
- **Pattern Recognition**: Support/resistance, chart patterns

### ⚡ Performance
- **SQLite Caching**: 50x faster than API calls
- **Real Training Time**: 10-60 seconds (not fake)
- **Concurrent Processing**: All services run in parallel
- **Optimized Queries**: Indexed databases for speed

### 🛠️ Troubleshooting

#### Services won't start
- Check Python version: `python --version` (need 3.8+)
- Run as Administrator if needed
- Check firewall isn't blocking ports 8000-8006

#### FinBERT not working
- First run downloads the model (~400MB)
- Requires internet connection for download
- Check transformers installed: `pip show transformers`

#### Slow performance
- Enable SQLite cache in settings
- Close other applications
- Ensure 4GB+ RAM available

#### Port conflicts
- Edit service files to change ports
- Update config.json with new ports
- Restart all services

### 📝 Support Commands

**Check service status:**
```batch
curl http://localhost:8000/api/services/status
```

**Clear cache:**
```batch
curl -X DELETE http://localhost:8004/cache
```

**View logs:**
Check console windows for each service

### 🚫 NO FAKE DATA
This system uses:
- **Real market data** from Yahoo Finance
- **Live news** from actual news sources
- **Real ML training** (10-60 seconds)
- **Actual FinBERT model** from HuggingFace
- **True backtesting** with realistic commission/slippage

### 📄 License
MIT License - Free for personal and commercial use

### 🤝 Credits
- FinBERT by ProsusAI
- Market data from Yahoo Finance
- News from various public APIs
- Built for Windows 11 local deployment

---

**Version**: 3.0 Enhanced
**Last Updated**: October 2024
**Deployment**: Windows 11 Local (Not cloud/sandbox)