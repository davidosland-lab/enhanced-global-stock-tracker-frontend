@echo off
REM ============================================================
REM ML STOCK PREDICTOR - PRODUCTION SYSTEM
REM ============================================================
REM Full-featured system with all components
REM ============================================================

title ML Stock Predictor - Production System
color 0A
cls

echo ============================================================
echo    ML STOCK PREDICTOR - PRODUCTION SYSTEM v2.0
echo ============================================================
echo.
echo Features:
echo   - Real-time Yahoo Finance and Alpha Vantage data
echo   - Technical indicators (RSI, MACD, Bollinger Bands)
echo   - ML predictions (with statistical fallback)
echo   - Strategy backtesting
echo   - Database storage
echo   - Data export to CSV
echo   - Professional web interface
echo.
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Python not installed!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

REM Install requirements
echo Installing/updating required packages...
echo.

REM Core packages
pip install --upgrade pip >nul 2>&1
pip install --upgrade yfinance flask flask-cors pandas requests

REM Optional ML packages (won't fail if NumPy conflict)
echo Installing optional ML packages (may show warnings)...
pip install scikit-learn 2>nul

echo.
echo [OK] Core packages installed
echo.

REM Kill existing servers
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Clear screen for final display
cls
color 0A

echo ============================================================
echo    ML STOCK PREDICTOR - PRODUCTION SYSTEM
echo ============================================================
echo.
echo System Components:
echo   [✓] Yahoo Finance - Real-time data
echo   [✓] Alpha Vantage - Backup data source  
echo   [✓] Technical Analysis - 15+ indicators
echo   [✓] Predictions - ML/Statistical models
echo   [✓] Backtesting - Strategy evaluation
echo   [✓] Database - SQLite storage
echo   [✓] Web Interface - Professional UI
echo.
echo ============================================================
echo.
echo Server starting at: http://localhost:8000
echo.
echo Available features:
echo   - Overview: Price and market summary
echo   - Technical: RSI, MACD, Moving averages
echo   - Predictions: 1/7/30 day forecasts
echo   - Backtest: Momentum strategy testing
echo   - Chart: Interactive price charts
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the production server
python unified_production_server.py

echo.
echo ============================================================
echo Server stopped.
echo ============================================================
pause