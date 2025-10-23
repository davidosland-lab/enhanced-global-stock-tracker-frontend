@echo off
echo ============================================
echo Restarting Backend with Health Endpoint Fix
echo ============================================
echo.

echo Stopping existing backend process on port 8002...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do (
    taskkill /PID %%a /F 2>nul
)
timeout /t 2

echo Starting backend with health endpoint fix...
cd /D "%~dp0"
start "Backend API (Port 8002)" /min cmd /k python backend.py

timeout /t 3

echo Testing health endpoint...
curl -s http://localhost:8002/api/health || echo Failed to connect

echo.
echo Backend has been restarted with the health endpoint fix.
echo The "Backend Status: Disconnected" issue should now be resolved.
echo.
echo Press any key to close this window...
pause >nul