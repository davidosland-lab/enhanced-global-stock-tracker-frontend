@echo off
title Stock Tracker - Quick Start
color 0A
cls
echo ============================================================
echo    Stock Tracker Complete - Quick Start
echo    Starting all services...
echo ============================================================
echo.

echo [1/4] Starting Frontend Server (Port 8000)...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo [2/4] Starting Main Backend (Port 8002)...
start /min cmd /c "python backend.py"
timeout /t 2 /nobreak >nul

echo [3/4] Starting ML Backend (Port 8003)...
start /min cmd /c "python ml_backend.py"
timeout /t 2 /nobreak >nul

echo [4/4] Starting Integration Bridge (Port 8004)...
start /min cmd /c "python integration_bridge.py"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo    All services started successfully!
echo ============================================================
echo.
echo Opening dashboard in browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo Services Running:
echo - Frontend:          http://localhost:8000
echo - Main Backend API:  http://localhost:8002
echo - ML Backend API:    http://localhost:8003
echo - Integration Bridge: http://localhost:8004
echo.
echo Integration Dashboard: http://localhost:8000/integration_dashboard.html
echo.
echo Press Ctrl+C in this window to stop all services
echo.
pause