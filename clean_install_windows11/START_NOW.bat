@echo off
REM ============================================================
REM ONE-CLICK START - Stock Tracker Windows 11
REM Double-click this file to start everything!
REM ============================================================

echo Starting Stock Tracker Suite...
echo.

REM Run the comprehensive fix and start script
call FIX_AND_START.bat

REM If that fails, try PowerShell version
if errorlevel 1 (
    echo.
    echo Trying PowerShell version...
    powershell -ExecutionPolicy Bypass -File FIX_AND_START.ps1
)