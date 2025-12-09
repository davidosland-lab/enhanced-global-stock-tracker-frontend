@echo off
REM Bug Fix Patch v1.2 - Windows Installer
REM Fixes: SyntaxError + Mock + ADX + LSTM

echo.
echo ============================================================
echo   Bug Fix Patch v1.2 Installer
echo   Fixes: SyntaxError + Mock Data + ADX + LSTM
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Run installer
python "%~dp0apply_all_fixes.py" %*

exit /b %errorlevel%
