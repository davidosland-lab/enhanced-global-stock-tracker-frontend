@echo off
REM ============================================================
REM WINDOWS ABSOLUTE FIX - Fixes path and file issues
REM ============================================================

cls
echo ============================================================
echo     ABSOLUTE FIX FOR WINDOWS 11
echo ============================================================
echo.

REM Show where we are
echo Current Location:
echo %CD%
echo.

REM List all Python and HTML files to see what we have
echo.
echo Files in current directory:
echo ============================================
dir /b *.py *.html *.bat
echo ============================================
echo.

REM Now apply all fixes regardless of where files are

echo STEP 1: Fixing Landing Page
echo ============================
REM Force copy the correct index
if exist index_complete.html (
    echo Found index_complete.html - copying to index.html
    copy /Y index_complete.html index.html >nul
    echo [OK] Landing page updated
) else if exist clean_install_windows11\index_complete.html (
    echo Found index_complete.html in subdirectory
    copy /Y clean_install_windows11\index_complete.html index.html >nul
    echo [OK] Landing page updated from subdirectory
) else (
    echo [ERROR] Cannot find index_complete.html
)

echo.
echo STEP 2: Fixing ML Backend
echo =========================
REM Check for ML backend in multiple locations
set ML_FOUND=0

if exist backend_ml_enhanced.py (
    echo Found backend_ml_enhanced.py in current directory
    set ML_FOUND=1
) else if exist clean_install_windows11\backend_ml_enhanced.py (
    echo Found backend_ml_enhanced.py in subdirectory - copying...
    copy clean_install_windows11\backend_ml_enhanced.py backend_ml_enhanced.py >nul
    set ML_FOUND=1
) else if exist ..\backend_ml_enhanced.py (
    echo Found backend_ml_enhanced.py in parent directory - copying...
    copy ..\backend_ml_enhanced.py backend_ml_enhanced.py >nul
    set ML_FOUND=1
)

if %ML_FOUND%==1 (
    echo Fixing ML Backend port to 8003...
    echo import sys > fix_ml_temp.py
    echo try: >> fix_ml_temp.py
    echo     with open('backend_ml_enhanced.py', 'r') as f: content = f.read() >> fix_ml_temp.py
    echo     content = content.replace('port=8004', 'port=8003').replace('port 8004', 'port 8003') >> fix_ml_temp.py
    echo     with open('backend_ml_enhanced.py', 'w') as f: f.write(content) >> fix_ml_temp.py
    echo     print('[OK] ML Backend port fixed to 8003') >> fix_ml_temp.py
    echo except Exception as e: print(f'[ERROR] {e}') >> fix_ml_temp.py
    python fix_ml_temp.py
    del fix_ml_temp.py
) else (
    echo [ERROR] Cannot find backend_ml_enhanced.py anywhere!
)

echo.
echo STEP 3: Create Directories
echo ==========================
if not exist historical_data mkdir historical_data
if not exist models mkdir models
if not exist uploads mkdir uploads
if not exist predictions mkdir predictions
if not exist logs mkdir logs
echo [OK] All directories created

echo.
echo STEP 4: Kill Existing Processes
echo ================================
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
echo [OK] All processes cleared
timeout /t 2 >nul

echo.
echo ============================================
echo     STARTING ALL SERVICES
echo ============================================
echo.

REM Start Frontend
echo Starting Frontend (port 8000)...
start "Frontend" /min cmd /c "python -m http.server 8000"
timeout /t 3 >nul

REM Start Backend API
echo Starting Backend API (port 8002)...
start "Backend" /min cmd /c "python -m uvicorn backend:app --host 0.0.0.0 --port 8002"
timeout /t 5 >nul

REM Start ML Backend
echo Starting ML Backend (port 8003)...
if exist backend_ml_enhanced.py (
    start "ML Backend" /min cmd /c "python -m uvicorn backend_ml_enhanced:app --host 0.0.0.0 --port 8003"
    echo [OK] ML Backend started
) else (
    echo [ERROR] ML Backend not started - file missing
)
timeout /t 5 >nul

echo.
echo ============================================
echo     VERIFICATION
echo ============================================
echo.

netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 (echo [OK] Frontend running on 8000) else (echo [FAIL] Frontend not running)

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (echo [OK] Backend API running on 8002) else (echo [FAIL] Backend not running)

netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 (echo [OK] ML Backend running on 8003) else (echo [FAIL] ML Backend not running)

echo.
echo ============================================
echo     COMPLETE!
echo ============================================
echo.
echo Opening browser to http://localhost:8000
start http://localhost:8000

echo.
echo If the landing page shows the old version:
echo   1. Press Ctrl+F5 in browser to force refresh
echo   2. Clear browser cache
echo.
echo To test all endpoints:
echo   Open http://localhost:8000/TEST_ALL_ENDPOINTS.html
echo.
echo KEEP THIS WINDOW OPEN - Closing stops all services
echo.
pause