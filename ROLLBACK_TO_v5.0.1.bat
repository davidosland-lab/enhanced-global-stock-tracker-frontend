@echo off
echo ============================================
echo ROLLBACK TO STABLE VERSION 5.0.1
echo ============================================
echo.
echo This script will rollback to the stable v5.0.1 release
echo with all fixes implemented and tested.
echo.
pause

echo.
echo [1/3] Fetching from GitHub...
git fetch origin

echo.
echo [2/3] Rolling back to v5.0.1...
git checkout v5.0.1

echo.
echo [3/3] Verifying rollback...
git status
echo.

echo ============================================
echo ROLLBACK COMPLETE
echo ============================================
echo.
echo You are now on version 5.0.1
echo.
echo To use the system:
echo 1. Extract StockTrackerPro_v5.0.1_FINAL.zip
echo 2. Run INSTALL.bat
echo 3. Run START_ALL_SERVICES.bat
echo 4. Open http://localhost:8000
echo.
pause