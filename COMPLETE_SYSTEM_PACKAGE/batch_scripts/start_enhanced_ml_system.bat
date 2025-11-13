@echo off
title Enhanced ML Stock Prediction System v2.0
cls

echo ================================================================================
echo        ENHANCED ML STOCK PREDICTION SYSTEM v2.0
echo        Based on ScienceDirect Research Findings
echo ================================================================================
echo.
echo Features:
echo - Support Vector Machines (SVM) and Neural Networks
echo - 50+ Technical Indicators (2,173 variables from research)
echo - SQLite Caching for 50x faster data retrieval
echo - Ensemble and Stacking Methods  
echo - Market Regime Adaptive Models
echo - Real FinBERT Sentiment Analysis
echo - Comprehensive Backtesting with $100,000 capital
echo.
echo ================================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/3] Installing required packages...
echo.

REM Install core packages
pip install --quiet fastapi uvicorn pandas numpy yfinance scikit-learn scipy 2>nul

REM Install advanced ML packages
pip install --quiet xgboost 2>nul

REM Install technical analysis
pip install --quiet TA-Lib 2>nul
if errorlevel 1 (
    echo Note: TA-Lib installation failed. Using basic indicators.
    echo For full features, install TA-Lib from: https://www.ta-lib.org
)

REM Install FinBERT
echo.
echo [2/3] Installing FinBERT for sentiment analysis...
pip install --quiet transformers torch 2>nul
if errorlevel 1 (
    echo Note: FinBERT installation failed. Sentiment analysis will be limited.
)

echo.
echo [3/3] Starting Enhanced ML System...
echo.
echo ================================================================================
echo Server starting at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Start the enhanced ML system
python ml_prediction_backtesting_enhanced.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the server.
    echo Please check the error messages above.
    pause
)