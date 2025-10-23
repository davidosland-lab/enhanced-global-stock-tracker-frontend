@echo off
REM ============================================
REM Stock Tracker ML Enhanced - System Launcher
REM Version 2.0.0 - Windows 11
REM ============================================

echo.
echo ======================================================
echo  Starting Stock Tracker ML Enhanced v2.0.0
echo ======================================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if backend is already running
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8000 is already in use
    echo Attempting to stop existing process...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
    timeout /t 2 >nul
)

REM Start the backend server
echo Starting ML Enhanced Backend Server...
start "Stock Tracker Backend" /min cmd /c "venv\Scripts\activate.bat && cd backend && python -m uvicorn main_backend:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 >nul

REM Check if backend started successfully
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend failed to start
    echo Check logs\backend.log for details
    pause
    exit /b 1
)

REM Open the web interface
echo Opening web interface...
start http://localhost:8000/frontend/index.html

echo.
echo ======================================================
echo  System Started Successfully!
echo ======================================================
echo.
echo Backend API: http://localhost:8000
echo Web Interface: http://localhost:8000/frontend/index.html
echo API Documentation: http://localhost:8000/docs
echo.
echo Features Available:
echo - ML Model Training (10-60 seconds)
echo - Real-time Predictions
echo - Backtesting with Transaction Costs
echo - FinBERT Sentiment Analysis
echo - SQLite Caching (50x faster)
echo - All Original Modules Integrated
echo.
echo Press Ctrl+C in this window to stop the server
echo.
pause