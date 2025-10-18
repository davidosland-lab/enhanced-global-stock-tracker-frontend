@echo off
echo =====================================
echo ML Stock Prediction System - Starting
echo WITH AUTOMATIC SAMPLE DATA FALLBACK
echo =====================================
echo.
echo This version automatically uses sample data
echo if Yahoo Finance is not working.
echo.
echo Starting server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python ml_core_with_fallback.py

echo.
echo Server stopped.
pause