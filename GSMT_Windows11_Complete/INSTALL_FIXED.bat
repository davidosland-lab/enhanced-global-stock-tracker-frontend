@echo off
setlocal enabledelayedexpansion

:: =========================================
:: GSMT Enhanced Stock Tracker
:: Windows 11 Complete Installation Package
:: Version 3.1 - Python Compatibility Fixed
:: =========================================

color 0A
cls

echo.
echo  ============================================================
echo   GSMT ENHANCED STOCK TRACKER - WINDOWS 11 INSTALLER
echo   Version 3.1 with Python Compatibility Fix
echo  ============================================================
echo.
echo  This installer will:
echo   1. Check Python installation and compatibility
echo   2. Create virtual environment
echo   3. Install compatible dependencies
echo   4. Configure the application
echo   5. Create desktop shortcuts
echo   6. Start the application
echo.
echo  ============================================================
echo.
pause

:: Set installation directory
set "INSTALL_DIR=%cd%"
echo  Installation Directory: %INSTALL_DIR%
echo.

:: Step 1: Check Python Installation and Version
echo  [STEP 1/6] Checking Python installation...
echo  ------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH
    echo.
    echo  Please install Python 3.8-3.12 from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: 
    echo  - Install Python 3.12 or earlier (3.13 has compatibility issues)
    echo  - Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo  [OK] Python !PYTHON_VERSION! detected
    
    :: Check if Python 3.13 (has numpy compatibility issues)
    echo !PYTHON_VERSION! | findstr /C:"3.13" >nul
    if !errorlevel! equ 0 (
        echo.
        echo  [WARNING] Python 3.13 detected - has compatibility issues with numpy
        echo  Recommended: Install Python 3.12 or 3.11 for best compatibility
        echo.
        echo  Attempting workaround installation...
        set "USE_COMPAT_MODE=1"
    ) else (
        set "USE_COMPAT_MODE=0"
    )
)

:: Step 2: Create Virtual Environment
echo.
echo  [STEP 2/6] Creating virtual environment...
echo  ------------------------------------------
if exist venv (
    echo  Removing old virtual environment...
    rmdir /s /q venv
)

:: Create venv without pip to avoid issues
python -m venv venv --without-pip
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create virtual environment
    echo  Trying alternative method...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  [ERROR] Cannot create virtual environment
        pause
        exit /b 1
    )
)
echo  [OK] Virtual environment created

:: Step 3: Activate and setup pip
echo.
echo  [STEP 3/6] Setting up pip in virtual environment...
echo  ------------------------------------------
call venv\Scripts\activate.bat

:: Ensure pip is installed in venv
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo  [OK] Pip configured

:: Step 4: Install Compatible Packages
echo.
echo  [STEP 4/6] Installing compatible packages...
echo  ------------------------------------------
echo  This may take a few minutes...
echo.

if "!USE_COMPAT_MODE!"=="1" (
    echo  Using compatibility mode for Python 3.13...
    
    :: Install with compatible numpy version
    echo  Installing numpy (compatible version)...
    pip install --no-cache-dir "numpy>=1.26.0" >nul 2>&1
    if %errorlevel% neq 0 (
        echo    Trying alternative numpy installation...
        pip install --no-cache-dir numpy --pre >nul 2>&1
    )
    
    echo  Installing core dependencies...
    pip install --no-cache-dir fastapi uvicorn[standard] >nul 2>&1
    
    echo  Installing data libraries...
    pip install --no-cache-dir pandas yfinance >nul 2>&1
    
    echo  Installing ML libraries...
    pip install --no-cache-dir scikit-learn >nul 2>&1
    
    echo  Installing utilities...
    pip install --no-cache-dir aiofiles python-multipart >nul 2>&1
    
) else (
    echo  Using standard installation...
    
    :: Install specific versions for better compatibility
    echo  Installing numpy...
    pip install --no-cache-dir "numpy>=1.24,<1.27" >nul 2>&1
    if %errorlevel% neq 0 (
        pip install --no-cache-dir numpy >nul 2>&1
    )
    
    echo  Installing core dependencies...
    pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0 >nul 2>&1
    if %errorlevel% neq 0 (
        pip install --no-cache-dir fastapi uvicorn[standard] >nul 2>&1
    )
    
    echo  Installing data libraries...
    pip install --no-cache-dir yfinance==0.2.33 pandas==2.1.3 >nul 2>&1
    if %errorlevel% neq 0 (
        pip install --no-cache-dir yfinance pandas >nul 2>&1
    )
    
    echo  Installing ML libraries...
    pip install --no-cache-dir scikit-learn==1.3.2 >nul 2>&1
    if %errorlevel% neq 0 (
        pip install --no-cache-dir scikit-learn >nul 2>&1
    )
    
    echo  Installing utilities...
    pip install --no-cache-dir aiofiles==23.2.1 python-multipart==0.0.6 >nul 2>&1
    if %errorlevel% neq 0 (
        pip install --no-cache-dir aiofiles python-multipart >nul 2>&1
    )
)

