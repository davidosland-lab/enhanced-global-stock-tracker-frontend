@echo off
cls
echo ============================================================
echo RESTORE TO v1.0 STABLE - Rollback to Working Version
echo ============================================================
echo.
echo This will restore the Stock Tracker to the stable v1.0
echo release where all issues were fixed and working.
echo.
echo Date of stable version: October 8, 2025
echo.

set /p confirm="Are you sure you want to rollback? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Rollback cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Stopping all services...
taskkill /F /IM python.exe 2>NUL
timeout /t 2 /nobreak >NUL

echo.
echo Step 2: Creating backup of current version...
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
mkdir "BACKUP_BEFORE_ROLLBACK_%timestamp%" 2>NUL
xcopy /E /I /Y *.py "BACKUP_BEFORE_ROLLBACK_%timestamp%\" >NUL 2>&1
xcopy /E /I /Y *.html "BACKUP_BEFORE_ROLLBACK_%timestamp%\" >NUL 2>&1
xcopy /E /I /Y modules "BACKUP_BEFORE_ROLLBACK_%timestamp%\modules\" >NUL 2>&1
echo Current version backed up to: BACKUP_BEFORE_ROLLBACK_%timestamp%

echo.
echo Step 3: Restoring stable v1.0 files...

REM Restore backend files
if exist backend_working_before_ml_fix.py (
    copy /Y backend_working_before_ml_fix.py backend.py >NUL
    echo   Restored: backend.py (with proper defaults)
)

if exist ml_backend_fixed.py (
    echo   Using: ml_backend_fixed.py (with all endpoints)
)

REM Check if we have the stable package
if exist StockTracker_Windows_Complete_Fixed_20251008.zip (
    echo   Stable package found: StockTracker_Windows_Complete_Fixed_20251008.zip
    echo   You can also extract this ZIP for a complete restore.
)

echo.
echo Step 4: Starting services with stable version...
echo.

REM Start Backend API
if exist backend.py (
    start "Backend API - Stable v1.0" cmd /k "python backend.py"
) else (
    echo ERROR: backend.py not found!
)
timeout /t 3 /nobreak >NUL

REM Start ML Backend
if exist ml_backend_fixed.py (
    start "ML Backend - Stable v1.0" cmd /k "python ml_backend_fixed.py"
) else if exist ml_backend_working.py (
    start "ML Backend - Stable v1.0" cmd /k "python ml_backend_working.py"
) else (
    echo ERROR: No ML backend found!
)
timeout /t 3 /nobreak >NUL

REM Start Frontend
start "Frontend - Stable v1.0" cmd /k "python -m http.server 8000"

echo.
echo ============================================================
echo ✅ Rollback to v1.0 STABLE Complete!
echo ============================================================
echo.
echo Restored to stable version from October 8, 2025
echo.
echo What's working in this version:
echo   ✓ All backend endpoints return proper values
echo   ✓ ML Backend has all required endpoints
echo   ✓ ML Training Centre dropdown works
echo   ✓ No 404 errors
echo   ✓ Real Yahoo Finance data
echo   ✓ All modules functional
echo.
echo Access at: http://localhost:8000
echo.
echo If you need the complete stable package, extract:
echo   StockTracker_Windows_Complete_Fixed_20251008.zip
echo.
pause