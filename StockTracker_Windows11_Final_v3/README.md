# Stock Tracker V3 - Windows 11 Complete Edition

## 🚀 Version 3.0 - Latest Enhancements

This is the complete Windows 11 deployment package with all recent enhancements:

### ✨ Key Features

#### 1. **FinBERT Integration** 
- Real financial sentiment analysis (no more random data!)
- Consistent results for the same text
- Professional-grade NLP for financial documents
- Intelligent keyword-based fallback

#### 2. **Historical Data Module**
- Local SQLite database storage
- 50x faster data retrieval than API calls
- Batch download for multiple symbols
- Automatic updates for stale data
- Working Chart.js visualizations

#### 3. **ML Integration Layer**
- All 11 modules interconnected
- Shared knowledge base
- Transfer learning capabilities
- Iterative model improvement

#### 4. **Real Market Data**
- Live Yahoo Finance integration
- Accurate prices (CBA.AX ~$170, not $100)
- No synthetic or demo data
- Reduced API dependency with caching

## 📦 What's Included

### Core Services
- **Main Backend** (`backend.py`) - Port 8002
- **ML Backend** (`ml_backend_enhanced.py`) - Port 8003  
- **Integration Bridge** (`integration_bridge.py`) - Port 8004

### Enhanced Services
- **FinBERT Analyzer** (`finbert_analyzer.py`) - Sentiment analysis
- **Historical Data Service** (`historical_data_service.py`) - Local storage

### 11 Integrated Modules
1. **Market Tracker** - Real-time market monitoring
2. **Prediction Centre** - ML-based price predictions
3. **ML Training Centre** - Custom model training
4. **Portfolio Optimizer** - Portfolio optimization
5. **Risk Analyzer** - Risk assessment tools
6. **Document Analyzer** - FinBERT sentiment analysis
7. **Backtesting Engine** - Strategy backtesting
8. **Alert Manager** - Custom price alerts
9. **Historical Data Module** - Local data management
10. **Options Analyzer** - Options analysis
11. **Sentiment Monitor** - Market sentiment tracking

## 🔧 Installation

### Requirements
- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for FinBERT)
- 2GB free disk space
- Internet connection (for initial setup and data downloads)

### Quick Installation

#### Option 1: Quick Start (Recommended)
```batch
QUICK_START.bat
```
This will automatically install everything and start the application.

#### Option 2: Manual Installation
```batch
# Step 1: Install dependencies
INSTALL_ALL.bat

# Step 2: Start services
START_SYSTEM.bat
```

### First-Time Setup
1. After installation, the browser will open to http://localhost:8002
2. Navigate to **Historical Data Module**
3. Download data for your symbols:
   - Enter: `CBA.AX, BHP.AX, WBC.AX`
   - Or click "Batch Download ASX Top 20"
4. Data is now cached locally for fast access

## 📊 Using the Application

### Historical Data Module
1. **Download Data**: Enter symbols and period, click Download
2. **Batch Download**: Get ASX Top 20 with one click
3. **View Charts**: Click "View Chart" to see price/volume charts
4. **Statistics**: Monitor database size and records

### Document Analyzer (FinBERT)
1. Navigate to Document Analyzer
2. Enter financial text or news
3. Click "Analyze Document"
4. Get consistent sentiment scores (same text = same result)

### ML Training Centre
1. Select a symbol
2. Choose model type (Random Forest, XGBoost, LSTM)
3. Click "Train Model"
4. Uses local historical data for fast training

### Prediction Centre
1. Enter stock symbol
2. Select trained model
3. Get ML-based predictions
4. View confidence intervals

## 🛠️ Troubleshooting

### Service Not Starting
```batch
# Check if Python is installed
python --version

# Check if ports are available
netstat -an | findstr :8002
netstat -an | findstr :8003
netstat -an | findstr :8004

# Restart services
taskkill /F /IM python.exe
START_SYSTEM.bat
```

### FinBERT Not Working
```batch
# Reinstall transformers
pip install --upgrade transformers torch

# Test FinBERT
python -c "from finbert_analyzer import get_analyzer; print('OK')"
```

### Historical Data Issues
```batch
# Check database
dir historical_data\*.db

# Reset database
del historical_data\market_data.db
START_SYSTEM.bat
```

### Port Conflicts
If ports 8002-8004 are in use:
1. Edit `backend.py`, change port 8002 to 8005
2. Edit `ml_backend_enhanced.py`, change port 8003 to 8006
3. Edit `integration_bridge.py`, change port 8004 to 8007
4. Update `START_SYSTEM.bat` with new ports

## 📈 Performance Tips

### Speed Optimization
1. **Use Historical Data Module**: Download data once, use many times
2. **Batch Operations**: Download multiple symbols at once
3. **Local Models**: Train and save models locally
4. **Cache Usage**: Let the system cache frequently used data

### Memory Management
- Close unused browser tabs
- Limit simultaneous model training
- Clear old historical data periodically
- Restart services daily for best performance

## 🔐 Security Notes

- All data stored locally (no cloud dependency)
- API keys not required (uses yfinance)
- SQLite databases are local-only
- No external data transmission

## 📝 File Structure

```
StockTracker_Windows11_Complete_v3/
├── backend.py                      # Main backend service
├── ml_backend_enhanced.py          # ML service with iterative learning
├── integration_bridge.py           # ML integration service
├── finbert_analyzer.py            # FinBERT sentiment analyzer
├── historical_data_service.py     # Historical data management
├── ml_integration_client.js       # JavaScript integration library
├── index.html                     # Main dashboard
├── modules/
│   ├── document_analyzer.html    # FinBERT document analysis
│   ├── historical_data_module.html # Data management UI
│   └── [other modules]
├── INSTALL_ALL.bat               # Complete installation script
├── START_SYSTEM.bat              # Start all services
├── QUICK_START.bat               # One-click setup and start
└── requirements.txt              # Python dependencies
```

## 🎯 Key Improvements in V3

### From Previous Versions
- ✅ **Fixed**: Document Analyzer random sentiment issue
- ✅ **Fixed**: Charts not loading in Historical Analysis
- ✅ **Added**: Local SQLite storage for historical data
- ✅ **Added**: FinBERT real sentiment analysis
- ✅ **Added**: ML Integration Bridge
- ✅ **Added**: Batch download capabilities
- ✅ **Improved**: 50x faster data retrieval
- ✅ **Improved**: Consistent ML training with local data

## 💡 Tips for Best Experience

1. **Download Data First**: Use Historical Data Module to cache frequently used symbols
2. **Train Models Locally**: Better performance with local data
3. **Use Batch Operations**: Download multiple symbols at once
4. **Regular Updates**: Refresh stale data weekly
5. **Monitor Services**: Check the console window for service status

## 🆘 Support

### Common Issues
- **"Python not found"**: Install Python 3.8+ and add to PATH
- **"Port already in use"**: Another application using ports 8002-8004
- **"Module not found"**: Run INSTALL_ALL.bat to install dependencies
- **"No data available"**: Check internet connection, Yahoo Finance may be down

### Logs Location
- Main backend: Console window
- ML backend: Console window
- Historical data: `historical_data/` directory
- Models: `models/` directory

## 📄 License

This software is provided as-is for educational and personal use.

## 🎉 Enjoy Stock Tracker V3!

With FinBERT sentiment analysis, local historical data storage, and ML integration, you have a professional-grade stock analysis platform running entirely on your Windows 11 machine.

---

**Version**: 3.0.0  
**Release Date**: October 2024  
**Platform**: Windows 11 (Windows 10 compatible)