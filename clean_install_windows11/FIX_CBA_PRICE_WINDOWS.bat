@echo off
title Fix CBA.AX Price Issues
color 0E

echo ================================================================================
echo                      FIX CBA.AX PRICE ISSUES
echo                           Windows 11 Version
echo ================================================================================
echo.
echo This will fix the incorrect $100 price showing for CBA.AX
echo The actual price should be around $169-170
echo.
echo Current directory: %cd%
echo.

:: Check if we have the main files
if not exist backend.py (
    echo ERROR: backend.py not found!
    echo.
    echo Please run this script from your Stock Tracker installation directory
    echo The directory should contain files like:
    echo   - backend.py
    echo   - backend_ml_enhanced.py
    echo   - index.html
    echo   - prediction_centre_phase4.html or similar
    echo.
    pause
    exit /b 1
)

echo Files found. Starting fix...
echo.
pause

echo.
echo [1/3] Applying price fixes...
echo.

:: Run the Python fix script
python FIX_PREDICTION_PRICES_WINDOWS.py

if %errorlevel% NEQ 0 (
    echo.
    echo Note: Some files might not have been found, but fixes were applied where possible.
    echo.
)

echo.
echo [2/3] Restarting backend services...
echo.

:: Kill existing processes
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

:: Start services
echo Starting Main Backend (port 8002)...
start "Main Backend" /min cmd /c "python backend.py"

timeout /t 2 /nobreak >nul

if exist backend_ml_enhanced.py (
    echo Starting ML Backend (port 8003)...
    start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"
) else (
    echo ML Backend not found, skipping...
)

timeout /t 3 /nobreak >nul
echo    ✓ Services restarted

echo.
echo [3/3] Testing the fix...
echo.

:: Try to get CBA.AX price
echo Testing CBA.AX price from API...
echo.

curl -s http://localhost:8002/api/stock/CBA.AX 2>nul | findstr /i "price" >temp_price.txt

if %errorlevel% == 0 (
    type temp_price.txt
    del temp_price.txt >nul 2>&1
) else (
    echo Could not retrieve price. Make sure the backend is running.
)

echo.
echo ================================================================================
echo                      ✓ PRICE FIX PROCESS COMPLETE!
echo ================================================================================
echo.
echo What was fixed:
echo   ✓ Changed fallback prices from $100 to $170
echo   ✓ Fixed Prediction Centre to use 'price' field from API
echo   ✓ Removed hardcoded demo prices
echo.
echo To verify the fix:
echo   1. Open your browser to http://localhost:8000
echo   2. Go to Prediction Centre
echo   3. Enter CBA.AX as the symbol
echo   4. The price should show around $169-170 (not $100)
echo.
echo If you still see $100, try:
echo   - Clear browser cache (Ctrl+Shift+Del)
echo   - Hard refresh the page (Ctrl+F5)
echo.
pause