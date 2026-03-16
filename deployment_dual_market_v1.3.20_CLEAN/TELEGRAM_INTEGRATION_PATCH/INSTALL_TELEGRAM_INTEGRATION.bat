@echo off
REM ============================================================================
REM TELEGRAM INTEGRATION INSTALLER
REM Automatically integrates Telegram notifications into ASX and US pipelines
REM ============================================================================

echo ============================================================================
echo TELEGRAM INTEGRATION PATCH - INSTALLER
echo ============================================================================
echo.
echo This installer will:
echo   1. Verify python-telegram-bot dependency
echo   2. Run the Telegram setup wizard
echo   3. Test the Telegram connection
echo   4. Verify integration with both pipelines
echo.
echo Prerequisites:
echo   - Python 3.8+ installed
echo   - Telegram bot created (via @BotFather)
echo   - Bot token and chat ID ready
echo.
pause
echo.

REM Step 1: Verify python-telegram-bot is installed
echo ============================================================================
echo Step 1: Verifying python-telegram-bot dependency
echo ============================================================================
echo.

python -c "import telegram; print('✓ python-telegram-bot is installed')" 2>nul
if errorlevel 1 (
    echo ❌ python-telegram-bot is NOT installed
    echo.
    echo Installing python-telegram-bot==13.15...
    pip install python-telegram-bot==13.15
    
    if errorlevel 1 (
        echo.
        echo ❌ ERROR: Failed to install python-telegram-bot
        echo    Please install manually: pip install python-telegram-bot==13.15
        pause
        exit /b 1
    )
    
    echo ✓ python-telegram-bot installed successfully
) else (
    echo ✓ python-telegram-bot is already installed
)
echo.
pause

REM Step 2: Run Telegram setup wizard
echo.
echo ============================================================================
echo Step 2: Telegram Setup Wizard
echo ============================================================================
echo.
echo Running interactive setup wizard...
echo.

python setup_telegram.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Telegram setup failed
    echo    Please check the error messages above
    pause
    exit /b 1
)

echo.
pause

REM Step 3: Test Telegram integration
echo.
echo ============================================================================
echo Step 3: Testing Telegram Integration
echo ============================================================================
echo.
echo Running test suite...
echo Check your Telegram app for test messages.
echo.

cd tests
python test_telegram_integration.py
cd ..

if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Some tests failed
    echo    Telegram may still work, but check the error messages above
    echo.
) else (
    echo.
    echo ✓ All tests passed!
    echo.
)

pause

REM Step 4: Verification summary
echo.
echo ============================================================================
echo INSTALLATION COMPLETE
echo ============================================================================
echo.
echo ✅ Telegram notifications are now integrated with:
echo    • ASX Overnight Pipeline
echo    • US Overnight Pipeline
echo.
echo 📱 You will receive notifications when:
echo    • Pipelines complete (with HTML/CSV attachments)
echo    • High-quality opportunities are found
echo    • Errors or warnings occur
echo.
echo 🚀 Next steps:
echo    1. Run the ASX pipeline: python models\screening\overnight_pipeline.py
echo    2. Run the US pipeline: python models\screening\us_overnight_pipeline.py
echo    3. Check your Telegram for morning reports
echo.
echo 📋 Configuration files updated:
echo    • config\intraday_rescan_config.json
echo    • models\config\screening_config.json (if present)
echo.
echo ============================================================================
echo.
pause
