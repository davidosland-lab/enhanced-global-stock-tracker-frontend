@echo off
REM ============================================================================
REM Fix Dependency Conflict - cachetools Version Mismatch
REM ============================================================================
REM Resolves conflict between python-telegram-bot 13.15 and cachetools 6.2.2
REM
REM Created: 2025-12-05
REM Version: 1.0
REM ============================================================================

echo.
echo ============================================================
echo Dependency Conflict Fix
echo ============================================================
echo.
echo Issue: python-telegram-bot 13.15 requires cachetools==4.2.2
echo Current: cachetools 6.2.2 installed
echo.
echo This script will fix the conflict automatically.
echo.
pause

REM ============================================================
REM Step 1: Navigate to Project Directory
REM ============================================================
echo.
echo Step 1: Navigating to project directory...
echo ------------------------------------------------------------

cd /d C:\Users\david\AATelS
if errorlevel 1 (
    echo ERROR: Cannot access C:\Users\david\AATelS
    echo Please verify the directory exists.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM ============================================================
REM Step 2: Check if Telegram Bot is Used
REM ============================================================
echo Step 2: Checking if telegram bot is used in code...
echo ------------------------------------------------------------

REM Search for telegram imports
findstr /s /i "import telegram" *.py >nul 2>&1
if errorlevel 1 (
    set TELEGRAM_USED=NO
    echo Result: Telegram bot NOT found in code
) else (
    set TELEGRAM_USED=YES
    echo Result: Telegram bot IS found in code
)
echo.

REM Check if package is installed
pip show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    set TELEGRAM_INSTALLED=NO
    echo Telegram bot package: NOT installed
) else (
    set TELEGRAM_INSTALLED=YES
    echo Telegram bot package: INSTALLED
    pip show python-telegram-bot | findstr "Version"
)
echo.

REM ============================================================
REM Step 3: Determine Fix Strategy
REM ============================================================
echo Step 3: Determining fix strategy...
echo ------------------------------------------------------------

if "%TELEGRAM_USED%"=="NO" (
    if "%TELEGRAM_INSTALLED%"=="YES" (
        echo Strategy: REMOVE python-telegram-bot (not used in code)
        set FIX_STRATEGY=REMOVE
    ) else (
        echo Strategy: NO ACTION NEEDED (not installed, not used)
        set FIX_STRATEGY=NONE
    )
) else (
    echo Strategy: UPGRADE python-telegram-bot to v20+ (used in code)
    set FIX_STRATEGY=UPGRADE
)
echo.

if "%FIX_STRATEGY%"=="NONE" (
    echo No action needed. Dependency conflict may be from cached install.
    echo.
    goto VERIFY
)

pause

REM ============================================================
REM Step 4: Apply Fix
REM ============================================================
echo.
echo Step 4: Applying fix (%FIX_STRATEGY%)...
echo ------------------------------------------------------------

if "%FIX_STRATEGY%"=="REMOVE" goto DO_REMOVE
if "%FIX_STRATEGY%"=="UPGRADE" goto DO_UPGRADE

:DO_REMOVE
echo.
echo Removing python-telegram-bot...
echo.

pip uninstall python-telegram-bot -y
if errorlevel 1 (
    echo ERROR: Failed to remove python-telegram-bot
    echo.
    echo Trying force remove...
    pip uninstall python-telegram-bot -y --break-system-packages
    if errorlevel 1 (
        echo ERROR: Force remove also failed.
        echo Manual intervention required.
        pause
        exit /b 1
    )
)

echo Successfully removed python-telegram-bot
echo.
goto VERIFY

:DO_UPGRADE
echo.
echo Upgrading python-telegram-bot to v20+...
echo.

