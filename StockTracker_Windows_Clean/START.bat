@echo off
echo ====================================
echo Stock Tracker v9.0 - Windows Launcher
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python detected...
echo.

:: Install required packages
echo [2/4] Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet flask flask-cors yfinance pandas numpy scikit-learn xgboost lightgbm requests cachetools python-dateutil pytz

echo.
echo [3/4] Starting backend server...
:: Kill any existing Python processes on port 8002
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8002"') do taskkill /F /PID %%a >nul 2>&1

:: Start backend server
start /min cmd /c "python backend.py"

:: Wait for server to start
timeout /t 3 /nobreak >nul

echo.
echo [4/4] Opening Stock Tracker in browser...
start http://localhost:8002

echo.
echo ====================================
echo Stock Tracker is running!
echo Access at: http://localhost:8002
echo Press Ctrl+C in the server window to stop
echo ====================================
pause