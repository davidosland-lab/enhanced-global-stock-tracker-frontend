@echo off
echo.
echo =============================================
echo    FinBERT v3.3 - TROUBLESHOOTING TOOL
echo =============================================
echo.

echo If you're seeing errors like:
echo - Price showing as 0.00
echo - Charts not loading
echo - "Cannot read properties of undefined"
echo.
echo This tool will help fix them!
echo.
pause

echo.
echo STEP 1: Stopping any running backend...
echo.
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app_finbert*" >nul 2>&1
timeout /t 2 >nul

echo STEP 2: Clearing Python cache...
echo.
if exist "__pycache__" rd /s /q "__pycache__"
if exist ".pytest_cache" rd /s /q ".pytest_cache"

echo STEP 3: Testing network connection...
echo.
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No internet connection detected
    echo Please check your internet connection
    pause
    exit /b 1
)
echo [OK] Internet connection working

echo.
echo STEP 4: Starting HOTFIX backend...
echo.
echo The hotfix backend includes:
echo - Better error handling
echo - Fallback data when APIs fail
echo - Fixed 3m interval support
echo - Handles zero price issues
echo.

REM Check if hotfix exists, if not use regular backend
if exist "app_finbert_v3.3_hotfix.py" (
    echo Starting HOTFIX version...
    start "FinBERT v3.3 HOTFIX" cmd /k "python app_finbert_v3.3_hotfix.py"
) else (
    echo Hotfix not found, starting regular version...
    start "FinBERT v3.3" cmd /k "python app_finbert_complete_v3.2.py"
)

timeout /t 5 >nul

echo.
echo STEP 5: Opening browser...
echo.
start http://localhost:5000

echo.
echo =============================================
echo    TROUBLESHOOTING COMPLETE
echo =============================================
echo.
echo The system should now be working!
echo.
echo If you still see issues:
echo 1. Clear browser cache (Ctrl+Shift+Delete)
echo 2. Try a different browser
echo 3. Try a different stock symbol (MSFT, GOOGL)
echo 4. Check the console window for errors
echo.
pause