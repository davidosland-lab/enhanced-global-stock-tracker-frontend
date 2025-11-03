@echo off
echo ================================================================
echo    ECONOMIC DATA TEST
echo ================================================================
echo.

REM Check if venv exists and activate it
if exist venv (
    echo Using virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python...
)

echo.
python TEST_ECONOMIC_DATA.py

pause