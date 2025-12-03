@echo off
REM ============================================================================
REM Telegram Notification Fix - Automatic Installation
REM ============================================================================

color 0E
cls

echo.
echo ================================================================================
echo TELEGRAM NOTIFICATION FIX - INSTALLER
echo ================================================================================
echo.
echo This patch fixes Telegram notifications for both pipelines:
echo   1. Australian Pipeline (RUN_PIPELINE.bat)
echo   2. US Pipeline (us_overnight_pipeline.py)
echo.
echo What this patch does:
echo   - Backs up your current files to backup\ folder
echo   - Fixes RUN_PIPELINE.bat to run from root directory
echo   - Adds Telegram initialization to US pipeline
echo   - Adds fallback imports for better compatibility
echo.
echo ================================================================================
echo SAFETY: Your original files will be backed up before any changes
echo ================================================================================
echo.
pause

REM Get the script directory and navigate to project root
cd /d "%~dp0"
cd ..

echo.
echo Current directory: %CD%
echo.

REM ============================================================================
REM Step 1: Create backup
REM ============================================================================

echo ================================================================================
echo STEP 1: Creating backup of original files...
echo ================================================================================
echo.

if not exist "TELEGRAM_NOTIFICATION_PATCH\backup" mkdir "TELEGRAM_NOTIFICATION_PATCH\backup"

if exist "RUN_PIPELINE.bat" (
    copy /Y "RUN_PIPELINE.bat" "TELEGRAM_NOTIFICATION_PATCH\backup\RUN_PIPELINE.bat.backup"
    echo   [BACKUP] RUN_PIPELINE.bat
) else (
    echo   [WARNING] RUN_PIPELINE.bat not found - will be created
)

if exist "models\screening\us_overnight_pipeline.py" (
    copy /Y "models\screening\us_overnight_pipeline.py" "TELEGRAM_NOTIFICATION_PATCH\backup\us_overnight_pipeline.py.backup"
    echo   [BACKUP] models\screening\us_overnight_pipeline.py
) else (
    echo   [ERROR] models\screening\us_overnight_pipeline.py not found!
    echo   Please make sure you're running this from C:\Users\david\AATelS
    pause
    exit /b 1
)

if exist "models\screening\overnight_pipeline.py" (
    copy /Y "models\screening\overnight_pipeline.py" "TELEGRAM_NOTIFICATION_PATCH\backup\overnight_pipeline.py.backup"
    echo   [BACKUP] models\screening\overnight_pipeline.py
) else (
    echo   [ERROR] models\screening\overnight_pipeline.py not found!
    pause
    exit /b 1
)

echo.
echo Backup complete! Files saved to: TELEGRAM_NOTIFICATION_PATCH\backup\
echo.

REM ============================================================================
REM Step 2: Install fixed files
REM ============================================================================

echo ================================================================================
echo STEP 2: Installing fixed files...
echo ================================================================================
echo.

copy /Y "TELEGRAM_NOTIFICATION_PATCH\RUN_PIPELINE.bat" "RUN_PIPELINE.bat"
if %errorlevel% equ 0 (
    echo   [OK] RUN_PIPELINE.bat updated
) else (
    echo   [ERROR] Failed to update RUN_PIPELINE.bat
    pause
    exit /b 1
)

copy /Y "TELEGRAM_NOTIFICATION_PATCH\us_overnight_pipeline.py" "models\screening\us_overnight_pipeline.py"
if %errorlevel% equ 0 (
    echo   [OK] us_overnight_pipeline.py updated
) else (
    echo   [ERROR] Failed to update us_overnight_pipeline.py
    pause
    exit /b 1
)

copy /Y "TELEGRAM_NOTIFICATION_PATCH\overnight_pipeline.py" "models\screening\overnight_pipeline.py"
if %errorlevel% equ 0 (
    echo   [OK] overnight_pipeline.py updated
) else (
    echo   [ERROR] Failed to update overnight_pipeline.py
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Fixed files installed:
echo   1. RUN_PIPELINE.bat - Now runs from root directory
echo   2. us_overnight_pipeline.py - Telegram notifications added
echo   3. overnight_pipeline.py - Improved import handling
echo.
echo Backups saved to: TELEGRAM_NOTIFICATION_PATCH\backup\
echo.

REM ============================================================================
REM Step 3: Verification
REM ============================================================================

echo ================================================================================
echo STEP 3: Verification
echo ================================================================================
echo.

echo Testing Telegram import...
python -c "from models.notifications.telegram_notifier import TelegramNotifier; print('  [OK] TelegramNotifier imports successfully')"

if %errorlevel% equ 0 (
    echo.
    echo Telegram module is working correctly!
) else (
    echo.
    echo   [WARNING] Telegram import test failed
    echo   This might be normal if you haven't set up Telegram yet
)

echo.

REM ============================================================================
REM Next Steps
REM ============================================================================

echo ================================================================================
echo NEXT STEPS
echo ================================================================================
echo.
echo 1. Make sure your Telegram credentials are configured:
echo    File: config\intraday_rescan_config.json
echo    Section: notifications.telegram
echo.
echo 2. Test the Australian pipeline:
echo    Double-click: RUN_PIPELINE.bat
echo.
echo 3. Test the US pipeline:
echo    Double-click: RUN_US_PIPELINE.bat
echo.
echo 4. Look for this in the startup logs:
echo    "✓ Telegram notifications enabled"
echo.
echo 5. After pipeline completes, you'll receive:
echo    - Telegram message with summary
echo    - HTML report attachment
echo    - CSV file attachment
echo.
echo ================================================================================
echo ROLLBACK (If needed)
echo ================================================================================
echo.
echo If anything goes wrong, restore backups from:
echo   TELEGRAM_NOTIFICATION_PATCH\backup\
echo.
echo Simply copy the .backup files back to their original locations.
echo.
echo ================================================================================

pause
