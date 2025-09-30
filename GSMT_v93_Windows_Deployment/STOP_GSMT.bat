@echo off
title Stopping GSMT Services
color 0C

echo ============================================================
echo   Stopping Global Stock Market Tracker v9.3
echo ============================================================
echo.

echo Stopping Python processes...

:: Kill Python processes running our services
taskkill /F /FI "WINDOWTITLE eq GSMT Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq GSMT Frontend*" >nul 2>&1

:: Also try to kill by port if needed
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Services stopped successfully.
echo.
pause