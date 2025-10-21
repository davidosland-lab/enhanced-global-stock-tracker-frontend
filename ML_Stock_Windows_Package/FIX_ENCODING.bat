@echo off
REM ============================================================
REM FIX ENCODING ISSUES
REM ============================================================

title Fix Encoding Issues
color 0E
cls

echo ============================================================
echo    FIX UTF-8 ENCODING ISSUES
echo ============================================================
echo.
echo This will fix encoding problems that prevent server startup
echo.

REM Set UTF-8 mode
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Installing encoding detection tool...
pip install chardet >nul 2>&1

echo.
echo Running encoding fix...
python fix_encoding.py

echo.
echo ============================================================
echo    ENCODING FIX COMPLETE
echo ============================================================
echo.
echo Now try running:
echo   START_CLEAN.bat
echo.
echo This should start the server without encoding errors.
echo.
pause