# Stock Tracker - Windows 11 Deployment Guide

## 🚀 Quick Start

### Option 1: Automatic Start (Recommended)
Double-click on:
```
START_STOCK_TRACKER.bat
```
This will automatically detect and use the best method for your system.

### Option 2: PowerShell (Windows 11 Optimized)
Right-click on `MASTER_STARTUP_WIN11.ps1` and select "Run with PowerShell"

### Option 3: Command Prompt
Double-click on:
```
MASTER_STARTUP_WIN11.bat
```

## 📋 System Requirements

- **Windows 11** (also works on Windows 10)
- **Python 3.8+** (preferably 3.10 or 3.11)
- **4GB RAM minimum** (8GB recommended)
- **500MB free disk space**
- **Internet connection** (for real-time stock data)

## 🔧 Pre-Installation Setup

### 1. Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check ✅ "Add Python to PATH" during installation
3. Choose "Install Now" for default settings

### 2. Verify Installation
Open Command Prompt and run:
```cmd
python --version
pip --version
```

### 3. Windows Security Settings
If Windows Defender blocks the scripts:
1. Go to Windows Security > Virus & threat protection
2. Click "Manage settings" under Virus & threat protection settings
3. Add an exclusion for the Stock Tracker folder

## 🎯 Features of Master Startup Script

The `MASTER_STARTUP_WIN11.bat` script performs:

### Phase 1: System Cleanup
- ✅ Terminates all existing Python processes
- ✅ Clears ports 8000, 8002, 8003
- ✅ Removes hung processes

### Phase 2: Environment Verification
- ✅ Checks Python installation
- ✅ Verifies pip availability
- ✅ Validates Python version

### Phase 3: Dependency Installation
- ✅ Installs/updates all required packages
- ✅ Fixes Python 3.12 compatibility issues
- ✅ Creates required directories

### Phase 4: Service Startup
- ✅ Starts Frontend Server (port 8000)
- ✅ Starts Backend API (port 8002)
- ✅ Starts ML Backend (port 8003)

### Phase 5: Health Checks
- ✅ Verifies each service is running
- ✅ Tests API endpoints
- ✅ Validates Historical Data Manager
- ✅ Opens browser automatically

## 🖥️ Service Architecture

```
┌─────────────────────────────────────────┐
│         FRONTEND (Port 8000)            │
│         - User Interface                 │
│         - Module Pages                   │
│         - Test Suites                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        BACKEND API (Port 8002)          │
│         - Stock Data API                 │
│         - Historical Data Manager        │
│         - Real-time Prices              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ML BACKEND (Port 8003)          │
│         - Machine Learning Models        │
│         - Predictions                    │
│         - Training Pipeline             │
└─────────────────────────────────────────┘
```

## 📊 Available URLs After Startup

| Service | URL | Description |
|---------|-----|-------------|
| Main Application | http://localhost:8000 | Stock Tracker Dashboard |
| API Documentation | http://localhost:8002/docs | Interactive API docs |
| Historical Data Test | http://localhost:8000/test_historical_manager.html | Test data downloads |
| Connection Diagnostics | http://localhost:8000/diagnose_connection.html | Debug connections |

## 🔍 Troubleshooting

### Run Diagnostic Tool
```cmd
TROUBLESHOOT_WIN11.bat
```

This tool will:
- Check system status
- Verify port availability
- Test package installation
- Provide quick fixes

### Common Issues and Solutions

#### Issue: "Python is not recognized"
**Solution:** 
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to system PATH

#### Issue: "Port 8002 already in use"
**Solution:**
```cmd
# Kill process on port 8002
netstat -ano | findstr :8002
taskkill /F /PID [process_id]
```

#### Issue: "Historical Data Manager returns 404"
**Solution:** 
- The backend needs the fixed version
- Run `MASTER_STARTUP_WIN11.bat` to ensure correct backend starts

#### Issue: "pip install fails"
**Solution:**
```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# Install with user flag
pip install --user [package_name]
```

#### Issue: "Windows Defender blocks execution"
**Solution:**
1. Right-click script > Properties
2. Check "Unblock" at bottom
3. Click OK

## 📁 Project Structure

```
clean_install_windows11/
├── START_STOCK_TRACKER.bat      # Universal launcher
├── MASTER_STARTUP_WIN11.bat     # Main startup script (CMD)
├── MASTER_STARTUP_WIN11.ps1     # PowerShell version
├── TROUBLESHOOT_WIN11.bat       # Diagnostic tool
├── backend.py                   # Fixed backend with all endpoints
├── index.html                   # Main frontend
├── modules/                     # Application modules
│   ├── historical_data_manager.html
│   ├── prediction_centre_phase4.html
│   └── ... other modules
├── historical_data/             # Downloaded stock data (CSV)
├── logs/                        # Service log files
│   ├── frontend.log
│   ├── backend.log
│   └── ml_backend.log
└── uploads/                     # Document uploads

```

## ✅ Verification Checklist

After running the startup script, verify:

- [ ] Browser opens automatically
- [ ] Main dashboard loads
- [ ] Stock prices update
- [ ] Historical Data Manager works
- [ ] Can download stock data
- [ ] Statistics show cached symbols
- [ ] No error messages in console

## 🛠️ Manual Service Control

### Start Individual Services

**Frontend Only:**
```cmd
python -m http.server 8000
```

**Backend Only:**
```cmd
python backend.py
```

**ML Backend Only:**
```cmd
python ml_backend.py
```

### Stop All Services
Close the master control window or press Ctrl+C

### View Logs
```cmd
# Frontend logs
type logs\frontend.log

# Backend logs
type logs\backend.log

# ML Backend logs
type logs\ml_backend.log
```

## 📈 Performance Tips

1. **First Launch:** May take 30-60 seconds to install packages
2. **Subsequent Launches:** Should start in 10-15 seconds
3. **Browser Cache:** Clear with Ctrl+F5 if pages don't update
4. **Memory Usage:** Each service uses ~100-200MB RAM
5. **CPU Usage:** Low when idle, spikes during data downloads

## 🔐 Security Notes

- Services run locally (localhost only)
- No external access by default
- Add firewall rules if remote access needed
- Keep Python packages updated

## 📞 Support

If issues persist after troubleshooting:

1. Run `TROUBLESHOOT_WIN11.bat` and note all errors
2. Check `logs/` folder for detailed error messages
3. Verify all files are present in correct structure
4. Ensure antivirus isn't blocking Python

## 🎉 Success Indicators

You know everything is working when:
- ✅ Console shows "SYSTEM READY TO USE!"
- ✅ All 3 services show [RUNNING]
- ✅ Browser opens automatically
- ✅ Stock prices load in dashboard
- ✅ Historical Data Manager downloads work

---

**Last Updated:** October 2024
**Version:** 4.1.0 (Windows 11 Optimized)
**Status:** Production Ready