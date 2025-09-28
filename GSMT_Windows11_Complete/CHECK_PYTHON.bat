@echo off
:: Python Version Checker and Compatibility Tool
:: For GSMT Stock Tracker

color 0E
cls

echo ============================================================
echo  PYTHON VERSION CHECK AND COMPATIBILITY TOOL
echo ============================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    echo RECOMMENDED VERSIONS:
    echo  - Python 3.11.x (Best compatibility)
    echo  - Python 3.12.x (Good compatibility)
    echo  - Python 3.10.x (Also works well)
    echo.
    echo AVOID:
    echo  - Python 3.13.x (Has numpy compatibility issues)
    echo  - Python 2.x (Not supported)
    echo.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Detected Python version: %PYTHON_VERSION%
echo.

:: Parse version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

:: Check compatibility
echo Checking compatibility...
echo.

if %MAJOR% NEQ 3 (
    echo [ERROR] Python 3.x is required (found Python %MAJOR%.x)
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

if %MINOR% GEQ 13 (
    echo [WARNING] Python 3.13+ detected
    echo.
    echo This version has known compatibility issues with numpy and
    echo some scientific libraries used by the stock tracker.
    echo.
    echo RECOMMENDATION:
    echo  1. Install Python 3.11 or 3.12 alongside current version
    echo  2. Or use the simplified backend (simple_ml_backend.py)
    echo.
    echo The installer will attempt to work around these issues,
    echo but you may experience problems.
    echo.
    set COMPAT_LEVEL=LOW
) else if %MINOR% GEQ 11 (
    echo [OK] Python 3.%MINOR% - Excellent compatibility!
    echo This version works perfectly with all features.
    echo.
    set COMPAT_LEVEL=HIGH
) else if %MINOR% GEQ 8 (
    echo [OK] Python 3.%MINOR% - Good compatibility
    echo This version should work well.
    echo.
    set COMPAT_LEVEL=GOOD
) else (
    echo [WARNING] Python 3.%MINOR% - May have compatibility issues
    echo Consider upgrading to Python 3.11 or 3.12
    echo.
    set COMPAT_LEVEL=MEDIUM
)

:: Check for multiple Python installations
echo Checking for other Python installations...
echo.

:: Check common Python locations
set PYTHON_PATHS=
if exist "C:\Python311\python.exe" (
    echo Found: Python 3.11 at C:\Python311
    set PYTHON_PATHS=%PYTHON_PATHS%;C:\Python311
)
if exist "C:\Python312\python.exe" (
    echo Found: Python 3.12 at C:\Python312
    set PYTHON_PATHS=%PYTHON_PATHS%;C:\Python312
)
if exist "C:\Python310\python.exe" (
    echo Found: Python 3.10 at C:\Python310
    set PYTHON_PATHS=%PYTHON_PATHS%;C:\Python310
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo Found: Python 3.11 in AppData
    set PYTHON_PATHS=%PYTHON_PATHS%;%LOCALAPPDATA%\Programs\Python\Python311
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo Found: Python 3.12 in AppData
    set PYTHON_PATHS=%PYTHON_PATHS%;%LOCALAPPDATA%\Programs\Python\Python312
)

echo.
echo ============================================================
echo  RECOMMENDATIONS
echo ============================================================
echo.

if "%COMPAT_LEVEL%"=="HIGH" (
    echo Your Python version is perfect for GSMT Stock Tracker!
    echo You can proceed with the standard installation.
    echo.
    echo Run: INSTALL.bat or INSTALL_FIXED.bat
) else if "%COMPAT_LEVEL%"=="GOOD" (
    echo Your Python version will work well.
    echo You can proceed with the standard installation.
    echo.
    echo Run: INSTALL.bat or INSTALL_FIXED.bat
) else if "%COMPAT_LEVEL%"=="LOW" (
    echo For best results with Python 3.13+:
    echo.
    echo 1. Use INSTALL_FIXED.bat (handles compatibility)
    echo 2. Or install Python 3.11/3.12 from python.org
    echo 3. Use simple_ml_backend.py instead of enhanced version
    echo.
    echo The simplified backend works without numpy dependencies.
) else (
    echo Your Python version may work but consider upgrading.
    echo.
    echo Run: INSTALL_FIXED.bat for best compatibility
)

echo.
echo ============================================================
echo  NEXT STEPS
echo ============================================================
echo.
echo 1. If Python is compatible: Run INSTALL_FIXED.bat
echo 2. If issues persist: Install Python 3.11 or 3.12
echo 3. For Python 3.13: Use simplified backend
echo.
echo Press any key to exit...
pause >nul