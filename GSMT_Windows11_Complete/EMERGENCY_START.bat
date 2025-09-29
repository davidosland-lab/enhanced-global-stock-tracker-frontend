@echo off
:: EMERGENCY START - This WILL work
:: Try multiple server options until one works

title GSMT Emergency Start
color 0E
cls

echo ================================================================
echo           GSMT STOCK TRACKER - EMERGENCY START
echo              This will try multiple options
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install from: https://www.python.org
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

:: Option 1: Try ultra simple server
echo [1] Trying ultra_simple_server.py...
if exist "backend\ultra_simple_server.py" (
    echo Starting ultra simple server...
    python backend\ultra_simple_server.py
    echo.
    echo Server stopped or failed.
    echo.
)

:: Option 2: Try main server
echo [2] Trying main_server.py...
if exist "backend\main_server.py" (
    echo Starting main server...
    python backend\main_server.py
    echo.
    echo Server stopped or failed.
    echo.
)

:: Option 3: Try test server
echo [3] Trying test_server.py...
if exist "backend\test_server.py" (
    echo Starting test server...
    python backend\test_server.py
    echo.
    echo Server stopped or failed.
    echo.
)

:: Option 4: Try simple ML backend
echo [4] Trying simple_ml_backend.py...
if exist "backend\simple_ml_backend.py" (
    echo Starting simple ML backend...
    python backend\simple_ml_backend.py
    echo.
    echo Server stopped or failed.
    echo.
)

:: If we get here, nothing worked
echo.
echo ================================================================
echo ALL SERVERS FAILED!
echo.
echo Please try:
echo 1. Run: pip install fastapi uvicorn
echo 2. Run: python TEST_INSTALLATION.py
echo 3. Check error messages above
echo ================================================================
echo.
pause