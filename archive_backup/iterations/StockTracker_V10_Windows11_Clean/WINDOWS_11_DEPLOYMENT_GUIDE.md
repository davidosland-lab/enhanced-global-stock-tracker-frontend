# 🖥️ Windows 11 Local Deployment Guide

## ⚠️ IMPORTANT: This is for LOCAL Windows 11 deployment, NOT cloud/sandbox

## 📋 Prerequisites

### 1. Python Installation
- Python 3.8 or higher
- Add Python to PATH during installation
- Verify: `python --version`

### 2. Required Python Packages
```batch
pip install fastapi uvicorn pandas numpy yfinance scikit-learn
pip install requests aiohttp beautifulsoup4 feedparser
pip install transformers torch  # Optional for FinBERT
pip install xgboost  # Optional for XGBoost models
```

## 🚀 Quick Start

### Option 1: Automatic Start (Recommended)
```batch
cd C:\YourPath\StockTracker_V10_Windows11_Clean
START_ALL_SERVICES_WINDOWS.bat
```

### Option 2: Fix Web Scraper Issues
```batch
cd C:\YourPath\StockTracker_V10_Windows11_Clean
FIX_WEBSCRAPER_WINDOWS.bat
```

## 🔧 Troubleshooting Web Scraper on Windows 11

### Common Issue: "ERR_CONNECTION_REFUSED on port 8006"

#### Solution 1: Check Windows Firewall
1. Open Windows Security
2. Go to Firewall & network protection
3. Click "Allow an app through firewall"
4. Add Python.exe if not present
5. Check both Private and Public networks

#### Solution 2: Check if Port is Blocked
```batch
# Check what's using port 8006
netstat -aon | findstr :8006

# If something is using it, kill that process
taskkill /F /PID [PID_NUMBER]
```

#### Solution 3: Run as Administrator
1. Right-click on the .bat file
2. Select "Run as administrator"
3. This ensures proper port binding

#### Solution 4: Windows Defender/Antivirus
- Add exception for Python.exe
- Add exception for the StockTracker folder
- Temporarily disable real-time protection to test

#### Solution 5: Manual Start
```batch
# Open Command Prompt as Administrator
cd C:\YourPath\StockTracker_V10_Windows11_Clean

# Try each scraper until one works:
python web_scraper_real.py
# OR
python web_scraper_simple.py
# OR
python web_scraper_backend.py
```

## 📁 File Structure for Windows 11

```
C:\StockTracker\
├── StockTracker_V10_Windows11_Clean\
│   ├── *.py (Backend services)
│   ├── *.html (Frontend files)
│   ├── *.bat (Windows batch files)
│   ├── requirements.txt
│   └── models\ (ML models saved here)
```

## 🌐 Accessing the Application

### All services run on localhost:
- Main Dashboard: http://localhost:8000
- Historical API: http://localhost:8001  
- ML Backend: http://localhost:8002
- FinBERT: http://localhost:8003
- Backtesting: http://localhost:8005
- Web Scraper: http://localhost:8006

### Test URLs:
1. Main: http://localhost:8000
2. Prediction Center: http://localhost:8000/prediction_center.html
3. Sentiment Scraper: http://localhost:8000/sentiment_scraper.html

## ⚡ Performance Tips for Windows 11

### 1. Windows Security Exclusions
Add these folders to Windows Security exclusions:
- Your Python installation folder
- The StockTracker project folder
- `%TEMP%` folder (for temporary ML model files)

### 2. Power Settings
- Set to "High Performance" power plan
- Disable USB selective suspend
- Keep processor at 100% when plugged in

### 3. Network Settings
- Disable Windows Firewall temporarily for testing
- Or create specific inbound rules for ports 8000-8006

## 🐛 Debug Commands for Windows

### Check if services are running:
```batch
# Check all Python processes
tasklist | findstr python

# Check specific ports
netstat -aon | findstr :8000
netstat -aon | findstr :8001
netstat -aon | findstr :8002
netstat -aon | findstr :8003
netstat -aon | findstr :8005
netstat -aon | findstr :8006
```

### Test services with PowerShell:
```powershell
# Test web scraper
Invoke-WebRequest -Uri http://localhost:8006/health

# Test main backend
Invoke-WebRequest -Uri http://localhost:8000/health

# Test ML backend
Invoke-WebRequest -Uri http://localhost:8002/health
```

### Test with curl (if installed):
```batch
curl http://localhost:8006/health
curl -X POST http://localhost:8006/scrape -H "Content-Type: application/json" -d "{\"symbol\":\"AAPL\",\"sources\":[\"yahoo\"]}"
```

## 🔴 Critical Windows 11 Settings

### 1. Localhost Loopback
Enable localhost loopback (usually enabled by default):
```batch
# Run as Administrator
CheckNetIsolation LoopbackExempt -a -n="Microsoft.Win32WebViewHost_cw5n1h2txyewy"
```

### 2. Port Range
Windows 11 may reserve ports. Check reserved ports:
```batch
netsh int ipv4 show excludedportrange protocol=tcp
```

### 3. Reset Network Stack (if needed)
```batch
# Run as Administrator
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /renew
ipconfig /flushdns
```

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] All pip packages installed
- [ ] Windows Firewall configured
- [ ] Antivirus exceptions added
- [ ] Ports 8000-8006 available
- [ ] Running as Administrator (if needed)
- [ ] All .py files present in folder
- [ ] requirements.txt dependencies installed

## 📞 Final Test

After starting all services with `START_ALL_SERVICES_WINDOWS.bat`:

1. Open browser
2. Go to http://localhost:8000
3. Click on "Sentiment Scraper"
4. Enter "AAPL" as symbol
5. Click "Scrape Data"
6. Should see sentiment results

If this doesn't work, run `FIX_WEBSCRAPER_WINDOWS.bat` to diagnose and fix issues.

---
**Remember: This guide is for LOCAL Windows 11 deployment. All services use localhost, NOT external URLs.**