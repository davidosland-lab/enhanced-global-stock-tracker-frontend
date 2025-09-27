@echo off
REM Portable runner - works from any location
REM This version ensures we're in the right directory

echo ==========================================
echo Stock Predictor Pro - Portable Launcher
echo ==========================================
echo.

REM Change to the directory containing this batch file
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM List files to verify everything is here
echo Checking files...
if exist "stock_predictor_lite.py" (
    echo [OK] stock_predictor_lite.py found
) else (
    echo [ERROR] stock_predictor_lite.py NOT FOUND
    echo.
    echo Please extract ALL files from the ZIP archive!
    echo All files must be in the same folder.
    echo.
    pause
    exit /b 1
)

echo.
echo Detecting Python installation...

REM Method 1: Try the standard python command
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python in PATH
    python --version
    echo.
    echo Launching Stock Predictor Pro...
    python stock_predictor_lite.py
    goto :End
)

REM Method 2: Try python3
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python3 in PATH
    python3 --version
    echo.
    echo Launching Stock Predictor Pro...
    python3 stock_predictor_lite.py
    goto :End
)

REM Method 3: Try py launcher (Windows Python Launcher)
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python Launcher
    py --version
    echo.
    echo Launching Stock Predictor Pro...
    py stock_predictor_lite.py
    goto :End
)

REM Method 4: Look for Python in common locations
echo.
echo Searching for Python in common locations...

REM Check Python 3.9 standard location
if exist "C:\Python39\python.exe" (
    echo Found Python 3.9 at C:\Python39
    "C:\Python39\python.exe" --version
    echo.
    echo Launching Stock Predictor Pro...
    "C:\Python39\python.exe" stock_predictor_lite.py
    goto :End
)

REM Check user-specific Python 3.9
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo Found Python 3.9 in user directory
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" --version
    echo.
    echo Launching Stock Predictor Pro...
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" stock_predictor_lite.py
    goto :End
)

REM Check Windows Store Python (your case)
set STORE_PYTHON=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
if exist "%STORE_PYTHON%" (
    echo Found Windows Store Python
    "%STORE_PYTHON%" --version
    echo.
    echo Launching Stock Predictor Pro...
    "%STORE_PYTHON%" stock_predictor_lite.py
    goto :End
)

REM If nothing works
echo.
echo ==========================================
echo ERROR: Python Not Found!
echo ==========================================
echo.
echo Could not find Python installation.
echo.
echo To fix this:
echo 1. Install Python 3.9 or higher from python.org
echo 2. During installation, check "Add Python to PATH"
echo 3. Run this script again
echo.
echo Download Python from:
echo https://www.python.org/downloads/
echo.
pause
exit /b 1

:End
echo.
echo ==========================================
echo Application closed.
echo ==========================================
pause