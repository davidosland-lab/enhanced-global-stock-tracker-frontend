@echo off
echo ========================================
echo StockTracker V10 - Quick Fix Tool
echo ========================================
echo.
echo This will attempt to fix common issues automatically.
echo.

REM Fix 1: Kill all Python processes
echo [1/8] Killing any existing Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Fix 2: Clear SSL environment variables
echo [2/8] Clearing SSL environment variables...
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
echo SSL variables cleared

REM Fix 3: Check and create virtual environment
echo [3/8] Checking virtual environment...
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM Fix 4: Upgrade pip and setuptools
echo [4/8] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Fix 5: Reinstall core packages if missing
echo [5/8] Checking and installing missing packages...
python -c "import fastapi" 2>nul || pip install fastapi --quiet
python -c "import uvicorn" 2>nul || pip install uvicorn --quiet
python -c "import pandas" 2>nul || pip install pandas --quiet
python -c "import numpy" 2>nul || pip install numpy --quiet
python -c "import yfinance" 2>nul || pip install yfinance --quiet
python -c "import sklearn" 2>nul || pip install scikit-learn --quiet
python -c "import requests" 2>nul || pip install requests --quiet
python -c "import joblib" 2>nul || pip install joblib --quiet
python -c "import certifi" 2>nul || pip install certifi --quiet
python -c "import aiohttp" 2>nul || pip install aiohttp --quiet
python -c "import scipy" 2>nul || pip install scipy --quiet
python -c "import ta" 2>nul || pip install ta --quiet

REM Fix 6: Clear any database locks
echo [6/8] Clearing database locks...
if exist "*.db-journal" del /f "*.db-journal" 2>nul
if exist "*.db-wal" del /f "*.db-wal" 2>nul

REM Fix 7: Check port availability
echo [7/8] Checking port availability...
netstat -an | findstr ":8000.*LISTENING" >nul && (
    echo Port 8000 is in use - attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
        taskkill /PID %%a /F 2>nul
    )
)
netstat -an | findstr ":8002.*LISTENING" >nul && (
    echo Port 8002 is in use - attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002.*LISTENING"') do (
        taskkill /PID %%a /F 2>nul
    )
)
netstat -an | findstr ":8003.*LISTENING" >nul && (
    echo Port 8003 is in use - attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003.*LISTENING"') do (
        taskkill /PID %%a /F 2>nul
    )
)
netstat -an | findstr ":8004.*LISTENING" >nul && (
    echo Port 8004 is in use - attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8004.*LISTENING"') do (
        taskkill /PID %%a /F 2>nul
    )
)
netstat -an | findstr ":8005.*LISTENING" >nul && (
    echo Port 8005 is in use - attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005.*LISTENING"') do (
        taskkill /PID %%a /F 2>nul
    )
)

REM Fix 8: Test imports
echo [8/8] Testing service imports...
python -c "import main_backend; print('Main Backend: OK')" 2>nul || echo Main Backend: FAILED
python -c "import ml_backend; print('ML Backend: OK')" 2>nul || echo ML Backend: FAILED
python -c "import finbert_backend; print('FinBERT Backend: OK')" 2>nul || echo FinBERT Backend: FAILED
python -c "import historical_backend; print('Historical Backend: OK')" 2>nul || echo Historical Backend: FAILED
python -c "import backtesting_backend; print('Backtesting Backend: OK')" 2>nul || echo Backtesting Backend: FAILED

echo.
echo ========================================
echo Quick Fix Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run FULL_DIAGNOSTIC.bat to check system status
echo 2. Try START.bat to start services
echo 3. If still having issues, run TEST_INDIVIDUAL.bat
echo.
pause