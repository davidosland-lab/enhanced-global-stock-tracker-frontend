@echo off
title Stock Tracker - Quick Start
color 0A

echo ================================================================================
echo                      STOCK TRACKER - QUICK START
echo                         Windows 11 Edition
echo ================================================================================
echo.

:: Clean up any existing processes
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

:: Start all services
echo.
echo Starting services...
echo   [1/3] Frontend Server (port 8000)...
start "Frontend" /min cmd /c "cd /d %~dp0 && python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo   [2/3] Main Backend (port 8002)...
start "Backend" /min cmd /c "cd /d %~dp0 && python backend.py"
timeout /t 3 /nobreak >nul

echo   [3/3] ML Backend (port 8003)...
start "ML Backend" /min cmd /c "cd /d %~dp0 && python backend_ml_enhanced.py"
timeout /t 3 /nobreak >nul

:: Open browser
echo.
echo ================================================================================
echo ✓ All services started successfully!
echo ================================================================================
echo.
echo Opening Stock Tracker in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo Stock Tracker is running!
echo.
echo To stop all services, close this window and run StockTracker.bat
echo.
pause