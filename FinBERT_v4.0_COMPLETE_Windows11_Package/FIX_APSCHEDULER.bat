@echo off
echo ================================================================
echo   QUICK FIX: Install APScheduler and pytz
echo ================================================================
echo.
echo This will install the missing packages for prediction caching:
echo   - APScheduler (job scheduling)
echo   - pytz (timezone support)
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing APScheduler and pytz...
pip install APScheduler pytz

echo.
echo ================================================================
echo Verification:
echo ================================================================
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✓ APScheduler installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ APScheduler installation FAILED
    echo.
    echo Please run FIX_MISSING_PACKAGES.bat for full repair.
    pause
    exit /b 1
)

python -c "import pytz; print('✓ pytz installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ pytz installation FAILED
    echo.
    echo Please run FIX_MISSING_PACKAGES.bat for full repair.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo SUCCESS! Packages installed.
echo ================================================================
echo.
echo Now restart the application:
echo   1. Close the current server (Ctrl+C)
echo   2. Run: START_FINBERT_V4.bat
echo   3. Look for: "✓ Prediction caching: ACTIVE"
echo.
pause
