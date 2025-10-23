@echo off
title Stock Tracker - Master Shutdown Controller
color 0C
cls

echo ===============================================================================
echo                    STOCK TRACKER MASTER SHUTDOWN
echo                 Graceful System Shutdown and Cleanup
echo ===============================================================================
echo.
echo This will stop all Stock Tracker services and free all ports.
echo.
echo Press CTRL+C to cancel, or
pause

echo.
echo [1] Stopping Frontend Server (Port 8000)...
echo -----------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo   Terminating process %%a on port 8000...
        taskkill /F /PID %%a >nul 2>&1
        echo   ✓ Frontend server stopped
    )
)

echo.
echo [2] Stopping Main Backend API (Port 8002)...
echo -----------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo   Terminating process %%a on port 8002...
        taskkill /F /PID %%a >nul 2>&1
        echo   ✓ Main backend stopped
    )
)

echo.
echo [3] Stopping ML Training Backend (Port 8003)...
echo -----------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo   Terminating process %%a on port 8003...
        taskkill /F /PID %%a >nul 2>&1
        echo   ✓ ML backend stopped
    )
)

echo.
echo [4] Cleaning up remaining Python processes...
echo -----------------------------------------------
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
echo   ✓ All Python processes terminated

echo.
echo [5] Final port verification...
echo -----------------------------------------------
netstat -aon | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ Warning: Port 8000 may still be in use
) else (
    echo   ✓ Port 8000 is free
)

netstat -aon | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ Warning: Port 8002 may still be in use
) else (
    echo   ✓ Port 8002 is free
)

netstat -aon | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ Warning: Port 8003 may still be in use
) else (
    echo   ✓ Port 8003 is free
)

echo.
echo ===============================================================================
echo                        SHUTDOWN COMPLETE
echo ===============================================================================
echo.
echo All Stock Tracker services have been stopped.
echo You can now safely restart the system using MASTER_STARTUP.bat
echo.
pause