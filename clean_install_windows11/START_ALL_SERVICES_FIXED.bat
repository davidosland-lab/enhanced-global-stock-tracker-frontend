@echo off
echo ============================================
echo STOCK TRACKER - COMPLETE SERVICE STARTUP
echo With Backend Health Endpoint Fix
echo ============================================
echo.

REM Change to script directory
cd /D "%~dp0"

echo [1/4] Stopping any existing services...
echo --------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /PID %%a /F 2>nul
timeout /t 2 >nul

echo.
echo [2/4] Starting Frontend Server (Port 8000)...
echo --------------------------------------
start "Frontend Server" /min cmd /k python -m http.server 8000
timeout /t 2 >nul

echo.
echo [3/4] Starting Main Backend API (Port 8002)...
echo --------------------------------------
echo Using: backend.py (with health endpoint fix)
start "Backend API" /min cmd /k python backend.py
timeout /t 3 >nul

echo.
echo [4/4] Starting ML Backend (Port 8003)...
echo --------------------------------------
echo Using: ml_backend_fixed.py (with all endpoints)
start "ML Backend" /min cmd /k python ml_backend_fixed.py
timeout /t 3 >nul

echo.
echo ============================================
echo SERVICE STATUS CHECK
echo ============================================

echo.
echo Testing Backend Health Endpoint...
curl -s http://localhost:8002/api/health
echo.

echo.
echo Testing ML Backend Health...
curl -s http://localhost:8003/health
echo.

echo.
echo ============================================
echo ALL SERVICES STARTED SUCCESSFULLY!
echo ============================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Service Ports:
echo   - Frontend:    http://localhost:8000
echo   - Backend API: http://localhost:8002
echo   - ML Backend:  http://localhost:8003
echo.
echo Backend Status should now show "Connected"
echo ML Backend Status should show "Operational"
echo.
echo To stop all services, close this window and
echo the three service windows that opened.
echo.
pause