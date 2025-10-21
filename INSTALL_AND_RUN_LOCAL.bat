@echo off
echo ======================================================================
echo UNIFIED STOCK ANALYSIS SYSTEM - LOCAL CHARTS VERSION
echo ======================================================================
echo.
echo This installer will set up the complete stock analysis system
echo with LOCAL charting (no CDN dependencies required)
echo.
echo Features:
echo - Yahoo Finance + Alpha Vantage integration
echo - Australian stocks with automatic .AX suffix
echo - 12 Technical indicators (RSI, MACD, Bollinger Bands, etc.)
echo - ML Predictions (Random Forest, Gradient Boosting)
echo - Custom SVG charts (Candlestick, Line, Area)
echo - No internet required for charts (all code embedded)
echo.
pause

echo.
echo Step 1: Installing Python packages...
echo ======================================================================
pip install flask flask-cors yfinance pandas numpy scikit-learn requests

echo.
echo Step 2: Starting the server...
echo ======================================================================
echo.
echo Server will start at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python unified_stock_system_local.py

pause