REM Try upgrade to latest
pip install --upgrade python-telegram-bot
if errorlevel 1 (
    echo WARNING: Standard upgrade failed.
    echo.
    echo Trying specific version install...
    pip install "python-telegram-bot>=20.0"
    if errorlevel 1 (
        echo ERROR: Failed to upgrade python-telegram-bot
        echo.
        echo Possible solutions:
        echo 1. Check internet connection
        echo 2. Try: pip install --upgrade --force-reinstall python-telegram-bot
        echo 3. Manually install: pip install python-telegram-bot==20.7
        pause
        exit /b 1
    )
)

echo Successfully upgraded python-telegram-bot
echo.

REM Also ensure cachetools is up to date
echo Verifying cachetools version...
pip install --upgrade cachetools
if errorlevel 1 (
    echo WARNING: cachetools upgrade failed (may not be critical)
)
echo.

REM ============================================================
REM Step 5: Verify Fix
REM ============================================================
:VERIFY
echo.
echo Step 5: Verifying fix...
echo ------------------------------------------------------------

echo.
echo Checking for dependency conflicts...
pip check
if errorlevel 1 (
    echo.
    echo ============================================================
    echo WARNING: Some dependency conflicts remain
    echo ============================================================
    echo.
    echo Please review the conflicts above.
    echo You may need to:
    echo 1. Upgrade other conflicting packages
    echo 2. Check requirements.txt for version constraints
    echo 3. Run: pip check for details
    echo.
) else (
    echo.
    echo ============================================================
    echo SUCCESS: No broken requirements found!
    echo ============================================================
    echo.
)

REM Display current versions
echo.
echo Current package versions:
echo ------------------------------------------------------------

if "%TELEGRAM_INSTALLED%"=="YES" (
    pip show python-telegram-bot | findstr "Name Version"
)
pip show cachetools | findstr "Name Version"

echo.

REM ============================================================
REM Step 6: Summary
REM ============================================================
echo.
echo ============================================================
echo Fix Summary
echo ============================================================
echo.
echo Fix strategy: %FIX_STRATEGY%
echo Telegram used in code: %TELEGRAM_USED%
echo Telegram installed: %TELEGRAM_INSTALLED%
echo.

if "%FIX_STRATEGY%"=="REMOVE" (
    echo Action taken:
    echo - Removed python-telegram-bot package
    echo - cachetools conflict resolved
    echo.
    echo Note: If you need Telegram functionality later:
    echo   pip install python-telegram-bot^>=20.0
)

if "%FIX_STRATEGY%"=="UPGRADE" (
    echo Action taken:
    echo - Upgraded python-telegram-bot to v20+
    echo - Upgraded cachetools to latest compatible version
    echo.
    echo Note: python-telegram-bot v20+ has API changes.
    echo   Review: https://docs.python-telegram-bot.org/
)

if "%FIX_STRATEGY%"=="NONE" (
    echo No action taken - no conflict detected.
)

echo.
echo Next steps:
echo 1. Run 'pip check' to verify no conflicts
echo 2. Test your application to ensure it works
echo 3. Update requirements.txt if needed
echo.

REM ============================================================
REM Optional: Test Import
REM ============================================================
echo.
choice /C YN /M "Test Python imports now?"
if errorlevel 2 goto END
if errorlevel 1 goto TEST_IMPORT

:TEST_IMPORT
echo.
echo Testing Python imports...
echo ------------------------------------------------------------

if "%TELEGRAM_INSTALLED%"=="YES" (
    echo Testing telegram import...
    python -c "import telegram; print(f'✓ Telegram version: {telegram.__version__}')" 2>nul
    if errorlevel 1 (
        echo ✗ Telegram import FAILED
    )
)

echo Testing cachetools import...
python -c "import cachetools; print(f'✓ Cachetools version: {cachetools.__version__}')" 2>nul
if errorlevel 1 (
    echo ✗ Cachetools import FAILED
)

echo.

:END
echo.
echo ============================================================
echo Fix Complete
echo ============================================================
echo.
echo For more details, see: FIX_DEPENDENCY_CONFLICT.md
echo.
pause
