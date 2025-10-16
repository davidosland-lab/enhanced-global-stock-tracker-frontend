# Stock Tracker Suite - Clean Installation Package

## 🚀 Quick Start

### One-Click Desktop Shortcut
1. Copy `StockTracker.bat` to your Desktop
2. Double-click to open the Control Panel
3. Press `1` to START all services
4. Your browser will open automatically

### Manual Start
```batch
StockTracker.bat
```

## 📁 What's Included

- **StockTracker.bat** - Desktop control panel for start/stop/status
- **backend.py** - Main backend API with all fixes applied
- **backend_ml_enhanced.py** - ML backend for training centre (port 8003)
- **index.html** - Landing page with all 7 modules
- **modules/** - All frontend modules
- **requirements.txt** - Python dependencies

## 🛠️ Installation

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- pip (Python package manager)

### First Time Setup
1. Extract all files to a folder (e.g., `C:\StockTracker`)
2. Open Command Prompt in that folder
3. Install dependencies:
   ```batch
   pip install -r requirements.txt
   ```
4. Run StockTracker.bat

## 📊 Available Modules

1. **Global Stock Tracker** - Real-time market monitoring
2. **Document Analyser** - FinBERT AI analysis (100MB file limit)
3. **Technical Analysis** - Enhanced v5.3 with 50+ indicators
4. **Historical Data Manager** - Download and manage historical data
5. **ML Training Centre** - Train and test ML models
6. **CBA Enhanced** - Commonwealth Bank specialist tracker
7. **Prediction Centre** - Phase 4 advanced predictions

## 🔧 Control Panel Options

The `StockTracker.bat` control panel provides:

- **[1] START** - Launch all services and open browser
- **[2] STOP** - Shutdown all services cleanly
- **[3] STATUS** - Check service status
- **[4] RESTART** - Stop and start all services
- **[5] EXIT** - Exit control panel

## 🌐 Service Ports

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:8002
- **ML Backend**: http://localhost:8003

## 📝 Troubleshooting

### Services won't start
1. Check if Python is installed: `python --version`
2. Check if ports are in use: Use Status option [3]
3. Try Restart option [4] to clear ports

### ML Training Centre not working
- Ensure `backend_ml_enhanced.py` exists
- Check ML Backend is running on port 8003
- Use Status option [3] to verify

### Landing page shows old version
- Clear browser cache (Ctrl+F5)
- Check `index.html` file size (should be ~15KB)

### Port conflicts
- Use STOP option [2] to clear all ports
- If ports still blocked, restart computer

## 📁 Directory Structure

```
StockTracker/
├── StockTracker.bat        # Desktop control panel
├── backend.py              # Main API (port 8002)
├── backend_ml_enhanced.py  # ML API (port 8003)
├── index.html              # Landing page
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── modules/               # Frontend modules
│   ├── cba_enhanced.html
│   ├── document_uploader.html
│   ├── historical_data_manager.html
│   ├── ml_training_centre.html
│   ├── prediction_centre_phase4.html
│   ├── technical_analysis_enhanced.html
│   └── market-tracking/
│       └── market_tracker_final.html
├── historical_data/       # Downloaded data (created automatically)
├── models/               # ML models (created automatically)
├── uploads/              # Uploaded files (created automatically)
├── predictions/          # Predictions (created automatically)
└── logs/                # Service logs (created automatically)
```

## ✅ Features

- **Real Yahoo Finance Data** - No synthetic data
- **100MB File Upload** - Increased from 10MB
- **Correct CBA.AX Price** - Shows ~$170
- **All Modules Working** - 7 fully functional modules
- **ML Backend Included** - Training centre operational
- **Historical Data Fixed** - Download functionality works
- **Route Order Fixed** - No more "STATISTICS" errors

## 🔒 Security Notes

- Services run locally only (localhost)
- No external access by default
- Data stored locally in folders

## 📞 Support

For issues or questions:
1. Check the Status [3] in control panel
2. Review logs in the `logs/` folder
3. Try Restart [4] option
4. Ensure all files are in the same directory

## 🎯 Quick Commands

Start everything:
```batch
StockTracker.bat
[Press 1]
```

Stop everything:
```batch
StockTracker.bat
[Press 2]
```

Check status:
```batch
StockTracker.bat
[Press 3]
```

---

**Version**: 3.0 FINAL
**Date**: October 2024
**All fixes applied and ready to use!**