@echo off
REM Quick start - installs if needed and starts the app
title Quick Start - Stock Analysis
color 0A

echo ============================================================
echo     QUICK START - STOCK ANALYSIS WITH INTRADAY
echo ============================================================
echo.

REM Check if packages are installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo First time setup detected. Installing packages...
    call INSTALL.bat
)

REM Start the application
echo Starting Stock Analysis System...
echo.
cmd /k python app.py