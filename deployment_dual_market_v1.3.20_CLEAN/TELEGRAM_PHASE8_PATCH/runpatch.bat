@echo off
REM ========================================================================
REM Telegram Phase 8 Integration Patch
REM ========================================================================
REM
REM This script adds Phase 8 (Telegram Notifications) to overnight pipelines
REM Fixes the missing Telegram notification issue after pipeline completion
REM
REM ========================================================================

echo.
echo ========================================================================
echo TELEGRAM PHASE 8 INTEGRATION PATCH
echo ========================================================================
echo.
echo This patch will add:
echo   1. Phase 8 (Telegram Notifications) to overnight_pipeline.py
echo   2. Phase 8 (Telegram Notifications) to us_overnight_pipeline.py
echo   3. Telegram report notification function for both pipelines
echo.
echo Target directory: %CD%\..
echo.
echo NOTE: Your Telegram credentials are already configured.
echo       This patch only adds the missing Phase 8 code execution.
echo.
pause

REM Change to parent directory (where the project is)
cd ..

echo.
echo ========================================================================
echo STEP 1: Checking Environment
echo ========================================================================
echo.

if not exist "models\screening\overnight_pipeline.py" (
    echo ERROR: overnight_pipeline.py not found!
    echo.
    echo Please ensure you are running this from the correct directory.
    echo Expected: C:\Users\david\AATelS\TELEGRAM_PHASE8_PATCH
    pause
    exit /b 1
)

echo [OK] Found overnight_pipeline.py
echo.

if not exist "models\screening\us_overnight_pipeline.py" (
    echo WARNING: us_overnight_pipeline.py not found!
    echo Will only patch Australian pipeline.
    set US_PIPELINE_EXISTS=0
) else (
    echo [OK] Found us_overnight_pipeline.py
    set US_PIPELINE_EXISTS=1
)

echo.
echo ========================================================================
echo STEP 2: Creating Backups
echo ========================================================================
echo.

copy "models\screening\overnight_pipeline.py" "models\screening\overnight_pipeline.py.backup" >nul
if errorlevel 1 (
    echo ERROR: Failed to create backup for overnight_pipeline.py
    pause
    exit /b 1
)
echo [OK] Backed up overnight_pipeline.py

if %US_PIPELINE_EXISTS%==1 (
    copy "models\screening\us_overnight_pipeline.py" "models\screening\us_overnight_pipeline.py.backup" >nul
    if errorlevel 1 (
        echo WARNING: Failed to create backup for us_overnight_pipeline.py
    ) else (
        echo [OK] Backed up us_overnight_pipeline.py
    )
)

echo.
echo ========================================================================
echo STEP 3: Checking for Existing Phase 8
echo ========================================================================
echo.

findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" "models\screening\overnight_pipeline.py" >nul
if not errorlevel 1 (
    echo Phase 8 already exists in overnight_pipeline.py
    set ASX_NEEDS_PATCH=0
) else (
    echo Phase 8 NOT found in overnight_pipeline.py - will patch
    set ASX_NEEDS_PATCH=1
)

if %US_PIPELINE_EXISTS%==1 (
    findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" "models\screening\us_overnight_pipeline.py" >nul
    if not errorlevel 1 (
        echo Phase 8 already exists in us_overnight_pipeline.py
        set US_NEEDS_PATCH=0
    ) else (
        echo Phase 8 NOT found in us_overnight_pipeline.py - will patch
        set US_NEEDS_PATCH=1
    )
)

if %ASX_NEEDS_PATCH%==0 (
    if %US_PIPELINE_EXISTS%==0 (
        echo.
        echo All pipelines already have Phase 8 installed!
        echo No patching needed.
        pause
        exit /b 0
    )
    if %US_NEEDS_PATCH%==0 (
        echo.
        echo All pipelines already have Phase 8 installed!
        echo No patching needed.
        pause
        exit /b 0
    )
)

echo.
echo ========================================================================
echo STEP 4: Applying Python Patcher
echo ========================================================================
echo.

python TELEGRAM_PHASE8_PATCH\apply_patch.py
if errorlevel 1 (
    echo.
    echo ERROR: Patch application failed!
    echo.
    echo Your backups are safe at:
    echo   models\screening\overnight_pipeline.py.backup
    echo   models\screening\us_overnight_pipeline.py.backup
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 5: Verifying Installation
echo ========================================================================
echo.

findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" "models\screening\overnight_pipeline.py" >nul
if errorlevel 1 (
    echo [FAILED] Phase 8 not found in overnight_pipeline.py
    set VERIFY_FAILED=1
) else (
    echo [OK] Phase 8 found in overnight_pipeline.py
    set VERIFY_FAILED=0
)

findstr /C:"_send_telegram_report_notification" "models\screening\overnight_pipeline.py" >nul
if errorlevel 1 (
    echo [FAILED] Telegram function not found in overnight_pipeline.py
    set VERIFY_FAILED=1
) else (
    echo [OK] Telegram function found in overnight_pipeline.py
)

if %US_PIPELINE_EXISTS%==1 (
    findstr /C:"PHASE 8: TELEGRAM NOTIFICATIONS" "models\screening\us_overnight_pipeline.py" >nul
    if errorlevel 1 (
        echo [FAILED] Phase 8 not found in us_overnight_pipeline.py
        set VERIFY_FAILED=1
    ) else (
        echo [OK] Phase 8 found in us_overnight_pipeline.py
    )
    
    findstr /C:"_send_telegram_report_notification" "models\screening\us_overnight_pipeline.py" >nul
    if errorlevel 1 (
        echo [FAILED] Telegram function not found in us_overnight_pipeline.py
        set VERIFY_FAILED=1
    ) else (
        echo [OK] Telegram function found in us_overnight_pipeline.py
    )
)

if %VERIFY_FAILED%==1 (
    echo.
    echo VERIFICATION FAILED!
    echo Please check the files manually or restore from backups.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Phase 8 (Telegram Notifications) has been successfully added!
echo.
echo What was fixed:
echo   - Added Phase 8 execution after Phase 7 (Email Notifications)
echo   - Added _send_telegram_report_notification() function
echo   - Both ASX and US pipelines now send Telegram reports
echo.
echo Next steps:
echo   1. Test Australian pipeline:
echo      python models\screening\overnight_pipeline.py --stocks-per-sector 5
echo.
echo   2. Test US pipeline:
echo      python models\screening\us_overnight_pipeline.py --stocks-per-sector 5
echo.
echo   3. Look for "PHASE 8: TELEGRAM NOTIFICATIONS" in the log
echo.
echo   4. Check your Telegram for the morning report message!
echo.
echo Expected Telegram message:
echo   - Market summary (stocks scanned, opportunities, time)
echo   - HTML report attachment
echo   - CSV export attachment
echo.
echo Backups saved at:
echo   models\screening\overnight_pipeline.py.backup
echo   models\screening\us_overnight_pipeline.py.backup
echo.
pause
