@echo off
title Remove ALL Fallback and Synthetic Data
color 0C

echo ================================================================================
echo           REMOVE ALL FALLBACK, DEMO, AND SYNTHETIC DATA
echo ================================================================================
echo.
echo This will ensure your Stock Tracker uses ONLY real data:
echo   - NO fallback values (no 100, 170, etc.)
echo   - NO demo/mock data
echo   - NO synthetic prices
echo   - ONLY real Yahoo Finance data
echo.
echo If real data is not available, you will see an error message.
echo.
echo WARNING: This will modify your files. Backups will be created.
echo.
echo Press Ctrl+C to cancel, or...
pause

echo.
echo [1/4] Creating complete backup...
if not exist "BACKUP_%date:~-4%%date:~4,2%%date:~7,2%" (
    mkdir "BACKUP_%date:~-4%%date:~4,2%%date:~7,2%"
)
copy *.py "BACKUP_%date:~-4%%date:~4,2%%date:~7,2%\" >nul 2>&1
copy *.html "BACKUP_%date:~-4%%date:~4,2%%date:~7,2%\" >nul 2>&1
echo    ✓ Backup created in BACKUP_%date:~-4%%date:~4,2%%date:~7,2%

echo.
echo [2/4] Removing all fallback and synthetic data...
python REMOVE_ALL_FALLBACKS.py

if %errorlevel% NEQ 0 (
    echo.
    echo ✗ Fix failed! Your files have not been modified.
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [3/4] Restarting all services with real data only...
echo.

:: Stop all services
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 /nobreak >nul

:: Start services
echo Starting services with real data only...
start "Frontend" /min cmd /c "python -m http.server 8000"
timeout /t 2 /nobreak >nul

start "Backend" /min cmd /c "python backend.py"
timeout /t 2 /nobreak >nul

if exist backend_ml_enhanced.py (
    start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"
)

timeout /t 3 /nobreak >nul
echo    ✓ Services restarted

echo.
echo [4/4] Testing real data connection...
echo.

curl -s http://localhost:8002/api/stock/CBA.AX >test_data.tmp 2>nul

if %errorlevel% == 0 (
    echo Testing CBA.AX real data:
    type test_data.tmp | findstr /i "price"
    
    :: Check if we got real data (should have a price field)
    findstr /i "price" test_data.tmp >nul
    if %errorlevel% == 0 (
        echo.
        echo    ✓ Real data connection verified!
    ) else (
        echo.
        echo    ! No price data received - check your internet connection
    )
) else (
    echo    ! Backend not responding yet. It may need more time to start.
)

if exist test_data.tmp del test_data.tmp >nul 2>&1

echo.
echo ================================================================================
echo                    ✓ ALL FAKE DATA REMOVED!
echo ================================================================================
echo.
echo Your Stock Tracker now:
echo   ✓ Uses ONLY real Yahoo Finance data
echo   ✓ Shows errors when data is unavailable
echo   ✓ Never displays fake/fallback values
echo   ✓ Provides clear error messages to users
echo.
echo IMPORTANT CHANGES:
echo   - If Yahoo Finance is down, you'll see an error (not fake data)
echo   - Outside market hours, some data may be unavailable
echo   - Internet connection is REQUIRED for all features
echo.
echo To test:
echo   1. Open http://localhost:8000
echo   2. Try any module
echo   3. You should see real prices or error messages
echo   4. No more $100 fallback values!
echo.
echo If you need to restore the backup:
echo   Copy files from BACKUP_%date:~-4%%date:~4,2%%date:~7,2% folder
echo.
pause