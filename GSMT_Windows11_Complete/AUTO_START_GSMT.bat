@echo off
title GSMT Ver 8.1.3 - Auto Start with Landing Dashboard
color 0A
cls

echo ================================================================================
echo                    GSMT STOCK TRACKER Ver 8.1.3
echo                  AUTOMATED LAUNCHER WITH LANDING PAGE
echo ================================================================================
echo.
echo Starting complete GSMT system with real market data from Yahoo Finance...
echo.
echo This launcher will:
echo   1. Check Python installation
echo   2. Install required packages
echo   3. Start Market Data Server (Port 8000)
echo   4. Start CBA Specialist Server (Port 8001)
echo   5. Open the Landing Dashboard with all modules
echo.
echo ================================================================================
echo.

:: Check Python installation
echo [STEP 1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Python is not installed or not in PATH!
    echo ============================================================
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo ============================================================
    echo.
    pause
    exit /b 1
)

:: Display Python version
echo [OK] Python detected:
python --version
echo.

:: Check and install dependencies
echo [STEP 2] Checking required packages...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing FastAPI framework...
    pip install fastapi uvicorn --quiet --no-warn-script-location
)

python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo Installing Yahoo Finance API...
    pip install yfinance --quiet --no-warn-script-location
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing data processing libraries...
    pip install pandas numpy --quiet --no-warn-script-location
)

python -c "import sklearn" >nul 2>&1
if errorlevel 1 (
    echo Installing machine learning libraries...
    pip install scikit-learn --quiet --no-warn-script-location
)

echo [OK] All required packages installed
echo.

:: Kill any existing processes on ports 8000 and 8001
echo [STEP 3] Clearing ports 8000 and 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Ports cleared
echo.

:: Start Market Data Server
echo [STEP 4] Starting Market Data Server (Real Yahoo Finance data)...
echo Server will run on: http://localhost:8000
start "GSMT Market Server" /min cmd /c "cd /d "%~dp0" && python backend\market_data_server.py"
timeout /t 3 /nobreak >nul

:: Test Market Server
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Market server is starting slowly, please wait...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Market Data Server is running
)
echo.

:: Start CBA Specialist Server
echo [STEP 5] Starting CBA Specialist Server (Real CBA.AX data)...
echo Server will run on: http://localhost:8001
start "GSMT CBA Server" /min cmd /c "cd /d "%~dp0" && python backend\cba_specialist_server.py"
timeout /t 3 /nobreak >nul

:: Test CBA Server
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] CBA server is starting slowly, please wait...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] CBA Specialist Server is running
)
echo.

:: Create desktop shortcut for landing page
echo [STEP 6] Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
set "shortcut=%desktop%\GSMT Dashboard.url"
(
    echo [InternetShortcut]
    echo URL=file:///%~dp0frontend\landing_dashboard.html
    echo IconIndex=0
    echo IconFile=%SystemRoot%\system32\SHELL32.dll,13
) > "%shortcut%"
echo [OK] Desktop shortcut created
echo.

:: Wait a moment for servers to fully initialize
echo [STEP 7] Waiting for servers to fully initialize...
timeout /t 3 /nobreak >nul
echo [OK] Servers ready
echo.

:: Open the landing dashboard
echo [STEP 8] Opening GSMT Landing Dashboard...
start "" "%~dp0frontend\landing_dashboard.html"
echo [OK] Dashboard opened in browser
echo.

:: Display success message
echo.
echo ================================================================================
echo                        ✓ GSMT SUCCESSFULLY LAUNCHED!
echo ================================================================================
echo.
echo ▶ SERVERS RUNNING:
echo   • Market Data Server:     http://localhost:8000
echo   • CBA Specialist Server:  http://localhost:8001
echo.
echo ▶ LANDING DASHBOARD OPENED:
echo   • Shows all 6 modules with live data
echo   • Real-time market prices from Yahoo Finance
echo   • Click any module card to open detailed view
echo.
echo ▶ AVAILABLE MODULES:
echo   1. Global Market Indices  - 18 worldwide markets
echo   2. CBA Banking Analysis   - Commonwealth Bank specialist
echo   3. ML Predictions        - 6 AI models (LSTM, GRU, Transformer, etc.)
echo   4. Technical Analysis    - RSI, MACD, Bollinger, patterns
echo   5. Single Stock Tracker  - Track any stock with predictions
echo   6. Performance Dashboard - Model accuracy metrics
echo.
echo ▶ DATA FEATURES:
echo   • Real market data (no synthetic/fake data)
echo   • 5-minute cache for optimal performance
echo   • Live updates during market hours
echo   • Historical data for analysis
echo.
echo ▶ QUICK TIPS:
echo   • Landing page auto-refreshes every 5 minutes
echo   • Server status shown at top (green = online)
echo   • Click module cards to open detailed views
echo   • All prices are real from Yahoo Finance
echo.
echo ================================================================================
echo.
echo To stop servers: Close this window or press Ctrl+C
echo To restart: Run AUTO_START_GSMT.bat again
echo.
echo ================================================================================
echo.
pause