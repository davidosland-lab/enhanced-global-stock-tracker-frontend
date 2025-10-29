@echo off
echo ================================================================
echo    TESTING CBA.AX SMA_50 FIX
echo ================================================================
echo.

REM Check if venv exists
if exist venv (
    echo Using existing virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python...
)

echo.
echo Running CBA.AX fix verification...
echo.

python TEST_CBA_FIX.py

echo.
echo ================================================================
echo Test completed!
echo.
echo To use the fixed system:
echo   1. Run INSTALL_ULTIMATE.bat (if not done)
echo   2. Run RUN_ULTIMATE.bat
echo   3. Train CBA.AX with 6 months or 1 year
echo   4. Make prediction - no more SMA_50 errors!
echo ================================================================
echo.
pause