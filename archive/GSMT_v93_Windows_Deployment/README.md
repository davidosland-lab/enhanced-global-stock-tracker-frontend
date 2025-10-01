# Global Stock Market Tracker v9.3 - Windows 11 Deployment Package

## 🎯 CRITICAL FIX INCLUDED
This version resolves the market timing issue where S&P 500 was incorrectly showing AFTER ASX opens.

## 📦 Package Contents

### Backend Files:
- `backend/enhanced_market_backend.py` - Fixed backend with proper AEST timezone handling
- `backend/requirements.txt` - Python dependencies

### Frontend Files:
- `frontend/indices_tracker_final.html` - Main tracker interface (FIXED)
- `frontend/index.html` - Landing page
- `frontend/dashboard.html` - Main dashboard
- `frontend/technical_analysis.html` - Technical analysis module
- `frontend/cba_tracker.html` - CBA tracking module
- `frontend/prediction_performance.html` - Prediction dashboard

### Batch Files:
- `START_GSMT.bat` - One-click launcher for Windows
- `INSTALL_DEPENDENCIES.bat` - Dependency installer
- `STOP_GSMT.bat` - Stop all services

### Documentation:
- `README.md` - This file
- `RELEASE_NOTES_v93.md` - Detailed release notes
- `UPDATE_MARKET_TIMING_FIX.md` - Technical fix documentation

## 🚀 Quick Start for Windows 11

### Prerequisites:
- Python 3.8+ installed
- Internet connection for Yahoo Finance data

### Installation Steps:

1. **Extract the ZIP file** to your desired location (e.g., `C:\GSMT`)

2. **Install Dependencies** (first time only):
   - Double-click `INSTALL_DEPENDENCIES.bat`
   - Wait for all packages to install

3. **Start the Application**:
   - Double-click `START_GSMT.bat`
   - The backend will start on port 8000
   - The frontend will start on port 3001
   - Your browser will open automatically

4. **Access the Application**:
   - Main URL: http://localhost:3001
   - Direct Tracker: http://localhost:3001/indices_tracker_final.html

## ✅ What's Fixed in v9.3

### Market Timing (CRITICAL):
- S&P 500 now shows at 00:30-07:00 AEST (BEFORE ASX)
- FTSE shows at 18:00-02:30 AEST (evening)
- Proper chronological sequence throughout 24 hours

### Data & Features:
- All Ordinaries (^AORD) included
- 100% real Yahoo Finance data
- 5-minute interval updates
- Regional market filtering
- Proper AEST timezone display

## 📊 Market Trading Hours (AEST)

```
00:30 - 07:00  Americas (S&P 500, Dow, NASDAQ)
10:00 - 16:00  Asia-Pacific (ASX, All Ords, Nikkei)
18:00 - 02:30  Europe (FTSE, DAX, CAC)
```

## 🛑 Stopping the Application

- Double-click `STOP_GSMT.bat` to stop all services
- Or press Ctrl+C in the command windows

## 🔧 Troubleshooting

### Port Already in Use:
- Run `STOP_GSMT.bat` to clear ports
- Check Task Manager for Python processes
- Try alternative ports in the config

### Data Not Loading:
- Check internet connection
- Verify Yahoo Finance accessibility
- Check console for error messages

### Display Issues:
- Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Check browser console (F12)

## 📝 Configuration

### Change Ports (if needed):
Edit `START_GSMT.bat`:
- Backend port: Change `8000` to desired port
- Frontend port: Change `3001` to desired port

### Update Frequency:
Edit `frontend/indices_tracker_final.html`:
- Line ~380: Change `30000` (30 seconds) to desired milliseconds

## 🆘 Support

For issues or questions:
1. Check the console output for errors
2. Review RELEASE_NOTES_v93.md for known issues
3. Ensure all dependencies are installed
4. Verify firewall isn't blocking ports

---
Version: 9.3
Date: September 30, 2025
Status: Production Ready