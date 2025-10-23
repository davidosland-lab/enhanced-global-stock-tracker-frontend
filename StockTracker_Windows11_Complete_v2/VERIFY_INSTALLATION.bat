@echo off
title Stock Tracker - Installation Verification
color 0E
cls

echo ============================================================
echo    Stock Tracker Installation Verification
echo    Version 2.0
echo ============================================================
echo.
echo This will verify your installation is complete...
echo.

set /a passed=0
set /a failed=0

echo [Checking Python Installation]
python --version >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ Python is installed
    set /a passed+=1
) else (
    echo    ✗ Python not found - Please install Python 3.8+
    set /a failed+=1
)

echo.
echo [Checking Required Python Packages]

python -c "import fastapi" >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ FastAPI installed
    set /a passed+=1
) else (
    echo    ✗ FastAPI missing
    set /a failed+=1
)

python -c "import yfinance" >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ yfinance installed
    set /a passed+=1
) else (
    echo    ✗ yfinance missing
    set /a failed+=1
)

python -c "import pandas" >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ pandas installed
    set /a passed+=1
) else (
    echo    ✗ pandas missing
    set /a failed+=1
)

python -c "import numpy" >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ numpy installed
    set /a passed+=1
) else (
    echo    ✗ numpy missing
    set /a failed+=1
)

python -c "import sklearn" >nul 2>&1
if %errorlevel%==0 (
    echo    ✓ scikit-learn installed
    set /a passed+=1
) else (
    echo    ✗ scikit-learn missing
    set /a failed+=1
)

echo.
echo [Checking Core Files]

if exist "backend.py" (
    echo    ✓ backend.py found
    set /a passed+=1
) else (
    echo    ✗ backend.py missing
    set /a failed+=1
)

if exist "ml_backend.py" (
    echo    ✓ ml_backend.py found
    set /a passed+=1
) else (
    echo    ✗ ml_backend.py missing
    set /a failed+=1
)

if exist "integration_bridge.py" (
    echo    ✓ integration_bridge.py found
    set /a passed+=1
) else (
    echo    ✗ integration_bridge.py missing
    set /a failed+=1
)

if exist "index.html" (
    echo    ✓ index.html found
    set /a passed+=1
) else (
    echo    ✗ index.html missing
    set /a failed+=1
)

if exist "ml_integration_client.js" (
    echo    ✓ ml_integration_client.js found
    set /a passed+=1
) else (
    echo    ✗ ml_integration_client.js missing
    set /a failed+=1
)

echo.
echo [Checking Module Files]

set /a module_count=0
if exist "document_analyzer.html" set /a module_count+=1
if exist "historical_data_analysis.html" set /a module_count+=1
if exist "market_movers.html" set /a module_count+=1
if exist "ml_training_centre.html" set /a module_count+=1
if exist "stock_analysis.html" set /a module_count+=1

echo    Found %module_count% of 5 main modules
if %module_count%==5 (
    set /a passed+=1
) else (
    set /a failed+=1
)

echo.
echo ============================================================
echo    Verification Results
echo ============================================================
echo.
echo    Tests Passed: %passed%
echo    Tests Failed: %failed%
echo.

if %failed%==0 (
    color 0A
    echo    ✓ INSTALLATION VERIFIED SUCCESSFULLY!
    echo.
    echo    Your Stock Tracker is ready to use.
    echo    Run QUICK_START.bat to begin.
) else (
    color 0C
    echo    ✗ INSTALLATION INCOMPLETE
    echo.
    echo    Please run INSTALL_FIRST.bat to install missing components.
)

echo.
echo ============================================================
echo.
pause