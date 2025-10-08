@echo off
echo ==========================================
echo Stopping All Stock Tracker Services
echo ==========================================
echo.

:: Kill processes on our ports
echo Stopping Frontend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process PID %%a
)

echo Stopping Main Backend (port 8002)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process PID %%a
)

echo Stopping ML Backend (port 8003)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process PID %%a
)

echo.
echo ==========================================
echo All services stopped successfully!
echo ==========================================
echo.
pause