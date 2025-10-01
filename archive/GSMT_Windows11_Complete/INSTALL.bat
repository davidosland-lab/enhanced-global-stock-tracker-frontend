@echo off
setlocal enabledelayedexpansion

:: =========================================
:: GSMT Enhanced Stock Tracker
:: Windows 11 Complete Installation Package
:: Version 3.0 - ML Enhanced Edition
:: =========================================

color 0A
cls

echo.
echo  ============================================================
echo   GSMT ENHANCED STOCK TRACKER - WINDOWS 11 INSTALLER
echo   Version 3.0 with Phase 3 ^& 4 ML Models
echo  ============================================================
echo.
echo  This installer will:
echo   1. Check Python installation
echo   2. Create virtual environment
echo   3. Install all dependencies
echo   4. Configure the application
echo   5. Create desktop shortcuts
echo   6. Start the application
echo.
echo  ============================================================
echo.
pause

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo  [WARNING] Not running as Administrator
    echo  Some features may require admin privileges
    echo.
    pause
)

:: Set installation directory
set "INSTALL_DIR=%cd%"
echo  Installation Directory: %INSTALL_DIR%
echo.

:: Step 1: Check Python Installation
echo  [STEP 1/6] Checking Python installation...
echo  ------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH
    echo.
    echo  Please install Python 3.8 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo  [OK] Python !PYTHON_VERSION! detected
)

:: Step 2: Create Virtual Environment
echo.
echo  [STEP 2/6] Creating virtual environment...
echo  ------------------------------------------
if exist venv (
    echo  Virtual environment already exists. Removing old environment...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo  [OK] Virtual environment created

:: Step 3: Activate Virtual Environment and Upgrade pip
echo.
echo  [STEP 3/6] Activating environment and upgrading pip...
echo  ------------------------------------------
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo  [OK] Environment activated and pip upgraded

:: Step 4: Install Required Packages
echo.
echo  [STEP 4/6] Installing required packages...
echo  ------------------------------------------
echo  This may take a few minutes...
echo.

:: Core dependencies
echo  Installing core dependencies...
pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Data and ML dependencies
echo  Installing data processing libraries...
pip install --no-cache-dir yfinance==0.2.33 pandas==2.1.3 numpy==1.24.3 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

echo  Installing machine learning libraries...
pip install --no-cache-dir scikit-learn==1.3.2 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Additional utilities
echo  Installing additional utilities...
pip install --no-cache-dir aiofiles==23.2.1 python-multipart==0.0.6 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

echo  [OK] All packages installed successfully

:: Step 5: Create Configuration and Shortcuts
echo.
echo  [STEP 5/6] Creating shortcuts and configuration...
echo  ------------------------------------------

:: Create START_SERVER.bat
echo @echo off > START_SERVER.bat
echo cd /d "%INSTALL_DIR%" >> START_SERVER.bat
echo call venv\Scripts\activate.bat >> START_SERVER.bat
echo cls >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo ============================================================ >> START_SERVER.bat
echo echo  GSMT Enhanced Stock Tracker - Server Starting >> START_SERVER.bat
echo echo ============================================================ >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo Server will start on: http://localhost:8000 >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo echo Press Ctrl+C to stop the server >> START_SERVER.bat
echo echo. >> START_SERVER.bat
echo python backend\enhanced_ml_backend.py >> START_SERVER.bat
echo pause >> START_SERVER.bat

:: Create OPEN_DASHBOARD.bat
echo @echo off > OPEN_DASHBOARD.bat
echo echo Opening GSMT Dashboard in your default browser... >> OPEN_DASHBOARD.bat
echo timeout /t 2 /nobreak ^>nul >> OPEN_DASHBOARD.bat
echo start http://localhost:8000 >> OPEN_DASHBOARD.bat

:: Create STOP_SERVER.bat
echo @echo off > STOP_SERVER.bat
echo echo Stopping GSMT Server... >> STOP_SERVER.bat
echo taskkill /F /IM python.exe 2^>nul >> STOP_SERVER.bat
echo echo Server stopped. >> STOP_SERVER.bat
echo pause >> STOP_SERVER.bat

:: Create Desktop Shortcut (if desktop exists)
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    echo Creating desktop shortcuts...
    
    :: Create VBS script to make shortcuts
    echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
    echo sLinkFile = "%DESKTOP%\GSMT Stock Tracker.lnk" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
    echo oLink.TargetPath = "%INSTALL_DIR%\START_SERVER.bat" >> CreateShortcut.vbs
    echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
    echo oLink.Description = "Start GSMT Stock Tracker Server" >> CreateShortcut.vbs
    echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll, 13" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    
    cscript CreateShortcut.vbs >nul 2>&1
    del CreateShortcut.vbs
    
    echo  [OK] Desktop shortcut created
) else (
    echo  [INFO] Desktop not found, skipping shortcut creation
)

echo  [OK] Configuration complete

:: Step 6: Test Installation
echo.
echo  [STEP 6/6] Testing installation...
echo  ------------------------------------------
python -c "import fastapi, uvicorn, yfinance, pandas, numpy, sklearn; print('[OK] All imports successful')" 2>nul
if %errorlevel% neq 0 (
    echo  [WARNING] Some imports failed, but installation may still work
) else (
    echo  [OK] Installation test passed
)

:: Installation Complete
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  To use the application:
echo.
echo  1. QUICK START:
echo     - Double-click "START_SERVER.bat" to start the server
echo     - Double-click "OPEN_DASHBOARD.bat" to open the web interface
echo.
echo  2. MANUAL START:
echo     - Run: venv\Scripts\activate.bat
echo     - Run: python backend\enhanced_ml_backend.py
echo     - Open: http://localhost:8000 in your browser
echo.
echo  3. DESKTOP SHORTCUT:
echo     - Use "GSMT Stock Tracker" on your desktop
echo.
echo  ============================================================
echo.
echo  Would you like to start the application now? (Y/N)
set /p START_NOW=

if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting server...
    start /min cmd /c START_SERVER.bat
    timeout /t 5 /nobreak >nul
    echo Opening dashboard...
    start http://localhost:8000
    echo.
    echo Application started!
    echo You can close this window.
)

echo.
pause
exit /b 0

:install_error
echo  [ERROR] Package installation failed
echo  Please check your internet connection and try again
pause
exit /b 1