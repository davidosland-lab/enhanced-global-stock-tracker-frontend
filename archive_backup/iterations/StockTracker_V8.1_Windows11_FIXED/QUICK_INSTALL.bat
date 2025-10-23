@echo off
cls
echo ============================================================
echo    Stock Tracker V8 - Quick Installation
echo ============================================================
echo.

:: Simple Python check
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install from python.org
    pause
    exit
)

:: Install packages without virtual environment
echo Installing packages (this may take a few minutes)...
pip install fastapi uvicorn yfinance pandas numpy scikit-learn joblib requests

:: Create directories
mkdir models 2>nul
mkdir logs 2>nul
mkdir data 2>nul
mkdir saved_models 2>nul
mkdir cache 2>nul

echo.
echo ============================================================
echo Installation complete!
echo Run START_TRACKER.bat to begin
echo ============================================================
pause