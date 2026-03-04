@echo off
REM ============================================================================
REM  FinBERT v4.0 Enhanced - Windows 11 Startup Script
REM  Starts the Flask server with enhanced UI features
REM ============================================================================

echo.
echo ============================================================================
echo   FinBERT v4.0 ENHANCED - Starting Server
echo ============================================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run INSTALL_WINDOWS11_ENHANCED.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if app file exists
if not exist app_finbert_v4_dev.py (
    echo ERROR: app_finbert_v4_dev.py not found!
    echo.
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Display startup information
echo.
echo ============================================================================
echo   FinBERT v4.0 ENHANCED FEATURES
echo ============================================================================
echo.
echo  - Candlestick Charts (OHLC visualization)
echo  - Volume Chart (color-coded bars below main chart)
echo  - Training Interface (click "Train Model" button)
echo  - Extended Timeframes (1D, 5D, 1M, 3M, 6M, 1Y, 2Y)
echo  - Chart Type Toggle (Line / Candlestick)
echo  - US and Australian (ASX) stocks support
echo.
echo Server Configuration:
echo   URL:  http://localhost:5001
echo   Port: 5001
echo   Mode: Development (with auto-reload)
echo.
echo ============================================================================
echo.
echo Server is starting...
echo.
echo After server starts:
echo   1. Open your browser
echo   2. Go to: http://localhost:5001
echo   3. Click any stock button or enter a symbol
echo   4. Click "Candlestick" to see OHLC candles
echo   5. Scroll down to see volume chart
echo   6. Click "Train Model" to train for any symbol
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.

REM Start the Flask server
python app_finbert_v4_dev.py

REM If server stops
echo.
echo Server stopped.
pause
