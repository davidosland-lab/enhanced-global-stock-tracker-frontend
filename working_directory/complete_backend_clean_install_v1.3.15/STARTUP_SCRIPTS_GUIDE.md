# 🚀 STARTUP SCRIPTS GUIDE - Windows

## Two Simple Scripts for Windows Users

We provide two batch scripts to make starting the dashboard easy on Windows:

---

## 1️⃣ FIRST_TIME_SETUP.bat

**Use this script ONCE when you first install the system.**

### What it does:
1. ✅ Checks Python installation
2. ✅ Installs all dependencies automatically
3. ✅ Creates configuration files
4. ✅ Creates data directories
5. ✅ Runs integration tests
6. ✅ Offers to start dashboard immediately

### How to use:
```bash
# 1. Extract the package
unzip complete_backend_clean_install_v1.3.13.zip
cd complete_backend_clean_install_v1.3.13

# 2. Double-click FIRST_TIME_SETUP.bat
# OR run from command prompt:
FIRST_TIME_SETUP.bat
```

### What you'll see:
```
═══════════════════════════════════════════════════════════════════
 REGIME INTELLIGENCE DASHBOARD - FIRST TIME SETUP
 Version: v1.3.13 - Complete Backend Package
═══════════════════════════════════════════════════════════════════

✓ Python found: Python 3.12.0
✓ pip found: pip 23.x

STEP 1: Installing Python Dependencies
Installing... (this may take 2-3 minutes)
✓ All dependencies installed successfully

STEP 2: Creating Configuration Files
✓ Created data directories
✓ Created .env configuration file

STEP 3: Running Integration Tests
✓ All integration tests passed!

STEP 4: System Information
Package: Complete Backend Clean Install v1.3.13
Coverage: 720 stocks across AU/US/UK markets

✅ FIRST TIME SETUP COMPLETE!

Would you like to start the dashboard now? (Y/N)
```

### Time required: 3-5 minutes
- Dependency installation: 2-3 minutes
- Configuration setup: < 1 minute
- Integration tests: < 1 minute

---

## 2️⃣ START_DASHBOARD.bat

**Use this script EVERY TIME you want to start the dashboard after first setup.**

### What it does:
1. ✅ Verifies Python is available
2. ✅ Quick dependency check
3. ✅ Shows dashboard information
4. ✅ Starts the dashboard server
5. ✅ Keeps the server running until you stop it

### How to use:
```bash
# Navigate to the installation folder
cd complete_backend_clean_install_v1.3.13

# Double-click START_DASHBOARD.bat
# OR run from command prompt:
START_DASHBOARD.bat
```

### What you'll see:
```
═══════════════════════════════════════════════════════════════════
 REGIME INTELLIGENCE DASHBOARD - STARTUP
 Version: v1.3.13 - Complete Backend Package
═══════════════════════════════════════════════════════════════════

DASHBOARD INFORMATION
Features:
  • Live market regime detection (14 regime types)
  • Real-time market data monitoring
  • Sector impact visualization (8 sectors)
  • Cross-market features (15+ features)
  • Auto-refresh every 5 minutes

Coverage:
  • 720 stocks across 3 markets

Dashboard will be available at:
  http://localhost:5002

STARTING DASHBOARD SERVER...

✓ Configuration file found (.env)

Initializing components...
  • Market Data Fetcher
  • Market Regime Detector
  • Enhanced Data Sources
  • Cross-Market Features

═══════════════════════════════════════════════════════════════════
 DASHBOARD STARTING - DO NOT CLOSE THIS WINDOW
═══════════════════════════════════════════════════════════════════

Open your web browser and navigate to:
  http://localhost:5002

Press Ctrl+C to stop the dashboard server

 * Running on http://0.0.0.0:5002
```

### Time required: < 10 seconds
The dashboard starts almost immediately after running the script.

---

## 📋 USAGE WORKFLOW

### First Time Installation
```
1. Extract package
2. Run FIRST_TIME_SETUP.bat (once)
   ↓
   Installs dependencies
   Creates configuration
   Runs tests
   ↓
3. Dashboard ready to use!
```

### Regular Usage (Daily)
```
1. Run START_DASHBOARD.bat
   ↓
   Dashboard starts in < 10 seconds
   ↓
2. Open browser: http://localhost:5002
   ↓
3. Use dashboard
   ↓
4. Press Ctrl+C to stop when done
```

