@echo off
REM ================================================================================
REM Create Complete Integrated Package with Document Sentiment Analysis
REM ================================================================================

echo.
echo =========================================================================
echo    CREATING INTEGRATED STOCK TRACKER PACKAGE
echo =========================================================================
echo.

REM Set variables
set PACKAGE_NAME=StockTracker_Integrated_v1.0_%DATE:~-4%%DATE:~3,2%%DATE:~0,2%
set PACKAGE_DIR=%PACKAGE_NAME%

REM Create package directory
echo [1/7] Creating package directory: %PACKAGE_DIR%
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\modules"
mkdir "%PACKAGE_DIR%\modules\market-tracking"
mkdir "%PACKAGE_DIR%\static"
mkdir "%PACKAGE_DIR%\static\css"
mkdir "%PACKAGE_DIR%\static\js"

echo.
echo [2/7] Copying backend files...

REM Copy backend files
copy backend_integrated.py "%PACKAGE_DIR%\" >nul 2>&1
if exist backend.py copy backend.py "%PACKAGE_DIR%\backend_original.py" >nul 2>&1
if exist ml_backend_fixed.py copy ml_backend_fixed.py "%PACKAGE_DIR%\" >nul 2>&1
if exist ml_backend_simple.py copy ml_backend_simple.py "%PACKAGE_DIR%\" >nul 2>&1
copy requirements.txt "%PACKAGE_DIR%\" >nul 2>&1

echo Backend files copied

echo.
echo [3/7] Copying frontend files...

REM Copy main HTML files
copy index_integrated.html "%PACKAGE_DIR%\index.html" >nul 2>&1
if exist index.html copy index.html "%PACKAGE_DIR%\index_original.html" >nul 2>&1

echo Frontend files copied

echo.
echo [4/7] Copying integrated modules...

REM Copy integrated modules
copy modules\stock_analysis_integrated.html "%PACKAGE_DIR%\modules\" >nul 2>&1
copy modules\ml_training_integrated.html "%PACKAGE_DIR%\modules\" >nul 2>&1
copy modules\document_uploader.html "%PACKAGE_DIR%\modules\" >nul 2>&1
copy modules\prediction_centre.html "%PACKAGE_DIR%\modules\" >nul 2>&1
copy modules\cba_enhanced.html "%PACKAGE_DIR%\modules\" >nul 2>&1

REM Copy market tracker
if exist market_tracker_final_COMPLETE_FIXED.html (
    copy market_tracker_final_COMPLETE_FIXED.html "%PACKAGE_DIR%\modules\market-tracking\" >nul 2>&1
) else if exist modules\market-tracking\market_tracker_final_COMPLETE_FIXED.html (
    copy modules\market-tracking\market_tracker_final_COMPLETE_FIXED.html "%PACKAGE_DIR%\modules\market-tracking\" >nul 2>&1
)

REM Copy other existing modules
if exist modules\global_market_tracker.html copy modules\global_market_tracker.html "%PACKAGE_DIR%\modules\" >nul 2>&1
if exist modules\indices_tracker_fixed_times.html copy modules\indices_tracker_fixed_times.html "%PACKAGE_DIR%\modules\" >nul 2>&1
if exist modules\technical_analysis.html copy modules\technical_analysis.html "%PACKAGE_DIR%\modules\" >nul 2>&1
if exist modules\stock_tracker.html copy modules\stock_tracker.html "%PACKAGE_DIR%\modules\" >nul 2>&1

echo Modules copied

echo.
echo [5/7] Copying startup scripts...

REM Copy startup scripts
copy START_INTEGRATED_SYSTEM.bat "%PACKAGE_DIR%\START.bat" >nul 2>&1

REM Create additional startup scripts
echo @echo off > "%PACKAGE_DIR%\QUICK_START.bat"
echo echo Starting Integrated Stock Tracker System... >> "%PACKAGE_DIR%\QUICK_START.bat"
echo call START.bat >> "%PACKAGE_DIR%\QUICK_START.bat"

