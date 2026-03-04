@echo off
title FinBERT v3.3 Installation
color 0A
cls

echo ================================================================================
echo                     FinBERT Ultimate Trading System v3.3                       
echo                            INSTALLATION WIZARD                                 
echo ================================================================================
echo.
echo This installer will set up the FinBERT Trading System on your Windows machine.
echo.
echo Requirements:
echo - Python 3.8 or higher
echo - Internet connection for market data
echo - Windows 10/11
echo.
pause

REM Check if Python is installed
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo Python found successfully!
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Warning: Could not activate virtual environment, continuing with global Python...
)
echo.

REM Install required packages
echo [4/5] Installing required packages...
echo.
echo Installing Flask...
pip install flask --quiet --disable-pip-version-check
if errorlevel 1 (
    echo Retrying Flask installation...
    python -m pip install flask --user
)

echo Installing Flask-CORS...
pip install flask-cors --quiet --disable-pip-version-check
if errorlevel 1 (
    echo Retrying Flask-CORS installation...
    python -m pip install flask-cors --user
)

echo Installing NumPy...
pip install numpy --quiet --disable-pip-version-check
if errorlevel 1 (
    echo Retrying NumPy installation...
    python -m pip install numpy --user
)

echo.
echo All packages installed successfully!
echo.

REM Check if files exist
echo [5/5] Verifying installation files...
set missing_files=0

if not exist "app_finbert_predictions_clean.py" (
    echo ERROR: app_finbert_predictions_clean.py not found!
    set missing_files=1
)

if not exist "finbert_charts_complete.html" (
    echo ERROR: finbert_charts_complete.html not found!
    set missing_files=1
)

if %missing_files%==1 (
    color 0C
    echo.
    echo ERROR: Required files are missing!
    echo Please ensure all files are extracted to the same directory.
    pause
    exit /b 1
)

echo All files verified successfully!
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
set SCRIPT_PATH=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\FinBERT Trading System.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_PATH%START_SYSTEM.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_PATH%" >> CreateShortcut.vbs
echo oLink.IconLocation = "cmd.exe" >> CreateShortcut.vbs
echo oLink.Description = "Launch FinBERT Trading System" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

color 0A
echo.
echo ================================================================================
echo                        INSTALLATION COMPLETE!                                  
echo ================================================================================
echo.
echo FinBERT v3.3 has been successfully installed!
echo.
echo A desktop shortcut has been created: "FinBERT Trading System"
echo.
echo To start the system:
echo   1. Double-click the desktop shortcut, OR
echo   2. Run START_SYSTEM.bat from this directory
echo.
echo The system will open in your browser at: http://localhost:5000
echo.
echo Press any key to launch FinBERT now...
pause >nul

REM Launch the system
call START_SYSTEM.bat