@echo off
cls
color 0E
title GSMT - Clean Installation

echo ============================================================
echo     GLOBAL STOCK MARKET TRACKER (GSMT)
echo     Clean Installation Script v7.0
echo ============================================================
echo.
echo This will install GSMT with:
echo - Real-time Yahoo Finance data ONLY
echo - Market hours display (shows markets only when open)
echo - Automatic browser launching
echo - All required dependencies
echo.
echo Press any key to begin installation...
pause >nul

echo.
echo [Step 1/5] Checking system requirements...
echo ----------------------------------------

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.8 or higher:
    echo 1. Visit https://python.org/downloads
    echo 2. Download Python 3.8+ for Windows
    echo 3. During installation, CHECK "Add Python to PATH"
    echo 4. Run this installer again after Python installation
    echo.
    pause
    exit /b 1
)
echo ✓ Python installed

REM Check pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found, installing...
    python -m ensurepip --upgrade
)
echo ✓ pip available

echo.
echo [Step 2/5] Creating directory structure...
echo ----------------------------------------

REM Ensure we're in the right directory
set INSTALL_DIR=%~dp0
cd /d "%INSTALL_DIR%"

REM Create required directories
if not exist "backend" mkdir backend
if not exist "frontend" mkdir frontend
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo ✓ Directory structure created

echo.
echo [Step 3/5] Installing Python dependencies...
echo ----------------------------------------

echo Updating pip...
python -m pip install --upgrade pip --quiet

echo Installing core packages...
python -m pip install fastapi uvicorn yfinance --quiet
if errorlevel 1 (
    echo ⚠ Some packages failed, retrying...
    python -m pip install fastapi uvicorn yfinance
)

echo Installing additional packages...
python -m pip install pandas numpy python-multipart requests --quiet

echo ✓ Dependencies installed

echo.
echo [Step 4/5] Configuring GSMT...
echo ----------------------------------------

REM Create default config
echo {"api_port": 8000, "auto_refresh": 60, "default_markets": ["^AXJO", "^FTSE", "^GSPC"]} > config\settings.json

echo ✓ Configuration complete

echo.
echo [Step 5/5] Creating desktop shortcut...
echo ----------------------------------------

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
if exist "%DESKTOP%" (
    echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
    echo sLinkFile = "%DESKTOP%\GSMT.lnk" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
    echo oLink.TargetPath = "%INSTALL_DIR%LAUNCH_GSMT.cmd" >> CreateShortcut.vbs
    echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
    echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll, 13" >> CreateShortcut.vbs
    echo oLink.Description = "Global Stock Market Tracker" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    cscript //nologo CreateShortcut.vbs
    del CreateShortcut.vbs
    echo ✓ Desktop shortcut created
) else (
    echo ⚠ Could not create desktop shortcut
)

echo.
echo ============================================================
echo     INSTALLATION COMPLETE!
echo ============================================================
echo.
echo To start GSMT:
echo.
echo   Option 1: Double-click "LAUNCH_GSMT.cmd"
echo   Option 2: Use the desktop shortcut (if created)
echo.
echo The tracker will:
echo - Start the backend server automatically
echo - Open in your default web browser
echo - Display real Yahoo Finance data
echo - Show markets only during trading hours
echo.
echo Press any key to launch GSMT now...
pause >nul

echo.
echo Launching GSMT...
call LAUNCH_GSMT.cmd