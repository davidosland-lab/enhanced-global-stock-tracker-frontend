@echo off
REM ============================================================
REM FIX LANDING PAGE - Ensures correct index.html is in place
REM ============================================================

echo Fixing landing page with all 7 modules...
echo.

REM Backup current index.html
if exist index.html (
    copy index.html index_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.html >nul 2>&1
    echo Backed up current index.html
)

REM Copy the complete index with all 7 modules
copy /Y index_complete.html index.html
if errorlevel 1 (
    echo ERROR: Could not update index.html
    echo Please manually rename index_complete.html to index.html
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    LANDING PAGE FIXED!
echo ============================================================
echo.
echo The landing page now includes all 7 modules:
echo   1. Global Stock Tracker
echo   2. Document Analyser with FinBERT
echo   3. Technical Analysis Enhanced v5.3
echo   4. Historical Data Manager
echo   5. ML Training Centre
echo   6. CBA Enhanced
echo   7. Prediction Centre
echo.
echo Refresh your browser or navigate to http://localhost:8000
echo.
pause