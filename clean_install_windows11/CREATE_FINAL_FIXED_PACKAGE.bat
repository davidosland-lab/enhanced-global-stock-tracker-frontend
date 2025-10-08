@echo off
echo ============================================
echo Creating Final Fixed Package
echo ============================================
echo.

REM Create package directory
set PACKAGE_NAME=StockTracker_Fixed_Health_Endpoint_%DATE:~-4%%DATE:~4,2%%DATE:~7,2%
mkdir "%PACKAGE_NAME%" 2>nul

echo Copying fixed files...

REM Copy main files
copy backend.py "%PACKAGE_NAME%\" >nul
copy ml_backend_fixed.py "%PACKAGE_NAME%\" >nul
copy index.html "%PACKAGE_NAME%\" >nul
copy requirements.txt "%PACKAGE_NAME%\" >nul

REM Copy startup scripts
copy START_ALL_SERVICES_FIXED.bat "%PACKAGE_NAME%\" >nul
copy START_FIXED_SERVICES.bat "%PACKAGE_NAME%\" >nul
copy RESTART_BACKEND_WITH_HEALTH.bat "%PACKAGE_NAME%\" >nul
copy TEST_HEALTH_ENDPOINT.bat "%PACKAGE_NAME%\" >nul

REM Copy fix scripts
copy FIX_BACKEND_HEALTH_ENDPOINT.py "%PACKAGE_NAME%\" >nul

REM Copy modules directory
xcopy /E /I /Q modules "%PACKAGE_NAME%\modules" >nul

REM Create README
echo Creating README...
(
echo STOCK TRACKER - FIXED VERSION WITH HEALTH ENDPOINT
echo ==================================================
echo.
echo This package includes the fix for "Backend Status: Disconnected" issue.
echo.
echo WHAT WAS FIXED:
echo - Added missing /api/health endpoint to backend.py
echo - Ensures frontend can properly check backend connectivity
echo - All API calls hardcoded to localhost for Windows compatibility
echo.
echo TO START ALL SERVICES:
echo   Run: START_ALL_SERVICES_FIXED.bat
echo.
echo TO TEST HEALTH ENDPOINT:
echo   Run: TEST_HEALTH_ENDPOINT.bat
echo.
echo SERVICE URLS:
echo   - Frontend: http://localhost:8000
echo   - Backend API: http://localhost:8002
echo   - ML Backend: http://localhost:8003
echo.
echo FIXED ISSUES:
echo   1. Backend Status now shows "Connected" instead of "Disconnected"
echo   2. No more 404 errors for /api/health endpoint
echo   3. All modules use hardcoded localhost URLs
echo   4. ML Training Centre properly connects to ML backend
echo   5. Trained models appear in prediction dropdown
echo.
echo Files Included:
echo   - backend.py (with health endpoint)
echo   - ml_backend_fixed.py (with all required endpoints)
echo   - All 27 HTML modules with localhost hardcoding
echo   - Batch scripts for easy Windows startup
echo.
) > "%PACKAGE_NAME%\README.txt"

echo Package created: %PACKAGE_NAME%
echo.
pause