@echo off
title Stock Tracker Professional Installer
color 0A
cls

echo ===============================================================================
echo                       STOCK TRACKER PROFESSIONAL
echo                    Complete System with ML Training
echo ===============================================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.8+ from: https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

:: Install packages
echo [1/5] Installing Python packages (5-10 minutes)...
pip install --upgrade pip --quiet
pip install -r requirements_ml.txt --quiet

echo.
echo [2/5] Initializing database...
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager()"

echo.
echo [3/5] Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Stock Tracker.lnk'); $Shortcut.TargetPath = '%CD%\LAUNCH_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Save()"

echo.
echo [4/5] Running system test...
python test_system.py

echo.
echo [5/5] Installation complete!
echo.
echo ===============================================================================
echo                         INSTALLATION SUCCESSFUL!
echo ===============================================================================
echo.
echo Desktop shortcut created: Stock Tracker
echo.
echo To launch: Double-click the desktop shortcut
echo           OR run LAUNCH_ALL_SERVICES.bat
echo.
echo Application URL: http://localhost:8000
echo.
set /p launch="Launch Stock Tracker now? (Y/N): "
if /i "%launch%"=="Y" (
    start "" "LAUNCH_ALL_SERVICES.bat"
)
pause