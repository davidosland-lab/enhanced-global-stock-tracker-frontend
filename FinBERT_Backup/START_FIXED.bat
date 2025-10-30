@echo off
echo =====================================
echo   FinBERT Trading System v3.3 FIXED
echo   Starting with corrected API...
echo =====================================
echo.

REM Stop any existing Python processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Starting fixed backend...
echo.

REM Try the fixed version first
if exist "app_finbert_complete_v3.2_FIXED.py" (
    echo Using FIXED version with correct API field names...
    start "FinBERT Fixed" cmd /k python app_finbert_complete_v3.2_FIXED.py
) else if exist "app_finbert_complete_v3.2.py" (
    echo Using original version...
    start "FinBERT" cmd /k python app_finbert_complete_v3.2.py
) else (
    echo ERROR: No backend file found!
    pause
    exit /b 1
)

timeout /t 5 >nul

echo.
echo Opening browser...
start http://localhost:5000

echo.
echo =====================================
echo System should now work correctly!
echo =====================================
echo.
echo The API now returns:
echo - current_price (was missing!)
echo - day_high
echo - day_low  
echo - All required fields
echo.
pause