echo Startup scripts created

echo.
echo [6/7] Creating documentation...

REM Create README
echo # Stock Tracker Integrated System > "%PACKAGE_DIR%\README.md"
echo. >> "%PACKAGE_DIR%\README.md"
echo ## Features >> "%PACKAGE_DIR%\README.md"
echo - Document sentiment analysis integration >> "%PACKAGE_DIR%\README.md"
echo - Real-time Yahoo Finance data >> "%PACKAGE_DIR%\README.md"
echo - Sentiment-weighted predictions >> "%PACKAGE_DIR%\README.md"
echo - SQLite database for document-stock linking >> "%PACKAGE_DIR%\README.md"
echo - 100MB document upload limit >> "%PACKAGE_DIR%\README.md"
echo - ADST timezone support >> "%PACKAGE_DIR%\README.md"
echo. >> "%PACKAGE_DIR%\README.md"
echo ## Quick Start >> "%PACKAGE_DIR%\README.md"
echo 1. Double-click START.bat or QUICK_START.bat >> "%PACKAGE_DIR%\README.md"
echo 2. Wait for all services to start >> "%PACKAGE_DIR%\README.md"
echo 3. Open http://localhost:8000 in your browser >> "%PACKAGE_DIR%\README.md"
echo. >> "%PACKAGE_DIR%\README.md"
echo ## Services >> "%PACKAGE_DIR%\README.md"
echo - Frontend: http://localhost:8000 >> "%PACKAGE_DIR%\README.md"
echo - Backend API: http://localhost:8002 >> "%PACKAGE_DIR%\README.md"
echo - ML Service: http://localhost:8003 >> "%PACKAGE_DIR%\README.md"
echo. >> "%PACKAGE_DIR%\README.md"
echo ## Integrated Modules >> "%PACKAGE_DIR%\README.md"
echo - Stock Analysis: Full sentiment integration >> "%PACKAGE_DIR%\README.md"
echo - ML Training Centre: Sentiment-aware model training >> "%PACKAGE_DIR%\README.md"
echo - Document Analyzer: FinBERT-powered analysis >> "%PACKAGE_DIR%\README.md"
echo - Prediction Centre: Sentiment-weighted predictions >> "%PACKAGE_DIR%\README.md"
echo. >> "%PACKAGE_DIR%\README.md"
echo ## Requirements >> "%PACKAGE_DIR%\README.md"
echo - Windows 11 >> "%PACKAGE_DIR%\README.md"
echo - Python 3.8+ >> "%PACKAGE_DIR%\README.md"
echo - Chrome/Edge/Firefox browser >> "%PACKAGE_DIR%\README.md"

echo Documentation created

echo.
echo [7/7] Creating ZIP archive...

REM Check if PowerShell is available for compression
where powershell >nul 2>&1
if %errorlevel% == 0 (
    powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_DIR%.zip' -Force"
    echo Package compressed to %PACKAGE_DIR%.zip
) else (
    echo PowerShell not found, package saved as directory: %PACKAGE_DIR%
)

echo.
echo =========================================================================
echo    INTEGRATED PACKAGE CREATED SUCCESSFULLY
echo =========================================================================
echo.
echo Package Details:
echo   Name: %PACKAGE_DIR%
echo   Location: %CD%\%PACKAGE_DIR%
if exist "%PACKAGE_DIR%.zip" echo   Archive: %CD%\%PACKAGE_DIR%.zip
echo.
echo Key Features:
echo   ✓ Document sentiment analysis fully integrated
echo   ✓ All modules updated with sentiment capabilities
echo   ✓ SQLite database for document storage
echo   ✓ Real Yahoo Finance data only (no fallbacks)
echo   ✓ Windows 11 optimized with localhost hardcoding
echo.
echo To use:
echo   1. Extract the package (if zipped)
echo   2. Navigate to the package directory
echo   3. Run START.bat or QUICK_START.bat
echo   4. Open http://localhost:8000
echo.
echo =========================================================================
echo.

pause