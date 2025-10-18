@echo off
echo ============================================================
echo Sentiment Analysis Control Panel
echo ============================================================
echo.

echo Current Status:
python toggle_sentiment.py
echo.

echo ============================================================
echo Options:
echo   1. Disable Sentiment (Safe Mode - Recommended)
echo   2. Enable Sentiment (May cause Yahoo Finance issues)
echo   3. Show Current Status Only
echo   4. Exit
echo ============================================================
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    python toggle_sentiment.py off
    echo.
    echo ✅ Sentiment disabled - System will use 35 technical features
)
if "%choice%"=="2" (
    echo.
    echo WARNING: Enabling sentiment may cause Yahoo Finance rate limiting!
    set /p confirm="Are you sure? (y/n): "
    if /i "%confirm%"=="y" (
        python toggle_sentiment.py on
        echo.
        echo ⚠️  Sentiment enabled - Monitor for connection issues
    )
)
if "%choice%"=="3" (
    echo.
    python toggle_sentiment.py
)

echo.
pause