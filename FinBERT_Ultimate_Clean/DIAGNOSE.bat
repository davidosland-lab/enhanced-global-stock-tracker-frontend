@echo off
echo ================================================================
echo    INSTALLATION DIAGNOSTIC TOOL
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
python DIAGNOSE_TRANSFORMERS.py

pause