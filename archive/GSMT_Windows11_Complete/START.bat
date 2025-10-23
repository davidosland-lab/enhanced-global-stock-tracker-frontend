@echo off
title GSMT Stock Tracker - Main Launcher
cls

echo ================================================================
echo                 GSMT STOCK TRACKER v8.1.3
echo              COMPLETE WINDOWS 11 EDITION
echo ================================================================
echo.

:: Check if running from System32
set "CURRENT_DIR=%CD%"
echo Current directory: %CURRENT_DIR%
echo.

if /I "%CURRENT_DIR%" == "C:\Windows\System32" (
    echo ERROR: Cannot run from System32 directory!
    echo Please copy this folder to another location like:
    echo   - C:\GSMT
    echo   - Desktop
    echo   - Documents
    echo.
    pause
    exit /b 1
)

:: Check for Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

python --version
echo.

:: Check for required packages
echo Checking required packages...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo FastAPI not found. Installing required packages...
    echo.
    pip install fastapi uvicorn --no-warn-script-location
    if errorlevel 1 (
        echo.
        echo Failed to install packages automatically.
        echo Please run FIX_INSTALLATION.bat first!
        pause
        exit /b 1
    )
)

:: Menu
:MENU
cls
echo ================================================================
echo                 GSMT STOCK TRACKER v8.1.3
echo ================================================================
echo.
echo Select an option:
echo.
echo   1. Launch Complete System (All Modules) - RECOMMENDED
echo   2. Start Main Server Only
echo   3. Start Test Server (For Testing)
echo   4. Start Simple Backend (Lightweight)
echo   5. Check Server Status
echo   6. Open Frontend in Browser
echo   7. Run Diagnostics
echo   8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto LAUNCH_COMPLETE
if "%choice%"=="2" goto START_MAIN
if "%choice%"=="3" goto START_TEST
if "%choice%"=="4" goto START_SIMPLE
if "%choice%"=="5" goto CHECK_STATUS
if "%choice%"=="6" goto OPEN_FRONTEND
if "%choice%"=="7" goto DIAGNOSTICS
if "%choice%"=="8" goto EXIT

echo Invalid choice. Please try again.
pause
goto MENU

:LAUNCH_COMPLETE
cls
echo ================================================================
echo Launching Complete GSMT System with All Modules...
echo ================================================================
echo.
call LAUNCH_COMPLETE.bat
goto MENU

:START_MAIN
cls
echo ================================================================
echo Starting GSMT Main Server...
echo ================================================================
echo.
echo Server will run on: http://localhost:8000
echo.
echo To test the server, open your browser and visit:
echo   - http://localhost:8000 (API Documentation)
echo   - http://localhost:8000/health (Health Check)
echo   - http://localhost:8000/api/tracker (Stock Data)
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

if exist "backend\main_server.py" (
    python backend\main_server.py
) else (
    echo ERROR: main_server.py not found!
    echo Please ensure the backend folder contains main_server.py
    pause
)
goto MENU

:START_TEST
cls
echo ================================================================
echo Starting Test Server...
echo ================================================================
echo.

if exist "backend\test_server.py" (
    python backend\test_server.py
) else (
    echo ERROR: test_server.py not found!
    pause
)
goto MENU

:START_SIMPLE
cls
echo ================================================================
echo Starting Simple Backend...
echo ================================================================
echo.

if exist "backend\simple_ml_backend.py" (
    python backend\simple_ml_backend.py
) else (
    echo ERROR: simple_ml_backend.py not found!
    pause
)
goto MENU

:CHECK_STATUS
cls
echo ================================================================
echo Checking Server Status...
echo ================================================================
echo.

:: Test localhost:8000
echo Testing http://localhost:8000 ...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/health 2>nul
if errorlevel 1 (
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing; Write-Host 'Server is RUNNING' -ForegroundColor Green; Write-Host $response.Content } catch { Write-Host 'Server is NOT running' -ForegroundColor Red }"
) else (
    echo Server appears to be running!
)

echo.
pause
goto MENU

:OPEN_FRONTEND
cls
echo ================================================================
echo Opening Frontend...
echo ================================================================
echo.

if exist "frontend\index.html" (
    echo Opening frontend in default browser...
    start "" "frontend\index.html"
) else (
    echo Frontend files not found!
    echo Looking for alternative locations...
    if exist "index.html" (
        start "" "index.html"
    ) else (
        echo No frontend files found!
    )
)

echo.
pause
goto MENU

:DIAGNOSTICS
cls
echo ================================================================
echo Running Diagnostics...
echo ================================================================
echo.

echo Python Version:
python --version
echo.

echo Installed Packages:
pip list | findstr /I "fastapi uvicorn"
echo.

echo Current Directory:
echo %CD%
echo.

echo Backend Files:
dir /B backend\*.py 2>nul
echo.

echo Frontend Files:
dir /B frontend\*.html 2>nul
echo.

pause
goto MENU

:EXIT
echo.
echo Thank you for using GSMT Stock Tracker!
echo.
pause
exit /b 0