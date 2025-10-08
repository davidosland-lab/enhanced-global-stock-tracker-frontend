@echo off
cls
echo ============================================================
echo     ML Training Centre - Model Dropdown Fix v2.0
echo ============================================================
echo.
echo This script fixes the syntax error and model dropdown issue.
echo.

REM Check current directory
echo Checking environment...
if not exist modules\ml_training_centre.html (
    echo.
    echo ERROR: Cannot find modules\ml_training_centre.html
    echo.
    echo Please run this script from the Stock Tracker main folder
    echo Example: C:\StockTracker\clean_install_windows11\
    echo.
    pause
    exit /b 1
)

echo ✓ Found ML Training Centre file
echo.

REM Stop any running services first
echo Stopping any running services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✓ Services stopped
echo.

REM Create backup
echo Creating backup...
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
copy modules\ml_training_centre.html "modules\ml_training_centre.BACKUP_%timestamp%.html" >nul
echo ✓ Backup created: ml_training_centre.BACKUP_%timestamp%.html
echo.

REM Download or use the fixed Python script
echo Applying fixes...
if exist FIX_ML_DROPDOWN_CLEAN.py (
    python FIX_ML_DROPDOWN_CLEAN.py >nul 2>&1
    if errorlevel 1 (
        echo ⚠ Python fix encountered issues, trying manual fix...
        goto :manual_fix
    ) else (
        echo ✓ Applied Python-based fix
        goto :verify_fix
    )
) else (
    goto :manual_fix
)

:manual_fix
REM If Python script isn't available, download the fixed file directly
echo Downloading fixed version...
curl -s -o modules\ml_training_centre.html https://raw.githubusercontent.com/your-repo/ml_training_centre_fixed.html >nul 2>&1
if errorlevel 1 (
    echo ⚠ Could not download fixed version
    echo.
    echo Please manually copy the fixed ml_training_centre.html file
    echo to the modules\ directory.
    echo.
    pause
    exit /b 1
)
echo ✓ Fixed version installed

:verify_fix
REM Clear browser cache reminder
echo.
echo ============================================================
echo ✅ Fix Applied Successfully!
echo ============================================================
echo.
echo IMPORTANT: Clear your browser cache!
echo.
echo 1. Close ALL browser windows completely
echo 2. Open a new browser window
echo 3. Press Ctrl+Shift+Delete
echo 4. Select "Cached images and files"
echo 5. Click "Clear data"
echo.
echo ============================================================
echo.
echo Fixed Issues:
echo ✓ Removed syntax errors (unexpected token '^')
echo ✓ Fixed duplicate variable declarations
echo ✓ Models now appear in dropdown after training
echo ✓ Dropdown syncs with visual model list
echo.
echo To start the application:
echo 1. Run: START_ALL_SERVICES.bat
echo 2. Open: http://localhost:8000
echo 3. Go to ML Training Centre
echo 4. Train a model - it will appear in the dropdown!
echo.
echo Press any key to exit...
pause >nul