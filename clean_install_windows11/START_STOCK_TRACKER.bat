@echo off
REM =====================================================
REM Stock Tracker Master Startup - Windows 11
REM Version 5.0 - All Services on Localhost
REM =====================================================

echo =====================================================
echo Stock Tracker Master Startup v5.0
echo =====================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Kill any existing processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 >nul

REM Install required packages
echo Installing required packages...
pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy scikit-learn aiofiles python-multipart

REM Start Frontend Server (Port 8000)
echo.
echo Starting Frontend Server on http://localhost:8000
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 >nul

REM Start Backend API (Port 8002)
echo Starting Backend API on http://localhost:8002
start "Backend API" cmd /k "python backend.py"
timeout /t 3 >nul

REM Start ML Backend (Port 8003)
echo Starting ML Backend on http://localhost:8003
if exist backend_ml_fixed.py (
    start "ML Backend" cmd /k "python backend_ml_fixed.py"
) else if exist backend_ml_working.py (
    start "ML Backend" cmd /k "python backend_ml_working.py"
) else (
    echo WARNING: ML Backend file not found
)
timeout /t 3 >nul

REM Verify all services are running
echo.
echo =====================================================
echo Verifying services...
echo =====================================================
timeout /t 3 >nul

curl -s http://localhost:8000 >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Frontend Server: http://localhost:8000
) else (
    echo [FAIL] Frontend Server not responding
)

curl -s http://localhost:8002/api/health >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Backend API: http://localhost:8002
) else (
    echo [FAIL] Backend API not responding
)

curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel%==0 (
    echo [OK] ML Backend: http://localhost:8003
) else (
    echo [FAIL] ML Backend not responding
)

echo.
echo =====================================================
echo Stock Tracker is running!
echo Open your browser to: http://localhost:8000
echo =====================================================
echo.
echo Press Ctrl+C in each window to stop services
echo Or run SHUTDOWN_ALL.bat to stop all services
echo.
pause
