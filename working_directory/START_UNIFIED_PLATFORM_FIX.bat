@echo off
REM Quick Fix for Unicode Error in Unified Trading Platform

echo Fixing Unicode encoding issue...

cd /d "%~dp0"

REM Set UTF-8 encoding for Python
set PYTHONIOENCODING=utf-8

echo.
echo Starting Unified Trading Platform with UTF-8 encoding...
echo.

python unified_trading_platform.py --paper-trading

pause
