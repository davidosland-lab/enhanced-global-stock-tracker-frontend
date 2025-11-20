@echo off
REM ====================================================================
REM Auto-Fix Script for TRAIN_LSTM_OVERNIGHT.bat TensorFlow Detection
REM Version 2 - Uses Python instead of PowerShell (more reliable)
REM ====================================================================

echo.
echo ========================================================================
echo   AUTO-FIX: TRAIN_LSTM_OVERNIGHT.bat TensorFlow Detection (V2)
echo ========================================================================
echo.
echo This will fix the TensorFlow detection issue in TRAIN_LSTM_OVERNIGHT.bat
echo.
echo What this does:
echo   1. Creates backup of original file
echo   2. Fixes line 57 (TensorFlow detection check)
echo   3. Verifies the fix was applied
echo.
pause
echo.

REM Check if the file exists
if not exist "TRAIN_LSTM_OVERNIGHT.bat" (
    echo [ERROR] TRAIN_LSTM_OVERNIGHT.bat not found in current directory
    echo.
    echo Current directory: %CD%
    echo Expected location: C:\Users\david\AASS\deployment_event_risk_guard
    echo.
    echo Please navigate to the correct directory and run this script again.
    echo.
    pause
    exit /b 1
)

echo [INFO] Found TRAIN_LSTM_OVERNIGHT.bat in: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo.
    echo The automatic fix requires Python.
    echo Please use the Manual Fix method instead (see QUICK_FIX_GUIDE.txt)
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected
echo.

REM Create backup
echo Creating backup...
copy /Y "TRAIN_LSTM_OVERNIGHT.bat" "TRAIN_LSTM_OVERNIGHT.bat.backup" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Could not create backup file
    echo.
    echo Try one of these solutions:
    echo   1. Run this script as Administrator (Right-click -> Run as administrator)
    echo   2. Use the Manual Fix method (see QUICK_FIX_GUIDE.txt)
    echo.
    pause
    exit /b 1
)

echo [OK] Backup created: TRAIN_LSTM_OVERNIGHT.bat.backup
echo.

REM Create Python fix script
echo Creating Python fix script...
echo import sys > _temp_fix.py
echo import re >> _temp_fix.py
echo. >> _temp_fix.py
echo # Read the file >> _temp_fix.py
echo with open('TRAIN_LSTM_OVERNIGHT.bat', 'r', encoding='utf-8') as f: >> _temp_fix.py
echo     content = f.read() >> _temp_fix.py
echo. >> _temp_fix.py
echo # Apply the fix >> _temp_fix.py
echo old_pattern = r'python -c "import tensorflow; print\(f[\'"]TensorFlow \{tensorflow\.__version__\} detected[\'"]?\)" 2^>nul' >> _temp_fix.py
echo new_text = 'python -c "import tensorflow" 2^>nul' >> _temp_fix.py
echo. >> _temp_fix.py
echo # Check if pattern exists >> _temp_fix.py
echo if 'tensorflow.__version__' in content: >> _temp_fix.py
echo     # Replace the line >> _temp_fix.py
echo     content = re.sub(old_pattern, new_text, content) >> _temp_fix.py
echo     print('Pattern found and replaced') >> _temp_fix.py
echo else: >> _temp_fix.py
echo     print('Pattern not found - file may already be fixed') >> _temp_fix.py
echo. >> _temp_fix.py
echo # Write the fixed content >> _temp_fix.py
echo with open('TRAIN_LSTM_OVERNIGHT.bat', 'w', encoding='utf-8') as f: >> _temp_fix.py
echo     f.write(content) >> _temp_fix.py
echo. >> _temp_fix.py
echo print('Fix applied successfully') >> _temp_fix.py

REM Run the Python fix script
echo.
echo Applying fix...
python _temp_fix.py
set FIX_RESULT=%ERRORLEVEL%

REM Clean up temporary script
del _temp_fix.py >nul 2>&1

if %FIX_RESULT% neq 0 (
    echo.
    echo [ERROR] Fix failed
    echo.
    echo Restoring backup...
    copy /Y "TRAIN_LSTM_OVERNIGHT.bat.backup" "TRAIN_LSTM_OVERNIGHT.bat" >nul
    echo Backup restored.
    echo.
    echo Please use Manual Fix method (see QUICK_FIX_GUIDE.txt)
    echo.
    pause
    exit /b 1
)

echo [OK] Fix applied
echo.

REM Verify the fix
echo Verifying fix...
findstr /C:"import tensorflow\" 2>nul" "TRAIN_LSTM_OVERNIGHT.bat" >nul
if errorlevel 1 (
    echo [WARNING] Could not verify fix was applied correctly
    echo.
    echo Please manually check line 57 in TRAIN_LSTM_OVERNIGHT.bat
    echo It should be: python -c "import tensorflow" 2^>nul
    echo.
    echo You can also compare with the backup file to see changes.
    echo.
) else (
    echo [OK] Fix verified successfully!
    echo.
)

REM Show what changed
echo ========================================================================
echo   FIX COMPLETED
echo ========================================================================
echo.
echo Changes made:
echo   - Original file backed up to: TRAIN_LSTM_OVERNIGHT.bat.backup
echo   - Fixed TensorFlow detection check (line 57)
echo.
echo OLD LINE (before fix):
echo   python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2^>nul
echo.
echo NEW LINE (after fix):
echo   python -c "import tensorflow" 2^>nul
echo.
echo ========================================================================
echo.
echo Next Steps:
echo   1. Run: TRAIN_LSTM_OVERNIGHT.bat
echo   2. You should see: [OK] TensorFlow is installed
echo   3. Training should start automatically
echo.
echo If there are any issues:
echo   - Restore backup: copy TRAIN_LSTM_OVERNIGHT.bat.backup TRAIN_LSTM_OVERNIGHT.bat
echo   - See detailed guide: FIX_WINDOWS_LSTM_OVERNIGHT.md
echo   - Use manual fix: See QUICK_FIX_GUIDE.txt
echo.
echo ========================================================================
echo.
echo Press any key to close this window...
pause >nul
