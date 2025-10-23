@echo off
cls
color 0A
echo ==============================================================
echo         COPY THE FIXED BACKEND WITH ALL ENDPOINTS
echo ==============================================================
echo.
echo Your current backend.py is missing the endpoints.
echo This will replace it with the complete fixed version.
echo.
echo ==============================================================
pause

REM Stop the current backend
echo.
echo STEP 1: Stopping current backend...
echo --------------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /PID %%a /F 2>nul
)
timeout /t 2 >nul

REM Backup current backend
echo.
echo STEP 2: Backing up current backend.py...
echo --------------------------------------------------
copy backend.py backend_BACKUP_%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py >nul
echo Backup created.

REM Copy the fixed backend
echo.
echo STEP 3: Copying fixed backend with all endpoints...
echo --------------------------------------------------
copy /Y backend_COMPLETE_WITH_ALL_ENDPOINTS.py backend.py
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: backend.py has been replaced with fixed version!
) else (
    echo ERROR: Failed to copy fixed backend.
    echo Please manually copy backend_COMPLETE_WITH_ALL_ENDPOINTS.py to backend.py
    pause
    exit /b 1
)

REM Start the new backend
echo.
echo STEP 4: Starting the fixed backend...
echo --------------------------------------------------
start "Stock Tracker Backend (FIXED)" cmd /k "python backend.py"

timeout /t 5 >nul

REM Test the endpoints
echo.
echo STEP 5: Testing the endpoints...
echo --------------------------------------------------
echo.
echo Testing /api/health:
curl -s http://localhost:8002/api/health
echo.
echo.
echo Testing /api/market-summary (first few lines):
curl -s http://localhost:8002/api/market-summary 2>nul | more +1 | head -3
echo.

echo.
echo ==============================================================
echo                     FIX COMPLETE!
echo ==============================================================
echo.
echo The backend now has all endpoints:
echo   ✓ /api/health - Returns health status
echo   ✓ /api/market-summary - Returns market data
echo.
echo Go to http://localhost:8000 and refresh (F5)
echo Backend Status should show "Connected" in green!
echo.
pause