@echo off
REM Installation script for Windows
REM Swing Trading + Intraday Integration v1.0

echo ==========================================
echo Swing Trading + Intraday Integration v1.0
echo Installation Script (Windows)
echo ==========================================
echo.

REM Check Python installation
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist backups mkdir backups

REM Run tests
echo.
echo Running integration tests...
python test_integration.py
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed. Please review errors above.
    echo You may still proceed, but fix issues before live trading.
) else (
    echo.
    echo SUCCESS: All tests passed!
)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit config.json with your settings
echo 2. Configure alerts (Telegram, Email, SMS)
echo 3. Run: python live_trading_coordinator.py --paper-trading
echo.
echo To activate the environment in future sessions:
echo   venv\Scripts\activate.bat
echo.
pause
