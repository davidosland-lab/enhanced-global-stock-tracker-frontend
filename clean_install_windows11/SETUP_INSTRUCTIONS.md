# 📋 Windows 11 Stock Tracker - Complete Setup Instructions

## 🎯 Quick Start Guide

### Step 1: Verify Files
Ensure you have these files in your directory:
- `backend.py` - Main backend server
- `historical_data_manager.py` - SQLite local storage
- `index.html` - Landing page
- `modules/` folder with all HTML modules

### Step 2: Install Requirements
```bash
pip install fastapi uvicorn yfinance pandas numpy cachetools pytz python-multipart aiofiles websockets python-dotenv
```

### Step 3: Initialize SQLite Database
```bash
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('Database initialized')"
```

### Step 4: Run the Backend
```bash
python backend.py
```

Or use the launcher:
```bash
python launch_advanced.py
```

### Step 5: Access the Application
Open browser to: http://localhost:8002

---

## 🔧 Detailed Setup Instructions

### 1. Prerequisites
- **Python 3.8+** installed
- **pip** package manager
- **Windows 11** (or any OS with Python)

### 2. Complete Installation

#### Option A: Using requirements.txt
Create a `requirements.txt` file:
```txt
fastapi==0.104.1
uvicorn==0.24.0
yfinance==0.2.33
pandas==2.1.3
numpy==1.24.3
cachetools==5.3.2
pytz==2023.3
python-multipart==0.0.6
aiofiles==23.2.1
websockets==12.0
python-dotenv==1.0.0
pydantic==2.5.0
```

Then install:
```bash
pip install -r requirements.txt
```

#### Option B: Direct Installation
```bash
pip install fastapi uvicorn yfinance pandas numpy cachetools pytz python-multipart aiofiles websockets python-dotenv pydantic
```

### 3. Database Initialization

The SQLite database needs to be initialized for local storage (100x faster backtesting):

```python
# Run this Python script once to initialize:
from historical_data_manager import HistoricalDataManager

# Initialize the database
hdm = HistoricalDataManager()
print("Database initialized at:", hdm.db_dir)

# Optional: Pre-load some data
symbols = ['CBA.AX', 'AAPL', '^AORD', '^GSPC', '^FTSE']
for symbol in symbols:
    try:
        hdm.update_symbol(symbol, period='1mo')
        print(f"Loaded data for {symbol}")
    except Exception as e:
        print(f"Could not load {symbol}: {e}")
```

### 4. Backend Configuration

The backend should automatically detect and load the Historical Data Manager. Check the console output when starting:

**Expected output:**
```
📦 Historical Data Manager initialized at historical_data
Historical Data Manager initialized - 100x faster backtesting enabled
Starting Complete Stock Tracker Backend on port 8002
Access the API at http://localhost:8002
API documentation at http://localhost:8002/docs
```

**If you see this instead:**
```
⚠️  Historical Data Manager not available: [error]
```

Then the SQLite integration is not working.

### 5. Troubleshooting

#### Problem: "Historical Data Manager not available"
**Solution:**
1. Ensure `historical_data_manager.py` is in the same directory as `backend.py`
2. Check Python imports:
```python
python -c "import sqlite3; print('SQLite available')"
```

#### Problem: "Database locked" error
**Solution:**
```bash
# Remove old database and reinitialize
rm -rf historical_data/
python -c "from historical_data_manager import HistoricalDataManager; HistoricalDataManager()"
```

#### Problem: Backend doesn't import Historical Data Manager
**Solution:**
Add this to the top of `backend.py` after the logging setup:
```python
# Import Historical Data Manager for local storage
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from historical_data_manager import HistoricalDataManager
    hdm = HistoricalDataManager()
    HISTORICAL_DATA_MANAGER = True
    logger.info("Historical Data Manager initialized - 100x faster backtesting enabled")
except ImportError as e:
    HISTORICAL_DATA_MANAGER = False
    logger.warning(f"Historical Data Manager not available: {e}")
```

### 6. Verify Installation

