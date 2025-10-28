@echo off
REM ========================================
REM FinBERT Ultimate Trading System v3.2
REM System Startup Script for Windows 11
REM ========================================

echo.
echo =====================================
echo   FinBERT Ultimate Trading System
echo      Version 3.3 ENHANCED
echo   Now with Time & Volume Charts!
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please run INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found
    echo Please run INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating Python virtual environment...
call venv\Scripts\activate.bat

REM Check for required packages
echo [INFO] Checking dependencies...
python -c "import flask, yfinance, numpy, pandas, scikit-learn" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some dependencies missing
    echo Running pip install...
    pip install -r requirements.txt
)

REM Clear any cache issues
echo [INFO] Clearing cache...
if exist "%LOCALAPPDATA%\py-yfinance" (
    rd /s /q "%LOCALAPPDATA%\py-yfinance" >nul 2>&1
)

REM Start the application
echo.
echo [INFO] Starting FinBERT Trading System...
echo.
echo ========================================
echo   System will be available at:
echo   http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

REM Launch default browser after 3 seconds
start /b cmd /c "timeout /t 3 >nul && start http://localhost:5000"

REM Run the application
python app_finbert_complete_v3.2.py

REM Deactivate virtual environment when done
deactivate

echo.
echo [INFO] FinBERT Trading System stopped
pause