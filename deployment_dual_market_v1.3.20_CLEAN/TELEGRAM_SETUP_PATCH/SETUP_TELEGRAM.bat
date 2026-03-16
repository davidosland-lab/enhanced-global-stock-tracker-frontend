@echo off
REM =====================================================================
REM TELEGRAM SETUP FOR OVERNIGHT STOCK SCREENER
REM =====================================================================
REM
REM This script will guide you through setting up Telegram notifications
REM for your stock screening system.
REM
REM Prerequisites:
REM   - Telegram app installed on your phone/desktop
REM   - 5-10 minutes of time
REM
REM =====================================================================

echo.
echo ========================================================================
echo    TELEGRAM NOTIFICATION SETUP
echo ========================================================================
echo.
echo This setup will enable:
echo   - Real-time breakout alerts
echo   - Morning/overnight reports via Telegram
echo   - Pipeline status notifications
echo   - Zero cost notifications (no SMS/email fees)
echo.
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
    echo   4. Run: TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
    echo.
    pause
    exit /b 1
)

echo Step 1: CREATE YOUR TELEGRAM BOT
echo ========================================================================
echo.
echo 1. Open Telegram on your phone or desktop
echo 2. Search for: @BotFather
echo 3. Start a chat with BotFather
echo 4. Send the command: /newbot
echo 5. Follow the prompts to:
echo    - Choose a name for your bot (e.g., "My Stock Screener Bot")
echo    - Choose a username (must end in 'bot', e.g., "mystock_screener_bot")
echo.
echo BotFather will give you a TOKEN that looks like:
echo    123456789:ABCdefGhIjKlMnOpQrStUvWxYz
echo.
pause
echo.

echo Step 2: GET YOUR CHAT ID
echo ========================================================================
echo.
echo 1. Search for your bot in Telegram (use the username you just created)
echo 2. Start a chat with your bot
echo 3. Send any message to your bot (e.g., "Hello")
echo.
echo 4. Now, open this URL in your browser (replace YOUR_BOT_TOKEN):
echo.
echo    https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
echo.
echo    Example:
echo    https://api.telegram.org/bot123456789:ABCdefGhIjKlMnOpQrStUvWxYz/getUpdates
echo.
echo 5. Look for "chat":{"id": in the response
echo    Your CHAT_ID is the number after "id": (e.g., 123456789)
echo.
pause
echo.

echo Step 3: CONFIGURE CREDENTIALS
echo ========================================================================
echo.
echo Now let's add your credentials to the system.
echo.

REM Prompt for bot token
set /p BOT_TOKEN="Enter your BOT TOKEN: "
if "%BOT_TOKEN%"=="" (
    echo.
    echo ERROR: Bot token cannot be empty!
    pause
    exit /b 1
)

REM Prompt for chat ID
set /p CHAT_ID="Enter your CHAT ID: "
if "%CHAT_ID%"=="" (
    echo.
    echo ERROR: Chat ID cannot be empty!
    pause
    exit /b 1
)

echo.
echo Saving credentials...
echo.

REM Update or create telegram.env
(
    echo TELEGRAM_BOT_TOKEN=%BOT_TOKEN%
    echo TELEGRAM_CHAT_ID=%CHAT_ID%
) > telegram.env

echo ✓ Credentials saved to telegram.env
echo.

echo Step 4: UPDATE CONFIGURATION FILES
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Python not found in PATH
    echo.
    echo Manual configuration required:
    echo   1. Open: models\config\screening_config.json
    echo   2. Add the telegram_notifications section from:
    echo      TELEGRAM_SETUP_PATCH\config\screening_config_telegram_patch.json
    echo   3. Update bot_token and chat_id with your credentials
    echo.
    pause
) else (
    echo Updating configuration files with Python...
    python TELEGRAM_SETUP_PATCH\update_config.py "%BOT_TOKEN%" "%CHAT_ID%"
    if errorlevel 1 (
        echo.
        echo WARNING: Auto-configuration failed
        echo Please manually update config files (see docs)
        echo.
    ) else (
        echo ✓ Configuration files updated
        echo.
    )
)

echo Step 5: TEST YOUR SETUP
echo ========================================================================
echo.
echo Let's test the Telegram connection...
echo.
pause

REM Run test script
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
if errorlevel 1 (
    echo.
    echo ✗ Test failed! Please check your credentials.
    echo.
    echo Troubleshooting:
    echo   1. Verify your bot token is correct
    echo   2. Verify your chat ID is correct
    echo   3. Make sure you sent a message to your bot first
    echo   4. Check internet connection
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    SETUP COMPLETE!
echo ========================================================================
echo.
echo ✓ Telegram bot created
echo ✓ Credentials configured
echo ✓ Connection tested successfully
echo.
echo Your bot is ready! You should have received test messages in Telegram.
echo.
echo What happens next:
echo   - When the overnight pipeline runs, you'll get a morning report
echo   - Real-time breakout alerts will be sent as they occur
echo   - Pipeline status notifications will keep you informed
echo.
echo To test with a real report:
echo   cd C:\Users\david\AATelS
echo   python models\screening\us_overnight_pipeline.py --test-mode
echo.
echo ========================================================================
echo.
pause
