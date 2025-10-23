# Stock Tracker Integrated System

## 🚀 Quick Start

### For Windows 11 Users:
1. **Extract the ZIP file** to any folder on your computer
2. **Double-click** `QUICK_START.bat` 
3. **Wait** for the browser to open automatically (about 10-15 seconds)
4. **Done!** The system is ready at http://localhost:8000

### Alternative Start Methods:
- **START.bat** - Shows detailed startup process
- **QUICK_START.bat** - Minimal output, auto-opens browser

## 📋 Requirements

- **Windows 11** (or Windows 10)
- **Python 3.8+** installed ([Download Python](https://www.python.org/downloads/))
- **Modern Web Browser** (Chrome, Edge, Firefox)
- **Internet Connection** (for Yahoo Finance data)

## ✨ Key Features

### Document Sentiment Integration
- Upload financial documents (PDF, DOC, TXT)
- AI-powered sentiment analysis
- Link documents to specific stocks
- Sentiment-weighted predictions

### Real-Time Data
- Live Yahoo Finance integration
- No synthetic/fallback data
- Real CBA.AX pricing (~$170)
- ADST timezone support

### Advanced Analysis
- ML model training with sentiment
- Technical indicators
- 7-30 day predictions
- Market sentiment tracking

## 🗂️ Package Contents

```
StockTracker_Integrated_Complete/
├── backend.py                 # Main backend with document integration
├── ml_backend.py              # ML service
├── index.html                 # Main dashboard
├── QUICK_START.bat           # One-click startup
├── START.bat                 # Detailed startup
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── modules/
    ├── stock_analysis.html   # Stock analysis with sentiment
    ├── ml_training_centre.html # ML training interface
    ├── document_uploader.html  # Document upload (100MB limit)
    ├── prediction_centre.html  # Predictions with sentiment
    ├── cba_enhanced.html      # CBA analysis
    └── market-tracking/
        └── market_tracker_final_COMPLETE_FIXED.html

```

## 🌐 Services & Ports

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Frontend | 8000 | http://localhost:8000 | Web interface |
| Backend API | 8002 | http://localhost:8002 | Main API with documents |
| ML Service | 8003 | http://localhost:8003 | Machine learning API |

## 📊 API Endpoints

### Document Analysis
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents/sentiment/{symbol}` - Get stock sentiment
- `GET /api/market/sentiment` - Market sentiment overview

### Stock Data
- `GET /api/stock/{symbol}` - Real-time data
- `GET /api/historical/{symbol}` - Historical data
- `POST /api/predict` - Generate predictions

### ML Operations
- `POST /api/ml/train` - Train models
- `POST /api/ml/predict` - ML predictions
- `GET /api/ml/status` - Service status

## 🛠️ Troubleshooting

### Services won't start
1. Check Python is installed: `python --version`
2. Install requirements: `pip install -r requirements.txt`
3. Check ports aren't in use: `netstat -an | findstr :8000`

### "Backend Disconnected" error
1. Ensure backend.py is running
2. Check http://localhost:8002/api/health
3. Restart services using QUICK_START.bat

### Document upload issues
- Maximum file size: 100MB
- Supported formats: PDF, DOC, DOCX, TXT
- Check backend console for errors

### Wrong prices showing
- Clear browser cache
- Ensure internet connection for Yahoo Finance
- Check symbol format (e.g., CBA.AX for Australian stocks)

## 🔧 Manual Installation

If the batch files don't work:

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Start Backend (new terminal)
python backend.py 8002

# 3. Start ML Service (new terminal)
python ml_backend.py 8003

# 4. Start Frontend (new terminal)
python -m http.server 8000

# 5. Open browser
http://localhost:8000
```

## 📈 Using the System

### Upload Documents
1. Go to Document Analyzer
2. Select a file (PDF, DOC, TXT)
3. Choose stock symbol to link
4. Upload and wait for analysis

### View Sentiment Impact
1. Open Stock Analysis
2. Enter stock symbol
3. Toggle "Include sentiment"
4. See sentiment-weighted predictions

### Train ML Models
1. Open ML Training Centre
2. Select stock and model type
3. Enable sentiment integration
4. Start training and monitor progress

## 🔒 Security Notes

- All services run locally (localhost only)
- No external API keys required
- Documents stored locally in SQLite
- No data sent to external servers

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all requirements are met
3. Restart using QUICK_START.bat
4. Check service logs in console windows

## 🎯 Version

**Version**: 1.0 Integrated
**Released**: October 2024
**Features**: Full document sentiment integration

---

**Important**: This system requires an active internet connection for Yahoo Finance data. All analysis and predictions are for educational purposes only.