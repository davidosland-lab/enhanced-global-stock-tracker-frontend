@echo off
REM ================================================================================
REM TELEGRAM NOTIFIER FIX - Complete Installation
REM ================================================================================
REM
REM This installer fixes the "TelegramNotifier not defined" error by:
REM 1. Creating missing directories
REM 2. Installing telegram_notifier.py
REM 3. Verifying installation
REM
REM No Git required - Direct file copy
REM ================================================================================

echo.
echo ================================================================================
echo TELEGRAM NOTIFIER FIX - Installation Starting
echo ================================================================================
echo.

REM Check if we're in the right directory
if not exist "models\screening\overnight_pipeline.py" (
    echo ERROR: Not in correct directory!
    echo.
    echo Please run this from: C:\Users\david\AATelS
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM ================================================================================
REM STEP 1: Create directories
REM ================================================================================
echo [STEP 1/4] Creating directory structure...
echo.

if not exist "models\notifications" (
    echo   Creating models\notifications\
    mkdir "models\notifications"
) else (
    echo   ✓ models\notifications\ already exists
)

REM Create __init__.py if missing
if not exist "models\notifications\__init__.py" (
    echo   Creating models\notifications\__init__.py
    echo. > "models\notifications\__init__.py"
) else (
    echo   ✓ models\notifications\__init__.py exists
)

echo.

REM ================================================================================
REM STEP 2: Backup existing file (if any)
REM ================================================================================
echo [STEP 2/4] Backing up existing files...
echo.

if exist "models\notifications\telegram_notifier.py" (
    set BACKUP_NAME=telegram_notifier.py.backup_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
    set BACKUP_NAME=%BACKUP_NAME: =0%
    echo   Backing up to: %BACKUP_NAME%
    copy "models\notifications\telegram_notifier.py" "models\notifications\%BACKUP_NAME%" >nul
    echo   ✓ Backup created
) else (
    echo   No existing file to backup
)

echo.

REM ================================================================================
REM STEP 3: Install TelegramNotifier
REM ================================================================================
echo [STEP 3/4] Installing telegram_notifier.py...
echo.

if not exist "telegram_notifier.py" (
    echo ERROR: telegram_notifier.py not found in fix package!
    echo.
    echo Please ensure you have:
    echo   - telegram_notifier.py (in this directory)
    echo.
    pause
    exit /b 1
)

echo   Copying telegram_notifier.py to models\notifications\
copy /Y "telegram_notifier.py" "models\notifications\telegram_notifier.py" >nul

if exist "models\notifications\telegram_notifier.py" (
    echo   ✓ File installed successfully
) else (
    echo   ✗ Installation failed
    pause
    exit /b 1
)

echo.

REM ================================================================================
REM STEP 4: Verify installation
REM ================================================================================
echo [STEP 4/4] Verifying installation...
echo.

REM Check file exists and has content
for %%A in (models\notifications\telegram_notifier.py) do (
    if %%~zA GTR 1000 (
        echo   ✓ telegram_notifier.py installed (%%~zA bytes^)
    ) else (
        echo   ✗ File appears incomplete
        pause
        exit /b 1
    )
)

REM Check for key content
findstr /C:"class TelegramNotifier" "models\notifications\telegram_notifier.py" >nul
if %ERRORLEVEL% EQU 0 (
    echo   ✓ TelegramNotifier class found
) else (
    echo   ✗ TelegramNotifier class not found in file
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo What was fixed:
echo   ✓ models\notifications\ directory created
echo   ✓ telegram_notifier.py installed
echo   ✓ TelegramNotifier class is now available
echo.
echo Next steps:
echo   1. Your pipeline should now work without the "TelegramNotifier" error
echo   2. Run: pipeline.bat
echo   3. Check Phase 8 for Telegram notification
echo.
echo Telegram configuration (in config\intraday_rescan_config.json):
echo   - "notifications.telegram.enabled": true
echo   - "notifications.telegram.bot_token": (your bot token)
echo   - "notifications.telegram.chat_id": (your chat ID)
echo.
echo If you still see errors, check:
echo   - logs\overnight_pipeline.log
echo   - config\intraday_rescan_config.json (Telegram section)
echo.
echo ================================================================================
echo.
pause
