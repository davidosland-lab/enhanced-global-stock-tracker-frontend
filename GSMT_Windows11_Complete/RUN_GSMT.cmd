@echo off
:: GSMT Ver 8.1.3 - Main Launcher
:: Use .cmd extension to ensure proper execution
:: This file will run as a batch script, not open in notepad

title GSMT Ver 8.1.3 - Complete System
color 0A
cls

echo ================================================================================
echo                        GSMT STOCK TRACKER Ver 8.1.3
echo                            COMPLETE SYSTEM
echo ================================================================================
echo.
echo Starting GSMT with all fixes applied...
echo.

:: Set directory
cd /d "%~dp0"

:: Check Python
echo [1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
echo.

:: Install packages
echo [2] Installing required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install fastapi uvicorn yfinance pandas numpy scikit-learn aiofiles requests --quiet --no-warn-script-location >nul 2>&1
echo    Dependencies installed
echo.

:: Clear ports
echo [3] Clearing ports 8000 and 8001...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Ports cleared
echo.

:: Start Market Server
echo [4] Starting Market Data Server...
start "Market Server" /min cmd /c "cd /d "%~dp0" && python backend\market_data_server.py"
timeout /t 3 /nobreak >nul
echo    Market server started on port 8000
echo.

:: Start CBA Server
echo [5] Starting CBA Specialist Server...
start "CBA Server" /min cmd /c "cd /d "%~dp0" && python backend\cba_specialist_server.py"
timeout /t 3 /nobreak >nul
echo    CBA server started on port 8001
echo.

:: Wait for servers
echo [6] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul
echo    Servers ready
echo.

:: Open dashboard
echo [7] Opening Main Dashboard...
echo.

:: Use start with empty title to open HTML file in default browser
start "" "%~dp0frontend\main_dashboard.html"

echo.
echo ================================================================================
echo                    GSMT LAUNCHED SUCCESSFULLY!
echo ================================================================================
echo.
echo SERVERS RUNNING:
echo   - Market Data Server: http://localhost:8000
echo   - CBA Specialist Server: http://localhost:8001
echo.
echo DASHBOARD OPENED:
echo   - Main dashboard with all modules
echo   - Click any module card to open it
echo.
echo AVAILABLE MODULES:
echo   1. Global Market Indices (AEST/AEDT timezone)
echo   2. Single Stock Tracker (Any symbol)
echo   3. CBA Banking Analysis (Commonwealth Bank)
echo   4. Technical Analysis (Candlesticks & indicators)
echo   5. ML Predictions (6 AI models)
echo   6. Performance Metrics (Model accuracy)
echo.
echo IMPORTANT NOTES:
echo   - Markets only plot during trading hours
echo   - ASX: 10:00-16:00 AEST
echo   - FTSE: 17:00-01:30 AEST
echo   - NYSE: 23:30-06:00 AEST
echo.
echo ================================================================================
echo.
echo Keep this window open to keep servers running.
echo Press any key to stop servers and exit...
echo.
pause >nul

:: Kill servers when exiting
echo.
echo Stopping servers...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Servers stopped.
echo.
exit