@echo off
REM Dashboard Installation Script - Fixed Version
REM No progress files, direct installation

setlocal enabledelayedexpansion

echo ================================================================
echo        DASHBOARD INSTALLATION - FIXED VERSION
echo ================================================================
echo.

REM Detect target directory
set "TARGET_DIR="
if exist "..\..\finbert_v4.4.4" (
    set "TARGET_DIR=..\..\finbert_v4.4.4"
    echo [OK] Found finbert_v4.4.4 directory (2 levels up^)
) else if exist "..\finbert_v4.4.4" (
    set "TARGET_DIR=..\finbert_v4.4.4"
    echo [OK] Found finbert_v4.4.4 directory (1 level up^)
) else if exist "finbert_v4.4.4" (
    set "TARGET_DIR=finbert_v4.4.4"
    echo [OK] Found finbert_v4.4.4 directory (current level^)
) else (
    echo [ERROR] Cannot find finbert_v4.4.4 directory
    echo Please run this script from within the deployment package
    pause
    exit /b 1
)

echo.
echo Target Installation Directory: %TARGET_DIR%
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    echo [OK] Python !PYTHON_VERSION! found
) else (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
%PYTHON_CMD% -m pip install --quiet flask flask-cors pandas numpy >nul 2>&1
echo [OK] Dependencies installed

REM Create directories
echo.
echo Creating directories...
if not exist "%TARGET_DIR%\templates" mkdir "%TARGET_DIR%\templates"
if not exist "%TARGET_DIR%\static\css" mkdir "%TARGET_DIR%\static\css"
if not exist "%TARGET_DIR%\static\js" mkdir "%TARGET_DIR%\static\js"
if not exist "%TARGET_DIR%\logs" mkdir "%TARGET_DIR%\logs"
if not exist "%TARGET_DIR%\config" mkdir "%TARGET_DIR%\config"
echo [OK] Directories created

REM Copy files
echo.
echo Copying dashboard files...
copy /Y "live_trading_dashboard.py" "%TARGET_DIR%\" >nul 2>&1
echo   - live_trading_dashboard.py: copied
copy /Y "live_trading_with_dashboard.py" "%TARGET_DIR%\" >nul 2>&1
echo   - live_trading_with_dashboard.py: copied
copy /Y "templates\dashboard.html" "%TARGET_DIR%\templates\" >nul 2>&1
echo   - dashboard.html: copied
copy /Y "static\css\dashboard.css" "%TARGET_DIR%\static\css\" >nul 2>&1
echo   - dashboard.css: copied
copy /Y "static\js\dashboard.js" "%TARGET_DIR%\static\js\" >nul 2>&1
echo   - dashboard.js: copied
echo [OK] All files copied

REM Quick validation
echo.
echo Validating installation...
set "VALID=1"

if not exist "%TARGET_DIR%\live_trading_dashboard.py" (
    echo [ERROR] Missing: live_trading_dashboard.py
    set "VALID=0"
)

if not exist "%TARGET_DIR%\templates\dashboard.html" (
    echo [ERROR] Missing: templates\dashboard.html
    set "VALID=0"
)

if not exist "%TARGET_DIR%\static\css\dashboard.css" (
    echo [ERROR] Missing: static\css\dashboard.css
    set "VALID=0"
)

if not exist "%TARGET_DIR%\static\js\dashboard.js" (
    echo [ERROR] Missing: static\js\dashboard.js
    set "VALID=0"
)

if %VALID% equ 1 (
    echo [OK] All files validated
) else (
    echo [WARN] Some files missing - please check manually
)

REM Success
echo.
echo ================================================================
echo                 INSTALLATION COMPLETE!
echo ================================================================
echo.
echo Installation Location: %TARGET_DIR%
echo.
echo Quick Start:
echo    cd %TARGET_DIR%
echo    %PYTHON_CMD% live_trading_dashboard.py
echo.
echo Then visit: http://localhost:5000
echo.
echo Documentation:
echo    - DASHBOARD_SETUP_GUIDE.md
echo    - SYSTEM_ARCHITECTURE.md
echo    - DASHBOARD_COMPLETE_SUMMARY.md
echo.
pause
