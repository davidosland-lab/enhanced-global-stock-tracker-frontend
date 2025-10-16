@echo off
cls
color 0B
title Stock Tracker V8 Professional

echo ============================================================
echo    Stock Tracker V8 Professional - Starting Services
echo    REAL ML Implementation - Windows 11
echo ============================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit
)

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Note: No virtual environment found, using system Python
)
echo.

:: Kill any existing Python processes on our ports
echo Checking for existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8003"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8004"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080"') do taskkill /F /PID %%a >nul 2>&1
echo Ports cleared.
echo.

:: Check if backends directory exists
if not exist backends (
    echo ERROR: backends directory not found!
    echo Current directory: %CD%
    echo Please run this from the StockTracker_V8 directory
    pause
    exit
)

:: Start services with better error handling
echo Starting services...
echo.

:: Start Main Backend (Port 8002)
echo [1/4] Starting Main Backend API (Port 8002)...
if exist backends\backend.py (
    start "Main API" /min cmd /c "cd backends && python backend.py 2>&1"
    timeout /t 2 >nul
) else (
    echo ERROR: backends\backend.py not found!
)

:: Start ML Backend (Port 8003)
echo [2/4] Starting ML Backend - REAL Training (Port 8003)...
if exist backends\ml_backend.py (
    start "ML Backend" /min cmd /c "cd backends && python ml_backend.py 2>&1"
    timeout /t 2 >nul
) else (
    echo ERROR: backends\ml_backend.py not found!
)

:: Start FinBERT Backend (Port 8004)
echo [3/4] Starting FinBERT Sentiment Analysis (Port 8004)...
if exist backends\finbert_backend.py (
    start "FinBERT" /min cmd /c "cd backends && python finbert_backend.py 2>&1"
    timeout /t 2 >nul
) else (
    echo ERROR: backends\finbert_backend.py not found!
)

:: Start Web Server (Port 8080)
echo [4/4] Starting Web Interface (Port 8080)...
start "Web Server" /min cmd /c "python -m http.server 8080 2>&1"
timeout /t 3 >nul

echo.
echo Checking service status...
timeout /t 2 >nul

:: Check if services are running
netstat -an | findstr ":8002" >nul
if %errorlevel% equ 0 (
    echo [OK] Main API running on port 8002
) else (
    echo [FAIL] Main API not detected on port 8002
)

netstat -an | findstr ":8003" >nul
if %errorlevel% equ 0 (
    echo [OK] ML Backend running on port 8003
) else (
    echo [FAIL] ML Backend not detected on port 8003
)

netstat -an | findstr ":8004" >nul
if %errorlevel% equ 0 (
    echo [OK] FinBERT running on port 8004
) else (
    echo [FAIL] FinBERT not detected on port 8004
)

netstat -an | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo [OK] Web Server running on port 8080
) else (
    echo [FAIL] Web Server not detected on port 8080
)

echo.
echo ============================================================
echo    Startup Complete!
echo ============================================================
echo.

:: Try to open browser
echo Opening Stock Tracker in your default browser...
timeout /t 2 >nul

:: Check which HTML file to use
if exist index_fixed.html (
    start http://localhost:8080/index_fixed.html
) else (
    start http://localhost:8080
)

echo.
echo Services Information:
echo   - Web Interface: http://localhost:8080
echo   - Main API:      http://localhost:8002
echo   - ML Backend:    http://localhost:8003 (REAL ML)
echo   - FinBERT:       http://localhost:8004
echo.
echo If the page shows connection errors:
echo   1. Wait 10 seconds for services to fully start
echo   2. Refresh the browser page
echo   3. Try http://localhost:8080/index_fixed.html
echo   4. Check Windows Firewall settings
echo.
echo Features available:
echo   * Real-time stock tracking
echo   * REAL ML training (10-60 seconds for large datasets)
echo   * Real predictions from trained models
echo   * FinBERT sentiment analysis
echo   * 15+ Global market indices
echo   * Backtesting with $100k capital
echo   * SQLite cached historical data
echo   * Document upload and analysis
echo.
echo ============================================================
echo    KEEP THIS WINDOW OPEN - Services are running here
echo    Press Ctrl+C to stop all services
echo ============================================================
echo.

:: Keep the window open and show any errors
cmd /k