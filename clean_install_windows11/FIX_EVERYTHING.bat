@echo off
REM ============================================================
REM FIX EVERYTHING - Complete fix for all issues
REM ============================================================

cls
echo ============================================================
echo     FIXING ALL STOCK TRACKER ISSUES
echo ============================================================
echo.

REM Step 1: Show current directory and files
echo Current Directory:
cd
echo.
echo.
echo Checking for critical files...
echo ============================================

REM Check for backend_ml_enhanced.py
if exist backend_ml_enhanced.py (
    echo [FOUND] backend_ml_enhanced.py
) else (
    echo [MISSING] backend_ml_enhanced.py - ML Training won't work!
)

REM Check for index_complete.html
if exist index_complete.html (
    echo [FOUND] index_complete.html - new landing page
) else (
    echo [MISSING] index_complete.html
)

REM Check for index.html
if exist index.html (
    echo [FOUND] index.html - current landing page
) else (
    echo [MISSING] index.html
)

REM Check for backend.py
if exist backend.py (
    echo [FOUND] backend.py
) else (
    echo [MISSING] backend.py
)

echo.
echo ============================================
echo Applying fixes...
echo ============================================
echo.

REM Fix 1: Update landing page
echo [1/5] Updating landing page to show all 7 modules...
if exist index_complete.html (
    copy /Y index_complete.html index.html
    echo Landing page updated!
) else (
    echo WARNING: index_complete.html not found, landing page not updated
)

REM Fix 2: Fix backend
echo.
echo [2/5] Fixing backend.py...
if exist FINAL_FIX_ALL.py (
    python FINAL_FIX_ALL.py
) else (
    echo WARNING: FINAL_FIX_ALL.py not found
)

REM Fix 3: Fix ML backend port
echo.
echo [3/5] Fixing ML Backend port...
if exist backend_ml_enhanced.py (
    python -c "content=open('backend_ml_enhanced.py').read(); content=content.replace('port=8004','port=8003'); open('backend_ml_enhanced.py','w').write(content); print('ML Backend port fixed to 8003')"
) else (
    echo ERROR: backend_ml_enhanced.py not found!
    echo Attempting to find it...
    
    REM Try to find in parent directory
    if exist ..\backend_ml_enhanced.py (
        copy ..\backend_ml_enhanced.py backend_ml_enhanced.py
        echo Found and copied from parent directory
        python -c "content=open('backend_ml_enhanced.py').read(); content=content.replace('port=8004','port=8003'); open('backend_ml_enhanced.py','w').write(content); print('ML Backend port fixed to 8003')"
    )
)

REM Fix 4: Kill all Python processes
echo.
echo [4/5] Killing all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Fix 5: Clear ports
echo.
echo [5/5] Clearing ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul

echo.
echo ============================================
echo     FIXES APPLIED!
echo ============================================
echo.
echo Now run one of these to start all services:
echo   - START_ALL_SERVICES.bat (recommended)
echo   - START_ALL_SERVICES.ps1 (PowerShell)
echo.
echo If backend_ml_enhanced.py is still missing:
echo   1. Check if it's in a parent or subdirectory
echo   2. Copy it to this directory
echo   3. Then run START_ALL_SERVICES.bat
echo.
pause