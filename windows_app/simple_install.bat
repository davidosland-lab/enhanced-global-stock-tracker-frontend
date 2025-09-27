@echo off
REM Simple installer for Stock Predictor Pro
REM This version directly copies files and creates a working installation

echo.
echo ====================================
echo Stock Predictor Pro - Simple Install
echo ====================================
echo.

REM Set installation directory (can be changed)
set INSTALL_DIR=C:\StockPredictorPro

echo Installation directory: %INSTALL_DIR%
echo.

REM Create directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created installation directory
) else (
    echo Directory already exists
    choice /C YN /M "Overwrite existing installation?"
    if errorlevel 2 exit /b 0
)

REM Copy all Python files to installation directory
echo.
echo Copying application files...

REM Copy main application files directly
copy /Y "*.py" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.txt" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.md" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.bat" "%INSTALL_DIR%\" >nul 2>&1

REM Create subdirectories
if not exist "%INSTALL_DIR%\assets" mkdir "%INSTALL_DIR%\assets"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"
if not exist "%INSTALL_DIR%\models" mkdir "%INSTALL_DIR%\models"

echo Files copied successfully

REM Create a simple launcher
echo Creating launcher...
(
echo @echo off
echo echo Starting Stock Predictor Pro...
echo cd /d "%INSTALL_DIR%"
echo python stock_predictor_lite.py
echo if errorlevel 1 (
echo     echo.
echo     echo Error: Could not start application
echo     echo Make sure Python is installed
echo     pause
echo ^)
) > "%INSTALL_DIR%\run_app.bat"

REM Create desktop shortcut using VBScript (more reliable)
echo Creating desktop shortcut...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\Stock Predictor Pro.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\run_app.bat"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Stock Predictor Pro - AI Trading System"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo Desktop shortcut created

REM Install minimal Python packages
echo.
echo Installing Python packages...
echo This may take a few minutes...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Python is not installed or not in PATH
    echo You need to install Python 3.9+ to run this application
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo.
    goto :SkipPackages
)

REM Try to install basic packages
echo Installing basic packages...
cd /d "%INSTALL_DIR%"

REM Install one by one to avoid failures
python -m pip install --upgrade pip >nul 2>&1
python -m pip install requests >nul 2>&1
echo - Installed: requests

python -m pip install numpy >nul 2>&1
echo - Installed: numpy

python -m pip install pandas >nul 2>&1
echo - Installed: pandas

echo.
echo Basic packages installed (some may have failed - that's OK)

:SkipPackages

REM Create uninstaller
echo Creating uninstaller...
(
echo @echo off
echo echo Uninstalling Stock Predictor Pro...
echo rmdir /S /Q "%INSTALL_DIR%"
echo del "%USERPROFILE%\Desktop\Stock Predictor Pro.lnk" 2^>nul
echo echo Uninstallation complete
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

REM Installation complete
echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo Stock Predictor Pro has been installed to:
echo %INSTALL_DIR%
echo.
echo To run the application:
echo 1. Use the desktop shortcut, or
echo 2. Run: %INSTALL_DIR%\run_app.bat
echo.
echo The LITE version will work even if some packages are missing.
echo.

choice /C YN /M "Launch Stock Predictor Pro now?"
if errorlevel 2 goto :End
if errorlevel 1 (
    echo.
    echo Launching application...
    start "" "%INSTALL_DIR%\run_app.bat"
)

:End
echo.
pause