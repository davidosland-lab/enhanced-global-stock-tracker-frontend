@echo off
echo ========================================================
echo FinBERT Trading System v3.1
echo INTRADAY TRADING + ZOOM FEATURES
echo ========================================================
echo.
echo Features:
echo   - Intraday intervals: 1m, 3m, 5m, 15m, 30m, 60m
echo   - Zoom: Mouse wheel, pinch, drag to zoom
echo   - Pan: Ctrl + drag
echo   - Real-time market data
echo   - VWAP indicator for intraday
echo   - Auto-refresh every 30 seconds
echo.
echo Starting server...
echo The system will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app_finbert_intraday.py

pause