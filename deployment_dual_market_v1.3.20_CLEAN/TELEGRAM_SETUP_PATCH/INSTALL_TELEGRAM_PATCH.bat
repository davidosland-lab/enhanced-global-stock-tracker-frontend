@echo off
REM =====================================================================
REM TELEGRAM PATCH INSTALLER
REM =====================================================================
REM
REM This script installs the Telegram notification patch.
REM It does NOT configure credentials - use SETUP_TELEGRAM.bat for that.
REM
REM =====================================================================

echo.
echo ========================================================================
echo    TELEGRAM PATCH INSTALLER
echo ========================================================================
echo.

REM Check if we're in the right directory
if not exist "models\notifications\telegram_notifier.py" (
    echo.
    echo ======================================================================
    echo ERROR: Wrong directory!
    echo ======================================================================
    echo.
    echo This script must be run from: C:\Users\david\AATelS\
    echo.
    echo Current directory: %CD%
    echo.
    echo Please:
    echo   1. Extract TELEGRAM_SETUP_PATCH.zip to C:\Users\david\AATelS\
    echo   2. Open Command Prompt
    echo   3. Run: cd C:\Users\david\AATelS
    echo   4. Run: TELEGRAM_SETUP_PATCH\INSTALL_TELEGRAM_PATCH.bat
    echo.
    pause
    exit /b 1
)

echo This patch adds Telegram notification support.
echo.
echo What it does:
echo   - Verifies telegram_notifier.py is present
echo   - Checks Python dependencies (requests)
echo   - Updates requirements.txt if needed
echo   - Does NOT configure credentials (use SETUP_TELEGRAM.bat)
echo.
pause

echo.
echo Step 1: Checking telegram_notifier.py
echo ========================================================================
if exist "models\notifications\telegram_notifier.py" (
    echo ✓ telegram_notifier.py found
) else (
    echo ✗ telegram_notifier.py NOT found!
    echo.
    echo The notifier module should already exist in your system.
    echo Please check your installation.
    pause
    exit /b 1
)

echo.
echo Step 2: Checking Python
echo ========================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found in PATH
    echo Please install Python or add it to PATH
    pause
    exit /b 1
) else (
    python --version
    echo ✓ Python found
)

echo.
echo Step 3: Checking Dependencies
echo ========================================================================
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠ 'requests' module not installed
    echo.
    echo Installing requests...
    pip install requests
    if errorlevel 1 (
        echo ✗ Failed to install requests
        pause
        exit /b 1
    )
    echo ✓ requests installed
) else (
    echo ✓ requests module already installed
)

python -c "import dotenv" >nul 2>&1
if errorlevel 1 (
    echo ⚠ 'python-dotenv' module not installed
    echo.
    echo Installing python-dotenv...
    pip install python-dotenv
    if errorlevel 1 (
        echo ✗ Failed to install python-dotenv
        pause
        exit /b 1
    )
    echo ✓ python-dotenv installed
) else (
    echo ✓ python-dotenv module already installed
)

echo.
echo Step 4: Updating requirements.txt (optional)
echo ========================================================================
if exist "requirements.txt" (
    findstr /C:"python-dotenv" requirements.txt >nul
    if errorlevel 1 (
        echo Adding python-dotenv to requirements.txt...
        echo python-dotenv==1.0.0>>requirements.txt
        echo ✓ Added python-dotenv
    ) else (
        echo ✓ python-dotenv already in requirements.txt
    )
    
    findstr /C:"requests" requirements.txt >nul
    if errorlevel 1 (
        echo Adding requests to requirements.txt...
        echo requests==2.31.0>>requirements.txt
        echo ✓ Added requests
    ) else (
        echo ✓ requests already in requirements.txt
    )
) else (
    echo ⚠ requirements.txt not found (skipping)
)

echo.
echo ========================================================================
echo    INSTALLATION COMPLETE
echo ========================================================================
echo.
echo ✓ Telegram notifier module verified
echo ✓ Dependencies installed
echo ✓ System ready for Telegram notifications
echo.
echo IMPORTANT: This patch is installed, but NOT configured yet!
echo.
echo To configure Telegram notifications:
echo   1. Run: TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
echo   2. Follow the interactive prompts
echo   3. Get your bot token from @BotFather
echo   4. Get your chat ID
echo   5. Test with: python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
echo.
echo Or see: TELEGRAM_SETUP_PATCH\README.txt for manual setup
echo.
echo ========================================================================
echo.
pause
