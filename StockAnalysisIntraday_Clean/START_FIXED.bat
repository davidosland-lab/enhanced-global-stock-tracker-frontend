@echo off
title Stock Analysis - Running
color 0A
cls

echo ============================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT
echo ============================================================
echo.

REM Check if Python is installed
python --version 2>nul
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please:
    echo 1. Install Python from https://python.org
    echo 2. Make sure to check "Add Python to PATH"
    echo 3. Restart your computer
    echo 4. Run INSTALL_FIXED.bat first
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed (basic dependency check)
python -c "import flask" 2>nul
if errorlevel 1 (
    color 0E
    echo WARNING: Dependencies not installed!
    echo.
    echo Running installer first...
    echo.
    call INSTALL_FIXED.bat
    echo.
)

echo Starting server at http://localhost:8000
echo.
echo Features:
echo   * Intraday intervals: 1m, 2m, 5m, 15m, 30m, 1h, 90m
echo   * Real-time candlestick charts
echo   * Technical indicators (RSI, MACD, Bollinger Bands)
echo   * Machine Learning predictions
echo   * Auto-refresh options
echo   * Export to CSV
echo.
echo ============================================================
echo.
echo Server is starting...
echo Once started, open your browser to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUNBUFFERED=1

REM Run the app and keep window open
python app.py
echo.
echo ============================================================
echo Server has stopped.
echo.
echo Possible reasons:
echo   1. You pressed Ctrl+C (normal shutdown)
echo   2. Port 8000 is already in use
echo   3. Missing dependencies (run INSTALL_FIXED.bat)
echo   4. Python error (check messages above)
echo ============================================================
echo.
pause