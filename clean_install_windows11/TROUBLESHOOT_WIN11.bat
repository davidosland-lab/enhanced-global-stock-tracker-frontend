@echo off
setlocal EnableDelayedExpansion
color 0E
title Stock Tracker Troubleshooting - Windows 11

echo ================================================================================
echo                    STOCK TRACKER TROUBLESHOOTING TOOL
echo ================================================================================
echo.

cd /d "%~dp0"

echo [1] CHECKING SYSTEM STATUS
echo --------------------------------------------------------------------------------

:: Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Python not found in PATH
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do echo    [OK] Python %%a installed
)

:: Check pip
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] pip not found
) else (
    echo    [OK] pip is available
)

echo.
echo [2] CHECKING PORTS
echo --------------------------------------------------------------------------------

:: Function to check each port
for %%p in (8000 8002 8003) do (
    netstat -an | findstr :%%p | findstr LISTENING >nul 2>&1
    if !errorlevel! equ 0 (
        echo    Port %%p: IN USE
        for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
            echo       - Process ID: %%a
            for /f "tokens=1,2" %%b in ('tasklist /FI "PID eq %%a" ^| findstr %%a') do (
                echo       - Process Name: %%b
            )
        )
    ) else (
        echo    Port %%p: FREE
    )
)

echo.
echo [3] CHECKING REQUIRED FILES
echo --------------------------------------------------------------------------------

set FILES_OK=0
set FILES_MISSING=0

if exist "backend.py" (
    echo    [OK] backend.py found
    set /a FILES_OK+=1
) else (
    echo    [MISSING] backend.py
    set /a FILES_MISSING+=1
)

if exist "index.html" (
    echo    [OK] index.html found
    set /a FILES_OK+=1
) else (
    echo    [MISSING] index.html
    set /a FILES_MISSING+=1
)

if exist "modules\historical_data_manager.html" (
    echo    [OK] Historical Data Manager module found
    set /a FILES_OK+=1
) else (
    echo    [MISSING] Historical Data Manager module
    set /a FILES_MISSING+=1
)

echo.
echo    Files OK: !FILES_OK!
echo    Files Missing: !FILES_MISSING!

echo.
echo [4] CHECKING PYTHON PACKAGES
echo --------------------------------------------------------------------------------

:: Check critical packages
for %%p in (yfinance fastapi uvicorn pandas numpy) do (
    pip show %%p >nul 2>&1
    if !errorlevel! equ 0 (
        echo    [OK] %%p installed
    ) else (
        echo    [MISSING] %%p - install with: pip install %%p
    )
)

echo.
echo [5] TESTING BACKEND ENDPOINTS
echo --------------------------------------------------------------------------------

:: Test if backend is running
curl -s http://localhost:8002/ >nul 2>&1
if !errorlevel! equ 0 (
    echo    [OK] Backend responding on port 8002
    
    :: Test specific endpoints
    curl -s http://localhost:8002/api/historical/statistics >nul 2>&1
    if !errorlevel! equ 0 (
        echo    [OK] Historical Data Manager endpoint accessible
    ) else (
        echo    [WARNING] Historical Data Manager endpoint not responding
    )
) else (
    echo    [INFO] Backend not running - start with MASTER_STARTUP_WIN11.bat
)

echo.
echo [6] COMMON ISSUES AND SOLUTIONS
echo --------------------------------------------------------------------------------
echo.
echo ISSUE: "Python is not recognized"
echo SOLUTION: Install Python from python.org and add to PATH
echo.
echo ISSUE: "Port already in use"
echo SOLUTION: Run this command to kill processes:
echo    taskkill /F /IM python.exe
echo.
echo ISSUE: "Historical Data Manager not working"
echo SOLUTION: The backend.py file may be outdated. Ensure you have the latest version.
echo.
echo ISSUE: "Cannot install packages"
echo SOLUTION: Run as Administrator or use:
echo    python -m pip install --user [package]
echo.

echo.
echo [7] QUICK FIXES
echo --------------------------------------------------------------------------------
echo.
echo Press the number for the action you want:
echo.
echo 1 - Kill all Python processes
echo 2 - Install/Update all required packages
echo 3 - Start services with master script
echo 4 - Open application in browser
echo 5 - View log files
echo 6 - Exit
echo.

choice /c 123456 /n /m "Select option: "

if errorlevel 6 goto :end
if errorlevel 5 goto :logs
if errorlevel 4 goto :browser
if errorlevel 3 goto :start
if errorlevel 2 goto :install
if errorlevel 1 goto :kill

:kill
echo.
echo Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo Done!
pause
goto :end

:install
echo.
echo Installing required packages...
pip install --upgrade pip
pip install --upgrade "urllib3<2" yfinance fastapi uvicorn python-multipart pandas numpy cachetools pytz requests scikit-learn xgboost joblib
echo Done!
pause
goto :end

:start
echo.
echo Starting services...
call "%~dp0MASTER_STARTUP_WIN11.bat"
goto :end

:browser
echo.
echo Opening application...
start http://localhost:8000
pause
goto :end

:logs
echo.
echo Log files location: %~dp0logs\
if exist "logs" (
    echo.
    echo Available log files:
    dir /b logs\*.log 2>nul
    echo.
    echo Opening logs folder...
    start explorer "%~dp0logs"
) else (
    echo No log directory found.
)
pause
goto :end

:end
echo.
echo Troubleshooting complete.
pause
exit /b