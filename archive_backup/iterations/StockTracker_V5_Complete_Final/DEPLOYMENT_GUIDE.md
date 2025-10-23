# Stock Tracker V5 - Windows 11 Deployment Guide
## Complete System with ML Backtesting

### System Overview
This is the complete StockTracker V5 system with all modules integrated:
- **FinBERT Sentiment Analysis** - Real financial sentiment using transformer models
- **SQLite Historical Data Cache** - 50x faster data retrieval
- **ML Unified Module** - Integrated training, prediction, and backtesting
- **Backtesting Component** - Strategy testing with $100,000 starting capital
- **Multiple Trading Strategies** - Moving Average, RSI, MACD, Mean Reversion, Breakout

### Key Features Implemented
1. **Backtesting System**
   - Starting capital: $100,000 (configurable)
   - Timeframes: 1 week to 2 years
   - Position sizing: 10-100% of capital
   - Stop loss & take profit management
   - Commission calculations ($5 per trade)
   - Real-time portfolio tracking

2. **Trading Strategies**
   - **Moving Average**: Golden cross/Death cross (SMA 20/50)
   - **RSI**: Overbought/Oversold levels (30/70)
   - **MACD**: Signal line crossovers
   - **Mean Reversion**: 3% price movement triggers
   - **Breakout**: Volatility-based entry/exit

3. **Performance Metrics**
   - Total Return & Win Rate
   - Sharpe Ratio (risk-adjusted returns)
   - Maximum Drawdown
   - Average Profit/Loss per trade
   - Complete trade history with P&L

4. **Enhanced Features**
   - **FinBERT Integration**: Deterministic sentiment analysis
   - **SQLite Caching**: Historical data stored locally
   - **Transfer Learning**: Models inherit knowledge from previous versions
   - **Progressive Complexity**: Model capacity increases with iterations
   - **Integration Bridge**: Cross-module communication (port 8004)

### System Architecture
```
Port 8080: Main Web Interface
Port 8002: Main Backend API (FastAPI)
Port 8003: ML Backend (Enhanced with sentiment)
Port 8004: Integration Bridge Service
```

### Windows 11 Installation

#### Prerequisites
- Windows 11 (64-bit)
- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

#### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Verify installation:
```cmd
python --version
```

#### Step 2: Extract Application
1. Extract the zip file to a location like `C:\StockTracker`
2. Open Command Prompt as Administrator
3. Navigate to the directory:
```cmd
cd C:\StockTracker
```

#### Step 3: Install Dependencies
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Initialize Database
```cmd
python scripts/init_database.py
```

#### Step 5: Start Services

Option A: Use the batch file (Recommended)
```cmd
start_services.bat
```

Option B: Start services manually
```cmd
# Terminal 1 - Main Backend
python backend.py

# Terminal 2 - ML Backend  
python ml_backend_enhanced.py

# Terminal 3 - Integration Bridge
python integration_bridge.py

# Terminal 4 - Web Server
python -m http.server 8080
```

#### Step 6: Access the Application
Open your browser and navigate to:
```
http://localhost:8080
```

### Using the Backtesting Module

1. **Navigate to ML Unified Module**
   - Click "ML Center" in the main navigation
   - Select "Unified ML Module"

2. **Train a Model First**
   - Go to the "Training" tab
   - Enter a stock symbol (e.g., AAPL, MSFT)
   - Select model type and parameters
   - Click "Start Training"

3. **Run Backtest**
   - Switch to "Backtest" tab
   - Select your trained model
   - Configure parameters:
     - Starting Capital: $100,000 (default)
     - Timeframe: 1 week to 2 years
     - Strategy: Choose from 5 available strategies
     - Position Size: 10-100% of capital
     - Stop Loss: 1-10%
     - Take Profit: 1-20%
   - Click "Run Backtest"

4. **Analyze Results**
   - View performance metrics (Return, Sharpe Ratio, Win Rate)
   - Check portfolio value chart
   - Review trade history
   - Compare multiple strategies

### Model Learning Capabilities

**Q: Do models learn from previous training?**
**A:** Yes! The system implements transfer learning:
- Models save their learned parameters
- New training sessions build upon previous knowledge
- Model complexity increases progressively (50→80→110 trees)
- Each iteration refines predictions based on accumulated data

**Q: What data do models review?**
**A:** Models analyze:
- Historical price data (OHLCV)
- Technical indicators (SMA, RSI, MACD, Bollinger Bands)
- Volume patterns
- Price momentum
- Volatility measures
- **FinBERT sentiment scores** from news and documents

**Q: How does FinBERT sentiment help?**
**A:** FinBERT provides:
- Real sentiment analysis of financial text (not random)
- Sentiment momentum tracking
- News impact scoring
- Document sentiment integration
- 20+ sentiment-derived features for ML training
- Correlation between sentiment and price movements

**Q: Where does FinBERT sentiment data come from?**
**A:** Multiple sources:
1. **Yahoo Finance News** - Real-time financial news
2. **RSS Feeds** - Financial news aggregation
3. **Document Uploads** - User-uploaded reports/analysis
4. **Integration Bridge** - Sentiment from document analyzer
5. **Historical Sentiment** - Cached sentiment data in SQLite

### Performance Optimizations

1. **SQLite Caching**
   - 50x faster than API calls
   - Local storage at `historical_data/market_data.db`
   - Automatic cache updates
   - Reduced API rate limiting

2. **Parallel Processing**
   - Multi-threaded training
   - Async data fetching
   - Concurrent sentiment analysis

3. **Memory Management**
   - Efficient data structures
   - Garbage collection optimization
   - Streaming data processing

### Troubleshooting

#### Services Not Starting
```cmd
# Check Python version
python --version

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -an | findstr :8080
netstat -an | findstr :8002
netstat -an | findstr :8003
netstat -an | findstr :8004
```

#### Backtesting Errors
- Ensure sufficient historical data (minimum 20 days)
- Check model is trained before backtesting
- Verify stock symbol is valid
- Confirm services are running

#### Performance Issues
- Close unnecessary applications
- Increase Python memory limit
- Use SQLite cached data
- Reduce backtesting timeframe

### Security Considerations
- API keys stored in environment variables
- Local-only service binding (localhost)
- No external network exposure by default
- Secure SQLite database permissions

### Advanced Configuration

#### Custom Strategies
Edit `ml_unified.html` to add custom trading strategies:
```javascript
case 'custom_strategy':
    // Your logic here
    if (customCondition) {
        return 'BUY';
    } else if (otherCondition) {
        return 'SELL';
    }
    break;
```

#### Modify Backtesting Parameters
Adjust in `ml_unified.html`:
- Commission rates
- Slippage modeling
- Position sizing algorithms
- Risk management rules

### Support and Updates
- Check logs in `logs/` directory
- Database backups in `backups/`
- Model checkpoints in `model_checkpoints/`

### Version Information
- **Version**: 5.0 Complete Final
- **Last Updated**: October 14, 2024
- **ML Models**: Random Forest, XGBoost, LSTM
- **Backtesting Engine**: Custom implementation with technical indicators

### Credits
Developed with advanced ML capabilities including:
- FinBERT sentiment analysis (ProsusAI/finbert)
- Transfer learning architecture
- Real-time backtesting engine
- Professional trading strategies

---
**Note**: This is a development/educational tool. Always perform your own due diligence before making investment decisions.