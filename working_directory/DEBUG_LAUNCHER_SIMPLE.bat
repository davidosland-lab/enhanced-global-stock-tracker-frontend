@echo off
REM ============================================================================
REM ULTRA-SIMPLE LAUNCHER - v1.3.15.59 DEBUG VERSION
REM ============================================================================
REM This is a minimal version to test what's working
REM ============================================================================

echo.
echo ========================================================================
echo   ULTRA-SIMPLE LAUNCHER - DEBUG MODE
echo ========================================================================
echo.

REM Test 1: Show current directory
echo [TEST 1] Current Directory
echo %CD%
echo.

REM Test 2: Check Python
echo [TEST 2] Python Check
python --version 2>nul
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found in PATH
    echo Trying venv Python...
    IF EXIST "venv\Scripts\python.exe" (
        venv\Scripts\python.exe --version
        echo [OK] Found venv Python
    ) ELSE (
        echo [ERROR] No Python found
    )
) ELSE (
    echo [OK] System Python found
)
echo.

REM Test 3: Check for key files
echo [TEST 3] Key Files Check
IF EXIST "unified_trading_dashboard.py" (
    echo [OK] unified_trading_dashboard.py exists
) ELSE (
    echo [ERROR] unified_trading_dashboard.py NOT FOUND
)

IF EXIST "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment exists
) ELSE (
    echo [WARN] No virtual environment
)
echo.

REM Test 4: Try to start dashboard with minimal setup
echo [TEST 4] Attempting to start dashboard...
echo.
echo Press Ctrl+C to stop, or close window
echo.

IF EXIST "venv\Scripts\python.exe" (
    echo Using venv Python...
    venv\Scripts\python.exe unified_trading_dashboard.py
) ELSE (
    echo Using system Python...
    python unified_trading_dashboard.py
)

echo.
echo Dashboard stopped or failed to start
pause
