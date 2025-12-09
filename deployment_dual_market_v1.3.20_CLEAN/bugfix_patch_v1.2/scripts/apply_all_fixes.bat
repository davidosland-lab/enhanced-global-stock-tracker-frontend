@echo off
chcp 65001 >nul
echo.
echo =========================================
echo FinBERT v4.4.4 - Bug Fix Patch v1.2
echo NO MOCK DATA - REAL DATA ONLY
echo =========================================
echo.
echo This patch fixes:
echo [1] Removes mock sentiment from app
echo [2] Disables broken LSTM temporarily
echo [3] Removes mock sentiment from LSTM predictor
echo [4] Fixes ADX calculation crashes
echo.
pause

python "%~dp0apply_all_fixes.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Patch installation failed
    pause
    exit /b 1
)

echo.
echo =========================================
echo Patch Installation Complete!
echo =========================================
pause
