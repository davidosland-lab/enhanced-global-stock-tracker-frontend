@echo off
title Stock Tracker - Shutdown
color 0C

echo ================================================================================
echo                      STOCK TRACKER - SHUTDOWN
echo ================================================================================
echo.
echo Stopping all Stock Tracker services...
echo.

:: Stop Frontend Server
echo [1/3] Stopping Frontend Server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul && echo    ✓ Frontend Server stopped
)

:: Stop Main Backend
echo [2/3] Stopping Main Backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul && echo    ✓ Main Backend stopped
)

:: Stop ML Backend
echo [3/3] Stopping ML Backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul && echo    ✓ ML Backend stopped
)

echo.
echo ================================================================================
echo ✓ All services have been stopped successfully!
echo ================================================================================
echo.
pause