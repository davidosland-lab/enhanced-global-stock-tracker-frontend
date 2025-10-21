@echo off
REM ============================================================
REM START CLEAN SERVER - NO ENCODING ISSUES
REM ============================================================

title ML Stock Predictor - Clean Server
color 0A
cls

echo ============================================================
echo    ML STOCK PREDICTOR - CLEAN SERVER
echo ============================================================
echo.
echo This server has no encoding issues and will work on Windows 11
echo.

REM Set UTF-8 encoding for Windows console
chcp 65001 >nul 2>&1

REM Set Python to use UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Kill any process on port 8000
echo Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Starting clean server...
echo.

python server_clean.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo Server failed to start!
    echo.
    echo Trying with explicit UTF-8 mode...
    python -X utf8 server_clean.py
)

echo.
echo Server stopped.
pause