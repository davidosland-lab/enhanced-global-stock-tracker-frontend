@echo off
cls
color 0A
echo ================================================================================
echo                     FinBERT v4.0 - LSTM Enhanced System
echo ================================================================================
echo.
echo Starting FinBERT v4.0 Development Server...
echo.
echo Features:
echo   - LSTM Neural Networks
echo   - US + ASX Market Support
echo   - Real-time Predictions
echo   - Interactive Charts
echo.
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Dependencies not installed!
    echo Would you like to install them now? (Y/N)
    set /p install_deps="> "
    if /i "%install_deps%"=="Y" (
        echo.
        echo Installing dependencies...
        pip install flask flask-cors yfinance numpy pandas scikit-learn
    ) else (
        echo.
        echo Please run INSTALL_V4.bat first!
        pause
        exit /b 1
    )
)

echo [2/3] Starting Flask server...
echo.

REM Start the server
start "" python app_finbert_v4_dev.py

REM Wait for server to start
timeout /t 3 /nobreak >nul

echo [3/3] Opening browser...
echo.

REM Open browser
start "" http://localhost:5001

echo ================================================================================
echo.
echo FinBERT v4.0 is now running!
echo.
echo   Server URL:  http://localhost:5001
echo   UI File:     finbert_v4_ui_complete.html
echo.
echo Press Ctrl+C in the server window to stop
echo.
echo ================================================================================
echo.

REM Keep window open
pause
