@echo off
REM ========================================================================
REM HOTFIX v1.3.15.45 - Dashboard FinBERT Integration Fix
REM ========================================================================
REM
REM Fixes ImportError: cannot import name 'SentimentIntegration'
REM
REM This script:
REM 1. Backs up unified_trading_dashboard.py
REM 2. Fixes the import statement
REM 3. Clears Python cache
REM 4. Verifies the fix
REM
REM ========================================================================

echo.
echo ========================================================================
echo HOTFIX v1.3.15.45 - Dashboard FinBERT Integration Fix
echo ========================================================================
echo.

REM Check if we're in the right directory
if not exist "unified_trading_dashboard.py" (
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Please run this script from:
    echo C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
    echo.
    pause
    exit /b 1
)

echo [1/4] Backing up dashboard...
if not exist "unified_trading_dashboard.py.backup_hotfix" (
    copy /Y "unified_trading_dashboard.py" "unified_trading_dashboard.py.backup_hotfix" >nul
    echo       Backup created: unified_trading_dashboard.py.backup_hotfix
) else (
    echo       Backup already exists (skipping)
)

echo.
echo [2/4] Applying fix...

REM Create a temporary Python script to do the replacement
echo import sys > _temp_fix.py
echo with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f: >> _temp_fix.py
echo     content = f.read() >> _temp_fix.py
echo. >> _temp_fix.py
echo # Fix the imports >> _temp_fix.py
echo content = content.replace( >> _temp_fix.py
echo     'from sentiment_integration import SentimentIntegration', >> _temp_fix.py
echo     'from sentiment_integration import IntegratedSentimentAnalyzer' >> _temp_fix.py
echo ) >> _temp_fix.py
echo. >> _temp_fix.py
echo content = content.replace( >> _temp_fix.py
echo     'sentiment_int = SentimentIntegration()', >> _temp_fix.py
echo     'sentiment_int = IntegratedSentimentAnalyzer()' >> _temp_fix.py
echo ) >> _temp_fix.py
echo. >> _temp_fix.py
echo with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f: >> _temp_fix.py
echo     f.write(content) >> _temp_fix.py
echo. >> _temp_fix.py
echo print('Fix applied successfully') >> _temp_fix.py

REM Run the fix
python _temp_fix.py
if errorlevel 1 (
    echo       [ERROR] Failed to apply fix
    del _temp_fix.py
    pause
    exit /b 1
)

del _temp_fix.py
echo       Import statements fixed

echo.
echo [3/4] Clearing Python cache...
del /S /Q __pycache__\*.pyc 2>nul
del /S /Q models\screening\__pycache__\*.pyc 2>nul
echo       Cache cleared

echo.
echo [4/4] Verifying fix...
findstr /C:"IntegratedSentimentAnalyzer" unified_trading_dashboard.py >nul
if errorlevel 1 (
    echo       [ERROR] Fix verification failed!
    pause
    exit /b 1
) else (
    echo       Fix verified successfully
)

echo.
echo ========================================================================
echo HOTFIX COMPLETE
echo ========================================================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start dashboard: python unified_trading_dashboard.py
echo 3. Open browser: http://localhost:8050
echo.
echo Expected result:
echo - Dashboard starts without ImportError
echo - FinBERT sentiment panel loads data
echo - Morning report displayed
echo.
echo ========================================================================
echo.

pause
