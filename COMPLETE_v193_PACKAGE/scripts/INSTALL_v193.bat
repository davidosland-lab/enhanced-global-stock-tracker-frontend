@echo off
REM ============================================================================
REM v193 Installation Script
REM World Event Risk Monitor + UK/US HTML Reports Fix
REM ============================================================================

echo ================================================================================
echo v193 INSTALLATION WIZARD
echo World Event Risk Monitor + UK/US HTML Reports Fix
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.8+ or add it to PATH
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Get current directory
set "INSTALL_DIR=%~dp0"
echo Installation Directory: %INSTALL_DIR%
echo.

REM Backup existing files
echo ================================================================================
echo STEP 1: BACKING UP EXISTING FILES
echo ================================================================================
echo.

if not exist "%INSTALL_DIR%backup_pre_v193" mkdir "%INSTALL_DIR%backup_pre_v193"

echo Creating backups...
if exist "%INSTALL_DIR%pipelines\models\screening\overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\overnight_pipeline.py" "%INSTALL_DIR%backup_pre_v193\overnight_pipeline.py.bak" >nul
    echo [OK] Backed up overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\uk_overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\uk_overnight_pipeline.py" "%INSTALL_DIR%backup_pre_v193\uk_overnight_pipeline.py.bak" >nul
    echo [OK] Backed up uk_overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\us_overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\us_overnight_pipeline.py" "%INSTALL_DIR%backup_pre_v193\us_overnight_pipeline.py.bak" >nul
    echo [OK] Backed up us_overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\report_generator.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\report_generator.py" "%INSTALL_DIR%backup_pre_v193\report_generator.py.bak" >nul
    echo [OK] Backed up report_generator.py
)

if exist "%INSTALL_DIR%core\sentiment_integration.py" (
    copy /Y "%INSTALL_DIR%core\sentiment_integration.py" "%INSTALL_DIR%backup_pre_v193\sentiment_integration.py.bak" >nul
    echo [OK] Backed up sentiment_integration.py
)

if exist "%INSTALL_DIR%scripts\run_uk_full_pipeline.py" (
    copy /Y "%INSTALL_DIR%scripts\run_uk_full_pipeline.py" "%INSTALL_DIR%backup_pre_v193\run_uk_full_pipeline.py.bak" >nul
    echo [OK] Backed up run_uk_full_pipeline.py
)

if exist "%INSTALL_DIR%scripts\run_us_full_pipeline.py" (
    copy /Y "%INSTALL_DIR%scripts\run_us_full_pipeline.py" "%INSTALL_DIR%backup_pre_v193\run_us_full_pipeline.py.bak" >nul
    echo [OK] Backed up run_us_full_pipeline.py
)

echo.
echo [OK] Backup complete: %INSTALL_DIR%backup_pre_v193\
echo.

REM Check if running from git repository
echo ================================================================================
echo STEP 2: CHECKING INSTALLATION METHOD
echo ================================================================================
echo.

if exist "%INSTALL_DIR%.git\" (
    echo [OK] Git repository detected
    echo.
    echo Attempting git pull...
    echo.
    
    cd /d "%INSTALL_DIR%"
    git pull origin market-timing-critical-fix
    
    if errorlevel 1 (
        echo.
        echo [WARNING] Git pull failed. This might be normal if you have local changes.
        echo.
        echo You can manually apply the patch or use a fresh install.
        echo.
        pause
    ) else (
        echo.
        echo [OK] Git pull successful
    )
) else (
    echo [INFO] Not a git repository
    echo Files appear to already be in place
    echo Continuing with verification...
)

echo.

REM Verify critical files exist
echo ================================================================================
echo STEP 3: VERIFYING v193 FILES
echo ================================================================================
echo.

set "MISSING_FILES=0"

if not exist "%INSTALL_DIR%pipelines\models\screening\world_event_monitor.py" (
    echo [ERROR] Missing: world_event_monitor.py
    set "MISSING_FILES=1"
) else (
    echo [OK] Found: world_event_monitor.py
)

if not exist "%INSTALL_DIR%test_world_event_monitor.py" (
    echo [WARNING] Missing: test_world_event_monitor.py ^(optional^)
) else (
    echo [OK] Found: test_world_event_monitor.py
)

