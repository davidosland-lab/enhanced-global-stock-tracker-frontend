@echo off
REM Bug Fix Patch v1.0 - Windows Installer
REM Applies all fixes automatically

echo ======================================================================
echo Bug Fix Patch v1.0 - Master Installer
echo Fixes app errors WITHOUT adding fake/mock data
echo ======================================================================
echo.

REM Get base path
set /p BASE_PATH="Enter FinBERT installation path (e.g., C:\Users\david\AATelS): "

REM Remove trailing backslash
if "%BASE_PATH:~-1%"=="\" set BASE_PATH=%BASE_PATH:~0,-1%

REM Verify path
if not exist "%BASE_PATH%\" (
    echo ERROR: Path not found: %BASE_PATH%
    pause
    exit /b 1
)

if not exist "%BASE_PATH%\finbert_v4.4.4\" (
    echo ERROR: FinBERT v4.4.4 not found in: %BASE_PATH%
    pause
    exit /b 1
)

echo [OK] FinBERT installation found
echo.

REM Run master installer
python "%~dp0apply_all_fixes.py" "%BASE_PATH%"

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Installation Complete!
echo ======================================================================
echo.
echo Next steps:
echo 1. Restart FinBERT server
echo 2. Test stock analysis (should work without crashes)
echo 3. Swing backtest still works independently
echo.
pause
