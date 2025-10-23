@echo off
:: Installation Fixer for GSMT Stock Tracker
:: Resolves common installation problems

color 0B
cls

echo ============================================================
echo  GSMT STOCK TRACKER - INSTALLATION FIXER
echo  Resolves Common Installation Problems
echo ============================================================
echo.
echo This tool will help fix installation issues like:
echo  - Running from System32/SysWOW64
echo  - Package installation failures
echo  - Virtual environment problems
echo  - Missing dependencies
echo.
pause

:: First, ensure we're in the right directory
echo.
echo Checking current directory...
set "CURRENT_DIR=%cd%"
echo Current location: %CURRENT_DIR%
echo.

if "%CURRENT_DIR%"=="C:\Windows\System32" goto :WRONG_DIR
if "%CURRENT_DIR%"=="C:\Windows\SysWOW64" goto :WRONG_DIR
if "%CURRENT_DIR%"=="C:\Windows" goto :WRONG_DIR
goto :CORRECT_DIR

:WRONG_DIR
echo ============================================================
echo  ERROR: Running from wrong directory!
echo ============================================================
echo.
echo You're running this from: %CURRENT_DIR%
echo This is a Windows system directory - not allowed!
echo.
echo TO FIX THIS:
echo.
echo 1. Open File Explorer
echo 2. Navigate to where you extracted GSMT_Windows11_Complete
echo    (Usually Downloads, Desktop, or C:\GSMT)
echo 3. Double-click this file from THAT location
echo    DO NOT use "Run as administrator" from System32!
echo.
echo If you can't find the extracted folder:
echo 1. Re-extract GSMT_Windows11_Final.zip to C:\GSMT
echo 2. Navigate to C:\GSMT\GSMT_Windows11_Complete
echo 3. Run this file from there
echo.
pause
exit /b 1

:CORRECT_DIR
echo [OK] Running from correct directory
set "INSTALL_DIR=%CURRENT_DIR%"

:: Check Python installation
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        goto :NO_PYTHON
    ) else (
        set "PYTHON_CMD=py"
        for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION=%%i
    )
) else (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
)
echo [OK] Python %PYTHON_VERSION% found
echo.

:: Menu
:MENU
echo ============================================================
echo  SELECT FIX TO APPLY:
echo ============================================================
echo.
echo  1. Full Clean Install (Recommended)
echo  2. Fix Virtual Environment Only
echo  3. Install Packages Manually
echo  4. Use Simple Backend (No numpy required)
echo  5. Test Current Installation
echo  6. Remove Everything and Start Fresh
echo  7. Exit
echo.
set /p CHOICE=Enter your choice (1-7): 

if "%CHOICE%"=="1" goto :CLEAN_INSTALL
if "%CHOICE%"=="2" goto :FIX_VENV
if "%CHOICE%"=="3" goto :MANUAL_PACKAGES
if "%CHOICE%"=="4" goto :SIMPLE_BACKEND
if "%CHOICE%"=="5" goto :TEST_INSTALL
if "%CHOICE%"=="6" goto :REMOVE_ALL
if "%CHOICE%"=="7" exit /b 0
goto :MENU

:CLEAN_INSTALL
echo.
echo Performing clean installation...
echo.

:: Remove old venv
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

:: Create new venv
echo Creating fresh virtual environment...
%PYTHON_CMD% -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install packages one by one
echo Installing packages (please wait)...
pip install fastapi
pip install uvicorn
pip install yfinance
pip install pandas
pip install aiofiles
pip install python-multipart

:: Try to install optional packages
pip install scikit-learn 2>nul
pip install numpy 2>nul

echo.
echo Clean installation complete!
pause
goto :CREATE_SCRIPTS

:FIX_VENV
echo.
echo Fixing virtual environment...

if exist venv (
    rmdir /s /q venv
)

%PYTHON_CMD% -m venv venv --clear
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel

echo Virtual environment fixed!
echo Run option 3 to install packages.
pause
goto :MENU

