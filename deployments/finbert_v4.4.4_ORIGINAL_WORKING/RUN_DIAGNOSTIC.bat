@echo off
echo =============================================
echo    FinBERT v3.3 - SYSTEM DIAGNOSTIC
echo =============================================
echo.
echo This will test all components and identify issues...
echo.

REM Run the diagnostic script
python diagnose_finbert.py

REM If that doesn't exist, try the fixed version
if errorlevel 1 (
    python diagnose_finbert_fixed.py
)

REM If Python isn't found, show error
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found or diagnostic script missing
    echo Please ensure Python is installed and in PATH
    echo.
)

echo.
echo =============================================
echo    DIAGNOSTIC COMPLETE
echo =============================================
echo.
pause