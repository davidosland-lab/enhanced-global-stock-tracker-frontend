@echo off
REM ===============================================================================
REM   FinBERT v4.4.4 - Apply Rate Limit Prevention Fixes
REM   Automatically applies delays and throttling to prevent Yahoo blocking
REM ===============================================================================

echo ================================================================================
echo   FinBERT v4.4.4 - RATE LIMIT PREVENTION FIXES
echo ================================================================================
echo.
echo This script will automatically apply fixes to prevent Yahoo Finance blocking:
echo.
echo   1. Add 0.5s delays between yfinance ticker validations
echo   2. Add 1s throttling between market index fetches
echo   3. Reduce parallel workers from 4 to 2
echo.
echo Backups will be created before any modifications.
echo.

REM Set the working directory to script location
cd /d "%~dp0"

echo ================================================================================
echo   System Information
echo ================================================================================
echo.
echo Current Directory: %CD%
echo Python Version:
python --version 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   ERROR: Python is not installed!
    echo ================================================================================
    echo.
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo   Applying Fixes
echo ================================================================================
echo.

REM Run the fix script
python apply_rate_limit_fixes.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   FIXES FAILED OR CANCELLED
    echo ================================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   FIXES APPLIED SUCCESSFULLY
echo ================================================================================
echo.
echo Your system has been configured to prevent Yahoo Finance rate limiting.
echo.
echo Next steps:
echo   1. If currently blocked, wait 1-2 hours
echo   2. Run DIAGNOSE_YFINANCE.bat to verify yfinance working
echo   3. Run RUN_STOCK_SCREENER.bat to test
echo.

pause
