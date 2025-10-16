@echo off
echo ========================================
echo StockTracker V6 - Starting All Services
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment and install requirements
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    echo.
    echo Packages installed successfully.
    echo.
)

REM Start services in separate windows
echo Starting Main Backend API (Port 8002)...
start "Main Backend API" cmd /k "call venv\Scripts\activate.bat && python backend.py"
timeout /t 3 >nul

echo Starting ML Backend Service (Port 8003)...
start "ML Backend Service" cmd /k "call venv\Scripts\activate.bat && python ml_backend_enhanced.py"
timeout /t 3 >nul

echo Starting Integration Bridge (Port 8004)...
start "Integration Bridge" cmd /k "call venv\Scripts\activate.bat && python integration_bridge.py"
timeout /t 3 >nul

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Main Dashboard: http://localhost:8002
echo ML Interface:   http://localhost:8002/modules/ml_unified.html
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

REM Open browser
start http://localhost:8002

echo.
echo Services are running. Close this window to continue using the system.
echo To stop all services, close each service window individually.
pause