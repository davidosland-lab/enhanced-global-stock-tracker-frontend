@echo off
REM Fix Intraday Monitor Syntax Error on Windows
REM =============================================

echo.
echo ================================================================================
echo   FIXING INTRADAY MONITOR SYNTAX ERROR
echo ================================================================================
echo.

cd /d C:\Users\david\AATelS

REM Check if we're in a git repo
git status >nul 2>&1
if errorlevel 1 (
    echo [WARNING] This directory is not a git repository or git remote is not configured
    echo.
    echo MANUAL FIX REQUIRED:
    echo.
    goto MANUAL_FIX
)

echo [1/3] Fetching latest changes from repository...
git fetch origin main
if errorlevel 1 (
    echo [ERROR] Failed to fetch from origin
    goto MANUAL_FIX
)

echo [2/3] Pulling latest changes...
git pull origin main
if errorlevel 1 (
    echo [ERROR] Failed to pull changes
    goto MANUAL_FIX
)

echo [3/3] Verifying syntax...
python -m py_compile models\scheduling\intraday_rescan_manager.py
if errorlevel 1 (
    echo [ERROR] Syntax error still present
    goto MANUAL_FIX
)

echo.
echo ================================================================================
echo   SUCCESS! File has been fixed
echo ================================================================================
echo.
echo You can now run the intraday monitor:
echo   python models\scheduling\intraday_scheduler.py
echo.
pause
exit /b 0

:MANUAL_FIX
echo.
echo ================================================================================
echo   MANUAL FIX REQUIRED
echo ================================================================================
echo.
echo Please follow these steps:
echo.
echo 1. Open this file in a text editor:
echo    C:\Users\david\AATelS\models\scheduling\intraday_rescan_manager.py
echo.
echo 2. Go to line 342 and make sure it looks EXACTLY like this:
echo    """Reset session state (for new day)"""
echo    (THREE quotes at start and end)
echo.
echo 3. Go to line 352 and make sure it looks EXACTLY like this:
echo    """Test intraday rescan manager"""
echo    (THREE quotes at start and end)
echo.
echo 4. Save the file and run this command to verify:
echo    python -m py_compile models\scheduling\intraday_rescan_manager.py
echo.
echo If you see NO output, the file is fixed!
echo.
echo ================================================================================
echo.
pause
exit /b 1
