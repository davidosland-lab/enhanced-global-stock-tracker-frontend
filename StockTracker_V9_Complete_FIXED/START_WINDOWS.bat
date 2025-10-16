@echo off
echo ============================================================
echo Stock Tracker V9 - Starting Services
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if required modules are installed
echo Checking dependencies...
python -c "import fastapi, yfinance, sklearn, pandas" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Required packages not installed
    echo Please run INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

REM Kill any existing Python processes on our ports
echo Checking for existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Stopping existing service on port 8002...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Stopping existing service on port 8003...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do (
    echo Stopping existing service on port 8004...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do (
    echo Stopping existing service on port 8005...
    taskkill /F /PID %%a 2>nul
)

REM Small delay to ensure ports are freed
timeout /t 2 /nobreak >nul

REM Start services
echo.
echo Starting all services...
echo ============================================================
python start_services.py

REM If Python script exits, pause to see any error messages
pause