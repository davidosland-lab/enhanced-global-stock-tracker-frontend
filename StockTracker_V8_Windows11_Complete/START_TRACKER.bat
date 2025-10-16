@echo off
cls
color 0B
title Stock Tracker V8 Professional

echo ============================================================
echo    Stock Tracker V8 Professional - Starting Services
echo    REAL ML Implementation - Windows 11
echo ============================================================
echo.

:: Activate virtual environment if it exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python installation...
)
echo.

:: Kill any existing Python processes
echo Stopping any existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul
echo.

:: Start Main Backend (Port 8002)
echo [1/5] Starting Main Backend API (Port 8002)...
start /min cmd /c "cd backends && python backend.py"
timeout /t 3 >nul

:: Start ML Backend (Port 8003)
echo [2/5] Starting ML Backend - REAL Training (Port 8003)...
start /min cmd /c "cd backends && python ml_backend.py"
timeout /t 3 >nul

:: Start FinBERT Backend (Port 8004)
echo [3/5] Starting FinBERT Sentiment Analysis (Port 8004)...
start /min cmd /c "cd backends && python finbert_backend.py"
timeout /t 3 >nul

:: Start Web Server (Port 8080)
echo [4/5] Starting Web Interface (Port 8080)...
start /min cmd /c "python -m http.server 8080"
timeout /t 2 >nul

:: Open browser
echo [5/5] Opening Stock Tracker in browser...
timeout /t 2 >nul
start http://localhost:8080

echo.
echo ============================================================
echo    All Services Started Successfully!
echo ============================================================
echo.
echo Services running:
echo   - Main API:      http://localhost:8002
echo   - ML Backend:    http://localhost:8003  (REAL ML)
echo   - FinBERT:       http://localhost:8004
echo   - Web Interface: http://localhost:8080
echo.
echo Features available:
echo   ✓ Real-time stock tracking
echo   ✓ REAL ML training (10-60 seconds for large datasets)
echo   ✓ Real predictions from trained models
echo   ✓ FinBERT sentiment analysis
echo   ✓ 15+ Global market indices
echo   ✓ Backtesting with $100k capital
echo   ✓ SQLite cached historical data
echo   ✓ Document upload and analysis
echo.
echo Press Ctrl+C to stop all services
echo.
echo ============================================================
echo    DO NOT CLOSE THIS WINDOW - Services are running
echo ============================================================
echo.
pause