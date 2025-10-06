@echo off
:: Stock Tracker Universal Launcher for Windows 11
:: This script automatically chooses the best startup method

echo ================================================================================
echo                      STOCK TRACKER - WINDOWS 11 LAUNCHER
echo ================================================================================
echo.

:: Check if PowerShell is available and execution policy allows scripts
powershell -Command "Get-ExecutionPolicy" >nul 2>&1
if %errorlevel% equ 0 (
    echo Launching with PowerShell (recommended for Windows 11)...
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0MASTER_STARTUP_WIN11.ps1"
) else (
    echo Launching with Command Prompt...
    echo.
    call "%~dp0MASTER_STARTUP_WIN11.bat"
)

exit /b %errorlevel%