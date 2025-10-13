@echo off
REM ================================================================================
REM Stock Tracker - Installation and Startup Script
REM Handles frozen installations and missing dependencies
REM ================================================================================

setlocal enabledelayedexpansion

echo.
echo =========================================================================
echo    STOCK TRACKER - INSTALLATION AND STARTUP
echo =========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python detected successfully!
echo.

REM Create a flag file to track installation
set "INSTALL_FLAG=.installed"

if not exist "%INSTALL_FLAG%" (
    echo [FIRST TIME SETUP] Installing required packages...
    echo This will take 2-5 minutes. Please be patient...
    echo.
    
    REM Upgrade pip first
    echo Upgrading pip...
    python -m pip install --upgrade pip
    
    REM Install packages one by one to avoid freezing
    echo.
    echo Installing FastAPI framework...
    python -m pip install fastapi
    
    echo Installing Uvicorn server...
    python -m pip install uvicorn
    
    echo Installing Yahoo Finance...
    python -m pip install yfinance
    
    echo Installing data processing libraries...
    python -m pip install pandas numpy
    
    echo Installing timezone support...
    python -m pip install pytz
    
    echo Installing file upload support...
    python -m pip install python-multipart aiofiles
    
    echo Installing ML libraries (optional, may skip if issues)...
    python -m pip install scikit-learn 2>nul || echo Skipped scikit-learn
    
    REM Create installation flag
    echo Installation completed on %date% %time% > "%INSTALL_FLAG%"
    
    echo.
    echo =========================================================================
    echo    INSTALLATION COMPLETE!
    echo =========================================================================
    echo.
) else (
    echo Dependencies already installed. Skipping installation...
    echo.
)

REM Kill any existing services
echo Cleaning up any running services...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 >nul

echo.
echo Starting services...
echo.

REM Start Backend Service
echo [1/3] Starting Backend Service (Port 8002)...
start /b cmd /c "python backend.py 8002 2>nul"
timeout /t 3 >nul

REM Start ML Service
echo [2/3] Starting ML Service (Port 8003)...
start /b cmd /c "python ml_backend.py 8003 2>nul"
timeout /t 3 >nul

REM Start Frontend
echo [3/3] Starting Web Interface (Port 8000)...
start /b cmd /c "python -m http.server 8000 --bind 127.0.0.1 2>nul"
timeout /t 2 >nul

echo.
echo =========================================================================
echo    STOCK TRACKER IS RUNNING!
echo =========================================================================
echo.
echo Opening your browser...
timeout /t 2 >nul
start http://localhost:8000

echo.
echo Services are running at:
echo   - Web Interface: http://localhost:8000
echo   - Backend API:   http://localhost:8002/docs
echo   - ML Service:    http://localhost:8003/docs
echo.
echo IMPORTANT: Keep this window open!
echo Press Ctrl+C or close this window to stop all services.
echo.
echo =========================================================================
echo.

REM Keep the script running
:loop
timeout /t 60 >nul
goto loop

endlocal