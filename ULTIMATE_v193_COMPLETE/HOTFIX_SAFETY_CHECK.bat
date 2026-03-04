@echo off
REM ============================================================================
REM  HOTFIX v1.3.15.115 - Pre-Installation Safety Check
REM ============================================================================
REM
REM  Purpose: Verify system is ready for hotfix installation
REM  Run this BEFORE applying hotfix
REM
REM ============================================================================

echo.
echo ============================================================================
echo  HOTFIX v1.3.15.115 - Pre-Installation Safety Check
echo ============================================================================
echo.
echo  This will verify your system is ready for the hotfix.
echo  No changes will be made.
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set CHECK_PASSED=1

REM Check 1: Verify we're in the correct directory
echo [CHECK 1/8] Verifying installation directory...
if exist "pipelines\models\screening\report_generator.py" (
    echo [OK] Found report_generator.py
) else (
    echo [FAIL] Cannot find report_generator.py
    echo Are you in the unified_trading_dashboard folder?
    set CHECK_PASSED=0
)

echo.
REM Check 2: Check if file is writable
echo [CHECK 2/8] Checking file permissions...
copy "pipelines\models\screening\report_generator.py" "pipelines\models\screening\report_generator.py.test" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    del "pipelines\models\screening\report_generator.py.test" >nul 2>&1
    echo [OK] File is writable
) else (
    echo [WARNING] File may not be writable
    echo Try running as Administrator
)

echo.
REM Check 3: Check Python is available
echo [CHECK 3/8] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python --version
    echo [OK] Python is available
) else (
    echo [WARNING] Python not found in PATH
    echo This may affect dashboard functionality
)

echo.
REM Check 4: Check if dashboard is running
echo [CHECK 4/8] Checking if trading dashboard is running...
tasklist /FI "WINDOWTITLE eq Unified Trading Dashboard*" 2>nul | find /I "cmd.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Trading dashboard appears to be running
    echo [OK] Hotfix can be applied without stopping it
) else (
    echo [INFO] Trading dashboard not detected as running
    echo [OK] Can apply hotfix anytime
)

echo.
REM Check 5: Check disk space
echo [CHECK 5/8] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%a
echo Free space: %FREE_SPACE% bytes
if %FREE_SPACE% GTR 10000000 (
    echo [OK] Sufficient disk space
) else (
    echo [WARNING] Low disk space detected
)

echo.
REM Check 6: Check if hotfix already applied
echo [CHECK 6/8] Checking if hotfix already applied...
findstr /C:"parent.parent.parent.parent" "pipelines\models\screening\report_generator.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Hotfix may already be applied
    echo Applying again is safe (idempotent) but may not be necessary
) else (
    echo [OK] Hotfix not yet applied
)

echo.
REM Check 7: Check backup directory
echo [CHECK 7/8] Checking backup directory...
if exist "backups" (
    echo [OK] Backup directory exists
    dir /b "backups\report_generator.py.backup_*" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Previous backups found:
        dir /b "backups\report_generator.py.backup_*"
    )
) else (
    echo [INFO] Backup directory will be created
)

echo.
REM Check 8: Check report directories
echo [CHECK 8/8] Checking report directory structure...
if exist "reports" (
    echo [OK] Root reports\ directory exists
) else (
    echo [INFO] Root reports\ directory will be created
)

if exist "pipelines\reports\morning_reports" (
    echo [INFO] Old report location exists
    dir "pipelines\reports\morning_reports\*.html" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] HTML reports found in old location (will be moved)
    )
)

echo.
echo ============================================================================
echo  SAFETY CHECK SUMMARY
echo ============================================================================
echo.

if %CHECK_PASSED% EQU 1 (
    echo  Result: PASSED
    echo.
    echo  Your system is ready for hotfix installation!
    echo.
    echo  Next Steps:
    echo    1. Run APPLY_HOTFIX_v1.3.15.115.bat (as Administrator)
    echo    2. Wait for completion (~10 seconds)
    echo    3. Run HOTFIX_VALIDATION.bat to verify
    echo.
    echo  Remember:
    echo    - No need to stop trading dashboard
    echo    - Automatic backup will be created
    echo    - Fix takes effect on NEXT pipeline run
    echo.
) else (
    echo  Result: WARNINGS DETECTED
    echo.
    echo  Please address the issues above before applying hotfix.
    echo.
    echo  Common solutions:
    echo    - Run as Administrator (for file permissions)
    echo    - Navigate to correct directory
    echo    - Free up disk space if needed
    echo.
)

echo ============================================================================
echo.

REM Display system information
echo Additional System Information:
echo   Current Directory: %CD%
echo   Date/Time: %DATE% %TIME%
echo   User: %USERNAME%
echo   Computer: %COMPUTERNAME%
echo.

pause
