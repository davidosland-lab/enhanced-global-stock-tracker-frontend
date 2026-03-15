@echo off
REM ====================================================================
REM  QUICK DASHBOARD STARTER - Minimal Version
REM  For when you just want to start the dashboard quickly
REM ====================================================================

cls
echo Starting Live Trading Dashboard...
echo.

cd /d "%~dp0"

python live_trading_dashboard.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Dashboard failed to start!
    echo.
    echo Common fixes:
    echo 1. Install dependencies: pip install flask flask-cors pandas numpy
    echo 2. Make sure you're in the correct directory
    echo 3. Check that templates and static folders exist
    echo.
    pause
)
