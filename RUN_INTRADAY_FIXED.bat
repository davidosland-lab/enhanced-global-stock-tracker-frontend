@echo off
title Stock Analysis with Intraday Support - FIXED
color 0A
cls

echo ========================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT - FIXED
echo     JavaScript Errors Resolved
echo ========================================================
echo.
echo Fixed Issues:
echo [✓] JavaScript exports error resolved
echo [✓] Chart.js financial plugin loaded correctly
echo [✓] Favicon 404 handled
echo [✓] All functions properly defined
echo [✓] Export to CSV working
echo.
echo Features:
echo - Intraday: 1m, 2m, 5m, 15m, 30m, 1h, 90m intervals
echo - Real-time candlestick charts
echo - Auto-refresh options (30s, 1m, 5m, 10m)
echo - Quick interval buttons
echo - Export to CSV
echo.
echo ========================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Starting server at http://localhost:8000
echo.

REM Keep window open and run
cmd /k python stock_analysis_intraday_fixed.py