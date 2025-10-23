@echo off
echo ============================================================
echo CHART TEST - Stock Analysis System
echo ============================================================
echo.
echo This will test if the charts are working correctly.
echo.
echo Starting server on port 5000...
echo.
echo ============================================================
echo INSTRUCTIONS:
echo 1. Server will start in a moment
echo 2. Open your browser to: http://localhost:5000
echo 3. Enter a stock symbol (e.g., AAPL, MSFT, CBA)
echo 4. Click "Get Analysis"
echo 5. Check if chart displays correctly
echo 6. Try switching between Candlestick and Line chart types
echo ============================================================
echo.
echo Press Ctrl+C to stop the server when done testing
echo.
pause
python app.py
pause