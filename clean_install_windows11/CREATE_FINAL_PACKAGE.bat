@echo off
REM ====================================================
REM Create Final Deployment Package - Version 6.0
REM All fixes applied, localhost hardcoded, no fallbacks
REM ====================================================

echo Creating Stock Tracker v6.0 Final Package...
echo.

REM Create package directory
set PACKAGE_NAME=StockTracker_v6.0_FINAL_LOCALHOST_ONLY
if exist %PACKAGE_NAME% rmdir /s /q %PACKAGE_NAME%
mkdir %PACKAGE_NAME%

REM Copy all essential files
echo Copying application files...
copy index.html %PACKAGE_NAME%\ >nul
copy backend.py %PACKAGE_NAME%\ >nul
copy backend_ml_fixed.py %PACKAGE_NAME%\ >nul
copy requirements.txt %PACKAGE_NAME%\ >nul
copy error_handler.js %PACKAGE_NAME%\ >nul

REM Copy batch files
echo Copying startup scripts...
copy START_STOCK_TRACKER.bat %PACKAGE_NAME%\ >nul
copy SHUTDOWN_ALL.bat %PACKAGE_NAME%\ >nul
copy TEST_SERVICES.bat %PACKAGE_NAME%\ >nul
copy TEST_CBA_PRICE.html %PACKAGE_NAME%\ >nul

REM Copy modules
echo Copying modules...
xcopy /s /q modules %PACKAGE_NAME%\modules\ >nul

REM Copy static files
if exist static (
    echo Copying static files...
    xcopy /s /q static %PACKAGE_NAME%\static\ >nul
)

REM Create README
echo Creating documentation...
(
echo Stock Tracker v6.0 - FINAL VERSION
echo =====================================
echo.
echo INSTALLATION:
echo 1. Extract this folder to any location
echo 2. Ensure Python 3.8+ is installed
echo 3. Double-click START_STOCK_TRACKER.bat
echo.
echo FEATURES:
echo - All services hardcoded to localhost
echo - NO synthetic/demo/fallback data
echo - Real Yahoo Finance data only
echo - CBA.AX shows real price ~$170
echo - Upload limit: 100MB
echo - All ML Backend issues fixed
echo.
echo SERVICES:
echo - Frontend: http://localhost:8000
echo - Backend API: http://localhost:8002
echo - ML Backend: http://localhost:8003
echo.
echo TO START:
echo - Double-click START_STOCK_TRACKER.bat
echo.
echo TO STOP:
echo - Run SHUTDOWN_ALL.bat
echo.
echo TO TEST:
echo - Run TEST_SERVICES.bat
echo - Open TEST_CBA_PRICE.html
echo.
echo TROUBLESHOOTING:
echo - If port in use: Run SHUTDOWN_ALL.bat first
echo - If module errors: Check all 3 services are running
echo - If no data: Check internet connection
echo.
echo Version 6.0 - %date%
) > %PACKAGE_NAME%\README.txt

REM Create the zip file
echo.
echo Creating zip archive...
powershell -Command "Compress-Archive -Path '%PACKAGE_NAME%' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

echo.
echo ====================================================
echo Package created successfully!
echo File: %PACKAGE_NAME%.zip
echo ====================================================
echo.
pause