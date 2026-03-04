@echo off
REM ============================================================================
REM  MANUAL PAPER TRADING PLATFORM - STARTER BATCH FILE
REM ============================================================================
REM  Full control over stock selection and quantities
REM  Usage: Double-click this file to start manual trading
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

cls
echo.
echo ============================================================================
echo   MANUAL PAPER TRADING PLATFORM - STARTING...
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if required files exist
if not exist "unified_trading_platform.py" (
    echo [ERROR] unified_trading_platform.py not found!
    echo.
    echo This file is required. Download from:
    echo https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/unified_trading_platform.py
    echo.
    pause
    exit /b 1
)

if not exist "manual_paper_trading.py" (
    echo [WARNING] manual_paper_trading.py not found! Downloading...
    echo.
    
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py' -OutFile 'manual_paper_trading.py' -UseBasicParsing; Write-Host '[OK] Downloaded manual_paper_trading.py'; exit 0 } catch { Write-Host '[ERROR] Download failed'; exit 1 }" 2>nul
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not download manual_paper_trading.py
        echo.
        echo Please download manually from:
        echo https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py
        echo.
        echo Save it to: %CD%\manual_paper_trading.py
        echo.
        pause
        exit /b 1
    )
)

echo [OK] All required files present
echo.

REM Check and install dependencies
echo [STEP 1/3] Checking dependencies...
echo.

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] Flask...
    pip install flask flask-cors --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install Flask
        pause
        exit /b 1
    )
)

python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] yfinance (for real-time stock prices)...
    pip install yfinance --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install yfinance
        pause
        exit /b 1
    )
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] pandas...
    pip install pandas --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install pandas
        pause
        exit /b 1
    )
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] numpy...
    pip install numpy --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install numpy
        pause
        exit /b 1
    )
)

echo [OK] All dependencies installed
echo.

REM Validate files
echo [STEP 2/3] Validating files...
echo.

python -c "import unified_trading_platform" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] unified_trading_platform.py has syntax errors
    pause
    exit /b 1
)

python -c "import manual_paper_trading" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] manual_paper_trading.py has syntax errors
    pause
    exit /b 1
)

echo [OK] All files validated
echo.

REM Start the platform
echo [STEP 3/3] Starting Manual Paper Trading Platform...
echo.
echo ============================================================================
echo   MANUAL TRADING COMMANDS
echo ============================================================================
echo.
echo   buy('AAPL', 100)     Buy 100 shares of AAPL at current price
echo   sell('AAPL')         Sell all AAPL shares at current price
echo   status()             Show portfolio summary
echo   positions()          Show all open positions with P^&L
echo.
echo   Examples:
echo     >>> buy('NVDA', 50)
echo     >>> buy('TSLA', 25)
echo     >>> status()
echo     >>> sell('NVDA')
echo.
echo ============================================================================
echo   Dashboard: http://localhost:5000
echo ============================================================================
echo.
echo Starting in 3 seconds...
echo.
timeout /t 3 /nobreak >nul

python manual_paper_trading.py

REM Handle exit
echo.
echo.
echo ============================================================================
echo   Platform stopped
echo ============================================================================
echo.
pause
