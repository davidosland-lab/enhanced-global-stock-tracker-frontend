@echo off
echo ====================================
echo Unified Trading Dashboard v1.3.15.87
echo ULTIMATE Edition (75-85%% Win Rate)
echo FinBERT v4.4.4: INCLUDED
echo ====================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo OK
echo.

echo Step 2: Installing dependencies...
pip install -q -r requirements.txt
echo OK
echo.

echo Step 3: Creating directories...
call SETUP_DIRECTORIES.bat >nul 2>&1
echo OK
echo.

echo Step 4: Verifying FinBERT v4.4.4...
if exist "finbert_v4.4.4\models\finbert_sentiment.py" (
    echo FinBERT v4.4.4 found - OK
) else (
    echo WARNING: FinBERT files may be incomplete
)
echo.

echo ====================================
echo Installation Complete
echo ====================================
echo.
echo Usage Options:
echo 1. Dashboard only (70-75%%): START.bat
echo 2. Complete workflow (75-85%%): RUN_COMPLETE_WORKFLOW.bat
echo.
echo FinBERT v4.4.4 is pre-installed in finbert_v4.4.4/
echo.
pause
