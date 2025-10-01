@echo off
REM ============================================
REM GSMT Installation Tester for Windows
REM ============================================

echo.
echo ==========================================
echo    GSMT INSTALLATION TEST
echo ==========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/5] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] pip is installed
) else (
    echo [ERROR] pip is not installed
    pause
    exit /b 1
)

echo.
echo [3/5] Checking required files...
set missing=0

if not exist "backend_fixed.py" (
    echo [ERROR] backend_fixed.py not found
    set missing=1
)

if not exist "simple_working_dashboard.html" (
    echo [ERROR] simple_working_dashboard.html not found
    set missing=1
)

if not exist "modules\global_indices_tracker.html" (
    echo [ERROR] modules directory or files not found
    set missing=1
)

if %missing% equ 0 (
    echo [OK] All required files found
) else (
    echo [ERROR] Some files are missing
    pause
    exit /b 1
)

echo.
echo [4/5] Checking Python dependencies...
python -c "import fastapi, uvicorn, yfinance" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Dependencies already installed
) else (
    echo [INFO] Dependencies not installed - will install on first run
)

echo.
echo [5/5] Checking port availability...
netstat -an | findstr :8002 >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 8002 may be in use
) else (
    echo [OK] Port 8002 is available
)

netstat -an | findstr :8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 8080 may be in use
) else (
    echo [OK] Port 8080 is available
)

echo.
echo ==========================================
echo    TEST COMPLETE
echo ==========================================
echo.
echo Ready to run START_GSMT_WINDOWS.bat
echo.
pause