@echo off
REM Bug Fix Patch v1.3 - Windows Installer

echo.
echo ============================================================
echo   Bug Fix Patch v1.3 Installer
echo   Fixes: SyntaxError + Config + Mock + ADX
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

python "%~dp0apply_all_fixes.py" %*
exit /b %errorlevel%
