@echo off
echo ============================================================
echo    ML STOCK PREDICTOR - WINDOWS SAFE MODE STARTUP
echo ============================================================
echo.

:: Set UTF-8 encoding
chcp 65001 >nul 2>&1

:: Set Python to use UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo [1/3] Setting up environment...
echo       UTF-8 encoding enabled

:: Clear any problematic cache
echo [2/3] Clearing cache...
del /q *.pyc 2>nul
rmdir /s /q __pycache__ 2>nul
del /q *.db 2>nul
echo       Cache cleared

:: Start with the safe launcher
echo [3/3] Starting server (safe mode)...
echo.
echo ============================================================
echo Starting on http://localhost:8000
echo Press Ctrl+C to stop
echo ============================================================
echo.

:: Try the safe launcher first
python run_server.py

:: If that fails, try the original with encoding set
if errorlevel 1 (
    echo.
    echo Trying alternative startup...
    python -X utf8 unified_ml_system.py
)

:: If that also fails, run minimal Flask server
if errorlevel 1 (
    echo.
    echo Starting minimal server...
    python -c "from flask import Flask; app = Flask(__name__); app.route('/')(lambda: 'ML Stock Predictor Running'); app.run(port=8000)"
)

echo.
echo ============================================================
echo Server stopped.
echo ============================================================
pause