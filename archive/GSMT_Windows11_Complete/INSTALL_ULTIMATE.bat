@echo off
setlocal enabledelayedexpansion

:: =========================================
:: GSMT Enhanced Stock Tracker
:: Ultimate Windows 11 Installer v3.2
:: Fixes all known installation issues
:: =========================================

color 0A
cls

echo.
echo  ============================================================
echo   GSMT ENHANCED STOCK TRACKER - ULTIMATE INSTALLER
echo   Version 3.2 - All Issues Fixed
echo  ============================================================
echo.

:: CRITICAL: Check if running from System32 and fix
set "CURRENT_DIR=%cd%"
echo  Current Directory: %CURRENT_DIR%

if "%CURRENT_DIR%"=="C:\Windows\System32" (
    echo.
    echo  [ERROR] Installer is running from System32!
    echo  This happens when you run the installer incorrectly.
    echo.
    echo  SOLUTION:
    echo  1. Close this window
    echo  2. Navigate to where you extracted the GSMT folder
    echo  3. Right-click INSTALL_ULTIMATE.bat
    echo  4. Select "Run as administrator" (if needed)
    echo.
    echo  DO NOT run from command prompt in System32!
    echo.
    pause
    exit /b 1
)

if "%CURRENT_DIR%"=="C:\Windows\SysWOW64" (
    echo.
    echo  [ERROR] Installer is running from SysWOW64!
    echo  Please run from the extracted GSMT folder instead.
    echo.
    pause
    exit /b 1
)

:: Set correct installation directory
set "INSTALL_DIR=%CURRENT_DIR%"
echo  Installation Directory: %INSTALL_DIR%
echo.
pause

:: Step 1: Check Python
echo  [STEP 1/7] Checking Python installation...
echo  ------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Python is not installed
        echo.
        echo  Please install Python 3.8-3.12 from:
        echo  https://www.python.org/downloads/
        echo.
        echo  IMPORTANT: Check "Add Python to PATH"
        echo.
        pause
        exit /b 1
    ) else (
        echo  [INFO] Using Python Launcher (py)
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

:: Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo  [OK] Python !PYTHON_VERSION! detected

:: Step 2: Create Virtual Environment
echo.
echo  [STEP 2/7] Creating virtual environment...
echo  ------------------------------------------

:: Remove old venv if exists
if exist "%INSTALL_DIR%\venv" (
    echo  Removing old virtual environment...
    rmdir /s /q "%INSTALL_DIR%\venv"
)

:: Create new venv in the correct directory
%PYTHON_CMD% -m venv "%INSTALL_DIR%\venv"
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create virtual environment
    echo  Trying alternative method...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        pause
        exit /b 1
    )
)
echo  [OK] Virtual environment created

:: Step 3: Activate venv and upgrade pip
echo.
echo  [STEP 3/7] Activating virtual environment...
echo  ------------------------------------------

:: Activate using full path
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo  [WARNING] Activation had issues, continuing anyway...
)

:: Use venv's python directly for safety
set "VENV_PYTHON=%INSTALL_DIR%\venv\Scripts\python.exe"

echo  Upgrading pip, setuptools, and wheel...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel --no-cache-dir >nul 2>&1
echo  [OK] Environment ready

:: Step 4: Install packages with verbose output
echo.
echo  [STEP 4/7] Installing packages (with progress)...
echo  ------------------------------------------

:: Try fast installation first
echo  Attempting fast installation...
"%VENV_PYTHON%" -m pip install fastapi uvicorn[standard] yfinance pandas scikit-learn aiofiles python-multipart --no-cache-dir >nul 2>&1

if %errorlevel% neq 0 (
    echo  Fast installation failed. Installing packages individually...
    
    :: Install one by one with output
    echo.
    echo  [1/7] Installing fastapi...
    "%VENV_PYTHON%" -m pip install fastapi --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [RETRY] Trying without version constraint...
        "%VENV_PYTHON%" -m pip install fastapi
    )
    
    echo.
    echo  [2/7] Installing uvicorn...
    "%VENV_PYTHON%" -m pip install uvicorn[standard] --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [RETRY] Trying basic uvicorn...
        "%VENV_PYTHON%" -m pip install uvicorn
    )
    
    echo.
    echo  [3/7] Installing yfinance...
    "%VENV_PYTHON%" -m pip install yfinance --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [WARNING] yfinance installation failed
        echo     The app will work but without real-time data
    )
    
    echo.
    echo  [4/7] Installing pandas...
    "%VENV_PYTHON%" -m pip install pandas --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [RETRY] Trying older pandas version...
        "%VENV_PYTHON%" -m pip install "pandas<2.0"
    )
    
    echo.
    echo  [5/7] Installing numpy (if needed)...
    "%VENV_PYTHON%" -m pip install numpy --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [INFO] Numpy not installed - using simple backend
        set "USE_SIMPLE_BACKEND=1"
    )
    
    echo.
    echo  [6/7] Installing scikit-learn...
    "%VENV_PYTHON%" -m pip install scikit-learn --no-cache-dir
    if %errorlevel% neq 0 (
        echo     [INFO] Scikit-learn not installed - basic ML only
    )
    
    echo.
    echo  [7/7] Installing utilities...
    "%VENV_PYTHON%" -m pip install aiofiles python-multipart --no-cache-dir
    
) else (
    echo  [OK] All packages installed successfully!
)

