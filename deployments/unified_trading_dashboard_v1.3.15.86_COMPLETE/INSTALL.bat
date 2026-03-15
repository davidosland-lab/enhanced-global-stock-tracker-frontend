@echo off
cls
echo ===============================================================
echo     Unified Trading Dashboard v1.3.15.86 Installation
echo ===============================================================
echo.

echo [Step 1] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)
echo SUCCESS: Python found
echo.

echo [Step 2] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo SUCCESS: Dependencies installed
echo.

echo [Step 3] Creating directory structure...
if not exist "logs" mkdir logs
if not exist "state" mkdir state
if not exist "reports\screening" mkdir reports\screening
echo SUCCESS: Directories created
echo.

echo [Step 4] Copying core files to current directory...
copy /Y core\*.py . > nul
if errorlevel 1 (
    echo ERROR: Failed to copy core files
    pause
    exit /b 1
)
echo SUCCESS: Core files copied
echo.

echo ===============================================================
echo              Installation Complete!
echo ===============================================================
echo.
echo To start the dashboard:
echo    1. Run: START.bat
echo    2. Open browser: http://localhost:8050
echo.
echo See docs\ folder for documentation
echo.
pause
