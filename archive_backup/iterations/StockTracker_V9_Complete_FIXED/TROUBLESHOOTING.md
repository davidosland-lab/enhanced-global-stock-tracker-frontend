# Troubleshooting Guide - Stock Tracker V9

## 🔧 Installation Error: "Cannot import 'setuptools.build_meta'"

### Problem
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

### Solutions (Try in Order)

#### Solution 1: Run FIX_SETUPTOOLS.bat
```batch
1. Double-click FIX_SETUPTOOLS.bat
2. Wait for it to complete
3. Run INSTALL_WINDOWS.bat again
```

#### Solution 2: Use QUICK_START.bat
```batch
1. Double-click QUICK_START.bat
2. This installs packages without version constraints
3. Should work on most systems
```

#### Solution 3: Manual Fix
```batch
# Open Command Prompt as Administrator
# Navigate to the project folder
cd C:\Users\david\OneDrive\Desktop\StockTrack\StockTracker_V9_Complete_FIXED

# Remove old virtual environment
rmdir /s /q venv

# Create new one
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install requirements one by one
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install pandas
python -m pip install numpy
python -m pip install yfinance
python -m pip install scikit-learn
python -m pip install joblib
python -m pip install aiohttp
python -m pip install python-multipart
python -m pip install ta
```

#### Solution 4: Use Python 3.11
If you have Python 3.12+, there might be compatibility issues. Try:
1. Uninstall current Python
2. Install Python 3.11 from python.org
3. Check "Add Python to PATH" during installation
4. Run QUICK_START.bat

---

## 🔧 Service Errors

### "Port already in use"
```batch
# Kill Python processes on the ports
netstat -ano | findstr :8002
taskkill /F /PID [PID_NUMBER]

# Or use Task Manager
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find python.exe processes
3. End them
4. Run START_WINDOWS.bat again
```

### "Module not found" errors
```batch
# Run TEST_SERVICES.bat to check what's missing
TEST_SERVICES.bat

# Install missing modules individually
venv\Scripts\activate.bat
python -m pip install [missing_module]
```

---

## 🔧 Runtime Errors

### Prediction Error 500
**Cause**: No trained models exist yet

**Solution**: 
1. Open prediction_center.html
2. Enter a stock symbol (e.g., AAPL)
3. Click "Train New Model"
4. Wait 10-60 seconds for training
5. Then try predictions

### FinBERT Not Working
**This is optional** - the system works without it

If you want FinBERT:
```batch
venv\Scripts\activate.bat
python -m pip install transformers torch
# This downloads ~2GB, takes 5-10 minutes
```

Otherwise, keyword-based sentiment analysis will be used automatically.

### XGBoost Not Installing
**This is optional** - RandomForest works great without it

If XGBoost fails to install:
1. The system will use RandomForest (default)
2. No functionality is lost
3. You can ignore XGBoost errors

---

## 🔧 Windows-Specific Issues

### "Python not found"
1. Install Python from python.org
2. **Important**: Check "Add Python to PATH" during installation
3. Restart Command Prompt after installation

### "Access Denied" errors
1. Run Command Prompt as Administrator
2. Or move project folder out of OneDrive to C:\StockTracker

### OneDrive sync issues
OneDrive can cause problems with virtual environments
```batch
# Move project to a non-synced location
xcopy /E /I "C:\Users\david\OneDrive\Desktop\StockTrack\StockTracker_V9_Complete_FIXED" "C:\StockTracker"
cd C:\StockTracker
QUICK_START.bat
```

---

## 🚀 Quick Test After Installation

Run these commands to verify everything works:

```batch
# Test if services are responding
curl http://localhost:8002/
curl http://localhost:8003/api/ml/status
curl http://localhost:8004/api/sentiment/status
curl http://localhost:8005/
```

Or open in browser:
- http://localhost:8002/ - Should show "Stock Tracker Main Backend"
- http://localhost:8003/ - Should show "Enhanced ML Backend"
- http://localhost:8004/ - Should show "FinBERT Sentiment Analysis"
- http://localhost:8005/ - Should show "Backtesting Module"

---

## 📊 Database Files

If you see "database locked" errors:
1. Close all Python processes
2. Delete these files (they'll be recreated):
   - models.db
   - historical_cache.db
   - sentiment_cache.db
   - backtest_results.db
3. Restart services

---

## 💡 Best Practices

1. **Use QUICK_START.bat for easiest installation**
   - Works on most systems
   - Installs packages without version conflicts

2. **Run TEST_SERVICES.bat before starting**
   - Shows what's installed
   - Identifies missing components

3. **Don't worry about optional packages**
   - XGBoost: Optional, RandomForest works great
   - FinBERT: Optional, keyword analysis works fine
   - TA library: Optional but recommended

4. **If all else fails**
   - Use Python 3.11 (most compatible)
   - Install outside OneDrive folder
   - Run as Administrator

---

## 📞 Still Having Issues?

If none of the above works:

1. **System Information Needed:**
   - Windows version (run `winver`)
   - Python version (run `python --version`)
   - Error messages (full text)

2. **Clean Installation Steps:**
   ```batch
   # Complete clean install
   1. Uninstall Python
   2. Restart computer
   3. Install Python 3.11 from python.org
   4. Download fresh copy of StockTracker_V9
   5. Extract to C:\StockTracker (not in OneDrive)
   6. Run QUICK_START.bat
   ```

3. **Minimal Test:**
   Create a test file `test.py`:
   ```python
   import sys
   print(f"Python: {sys.version}")
   try:
       import fastapi
       print("FastAPI: OK")
   except:
       print("FastAPI: Missing")
   ```
   Run: `python test.py`

---

Remember: The system is designed to work even without optional components. Focus on getting the core services running first!