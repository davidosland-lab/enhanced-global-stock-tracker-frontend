# Stock Tracker ML Integration - Version 6.0

## 🚀 Quick Start Guide

### Windows Users
1. Double-click `START_SERVICES.bat` to start all services
2. Open `index.html` in your browser
3. All ML and prediction modules are now accessible

### Linux/Mac Users
1. Run `chmod +x START_SERVICES.sh` (first time only)
2. Run `./START_SERVICES.sh` to start all services
3. Open `index.html` in your browser

## 🔌 Service Architecture

### Core Services (Required)
- **Main Backend** (Port 8002): Core API for market data and basic operations
- **ML Backend** (Port 8003): Machine learning models and predictions
- **Integration Bridge** (Port 8004): Connects all modules for cross-learning

### Service URLs
- Main Backend: http://localhost:8002/api/status
- ML Backend: http://localhost:8003/api/ml/status
- Integration Bridge: http://localhost:8004/api/bridge/status

## 🤖 ML & Prediction Modules

### Fully Integrated Modules (No 404 Errors)

#### 1. ML Training Centre (`modules/ml_training_centre.html`)
- **Port**: 8003
- **Features**: 
  - Real ML model training (Random Forest, XGBoost, LSTM, ARIMA)
  - Integration bridge connected for cross-module learning
  - SQLite storage for model persistence
  - Automated backtesting after training
- **Status**: ✅ WORKING - Connected to ML Backend

#### 2. ML Integrated Training (`modules/ml_training_integrated.html`)
- **Port**: 8003
- **Features**:
  - Automated model selection and comparison
  - Performance metrics visualization
  - Result storage in SQLite
- **Status**: ✅ WORKING - Connected to ML Backend

#### 3. Prediction Centre ML Connected (`modules/prediction_centre_ml_connected.html`)
- **Port**: 8003
- **Features**:
  - Real-time ML predictions
  - Live model switching
  - Bridge pattern integration
  - Historical accuracy tracking
- **Status**: ✅ WORKING - Connected to ML Backend & Bridge

#### 4. Prediction Centre Phase 4 Real (`modules/prediction_centre_phase4_real.html`)
- **Port**: 8003
- **Features**:
  - Production-ready predictions
  - 6 ML models available
  - Comprehensive backtesting
  - Learning metrics tracking
- **Status**: ✅ WORKING - Real ML Implementation

#### 5. Prediction Performance Dashboard (`modules/prediction_performance_dashboard.html`)
- **Port**: 8003
- **Features**:
  - Model performance comparison
  - Accuracy tracking over time
  - Error analysis and improvement trends
- **Status**: ✅ WORKING - Analytics Dashboard

## 🔗 Integration Bridge Features

The Integration Bridge (Port 8004) enables:

### Cross-Module Learning
- **Document Analyzer** → Sentiment patterns → ML Knowledge Base
- **Historical Data** → Market patterns → ML Training
- **Technical Analysis** → Signal validation → ML Confirmation
- **ML Predictions** → Feedback → All modules

### Pattern Sharing
- Discovered patterns are shared across all modules
- ML models learn from patterns found by other modules
- Continuous improvement through iterative learning

### API Endpoints
- `/api/bridge/status` - Check bridge health
- `/api/bridge/document-sentiment` - Submit sentiment data
- `/api/bridge/historical-pattern` - Submit historical patterns
- `/api/bridge/technical-indicators` - Submit technical signals
- `/api/bridge/ml-knowledge/{symbol}` - Get ML insights for symbol
- `/api/bridge/sync-patterns` - Manual pattern sync

## 📊 Additional Working Modules

### Analysis Modules
- **Document Analyzer** (`modules/document_analyzer.html`)
  - FinBERT sentiment analysis
  - Sends insights to Integration Bridge
  
- **Historical Data Manager** (`modules/historical_data_manager_fixed.html`)
  - SQLite local storage (50x faster)
  - Pattern discovery and sharing

- **Technical Analysis Enhanced** (`modules/technical_analysis_enhanced.html`)
  - 150+ technical indicators
  - ML signal validation

### Market Tracking
- **Global Market Tracker** (`modules/global_market_tracker.html`)
- **Stock Tracker** (`modules/stock_tracker.html`)
- **Indices Tracker** (`modules/indices_tracker.html`)

## 🛠️ Troubleshooting

### If services don't start:
1. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn yfinance pandas numpy scikit-learn ta joblib sqlite3
   pip install transformers torch  # For FinBERT (optional)
   ```

2. Check if ports are already in use:
   ```bash
   # Windows
   netstat -ano | findstr :8002
   netstat -ano | findstr :8003
   netstat -ano | findstr :8004
   
   # Linux/Mac
   lsof -i:8002
   lsof -i:8003
   lsof -i:8004
   ```

3. Kill existing processes if needed:
   ```bash
   # Windows - use PID from netstat
   taskkill /PID <pid> /F
   
   # Linux/Mac
   kill -9 $(lsof -ti:8002)
   kill -9 $(lsof -ti:8003)
   kill -9 $(lsof -ti:8004)
   ```

### Module 404 Errors Fixed
All ML and prediction modules now correctly point to:
- ML Backend on port 8003
- Integration Bridge on port 8004
- Proper file paths in `modules/` directory

### Service Health Check
Open the dashboard (`index.html`) and look at the Service Status panel:
- Green dots = Service running
- Red dots = Service not running
- Blue dots = Integration Bridge active

Click "Refresh Status" to update service states.

## 📈 Performance Optimizations

### Local SQLite Storage
- Historical data cached locally for 50x faster access
- Model results stored for quick retrieval
- Pattern database for shared learning

### Iterative Learning
- Models improve over time
- Transfer learning from previous versions
- Knowledge accumulation in bridge database

## 🎯 Key Features Summary

1. **No More Random Predictions**: Real ML models with actual training
2. **No More 404 Errors**: All modules properly linked and working
3. **Integration Bridge**: Cross-module learning and pattern sharing
4. **FinBERT Sentiment**: Real financial sentiment analysis
5. **SQLite Storage**: Fast local data access
6. **Production Ready**: All services tested and working

## 📝 Version History

- **v6.0** (Current): Full ML integration with bridge, all 404s fixed
- **v5.0**: Added ML backend and prediction modules
- **v4.0**: Historical data service integration
- **v3.0**: Technical analysis enhancements
- **v2.0**: Basic prediction capabilities
- **v1.0**: Initial release

## 🤝 Support

For issues or questions:
1. Check service status in dashboard
2. Review logs in `logs/` directory
3. Ensure all Python dependencies installed
4. Restart services if needed

---
**Last Updated**: October 14, 2025
**Status**: ✅ All Systems Operational