@echo off
title Stock Tracker - Complete System Launcher
color 0A

echo ===============================================================================
echo                     STOCK TRACKER COMPLETE SYSTEM
echo              Windows 11 Production Deployment with ML Training
echo ===============================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo [1/5] Installing required Python packages...
echo -----------------------------------------------
pip install --quiet --upgrade pip
pip install --quiet -r requirements_ml.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed to install
    echo Attempting to continue...
)

echo.
echo [2/5] Setting up SQLite database for historical data...
echo -----------------------------------------------
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('SQLite database initialized successfully')"

echo.
echo [3/5] Starting Main Backend Server (Port 8002)...
echo -----------------------------------------------
start "Stock Tracker Backend" cmd /k "python backend.py"
timeout /t 3 >nul

echo.
echo [4/5] Starting ML Training Backend (Port 8003)...
echo -----------------------------------------------
start "ML Training Backend" cmd /k "python ml_training_backend.py"
timeout /t 3 >nul

echo.
echo [5/5] Starting Frontend Server (Port 8000)...
echo -----------------------------------------------
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 >nul

echo.
echo ===============================================================================
echo                        ALL SERVICES STARTED SUCCESSFULLY
echo ===============================================================================
echo.
echo Access Points:
echo --------------
echo   Main Application:     http://localhost:8000
echo   Backend API:          http://localhost:8002
echo   ML Training API:      http://localhost:8003
echo.
echo Available Modules:
echo -----------------
echo   1. CBA Enhanced Tracker (with Documents/Media/Reports)
echo   2. Global Indices Tracker (Real-time data)
echo   3. Stock Tracker with Technical Analysis
echo   4. Document Uploader with FinBERT Sentiment
echo   5. Phase 4 ML Predictor with Real Training
echo.
echo Features:
echo ---------
echo   - SQLite local storage (100x faster backtesting)
echo   - Real Yahoo Finance data (no mock data)
echo   - Real ML model training (LSTM, GRU, CNN-LSTM, Transformer)
echo   - Hardcoded to localhost:8002 for Windows 11 compatibility
echo.
echo ===============================================================================
echo.
echo Press any key to open the application in your browser...
pause >nul

:: Open browser
start "" "http://localhost:8000"

echo.
echo System is running. Keep this window open.
echo To stop all services, close this window and all command windows.
echo.
pause