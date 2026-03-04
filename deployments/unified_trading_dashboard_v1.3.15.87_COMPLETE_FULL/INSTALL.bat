@echo off
echo ====================================
echo Unified Trading Dashboard v1.3.15.87
echo Installation Script
echo ====================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)
echo Python found - OK
echo.

echo Step 2: Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed - OK
echo.

echo Step 3: Creating directories...
if not exist logs mkdir logs
if not exist state mkdir state
if not exist reports\screening mkdir reports\screening
echo Directories created - OK
echo.

echo Step 4: Setting up core files...
if exist core\*.py (
    echo Core files found - OK
) else (
    echo ERROR: Core files not found
    pause
    exit /b 1
)
echo.

echo ====================================
echo Installation Complete
echo ====================================
echo.
echo Next steps:
echo 1. Run START.bat to start dashboard
echo 2. Open browser to http://localhost:8050
echo 3. Check docs\ folder for documentation
echo.
pause
