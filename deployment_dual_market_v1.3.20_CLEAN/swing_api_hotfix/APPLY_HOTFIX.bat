@echo off
REM Swing API Hotfix - Fix HistoricalDataLoader Error

echo.
echo ============================================================
echo   Swing API Hotfix
echo   Fixes: HistoricalDataLoader initialization error
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Run fix script
python fixes\fix_swing_endpoint.py %*

exit /b %errorlevel%
