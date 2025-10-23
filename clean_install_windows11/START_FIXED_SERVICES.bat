@echo off
cls
echo ============================================================
echo Stock Tracker - Starting All Services (FIXED VERSION)
echo ============================================================
echo.

REM Kill any existing Python processes to ensure clean start
echo Cleaning up any existing processes...
taskkill /F /IM python.exe 2>NUL
timeout /t 2 /nobreak >NUL

REM Start Backend API (Port 8002) - Using the fixed backend
echo [1/3] Starting Backend API on port 8002...
if exist backend.py (
    start "Backend API" cmd /k "python backend.py"
) else if exist backend_working_before_ml_fix.py (
    copy backend_working_before_ml_fix.py backend.py /Y
    start "Backend API" cmd /k "python backend.py"
) else (
    echo ERROR: No backend.py found!
)
timeout /t 3 /nobreak >NUL

REM Start ML Backend (Port 8003) - Using the fixed ML backend
echo [2/3] Starting ML Backend on port 8003...
if exist ml_backend_fixed.py (
    start "ML Backend" cmd /k "python ml_backend_fixed.py"
) else if exist ml_backend_v2.py (
    start "ML Backend" cmd /k "python ml_backend_v2.py"
) else if exist ml_backend_minimal.py (
    start "ML Backend" cmd /k "python ml_backend_minimal.py"
) else (
    echo WARNING: No ML backend found!
)
timeout /t 3 /nobreak >NUL

REM Start Frontend Server (Port 8000)
echo [3/3] Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >NUL

echo.
echo ============================================================
echo All Services Started Successfully!
echo ============================================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Service Status:
echo   - Frontend:    http://localhost:8000
echo   - Backend API: http://localhost:8002
echo   - ML Backend:  http://localhost:8003
echo.
echo To stop all services:
echo   Run STOP_ALL_SERVICES.bat or close all command windows
echo.
pause