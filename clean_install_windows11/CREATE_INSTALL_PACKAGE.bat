@echo off
title Creating Stock Tracker Installation Package
color 0A

echo ===============================================================================
echo                    STOCK TRACKER INSTALLATION PACKAGE CREATOR
echo                         Creating Complete Windows 11 Package
echo ===============================================================================
echo.

:: Create package directory
set PACKAGE_NAME=StockTracker_Windows11_Complete_ML
set PACKAGE_DIR=%PACKAGE_NAME%
set ZIP_NAME=%PACKAGE_NAME%.zip

echo [1/5] Creating package directory structure...
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\modules"
mkdir "%PACKAGE_DIR%\static"
mkdir "%PACKAGE_DIR%\historical_data"

echo.
echo [2/5] Copying core files...
:: Backend files
copy backend.py "%PACKAGE_DIR%\" >nul
copy ml_training_backend.py "%PACKAGE_DIR%\" >nul
copy historical_data_manager.py "%PACKAGE_DIR%\" >nul
copy advanced_ensemble_predictor.py "%PACKAGE_DIR%\" >nul 2>nul
copy advanced_ensemble_backtester.py "%PACKAGE_DIR%\" >nul 2>nul

:: Frontend files
copy index.html "%PACKAGE_DIR%\" >nul
copy WORKING_PREDICTION_MODULE.html "%PACKAGE_DIR%\" >nul

:: Module files
xcopy /q modules\*.html "%PACKAGE_DIR%\modules\" >nul 2>nul

:: Static files
xcopy /q /s static\* "%PACKAGE_DIR%\static\" >nul 2>nul

:: Configuration files
copy requirements_ml.txt "%PACKAGE_DIR%\" >nul
copy package.json "%PACKAGE_DIR%\" >nul 2>nul

:: Launcher and setup files
copy LAUNCH_ALL_SERVICES.bat "%PACKAGE_DIR%\" >nul
copy test_system.py "%PACKAGE_DIR%\" >nul

:: Documentation
copy COMPLETE_DEPLOYMENT_GUIDE.md "%PACKAGE_DIR%\" >nul
copy WINDOWS11_COMPLETE_SOLUTION.md "%PACKAGE_DIR%\" >nul
copy SETUP_INSTRUCTIONS.md "%PACKAGE_DIR%\" >nul 2>nul

echo.
echo [3/5] Creating installer script...
(
echo @echo off
echo title Stock Tracker Complete Installation
echo color 0A
echo.
echo echo ===============================================================================
echo echo                          STOCK TRACKER INSTALLER
echo echo                    Complete System with ML Training Support
echo echo ===============================================================================
echo echo.
echo.
echo :: Check Python
echo python --version ^>nul 2^>^&1
echo if %%errorlevel%% neq 0 ^(
echo     echo [ERROR] Python is not installed!
echo     echo.
echo     echo Please install Python 3.8 or higher from:
echo     echo https://python.org/downloads/
echo     echo.
echo     echo Make sure to check "Add Python to PATH" during installation.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [1/4] Installing Python packages...
echo echo This may take 5-10 minutes on first installation.
echo pip install --quiet --upgrade pip
echo pip install --quiet -r requirements_ml.txt
echo.
echo echo.
echo echo [2/4] Setting up SQLite database...
echo python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('SQLite database initialized')"
echo.
echo echo.
echo echo [3/4] Creating desktop shortcut...
echo powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Stock Tracker.lnk'); $Shortcut.TargetPath = '%CD%\LAUNCH_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Save()"
echo.
echo echo.
echo echo [4/4] Running system test...
echo python test_system.py
echo.
echo echo.
echo echo ===============================================================================
echo echo                         INSTALLATION COMPLETE!
echo echo ===============================================================================
echo echo.
echo echo Installation Summary:
echo echo -------------------
echo echo - Location: %%CD%%
echo echo - Desktop shortcut created
echo echo - All dependencies installed
echo echo - Database initialized
echo echo.
echo echo To start the application:
echo echo 1. Double-click "Stock Tracker" on your desktop
echo echo    OR
echo echo 2. Run LAUNCH_ALL_SERVICES.bat
echo echo.
echo echo The application will open at: http://localhost:8000
echo echo.
echo pause
) > "%PACKAGE_DIR%\INSTALL.bat"

echo.
echo [4/5] Creating uninstaller...
(
echo @echo off
echo title Stock Tracker Uninstaller
echo color 0C
echo.
echo echo ===============================================================================
echo echo                          STOCK TRACKER UNINSTALLER
echo echo ===============================================================================
echo echo.
echo echo This will remove the Stock Tracker desktop shortcut.
echo echo The application files will remain in: %%CD%%
echo echo.
echo set /p confirm="Are you sure you want to uninstall? (Y/N): "
echo if /i "%%confirm%%"=="Y" ^(
echo     echo.
echo     echo Removing desktop shortcut...
echo     del "%%USERPROFILE%%\Desktop\Stock Tracker.lnk" 2^>nul
echo     echo.
echo     echo Uninstall complete.
echo     echo You can safely delete this folder to completely remove the application.
echo ^) else ^(
echo     echo Uninstall cancelled.
echo ^)
echo echo.
echo pause
) > "%PACKAGE_DIR%\UNINSTALL.bat"

echo.
echo [5/5] Creating README...
(
echo # Stock Tracker - Complete Installation Package
echo.
echo ## Quick Install
echo.
echo 1. Extract this folder to your desired location ^(e.g., C:\StockTracker^)
echo 2. Double-click **INSTALL.bat**
echo 3. Wait for installation to complete ^(5-10 minutes first time^)
echo 4. Use the desktop shortcut to launch
echo.
echo ## Package Contents
echo.
echo - **INSTALL.bat** - One-click installer
echo - **LAUNCH_ALL_SERVICES.bat** - Application launcher
echo - **backend.py** - Main backend server
echo - **ml_training_backend.py** - ML training server
echo - **index.html** - Main dashboard
echo - **modules/** - All 6 application modules
echo - **requirements_ml.txt** - Python dependencies
echo.
echo ## Features
echo.
echo - Real-time Yahoo Finance data
echo - 6 professional modules
echo - Real ML model training ^(TensorFlow^)
echo - SQLite for 100x faster backtesting
echo - Windows 11 optimized
echo.
echo ## System Requirements
echo.
echo - Windows 10/11
echo - Python 3.8+
echo - 8GB RAM ^(16GB for ML training^)
echo - 10GB disk space
echo - Internet connection
echo.
echo ## Support
echo.
echo Run **test_system.py** to diagnose any issues.
) > "%PACKAGE_DIR%\README.md"

echo.
echo Package created successfully!
echo.
echo ===============================================================================
echo                            PACKAGE READY
echo ===============================================================================
echo.
echo Package Name: %PACKAGE_DIR%
echo.
echo Next Steps:
echo -----------
echo 1. The package is in the folder: %PACKAGE_DIR%
echo 2. Compress it to a ZIP file for distribution
echo 3. Users just need to:
echo    - Extract the ZIP
echo    - Run INSTALL.bat
echo    - Use desktop shortcut to launch
echo.
echo To create ZIP file now (requires PowerShell):
echo.
set /p createzip="Create ZIP file now? (Y/N): "
if /i "%createzip%"=="Y" (
    echo Creating ZIP file...
    powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%ZIP_NAME%' -Force"
    echo.
    echo ZIP file created: %ZIP_NAME%
    echo Size: 
    for %%A in ("%ZIP_NAME%") do echo %%~zA bytes
)
echo.
pause