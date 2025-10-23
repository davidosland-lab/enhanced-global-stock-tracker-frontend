@echo off
title ML Prediction Backtesting Unified System
echo =============================================
echo ML PREDICTION BACKTESTING - UNIFIED SYSTEM
echo =============================================
echo.
echo Starting unified ML, Prediction, and Backtesting service...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Start the unified backend
echo Starting backend on port 8000...
start "ML Backend" python ml_prediction_backtesting_unified.py

REM Wait for service to start
echo Waiting for service to start...
timeout /t 5 /nobreak >nul

REM Open the interface
echo Opening browser interface...
start http://localhost:8000/
start ml_prediction_backtesting_interface.html

echo.
echo =============================================
echo SYSTEM RUNNING!
echo =============================================
echo.
echo Backend API: http://localhost:8000/
echo Interface: ml_prediction_backtesting_interface.html
echo.
echo Features:
echo - Real ML training (10-60 seconds)
echo - Real predictions with FinBERT sentiment
echo - Comprehensive backtesting ($100,000 capital)
echo - Multiple strategies (ML-based, Momentum, Mean Reversion)
echo - NO FAKE DATA - all real market data
echo.
echo Press Ctrl+C in the backend window to stop
echo.
pause