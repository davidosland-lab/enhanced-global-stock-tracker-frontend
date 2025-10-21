@echo off
echo Starting Stock Analysis System...
echo.

REM Prevent dotenv UTF-8 errors
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

REM Change to UTF-8 code page
chcp 65001 >nul 2>&1

REM Start the server
python unified_stock_system_local.py

pause