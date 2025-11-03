@echo off
setlocal enabledelayedexpansion

:: Enhanced debugging batch file
title Debug - Unified Robust Stock Analysis
color 0E

cls
echo ================================================================================
echo                         DEBUG MODE - DIAGNOSTIC INFORMATION
echo ================================================================================
echo.

:: System Information
echo [SYSTEM INFORMATION]
echo Operating System: %OS%
echo Computer Name: %COMPUTERNAME%
echo Current Directory: %CD%
echo Date/Time: %DATE% %TIME%
echo.

:: Python Information
echo [PYTHON INFORMATION]
python --version 2>&1
echo Python Path:
where python 2>&1
echo.

:: Check installed packages
echo [CHECKING INSTALLED PACKAGES]
echo.
echo Checking Flask...
python -c "import flask; print(f'Flask version: {flask.__version__}')" 2>&1
if %errorlevel% neq 0 echo [MISSING] Flask not installed

echo Checking pandas...
python -c "import pandas; print(f'pandas version: {pandas.__version__}')" 2>&1
if %errorlevel% neq 0 echo [MISSING] pandas not installed

echo Checking numpy...
python -c "import numpy; print(f'numpy version: {numpy.__version__}')" 2>&1
if %errorlevel% neq 0 echo [MISSING] numpy not installed

echo Checking yfinance...
python -c "import yfinance; print(f'yfinance version: {yfinance.__version__}')" 2>&1
if %errorlevel% neq 0 echo [MISSING] yfinance not installed

echo Checking requests...
python -c "import requests; print(f'requests version: {requests.__version__}')" 2>&1
if %errorlevel% neq 0 echo [MISSING] requests not installed

echo Checking scikit-learn...
python -c "import sklearn; print(f'scikit-learn version: {sklearn.__version__}')" 2>&1
if %errorlevel% neq 0 echo [OPTIONAL] scikit-learn not installed (ML features disabled)
echo.

:: Check if app file exists
echo [FILE CHECK]
if exist "app_unified_robust.py" (
    echo [OK] app_unified_robust.py found
    for %%F in (app_unified_robust.py) do echo File size: %%~zF bytes
) else (
    echo [ERROR] app_unified_robust.py NOT FOUND!
)
echo.

:: Network test
echo [NETWORK TEST]
echo Testing connection to Yahoo Finance...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" "https://finance.yahoo.com" 2>nul
if %errorlevel% neq 0 (
    ping -n 1 finance.yahoo.com >nul 2>&1
    if %errorlevel% eq 0 (
        echo [OK] Can reach Yahoo Finance
    ) else (
        echo [WARNING] Cannot reach Yahoo Finance
    )
)

echo Testing connection to Alpha Vantage...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" "https://www.alphavantage.co" 2>nul
if %errorlevel% neq 0 (
    ping -n 1 www.alphavantage.co >nul 2>&1
    if %errorlevel% eq 0 (
        echo [OK] Can reach Alpha Vantage
    ) else (
        echo [WARNING] Cannot reach Alpha Vantage
    )
)
echo.

:: Port check
echo [PORT CHECK]
netstat -an | findstr :5000 >nul 2>&1
if %errorlevel% eq 0 (
    echo [WARNING] Port 5000 is already in use!
    echo Another application may be using this port.
) else (
    echo [OK] Port 5000 is available
)
echo.

:: Try to start with verbose output
echo ================================================================================
echo                              STARTING IN DEBUG MODE
echo ================================================================================
echo.
echo Running with verbose output...
echo Press Ctrl+C to stop
echo.

:: Set Flask debug environment variables
set FLASK_DEBUG=1
set FLASK_ENV=development
set PYTHONUNBUFFERED=1

:: Run with Python verbose flag
python -u app_unified_robust.py

echo.
echo ================================================================================
echo                                  DEBUG SESSION ENDED
echo ================================================================================
echo.
pause