@echo off
cls
echo ============================================================
echo Creating Stock Tracker Windows Package
echo ============================================================
echo.

REM Create a clean package directory
if exist StockTracker_Windows rmdir /s /q StockTracker_Windows
mkdir StockTracker_Windows
mkdir StockTracker_Windows\modules
mkdir StockTracker_Windows\modules\market-tracking
mkdir StockTracker_Windows\modules\analysis
mkdir StockTracker_Windows\modules\predictions

echo Copying files...
echo.

REM Copy batch files
echo Copying startup scripts...
copy START_FIXED_SERVICES.bat StockTracker_Windows\ >nul
copy STOP_ALL.bat StockTracker_Windows\ >nul
copy INSTALL_REQUIREMENTS.bat StockTracker_Windows\ >nul
copy README_WINDOWS.txt StockTracker_Windows\ >nul

REM Copy backend files
echo Copying backend files...
if exist backend_working_before_ml_fix.py (
    copy backend_working_before_ml_fix.py StockTracker_Windows\backend.py >nul
) else (
    copy backend.py StockTracker_Windows\ >nul
)
copy ml_backend_fixed.py StockTracker_Windows\ >nul

REM Copy main index
echo Copying index file...
copy index.html StockTracker_Windows\ >nul

REM Copy module files
echo Copying module files...
copy modules\*.html StockTracker_Windows\modules\ >nul 2>nul

REM Copy market tracking
if exist modules\market-tracking\market_tracker_final.html (
    copy modules\market-tracking\market_tracker_final.html StockTracker_Windows\modules\market-tracking\ >nul
)

REM Copy analysis modules
if exist modules\analysis\cba_analysis_enhanced.html (
    copy modules\analysis\cba_analysis_enhanced.html StockTracker_Windows\modules\analysis\ >nul
)

REM Copy predictions modules  
if exist modules\predictions\prediction_centre_real_ml.html (
    copy modules\predictions\prediction_centre_real_ml.html StockTracker_Windows\modules\predictions\ >nul
)

echo.
echo Package created in: StockTracker_Windows\
echo.
echo To deploy:
echo 1. Copy the StockTracker_Windows folder to your desired location
echo 2. Run INSTALL_REQUIREMENTS.bat (first time only)
echo 3. Run START_FIXED_SERVICES.bat to start the application
echo.
pause