echo  [OK] Packages installed

:: Step 5: Create Scripts and Shortcuts
echo.
echo  [STEP 5/6] Creating scripts and shortcuts...
echo  ------------------------------------------

:: Create START_SERVER.bat
echo @echo off > START_SERVER.bat
echo title GSMT Stock Tracker Server >> START_SERVER.bat
echo cd /d "%INSTALL_DIR%" >> START_SERVER.bat
echo call venv\Scripts\activate.bat >> START_SERVER.bat
echo cls >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo ============================================================ >> START_SERVER.bat
echo echo  GSMT Enhanced Stock Tracker - Server Starting >> START_SERVER.bat
echo echo ============================================================ >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo Server URL: http://localhost:8000 >> START_SERVER.bat
echo echo API Docs: http://localhost:8000/docs >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo Press Ctrl+C to stop the server >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo python backend\enhanced_ml_backend.py >> START_SERVER.bat
echo pause >> START_SERVER.bat

:: Create OPEN_DASHBOARD.bat
echo @echo off > OPEN_DASHBOARD.bat
echo echo Opening GSMT Dashboard... >> OPEN_DASHBOARD.bat
echo timeout /t 2 /nobreak ^>nul >> OPEN_DASHBOARD.bat
echo start http://localhost:8000 >> OPEN_DASHBOARD.bat

:: Create STOP_SERVER.bat
echo @echo off > STOP_SERVER.bat
echo echo Stopping all Python processes... >> STOP_SERVER.bat
echo taskkill /F /IM python.exe 2^>nul >> STOP_SERVER.bat
echo echo Server stopped. >> STOP_SERVER.bat
echo timeout /t 2 /nobreak ^>nul >> STOP_SERVER.bat

:: Create RUN_APP.bat (Combined launcher)
echo @echo off > RUN_APP.bat
echo title GSMT Launcher >> RUN_APP.bat
echo echo Starting GSMT Stock Tracker... >> RUN_APP.bat
echo start /min START_SERVER.bat >> RUN_APP.bat
echo timeout /t 5 /nobreak ^>nul >> RUN_APP.bat
echo start http://localhost:8000 >> RUN_APP.bat
echo exit >> RUN_APP.bat

echo  [OK] Scripts created

:: Create Desktop Shortcut
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    echo Creating desktop shortcut...
    
    echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
    echo sLinkFile = "%DESKTOP%\GSMT Stock Tracker.lnk" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
    echo oLink.TargetPath = "%INSTALL_DIR%\RUN_APP.bat" >> CreateShortcut.vbs
    echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
    echo oLink.Description = "GSMT Enhanced Stock Tracker" >> CreateShortcut.vbs
    echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll, 13" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    
    cscript CreateShortcut.vbs >nul 2>&1
    del CreateShortcut.vbs
    
    echo  [OK] Desktop shortcut created
)

:: Step 6: Verify Installation
echo.
echo  [STEP 6/6] Verifying installation...
echo  ------------------------------------------

:: Test imports
python -c "import fastapi; print('  [OK] FastAPI installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] FastAPI import failed

python -c "import uvicorn; print('  [OK] Uvicorn installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] Uvicorn import failed

python -c "import yfinance; print('  [OK] yfinance installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] yfinance import failed

python -c "import pandas; print('  [OK] pandas installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] pandas import failed

python -c "import numpy; print('  [OK] numpy installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] numpy import failed

python -c "import sklearn; print('  [OK] scikit-learn installed')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] scikit-learn import failed

:: Installation Complete
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  Quick Start Options:
echo.
echo  1. DESKTOP SHORTCUT:
echo     - Use "GSMT Stock Tracker" on your desktop
echo.
echo  2. BATCH FILES:
echo     - Double-click "RUN_APP.bat" to start everything
echo     - Or use "START_SERVER.bat" then "OPEN_DASHBOARD.bat"
echo.
echo  3. MANUAL:
echo     - Run: venv\Scripts\activate.bat
echo     - Run: python backend\enhanced_ml_backend.py
echo     - Open: http://localhost:8000
echo.
echo  ============================================================
echo.
echo  Would you like to start the application now? (Y/N)
set /p START_NOW=

if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting GSMT Stock Tracker...
    start /min START_SERVER.bat
    echo Waiting for server to initialize...
    timeout /t 5 /nobreak >nul
    echo Opening dashboard in browser...
    start http://localhost:8000
    echo.
    echo  ============================================================
    echo   Application Started!
    echo   Dashboard: http://localhost:8000
    echo   To stop: Run STOP_SERVER.bat or press Ctrl+C in server window
    echo  ============================================================
)

echo.
pause
exit /b 0