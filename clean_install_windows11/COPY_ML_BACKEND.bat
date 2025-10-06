@echo off
REM ============================================================
REM COPY ML BACKEND - Ensures ML backend file exists
REM ============================================================

echo Checking for ML Backend file...
echo.

REM Check if backend_ml_enhanced.py exists in current directory
if exist backend_ml_enhanced.py (
    echo [OK] backend_ml_enhanced.py found in current directory
    goto :fix_port
)

REM Check parent directory
if exist ..\backend_ml_enhanced.py (
    echo Found backend_ml_enhanced.py in parent directory
    copy ..\backend_ml_enhanced.py backend_ml_enhanced.py
    echo Copied to current directory
    goto :fix_port
)

REM Check clean_install_windows11 directory
if exist clean_install_windows11\backend_ml_enhanced.py (
    echo Found backend_ml_enhanced.py in clean_install_windows11 directory  
    copy clean_install_windows11\backend_ml_enhanced.py backend_ml_enhanced.py
    echo Copied to current directory
    goto :fix_port
)

echo ERROR: backend_ml_enhanced.py not found anywhere!
echo Please ensure the file exists in your directory
pause
exit /b 1

:fix_port
echo.
echo Fixing ML Backend port to 8003...
python -c "import os; content=open('backend_ml_enhanced.py').read(); content=content.replace('port=8004','port=8003').replace('port 8004','port 8003'); open('backend_ml_enhanced.py','w').write(content); print('Port fixed to 8003')"

echo.
echo ML Backend file ready!
echo.
pause