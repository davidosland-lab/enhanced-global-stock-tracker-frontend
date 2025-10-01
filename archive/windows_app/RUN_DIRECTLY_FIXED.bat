@echo off
REM Direct run script with proper path handling
REM This version finds and runs the Python file correctly

echo ========================================
echo Stock Predictor Pro - Direct Run
echo ========================================
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
echo Script directory: %SCRIPT_DIR%

REM Check if the lite version exists in the current directory
if exist "%SCRIPT_DIR%stock_predictor_lite.py" (
    echo Found stock_predictor_lite.py in current directory
    cd /d "%SCRIPT_DIR%"
    goto :RunApp
) else (
    echo ERROR: stock_predictor_lite.py not found in %SCRIPT_DIR%
    echo.
    echo Please make sure all files are extracted to the same folder.
    echo.
    pause
    exit /b 1
)

:RunApp
echo.
echo Starting Stock Predictor Pro (Lite Version)...
echo.

REM Try with python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using 'python' command...
    python "%SCRIPT_DIR%stock_predictor_lite.py"
    if %errorlevel% equ 0 goto :Success
)

REM Try with python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using 'python3' command...
    python3 "%SCRIPT_DIR%stock_predictor_lite.py"
    if %errorlevel% equ 0 goto :Success
)

REM Try with py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using 'py' launcher...
    py "%SCRIPT_DIR%stock_predictor_lite.py"
    if %errorlevel% equ 0 goto :Success
)

REM Try specific Python paths
if exist "C:\Python39\python.exe" (
    echo Using Python 3.9 from C:\Python39...
    "C:\Python39\python.exe" "%SCRIPT_DIR%stock_predictor_lite.py"
    if %errorlevel% equ 0 goto :Success
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" (
    echo Using Python 3.9 from user directory...
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" "%SCRIPT_DIR%stock_predictor_lite.py"
    if %errorlevel% equ 0 goto :Success
)

REM If all fails
echo.
echo ==========================================
echo ERROR: Could not run Stock Predictor Pro
echo ==========================================
echo.
echo Python doesn't seem to be installed or accessible.
echo.
echo Please install Python 3.9 or higher from:
echo https://www.python.org/downloads/
echo.
echo During installation, make sure to check:
echo [X] Add Python to PATH
echo.
pause
exit /b 1

:Success
echo.
echo Application closed successfully.
pause