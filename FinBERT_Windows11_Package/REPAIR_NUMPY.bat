@echo off
REM FinBERT Trading System - Numpy Repair Script
REM Use this if you encounter numpy-related errors

echo ========================================
echo Numpy Repair Tool
echo ========================================
echo.
echo This script will fix numpy installation issues
echo that may prevent FinBERT from working properly.
echo.
pause

REM Activate virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
    echo [✓] Virtual environment activated
) else (
    echo [INFO] No virtual environment found, using system Python
)
echo.

echo Step 1: Uninstalling existing numpy...
pip uninstall numpy -y 2>nul
echo.

echo Step 2: Clearing pip cache...
pip cache purge 2>nul
echo.

echo Step 3: Installing numpy with forced reinstall...
pip install --force-reinstall --no-cache-dir numpy==1.24.3
if %errorlevel% neq 0 (
    echo [WARNING] Standard install failed, trying alternative version...
    pip install --force-reinstall --no-cache-dir numpy==1.23.5
)
echo.

echo Step 4: Verifying numpy installation...
python -c "import numpy; print(f'Numpy version: {numpy.__version__}'); print('Numpy is working correctly!')"
if %errorlevel% neq 0 (
    echo [ERROR] Numpy still not working properly!
    echo.
    echo Manual fix required:
    echo 1. Delete the venv folder
    echo 2. Run INSTALL.bat again
    echo.
    pause
    exit /b 1
)
echo.

echo Step 5: Testing with transformers...
python -c "import transformers; print('Transformers can load successfully!')"
if %errorlevel% neq 0 (
    echo [WARNING] Transformers having issues. Reinstalling...
    pip install --force-reinstall transformers==4.35.2
)
echo.

echo ========================================
echo Numpy Repair Complete!
echo ========================================
echo.
echo You can now run the application with RUN.bat
echo.
pause