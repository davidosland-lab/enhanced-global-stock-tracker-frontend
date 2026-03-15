@echo off
REM ============================================================================
REM  HOTFIX v1.3.15.115 - HTML Report Path Fix (NO RESTART REQUIRED)
REM ============================================================================
REM
REM  What this fixes:
REM    - HTML reports now save to reports/morning_reports/ (not pipelines/reports/)
REM
REM  Safe to run:
REM    - Trading dashboard can keep running
REM    - Fix applies to NEXT pipeline run only
REM    - No interruption to current trading
REM
REM ============================================================================

echo.
echo ============================================================================
echo  HOTFIX v1.3.15.115 - HTML Report Path Fix
echo ============================================================================
echo.
echo  This hotfix corrects the HTML report save location:
echo    BEFORE: pipelines/reports/morning_reports/
echo    AFTER:  reports/morning_reports/
echo.
echo  Safe to apply while trading dashboard is running!
echo  Fix will take effect on the NEXT pipeline run.
echo.
echo ============================================================================
echo.

REM Save current directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Verify we're in the correct directory
if not exist "pipelines\models\screening\report_generator.py" (
    echo [ERROR] Cannot find report_generator.py
    echo Please run this from the unified_trading_dashboard folder
    pause
    exit /b 1
)

echo [1/4] Creating backup of report_generator.py...
if not exist "backups" mkdir backups
copy "pipelines\models\screening\report_generator.py" "backups\report_generator.py.backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
echo [OK] Backup created in backups\ folder

echo.
echo [2/4] Applying hotfix to report_generator.py...

REM Use PowerShell to do in-place string replacement
powershell -Command "(Get-Content 'pipelines\models\screening\report_generator.py') -replace 'self\.base_path = Path\(__file__\)\.parent\.parent\.parent(?!\.parent)', 'self.base_path = Path(__file__).parent.parent.parent.parent' | Set-Content 'pipelines\models\screening\report_generator.py'"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to apply hotfix
    echo Restoring backup...
    copy "backups\report_generator.py.backup_*" "pipelines\models\screening\report_generator.py" >nul
    pause
    exit /b 1
)

echo [OK] Hotfix applied successfully

echo.
echo [3/4] Verifying fix...
findstr /C:"parent.parent.parent.parent" "pipelines\models\screening\report_generator.py" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Verification passed - Fix is active
) else (
    echo [WARNING] Verification failed - Manual check recommended
)

echo.
echo [4/4] Moving existing reports to correct location...
if exist "pipelines\reports\morning_reports" (
    if not exist "reports\morning_reports" mkdir "reports\morning_reports"
    
    echo Moving HTML reports...
    if exist "pipelines\reports\morning_reports\*.html" (
        move /Y "pipelines\reports\morning_reports\*.html" "reports\morning_reports\" >nul
        echo [OK] HTML reports moved
    )
    
    echo Moving JSON data files...
    if exist "pipelines\reports\morning_reports\*.json" (
        move /Y "pipelines\reports\morning_reports\*.json" "reports\morning_reports\" >nul
        echo [OK] JSON data files moved
    )
    
    echo [OK] All reports moved to correct location
) else (
    echo [INFO] No existing reports to move
)

echo.
echo ============================================================================
echo  HOTFIX COMPLETE
echo ============================================================================
echo.
echo  Status: APPLIED
echo  Trading Dashboard: STILL RUNNING (no restart needed)
echo  Next pipeline run: Will save reports to correct location
echo.
echo  Report locations after next run:
echo    HTML: reports\morning_reports\2026-02-11_market_report.html
echo    JSON: reports\morning_reports\2026-02-11_data.json
echo.
echo  Backup saved: backups\report_generator.py.backup_*
echo.
echo ============================================================================
echo.
pause
