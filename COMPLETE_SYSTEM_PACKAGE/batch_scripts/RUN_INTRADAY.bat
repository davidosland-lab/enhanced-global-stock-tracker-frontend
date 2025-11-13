@echo off
title Stock Analysis with Intraday Support
color 0A
cls

echo ========================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT
echo     Enhanced with Multiple Time Intervals
echo ========================================================
echo.
echo Features:
echo - Intraday: 1m, 2m, 5m, 15m, 30m, 1h, 90m intervals
echo - Daily/Weekly/Monthly intervals
echo - Real-time data from Yahoo Finance
echo - Auto-refresh options (30s, 1m, 5m, 10m)
echo - Quick interval selection buttons
echo - Export to CSV functionality
echo.
echo ========================================================
echo.

REM Set environment variables for Windows
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
cmd /k python stock_analysis_intraday.py