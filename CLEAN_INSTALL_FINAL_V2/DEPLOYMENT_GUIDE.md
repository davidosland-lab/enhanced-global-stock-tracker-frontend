# Stock Tracker Pro - Deployment Guide

## 📦 Clean Install Package Contents

This package contains a complete, production-ready stock tracker system with all recent fixes applied.

### What's Fixed
- ✅ Backend health endpoint for connectivity
- ✅ ADST timezone display (UTC+11)
- ✅ International market time offsets (FTSE +11h, S&P +16h)
- ✅ Document analyzer with FinBERT and caching
- ✅ 100MB file upload support
- ✅ All APIs hardcoded to localhost
- ✅ No synthetic/demo data - Yahoo Finance only

---

## 🚀 Deployment Steps

### Step 1: Extract Package
```
1. Create installation directory: C:\StockTracker
2. Extract all files to C:\StockTracker
3. Verify all files are present (see file list below)
```

### Step 2: Install Python (if needed)
```
1. Download Python 3.8+ from python.org
2. During installation, check "Add Python to PATH"
3. Verify: python --version
```

### Step 3: Install Dependencies
```batch
cd C:\StockTracker
INSTALL.bat
```

### Step 4: Start Services
```batch
START_ALL_SERVICES.bat
```

### Step 5: Verify Installation
```batch
python TEST_SYSTEM.py
```

### Step 6: Access Application
```
Open browser to: http://localhost:8000
```

---

## 📁 File Checklist

Ensure all these files are present:

### Core Files
- [ ] backend.py - Main API server
- [ ] backend_core.py - Stock data functions
- [ ] document_analyzer.py - FinBERT module
- [ ] ml_backend.py - ML service

### Frontend Files
- [ ] index.html - Main dashboard
- [ ] market_tracker.html - Market tracking with ADST

### Scripts
- [ ] START_ALL_SERVICES.bat - Startup script
- [ ] INSTALL.bat - Installation script
- [ ] TEST_SYSTEM.py - System test

### Documentation
- [ ] README.md - Main documentation
- [ ] DEPLOYMENT_GUIDE.md - This file
- [ ] requirements.txt - Python packages

---

## 🔧 Configuration

### Ports
Default ports (can be changed if needed):
- Frontend: 8000
- Backend API: 8002
- ML Backend: 8003

To change ports, edit:
1. START_ALL_SERVICES.bat - Update port numbers
2. index.html - Update API_BASE and ML_API
3. backend.py - Update uvicorn.run() port
4. ml_backend.py - Update uvicorn.run() port

### Data Directories
Created automatically on startup:
- historical_data/ - Historical market data
- uploads/ - Uploaded documents
- analysis_cache/ - Document analysis cache
- ml_models/ - Trained ML models

---

## 🌐 Network Configuration

### For Local Network Access
To access from other computers on your network:

1. Find your IP address:
```batch
ipconfig
```
Look for IPv4 Address (e.g., 192.168.1.100)

2. Windows Firewall - Add exceptions for ports:
```
- TCP Port 8000 (Frontend)
- TCP Port 8002 (Backend)
- TCP Port 8003 (ML Backend)
```

3. Access from other devices:
```
http://[YOUR-IP]:8000
```

### Security Note
For production deployment:
- Use proper authentication
- Enable HTTPS
- Restrict CORS origins
- Use environment variables for sensitive data

---

## 📊 Performance Optimization

### First Run
- FinBERT model downloads on first use (~400MB)
- Initial load may take 30-60 seconds
- Subsequent runs are faster (model cached)

### Caching
- Stock data: 5-minute cache
- Document analysis: Permanent until cleared
- Clear cache: Delete files in analysis_cache/

### Resource Usage
- RAM: ~2GB with FinBERT loaded
- CPU: Moderate during analysis
- Disk: ~1GB for models and cache

---

## 🔍 Verification Tests

### 1. Service Health
All three should show as running:
```
http://localhost:8000 - Frontend
http://localhost:8002/api/health - Backend
http://localhost:8003/health - ML Backend
```

### 2. Data Verification
Check CBA.AX price:
```
http://localhost:8002/api/stock/CBA.AX
```
Should show ~$170 (real market price)

### 3. Time Display
Market tracker should show:
- Current time in ADST
- Correct market hours:
  - ASX: 10:00-16:00 ADST
  - FTSE: 19:00-03:30 ADST
  - S&P: 01:30-08:00 ADST

### 4. Document Analysis
Upload a test document:
- Should return consistent sentiment
- Same file = same result

---

## 🛠️ Troubleshooting

### Services Won't Start
```batch
# Check if Python is installed
python --version

# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :8002
netstat -ano | findstr :8003

# Kill existing processes if needed
taskkill /F /PID [PID_NUMBER]
```

### Import Errors
```batch
# Reinstall requirements
pip install -r requirements.txt --upgrade

# For FinBERT issues
pip install transformers torch --upgrade
```

### Connection Refused
1. Check Windows Firewall
2. Verify services are running (check console windows)
3. Try 127.0.0.1 instead of localhost

### Wrong Data/Prices
1. Check internet connection
2. Verify Yahoo Finance is accessible
3. Clear cache and restart

---

## 📝 Maintenance

### Daily
- Monitor service console windows for errors
- Check disk space for cache/uploads

### Weekly
- Clear old cache files if needed
- Review uploaded documents
- Check for Python package updates

### Monthly
- Update requirements: `pip list --outdated`
- Backup historical_data folder
- Review system logs

---

## 🚨 Important Notes

1. **Production Use**: This is a development setup. For production:
   - Use proper process managers (PM2, Supervisor)
   - Implement authentication
   - Use HTTPS certificates
   - Set up monitoring

2. **Data Source**: Uses Yahoo Finance API
   - Subject to rate limits
   - Requires internet connection
   - Data may be delayed (15-20 min)

3. **Legal**: Ensure compliance with:
   - Yahoo Finance terms of service
   - Financial data regulations
   - Document privacy requirements

---

## 📞 Quick Reference

### Start Everything
```batch
START_ALL_SERVICES.bat
```

### Test System
```batch
python TEST_SYSTEM.py
```

### Access Dashboard
```
http://localhost:8000
```

### Stop Services
```
Close all console windows or:
taskkill /F /IM python.exe
```

---

**Stock Tracker Pro v5.0.0** - Complete Clean Install Package