Run this verification script:
```python
# verify_setup.py
import sys

print("Checking dependencies...")

# Check required packages
packages = {
    'fastapi': 'FastAPI',
    'uvicorn': 'Uvicorn',
    'yfinance': 'Yahoo Finance',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'sqlite3': 'SQLite3'
}

for module, name in packages.items():
    try:
        if module == 'sqlite3':
            import sqlite3
        else:
            __import__(module)
        print(f"✅ {name} - installed")
    except ImportError:
        print(f"❌ {name} - NOT installed")

# Check Historical Data Manager
try:
    from historical_data_manager import HistoricalDataManager
    hdm = HistoricalDataManager()
    print("✅ Historical Data Manager - initialized")
    print(f"   Database location: {hdm.db_dir}")
except Exception as e:
    print(f"❌ Historical Data Manager - {e}")

# Check backend
try:
    import backend
    print("✅ Backend - can be imported")
except Exception as e:
    print(f"❌ Backend - {e}")

print("\nSetup verification complete!")
```

### 7. Running the Complete System

#### Windows Command Prompt:
```cmd
cd C:\path\to\clean_install_windows11
python backend.py
```

#### Windows PowerShell:
```powershell
cd C:\path\to\clean_install_windows11
python .\backend.py
```

#### Using the Launcher:
```bash
python launch_advanced.py
```

### 8. Accessing the Modules

Once running, access these URLs:

- **Main Dashboard**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **CBA Enhanced**: http://localhost:8002/modules/cba_enhanced.html
- **Phase 4 Predictor**: http://localhost:8002/modules/prediction_centre_phase4.html
- **Document Analyzer**: http://localhost:8002/modules/document_uploader.html

### 9. Features Checklist

Verify these features are working:

- [ ] Backend starts on port 8002
- [ ] SQLite database initialized (check for `historical_data/` folder)
- [ ] CBA.AX shows ~$170 price
- [ ] Phase 4 predictor loads
- [ ] Document uploader accessible
- [ ] Backtesting runs fast (using local data)
- [ ] All 5 modules accessible from landing page

### 10. Performance Optimization

For best performance with SQLite:

1. **Pre-load frequently used symbols:**
```python
from historical_data_manager import HistoricalDataManager
hdm = HistoricalDataManager()

# Pre-load data for faster access
symbols = ['CBA.AX', 'BHP.AX', 'ANZ.AX', 'WBC.AX', 'NAB.AX']
for symbol in symbols:
    hdm.update_symbol(symbol, period='3mo')
```

2. **Set up automatic updates:**
```python
# Add to backend startup
import threading
import time

def update_data_periodically():
    while True:
        time.sleep(3600)  # Update every hour
        try:
            hdm.update_all_symbols()
        except:
            pass

threading.Thread(target=update_data_periodically, daemon=True).start()
```

---

## 📦 Complete File List

Your `clean_install_windows11` folder should contain:

```
clean_install_windows11/
├── backend.py                      # Main backend (19KB)
├── historical_data_manager.py      # SQLite storage (20KB)
├── launch_advanced.py              # Advanced launcher
├── index.html                      # Landing page
├── SETUP_INSTRUCTIONS.md           # This file
├── historical_data/                # SQLite database (created on first run)
│   └── market_data.db
└── modules/
    ├── cba_enhanced.html           # CBA tracker with all features
    ├── prediction_centre_phase4.html
    ├── stock_tracker.html
    ├── global_market_tracker.html
    ├── technical_analysis.html
    ├── document_uploader.html
    └── prediction_performance_dashboard.html
```

---

## ✅ Success Indicators

You know everything is working when you see:

1. **Console output shows:**
   - "Historical Data Manager initialized"
   - "Starting Complete Stock Tracker Backend on port 8002"

2. **Browser shows:**
   - Backend status: "Connected"
   - CBA.AX price around $170
   - All 5 module cards on landing page

3. **File system shows:**
   - `historical_data/` folder created
   - `market_data.db` file inside it

---

## 🆘 Need Help?

If SQLite is still not loading, run this diagnostic:
```bash
python -c "import backend; print('Backend loaded'); from historical_data_manager import HistoricalDataManager; print('HDM loaded'); hdm = HistoricalDataManager(); print('Database ready')"
```

This will show exactly where the issue is occurring.