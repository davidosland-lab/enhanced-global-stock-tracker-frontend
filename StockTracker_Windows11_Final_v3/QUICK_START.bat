@echo off
cls
echo ================================================================================
echo     STOCK TRACKER V3 - QUICK START
echo ================================================================================
echo.
echo This will:
echo   1. Install all dependencies
echo   2. Start all services
echo   3. Open the application
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/2] Running installation...
call INSTALL_ALL.bat

echo.
echo [2/2] Starting services...
call START_SYSTEM.bat