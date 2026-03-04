@echo off
REM v1.3.11 Calibration Patch Installer
REM Date: January 2, 2026

echo ========================================
echo  v1.3.11 Calibration Patch Installer
echo ========================================
echo.
echo This will install the calibration fix to your
echo existing Phase 3 Trading System installation.
echo.
echo IMPORTANT: Dashboard will be stopped during installation.
echo.
pause

REM Prompt for installation directory
set "DEFAULT_DIR=C:\Users\%USERNAME%\Trading\phase3_trading_system_v1.3.10"
echo.
echo Enter your installation directory:
echo (Press Enter to use default: %DEFAULT_DIR%)
echo.
set /p INSTALL_DIR="Installation directory: "

REM Use default if no input
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%DEFAULT_DIR%"

REM Verify directory exists
if not exist "%INSTALL_DIR%\phase3_intraday_deployment" (
    echo.
    echo ERROR: Installation directory not found!
    echo Checked: %INSTALL_DIR%\phase3_intraday_deployment
    echo.
    echo Please verify your installation path and try again.
    pause
    exit /b 1
)

echo.
echo Installation directory: %INSTALL_DIR%
echo.

REM Stop any running dashboard
echo Step 1: Stopping dashboard...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *unified_trading_dashboard*" 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM Create backup
echo Step 2: Creating backup...
set "BACKUP_FILE=%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py.v1.3.10.backup"
copy /Y "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" "%BACKUP_FILE%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backup created: unified_trading_dashboard.py.v1.3.10.backup
) else (
    echo WARNING: Could not create backup! (Error: %ERRORLEVEL%)
    echo Continue anyway? (Y/N)
    choice /c YN /n
    if errorlevel 2 exit /b 1
)
echo.

REM Copy updated file
echo Step 3: Installing patch...
if not exist "%~dp0phase3_intraday_deployment\unified_trading_dashboard.py" (
    echo ERROR: Patch file not found!
    echo Expected: %~dp0phase3_intraday_deployment\unified_trading_dashboard.py
    pause
    exit /b 1
)
copy /Y "%~dp0phase3_intraday_deployment\unified_trading_dashboard.py" "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Patch installed successfully!
) else (
    echo ERROR: Failed to copy patch file! (Error: %ERRORLEVEL%)
    echo.
    echo Restoring backup...
    copy /Y "%BACKUP_FILE%" "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" >nul 2>&1
    echo Backup restored.
    pause
    exit /b 1
)
echo.

REM Verify installation
echo Step 4: Verifying installation...
if exist "%INSTALL_DIR%\phase3_intraday_deployment\unified_trading_dashboard.py" (
    echo File verified: unified_trading_dashboard.py
    echo.
    echo ========================================
    echo  Installation Complete!
    echo ========================================
    echo.
    echo v1.3.11 Calibration Patch installed successfully.
    echo.
    echo Next steps:
    echo 1. Read PATCH_INSTALLATION_GUIDE.md for details
    echo 2. Restart your dashboard
    echo 3. Verify charts show "Change from Prev Close"
    echo.
    echo Start dashboard now? (Y/N)
    choice /c YN /n
    
    if errorlevel 2 goto :skip_start
    if errorlevel 1 goto :start_dashboard
    
    :start_dashboard
    echo.
    echo Starting dashboard...
    cd /d "%INSTALL_DIR%\phase3_intraday_deployment"
    if exist "START_UNIFIED_DASHBOARD.bat" (
        start "" "START_UNIFIED_DASHBOARD.bat"
        timeout /t 2 /nobreak >nul
        echo Dashboard started!
        echo Open browser: http://localhost:8050
    ) else (
        echo START_UNIFIED_DASHBOARD.bat not found.
        echo Please start dashboard manually.
    )
    goto :end_install
    
    :skip_start
    echo.
    echo Installation complete. Start dashboard manually when ready.
    goto :end_install
) else (
    echo ERROR: Installation verification failed!
    pause
    exit /b 1
)

:end_install
echo.
echo Installation completed successfully.
echo.
pause
