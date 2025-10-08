@echo off
cls
echo ============================================================
echo Stopping All Stock Tracker Services
echo ============================================================
echo.

REM Kill all Python processes
echo Stopping all Python processes...
taskkill /F /IM python.exe 2>NUL

REM Kill processes on specific ports to be sure
echo.
echo Stopping services on specific ports...

REM Stop Frontend (port 8000)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Stopped process on port 8000 (PID %%a)
)

REM Stop Backend (port 8002)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Stopped process on port 8002 (PID %%a)
)

REM Stop ML Backend (port 8003)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Stopped process on port 8003 (PID %%a)
)

echo.
echo ============================================================
echo All Services Stopped
echo ============================================================
echo.
echo All Stock Tracker services have been terminated.
echo Ports 8000, 8002, and 8003 are now free.
echo.
pause