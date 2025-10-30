@echo off
REM Diagnostic and Fix Tool for "Insufficient Data" Error

echo ========================================
echo DIAGNOSTIC AND FIX TOOL
echo For "Insufficient Data" Error
echo ========================================
echo.

REM Check virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] No virtual environment found!
    echo Please run INSTALL_FIXED.bat first
    pause
    exit /b 1
)

echo Step 1: Installing missing packages...
echo ========================================
pip install yfinance --upgrade
pip install feedparser beautifulsoup4 lxml requests
echo.

echo Step 2: Running diagnostic test...
echo ========================================
python test_data_fetch.py
echo.

echo Step 3: Clearing yfinance cache...
echo ========================================
python -c "import yfinance as yf; yf.cache.clear(); print('Cache cleared')"
echo.

echo Step 4: Testing fixed version...
echo ========================================
echo.
echo Starting the FIXED version of the application...
echo This version includes:
echo - Multiple fallback methods for data fetching
echo - Demo data generation if APIs fail  
echo - Better error handling
echo.
echo The application will open at http://localhost:5000
echo.
pause

python app_enhanced_fixed.py