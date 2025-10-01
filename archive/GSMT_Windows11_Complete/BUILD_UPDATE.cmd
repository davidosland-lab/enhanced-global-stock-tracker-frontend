@echo off
cls
color 0E
title GSMT - Build Update Package

echo ==========================================
echo  GSMT Update Package Builder
echo  Creating Indices Tracker v2.0 Update
echo ==========================================
echo.

echo This will create a distributable update package
echo for the enhanced Global Indices Tracker.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Building update package...
echo.

REM Run the PowerShell script to create the package
powershell -ExecutionPolicy Bypass -File "CREATE_UPDATE_PACKAGE.ps1"

echo.
echo Process complete!
echo.
pause