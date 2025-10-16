@echo off
REM ============================================
REM ML Core System Test Script
REM ============================================

echo.
echo ============================================
echo TESTING ML CORE SYSTEM
echo ============================================
echo.

REM Activate virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run install_windows.bat first
    pause
    exit /b 1
)

REM Run the test script
echo Running system tests...
python test_ml_comprehensive.py

echo.
echo ============================================
echo Test complete!
echo ============================================
pause