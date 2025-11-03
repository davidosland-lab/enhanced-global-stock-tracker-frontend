@echo off
REM FinBERT Trading System - REAL DATA ONLY
REM No synthetic, demo, or fake data

echo ========================================
echo FinBERT Trading - REAL DATA ONLY VERSION
echo ========================================
echo.
echo This version uses ONLY real market data from:
echo - Yahoo Finance
echo - Alpha Vantage (if API key set)
echo - IEX Cloud (if API key set)  
echo - Finnhub (if API key set)
echo - Polygon.io (if API key set)
echo - Financial RSS feeds
echo.
echo NO synthetic, demo, or fake data will be used!
echo If data is unavailable, it will show an error.
echo.

REM Check virtual environment
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL_FIXED.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Optional: Set API keys here for better data access
REM Uncomment and add your keys:
REM set ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
REM set IEX_TOKEN=your_iex_cloud_token_here
REM set FINNHUB_KEY=your_finnhub_key_here
REM set POLYGON_KEY=your_polygon_key_here

REM Check for API keys
echo Checking for API keys...
if defined ALPHA_VANTAGE_KEY (
    echo ✓ Alpha Vantage key found
) else (
    echo ✗ No Alpha Vantage key (set ALPHA_VANTAGE_KEY for more data)
)

if defined IEX_TOKEN (
    echo ✓ IEX Cloud token found
) else (
    echo ✗ No IEX token (set IEX_TOKEN for more data)
)

if defined FINNHUB_KEY (
    echo ✓ Finnhub key found
) else (
    echo ✗ No Finnhub key (set FINNHUB_KEY for more data)
)

if defined POLYGON_KEY (
    echo ✓ Polygon key found
) else (
    echo ✗ No Polygon key (set POLYGON_KEY for more data)
)
echo.

REM Install required packages
echo Checking required packages...
pip install yfinance pandas numpy scikit-learn flask flask-cors --quiet
pip install alpha_vantage pandas_datareader feedparser --quiet 2>nul
echo.

REM Start the application
echo ========================================
echo Starting REAL DATA ONLY Trading System
echo ========================================
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the real data only version
python app_real_data_only.py

REM If error, show message
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error!
    echo.
    echo Common issues:
    echo 1. No internet connection
    echo 2. Yahoo Finance might be temporarily down
    echo 3. Try adding API keys for backup data sources
    echo.
    pause
)