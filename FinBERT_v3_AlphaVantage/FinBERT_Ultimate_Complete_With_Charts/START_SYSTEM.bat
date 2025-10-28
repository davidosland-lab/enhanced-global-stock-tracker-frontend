@echo off
echo ================================================================================
echo STARTING FINBERT ULTIMATE v3.0 WITH ALPHA VANTAGE
echo ================================================================================
echo.

REM Clean environment
if exist ".env" del /f /q ".env"

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Data Sources:
echo   Primary: Yahoo Finance
echo   Backup: Alpha Vantage
echo.
echo Server starting on: http://localhost:5000
echo.
echo Available Endpoints:
echo   /                  - API Status
echo   /api/analyze       - Complete stock analysis
echo   /api/predict       - Get prediction
echo   /api/train         - Train ML model
echo   /api/technical     - Technical indicators
echo   /api/sentiment     - Sentiment analysis
echo   /api/health        - System health check
echo.
echo To view charts: Open finbert_charts.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

python app_finbert_ultimate_av.py