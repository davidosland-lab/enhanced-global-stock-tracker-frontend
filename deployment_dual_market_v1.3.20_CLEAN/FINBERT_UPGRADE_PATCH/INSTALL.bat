@echo off
REM ========================================================================
REM FinBERT Upgrade Patch Installer
REM ========================================================================
REM
REM This script installs the FinBERT upgrade patch which includes:
REM - Morning Report Telegram Notifications
REM - Macro News Monitoring (Fed/RBA)
REM
REM ========================================================================

echo.
echo ========================================================================
echo FINBERT UPGRADE PATCH INSTALLER
echo ========================================================================
echo.
echo This will install:
echo   1. Morning Report Telegram Notifications
echo   2. Macro News Monitoring (Fed/RBA announcements)
echo   3. Enhanced sentiment analysis with government data
echo.
echo Target directory: %CD%\..
echo.
pause

REM Change to parent directory (where the project is)
cd ..

echo.
echo ========================================================================
echo STEP 1: Checking Git Status
echo ========================================================================
echo.

git status
if errorlevel 1 (
    echo ERROR: Not a git repository or git not found
    echo.
    echo Please ensure you are running this from the project directory
    echo and that git is installed.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 2: Checking for Uncommitted Changes
echo ========================================================================
echo.

git diff --quiet
if errorlevel 1 (
    echo WARNING: You have uncommitted changes!
    echo.
    echo It's recommended to commit or stash your changes before applying the patch.
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if errorlevel 2 exit /b 1
)

echo.
echo ========================================================================
echo STEP 3: Backing Up Current State
echo ========================================================================
echo.

git branch finbert-backup-%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%
if errorlevel 1 (
    echo WARNING: Backup branch creation failed
) else (
    echo Backup branch created successfully
)

echo.
echo ========================================================================
echo STEP 4: Applying Patch
echo ========================================================================
echo.

git apply --check FINBERT_UPGRADE_PATCH\finbert_upgrade_full.patch
if errorlevel 1 (
    echo.
    echo ERROR: Patch check failed!
    echo.
    echo This could mean:
    echo   - Your code has conflicting changes
    echo   - The patch is incompatible with your version
    echo   - Files have been modified
    echo.
    echo Please see MANUAL_INSTALLATION.md for manual installation steps.
    pause
    exit /b 1
)

echo Patch check passed! Applying patch...
echo.

git apply FINBERT_UPGRADE_PATCH\finbert_upgrade_full.patch
if errorlevel 1 (
    echo.
    echo ERROR: Patch application failed!
    echo.
    echo Please see MANUAL_INSTALLATION.md for manual installation steps.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 5: Verifying Installation
echo ========================================================================
echo.

REM Check if key files exist
if exist "models\screening\macro_news_monitor.py" (
    echo [OK] macro_news_monitor.py
) else (
    echo [MISSING] macro_news_monitor.py
)

if exist "test_morning_report_telegram.py" (
    echo [OK] test_morning_report_telegram.py
) else (
    echo [MISSING] test_morning_report_telegram.py
)

if exist "MORNING_REPORT_SETUP.md" (
    echo [OK] MORNING_REPORT_SETUP.md
) else (
    echo [MISSING] MORNING_REPORT_SETUP.md
)

echo.
echo ========================================================================
echo STEP 6: Configuration Check
echo ========================================================================
echo.

if exist "config\intraday_rescan_config.json" (
    echo [OK] Configuration file exists
    echo.
    echo Please verify your Telegram credentials in:
    echo   config\intraday_rescan_config.json
    echo.
    echo Required fields:
    echo   notifications.telegram.enabled = true
    echo   notifications.telegram.bot_token = YOUR_BOT_TOKEN
    echo   notifications.telegram.chat_id = YOUR_CHAT_ID
) else (
    echo [WARNING] Configuration file not found
    echo.
    echo You'll need to create config\intraday_rescan_config.json
    echo See MORNING_REPORT_SETUP.md for details.
)

echo.
echo ========================================================================
echo INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Next steps:
echo   1. Review MORNING_REPORT_SETUP.md for configuration
echo   2. Verify Telegram credentials in config file
echo   3. Test with: python test_morning_report_telegram.py
echo   4. Run overnight pipeline to see upgrades in action
echo.
echo Documentation:
echo   - MORNING_REPORT_SETUP.md - Morning report setup
echo   - MACRO_NEWS_INTEGRATION_COMPLETE.md - Macro news details
echo   - NEWS_AND_EVENTS_STATUS.md - Complete feature status
echo.
echo Commit the changes:
echo   git add .
echo   git commit -m "Applied FinBERT upgrade patch"
echo.
pause
