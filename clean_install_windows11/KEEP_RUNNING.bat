@echo off
title Stock Tracker - Keep Running
cls
echo ================================================================
echo     STOCK TRACKER - AUTO-RESTART BACKEND
echo ================================================================
echo.
echo This script will keep your backend running even if it crashes.
echo.

:start
echo [%date% %time%] Starting backend...
python backend.py

echo.
echo ================================================================
echo Backend stopped! Restarting in 5 seconds...
echo Press Ctrl+C twice to stop auto-restart
echo ================================================================
timeout /t 5 >nul

goto start