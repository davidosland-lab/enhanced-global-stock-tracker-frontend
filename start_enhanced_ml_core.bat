@echo off
echo ================================================================
echo       ML CORE ENHANCED PRODUCTION SYSTEM v2.0
echo ================================================================
echo.
echo Starting rock-solid ML prediction system with:
echo   - Ensemble models (RandomForest, XGBoost, SVM, Neural Networks)
echo   - 30-35 optimized features
echo   - SQLite caching (50x faster)
echo   - Comprehensive backtesting with transaction costs
echo.
echo ================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
echo.

:: Install required packages
pip install --quiet --upgrade fastapi uvicorn pandas numpy yfinance scikit-learn xgboost 2>nul
pip install --quiet --upgrade scipy pydantic python-multipart 2>nul

:: Try to install TA-Lib (might fail on Windows without pre-built wheel)
echo Installing TA-Lib (optional - may require manual installation)...
pip install --quiet TA-Lib 2>nul || echo TA-Lib not available - using fallback calculations

echo.
echo [2/4] Initializing databases...
echo.

:: Create data directory if it doesn't exist
if not exist "data" mkdir data

echo [3/4] Starting ML Core Enhanced System...
echo.
echo ================================================================
echo.
echo System will be available at:
echo.
echo   Dashboard: http://localhost:8000/interface
echo   API Docs:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================
echo.

:: Start the server
python ml_core_enhanced_production.py

pause