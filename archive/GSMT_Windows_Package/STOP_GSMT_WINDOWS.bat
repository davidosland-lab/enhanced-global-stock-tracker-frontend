@echo off
REM ============================================
REM Stop Global Stock Market Tracker Services
REM ============================================

echo.
echo Stopping Global Stock Market Tracker services...

REM Kill Python processes on port 8002 (backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Stopping backend process (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Python processes on port 8080 (frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    echo Stopping frontend process (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill any named windows
taskkill /F /FI "WINDOWTITLE eq GSMT Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq GSMT Frontend*" >nul 2>&1

echo.
echo All GSMT services have been stopped.
echo.
pause