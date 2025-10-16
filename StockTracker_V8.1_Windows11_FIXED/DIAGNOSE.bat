@echo off
cls
color 0E
echo ============================================================
echo    Stock Tracker V8.1 - Diagnostic Tool
echo ============================================================
echo.

echo Checking system configuration...
echo.

:: Check Python
echo [1] Python Installation:
python --version 2>nul
if %errorlevel% neq 0 (
    echo    ERROR: Python not found in PATH
    echo    ACTION: Install Python from python.org
) else (
    echo    OK: Python is installed
)
echo.

:: Check pip
echo [2] Pip Installation:
pip --version 2>nul
if %errorlevel% neq 0 (
    echo    ERROR: Pip not found
) else (
    echo    OK: Pip is installed
)
echo.

:: Check required packages
echo [3] Required Python Packages:
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo    MISSING: fastapi - Run INSTALL.bat or QUICK_INSTALL.bat
) else (
    echo    OK: fastapi
)

python -c "import pandas" 2>nul
if %errorlevel% neq 0 (
    echo    MISSING: pandas - Run INSTALL.bat or QUICK_INSTALL.bat
) else (
    echo    OK: pandas
)

python -c "import sklearn" 2>nul
if %errorlevel% neq 0 (
    echo    MISSING: scikit-learn - Run INSTALL.bat or QUICK_INSTALL.bat
) else (
    echo    OK: scikit-learn
)
echo.

:: Check directories
echo [4] Required Directories:
if exist backends (
    echo    OK: backends directory found
    if exist backends\backend.py (
        echo        - backend.py found
    ) else (
        echo        ERROR: backend.py missing
    )
    if exist backends\ml_backend.py (
        echo        - ml_backend.py found
    ) else (
        echo        ERROR: ml_backend.py missing
    )
) else (
    echo    ERROR: backends directory not found
)

if exist modules (
    echo    OK: modules directory found
) else (
    echo    ERROR: modules directory not found
)
echo.

:: Check ports
echo [5] Port Availability:
netstat -an | findstr ":8002" >nul
if %errorlevel% equ 0 (
    echo    Port 8002: IN USE (Main API)
) else (
    echo    Port 8002: Available
)

netstat -an | findstr ":8003" >nul
if %errorlevel% equ 0 (
    echo    Port 8003: IN USE (ML Backend)
) else (
    echo    Port 8003: Available
)

netstat -an | findstr ":8004" >nul
if %errorlevel% equ 0 (
    echo    Port 8004: IN USE (FinBERT)
) else (
    echo    Port 8004: Available
)

netstat -an | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo    Port 8080: IN USE (Web Server)
) else (
    echo    Port 8080: Available
)
echo.

:: Test service connectivity
echo [6] Testing Service Connectivity:
echo.

:: Try Python HTTP request to localhost
echo Testing localhost connectivity...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/api/status')" 2>nul
if %errorlevel% equ 0 (
    echo    Main API (8002): RESPONDING
) else (
    echo    Main API (8002): NOT RESPONDING
)

python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/api/ml/status')" 2>nul
if %errorlevel% equ 0 (
    echo    ML Backend (8003): RESPONDING
) else (
    echo    ML Backend (8003): NOT RESPONDING
)
echo.

:: Recommendations
echo ============================================================
echo    RECOMMENDATIONS:
echo ============================================================
echo.
echo If services are NOT RESPONDING:
echo   1. Run QUICK_INSTALL.bat first
echo   2. Then run START_TRACKER.bat (or START.bat)
echo   3. Wait 10 seconds for services to start
echo   4. Check Windows Firewall settings
echo.
echo If ports show "IN USE" but services not responding:
echo   1. Run: taskkill /F /IM python.exe
echo   2. Then run START_TRACKER.bat again
echo.
echo Current directory: %CD%
echo.
pause