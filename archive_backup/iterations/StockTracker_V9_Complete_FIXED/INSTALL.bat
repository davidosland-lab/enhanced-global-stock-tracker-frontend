@echo off
echo ============================================================
echo Stock Tracker V9 - Complete Edition Installation
echo Real ML, Real Data, Real Predictions
echo ============================================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [2/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/4] Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To install FinBERT for real sentiment analysis (optional):
echo   pip install transformers torch
echo.
echo To start the system:
echo   Run START.bat
echo.
pause