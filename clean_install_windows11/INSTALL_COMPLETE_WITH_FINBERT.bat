@echo off
echo ========================================================================
echo    STOCK TRACKER COMPLETE INSTALLATION WITH FINBERT AND ML INTEGRATION
echo ========================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/8] Installing base dependencies...
pip install --upgrade pip
pip install fastapi uvicorn yfinance pandas numpy python-multipart cachetools pytz

echo.
echo [2/8] Installing ML dependencies...
pip install scikit-learn joblib matplotlib seaborn xgboost

echo.
echo [3/8] Installing FinBERT dependencies (this may take a while)...
echo Note: This will download the FinBERT model (~400MB) on first use
pip install transformers torch

echo.
echo [4/8] Installing additional analysis tools...
pip install textblob nltk beautifulsoup4 requests

echo.
echo [5/8] Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "historical_data" mkdir historical_data
if not exist "cache" mkdir cache
if not exist "models" mkdir models
if not exist "ml_models" mkdir ml_models
if not exist "knowledge_base" mkdir knowledge_base

echo.
echo [6/8] Setting up ML integration database...
python -c "import sqlite3; conn = sqlite3.connect('ml_integration_bridge.db'); conn.execute('CREATE TABLE IF NOT EXISTS knowledge_base (id INTEGER PRIMARY KEY, module TEXT, data TEXT, timestamp DATETIME, metadata TEXT)'); conn.commit(); conn.close()"

echo.
echo [7/8] Testing FinBERT installation...
python -c "from finbert_analyzer import get_analyzer; analyzer = get_analyzer(); print('FinBERT is ready!' if analyzer else 'Using fallback mode')"

echo.
echo [8/8] Creating desktop shortcuts...
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcut.ps1

echo.
echo ========================================================================
echo    INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo FinBERT Features:
echo - Real financial sentiment analysis (no random data)
echo - Consistent results for the same text
echo - ML integration across all 11 modules
echo - Knowledge base persistence
echo.
echo To start the application:
echo   1. Run START_STOCK_TRACKER.bat
echo   2. Open http://localhost:8002 in your browser
echo.
echo For ML Integration Bridge (optional):
echo   Run: python integration_bridge.py
echo   This enables advanced ML features and module communication
echo.
pause