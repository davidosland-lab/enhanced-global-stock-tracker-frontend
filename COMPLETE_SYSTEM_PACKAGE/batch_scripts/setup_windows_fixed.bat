@echo off
echo ======================================
echo UNIFIED STOCK ANALYSIS SYSTEM
echo Windows 11 Installation
echo ======================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set FLASK_SKIP_DOTENV=1

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip first (fixing warning)...
python -m pip install --upgrade pip --quiet 2>nul

echo [4/5] Installing required packages...
pip install flask flask-cors yfinance pandas numpy scikit-learn requests plotly --quiet 2>nul

echo [5/5] Setting environment variables...
set FLASK_APP=unified_stock_professional.py
set FLASK_ENV=production
set FLASK_SKIP_DOTENV=1

echo.
echo ======================================
echo APPLICATION READY!
echo ======================================
echo Access the system at: http://localhost:8000
echo.
echo QUICK TEST:
echo 1. Open browser to http://localhost:8000
echo 2. Click 'CBA' button for Australian stock
echo 3. Select 'Intraday (1 Day)' for real-time data
echo 4. View ML predictions and indicators
echo ======================================
echo.

python unified_stock_professional.py