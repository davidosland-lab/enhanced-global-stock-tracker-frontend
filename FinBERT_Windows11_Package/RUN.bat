@echo off
REM FinBERT Trading System - Run Script for Windows 11

echo ========================================
echo Starting FinBERT Trading System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [✓] Virtual environment activated
echo.

REM Check if required modules are installed
python -c "import torch, transformers, flask" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Required modules not installed!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

REM Start the application
echo ========================================
echo Starting FinBERT Trading System...
echo ========================================
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the application
python app_finbert_trading.py

REM If the application exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error!
    pause
)