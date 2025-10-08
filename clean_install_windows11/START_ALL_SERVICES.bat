@echo off
echo ========================================
echo Stock Tracker - Complete Service Startup
echo ========================================
echo.

echo Starting all required services...
echo.

REM Kill any existing Python processes to avoid port conflicts
echo Cleaning up any existing processes...
taskkill /F /IM python.exe 2>NUL
timeout /t 2 /nobreak >NUL

REM Start Backend API (Port 8002)
echo [1/3] Starting Backend API on port 8002...
start "Backend API" cmd /k "python backend.py"
timeout /t 3 /nobreak >NUL

REM Start ML Backend (Port 8003) 
echo [2/3] Starting ML Backend on port 8003...
start "ML Backend" cmd /k "python ml_backend_v2.py"
timeout /t 3 /nobreak >NUL

REM Start Frontend (Port 8000)
echo [3/3] Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >NUL

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Service Status:
echo   - Frontend:    http://localhost:8000
echo   - Backend API: http://localhost:8002
echo   - ML Backend:  http://localhost:8003
echo.
echo To stop all services, close all command windows
echo or press Ctrl+C in each window.
echo.
pause