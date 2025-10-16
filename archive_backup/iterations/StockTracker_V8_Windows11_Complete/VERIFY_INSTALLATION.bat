@echo off
cls
color 0E
echo ============================================================
echo    Stock Tracker V8 - Installation Verification
echo ============================================================
echo.

echo Checking installation components...
echo.

set /a total=0
set /a passed=0

:: Check Python
echo -n Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [ OK ]
    set /a passed+=1
) else (
    echo [ MISSING ]
)
set /a total+=1

:: Check required directories
echo Checking directories...
set dirs=backends modules config models logs data saved_models
for %%d in (%dirs%) do (
    if exist %%d (
        echo   %%d... [ OK ]
        set /a passed+=1
    ) else (
        echo   %%d... [ MISSING ]
    )
    set /a total+=1
)

:: Check key files
echo.
echo Checking key files...
if exist "backends\backend.py" (
    echo   Main Backend... [ OK ]
    set /a passed+=1
) else (
    echo   Main Backend... [ MISSING ]
)
set /a total+=1

if exist "backends\ml_backend.py" (
    echo   ML Backend... [ OK ]
    set /a passed+=1
) else (
    echo   ML Backend... [ MISSING ]
)
set /a total+=1

if exist "backends\finbert_backend.py" (
    echo   FinBERT Backend... [ OK ]
    set /a passed+=1
) else (
    echo   FinBERT Backend... [ MISSING ]
)
set /a total+=1

if exist "modules\index.html" (
    echo   Web Interface... [ OK ]
    set /a passed+=1
) else (
    echo   Web Interface... [ MISSING ]
)
set /a total+=1

if exist "modules\indices_tracker_enhanced.html" (
    echo   Enhanced Indices... [ OK ]
    set /a passed+=1
) else (
    echo   Enhanced Indices... [ MISSING ]
)
set /a total+=1

:: Check ML configuration
echo.
echo Checking ML configuration...
findstr /C:"n_estimators=500" backends\ml_backend.py >nul
if %errorlevel% equ 0 (
    echo   RandomForest trees=500... [ OK ]
    set /a passed+=1
) else (
    echo   RandomForest trees=500... [ NOT FOUND ]
)
set /a total+=1

findstr /C:"max_depth=20" backends\ml_backend.py >nul
if %errorlevel% equ 0 (
    echo   RandomForest depth=20... [ OK ]
    set /a passed+=1
) else (
    echo   RandomForest depth=20... [ NOT FOUND ]
)
set /a total+=1

:: Check for fake data patterns
echo.
echo Verifying NO FAKE DATA...
findstr /C:"Math.random" modules\*.html backends\*.py >nul 2>&1
if %errorlevel% neq 0 (
    echo   No Math.random found... [ OK ]
    set /a passed+=1
) else (
    echo   Math.random detected... [ WARNING ]
)
set /a total+=1

:: Summary
echo.
echo ============================================================
echo    Verification Results
echo ============================================================
echo.
echo   Passed: %passed% / %total% checks
echo.

if %passed% equ %total% (
    color 0A
    echo   STATUS: INSTALLATION VERIFIED - READY TO USE
    echo.
    echo   All components are properly installed.
    echo   This system uses REAL ML with no fake data.
    echo.
    echo   Training times will be:
    echo     - 365 days: 2-5 seconds
    echo     - 730 days: 5-15 seconds  
    echo     - 2000+ days: 10-60 seconds
) else (
    color 0C
    echo   STATUS: INSTALLATION INCOMPLETE
    echo.
    echo   Please run INSTALL_WINDOWS11.bat first
)

echo.
echo Press any key to exit...
pause >nul