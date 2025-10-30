@echo off
REM =========================================================================
REM FinBERT v4.0 - Windows 11 Startup Script
REM Starts the Flask backend server
REM =========================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 - Professional Trading System
echo   Starting Server...
echo ========================================================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run INSTALL_WINDOWS11.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Check if app file exists
if not exist app_finbert_v4_dev.py (
    echo [ERROR] Application file not found!
    echo Please ensure app_finbert_v4_dev.py is in the same directory.
    pause
    exit /b 1
)

echo ========================================================================
echo   Starting FinBERT v4.0 Server
echo ========================================================================
echo.
echo Server will start on: http://localhost:5001
echo.
echo Features:
echo   - Real-time Stock Data (Yahoo Finance)
echo   - LSTM Neural Network Predictions
echo   - FinBERT Sentiment Analysis (Real News)
echo   - Interactive Candlestick Charts (ECharts)
echo   - Volume Analysis
echo   - Technical Indicators
echo.
echo To access the application:
echo   1. Wait for server to start (you'll see "Running on http://...")
echo   2. Open your browser
echo   3. Go to: http://localhost:5001/finbert_v4_enhanced_ui.html
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================================================
echo.

REM Start the Flask application
python app_finbert_v4_dev.py

REM If the application exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server encountered an error and stopped
    echo.
    pause
)
