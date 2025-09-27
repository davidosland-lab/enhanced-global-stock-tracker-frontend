@echo off
REM Test what files are in the current directory

echo ==========================================
echo FILE CHECK - Stock Predictor Pro
echo ==========================================
echo.
echo Current Directory: %CD%
echo.
echo Files in this folder:
echo ==========================================
dir /B *.py 2>nul
if errorlevel 1 (
    echo NO PYTHON FILES FOUND!
    echo.
    echo This means you haven't extracted the files properly.
    echo Please extract ALL files from the ZIP to a folder.
)
echo ==========================================
echo.
echo Batch files in this folder:
dir /B *.bat 2>nul
echo ==========================================
echo.
echo Checking for specific files:
echo.

if exist "stock_predictor_minimal.py" (
    echo [OK] stock_predictor_minimal.py exists
) else (
    echo [MISSING] stock_predictor_minimal.py
)

if exist "stock_predictor_lite.py" (
    echo [OK] stock_predictor_lite.py exists  
) else (
    echo [MISSING] stock_predictor_lite.py
)

if exist "test_simple.py" (
    echo [OK] test_simple.py exists
) else (
    echo [MISSING] test_simple.py
)

echo.
echo ==========================================
echo.
pause