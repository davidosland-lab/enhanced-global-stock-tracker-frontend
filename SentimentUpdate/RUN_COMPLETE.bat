@echo off
title Complete Stock Analysis - ML, Sentiment & Charts
echo ============================================================
echo    COMPLETE STOCK ANALYSIS SYSTEM
echo ============================================================
echo.
echo Features:
echo [✓] Full Candlestick, Line, and Volume Charts
echo [✓] Chart Zoom and Pan functionality
echo [✓] ML Predictions with RandomForest (if sklearn available)
echo [✓] Market Sentiment (VIX, Market Breadth)
echo [✓] Technical Indicators (RSI, MACD, Bollinger, SMA)
echo [✓] Feature Importance Display
echo [✓] Australian Stocks Support (.AX auto-added)
echo [✓] Rate Limiting Protection (2s delays)
echo [✓] Yahoo Finance with Alpha Vantage Fallback
echo.

REM Stop existing services
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

echo Starting complete system...
python app_complete_ml_sentiment.py

pause