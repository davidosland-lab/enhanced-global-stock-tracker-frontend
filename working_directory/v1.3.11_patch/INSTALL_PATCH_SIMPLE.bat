@echo off
REM v1.3.11 Calibration Patch - Simple Manual Installer
REM Date: January 3, 2026
REM Use this if INSTALL_PATCH.bat hangs

echo ========================================
echo  v1.3.11 Simple Patch Installer
echo ========================================
echo.

REM Set your installation directory here
set "INSTALL_DIR=C:\Users\%USERNAME%\Trading\phase3_trading_system_v1.3.10"

echo Installation target: %INSTALL_DIR%
echo.

REM Check if directory exists
if not exist "%INSTALL_DIR%\phase3_intraday_deployment" (
    echo ERROR: Installation directory not found!
    echo.
    echo Please edit this batch file and set INSTALL_DIR to your installation path.
    echo Current path: %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

echo [1/5] Stopping dashboard...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

echo [2/5] Creating backup...
copy /Y "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py.backup" 2>nul
if exist "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py.backup" (
    echo Backup created successfully.
) else (
    echo WARNING: Backup may have failed. Continue anyway.
)
echo.

echo [3/5] Copying patch file...
if not exist "%~dp0phase3_intraday_deployment\unified_trading_dashboard.py" (
    echo ERROR: Patch file not found!
    echo Expected: %~dp0phase3_intraday_deployment\unified_trading_dashboard.py
    echo.
    pause
    exit /b 1
)

copy /Y "%~dp0phase3_intraday_deployment\unified_trading_dashboard.py" "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" 2>nul
echo Patch file copied.
echo.

echo [4/5] Verifying installation...
if exist "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" (
    echo File verified: unified_trading_dashboard.py
    echo.
) else (
    echo ERROR: Verification failed!
    pause
    exit /b 1
)

echo [5/5] Installation complete!
echo.
echo ========================================
echo  v1.3.11 Patch Installed Successfully
echo ========================================
echo.
echo Next steps:
echo 1. Navigate to: %INSTALL_DIR%\phase3_intraday_deployment
echo 2. Run: START_UNIFIED_DASHBOARD.bat
echo 3. Open browser: http://localhost:8050
echo 4. Verify hover tooltip shows "Change from Prev Close"
echo.
echo Backup saved as: unified_trading_dashboard.py.backup
echo.
pause
