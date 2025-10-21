@echo off
echo ============================================================
echo ML Stock Prediction System - Clean Installation
echo Version: 3.0 FINAL
echo ============================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found. Installing packages...
echo.

echo [1/7] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/7] Installing data processing libraries...
pip install pandas numpy

echo.
echo [3/7] Installing machine learning libraries...
pip install scikit-learn

echo.
echo [4/7] Installing technical analysis library...
pip install ta

echo.
echo [5/7] Installing Yahoo Finance and curl_cffi (REQUIRED)...
pip install yfinance requests curl_cffi

echo.
echo [6/7] Installing web framework...
pip install fastapi uvicorn python-multipart

echo.
echo [7/7] Installing optional libraries...
pip install xgboost python-dateutil

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Run 2_TEST.bat to verify installation
echo   2. Run 3_START.bat to start the system
echo.
pause