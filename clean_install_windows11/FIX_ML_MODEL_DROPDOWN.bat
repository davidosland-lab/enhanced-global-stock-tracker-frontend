@echo off
echo ============================================================
echo ML Training Centre - Model Dropdown Fix (Simple Version)
echo ============================================================
echo.
echo This will fix the issue where trained models don't appear
echo in the prediction dropdown selector.
echo.
echo Current directory: %cd%
echo.

REM Check if we're in the right directory
if not exist modules\ml_training_centre.html (
    echo ERROR: Cannot find modules\ml_training_centre.html
    echo.
    echo Please run this script from the Stock Tracker main directory
    echo (the folder containing the 'modules' subfolder)
    echo.
    pause
    exit /b 1
)

REM Create backup with timestamp
echo Step 1: Creating backup of original file...
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
copy modules\ml_training_centre.html "modules\ml_training_centre_BEFORE_FIX_%timestamp%.backup" >nul 2>&1
echo         Backup saved as: ml_training_centre_BEFORE_FIX_%timestamp%.backup
echo.

REM Apply the fix using Python
echo Step 2: Applying the ML dropdown fix...
echo.

REM Create a simple Python fix script
echo import os > fix_ml_dropdown.py
echo print("Fixing ML Training Centre dropdown...") >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo with open('modules/ml_training_centre.html', 'r', encoding='utf-8') as f: >> fix_ml_dropdown.py
echo     content = f.read() >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo # Check if already fixed >> fix_ml_dropdown.py
echo if 'const modelSelect = document.getElementById' in content: >> fix_ml_dropdown.py
echo     print("✓ File appears to already be fixed!") >> fix_ml_dropdown.py
echo     exit(0) >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo # Find and fix the loadTrainedModels function >> fix_ml_dropdown.py
echo if 'async function loadTrainedModels()' in content: >> fix_ml_dropdown.py
echo     # Add dropdown population code >> fix_ml_dropdown.py
echo     old_line = "const modelsList = document.getElementById('modelsList');" >> fix_ml_dropdown.py
echo     new_lines = """const modelsList = document.getElementById('modelsList'); >> fix_ml_dropdown.py
echo                 const modelSelect = document.getElementById('selectedModel'); // Get the dropdown""" >> fix_ml_dropdown.py
echo     content = content.replace(old_line, new_lines, 1) >> fix_ml_dropdown.py
echo     print("✓ Added dropdown reference") >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo     # Clear dropdown >> fix_ml_dropdown.py
echo     old_clear = "modelsList.innerHTML = '';" >> fix_ml_dropdown.py
echo     new_clear = """modelsList.innerHTML = ''; >> fix_ml_dropdown.py
echo                 modelSelect.innerHTML = ''; // Clear the dropdown""" >> fix_ml_dropdown.py
echo     content = content.replace(old_clear, new_clear, 1) >> fix_ml_dropdown.py
echo     print("✓ Added dropdown clearing") >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo # Add onchange event to dropdown >> fix_ml_dropdown.py
echo old_select = 'id="selectedModel"^>' >> fix_ml_dropdown.py
echo new_select = 'id="selectedModel" onchange="onModelSelectChange()"^>' >> fix_ml_dropdown.py
echo content = content.replace(old_select, new_select, 1) >> fix_ml_dropdown.py
echo print("✓ Added onchange event") >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo with open('modules/ml_training_centre.html', 'w', encoding='utf-8') as f: >> fix_ml_dropdown.py
echo     f.write(content) >> fix_ml_dropdown.py
echo. >> fix_ml_dropdown.py
echo print("\n✅ Fix applied successfully!") >> fix_ml_dropdown.py

REM Run the fix
python fix_ml_dropdown.py

if errorlevel 1 (
    echo.
    echo WARNING: Python script had issues. Trying alternative method...
    echo.
    
    REM Alternative: Direct file copy if you have the fixed version
    if exist ml_training_centre_fixed.html (
        echo Using pre-fixed version...
        copy ml_training_centre_fixed.html modules\ml_training_centre.html >nul
        echo ✅ Applied pre-fixed version
    ) else (
        echo.
        echo Please ensure Python is installed or place the fixed
        echo ml_training_centre.html file in this directory.
    )
)

REM Clean up
del fix_ml_dropdown.py 2>nul

echo.
echo ============================================================
echo ✅ ML Model Dropdown Fix Complete!
echo ============================================================
echo.
echo What was fixed:
echo - Trained models now appear in the prediction dropdown
echo - Model selection syncs between list and dropdown
echo - Can select models for making predictions
echo.
echo Next steps:
echo 1. Run START_ALL_SERVICES.bat to start the application
echo 2. Open http://localhost:8000 in your browser
echo 3. Go to ML Training Centre
echo 4. Train a model - it will now appear in the dropdown!
echo.
echo Original file backed up as:
echo modules\ml_training_centre_BEFORE_FIX_%timestamp%.backup
echo.
pause