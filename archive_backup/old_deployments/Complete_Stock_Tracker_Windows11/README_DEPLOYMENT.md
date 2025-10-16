# Complete Stock Tracker - Windows 11 Deployment Guide

## 🚀 Quick Start for Windows 11

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ (optional, only for development)
- Git (for version control)

### Installation Steps

1. **Clone or Download the Package**
```bash
# If using Git
git clone <repository-url>
cd Complete_Stock_Tracker_Windows11

# Or extract the ZIP file to a folder
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the Backend Server**
```bash
python backend.py
```
The server will start on **http://localhost:8002** (hardcoded for Windows 11)

4. **Open the Frontend**
- Open `index.html` in your browser
- Or navigate to: `http://localhost:8002/` if serving via backend

## 📦 Local Data Storage for Fast Backtesting

### First Time Setup - Download Historical Data

1. **Via Web Interface:**
   - Open `modules/historical_data_manager.html` 
   - Click "Download Common Symbols" to get started
   - This downloads CBA.AX, major indices, and popular stocks

2. **Via Command Line:**
```python
# Quick download script
from historical_data_manager import HistoricalDataManager
import asyncio

async def setup():
    manager = HistoricalDataManager()
    
    # Download essential symbols
    symbols = ["CBA.AX", "^AORD", "^GSPC", "^FTSE"]
    await manager.download_historical_data(
        symbols=symbols,
        period="2y",
        intervals=["1d", "1h", "30m", "5m"]
    )
    print("✅ Data downloaded successfully!")

asyncio.run(setup())
```

### Benefits of Local Storage
- **100x Faster Backtesting**: No API calls needed
- **Unlimited Queries**: No rate limits
- **Offline Capable**: Works without internet after initial download
- **Historical Consistency**: Same data for reproducible results

## 🎯 Module Overview

### 1. CBA Enhanced Tracker (`modules/cba_enhanced.html`)
- Real-time CBA.AX price tracking (~$170 range)
- Candlestick charts with technical indicators
- News sentiment analysis
- Document upload and analysis with FinBERT
- ML predictions integration

### 2. Global Indices Tracker (`modules/indices_tracker.html`)
- Simple view of ^AORD, ^FTSE, ^GSPC
- 24/48 hour toggle
- Percentage changes from previous close
- Clean, focused interface

### 3. Phase 4 Prediction Centre (`modules/prediction_centre_phase4_real.html`)
- Real Yahoo Finance data integration
- Multiple ML models (LSTM, GRU, Random Forest, XGBoost)
- Backtesting with continuous learning
- Model performance tracking
- Ensemble predictions

### 4. Stock Tracker (`modules/stock_tracker.html`)
- Any stock symbol lookup
- Candlestick charts with Chart.js
- Technical indicators overlay
- Volume analysis
- Multi-timeframe views

### 5. Document Uploader (`modules/document_uploader.html`)
- PDF/Text document analysis
- FinBERT sentiment extraction
- Market impact assessment
- Historical document storage

### 6. Historical Data Manager (`modules/historical_data_manager.html`)
- Download and store market data locally
- Manage data for fast backtesting
- View storage statistics
- Track best performing models

## 🔧 Configuration

### Backend Settings (backend.py)
```python
# Port Configuration (Line ~10480)
port = 8002  # Hardcoded for Windows 11

# Data Storage Path
DOCUMENT_STORAGE_PATH = "document_storage"
HISTORICAL_DATA_PATH = "historical_data"
```

### Frontend Settings (all HTML files)
```javascript
// API Base URL - hardcoded in all modules
const API_BASE = 'http://localhost:8002';
```

## 📊 Performance Optimizations

### Already Implemented:
1. **TTLCache** - Memory caching for frequent queries
2. **DataCache Class** - Multi-level caching system
3. **SQLite Indexes** - Fast database queries
4. **Parallel Processing** - ThreadPoolExecutor for downloads
5. **Batch Processing** - Efficient model training
6. **Incremental Learning** - Update models without full retrain
7. **GPU Support** - Automatic GPU detection and usage

### Recommended Settings:
- Keep ~10GB free disk space for historical data
- Allocate 4GB+ RAM for optimal performance
- Use SSD for database storage if possible

## 🚨 Troubleshooting

### Common Issues:

1. **Port 8002 Already in Use**
   - Check Task Manager for existing Python processes
   - Kill any process using port 8002
   - Or modify port in backend.py if needed

2. **Yahoo Finance Rate Limiting**
   - Use the Historical Data Manager to download data once
   - All subsequent queries use local storage

3. **Module Not Found Errors**
   ```bash
   pip install yfinance pandas numpy scikit-learn torch transformers flask flask-cors
   ```

4. **CORS Errors in Browser**
   - Ensure backend is running on port 8002
   - Check browser console for specific errors
   - Try opening HTML files via http://localhost:8002 instead of file://

## 📈 Data Management Tips

### Initial Data Setup (Recommended)
```python
# Download 2 years of data for optimal backtesting
symbols_to_download = [
    # Australian stocks
    "CBA.AX", "BHP.AX", "CSL.AX", "WBC.AX", "ANZ.AX", "NAB.AX",
    
    # Global indices
    "^AORD", "^GSPC", "^FTSE", "^DJI", "^IXIC",
    
    # Popular US stocks
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"
]

# This takes ~5-10 minutes but saves hours in backtesting
```

### Regular Updates
- Run data updates weekly or before major backtesting sessions
- Use the "Update Symbol" button in Historical Data Manager
- Or schedule automated updates via Windows Task Scheduler

## 🎯 Quick Test

1. Start backend: `python backend.py`
2. Open browser to: `http://localhost:8002`
3. Click on "CBA Enhanced Tracker"
4. Verify CBA.AX shows ~$170 price range
5. Check that charts load with real data
6. Test predictions and backtesting features

## 📝 Support Files

- `requirements.txt` - Python dependencies
- `historical_data_manager.py` - Local data storage system
- `advanced_ensemble_predictor_enhanced.py` - Enhanced ML predictor
- `advanced_ensemble_backtester_enhanced.py` - Fast backtesting engine
- `phase4_integration_enhanced.py` - Phase 4 model integration

## 🔐 Security Notes

- Backend runs locally only (0.0.0.0:8002)
- No external API keys required
- All data stored locally in SQLite
- Document uploads stored in local filesystem

## 📞 Need Help?

Check the following:
1. Browser Console (F12) for JavaScript errors
2. Terminal/Command Prompt for Python errors
3. `historical_data/metadata.json` for storage info
4. `documents.db` for document storage status

---

**Version**: 2.0.0  
**Last Updated**: October 2024  
**Port**: 8002 (Hardcoded for Windows 11)  
**Status**: Production Ready