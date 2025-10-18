@echo off
echo ============================================================
echo Starting ML Stock Prediction System
echo Version: 3.0 FINAL (Sentiment DISABLED)
echo ============================================================
echo.
echo Server starting at: http://localhost:8000
echo Web interface at:   http://localhost:8000/interface
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python ml_core.py

echo.
echo ============================================================
echo Server stopped
echo ============================================================
pause