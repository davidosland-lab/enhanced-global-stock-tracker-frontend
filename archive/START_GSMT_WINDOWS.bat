@echo off
REM ============================================
REM Global Stock Market Tracker - Windows Launcher
REM Version: 1.0 - All 6 Modules Complete
REM ============================================

echo.
echo ==========================================
echo    GLOBAL STOCK MARKET TRACKER v1.0
echo    Starting Application...
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Navigate to the application directory
cd /d "%~dp0"

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required dependencies...
    echo This may take a few minutes on first run...
    pip install -r requirements.txt
)

REM Kill any existing backend processes on port 8002
echo Stopping any existing backend processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Start the backend
echo Starting backend server on port 8002...
start "GSMT Backend" /min cmd /c "python backend_fixed.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8002/ >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend may not have started properly
    echo Check the backend window for error messages
)

REM Start the frontend server
echo Starting frontend server on port 8080...
start "GSMT Frontend" /min cmd /c "python -m http.server 8080"

REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul

REM Open the dashboard in default browser
echo.
echo ==========================================
echo    APPLICATION STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo Backend API: http://localhost:8002
echo Frontend: http://localhost:8080
echo.
echo Opening dashboard in your browser...
start http://localhost:8080/simple_working_dashboard.html

echo.
echo Press any key to stop all services and exit...
pause >nul

REM Stop all services
echo.
echo Stopping all services...
taskkill /F /FI "WINDOWTITLE eq GSMT Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq GSMT Frontend*" >nul 2>&1

echo Services stopped. Goodbye!
timeout /t 2 /nobreak >nul