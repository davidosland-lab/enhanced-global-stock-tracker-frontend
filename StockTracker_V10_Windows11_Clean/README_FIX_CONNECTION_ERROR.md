# FIX: Connection Refused Error

## ❌ The Problem
You're seeing: `Failed to load resource: net::ERR_CONNECTION_REFUSED`

This means the backend server is not running. The HTML interface is trying to connect to `localhost:8000` but nothing is listening on that port.

## ✅ Quick Solution

### Option 1: Use the Simplified Version (RECOMMENDED)

1. **Open Command Prompt or PowerShell**
2. **Navigate to the StockTracker folder**:
   ```
   cd C:\path\to\StockTracker_V10_Windows11_Clean
   ```
3. **Run the simple start script**:
   ```
   START_SIMPLE.bat
   ```
   
This will:
- Install required packages automatically
- Start the unified backend on port 8000
- Open your browser automatically

### Option 2: Manual Start

1. **Open Command Prompt**
2. **Navigate to the folder**:
   ```
   cd C:\path\to\StockTracker_V10_Windows11_Clean
   ```
3. **Install requirements**:
   ```
   pip install fastapi uvicorn pandas numpy yfinance scikit-learn beautifulsoup4 aiohttp
   ```
4. **Run the unified backend**:
   ```
   python unified_backend.py
   ```
5. **Open browser** to: http://localhost:8000/prediction_center_fixed.html

## 🔍 Why This Happened

The original setup had multiple services (ports 8000-8006) that needed to be started separately. This is complex for Windows deployment. The HTML was trying to connect to these services but they weren't running.

## 🎯 What's Different Now

I've created a **Unified Backend** (`unified_backend.py`) that:
- Runs ALL services on a single port (8000)
- Includes ML, sentiment, backtesting, everything
- Simpler to start and manage
- Works immediately with the HTML interface

## 📋 Step-by-Step Instructions

### Step 1: Start the Server
```batch
START_SIMPLE.bat
```

You should see:
```
================================================
   STOCK TRACKER - SIMPLIFIED VERSION
================================================
Installing required packages...
Starting Stock Tracker on port 8000...
```

### Step 2: Wait for Server to Start
The console will show:
```
STOCK TRACKER UNIFIED BACKEND
==================================================
FinBERT: Not Available (or Available if installed)
XGBoost: Not Available (or Available if installed)
==================================================
Starting server on http://localhost:8000
```

### Step 3: Browser Opens Automatically
After 5 seconds, your browser will open to the prediction center.

### Step 4: Test the Server (Optional)
In a new command prompt:
```
python test_server.py
```

This will verify all endpoints are working.

## 🛠️ Troubleshooting

### Still getting connection refused?

1. **Check if port 8000 is in use**:
   ```
   netstat -an | findstr :8000
   ```
   If something is using it, stop that process.

2. **Check Python version**:
   ```
   python --version
   ```
   Need Python 3.8 or higher.

3. **Check if server is running**:
   Look for the command prompt window running `unified_backend.py`
   It should stay open and show log messages.

4. **Firewall blocking?**:
   Windows Firewall might block Python. Allow it when prompted.

### Server starts but features don't work?

Some features require additional packages:

**For FinBERT sentiment** (optional):
```
pip install transformers torch
```

**For XGBoost** (optional):
```
pip install xgboost
```

These are optional - the system works without them.

## ✨ What Works in Simplified Version

- ✅ Stock data fetching (Yahoo Finance)
- ✅ ML training (RandomForest, GradientBoost)
- ✅ Predictions
- ✅ Basic sentiment analysis
- ✅ Technical indicators
- ✅ Simple backtesting
- ✅ All on single port 8000

## 📝 File Structure

```
Your Folder/
├── START_SIMPLE.bat          <-- RUN THIS FIRST
├── unified_backend.py        <-- All-in-one server
├── prediction_center_fixed.html  <-- UI interface
├── test_server.py           <-- Test if working
└── README_FIX_CONNECTION_ERROR.md  <-- This file
```

## 🚀 Quick Start Commands

```batch
# 1. Start server
START_SIMPLE.bat

# 2. Or manually
python unified_backend.py

# 3. Test it
python test_server.py

# 4. Access UI
http://localhost:8000/prediction_center_fixed.html
```

## ❓ FAQ

**Q: Do I need to run all those other Python files?**
A: No! The `unified_backend.py` includes everything in one file.

**Q: Can I still use the multi-service setup?**
A: Yes, but it's more complex. Use `START_ALL_SERVICES.bat` instead.

**Q: Why is training slow?**
A: It's real ML training, not fake. Takes 10-60 seconds.

**Q: Do I need FinBERT?**
A: No, it's optional. System works without it.

## 🎉 Success!

Once the server is running, you should be able to:
1. Train models on any stock
2. Make predictions
3. See sentiment analysis
4. Run backtests
5. View technical indicators

All without connection refused errors!

---

**Remember**: The server (unified_backend.py) must be running BEFORE opening the HTML file!