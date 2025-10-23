@echo off
REM =====================================================
REM Stock Tracker Shutdown - Stop All Services
REM =====================================================

echo Stopping all Stock Tracker services...

REM Kill processes on ports
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Stopping Frontend Server...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002" ^| find "LISTENING"') do (
    echo Stopping Backend API...
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003" ^| find "LISTENING"') do (
    echo Stopping ML Backend...
    taskkill /F /PID %%a >nul 2>&1
)

REM Also kill by process name
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Frontend Server*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend API*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq ML Backend*" >nul 2>&1

echo.
echo All services stopped.
pause
