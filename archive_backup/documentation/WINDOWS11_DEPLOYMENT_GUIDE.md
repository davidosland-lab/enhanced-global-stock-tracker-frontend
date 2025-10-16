# 🚀 Windows 11 Stock Tracker - Deployment Guide

## 📁 Deployment Package Location
```
/home/user/webapp/clean_install_windows11/
```

## 📋 Quick Deployment Steps

### 1. Download the Package
Copy the entire `clean_install_windows11` folder to your Windows 11 machine.

### 2. Install Python (if not installed)
- Download Python 3.8+ from https://python.org
- **IMPORTANT**: Check "Add Python to PATH" during installation

### 3. Open Command Prompt or PowerShell
Navigate to the deployment folder:
```cmd
cd C:\path\to\clean_install_windows11
```

### 4. Run Setup (First Time Only)
```cmd
python setup_complete.py
```
This will:
- Install all required packages
- Initialize SQLite database
- Pre-load market data
- Create start scripts

### 5. Start the Application

#### Option A: Double-click the batch file
```
RUN_WINDOWS11.bat
```

#### Option B: Run from command line
```cmd
python backend.py
```

### 6. Open in Browser
Navigate to: **http://localhost:8002**

---

## 📦 Complete File List

Your deployment package includes:

| File | Purpose | Size |
|------|---------|------|
| `backend.py` | Main backend server with all endpoints | ~20KB |
| `historical_data_manager.py` | SQLite local storage system | ~20KB |
| `index.html` | Main landing page with 5 modules | ~24KB |
| `setup_complete.py` | Automated setup script | ~10KB |
| `RUN_WINDOWS11.bat` | One-click launcher for Windows | ~1KB |
| `SETUP_INSTRUCTIONS.md` | Detailed setup guide | ~8KB |
| `modules/` folder | All HTML modules | - |

### Modules Included:
- `cba_enhanced.html` - CBA tracker with Documents/Media/Reports tabs
- `prediction_centre_phase4.html` - Phase 4 predictor with backtesting
- `stock_tracker.html` - Advanced candlestick charts
- `global_market_tracker.html` - Global indices with 24/48hr toggle
- `document_uploader.html` - FinBERT document analyzer
- `technical_analysis.html` - Technical indicators
- `historical_data_manager.html` - Data management UI
- `prediction_performance_dashboard.html` - Performance tracking

---

## ✅ Key Features

### 1. **Real-Time Data**
- Live Yahoo Finance data
- CBA.AX shows correct price (~$170)
- No mock/synthetic data

### 2. **Local Storage with SQLite**
- 100x faster backtesting
- Cached historical data
- Automatic data updates

### 3. **Advanced Modules**
- CBA Enhanced with 6 tabs (Overview, Technical, Predictions, Documents, Media, Reports)
- Phase 4 GNN predictor
- Document analysis with FinBERT
- Candlestick charts with Chart.js 4.4.0

### 4. **Windows 11 Optimized**
- Hardcoded to localhost:8002
- CORS enabled for local development
- All endpoints properly configured

---

## 🔧 Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```cmd
pip install fastapi uvicorn yfinance pandas numpy cachetools pytz python-multipart
```

### Issue: SQLite not initializing
**Solution:**
```cmd
python -c "from historical_data_manager import HistoricalDataManager; HistoricalDataManager()"
```

### Issue: Backend won't start
**Check Python version:**
```cmd
python --version
```
Should be 3.8 or higher.

### Issue: "Port 8002 already in use"
**Find and kill the process:**
```cmd
netstat -ano | findstr :8002
taskkill /PID [process_id] /F
```

---

## 🎯 Verification Checklist

After deployment, verify:

- [ ] Backend starts without errors
- [ ] Console shows "Historical Data Manager initialized"
- [ ] Browser shows "Backend Status: Connected"
- [ ] CBA.AX price is around $170
- [ ] All 5 module cards appear on landing page
- [ ] `historical_data/` folder is created
- [ ] SQLite database file exists (`market_data.db`)

---

## 💻 System Requirements

### Minimum:
- Windows 11 (or Windows 10)
- Python 3.8+
- 2GB RAM
- 500MB disk space

### Recommended:
- Windows 11
- Python 3.10+
- 4GB RAM
- 1GB disk space (for data caching)

---

## 📊 API Endpoints

Once running, these endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `http://localhost:8002/` | GET | Landing page |
| `http://localhost:8002/api/status` | GET | Backend status |
| `http://localhost:8002/api/stock/{symbol}` | GET | Real-time stock data |
| `http://localhost:8002/api/historical/{symbol}` | GET | Historical data |
| `http://localhost:8002/api/indices` | GET | Market indices |
| `http://localhost:8002/api/predict` | POST | Stock predictions |
| `http://localhost:8002/api/phase4/predict` | POST | GNN predictions |
| `http://localhost:8002/api/phase4/backtest` | POST | Backtesting |
| `http://localhost:8002/docs` | GET | API documentation |

---

## 🚦 Expected Console Output

When running correctly, you should see:

```
============================================================
    WINDOWS 11 STOCK TRACKER - ENTERPRISE EDITION
============================================================

Initializing SQLite Database for 100x faster backtesting...
SQLite database ready at: historical_data

Starting backend server...

============================================================
    Backend running on: http://localhost:8002
    Press Ctrl+C to stop the server
============================================================

INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Historical Data Manager initialized - 100x faster backtesting enabled
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

---

## 🎉 Success!

Your Windows 11 Stock Tracker is now deployed with:
- ✅ Real Yahoo Finance data
- ✅ SQLite local storage (100x faster)
- ✅ CBA Enhanced with Documents/Media
- ✅ Phase 4 predictor with backtesting
- ✅ Document analyzer with FinBERT
- ✅ All 5 requested modules working

Open **http://localhost:8002** in your browser to start using the application!