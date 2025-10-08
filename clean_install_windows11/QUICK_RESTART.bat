@echo off
echo ==========================================
echo Stock Tracker - Quick Service Restart
echo ==========================================
echo.

:: Kill existing processes on our ports
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1

:: Wait a moment for ports to be released
echo Waiting for ports to be released...
timeout /t 3 /nobreak >nul

:: Start Frontend Server
echo Starting Frontend Server on port 8000...
start /min cmd /c "cd /d %~dp0 && python -m http.server 8000"

:: Start Main Backend
echo Starting Main Backend on port 8002...
start /min cmd /c "cd /d %~dp0 && python backend.py"

:: Start ML Backend (use ml_backend_v2.py for stable version)
echo Starting ML Backend on port 8003...
start /min cmd /c "cd /d %~dp0 && python ml_backend_v2.py"

:: Wait for services to start
echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak

:: Check service status
echo.
echo ==========================================
echo Checking Service Status...
echo ==========================================

curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo [FAILED] Frontend Server
) else (
    echo [OK] Frontend Server - http://localhost:8000
)

curl -s http://localhost:8002/health >nul 2>&1
if errorlevel 1 (
    echo [FAILED] Main Backend
) else (
    echo [OK] Main Backend - http://localhost:8002
)

curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo [FAILED] ML Backend
) else (
    echo [OK] ML Backend - http://localhost:8003
)

echo.
echo ==========================================
echo Services restarted successfully!
echo ==========================================
echo.
echo Access the application at: http://localhost:8000
echo.
echo Press any key to exit...
pause >nul