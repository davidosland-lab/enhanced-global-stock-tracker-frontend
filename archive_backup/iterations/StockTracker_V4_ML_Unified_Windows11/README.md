# Stock Tracker v4.0 - ML Integrated Edition

## 🚀 Overview
Advanced stock market analysis platform with integrated machine learning, real-time predictions, and cross-module learning capabilities through the ML Integration Bridge.

## 🎯 Key Features
- **ML Integration Bridge**: Connects all modules for cross-module learning (Port 8004)
- **FinBERT Sentiment Analysis**: Deterministic financial document analysis
- **SQLite Historical Data**: 50x faster data retrieval with local caching
- **Iterative Learning**: ML models improve over time with transfer learning
- **Real-time Predictions**: Multiple ML models (LSTM, Random Forest, XGBoost, ARIMA)
- **150+ Technical Indicators**: Comprehensive technical analysis
- **Global Market Tracking**: Real-time tracking of major indices

## 📋 Requirements
- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for ML training)
- Internet connection for real-time data

## 🔧 Installation

### Quick Start
1. Double-click `START_ALL_SERVICES.bat` to start all services
2. The dashboard will open automatically in your browser
3. All dependencies will be installed automatically

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start services individually
cd backend
python backend.py          # Main backend (Port 8002)
python ml_backend.py        # ML backend (Port 8003)
python integration_bridge.py # Integration bridge (Port 8004)
```

## 🏗️ Architecture

### Service Ports
- **8002**: Main Backend - Core API and data services
- **8003**: ML Backend - Machine learning models and predictions
- **8004**: Integration Bridge - Cross-module communication and learning

### Module Integration Flow
```
Document Analyzer ─┐
Historical Data ───┼─→ Integration Bridge ─→ ML Backend
Market Tracker ────┼        (Port 8004)       (Port 8003)
Technical Analysis ┘              ↓
                          Pattern Discovery
                          Model Improvement
                          Shared Learning
```

## 📦 Core Modules

### ⭐ Unified ML Centre (RECOMMENDED)
**The all-in-one solution for ML training and prediction**
- **Single Interface**: Train models and generate predictions in one place
- **No Sync Issues**: Models are immediately available after training
- **Persistent Storage**: Models saved to localStorage and ML backend
- **Three Tabs**:
  - **Training Tab**: Configure and train ML models
  - **Prediction Tab**: Use trained models for predictions  
  - **Models Tab**: View and manage all trained models
- **Real-time Updates**: See training progress and results instantly
- **Performance Comparison**: Compare accuracy across models

### 1. ML Training Centre (Standalone)
- Train multiple ML models simultaneously
- Transfer learning and model versioning
- Real-time backtesting
- Performance metrics tracking

### 2. Prediction Centre (ML Connected)
- Real-time predictions from ML backend
- Multiple model support
- Performance tracking
- Historical accuracy analysis

### 3. Document Analyzer
- FinBERT transformer for sentiment analysis
- Deterministic scoring (no randomness)
- Supports 100MB files
- Automatic sentiment forwarding to ML

### 4. Historical Data Manager
- SQLite local caching for 50x faster access
- Pattern discovery and analysis
- Chart.js visualizations
- Automatic pattern sharing via bridge

### 5. Technical Analysis
- 150+ technical indicators
- Real Yahoo Finance data
- Pattern recognition
- ML prediction overlay

### 6. Global Market Tracker
- Real-time global indices
- Market movers detection
- Volume spike alerts
- Sector analysis

## 🔗 ML Integration Bridge

The Integration Bridge (Port 8004) enables:
- **Cross-Module Learning**: Modules share patterns and insights
- **Pattern Discovery**: Automatic detection of significant patterns
- **ML Feedback**: ML models provide recommendations back to modules
- **Event Processing**: Real-time processing of market events
- **Knowledge Building**: Continuous improvement of ML models

### Bridge Endpoints
- `POST /api/bridge/document-sentiment`: Forward document sentiment
- `POST /api/bridge/historical-pattern`: Share discovered patterns
- `POST /api/bridge/market-movement`: Report significant movements
- `POST /api/bridge/technical-indicators`: Share technical signals
- `GET /api/bridge/ml-knowledge/{symbol}`: Get ML insights for symbol
- `GET /api/bridge/status`: Check bridge status
- `POST /api/bridge/sync-patterns`: Manually sync patterns with ML

## 📊 Data Storage

### SQLite Databases
- `historical_data/market_data.db`: Historical market data cache
- `ml_integration_bridge.db`: Integration patterns and events
- `ml_models.db`: Trained model storage and versioning

## 🚨 Troubleshooting

### Services Not Starting
1. Ensure Python 3.8+ is installed
2. Check if ports 8002-8004 are available
3. Run `pip install -r requirements.txt` manually
4. Check logs in the `logs/` directory

### ML Backend Issues
- First run may take time to initialize models
- Ensure sufficient RAM for model training
- Check `logs/ml_backend.log` for errors

### Bridge Connection Issues
- Verify all three services are running
- Check `logs/bridge.log` for connection errors
- Use the "Test All Services" button in dashboard

## 📈 Performance Tips
1. **Use SQLite Cache**: Historical data loads 50x faster
2. **Train Models Overnight**: ML training is resource-intensive
3. **Monitor Bridge Queue**: Check pending events in bridge status
4. **Regular Pattern Sync**: Use "Sync ML Patterns" regularly

## 🔒 Security Notes
- Services bind to localhost only (not exposed externally)
- No authentication required for local use
- For production, add authentication layer

## 📝 Version History
- **v4.0**: ML Integration Bridge, FinBERT, SQLite caching
- **v3.0**: Enhanced ML backend with iterative learning
- **v2.0**: Basic ML integration
- **v1.0**: Initial release

## 🤝 Support
For issues or questions:
1. Check the logs in `logs/` directory
2. Use the diagnostic tools in the dashboard
3. Verify all services are running with "Test All Services"

## 📄 License
MIT License - Feel free to modify and distribute

---
**Note**: This is a development version. For production use, additional security measures and error handling should be implemented.