@echo off
echo ========================================
echo Stock Tracker ML Services Startup Script
echo Version 6.0 - ML Integration Enhanced
echo ========================================
echo.

echo Starting services in correct order...
echo.

REM Navigate to application directory
cd /d "%~dp0"

echo [1/4] Starting Main Backend (Port 8002)...
start "Main Backend" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

echo [2/4] Starting ML Backend (Port 8003)...
start "ML Backend" cmd /k "python ml_backend_enhanced.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Integration Bridge (Port 8004)...
start "Integration Bridge" cmd /k "python integration_bridge.py"
timeout /t 3 /nobreak >nul

echo [4/4] Starting Historical Data Service...
start "Historical Service" cmd /k "python historical_data_service.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Service Status:
echo - Main Backend:       http://localhost:8002
echo - ML Backend:         http://localhost:8003
echo - Integration Bridge: http://localhost:8004
echo - Dashboard:          Open index.html in browser
echo.
echo IMPORTANT: Keep all command windows open!
echo.
pause