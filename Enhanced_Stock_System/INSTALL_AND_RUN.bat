@echo off
cls
echo ================================================================================
echo                    UNIFIED STOCK ANALYSIS SYSTEM INSTALLER
echo ================================================================================
echo.
echo This will install and run the complete stock analysis system with:
echo - Yahoo Finance (Primary data source)
echo - Alpha Vantage (Backup with API key: 68ZFANK047DL0KSR)
echo - ML Predictions (Random Forest + Gradient Boosting)
echo - Technical Indicators (RSI, MACD, Bollinger Bands, etc.)
echo - Australian Stock Support (CBA, BHP, CSL, NAB, etc.)
echo.
echo ================================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Install required packages
echo Installing required packages...
echo.

echo [1/6] Installing Flask web framework...
pip install flask flask-cors --quiet --disable-pip-version-check 2>nul

echo [2/6] Installing Yahoo Finance...
pip install yfinance --quiet --disable-pip-version-check 2>nul

echo [3/6] Installing data processing libraries...
pip install "numpy<2.0" pandas --quiet --disable-pip-version-check 2>nul

echo [4/6] Installing ML libraries...
pip install scikit-learn --quiet --disable-pip-version-check 2>nul

echo [5/6] Installing network libraries...
pip install requests --quiet --disable-pip-version-check 2>nul

echo [6/6] Installing additional utilities...
pip install python-dateutil pytz --quiet --disable-pip-version-check 2>nul

echo.
echo ================================================================================
echo                              STARTING SERVER
echo ================================================================================
echo.
echo Server is starting at: http://localhost:8000
echo.
echo Features available:
echo  - Real-time stock data from Yahoo Finance
echo  - Backup data from Alpha Vantage (API integrated)
echo  - ML predictions with confidence scores
echo  - 35+ technical indicators
echo  - Australian stocks (auto .AX suffix)
echo.
echo Quick test symbols: CBA, BHP, AAPL, MSFT, TSLA
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Run the server
python unified_stock_system.py

REM If server stops
echo.
echo ================================================================================
echo Server has been stopped.
echo To restart, run this file again or execute: python unified_stock_system.py
echo ================================================================================
pause