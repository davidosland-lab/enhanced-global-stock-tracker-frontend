# Stock Tracker v6.0 - Complete Deployment Guide

## 🎯 What's Fixed in v6.0

### ✅ All Issues Resolved
1. **Localhost Hardcoded**: All API calls now use `http://localhost:8002` and `http://localhost:8003`
2. **No Synthetic Data**: Removed ALL fallback/demo/synthetic data - real Yahoo Finance only
3. **ML Backend Fixed**: No more Python syntax errors, ML backend starts correctly
4. **Module Links Fixed**: Historical Data Manager, Document Analyzer, Prediction Centre all work
5. **CBA.AX Price Fixed**: Shows real market price (~$170), not $100
6. **Backend Status**: Always shows "Connected" when services are running
7. **ML Training Centre**: Properly connects to ML Backend on port 8003
8. **Upload Limit**: Increased from 10MB to 100MB
9. **Master Control**: Single batch file to start/stop everything

## 📋 Requirements

- Windows 11 (also works on Windows 10)
- Python 3.8 or higher
- Internet connection (for Yahoo Finance data)
- 100MB free disk space

## 🚀 Quick Start

### Step 1: Extract Package
```
1. Extract StockTracker_v6.0_FINAL_LOCALHOST_ONLY.zip to any folder
2. Example: C:\StockTracker
```

### Step 2: Start Application
```
1. Double-click START_STOCK_TRACKER.bat
2. Three command windows will open:
   - Frontend Server (port 8000)
   - Backend API (port 8002)
   - ML Backend (port 8003)
3. Wait for "Stock Tracker is running!" message
```

### Step 3: Access Application
```
1. Open web browser
2. Navigate to: http://localhost:8000
3. All modules should work immediately
```

## 🔧 Service Architecture

```
┌─────────────────────────────────────┐
│   Browser (http://localhost:8000)   │
└────────────┬────────────────────────┘
             │
    ┌────────▼────────┐
    │  Frontend Server│
    │   Port: 8000    │
    └────────┬────────┘
             │
    ┌────────▼─────────────────────┐
    │                              │
    ▼                              ▼
┌─────────────┐          ┌─────────────┐
│ Backend API │          │ ML Backend  │
│ Port: 8002  │          │ Port: 8003  │
└──────┬──────┘          └──────┬──────┘
       │                         │
       └────────┬────────────────┘
                │
         ┌──────▼──────┐
         │Yahoo Finance│
         │  Real Data  │
         └─────────────┘
```

## 📁 File Structure

```
StockTracker/
├── START_STOCK_TRACKER.bat    # Master startup script
├── SHUTDOWN_ALL.bat           # Stop all services
├── TEST_SERVICES.bat          # Test all endpoints
├── TEST_CBA_PRICE.html        # Verify real prices
├── index.html                 # Main application
├── backend.py                 # Backend API (port 8002)
├── backend_ml_fixed.py        # ML Backend (port 8003)
├── requirements.txt           # Python dependencies
├── error_handler.js           # Error handling
├── modules/                   # Application modules
│   ├── historical_data.html
│   ├── document_analyzer.html
│   ├── prediction_centre.html
│   └── ml_training_centre.html
└── static/                    # Static assets

```

## 🛠️ Troubleshooting

### Issue: "Python not found"
**Solution**: Install Python from python.org, ensure "Add to PATH" is checked

### Issue: "Port already in use"
**Solution**: 
1. Run SHUTDOWN_ALL.bat to kill existing processes
2. Or manually: `netstat -ano | findstr :8000`
3. Kill process: `taskkill /F /PID <process_id>`

### Issue: "Backend Status: Disconnected"
**Solution**:
1. Check all 3 command windows are open
2. Run TEST_SERVICES.bat to verify
3. Check Windows Firewall isn't blocking Python

### Issue: "No market data available"
**Solution**:
1. Check internet connection
2. Verify market is open (ASX: 10am-4pm Sydney time)
3. Try different stock symbol

### Issue: Module shows 404 error
**Solution**:
1. Ensure all services are running
2. Clear browser cache (Ctrl+F5)
3. Check modules folder exists

## 🔍 Testing

### Test All Services
```batch
REM Run this to test all endpoints
TEST_SERVICES.bat
```

### Test CBA Price
```
1. Open TEST_CBA_PRICE.html in browser
2. Should show ~$170, not $100
```

### Manual Tests
```bash
# Test Backend
curl http://localhost:8002/api/health

# Test ML Backend  
curl http://localhost:8003/health

# Test Stock Data
curl http://localhost:8002/api/stock/CBA.AX
```

## 🔐 Security Notes

- Application runs locally only (localhost)
- No external access by default
- To allow network access, modify firewall rules
- No user data is sent externally

## 📊 Data Sources

- **Stock Data**: Yahoo Finance (real-time when market open)
- **Historical Data**: Yahoo Finance historical API
- **ML Predictions**: Based on real market data only
- **No Synthetic Data**: All fallbacks removed

## 🆘 Support

### Common Commands

**Start Everything**:
```batch
START_STOCK_TRACKER.bat
```

**Stop Everything**:
```batch
SHUTDOWN_ALL.bat
```

**Check Ports**:
```batch
netstat -ano | findstr "8000 8002 8003"
```

**Install Dependencies**:
```batch
pip install -r requirements.txt
```

## 📝 Version History

- **v6.0** (Current): Complete localhost fix, no synthetic data
- **v5.0**: ML Backend fixes
- **v4.x**: Attempted fallback removal (had issues)
- **v3.x**: Windows 11 compatibility
- **v2.x**: ML Training Centre added
- **v1.x**: Initial release

## ✨ Key Features

1. **Real Data Only**: Yahoo Finance live data
2. **Localhost Only**: All services on localhost
3. **No Fallbacks**: Error messages instead of fake data
4. **Proper ML Backend**: Training and prediction work
5. **100MB Uploads**: Document analyzer supports large files
6. **Windows Integration**: Batch files for easy control

## 🎯 Final Checklist

- [x] All services use localhost URLs
- [x] No synthetic/demo/fallback data
- [x] ML Backend runs without errors
- [x] All module links work
- [x] CBA.AX shows real price (~$170)
- [x] Backend status shows "Connected"
- [x] ML Training Centre connects properly
- [x] Upload limit increased to 100MB
- [x] Master batch files for control

---

**Version 6.0 - FINAL** | No synthetic data | Localhost only | Real market data