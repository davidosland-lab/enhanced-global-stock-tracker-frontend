@echo off
title Stock Market Dashboard - Quick Start
color 0A

echo ============================================
echo    STOCK MARKET DASHBOARD - QUICK START
echo ============================================
echo.

echo [1] Starting Backend Server...
echo ============================================
start /min cmd /k "title Yahoo Finance Backend && python backend.py"

echo [2] Waiting for server to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [3] Opening Dashboard in Browser...
echo ============================================
start http://localhost:8002

echo.
echo ============================================
echo    DASHBOARD LAUNCHED SUCCESSFULLY!
echo ============================================
echo.
echo Backend server is running in background
echo Browser should open automatically
echo.
echo If browser didn't open, navigate to:
echo http://localhost:8002
echo.
echo Press any key to view status...
pause > nul

start verify_setup.html