# Troubleshooting Guide - ML Stock Predictor on Windows

## Problem: localhost:8000 Not Connecting

### Step 1: Check if the server is running

The server won't be accessible until you start it. You need to:

1. **Open Command Prompt** in the ML_Stock_Windows_Clean folder
2. **Run the server**: `python ml_core_windows.py`

### Step 2: Installation Check

Before starting the server, make sure everything is installed:

```batch
# Run this first:
INSTALL_WINDOWS.bat
```

This will:
- Remove problematic packages (yfinance 0.2.33, curl_cffi)
- Install yfinance 0.2.18 (Windows compatible)
- Install all other dependencies

### Step 3: Test Yahoo Finance Connection

Run the test script to make sure Yahoo Finance is working:

```batch
python TEST_YAHOO_WINDOWS.py
```

You should see:
- ✓ yfinance 0.2.18 imported successfully
- ✓ curl_cffi is NOT installed (this is good!)
- ✓ Successfully fetched stock prices

### Step 4: Start the Server

Once tests pass, start the server:

```batch
python ml_core_windows.py
```

You should see:
```
==============================================================
ML Stock Predictor - Windows Compatible Version
==============================================================
Starting server on http://localhost:8000
This version works without curl_cffi
Requires: yfinance==0.2.18
==============================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Access the Server

Once running, open your browser and go to:
- **Main page**: http://localhost:8000
- **API docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'yfinance'"

**Solution**: Install requirements first
```batch
pip install -r requirements_windows.txt
```

### Issue 2: "Expecting value: line 1 column 1 (char 0)"

**Cause**: You still have yfinance 0.2.33 with broken curl_cffi

**Solution**: Downgrade yfinance
```batch
pip uninstall yfinance curl-cffi -y
pip install yfinance==0.2.18
```

### Issue 3: "Port 8000 is already in use"

**Cause**: Another application is using port 8000

**Solution**: 
1. Find what's using port 8000:
```batch
netstat -ano | findstr :8000
```

2. Kill the process or change the port in ml_core_windows.py:
```python
PORT = 8001  # Change to different port
```

### Issue 4: "ImportError: cannot import name 'Ticker' from 'yfinance'"

**Cause**: Corrupted yfinance installation

**Solution**: Clean reinstall
```batch
pip uninstall yfinance -y
pip cache purge
pip install yfinance==0.2.18
```

### Issue 5: Server starts but Yahoo Finance fails

**Symptoms**: Server runs but API calls return errors

**Solution**: Test Yahoo Finance separately
```python
import yfinance as yf

# If this fails, yfinance is not working
ticker = yf.Ticker("AAPL")
data = ticker.history(period="5d")
print(data)
```

If it fails, check:
1. Internet connection
2. Firewall/proxy settings
3. VPN (try disconnecting)

### Issue 6: "ValueError: No objects to concatenate"

**Cause**: Yahoo Finance returned empty data

**Solution**: This is usually temporary. Try:
1. Wait a few minutes
2. Try different stock symbols
3. Check if markets are open

## Quick Checklist

Run these commands in order:

```batch
# 1. Check Python version (should be 3.12.9 or similar)
python --version

# 2. Check yfinance version (should be 0.2.18)
python -c "import yfinance; print(yfinance.__version__)"

# 3. Check curl_cffi is NOT installed
python -c "import curl_cffi" 2>nul && echo BAD: curl_cffi is installed || echo GOOD: curl_cffi not installed

# 4. Test Yahoo Finance
python -c "import yfinance as yf; print(yf.Ticker('AAPL').history(period='1d'))"

# 5. Start server
python ml_core_windows.py
```

## If Everything Else Fails

1. **Create a fresh Python environment**:
```batch
python -m venv ml_env
ml_env\Scripts\activate
pip install yfinance==0.2.18 pandas numpy ta scikit-learn fastapi uvicorn
python ml_core_windows.py
```

2. **Use the diagnostic script**:
```batch
python yahoo_finance_windows_fix.py
```

This will identify the exact issue and provide specific fixes.

## Verification Steps

Once the server is running, test it:

1. **Browser Test**: Go to http://localhost:8000
2. **API Test**: Go to http://localhost:8000/docs and try the `/test/AAPL` endpoint
3. **Health Check**: Go to http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "version": "1.0",
  "windows_compatible": true,
  "yfinance_version": "0.2.18"
}
```

## Contact Points

If you're still having issues after trying all the above:

1. Check yfinance version: Must be 0.2.18 for Windows
2. Ensure curl_cffi is NOT installed
3. Run as Administrator if permission issues
4. Disable antivirus temporarily (might block network calls)
5. Check Windows Firewall settings

The key is: **yfinance 0.2.18 without curl_cffi** is the magic combination for Windows!