@echo off
REM ================================================================================
REM Stock Tracker Integrated - Quick Start for Windows 11
REM ================================================================================

echo.
echo =========================================================================
echo    STOCK TRACKER INTEGRATED - QUICK START
echo =========================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo [1/5] Installing required packages...
echo This may take a few minutes on first run...
echo.

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo Packages installed successfully!
echo.

REM Kill existing processes
echo [2/5] Cleaning up any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 >nul

echo [3/5] Starting Backend Service (Port 8002)...
start /min cmd /c "python backend.py 8002"
timeout /t 3 >nul

echo [4/5] Starting ML Service (Port 8003)...
start /min cmd /c "python ml_backend.py 8003"
timeout /t 3 >nul

echo [5/5] Starting Web Interface (Port 8000)...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 >nul

echo.
echo =========================================================================
echo    STOCK TRACKER IS READY!
echo =========================================================================
echo.
echo Opening web browser...
start http://localhost:8000
echo.
echo Services running:
echo   - Web Interface: http://localhost:8000
echo   - Backend API:   http://localhost:8002
echo   - ML Service:    http://localhost:8003
echo.
echo Press any key to stop all services and exit...
pause >nul

REM Stop all services
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo All services stopped.
timeout /t 2 >nul