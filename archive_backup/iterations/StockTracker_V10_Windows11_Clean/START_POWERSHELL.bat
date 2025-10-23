@echo off
echo ========================================
echo Starting StockTracker with PowerShell
echo ========================================
echo.

REM Check if PowerShell execution policy allows scripts
powershell -Command "Get-ExecutionPolicy" | findstr "Restricted" >nul
if %errorlevel% equ 0 (
    echo Setting PowerShell execution policy...
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
)

REM Run the PowerShell startup script
powershell -ExecutionPolicy Bypass -File START_POWERSHELL.ps1

pause