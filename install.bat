@echo off
echo ======================================================================
echo       STOCK ANALYSIS SYSTEM - WINDOWS 11 INSTALLER
echo ======================================================================
echo.
echo This installer will set up the Stock Analysis System on your Windows 11 PC
echo.
echo Prerequisites:
echo - Python 3.8 or higher must be installed
echo - Internet connection for downloading packages
echo.
pause

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo [1/5] Python detected successfully!
python --version

echo.
echo [2/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [4/5] Installing required packages...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [5/5] Creating start script...
echo @echo off > start_server.bat
echo echo Starting Stock Analysis System... >> start_server.bat
echo call venv\Scripts\activate.bat >> start_server.bat
echo set FLASK_SKIP_DOTENV=1 >> start_server.bat
echo python stock_analysis_fixed_charts.py >> start_server.bat
echo pause >> start_server.bat

echo.
echo ======================================================================
echo       INSTALLATION COMPLETED SUCCESSFULLY!
echo ======================================================================
echo.
echo To start the Stock Analysis System:
echo 1. Double-click "start_server.bat"
echo 2. Open your browser and go to: http://localhost:8000
echo.
echo Features:
echo - Real-time stock data from Yahoo Finance
echo - Professional candlestick, line, and area charts
echo - Technical indicators (RSI, MACD, Bollinger Bands)
echo - Support for US and Australian stocks
echo - Auto-refresh capability
echo.
echo Press any key to exit the installer...
pause >nul