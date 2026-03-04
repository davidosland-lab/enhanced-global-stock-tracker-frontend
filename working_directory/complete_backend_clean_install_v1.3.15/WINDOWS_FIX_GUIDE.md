# 🔧 WINDOWS INSTALLATION FIX GUIDE

## Issue: UnicodeDecodeError when starting dashboard

**Error Message:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

**Cause:** The `.env` file has encoding issues (BOM or non-UTF-8 encoding) that Flask cannot read.

---

## 🚀 QUICK FIX (3 Solutions)

### Solution 1: Use Fixed Launcher Script (Recommended)

```bash
# Run the fixed Python launcher
python start_dashboard_fixed.py
```

This script bypasses .env file loading entirely and uses default settings.

**Access dashboard at:** http://localhost:5002

---

### Solution 2: Use Fixed Batch Script (Windows)

```bash
# Double-click or run from command prompt
START_DASHBOARD_FIXED.bat
```

This batch file:
1. Creates a clean .env file with proper encoding
2. Sets environment variables to skip dotenv loading
3. Starts the dashboard

**Access dashboard at:** http://localhost:5002

---

### Solution 3: Manual Fix

#### Step 1: Delete existing .env file
```bash
del .env
```

#### Step 2: Create new .env file with Notepad
1. Open Notepad (not Notepad++)
2. Copy and paste this content:

```
# Flask Configuration
FLASK_SECRET_KEY=your-secure-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5002

# Regime Intelligence Settings
REGIME_WEIGHT=0.20
CONFIDENCE_THRESHOLD=0.30
ADAPTIVE_WEIGHTS=True

# Authentication (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123

# Logging
LOG_LEVEL=INFO
```

3. Save as `.env` (including the dot)
4. In "Save as type" dropdown, select "All Files (*.*)"
5. Encoding: select "UTF-8" (NOT "UTF-8 with BOM")
6. Click Save

#### Step 3: Run dashboard normally
```bash
python regime_dashboard.py
```

**Access dashboard at:** http://localhost:5002

---

## 📋 ALTERNATIVE: Run Without .env File

The dashboard can run without a .env file using default settings:

```bash
# Set environment variable and run
set FLASK_SKIP_DOTENV=1
python regime_dashboard.py
```

Or use the modified script:
```bash
python start_dashboard_fixed.py
```

---

## 🔍 VERIFICATION

After applying any fix above, you should see:

```
===============================================================================
 REGIME INTELLIGENCE DASHBOARD - LIVE
 Version: v1.3.13 (Week 2)
 Starting server on http://0.0.0.0:5002
===============================================================================

Initializing regime intelligence components...
✓ Market Data Fetcher initialized
✓ Market Regime Detector initialized
✓ Enhanced Data Sources initialized
✓ Cross-Market Features initialized

Dashboard Features:
   - Live market regime detection
   - Real-time market data monitoring
   - Sector impact visualization
   - Cross-market feature display
   - Auto-refresh every 5 minutes

================================================================================

Press Ctrl+C to stop the server

 * Running on http://0.0.0.0:5002
```

---

## 🌐 ACCESSING THE DASHBOARD

Once running, open your web browser and go to:

- **Local access:** http://localhost:5002
- **Network access:** http://127.0.0.1:5002
- **From other devices:** http://YOUR_IP_ADDRESS:5002

---

## 🐛 STILL HAVING ISSUES?

### Issue: Port already in use
```
OSError: [Errno 48] Address already in use
```

**Solution:** Kill existing process or use different port
```bash
# Find process using port 5002
netstat -ano | findstr :5002

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in start_dashboard_fixed.py (line 54)
app.run(host='0.0.0.0', port=5003, debug=False, load_dotenv=False)
```

### Issue: Module not found
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Cannot import regime modules
```
ImportError: cannot import name 'MarketDataFetcher'
```

**Solution:** Verify directory structure and ensure models/ folder exists
```bash
# Check if models folder exists
dir models

# Should show:
# market_data_fetcher.py
# market_regime_detector.py
# enhanced_data_sources.py
# cross_market_features.py
```

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- **Complete Installation Guide:** COMPLETE_INSTALLATION_GUIDE.md
- **Package README:** README_COMPLETE_BACKEND.md
- **Quick Start:** QUICK_START.md

### Support
- **GitHub Issues:** https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/issues
- **Pull Request:** https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/11

---

## ✅ SUMMARY OF FIX

The issue was caused by:
1. `.env` file with incorrect encoding (UTF-8 BOM or non-UTF-8)
2. Flask trying to load and parse the corrupted file
3. Python's UTF-8 codec failing on invalid byte sequences

The solutions provided:
1. ✅ **start_dashboard_fixed.py** - Bypasses .env loading completely
2. ✅ **START_DASHBOARD_FIXED.bat** - Creates clean .env and starts dashboard
3. ✅ **Manual fix** - Recreate .env with proper UTF-8 encoding
4. ✅ **Modified regime_dashboard.py** - Added load_dotenv=False parameter

---

## 🚀 RECOMMENDED APPROACH

**For immediate use:**
```bash
python start_dashboard_fixed.py
```

**For long-term use:**
1. Fix the .env file encoding (Solution 3)
2. Or continue using start_dashboard_fixed.py (no configuration needed)

---

**Version:** v1.3.13 - Windows Compatibility Fix  
**Date:** January 6, 2026  
**Status:** ✅ TESTED & WORKING

---

**Next Steps:**
1. Start dashboard using one of the solutions above
2. Open http://localhost:5002 in browser
3. Verify regime detection is working
4. Review configuration in COMPLETE_INSTALLATION_GUIDE.md

---

🚀 **TRADE SMARTER WITH REGIME INTELLIGENCE!**
