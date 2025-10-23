@echo off
cd /d "%~dp0"
cls
color 0A

echo ================================================================================
echo                    STOCK TRACKER - WINDOWS 11 FIX AND RUN
echo ================================================================================
echo.

echo [1] Checking current directory structure...
echo Current location: %cd%
echo.

echo [2] Checking for critical files...
if not exist "index.html" (
    echo [ERROR] index.html not found!
    echo.
    echo Please make sure you extracted ALL files from the ZIP archive.
    echo You should have:
    echo   - index.html
    echo   - backend.py  
    echo   - modules folder with HTML files
    echo   - historical_data folder
    echo.
    pause
    exit /b 1
)

echo [3] Verifying backend.py exists...
if not exist "backend.py" (
    echo [ERROR] backend.py not found!
    echo Please extract all files from the ZIP.
    pause
    exit /b 1
)

echo [4] Killing any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo [5] Installing Python packages...
pip install --quiet --upgrade "urllib3<2" >nul 2>&1
pip install --quiet yfinance fastapi uvicorn pandas numpy python-multipart cachetools pytz requests >nul 2>&1

echo [6] Creating required directories...
if not exist "historical_data" mkdir "historical_data"
if not exist "uploads" mkdir "uploads"
if not exist "logs" mkdir "logs"

echo [7] Starting Frontend Server on port 8000...
start /min cmd /c "title Frontend Server && cd /d %cd% && python -m http.server 8000 2>logs\frontend.log"
timeout /t 2 >nul

echo [8] Starting Backend API on port 8002...
start /min cmd /c "title Backend API && cd /d %cd% && python backend.py 2>logs\backend.log"
timeout /t 3 >nul

echo.
echo ================================================================================
echo                              STARTUP COMPLETE
echo ================================================================================
echo.
echo Services started:
echo   Frontend: http://localhost:8000
echo   Backend:  http://localhost:8002
echo   API Docs: http://localhost:8002/docs
echo.
echo Opening main application...
start http://localhost:8000
echo.
echo If you see any 404 errors:
echo   1. Make sure ALL files were extracted from the ZIP
echo   2. Check that the modules folder contains all HTML files
echo   3. Try: http://localhost:8000/index.html directly
echo.
echo To test the system:
echo   - Main page should show stock dashboard
echo   - Click on modules to test functionality
echo   - Historical Data Manager should be able to download data
echo.
pause