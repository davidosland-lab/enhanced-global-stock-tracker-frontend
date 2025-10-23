@echo off
echo ============================================================
echo ML Training Centre - Model Dropdown Fix (Clean Version)
echo ============================================================
echo.
echo This will properly fix the model dropdown issue without
echo any syntax errors.
echo.

REM Check if Python script exists
if not exist FIX_ML_DROPDOWN_CLEAN.py (
    echo ERROR: FIX_ML_DROPDOWN_CLEAN.py not found!
    echo Please ensure all files are in the correct location.
    pause
    exit /b 1
)

REM Check if modules directory exists
if not exist modules\ml_training_centre.html (
    echo ERROR: modules\ml_training_centre.html not found!
    echo Please run this from the Stock Tracker main directory.
    pause
    exit /b 1
)

echo Applying the clean fix...
echo.

REM Run the Python fix script
python FIX_ML_DROPDOWN_CLEAN.py

if errorlevel 1 (
    echo.
    echo ERROR: Fix failed. Please ensure Python is installed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ Fix Applied Successfully!
echo ============================================================
echo.
echo The syntax error has been fixed and the model dropdown
echo will now work properly.
echo.
echo What was fixed:
echo ✓ Removed any syntax errors (^ characters)
echo ✓ Models now appear in the dropdown after training
echo ✓ Dropdown and list stay synchronized
echo ✓ Can select models for predictions
echo.
echo Next steps:
echo 1. Close your browser completely
echo 2. Run STOP_ALL_SERVICES.bat
echo 3. Run START_ALL_SERVICES.bat
echo 4. Open http://localhost:8000 in a fresh browser window
echo 5. Clear browser cache (Ctrl+Shift+Delete) if needed
echo.
pause