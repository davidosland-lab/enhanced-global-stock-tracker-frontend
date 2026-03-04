@echo off
REM ============================================================================
REM COMPLETE v193 INSTALLATION SCRIPT
REM Includes: v192 (AI Sentiment) + v193 (World Event Risk + HTML Reports)
REM ============================================================================

echo ================================================================================
echo COMPLETE v193 INSTALLATION WIZARD
echo ================================================================================
echo.
echo This package includes:
echo   - v192: AI-Enhanced Macro Sentiment Analysis
echo   - v193: World Event Risk Monitor
echo   - v193: UK/US HTML Report Generation Fix
echo.
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.8+ or add it to PATH
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Get installation directory
set "INSTALL_DIR=%~dp0..\"
echo Installation Directory: %INSTALL_DIR%
echo.

REM Confirm installation
echo This will install/update the following files:
echo.
echo NEW FILES (4):
echo   - pipelines/models/screening/world_event_monitor.py
echo   - pipelines/models/screening/ai_market_impact_analyzer.py
echo   - test_world_event_monitor.py
echo   - test_ai_macro_sentiment.py
echo.
echo MODIFIED FILES (8):
echo   - pipelines/models/screening/overnight_pipeline.py
echo   - pipelines/models/screening/uk_overnight_pipeline.py
echo   - pipelines/models/screening/us_overnight_pipeline.py
echo   - pipelines/models/screening/report_generator.py
echo   - pipelines/models/screening/macro_news_monitor.py
echo   - core/sentiment_integration.py
echo   - scripts/run_uk_full_pipeline.py
echo   - scripts/run_us_full_pipeline.py
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

REM Create backup directory
echo ================================================================================
echo STEP 1: CREATING BACKUPS
echo ================================================================================
echo.

set "BACKUP_DIR=%INSTALL_DIR%backup_v193_install_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
echo Created: %BACKUP_DIR%
echo.

REM Backup existing files
echo Backing up existing files...

if exist "%INSTALL_DIR%pipelines\models\screening\overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\overnight_pipeline.py" "%BACKUP_DIR%\overnight_pipeline.py.bak" >nul
    echo [OK] Backed up overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\uk_overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\uk_overnight_pipeline.py" "%BACKUP_DIR%\uk_overnight_pipeline.py.bak" >nul
    echo [OK] Backed up uk_overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\us_overnight_pipeline.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\us_overnight_pipeline.py" "%BACKUP_DIR%\us_overnight_pipeline.py.bak" >nul
    echo [OK] Backed up us_overnight_pipeline.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\report_generator.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\report_generator.py" "%BACKUP_DIR%\report_generator.py.bak" >nul
    echo [OK] Backed up report_generator.py
)

if exist "%INSTALL_DIR%pipelines\models\screening\macro_news_monitor.py" (
    copy /Y "%INSTALL_DIR%pipelines\models\screening\macro_news_monitor.py" "%BACKUP_DIR%\macro_news_monitor.py.bak" >nul
    echo [OK] Backed up macro_news_monitor.py
)

if exist "%INSTALL_DIR%core\sentiment_integration.py" (
    copy /Y "%INSTALL_DIR%core\sentiment_integration.py" "%BACKUP_DIR%\sentiment_integration.py.bak" >nul
    echo [OK] Backed up sentiment_integration.py
)

if exist "%INSTALL_DIR%scripts\run_uk_full_pipeline.py" (
    copy /Y "%INSTALL_DIR%scripts\run_uk_full_pipeline.py" "%BACKUP_DIR%\run_uk_full_pipeline.py.bak" >nul
    echo [OK] Backed up run_uk_full_pipeline.py
)

if exist "%INSTALL_DIR%scripts\run_us_full_pipeline.py" (
    copy /Y "%INSTALL_DIR%scripts\run_us_full_pipeline.py" "%BACKUP_DIR%\run_us_full_pipeline.py.bak" >nul
    echo [OK] Backed up run_us_full_pipeline.py
)

echo.
echo [OK] Backup complete: %BACKUP_DIR%
echo.

REM Install new files
echo ================================================================================
echo STEP 2: INSTALLING NEW FILES
echo ================================================================================
echo.

set "SCRIPT_DIR=%~dp0"

if not exist "%INSTALL_DIR%pipelines\models\screening" mkdir "%INSTALL_DIR%pipelines\models\screening"

echo Installing new modules...
copy /Y "%SCRIPT_DIR%..\new_files\world_event_monitor.py" "%INSTALL_DIR%pipelines\models\screening\world_event_monitor.py" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy world_event_monitor.py
) else (
    echo [OK] Installed world_event_monitor.py
)

copy /Y "%SCRIPT_DIR%..\new_files\ai_market_impact_analyzer.py" "%INSTALL_DIR%pipelines\models\screening\ai_market_impact_analyzer.py" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy ai_market_impact_analyzer.py
) else (
    echo [OK] Installed ai_market_impact_analyzer.py
)

copy /Y "%SCRIPT_DIR%..\new_files\test_world_event_monitor.py" "%INSTALL_DIR%test_world_event_monitor.py" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy test_world_event_monitor.py
) else (
    echo [OK] Installed test_world_event_monitor.py
)

copy /Y "%SCRIPT_DIR%..\new_files\test_ai_macro_sentiment.py" "%INSTALL_DIR%test_ai_macro_sentiment.py" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy test_ai_macro_sentiment.py
) else (
    echo [OK] Installed test_ai_macro_sentiment.py
)

echo.

REM Update modified files
echo ================================================================================
echo STEP 3: UPDATING MODIFIED FILES
echo ================================================================================
echo.

echo Updating pipeline files...

