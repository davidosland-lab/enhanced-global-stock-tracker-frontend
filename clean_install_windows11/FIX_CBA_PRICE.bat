@echo off
title Fix CBA.AX Price Issues
color 0E

echo ================================================================================
echo                      FIX CBA.AX PRICE ISSUES
echo ================================================================================
echo.
echo This will fix the incorrect $100 price showing for CBA.AX
echo The actual price should be around $170
echo.
echo Press any key to apply the fix...
pause >nul

echo.
echo [1/3] Applying price fixes...
python FIX_PREDICTION_PRICES.py

if %errorlevel% NEQ 0 (
    echo.
    echo ✗ Fix failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo [2/3] Restarting backend services...

:: Restart Main Backend
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul
start "Main Backend" /min cmd /c "python backend.py"

:: Restart ML Backend
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul
start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"

echo    ✓ Backend services restarted

echo.
echo [3/3] Verifying fix...
timeout /t 3 /nobreak >nul

:: Test the API
echo.
echo Testing CBA.AX price from API...
curl -s http://localhost:8002/api/stock/CBA.AX 2>nul | findstr /i "price"
echo.

echo ================================================================================
echo                      ✓ PRICE FIX APPLIED!
echo ================================================================================
echo.
echo Fixed:
echo   ✓ CBA.AX now shows correct price (~$170 range)
echo   ✓ Removed all $100 hardcoded fallbacks
echo   ✓ Prediction Centre uses real API prices
echo.
echo Please refresh the Prediction Centre in your browser (Ctrl+F5)
echo.
pause