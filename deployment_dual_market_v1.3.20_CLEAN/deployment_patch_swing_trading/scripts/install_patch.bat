@echo off
REM Swing Trading Backtest - Deployment Patch Installer (Windows)
REM Version: 1.0
REM Date: December 6, 2025

echo =========================================
echo Swing Trading Backtest - Patch Installer
echo =========================================
echo.

REM Check if running from correct directory
if not exist "code\" (
    echo ERROR: Please run this script from the deployment_patch_swing_trading directory
    echo Expected structure:
    echo   deployment_patch_swing_trading\
    echo   +-- code\
    echo   +-- docs\
    echo   +-- scripts\
    pause
    exit /b 1
)

REM Ask for FinBERT installation path
set /p FINBERT_PATH="Enter the path to your FinBERT v4.4.4 installation (e.g., C:\Users\david\AATelS): "

REM Remove trailing backslash if present
if "%FINBERT_PATH:~-1%"=="\" set FINBERT_PATH=%FINBERT_PATH:~0,-1%

REM Validate path
if not exist "%FINBERT_PATH%\" (
    echo ERROR: Directory not found: %FINBERT_PATH%
    pause
    exit /b 1
)

if not exist "%FINBERT_PATH%\finbert_v4.4.4\" (
    echo ERROR: FinBERT v4.4.4 not found in: %FINBERT_PATH%
    pause
    exit /b 1
)

set BACKTESTING_DIR=%FINBERT_PATH%\finbert_v4.4.4\models\backtesting

if not exist "%BACKTESTING_DIR%\" (
    echo ERROR: Backtesting directory not found: %BACKTESTING_DIR%
    pause
    exit /b 1
)

echo [OK] FinBERT v4.4.4 installation found
echo.

REM Create backup directory
set BACKUP_DIR=%FINBERT_PATH%\backups\swing_trading_patch_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
echo Creating backup at: %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul

REM Backup existing files (if any)
if exist "%BACKTESTING_DIR%\swing_trader_engine.py" (
    copy "%BACKTESTING_DIR%\swing_trader_engine.py" "%BACKUP_DIR%\" >nul
    echo   - Backed up swing_trader_engine.py
)

if exist "%BACKTESTING_DIR%\news_sentiment_fetcher.py" (
    copy "%BACKTESTING_DIR%\news_sentiment_fetcher.py" "%BACKUP_DIR%\" >nul
    echo   - Backed up news_sentiment_fetcher.py
)

if exist "%FINBERT_PATH%\finbert_v4.4.4\app_finbert_v4_dev.py" (
    copy "%FINBERT_PATH%\finbert_v4.4.4\app_finbert_v4_dev.py" "%BACKUP_DIR%\" >nul
    echo   - Backed up app_finbert_v4_dev.py
)

echo [OK] Backup created
echo.

REM Install code files
echo Installing code files...
copy "code\swing_trader_engine.py" "%BACKTESTING_DIR%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy swing_trader_engine.py
    pause
    exit /b 1
)
echo   - Installed swing_trader_engine.py

copy "code\news_sentiment_fetcher.py" "%BACKTESTING_DIR%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy news_sentiment_fetcher.py
    pause
    exit /b 1
)
echo   - Installed news_sentiment_fetcher.py

copy "code\example_swing_backtest.py" "%BACKTESTING_DIR%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy example_swing_backtest.py
    pause
    exit /b 1
)
echo   - Installed example_swing_backtest.py

echo [OK] Code files installed
echo.

REM Install documentation
echo Installing documentation...
set DOCS_DIR=%FINBERT_PATH%\docs\swing_trading
mkdir "%DOCS_DIR%" 2>nul

copy "docs\*.md" "%DOCS_DIR%\" >nul
if errorlevel 1 (
    echo WARNING: Failed to copy some documentation files
) else (
    echo   - Installed documentation to %DOCS_DIR%
)

echo [OK] Documentation installed
echo.

REM Manual step notice
echo =========================================
echo MANUAL STEP REQUIRED: API Endpoint
echo =========================================
echo.
echo The API endpoint needs to be manually added to:
echo   %FINBERT_PATH%\finbert_v4.4.4\app_finbert_v4_dev.py
echo.
echo Add the endpoint code from:
echo   code\swing_endpoint_patch.py
echo.
echo BEFORE the @app.route('/api/backtest/optimize', methods=['POST']) endpoint
echo.
echo OR use the provided Python script:
echo   python scripts\add_api_endpoint.py
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import tensorflow" 2>nul
if errorlevel 1 (
    echo [WARNING] TensorFlow not found - LSTM will use fallback mode
    echo   To enable LSTM: pip install tensorflow
) else (
    echo [OK] TensorFlow available - LSTM will work
)

python -c "import transformers" 2>nul
if errorlevel 1 (
    echo [WARNING] Transformers not found - Sentiment will be limited
    echo   To enable sentiment: pip install transformers
) else (
    echo [OK] Transformers available - FinBERT will work
)

echo.
echo =========================================
echo Installation Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Manually add API endpoint (see code\swing_endpoint_patch.py)
echo    OR run: python scripts\add_api_endpoint.py
echo 2. Restart FinBERT v4.4.4 server
echo 3. Test with Quick Test Guide in docs\
echo.
echo Documentation available at:
echo   %DOCS_DIR%\QUICK_TEST_GUIDE.md
echo.
echo Backup saved at:
echo   %BACKUP_DIR%
echo.
pause
