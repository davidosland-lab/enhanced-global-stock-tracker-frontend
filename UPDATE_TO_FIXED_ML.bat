@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo UPDATING TO FIXED ML VERSION
echo ===============================================================================
echo.

:: Check if the fixed file exists
if not exist "app_unified_robust_fixed.py" (
    echo ERROR: app_unified_robust_fixed.py not found!
    echo Please ensure you have downloaded the fixed version.
    echo.
    pause
    exit /b 1
)

:: Backup the original if it exists
if exist "app_unified_robust.py" (
    echo Creating backup of original file...
    copy "app_unified_robust.py" "app_unified_robust_backup.py" >nul
    echo Backup saved as: app_unified_robust_backup.py
    echo.
)

:: Copy fixed version to main file
echo Updating to fixed ML version...
copy "app_unified_robust_fixed.py" "app_unified_robust.py" >nul

if %errorlevel% eq 0 (
    echo ===============================================================================
    echo UPDATE SUCCESSFUL!
    echo ===============================================================================
    echo.
    echo The ML predictions have been fixed. Changes include:
    echo   - Fixed JavaScript tab switching error
    echo   - Improved ML model training
    echo   - Better error handling
    echo   - Enhanced prediction display with price ranges
    echo   - ML status indicator in header
    echo.
    echo You can now run the application using your existing batch files:
    echo   - QUICK_START_UNIFIED.bat
    echo   - RUN_UNIFIED_ROBUST.bat
    echo.
    echo Original file backed up as: app_unified_robust_backup.py
    echo ===============================================================================
) else (
    echo ERROR: Failed to update file
    echo Please check file permissions
)

echo.
pause