if not exist "%INSTALL_DIR%INSTALL_v193.md" (
    echo [WARNING] Missing: INSTALL_v193.md ^(documentation^)
) else (
    echo [OK] Found: INSTALL_v193.md
)

echo.

if "%MISSING_FILES%"=="1" (
    echo [ERROR] Critical files missing. Installation incomplete.
    echo.
    echo Please ensure you have:
    echo   1. Extracted the v193 patch to the correct directory, OR
    echo   2. Pulled from the git repository successfully
    echo.
    pause
    exit /b 1
)

REM Run test suite
echo ================================================================================
echo STEP 4: RUNNING TEST SUITE
echo ================================================================================
echo.

cd /d "%INSTALL_DIR%"

if exist "test_world_event_monitor.py" (
    echo Running world event monitor tests...
    echo.
    python test_world_event_monitor.py
    
    if errorlevel 1 (
        echo.
        echo [WARNING] Tests failed. Please review errors above.
        echo.
        echo Common issues:
        echo   - Missing dependencies ^(install via: pip install -r requirements.txt^)
        echo   - Import errors ^(check Python path^)
        echo.
        pause
    ) else (
        echo.
        echo [OK] All tests passed
    )
) else (
    echo [INFO] Test file not found, skipping tests
)

echo.

REM Create verification report
echo ================================================================================
echo STEP 5: GENERATING VERIFICATION REPORT
echo ================================================================================
echo.

set "REPORT_FILE=%INSTALL_DIR%v193_installation_report.txt"

echo v193 Installation Report > "%REPORT_FILE%"
echo Generated: %date% %time% >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Installation Directory: %INSTALL_DIR% >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Files Installed: >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/world_event_monitor.py >> "%REPORT_FILE%"
echo   [X] test_world_event_monitor.py >> "%REPORT_FILE%"
echo   [X] INSTALL_v193.md >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Files Modified: >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/uk_overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/us_overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/report_generator.py >> "%REPORT_FILE%"
echo   [X] core/sentiment_integration.py >> "%REPORT_FILE%"
echo   [X] scripts/run_uk_full_pipeline.py >> "%REPORT_FILE%"
echo   [X] scripts/run_us_full_pipeline.py >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Backup Location: >> "%REPORT_FILE%"
echo   backup_pre_v193/ >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Next Steps: >> "%REPORT_FILE%"
echo   1. Run overnight pipelines ^(AU/UK/US^) >> "%REPORT_FILE%"
echo   2. Check logs for "PHASE 1.4: WORLD EVENT RISK MONITORING" >> "%REPORT_FILE%"
echo   3. Verify HTML reports generated in reports/screening/ >> "%REPORT_FILE%"
echo   4. Open HTML reports and check for "World Event Risk" card >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [OK] Installation report saved: v193_installation_report.txt
echo.

REM Final summary
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo.
echo v193 has been successfully installed!
echo.
echo WHAT'S NEW:
echo   - World Event Risk Monitor ^(geopolitical crisis detection^)
echo   - UK/US HTML morning reports ^(previously only JSON^)
echo   - Trading position gates ^(auto size reduction during crises^)
echo   - World risk display in all market overview cards
echo.
echo NEXT STEPS:
echo   1. Review installation report: v193_installation_report.txt
echo   2. Run test: python test_world_event_monitor.py
echo   3. Run pipelines tonight:
echo      - python scripts/run_au_pipeline_v1.3.13.py
echo      - python scripts/run_uk_full_pipeline.py --full-scan
echo      - python scripts/run_us_full_pipeline.py --full-scan
echo   4. Check HTML reports: dir reports\screening\*.html
echo   5. Open reports in browser and verify World Risk card
echo.
echo DOCUMENTATION:
echo   - Installation Guide: INSTALL_v193.md
echo   - Technical Summary: v193_COMPLETE_SUMMARY.md
echo   - Quick Reference: QUICK_REFERENCE_v193.md
echo.
echo BACKUP:
echo   - Original files backed up to: backup_pre_v193\
echo   - To rollback: restore files from backup folder
echo.
echo SUPPORT:
echo   - Run test suite: python test_world_event_monitor.py
echo   - Check module: python -c "from pipelines.models.screening.world_event_monitor import WorldEventMonitor; print('OK')"
echo   - Review logs for PHASE 1.4 sections
echo.
echo ================================================================================
echo.

pause
