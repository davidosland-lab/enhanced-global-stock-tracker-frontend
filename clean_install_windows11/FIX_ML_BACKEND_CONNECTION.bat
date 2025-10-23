@echo off
title Fix ML Backend Connection Issue
color 0A

echo ================================================================================
echo                 FIX ML BACKEND CONNECTION REFUSED ERROR
echo ================================================================================
echo.
echo Fixing: GET http://localhost:8003/health net::ERR_CONNECTION_REFUSED
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ first
    pause
    exit /b 1
)

echo [1/5] Checking current services...
echo.

:: Check what's running on our ports
netstat -an | findstr :8003 >nul 2>&1
if %errorlevel% == 0 (
    echo Found service on port 8003, stopping it...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo [2/5] Checking for ML Backend file...
echo.

if not exist backend_ml_enhanced.py (
    echo ERROR: backend_ml_enhanced.py not found!
    echo.
    echo The ML Backend file is missing from this directory.
    echo Please ensure you have extracted ALL files from the zip.
    echo.
    echo Expected file: backend_ml_enhanced.py
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

echo    ✓ ML Backend file found

echo.
echo [3/5] Installing required Python packages...
echo.

:: Install required packages silently
pip install fastapi uvicorn yfinance pandas numpy scikit-learn >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Python packages installed
) else (
    echo    ! Some packages may have failed to install
    echo    Running verbose install...
    pip install fastapi uvicorn yfinance pandas numpy scikit-learn
)

echo.
echo [4/5] Starting ML Backend on port 8003...
echo.

:: Start ML Backend
start "ML Backend (Port 8003)" cmd /c "python backend_ml_enhanced.py"

echo    Waiting for ML Backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [5/5] Testing ML Backend connection...
echo.

:: Test the health endpoint
curl -s http://localhost:8003/health >test_ml.tmp 2>nul
if %errorlevel% == 0 (
    echo.
    echo    ✓ ML Backend is responding!
    echo.
    echo    Response from /health endpoint:
    type test_ml.tmp
    del test_ml.tmp >nul 2>&1
    echo.
    echo ================================================================================
    echo                    ✓ ML BACKEND FIXED AND RUNNING!
    echo ================================================================================
    echo.
    echo The ML Training Centre should now show "Connected" in green.
    echo.
    echo If you still see "Disconnected":
    echo   1. Refresh the browser page (F5)
    echo   2. Clear browser cache (Ctrl+Shift+Delete)
    echo   3. Check Windows Firewall isn't blocking port 8003
    echo.
) else (
    echo.
    echo    ✗ ML Backend is not responding yet
    echo.
    echo Possible issues:
    echo   1. Python packages not installed correctly
    echo   2. Port 8003 is blocked by firewall
    echo   3. Another program is using port 8003
    echo.
    echo Checking for Python errors...
    echo.
    
    :: Try to run the backend directly to see errors
    echo Running ML Backend in debug mode (press Ctrl+C to stop)...
    python backend_ml_enhanced.py
)

pause