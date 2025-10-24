@echo off
title Enhanced Weighted Sentiment-ML Stock Analysis
echo ================================================================================
echo ENHANCED WEIGHTED SENTIMENT-ML STOCK ANALYSIS SYSTEM
echo ================================================================================
echo.
echo Features:
echo   * Adjustable sentiment weight slider (0-2x)
echo   * Pre-calculated sentiment values (no API calls during ML training)
echo   * Combined sentiment-technical ML features
echo   * Feature importance visualization
echo   * Real-time sentiment weight adjustment
echo.
echo ================================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
echo.
pip install --quiet flask flask-cors yfinance requests pandas numpy scikit-learn 2>nul

echo.
echo Starting Enhanced Weighted Sentiment-ML Server...
echo.
echo ================================================================================
echo Server will start at: http://localhost:5001
echo.
echo FEATURES:
echo   1. Move the sentiment weight slider to adjust influence (0 = pure technical, 2 = heavy sentiment)
echo   2. Click "Get ML Predictions with Sentiment" to see weighted predictions
echo   3. View feature importance to see how much sentiment affects the model
echo   4. Pre-calculated sentiment means NO delays during ML training
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

python app_weighted_sentiment_ml.py

echo.
echo Server stopped.
pause