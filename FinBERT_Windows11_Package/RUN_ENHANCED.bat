@echo off
REM Enhanced FinBERT Trading System with Automatic Data Feeds
REM This version includes all economic indicators and news feeds

echo ========================================
echo Starting Enhanced FinBERT Trading System
echo ========================================
echo.
echo Features:
echo - Customizable historical periods (1mo to max)
echo - Government announcements (Fed, ECB, RBA, BoE)
echo - Economic indicators (VIX, Dollar, Gold, Oil)
echo - Treasury yields and interest rates
echo - Geopolitical event monitoring
echo - Market news aggregation
echo - Advanced ML with multiple models
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL_FIXED.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [✓] Virtual environment activated
echo.

REM Check required packages
echo Checking required packages...
python -c "import pandas, yfinance, flask, sklearn, requests, feedparser" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Some packages missing. Installing additional requirements...
    pip install feedparser beautifulsoup4 requests
)

REM Start the enhanced application
echo ========================================
echo Starting Enhanced Trading System...
echo ========================================
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Data feeds will automatically fetch:
echo - Stock prices (Yahoo Finance)
echo - Treasury yields (US Treasury API)
echo - Economic indicators (FRED, Yahoo)
echo - Central bank announcements (RSS feeds)
echo - Geopolitical events (Reuters, BBC)
echo - Market news (Multiple sources)
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the enhanced application
python app_enhanced_finbert.py

REM If the application exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error!
    pause
)