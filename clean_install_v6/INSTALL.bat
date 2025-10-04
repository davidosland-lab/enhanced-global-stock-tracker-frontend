@echo off
title Stock Market Dashboard - Installation
color 0B

echo ============================================
echo   STOCK MARKET DASHBOARD - INSTALLER v6.0
echo ============================================
echo.
echo This will install all required Python packages
echo and set up the Stock Market Dashboard
echo.
echo Press any key to continue or close to cancel...
pause > nul

echo.
echo [1] Checking Python Installation...
echo ============================================
python --version 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.7 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found successfully!
echo.

echo [2] Installing Required Packages...
echo ============================================
echo Installing yfinance...
pip install yfinance --quiet --disable-pip-version-check

echo Installing fastapi...
pip install fastapi --quiet --disable-pip-version-check

echo Installing uvicorn...
pip install uvicorn --quiet --disable-pip-version-check

echo Installing supporting packages...
pip install python-multipart cachetools pandas pytz numpy --quiet --disable-pip-version-check

echo.
echo [3] Verifying Installation...
echo ============================================
python -c "import yfinance, fastapi, uvicorn; print('All packages installed successfully!')"
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Some packages failed to install
    echo Trying alternative installation method...
    pip install -r requirements.txt
)

echo.
echo [4] Creating Desktop Shortcut...
echo ============================================
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Stock Dashboard.lnk'); $SC.TargetPath = '%CD%\QUICK_START.bat'; $SC.WorkingDirectory = '%CD%'; $SC.IconLocation = '%windir%\System32\shell32.dll,13'; $SC.Save()"
echo Desktop shortcut created!

echo.
color 0A
echo ============================================
echo    INSTALLATION COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo You can now:
echo 1. Double-click "QUICK_START.bat" to launch
echo 2. Or use the desktop shortcut "Stock Dashboard"
echo.
echo Press any key to launch the dashboard now...
pause > nul

call QUICK_START.bat