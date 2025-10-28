@echo off
title Stock Analysis with Intraday Support
color 0A
cls

echo ============================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT
echo ============================================================
echo.
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
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1

REM Start the application
python app.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Failed to start the application
    echo.
    echo Possible solutions:
    echo   1. Run INSTALL.bat first
    echo   2. Check if port 8000 is already in use
    echo   3. Verify Python is in your PATH
    echo ============================================================
)

echo.
pause