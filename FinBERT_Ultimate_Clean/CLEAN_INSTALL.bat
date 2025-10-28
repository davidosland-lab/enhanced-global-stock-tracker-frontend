@echo off
echo ================================================================
echo    CLEAN INSTALLATION - REMOVES OLD INSTALLATIONS
echo ================================================================
echo.
echo This will remove any existing virtual environments and caches
echo to ensure a completely clean installation.
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Cleaning up old installations...

REM Remove old virtual environments
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv 2>nul
)

if exist .venv (
    echo Removing .venv...
    rmdir /s /q .venv 2>nul
)

REM Remove cache directories
if exist __pycache__ (
    echo Removing Python cache...
    rmdir /s /q __pycache__ 2>nul
)

if exist .pytest_cache (
    echo Removing pytest cache...
    rmdir /s /q .pytest_cache 2>nul
)

REM Remove any .env files that might cause issues
if exist .env (
    echo Removing .env file...
    del .env 2>nul
)

if exist .env.local (
    del .env.local 2>nul
)

REM Remove old model files
if exist models (
    echo Clearing old models...
    del /q models\*.pkl 2>nul
)

REM Remove old log files
if exist logs (
    echo Clearing old logs...
    del /q logs\*.log 2>nul
)

echo.
echo ================================================================
echo Clean-up complete!
echo.
echo Now running fresh installation...
echo ================================================================
echo.

REM Run the installer
call INSTALL_ULTIMATE.bat