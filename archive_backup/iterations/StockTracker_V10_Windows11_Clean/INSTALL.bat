@echo off
echo ========================================
echo StockTracker V10 - Windows 11 Installation
echo Real Data Only - No Mock/Simulated Data
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel

echo [4/5] Installing core requirements...
pip install fastapi uvicorn pandas numpy yfinance scikit-learn requests python-multipart websockets joblib scipy ta certifi aiohttp

echo [5/5] Installing optional FinBERT (may take time)...
echo Note: If this fails, the system will use keyword-based sentiment analysis
pip install transformers torch --timeout 300 2>nul || echo FinBERT installation skipped - will use fallback

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the system, run: START.bat
echo.
pause