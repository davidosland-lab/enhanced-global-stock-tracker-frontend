@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo UNIFIED STOCK ANALYSIS SYSTEM - LOCAL CHARTS VERSION
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Set environment variable to skip dotenv (prevents UTF-8 errors)
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

echo Installing/Updating required packages...
echo ----------------------------------------------------------------------
pip install --upgrade flask flask-cors yfinance pandas numpy scikit-learn requests >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some packages may not have installed correctly
    echo Trying with user installation...
    pip install --user flask flask-cors yfinance pandas numpy scikit-learn requests
)

echo.
echo Checking for conflicting .env files...
if exist ".env" (
    echo WARNING: Found .env file that may cause UTF-8 errors
    echo Renaming to .env.backup...
    move /Y .env .env.backup >nul 2>&1
)

echo.
echo ======================================================================
echo STARTING STOCK ANALYSIS SERVER
echo ======================================================================
echo.
echo Server will run at: http://localhost:8000
echo.
echo To stop the server: Press Ctrl+C
echo.
echo If you see encoding errors, the system will auto-fix them...
echo ----------------------------------------------------------------------
echo.

REM Try to run with UTF-8 encoding
chcp 65001 >nul 2>&1
python unified_stock_system_local.py

if errorlevel 1 (
    echo.
    echo ----------------------------------------------------------------------
    echo Server encountered an error. Trying alternate startup method...
    echo ----------------------------------------------------------------------
    
    REM Create a wrapper Python script to handle encoding
    echo import os > run_wrapper.py
    echo import sys >> run_wrapper.py
    echo os.environ['FLASK_SKIP_DOTENV'] = '1' >> run_wrapper.py
    echo os.environ['PYTHONIOENCODING'] = 'utf-8' >> run_wrapper.py
    echo if hasattr(sys.stdout, 'reconfigure'): >> run_wrapper.py
    echo     sys.stdout.reconfigure(encoding='utf-8') >> run_wrapper.py
    echo if hasattr(sys.stderr, 'reconfigure'): >> run_wrapper.py
    echo     sys.stderr.reconfigure(encoding='utf-8') >> run_wrapper.py
    echo exec(open('unified_stock_system_local.py', encoding='utf-8').read()) >> run_wrapper.py
    
    echo Running with encoding wrapper...
    python run_wrapper.py
    
    del run_wrapper.py >nul 2>&1
)

echo.
echo ----------------------------------------------------------------------
echo Server stopped.
echo ----------------------------------------------------------------------
pause