@echo off
title Stock Tracker - Stopping Services
color 0C

echo ================================================
echo    STOPPING ALL STOCK TRACKER SERVICES
echo ================================================
echo.

echo Stopping services on ports 8000-8006...

:: Kill Python processes on specific ports
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Stopping service on port 8000 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Stopping service on port 8002 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do (
    echo Stopping service on port 8003 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do (
    echo Stopping service on port 8004 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do (
    echo Stopping service on port 8005 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do (
    echo Stopping service on port 8006 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo All services stopped.
echo.
pause