copy /Y "%SCRIPT_DIR%..\modified_files\overnight_pipeline.py" "%INSTALL_DIR%pipelines\models\screening\overnight_pipeline.py" >nul
echo [OK] Updated overnight_pipeline.py

copy /Y "%SCRIPT_DIR%..\modified_files\uk_overnight_pipeline.py" "%INSTALL_DIR%pipelines\models\screening\uk_overnight_pipeline.py" >nul
echo [OK] Updated uk_overnight_pipeline.py

copy /Y "%SCRIPT_DIR%..\modified_files\us_overnight_pipeline.py" "%INSTALL_DIR%pipelines\models\screening\us_overnight_pipeline.py" >nul
echo [OK] Updated us_overnight_pipeline.py

copy /Y "%SCRIPT_DIR%..\modified_files\report_generator.py" "%INSTALL_DIR%pipelines\models\screening\report_generator.py" >nul
echo [OK] Updated report_generator.py

copy /Y "%SCRIPT_DIR%..\modified_files\macro_news_monitor.py" "%INSTALL_DIR%pipelines\models\screening\macro_news_monitor.py" >nul
echo [OK] Updated macro_news_monitor.py

copy /Y "%SCRIPT_DIR%..\modified_files\sentiment_integration.py" "%INSTALL_DIR%core\sentiment_integration.py" >nul
echo [OK] Updated sentiment_integration.py

copy /Y "%SCRIPT_DIR%..\modified_files\run_uk_full_pipeline.py" "%INSTALL_DIR%scripts\run_uk_full_pipeline.py" >nul
echo [OK] Updated run_uk_full_pipeline.py

copy /Y "%SCRIPT_DIR%..\modified_files\run_us_full_pipeline.py" "%INSTALL_DIR%scripts\run_us_full_pipeline.py" >nul
echo [OK] Updated run_us_full_pipeline.py

echo.

REM Run tests
echo ================================================================================
echo STEP 4: RUNNING TEST SUITE
echo ================================================================================
echo.

cd /d "%INSTALL_DIR%"

echo Testing World Event Risk Monitor...
python test_world_event_monitor.py
if errorlevel 1 (
    echo.
    echo [WARNING] World Event Monitor tests failed
    echo.
) else (
    echo.
    echo [OK] World Event Monitor tests passed
    echo.
)

echo.
echo Testing AI Macro Sentiment Analyzer...
python test_ai_macro_sentiment.py
if errorlevel 1 (
    echo.
    echo [WARNING] AI Sentiment tests failed
    echo.
) else (
    echo.
    echo [OK] AI Sentiment tests passed
    echo.
)

echo.

REM Generate installation report
echo ================================================================================
echo STEP 5: GENERATING INSTALLATION REPORT
echo ================================================================================
echo.

set "REPORT_FILE=%INSTALL_DIR%v193_installation_report.txt"

echo COMPLETE v193 INSTALLATION REPORT > "%REPORT_FILE%"
echo Generated: %date% %time% >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo Installation Directory: %INSTALL_DIR% >> "%REPORT_FILE%"
echo Backup Directory: %BACKUP_DIR% >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo NEW FILES INSTALLED: >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/world_event_monitor.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/ai_market_impact_analyzer.py >> "%REPORT_FILE%"
echo   [X] test_world_event_monitor.py >> "%REPORT_FILE%"
echo   [X] test_ai_macro_sentiment.py >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo MODIFIED FILES UPDATED: >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/uk_overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/us_overnight_pipeline.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/report_generator.py >> "%REPORT_FILE%"
echo   [X] pipelines/models/screening/macro_news_monitor.py >> "%REPORT_FILE%"
echo   [X] core/sentiment_integration.py >> "%REPORT_FILE%"
echo   [X] scripts/run_uk_full_pipeline.py >> "%REPORT_FILE%"
echo   [X] scripts/run_us_full_pipeline.py >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"
echo FEATURES ADDED: >> "%REPORT_FILE%"
echo   - v192: AI-Enhanced Macro Sentiment Analysis >> "%REPORT_FILE%"
echo   - v193: World Event Risk Monitor >> "%REPORT_FILE%"
echo   - v193: UK/US HTML Report Generation >> "%REPORT_FILE%"
echo   - Trading Position Gates (auto size reduction) >> "%REPORT_FILE%"
echo   - World Risk Display in HTML Reports >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo [OK] Installation report: v193_installation_report.txt
echo.

REM Final summary
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo.
echo SUCCESS! v193 has been installed successfully.
echo.
echo WHAT'S NEW:
echo   v192: AI-Enhanced Macro Sentiment (Iran-US war detection)
echo   v193: World Event Risk Monitor (geopolitical crisis scoring)
echo   v193: UK/US HTML Morning Reports (FTSE/S^&P sentiment)
echo   v193: Trading Position Gates (50%% reduction during crises)
echo.
echo NEXT STEPS:
echo   1. Review: v193_installation_report.txt
echo   2. Run pipelines tonight:
echo      - python scripts/run_au_pipeline_v1.3.13.py
echo      - python scripts/run_uk_full_pipeline.py --full-scan
echo      - python scripts/run_us_full_pipeline.py --full-scan
echo   3. Check logs for "PHASE 1.4: WORLD EVENT RISK"
echo   4. Verify HTML reports: dir reports\screening\*.html
echo   5. Open reports and check World Risk card
echo.
echo BACKUP LOCATION:
echo   %BACKUP_DIR%
echo.
echo ROLLBACK (if needed):
echo   Copy files from backup folder back to original locations
echo.
echo DOCUMENTATION:
echo   See documentation/ folder for complete guides
echo.
echo ================================================================================
echo.

pause
