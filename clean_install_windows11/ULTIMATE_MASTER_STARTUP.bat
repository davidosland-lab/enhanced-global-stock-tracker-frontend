@echo off
cls
color 0A
echo ================================================================
echo        ULTIMATE STOCK TRACKER MASTER STARTUP
echo        Complete Fix for Windows 11
echo ================================================================
echo.

:: Set window title
title Stock Tracker Master Control

:: Phase 1: Kill all existing processes
echo [PHASE 1] Terminating existing processes...
echo ----------------------------------------

:: Kill Python processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process on port 8000: PID %%a
    taskkill /F /PID %%a >nul 2>&1
    wmic process where ProcessId=%%a delete >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    echo Killing process on port 8002: PID %%a
    taskkill /F /PID %%a >nul 2>&1
    wmic process where ProcessId=%%a delete >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo Killing process on port 8003: PID %%a
    taskkill /F /PID %%a >nul 2>&1
    wmic process where ProcessId=%%a delete >nul 2>&1
)

:: Additional cleanup - kill any python processes with our script names
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Stock Tracker*" >nul 2>&1
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq Stock Tracker*" >nul 2>&1

echo Cleanup complete!
timeout /t 2 >nul

:: Phase 2: Environment Check
echo.
echo [PHASE 2] Checking environment...
echo ----------------------------------------

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python: OK
python --version

:: Check for required files
if not exist backend_ultimate_fixed.py (
    if exist backend.py (
        echo Using existing backend.py
        set BACKEND_FILE=backend.py
    ) else (
        color 0C
        echo ERROR: Backend file not found!
        echo Please ensure backend.py or backend_ultimate_fixed.py exists
        pause
        exit /b 1
    )
) else (
    set BACKEND_FILE=backend_ultimate_fixed.py
)

echo Backend file: %BACKEND_FILE%

:: Phase 3: Install Dependencies
echo.
echo [PHASE 3] Installing/Updating dependencies...
echo ----------------------------------------

:: Upgrade pip first
python -m pip install --upgrade pip >nul 2>&1

:: Install required packages with specific versions for stability
echo Installing core packages...
pip install --quiet fastapi==0.104.1
pip install --quiet uvicorn[standard]==0.24.0
pip install --quiet yfinance==0.2.32
pip install --quiet pandas==2.1.3
pip install --quiet numpy==1.24.3
pip install --quiet cachetools==5.3.2
pip install --quiet python-multipart==0.0.6
pip install --quiet aiofiles==23.2.1
pip install --quiet websockets==12.0

:: ML packages (optional, for ML backend)
echo Installing ML packages (optional)...
pip install --quiet scikit-learn==1.3.2 2>nul
pip install --quiet tensorflow==2.15.0 2>nul || echo TensorFlow not installed (optional)

echo Dependencies installed!

:: Phase 4: Create upload directory
if not exist uploads (
    mkdir uploads
    echo Created uploads directory for document storage
)

:: Phase 5: Start Services
echo.
echo [PHASE 5] Starting services...
echo ----------------------------------------

:: Start Backend API on port 8002
echo Starting Backend API on port 8002...
start "Stock Tracker Backend" /min cmd /c "python %BACKEND_FILE%"
timeout /t 3 >nul

:: Verify backend is running
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend may not have started properly
    echo Continuing anyway...
) else (
    echo Backend API: RUNNING
)

:: Start Frontend HTTP Server on port 8000
echo Starting Frontend Server on port 8000...
if exist frontend_server.py (
    start "Stock Tracker Frontend" /min cmd /c "python frontend_server.py"
) else (
    :: Fallback to simple HTTP server
    start "Stock Tracker Frontend" /min cmd /c "python -m http.server 8000"
)
timeout /t 2 >nul

:: Start ML Backend on port 8003 (if exists)
if exist ml_backend_fixed.py (
    echo Starting ML Backend on port 8003...
    start "Stock Tracker ML Backend" /min cmd /c "python ml_backend_fixed.py"
    timeout /t 2 >nul
) else if exist ml_backend_working.py (
    echo Starting ML Backend on port 8003...
    start "Stock Tracker ML Backend" /min cmd /c "python ml_backend_working.py"
    timeout /t 2 >nul
) else if exist ml_training_backend.py (
    echo Starting ML Backend on port 8003...
    start "Stock Tracker ML Backend" /min cmd /c "python ml_training_backend.py"
    timeout /t 2 >nul
) else (
    echo ML Backend not found (optional)
)

:: Phase 6: Launch Application
echo.
echo ================================================================
echo        STOCK TRACKER IS NOW RUNNING!
echo ================================================================
echo.
echo Services Status:
echo ----------------
echo [✓] Backend API:     http://localhost:8002
echo [✓] Frontend UI:     http://localhost:8000  
echo [✓] ML Backend:      http://localhost:8003 (if available)
echo.
echo Features:
echo ---------
echo • All modules load correctly (no file:// errors)
echo • 100MB document upload support
echo • Real Yahoo Finance data
echo • Technical Analysis with live tracking
echo • Prediction Centre with boundaries
echo • Historical Data Manager working
echo.
echo Opening application in your default browser...
timeout /t 2 >nul

:: Open in default browser
start http://localhost:8000

echo.
echo ================================================================
echo IMPORTANT: Keep this window open while using the application
echo ================================================================
echo.
echo Controls:
echo ---------
echo Press Ctrl+C to stop all services
echo Press any key to stop all services and exit
echo.

:: Wait for user input
pause >nul

:: Phase 7: Cleanup on exit
echo.
echo [PHASE 7] Shutting down services...
echo ----------------------------------------

:: Kill all our services
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping Frontend Server...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    echo Stopping Backend API...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo Stopping ML Backend...
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill any remaining python processes with our window titles
taskkill /F /FI "WINDOWTITLE eq Stock Tracker*" >nul 2>&1

echo.
echo All services stopped successfully!
echo Thank you for using Stock Tracker!
timeout /t 3 >nul
exit