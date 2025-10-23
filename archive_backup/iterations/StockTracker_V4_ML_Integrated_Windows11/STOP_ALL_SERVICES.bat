@echo off
title Stock Tracker v4.0 - Stop Services
color 0C
cls

echo =====================================================
echo    Stock Tracker v4.0 - Stopping All Services
echo =====================================================
echo.

echo Stopping Python services...
echo.

:: Kill Python processes running our services
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *backend*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *ml_backend*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *integration_bridge*" >nul 2>&1

:: Alternative method - kill by port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /F /PID %%a >nul 2>&1

echo All services have been stopped.
echo.
pause