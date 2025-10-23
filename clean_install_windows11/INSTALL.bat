@echo off
title Stock Tracker Installation
color 0B

echo ================================================================================
echo                      STOCK TRACKER INSTALLATION
echo                         Windows 11 Edition v2.0
echo ================================================================================
echo.
echo This installer will:
echo   1. Check Python installation
echo   2. Install required packages
echo   3. Create desktop shortcuts
echo   4. Verify all files are present
echo   5. Start the Stock Tracker
echo.
echo Press any key to begin installation...
pause >nul

cls
echo ================================================================================
echo                         STEP 1: CHECKING PYTHON
echo ================================================================================
echo.

python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python is installed
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo    Version: %%i
) else (
    echo ✗ Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                      STEP 2: INSTALLING PACKAGES
echo ================================================================================
echo.
echo Installing required Python packages...
echo.

echo [1/7] Installing FastAPI...
pip install fastapi >nul 2>&1
if %errorlevel% == 0 (echo    ✓ FastAPI installed) else (echo    ! FastAPI installation failed)

echo [2/7] Installing Uvicorn...
pip install uvicorn >nul 2>&1
if %errorlevel% == 0 (echo    ✓ Uvicorn installed) else (echo    ! Uvicorn installation failed)

echo [3/7] Installing yfinance...
pip install yfinance >nul 2>&1
if %errorlevel% == 0 (echo    ✓ yfinance installed) else (echo    ! yfinance installation failed)

echo [4/7] Installing pandas...
pip install pandas >nul 2>&1
if %errorlevel% == 0 (echo    ✓ pandas installed) else (echo    ! pandas installation failed)

echo [5/7] Installing numpy...
pip install numpy >nul 2>&1
if %errorlevel% == 0 (echo    ✓ numpy installed) else (echo    ! numpy installation failed)

echo [6/7] Installing scikit-learn...
pip install scikit-learn >nul 2>&1
if %errorlevel% == 0 (echo    ✓ scikit-learn installed) else (echo    ! scikit-learn installation failed)

echo [7/7] Installing python-multipart...
pip install python-multipart >nul 2>&1
if %errorlevel% == 0 (echo    ✓ python-multipart installed) else (echo    ! python-multipart installation failed)

echo.
echo ================================================================================
echo                      STEP 3: VERIFYING FILES
echo ================================================================================
echo.

set files_ok=1

if exist "%~dp0backend.py" (
    echo ✓ Main backend found
) else (
    echo ✗ backend.py is missing!
    set files_ok=0
)

if exist "%~dp0backend_ml_enhanced.py" (
    echo ✓ ML backend found
) else (
    echo ✗ backend_ml_enhanced.py is missing!
    set files_ok=0
)

if exist "%~dp0index.html" (
    echo ✓ Frontend interface found
) else (
    echo ✗ index.html is missing!
    set files_ok=0
)

if exist "%~dp0modules\" (
    echo ✓ Modules folder found
) else (
    echo ✗ modules folder is missing!
    set files_ok=0
)

if %files_ok% == 0 (
    echo.
    echo ✗ Some required files are missing!
    echo Please ensure all files are extracted properly.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                    STEP 4: CREATING DESKTOP SHORTCUTS
echo ================================================================================
echo.

call "%~dp0CREATE_DESKTOP_SHORTCUTS.bat" >nul 2>&1
echo ✓ Desktop shortcuts created

echo.
echo ================================================================================
echo                    STEP 5: STARTING STOCK TRACKER
echo ================================================================================
echo.

:: Clean up any existing processes
echo Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo Starting services...
echo   [1/3] Frontend Server...
start "Frontend" /min cmd /c "cd /d %~dp0 && python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo   [2/3] Main Backend...
start "Backend" /min cmd /c "cd /d %~dp0 && python backend.py"
timeout /t 3 /nobreak >nul

echo   [3/3] ML Backend...
start "ML Backend" /min cmd /c "cd /d %~dp0 && python backend_ml_enhanced.py"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo              ✓ INSTALLATION COMPLETE - STOCK TRACKER IS RUNNING!
echo ================================================================================
echo.
echo Opening Stock Tracker in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo Desktop shortcuts have been created:
echo   • Stock Tracker Control Panel - For managing services
echo   • Stock Tracker Quick Start - For quick launching
echo   • Stock Tracker Shutdown - For stopping services
echo   • Stock Tracker Web Interface - For browser access
echo.
echo Stock Tracker is now accessible at: http://localhost:8000
echo.
echo To manage services, use the Stock Tracker Control Panel on your desktop.
echo.
pause