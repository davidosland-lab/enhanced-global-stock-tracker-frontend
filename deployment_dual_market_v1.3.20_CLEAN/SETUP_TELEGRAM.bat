@echo off
REM ===================================================================
REM FinBERT - Telegram Setup Helper
REM ===================================================================

echo ========================================
echo   FinBERT Telegram Setup
echo ========================================
echo.

echo This script will help you configure Telegram alerts.
echo.
echo STEP 1: Create a Telegram Bot
echo ----------------------------------------
echo 1. Open Telegram and search for @BotFather
echo 2. Send: /newbot
echo 3. Follow instructions to create your bot
echo 4. Copy the BOT TOKEN you receive
echo.
pause
echo.

echo STEP 2: Get Your Chat ID
echo ----------------------------------------
echo 1. Start a chat with your new bot (click the link from BotFather)
echo 2. Send any message to your bot (e.g., "Hello")
echo 3. Open this URL in your browser:
echo    https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
echo    (Replace YOUR_BOT_TOKEN with your actual token)
echo 4. Look for "chat":{"id": XXXXXXXXX
echo 5. Copy that number (your CHAT ID)
echo.
pause
echo.

echo STEP 3: Enter Your Credentials
echo ----------------------------------------
echo.
set /p BOT_TOKEN="Enter your Bot Token: "
set /p CHAT_ID="Enter your Chat ID: "
echo.

echo Updating .env file...
echo.

REM Create or update .env file
(
echo # FinBERT Telegram Configuration
echo TELEGRAM_BOT_TOKEN=%BOT_TOKEN%
echo TELEGRAM_CHAT_ID=%CHAT_ID%
) > .env

echo.
echo ========================================
echo   Configuration Complete!
echo ========================================
echo.
echo Your credentials have been saved to .env
echo.
echo NEXT STEPS:
echo 1. Run: python test_telegram.py
echo    (This will test your Telegram connection)
echo.
echo 2. If test successful, run:
echo    RUN_INTRADAY_MONITOR_US.bat (for US market)
echo    RUN_INTRADAY_MONITOR_ASX.bat (for ASX market)
echo.
pause
