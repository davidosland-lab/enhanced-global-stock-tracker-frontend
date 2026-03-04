@echo off
REM ============================================================================
REM ASX Chart Fix Patch - v1.3.15.24
REM ============================================================================
REM
REM This patch fixes the ASX All Ordinaries chart to show correct market hours
REM (23:00-05:00 GMT instead of 00:00-06:00 GMT) and eliminates the flat line
REM at 0% issue.
REM
REM What this patch does:
REM   - Backs up your current unified_trading_dashboard.py
REM   - Replaces it with the fixed version
REM   - No need to reinstall the entire package!
REM
REM ============================================================================

echo.
echo ============================================================================
echo   ASX CHART FIX PATCH - v1.3.15.24
echo ============================================================================
echo.
echo This patch will fix the ASX All Ordinaries chart issue.
echo.
echo [!] IMPORTANT: Make sure the dashboard is NOT running before applying patch!
echo.
pause

REM Check if we're in the right directory
if not exist "unified_trading_dashboard.py" (
    echo.
    echo [X] ERROR: unified_trading_dashboard.py not found!
    echo.
    echo Please run this patch from your installation directory:
    echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\
    echo.
    pause
    exit /b 1
)

echo.
echo [1/3] Creating backup...
REM Create simple timestamp without special characters
set BACKUP_NAME=unified_trading_dashboard.py.backup
copy /Y unified_trading_dashboard.py "%BACKUP_NAME%"
if errorlevel 1 (
    echo [X] Backup failed!
    pause
    exit /b 1
)
echo [OK] Backup created: %BACKUP_NAME%

echo.
echo [2/3] Checking patch file exists...
if not exist "patch_v1.3.15.24\unified_trading_dashboard.py" (
    echo [X] Patch file not found! 
    echo Please make sure you extracted the patch ZIP in the correct location.
    pause
    exit /b 1
)
echo [OK] Patch file found

echo.
echo [3/3] Applying patch...
copy /Y "patch_v1.3.15.24\unified_trading_dashboard.py" unified_trading_dashboard.py
if errorlevel 1 (
    echo [X] Patch failed!
    echo Restoring backup...
    copy /Y "%BACKUP_NAME%" unified_trading_dashboard.py
    pause
    exit /b 1
)

REM Verify Python syntax
echo.
echo [4/4] Verifying Python syntax...
python -m py_compile unified_trading_dashboard.py
if errorlevel 1 (
    echo [X] Syntax error! Rolling back...
    copy /Y "%BACKUP_NAME%" unified_trading_dashboard.py
    pause
    exit /b 1
)
echo [OK] Syntax check passed

echo.
echo ============================================================================
echo   PATCH APPLIED SUCCESSFULLY!
echo ============================================================================
echo.
echo Changes made:
echo   - ASX market hours updated: 23:00-05:00 GMT (was 00:00-06:00)
echo   - Added midnight-spanning session logic
echo   - ASX chart will now show correct data throughout trading day
echo.
echo Next steps:
echo   1. Restart the dashboard: LAUNCH_COMPLETE_SYSTEM.bat -^> Option 7
echo   2. Open browser: http://localhost:8050
echo   3. The ASX All Ords line will now show correctly!
echo.
echo Backup location: %BACKUP_NAME%
echo (You can restore from backup if needed)
echo.
echo ============================================================================
pause
