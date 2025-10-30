@echo off
echo ========================================================
echo FinBERT Trading System v3.1 - COMPLETE INSTALLER
echo With Intraday Trading and Zoom Features
echo ========================================================
echo.

:: Keep window open on error
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/3] Installing core dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [2/3] Creating shortcuts...
echo @echo off > START_INTRADAY.bat
echo echo Starting FinBERT v3.1 with Intraday and Zoom... >> START_INTRADAY.bat
echo python app_finbert_intraday.py >> START_INTRADAY.bat

echo @echo off > START_DAILY_ONLY.bat
echo echo Starting FinBERT v3.1 (Daily charts only)... >> START_DAILY_ONLY.bat
echo python app_finbert_daily_only.py >> START_DAILY_ONLY.bat

echo.
echo [3/3] Installation complete!
echo.
echo ========================================================
echo Installation Successful!
echo ========================================================
echo.
echo To start the system:
echo   - For FULL features (intraday + zoom): Run START_INTRADAY.bat
echo   - For daily charts only: Run START_DAILY_ONLY.bat
echo.
echo Then open: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul