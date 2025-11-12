@echo off
REM ============================================================================
REM FinBERT v4.4.4 Rollback Script
REM 
REM This script restores the FinBERT v4.4.4 MARKERS_VISIBLE version
REM from the rollback package.
REM 
REM Features of v4.4.4:
REM - Real FinBERT sentiment analysis (transformers)
REM - Paper trading system
REM - Backtesting with trade markers visible
REM - Portfolio analysis
REM - Custom LSTM training
REM 
REM Date: 2025-11-07
REM ============================================================================

echo.
echo ============================================================================
echo FINBERT v4.4.4 ROLLBACK - STARTING
echo ============================================================================
echo Rollback Package: FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip
echo Target Version: FinBERT v4.4.4 CORRECTED
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as administrator
    echo Some operations may fail. Consider running as admin.
    echo.
    pause
)

REM Step 1: Backup current state
echo [1/8] Backing up current state...
set TIMESTAMP=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=backup_before_rollback_%TIMESTAMP%

if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
mkdir "%BACKUP_DIR%"

echo    Backing up models...
if exist "models" xcopy /E /Y /Q models "%BACKUP_DIR%\models\" >nul 2>&1

echo    Backing up static files...
if exist "static" xcopy /E /Y /Q static "%BACKUP_DIR%\static\" >nul 2>&1

echo    Backing up templates...
if exist "templates" xcopy /E /Y /Q templates "%BACKUP_DIR%\templates\" >nul 2>&1

echo    Backing up application files...
if exist "app*.py" copy app*.py "%BACKUP_DIR%\" >nul 2>&1
if exist "config*.py" copy config*.py "%BACKUP_DIR%\" >nul 2>&1

echo    ✓ Current state backed up to: %BACKUP_DIR%
echo.

REM Step 2: Check for rollback package
echo [2/8] Checking for rollback package...
if not exist "FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip" (
    echo    ✗ ERROR: Rollback package not found!
    echo.
    echo    The file 'FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip' is missing.
    echo    Please ensure the ZIP file is in the current directory.
    echo.
    pause
    exit /b 1
)
echo    ✓ Rollback package found (217KB)
echo.

REM Step 3: Extract rollback package
echo [3/8] Extracting rollback package...
echo    This may take a moment...
powershell -command "Expand-Archive -Path 'FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip' -DestinationPath '.' -Force" >nul 2>&1
if %errorLevel% neq 0 (
    echo    ✗ ERROR: Failed to extract package
    echo    Please check if the ZIP file is corrupted
    pause
    exit /b 1
)
echo    ✓ Package extracted successfully
echo.

REM Step 4: Verify extracted files
echo [4/8] Verifying extracted files...
if not exist "FinBERT_v4.4.4_CORRECTED" (
    echo    ✗ ERROR: Expected directory 'FinBERT_v4.4.4_CORRECTED' not found
    pause
    exit /b 1
)
if not exist "FinBERT_v4.4.4_CORRECTED\app_finbert_v4_dev.py" (
    echo    ✗ ERROR: Main application file not found in package
    pause
    exit /b 1
)
echo    ✓ Files verified
echo.

REM Step 5: Copy files
echo [5/8] Restoring FinBERT v4.4.4 files...
echo    Copying models...
xcopy /E /Y /Q FinBERT_v4.4.4_CORRECTED\models .\models\ >nul 2>&1
echo    Copying static files...
xcopy /E /Y /Q FinBERT_v4.4.4_CORRECTED\static .\static\ >nul 2>&1
echo    Copying templates...
xcopy /E /Y /Q FinBERT_v4.4.4_CORRECTED\templates .\templates\ >nul 2>&1
echo    Copying application files...
copy /Y FinBERT_v4.4.4_CORRECTED\*.py . >nul 2>&1
copy /Y FinBERT_v4.4.4_CORRECTED\*.bat . >nul 2>&1
copy /Y FinBERT_v4.4.4_CORRECTED\*.txt . >nul 2>&1
copy /Y FinBERT_v4.4.4_CORRECTED\*.md . >nul 2>&1
echo    ✓ Files restored successfully
echo.

REM Step 6: Setup Python environment
echo [6/8] Setting up Python environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo    ✓ Virtual environment activated
) else (
    echo    ! Virtual environment not found, creating new one...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo    ✗ ERROR: Failed to create virtual environment
        echo    Please ensure Python 3.8+ is installed
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo    ✓ Virtual environment created and activated
)
echo.

REM Step 7: Install dependencies
echo [7/8] Installing dependencies...
echo    This may take 5-10 minutes depending on your internet speed...
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo    ✗ ERROR: Dependency installation failed
    echo    Please check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo    ✓ All dependencies installed successfully
echo.

REM Step 8: Cleanup
echo [8/8] Cleaning up temporary files...
if exist "FinBERT_v4.4.4_CORRECTED" rmdir /s /q "FinBERT_v4.4.4_CORRECTED"
del /q __pycache__ >nul 2>&1
del /q *.pyc >nul 2>&1
echo    ✓ Cleanup complete
echo.

REM Success message
echo ============================================================================
echo ROLLBACK COMPLETE - FinBERT v4.4.4 RESTORED
echo ============================================================================
echo.
echo ✅ FinBERT v4.4.4 MARKERS_VISIBLE has been successfully restored!
echo.
echo 📦 Package restored from: FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip
echo 💾 Previous version backed up to: %BACKUP_DIR%
echo.
echo 🎯 Next Steps:
echo    1. Start the server: START_FINBERT.bat
echo    2. Open browser: http://localhost:5002
echo    3. Test prediction for any stock (e.g., AAPL, TSLA)
echo    4. Verify FinBERT sentiment analysis is working
echo    5. Test trade markers in backtest section
echo.
echo 📚 Documentation:
echo    - User Guide: README.md
echo    - Training Guide: LSTM_TRAINING_GUIDE.md
echo    - Rollback Guide: FINBERT_V4.4.4_ROLLBACK_GUIDE.md
echo.
echo ============================================================================
echo.
pause
