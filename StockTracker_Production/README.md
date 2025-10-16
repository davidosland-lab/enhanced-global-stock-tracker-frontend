# Stock Tracker Production System

## Overview
Enhanced Global Stock Tracker with ML-powered predictions, focusing on Australian markets (CBA, AORD) while tracking global indices (FTSE, S&P 500).

## Core Features
1. **ML Prediction Engine** - Ensemble models (RandomForest, XGBoost, SVM)
2. **Enhanced CBA Module** - Specialized Commonwealth Bank analysis
3. **Global Indices Tracker** - 24/48hr timelines for AORD, FTSE, S&P
4. **Sentiment Analysis** - FinBERT + web scraping
5. **Technical Analysis** - 30+ indicators with visualizations
6. **Document Analyzer** - Upload and analyze financial documents
7. **Backtesting Engine** - Historical performance validation

## Quick Start

### Windows Installation
1. Run `scripts/start_enhanced_ml_system.bat`
2. Access http://localhost:8000

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the unified backend
python backend/ml_prediction_backtesting_enhanced.py

# Access the web interface
# http://localhost:8000
```

## Architecture

### Backend Services
- **Port 8000**: Unified ML System (main)
- **Port 8007**: Indices Tracker (optional standalone)
- **Port 8008**: Performance Tracker (optional standalone)

### Key Components
```
backend/
├── ml_prediction_backtesting_enhanced.py  # Main unified system
├── ml_enhancements_based_on_research.py   # Advanced ML features
├── indices_tracker_backend.py             # Global indices monitoring
└── performance_tracker_backend.py         # Performance metrics

frontend/
├── ml_prediction_backtesting_enhanced.html # Main dashboard
├── cba_enhanced.html                       # CBA analysis
├── indices_tracker.html                    # Indices visualization
└── technical_analysis.html                 # TA charts

data/
├── ml_models_enhanced.db      # Trained models
├── predictions_enhanced.db     # Prediction history
├── historical_data_cache.db   # 50x faster data access
└── backtest_results_enhanced.db # Backtesting results
```

## ML Models

### Ensemble Configuration
- **RandomForest**: 100 estimators, max_depth=10
- **XGBoost**: 100 rounds, learning_rate=0.1
- **SVM**: RBF kernel, C=100
- **Neural Network**: 3 layers (100-50-25)

### Features (30-35 optimal)
- Technical: RSI, MACD, Bollinger Bands, ATR, OBV
- Price: Returns (1,5,20 days), volatility
- Volume: Volume ratio, MFI
- Market: Regime detection, trend strength

### Performance Targets
- Directional Accuracy: 65-75%
- Sharpe Ratio: >1.2
- Max Drawdown: <20%
- Training Time: 10-60 seconds

## Original Modules (Preserved)

### CBA Enhanced
- Real-time ASX:CBA tracking
- Dividend analysis
- Australian market context

### Indices Tracker
- AORD (All Ordinaries)
- FTSE 100
- S&P 500
- 24/48 hour timelines

### Sentiment Scraper
- Real-time news scraping
- FinBERT analysis
- Market sentiment scores

### Technical Analysis
- Interactive charts
- 30+ indicators
- Pattern recognition

### Document Uploader
- PDF/Word support
- Financial document analysis
- Impact on predictions

## Configuration

### Environment Variables
```bash
# Optional - defaults work fine
ML_CACHE_DURATION=86400  # 24 hours
ML_RETRAIN_DAYS=7        # Weekly retraining
ML_FEATURE_COUNT=35      # Optimal features
```

### Database Management
- SQLite databases in `data/` directory
- Automatic migration on startup
- Cache expires after 24 hours

## API Endpoints

### ML Predictions
- `POST /api/train` - Train models
- `POST /api/predict` - Get predictions
- `POST /api/backtest` - Run backtesting

### Market Data
- `GET /api/indices/current` - Current indices
- `GET /api/indices/timeline` - 24/48hr data
- `GET /api/cba/analysis` - CBA enhanced analysis

### Analysis
- `POST /api/sentiment/analyze` - Sentiment analysis
- `GET /api/technical/{symbol}` - Technical indicators
- `POST /api/documents/upload` - Document analysis

## Performance Optimizations
- SQLite caching: 50x faster data retrieval
- Parallel model training
- Efficient feature calculation
- Optimized for Windows 11

## Requirements
- Python 3.8+
- 4GB RAM minimum
- Windows 10/11 or Linux
- Internet connection for data

## Support
For issues or questions, check the documentation in `/archive_backup/documentation/`

## Version
Production v2.0 - Enhanced ML with Original Modules

## License
Private - All rights reserved