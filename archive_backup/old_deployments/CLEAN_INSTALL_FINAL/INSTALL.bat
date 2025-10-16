@echo off
REM ============================================================
REM STOCK TRACKER - INSTALLER
REM Run this ONCE to set everything up
REM ============================================================

cls
color 0B
echo.
echo    ============================================================
echo                   STOCK TRACKER INSTALLER
echo    ============================================================
echo.
echo    This will install and configure Stock Tracker on your system
echo.
pause

echo.
echo    [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo        [ERROR] Python not found!
    echo.
    echo        Please install Python 3.8+ from python.org
    echo        Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo        [OK] Python found

echo.
echo    [2/6] Creating directories...
if not exist historical_data mkdir historical_data
if not exist models mkdir models
if not exist uploads mkdir uploads
if not exist predictions mkdir predictions
if not exist logs mkdir logs
echo        [OK] Directories created

echo.
echo    [3/6] Installing Python dependencies...
echo        This will take 2-5 minutes on first install...
echo.
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo        [WARNING] Some packages may have failed
    echo        Trying alternative installation...
    pip install fastapi uvicorn yfinance pandas numpy
    pip install joblib scikit-learn python-multipart aiofiles
    pip install urllib3==1.26.15
)
echo        [OK] Dependencies installed

echo.
echo    [4/6] Verifying critical files...
set FILES_OK=1

if not exist backend.py (
    echo        [ERROR] backend.py not found!
    set FILES_OK=0
)
if not exist backend_ml_enhanced.py (
    echo        [WARNING] backend_ml_enhanced.py not found
    echo                  ML Training Centre will be disabled
)
if not exist index.html (
    echo        [ERROR] index.html not found!
    set FILES_OK=0
)
if not exist modules (
    echo        [ERROR] modules folder not found!
    set FILES_OK=0
)

if %FILES_OK%==0 (
    echo.
    echo        [ERROR] Critical files missing!
    echo        Please ensure all files were extracted correctly.
    pause
    exit /b 1
)
echo        [OK] All critical files present

echo.
echo    [5/6] Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
if exist "%DESKTOP%" (
    copy StockTracker.bat "%DESKTOP%\Stock Tracker.bat" >nul 2>&1
    if exist "%DESKTOP%\Stock Tracker.bat" (
        echo        [OK] Desktop shortcut created
    ) else (
        echo        [INFO] Could not create desktop shortcut
        echo               You can manually copy StockTracker.bat to desktop
    )
) else (
    echo        [INFO] Desktop not found, skipping shortcut
)

echo.
echo    [6/6] Testing backend imports...
python -c "import fastapi, uvicorn, yfinance, pandas; print('        [OK] Core packages working')"
if errorlevel 1 (
    echo        [WARNING] Some imports failed
    echo        The application may not work properly
)

echo.
echo    ============================================================
echo                 INSTALLATION COMPLETE!
echo    ============================================================
echo.
echo    To start Stock Tracker:
echo.
echo    Option 1: Use desktop shortcut "Stock Tracker.bat"
echo    Option 2: Run StockTracker.bat from this folder
echo.
echo    First launch will take a few seconds to start all services.
echo.
set /p launch="    Would you like to start Stock Tracker now? (y/n): "
if /i "%launch%"=="y" (
    echo.
    echo    Starting Stock Tracker...
    call StockTracker.bat
) else (
    echo.
    echo    You can start Stock Tracker anytime using StockTracker.bat
    echo.
    pause
)