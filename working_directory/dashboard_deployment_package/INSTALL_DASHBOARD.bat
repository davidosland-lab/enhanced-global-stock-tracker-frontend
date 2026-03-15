@echo off
REM Live Trading Dashboard Deployment Installer (Windows)
REM ======================================================
REM 
REM This script installs the complete Live Trading Dashboard system
REM with intraday monitoring integration on Windows.
REM
REM Usage:
REM   INSTALL_DASHBOARD.bat [installation_directory]
REM
REM Author: FinBERT Enhanced System
REM Date: December 21, 2024
REM Version: 2.0

setlocal enabledelayedexpansion

REM Colors are limited in Windows batch, using text markers instead
set "CHECK=[OK]"
set "CROSS=[ERROR]"
set "ARROW=->"

echo.
echo ================================================================
echo          LIVE TRADING DASHBOARD INSTALLER v2.0
echo          Swing Trading + Intraday Monitoring
echo ================================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PACKAGE_DIR=%SCRIPT_DIR%"

REM Default installation directory
set "INSTALL_DIR=."
if not "%~1"=="" set "INSTALL_DIR=%~1"

echo Installation Settings:
echo   Source: %PACKAGE_DIR%
echo   Target: %INSTALL_DIR%
echo.

REM Step 1: Check Python
echo %ARROW% Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %CROSS% Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %CHECK% Found Python %PYTHON_VERSION%

REM Step 2: Check pip
echo %ARROW% Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %CROSS% pip is not installed
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)
echo %CHECK% pip is installed

REM Step 3: Create backup
echo %ARROW% Creating backup of existing files...
set "BACKUP_DIR=dashboard_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

if exist "%INSTALL_DIR%\live_trading_dashboard.py" (
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    if exist "%INSTALL_DIR%\live_trading_dashboard.py" copy "%INSTALL_DIR%\live_trading_dashboard.py" "%BACKUP_DIR%\" >nul 2>&1
    if exist "%INSTALL_DIR%\live_trading_with_dashboard.py" copy "%INSTALL_DIR%\live_trading_with_dashboard.py" "%BACKUP_DIR%\" >nul 2>&1
    if exist "%INSTALL_DIR%\templates" xcopy /E /I /Q "%INSTALL_DIR%\templates" "%BACKUP_DIR%\templates" >nul 2>&1
    if exist "%INSTALL_DIR%\static" xcopy /E /I /Q "%INSTALL_DIR%\static" "%BACKUP_DIR%\static" >nul 2>&1
    echo %CHECK% Backup created: %BACKUP_DIR%
) else (
    echo %CHECK% No existing files to backup
)

REM Step 4: Install dependencies
echo %ARROW% Installing Python dependencies...
echo This may take a few minutes...
pip install flask flask-cors pandas numpy --quiet
if %errorlevel% neq 0 (
    echo %CROSS% Failed to install dependencies
    pause
    exit /b 1
)
echo %CHECK% Dependencies installed

REM Step 5: Create directory structure
echo %ARROW% Creating directory structure...
if not exist "%INSTALL_DIR%\templates" mkdir "%INSTALL_DIR%\templates"
if not exist "%INSTALL_DIR%\static\css" mkdir "%INSTALL_DIR%\static\css"
if not exist "%INSTALL_DIR%\static\js" mkdir "%INSTALL_DIR%\static\js"
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"
echo %CHECK% Directory structure created

REM Step 6: Copy dashboard files
echo %ARROW% Copying dashboard files...

if exist "%PACKAGE_DIR%\live_trading_dashboard.py" (
    copy /Y "%PACKAGE_DIR%\live_trading_dashboard.py" "%INSTALL_DIR%\" >nul
    echo %CHECK% Copied live_trading_dashboard.py
) else (
    echo %CROSS% Missing live_trading_dashboard.py in package
    pause
    exit /b 1
)

if exist "%PACKAGE_DIR%\live_trading_with_dashboard.py" (
    copy /Y "%PACKAGE_DIR%\live_trading_with_dashboard.py" "%INSTALL_DIR%\" >nul
    echo %CHECK% Copied live_trading_with_dashboard.py
)

if exist "%PACKAGE_DIR%\templates\dashboard.html" (
    copy /Y "%PACKAGE_DIR%\templates\dashboard.html" "%INSTALL_DIR%\templates\" >nul
    echo %CHECK% Copied dashboard.html
) else (
    echo %CROSS% Missing templates/dashboard.html in package
    pause
    exit /b 1
)

