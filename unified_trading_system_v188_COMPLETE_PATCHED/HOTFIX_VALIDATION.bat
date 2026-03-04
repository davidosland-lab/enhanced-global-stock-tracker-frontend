@echo off
REM ============================================================================
REM  Hotfix v1.3.15.115 Validation Script
REM ============================================================================
REM
REM  Purpose: Verify hotfix was applied correctly
REM  Run this AFTER applying hotfix to confirm success
REM
REM ============================================================================

echo.
echo ============================================================================
echo  Hotfix v1.3.15.115 - Validation Check
echo ============================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set VALIDATION_PASSED=1

REM Check 1: Verify report_generator.py has the fix
echo [CHECK 1/5] Verifying report_generator.py fix...
findstr /C:"parent.parent.parent.parent" "pipelines\models\screening\report_generator.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] report_generator.py has correct path calculation
) else (
    echo [FAIL] report_generator.py does NOT have the fix
    set VALIDATION_PASSED=0
)

echo.
REM Check 2: Verify backup exists
echo [CHECK 2/5] Checking for backup file...
if exist "backups\report_generator.py.backup_*" (
    echo [OK] Backup file found in backups\ folder
) else (
    echo [WARNING] No backup file found (may not have been created yet)
)

echo.
REM Check 3: Verify report directories
echo [CHECK 3/5] Checking report directory structure...
if exist "reports" (
    echo [OK] Root reports\ directory exists
) else (
    echo [INFO] Root reports\ directory will be created on next pipeline run
)

if exist "reports\morning_reports" (
    echo [OK] reports\morning_reports\ directory exists
) else (
    echo [INFO] reports\morning_reports\ will be created on next pipeline run
)

echo.
REM Check 4: Check for files in old location
echo [CHECK 4/5] Checking for reports in old location...
if exist "pipelines\reports\morning_reports\*.html" (
    echo [INFO] HTML reports still exist in old location (pipelines\reports\morning_reports\)
    echo [INFO] These should be moved to reports\morning_reports\
) else (
    echo [OK] No HTML reports in old location
)

echo.
REM Check 5: Check VERSION.md
echo [CHECK 5/5] Checking VERSION.md for hotfix entry...
if exist "VERSION.md" (
    findstr /C:"v1.3.15.115" "VERSION.md" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] VERSION.md shows v1.3.15.115
    ) else (
        echo [INFO] VERSION.md may need updating
    )
) else (
    echo [INFO] VERSION.md not found
)

echo.
echo ============================================================================
echo  VALIDATION SUMMARY
echo ============================================================================
echo.

if %VALIDATION_PASSED% EQU 1 (
    echo  Result: PASSED
    echo.
    echo  Hotfix v1.3.15.115 is correctly installed!
    echo.
    echo  Next Steps:
    echo    1. Trading dashboard can continue running
    echo    2. Wait for next pipeline run
    echo    3. Check reports\morning_reports\ for new HTML reports
    echo.
) else (
    echo  Result: FAILED
    echo.
    echo  Hotfix may not be correctly installed.
    echo.
    echo  Recommended Actions:
    echo    1. Re-run APPLY_HOTFIX_v1.3.15.115.bat
    echo    2. Check for errors during application
    echo    3. Manually verify pipelines\models\screening\report_generator.py line 54
    echo.
)

echo ============================================================================
echo.
pause