:MANUAL_PACKAGES
echo.
echo Installing packages manually...

if not exist venv (
    echo Creating virtual environment first...
    %PYTHON_CMD% -m venv venv
)

call venv\Scripts\activate.bat

echo.
echo Installing core packages:
echo.
pip list

echo.
echo Installing FastAPI...
pip install fastapi

echo.
echo Installing Uvicorn...
pip install uvicorn

echo.
echo Installing yfinance...
pip install yfinance

echo.
echo Installing pandas...
pip install pandas

echo.
echo Installing utilities...
pip install aiofiles python-multipart

echo.
echo Manual installation complete!
pause
goto :CREATE_SCRIPTS

:SIMPLE_BACKEND
echo.
echo Configuring simple backend (no numpy required)...

:CREATE_SCRIPTS
echo.
echo Creating startup scripts...

:: Create START_SIMPLE.bat
echo @echo off > START_SIMPLE.bat
echo cd /d "%INSTALL_DIR%" >> START_SIMPLE.bat
echo call venv\Scripts\activate.bat >> START_SIMPLE.bat
echo echo Starting Simple Backend (numpy-free)... >> START_SIMPLE.bat
echo python backend\simple_ml_backend.py >> START_SIMPLE.bat
echo pause >> START_SIMPLE.bat

:: Create standard START_SERVER.bat
echo @echo off > START_SERVER.bat
echo cd /d "%INSTALL_DIR%" >> START_SERVER.bat
echo call venv\Scripts\activate.bat >> START_SERVER.bat
echo echo Starting server... >> START_SERVER.bat
echo python backend\simple_ml_backend.py >> START_SERVER.bat
echo if %%errorlevel%% neq 0 python backend\enhanced_ml_backend.py >> START_SERVER.bat
echo pause >> START_SERVER.bat

echo.
echo Scripts created! Use START_SIMPLE.bat for numpy-free version.
pause
goto :MENU

:TEST_INSTALL
echo.
echo Testing installation...
echo.

if not exist venv (
    echo [ERROR] No virtual environment found!
    echo Run option 1 or 2 first.
    pause
    goto :MENU
)

call venv\Scripts\activate.bat

echo Testing Python packages:
python -c "import fastapi; print('[OK] FastAPI')" 2>nul || echo [FAIL] FastAPI
python -c "import uvicorn; print('[OK] Uvicorn')" 2>nul || echo [FAIL] Uvicorn
python -c "import yfinance; print('[OK] yfinance')" 2>nul || echo [FAIL] yfinance
python -c "import pandas; print('[OK] pandas')" 2>nul || echo [FAIL] pandas
python -c "import numpy; print('[OK] numpy')" 2>nul || echo [INFO] numpy not installed (use simple backend)
python -c "import sklearn; print('[OK] scikit-learn')" 2>nul || echo [INFO] scikit-learn not installed

echo.
echo Test complete!
pause
goto :MENU

:REMOVE_ALL
echo.
echo This will remove all installed files and start fresh.
echo Are you sure? (Y/N)
set /p CONFIRM=

if /i "%CONFIRM%"=="Y" (
    echo Removing virtual environment...
    if exist venv rmdir /s /q venv
    
    echo Removing generated files...
    del START_*.bat 2>nul
    del RUN_*.bat 2>nul
    del OPEN_*.bat 2>nul
    
    echo.
    echo Cleanup complete. Run INSTALL_ULTIMATE.bat to reinstall.
) else (
    echo Cancelled.
)
pause
goto :MENU

:NO_PYTHON
echo ============================================================
echo  ERROR: Python Not Found!
echo ============================================================
echo.
echo Python is not installed or not in PATH.
echo.
echo Please:
echo 1. Download Python from https://www.python.org/downloads/
echo 2. Install Python 3.8 to 3.12 (3.11 recommended)
echo 3. CHECK "Add Python to PATH" during installation
echo 4. Restart your computer
echo 5. Run this fixer again
echo.
pause
exit /b 1