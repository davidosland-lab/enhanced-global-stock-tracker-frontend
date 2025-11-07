@echo off
echo ================================================================
echo    PRICE PREDICTION FEATURE TEST
echo ================================================================
echo.
echo This tests the new price estimation and timeframe features
echo.

REM Check if venv exists and activate it
if exist venv (
    echo Using virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python...
)

echo.
python TEST_PRICE_PREDICTION.py

pause