---

## 🎯 QUICK REFERENCE

### When to use FIRST_TIME_SETUP.bat:
- ✅ First installation
- ✅ After updating Python
- ✅ After reinstalling the system
- ✅ If dependencies are corrupted/missing

### When to use START_DASHBOARD.bat:
- ✅ Every day for normal use
- ✅ After system restart
- ✅ When you want to access the dashboard
- ✅ After closing the previous dashboard session

---

## 🔧 TROUBLESHOOTING

### "Python is not installed"
**Solution:** Install Python 3.8+ from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "Failed to install dependencies"
**Solution:** Check internet connection and run:
```bash
pip install -r requirements.txt
```

### "Some tests failed"
**Solution:** This may not prevent the dashboard from running.
- Press any key to continue
- Dashboard will likely work fine
- Check WINDOWS_FIX_GUIDE.md for details

### "Address already in use"
**Solution:** Port 5002 is occupied
```bash
# Find process using port 5002
netstat -ano | findstr :5002

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in start_dashboard_fixed.py
```

### "Module not found" errors
**Solution:** Re-run FIRST_TIME_SETUP.bat to reinstall dependencies

---

## 📚 ADDITIONAL RESOURCES

### For First Time Setup Issues:
- **COMPLETE_INSTALLATION_GUIDE.md** - Detailed installation guide
- **WINDOWS_FIX_GUIDE.md** - Windows-specific troubleshooting

### For Regular Usage:
- **README_COMPLETE_BACKEND.md** - Package overview
- **QUICK_START.md** - Quick reference guide

### For Advanced Users:
- **Manual startup:** `python start_dashboard_fixed.py`
- **Alternative startup:** `python regime_dashboard.py`
- **Production deployment:** See PRODUCTION_DEPLOYMENT_GUIDE.md

---

## 🎉 COMPARISON

| Feature | FIRST_TIME_SETUP.bat | START_DASHBOARD.bat |
|---------|----------------------|---------------------|
| **Use frequency** | Once | Every time |
| **Install dependencies** | ✅ Yes | ❌ No |
| **Create config files** | ✅ Yes | ❌ No |
| **Run tests** | ✅ Yes | ❌ No |
| **Start dashboard** | ✅ Optional | ✅ Always |
| **Time required** | 3-5 minutes | < 10 seconds |
| **User interaction** | Requires input | Automatic |

---

## 💡 PRO TIPS

1. **Create Desktop Shortcuts:**
   - Right-click START_DASHBOARD.bat
   - Select "Create shortcut"
   - Move shortcut to Desktop
   - Rename to "Regime Intelligence Dashboard"

2. **Run on Startup:**
   - Press Win+R
   - Type: `shell:startup`
   - Copy START_DASHBOARD.bat shortcut here
   - Dashboard starts automatically on login

3. **Multiple Terminals:**
   - Keep dashboard running in one terminal
   - Open second terminal for pipelines
   - Run RUN_AU_PIPELINE.bat in second terminal

4. **Network Access:**
   - Find your IP: `ipconfig`
   - Share with team: `http://YOUR_IP:5002`
   - Make sure firewall allows port 5002

---

## ✅ VERIFICATION

### After FIRST_TIME_SETUP.bat:
- [ ] All dependencies installed (no errors)
- [ ] Configuration files created (.env exists)
- [ ] Data directories created (data/cache, data/state, data/logs)
- [ ] Integration tests passed (or continued anyway)
- [ ] System information displayed

### After START_DASHBOARD.bat:
- [ ] Python check passed
- [ ] Configuration loaded
- [ ] Components initialized
- [ ] Server running on port 5002
- [ ] Can access http://localhost:5002
- [ ] Dashboard shows live data

---

## 🚀 READY TO START!

### First Time:
```bash
FIRST_TIME_SETUP.bat
```

### Every Time After:
```bash
START_DASHBOARD.bat
```

### Access Dashboard:
```
http://localhost:5002
```

---

**Version:** v1.3.13.1 - Windows Startup Scripts  
**Status:** ✅ PRODUCTION READY  
**Date:** January 6, 2026

🚀 **TRADE SMARTER WITH REGIME INTELLIGENCE!**
