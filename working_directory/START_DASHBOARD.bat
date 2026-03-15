@echo off
REM ============================================================================
REM MINIMAL WORKING LAUNCHER - v1.3.15.59.1
REM ============================================================================
REM The simplest possible launcher that works
REM ============================================================================

cls
echo.
echo ========================================================================
echo   TRADING SYSTEM - SIMPLE LAUNCHER
echo ========================================================================
echo.

REM Step 1: Install scikit-learn if needed (the missing dependency)
echo [1/2] Checking dependencies...
venv\Scripts\pip show scikit-learn >nul 2>&1
IF ERRORLEVEL 1 (
    echo Installing scikit-learn...
    venv\Scripts\pip install scikit-learn --quiet
    echo Done.
) ELSE (
    echo Dependencies OK.
)

echo.
echo [2/2] Starting dashboard...
echo.
echo Dashboard URL: http://localhost:8050
echo Press Ctrl+C to stop
echo.

REM Step 2: Start the dashboard
venv\Scripts\python.exe unified_trading_dashboard.py

echo.
pause
