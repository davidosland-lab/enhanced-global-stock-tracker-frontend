@echo off
echo ============================================================
echo      ML STOCK PREDICTOR - COMPLETE SYSTEM
echo ============================================================
echo.
echo This will start the complete server with all features!
echo.

:: Clean environment
del /q .env 2>nul
del /q .flaskenv 2>nul
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

:: Start the complete server
echo Starting complete server with all API endpoints...
echo.
echo ============================================================
echo Open your browser to: http://localhost:8000
echo All features will work!
echo ============================================================
echo.

python complete_server.py

pause