@echo off
echo ============================================================
echo      ML STOCK PREDICTOR - UNIFIED INSTALLATION & STARTUP
echo ============================================================
echo.

:: Step 1: Check Python
echo [Step 1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
python --version

:: Step 2: Install Dependencies
echo.
echo [Step 2/3] Installing required packages...
echo This may take a few minutes on first run...
pip install --upgrade pip >nul 2>&1
pip install -r requirements_windows_py312.txt
if errorlevel 1 (
    echo.
    echo Trying alternative requirements file...
    pip install -r requirements.txt
)

:: Step 3: Start System
echo.
echo [Step 3/3] Starting unified ML system...
echo.
echo ============================================================
echo.
call START_UNIFIED_SYSTEM.bat