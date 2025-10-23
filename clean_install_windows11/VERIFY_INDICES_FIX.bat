@echo off
echo ============================================
echo VERIFYING INDICES TRACKER FIX
echo ============================================
echo.

cd /D "%~dp0\modules"

echo Checking if fixed file exists...
if exist "indices_tracker_fixed_times.html" (
    echo [OK] Fixed version exists
) else (
    echo [ERROR] Fixed version not found!
    pause
    exit /b 1
)

echo.
echo Checking current indices_tracker.html...
findstr /C:"ADST" indices_tracker.html >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Current tracker mentions ADST - Fix is applied!
    echo.
    echo The Global Indices Tracker should now show:
    echo   - Times in ADST timezone
    echo   - ASX: 10:00-16:00
    echo   - FTSE: 19:00-03:30
    echo   - SP500: 01:30-08:00
) else (
    echo [WARNING] Current tracker doesn't mention ADST
    echo.
    echo Applying fix now...
    copy /Y indices_tracker_fixed_times.html indices_tracker.html
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Fix applied successfully!
    ) else (
        echo [ERROR] Could not apply fix
        echo.
        echo Please manually copy:
        echo   indices_tracker_fixed_times.html
        echo to:
        echo   indices_tracker.html
    )
)

echo.
echo ============================================
echo Next Steps:
echo 1. Go to http://localhost:8000
echo 2. Open Global Indices Tracker
echo 3. Verify times show in ADST
echo ============================================
echo.
pause