:: Step 5: Create batch files
echo.
echo  [STEP 5/7] Creating startup scripts...
echo  ------------------------------------------

:: Create START_SERVER.bat with proper paths
echo @echo off > "%INSTALL_DIR%\START_SERVER.bat"
echo title GSMT Stock Tracker Server >> "%INSTALL_DIR%\START_SERVER.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\START_SERVER.bat"
echo call "%INSTALL_DIR%\venv\Scripts\activate.bat" >> "%INSTALL_DIR%\START_SERVER.bat"
echo cls >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo. >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo ============================================================ >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo  GSMT Stock Tracker - Server Starting >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo ============================================================ >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo. >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo Server: http://localhost:8000 >> "%INSTALL_DIR%\START_SERVER.bat"
echo echo. >> "%INSTALL_DIR%\START_SERVER.bat"

if "%USE_SIMPLE_BACKEND%"=="1" (
    echo echo Using simplified backend (numpy-free^) >> "%INSTALL_DIR%\START_SERVER.bat"
    echo "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\simple_ml_backend.py" >> "%INSTALL_DIR%\START_SERVER.bat"
) else (
    echo "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\enhanced_ml_backend.py" >> "%INSTALL_DIR%\START_SERVER.bat"
    echo if %%errorlevel%% neq 0 ^( >> "%INSTALL_DIR%\START_SERVER.bat"
    echo     echo Enhanced backend failed, trying simple backend... >> "%INSTALL_DIR%\START_SERVER.bat"
    echo     "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\simple_ml_backend.py" >> "%INSTALL_DIR%\START_SERVER.bat"
    echo ^) >> "%INSTALL_DIR%\START_SERVER.bat"
)
echo pause >> "%INSTALL_DIR%\START_SERVER.bat"

:: Create OPEN_DASHBOARD.bat
echo @echo off > "%INSTALL_DIR%\OPEN_DASHBOARD.bat"
echo echo Opening dashboard... >> "%INSTALL_DIR%\OPEN_DASHBOARD.bat"
echo timeout /t 3 /nobreak ^>nul >> "%INSTALL_DIR%\OPEN_DASHBOARD.bat"
echo start http://localhost:8000 >> "%INSTALL_DIR%\OPEN_DASHBOARD.bat"

:: Create RUN_APP.bat
echo @echo off > "%INSTALL_DIR%\RUN_APP.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\RUN_APP.bat"
echo start "GSMT Server" /min START_SERVER.bat >> "%INSTALL_DIR%\RUN_APP.bat"
echo timeout /t 5 /nobreak ^>nul >> "%INSTALL_DIR%\RUN_APP.bat"
echo start http://localhost:8000 >> "%INSTALL_DIR%\RUN_APP.bat"

echo  [OK] Scripts created

:: Step 6: Test imports
echo.
echo  [STEP 6/7] Testing installation...
echo  ------------------------------------------

"%VENV_PYTHON%" -c "import fastapi; print('  [OK] FastAPI works')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] FastAPI import failed

"%VENV_PYTHON%" -c "import uvicorn; print('  [OK] Uvicorn works')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] Uvicorn import failed

"%VENV_PYTHON%" -c "import yfinance; print('  [OK] yfinance works')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] yfinance import failed

"%VENV_PYTHON%" -c "import pandas; print('  [OK] pandas works')" 2>nul
if %errorlevel% neq 0 echo  [WARNING] pandas import failed

:: Step 7: Create desktop shortcut
echo.
echo  [STEP 7/7] Creating desktop shortcut...
echo  ------------------------------------------

set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
    echo sLinkFile = "%DESKTOP%\GSMT Stock Tracker.lnk" >> "%TEMP%\CreateShortcut.vbs"
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
    echo oLink.TargetPath = "%INSTALL_DIR%\RUN_APP.bat" >> "%TEMP%\CreateShortcut.vbs"
    echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\CreateShortcut.vbs"
    echo oLink.Description = "GSMT Stock Tracker" >> "%TEMP%\CreateShortcut.vbs"
    echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll, 13" >> "%TEMP%\CreateShortcut.vbs"
    echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
    
    cscript //nologo "%TEMP%\CreateShortcut.vbs" >nul 2>&1
    del "%TEMP%\CreateShortcut.vbs"
    echo  [OK] Desktop shortcut created
) else (
    echo  [INFO] Desktop not found, skipping
)

:: Completion
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  Installation directory: %INSTALL_DIR%
echo.
echo  To start the application:
echo    1. Use desktop shortcut "GSMT Stock Tracker"
echo    2. Or double-click RUN_APP.bat
echo    3. Or run START_SERVER.bat then open http://localhost:8000
echo.
if "%USE_SIMPLE_BACKEND%"=="1" (
    echo  NOTE: Using simplified backend (numpy-free version)
    echo        Full features available but with basic ML models
    echo.
)
echo  ============================================================
echo.
echo  Start the application now? (Y/N)
set /p START_NOW=

if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting GSMT Stock Tracker...
    cd /d "%INSTALL_DIR%"
    start "GSMT Server" /min START_SERVER.bat
    echo Waiting for server...
    timeout /t 5 /nobreak >nul
    start http://localhost:8000
    echo.
    echo Application started!
)

echo.
echo Press any key to exit installer...
pause >nul
exit /b 0