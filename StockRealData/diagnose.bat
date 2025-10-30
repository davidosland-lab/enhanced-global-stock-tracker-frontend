@echo off
cls
echo ============================================================
echo    API CONNECTION DIAGNOSTICS
echo ============================================================
echo.
echo This will test why Yahoo Finance and Alpha Vantage are failing.
echo.

REM Use venv Python if available
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON_EXE=python
    echo Using system Python
)

echo.
%PYTHON_EXE% test_apis.py

pause