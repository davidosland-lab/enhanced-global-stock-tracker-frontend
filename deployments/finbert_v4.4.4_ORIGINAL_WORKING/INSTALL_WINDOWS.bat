@echo off
echo ============================================================
echo FinBERT Trading System v3.2 - Windows 11 Installation
echo ============================================================
echo.
echo This installer will set up the complete trading system with:
echo   - Fixed candlestick charts
echo   - Intraday trading (1m, 3m, 5m, 15m, 30m, 60m)
echo   - ML predictions with confidence scores
echo   - Sentiment analysis
echo   - Zoom and pan features
echo   - Real market data only
echo.

:: Keep window open on error
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

:: Check Python installation
echo [Step 1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo Python detected successfully!
echo.

:: Upgrade pip
echo [Step 2/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install requirements
echo [Step 3/4] Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some packages
    echo Try running: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo.

:: Create start script
echo [Step 4/4] Creating start script...
echo @echo off > START_SYSTEM.bat
echo echo Starting FinBERT Trading System v3.2... >> START_SYSTEM.bat
echo echo. >> START_SYSTEM.bat
echo echo The system will be available at: http://localhost:5000 >> START_SYSTEM.bat
echo echo Press Ctrl+C to stop the server >> START_SYSTEM.bat
echo echo. >> START_SYSTEM.bat
echo python app_finbert_complete_v3.2.py >> START_SYSTEM.bat
echo pause >> START_SYSTEM.bat

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To start the system:
echo   1. Double-click START_SYSTEM.bat
echo   2. Open your browser to http://localhost:5000
echo.
echo Features available:
echo   - Candlestick, OHLC, and Line charts
echo   - Intraday intervals (1m to 60m) and daily
echo   - ML predictions with confidence percentages
echo   - Sentiment analysis with news feed
echo   - Zoom with mouse wheel, pinch, or drag
echo   - Pan with Ctrl+drag
echo   - Economic indicators (VIX, Treasury, Dollar, Gold)
echo.
echo Press any key to exit installer...
pause >nul