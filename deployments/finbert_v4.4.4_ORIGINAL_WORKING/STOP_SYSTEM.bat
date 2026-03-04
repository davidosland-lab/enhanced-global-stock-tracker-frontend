@echo off
title Stop FinBERT System
color 0E
cls

echo ================================================================================
echo                    STOPPING FINBERT TRADING SYSTEM                            
echo ================================================================================
echo.

echo Stopping all FinBERT processes...

REM Kill Python processes on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    echo Stopping process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill any FinBERT backend windows
taskkill /F /FI "WindowTitle eq FinBERT Backend*" >nul 2>&1
taskkill /F /FI "WindowTitle eq FinBERT*" >nul 2>&1

REM Kill specific Python scripts
wmic process where "CommandLine like '%%app_finbert%%'" delete >nul 2>&1

echo.
echo All FinBERT processes have been stopped.
echo.
pause