if exist "%PACKAGE_DIR%\static\css\dashboard.css" (
    copy /Y "%PACKAGE_DIR%\static\css\dashboard.css" "%INSTALL_DIR%\static\css\" >nul
    echo %CHECK% Copied dashboard.css
) else (
    echo %CROSS% Missing static/css/dashboard.css in package
    pause
    exit /b 1
)

if exist "%PACKAGE_DIR%\static\js\dashboard.js" (
    copy /Y "%PACKAGE_DIR%\static\js\dashboard.js" "%INSTALL_DIR%\static\js\" >nul
    echo %CHECK% Copied dashboard.js
) else (
    echo %CROSS% Missing static/js/dashboard.js in package
    pause
    exit /b 1
)

REM Copy documentation
echo %ARROW% Copying documentation...
if exist "%PACKAGE_DIR%\DASHBOARD_SETUP_GUIDE.md" (
    copy /Y "%PACKAGE_DIR%\DASHBOARD_SETUP_GUIDE.md" "%INSTALL_DIR%\" >nul
    echo %CHECK% Copied DASHBOARD_SETUP_GUIDE.md
)
if exist "%PACKAGE_DIR%\DASHBOARD_COMPLETE_SUMMARY.md" (
    copy /Y "%PACKAGE_DIR%\DASHBOARD_COMPLETE_SUMMARY.md" "%INSTALL_DIR%\" >nul
    echo %CHECK% Copied DASHBOARD_COMPLETE_SUMMARY.md
)
if exist "%PACKAGE_DIR%\SYSTEM_ARCHITECTURE.md" (
    copy /Y "%PACKAGE_DIR%\SYSTEM_ARCHITECTURE.md" "%INSTALL_DIR%\" >nul
    echo %CHECK% Copied SYSTEM_ARCHITECTURE.md
)

REM Step 7: Validate installation
echo %ARROW% Validating installation...

set "VALIDATION_FAILED=0"

if not exist "%INSTALL_DIR%\live_trading_dashboard.py" (
    echo %CROSS% Missing live_trading_dashboard.py
    set "VALIDATION_FAILED=1"
)
if not exist "%INSTALL_DIR%\templates\dashboard.html" (
    echo %CROSS% Missing templates/dashboard.html
    set "VALIDATION_FAILED=1"
)
if not exist "%INSTALL_DIR%\static\css\dashboard.css" (
    echo %CROSS% Missing static/css/dashboard.css
    set "VALIDATION_FAILED=1"
)
if not exist "%INSTALL_DIR%\static\js\dashboard.js" (
    echo %CROSS% Missing static/js/dashboard.js
    set "VALIDATION_FAILED=1"
)

if "!VALIDATION_FAILED!"=="0" (
    echo %CHECK% All required files present
) else (
    echo %CROSS% Validation failed
    pause
    exit /b 1
)

REM Test imports
echo %ARROW% Testing Flask import...
python -c "import flask; import flask_cors" 2>nul
if %errorlevel% equ 0 (
    echo %CHECK% Flask is properly installed
) else (
    echo [WARNING] Flask import test failed
)

REM Display summary
echo.
echo ================================================================
echo             INSTALLATION COMPLETE
echo ================================================================
echo.

echo Installed Components:
echo   %CHECK% Flask backend (live_trading_dashboard.py)
echo   %CHECK% Web UI (templates/dashboard.html)
echo   %CHECK% Styles (static/css/dashboard.css)
echo   %CHECK% JavaScript (static/js/dashboard.js)
echo   %CHECK% Integration example (live_trading_with_dashboard.py)
echo   %CHECK% Documentation files
echo.

echo Next Steps:
echo.
echo 1. Test Dashboard (Standalone):
echo    cd %INSTALL_DIR%
echo    python live_trading_dashboard.py
echo    Then visit: http://localhost:5000
echo.

echo 2. Test with Trading System:
echo    cd %INSTALL_DIR%
echo    python live_trading_with_dashboard.py --paper-trading
echo    Then visit: http://localhost:5000
echo.

echo 3. Production Deployment:
echo    pip install gunicorn
echo    gunicorn -w 4 -b 0.0.0.0:5000 live_trading_dashboard:app
echo.

echo 4. Read Documentation:
echo    type %INSTALL_DIR%\DASHBOARD_SETUP_GUIDE.md
echo.

if exist "%BACKUP_DIR%" (
    echo Backup Location: %BACKUP_DIR%
    echo.
)

echo Installation successful! Happy trading!
echo.

pause
exit /b 0
