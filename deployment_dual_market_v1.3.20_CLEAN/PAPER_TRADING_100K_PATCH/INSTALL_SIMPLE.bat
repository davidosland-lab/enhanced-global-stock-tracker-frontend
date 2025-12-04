@echo off
REM =====================================================================
REM PAPER TRADING $100K PATCH INSTALLER - SIMPLE VERSION
REM =====================================================================
REM This version always stays open so you can see what happened
REM =====================================================================

echo.
echo ========================================================================
echo    PAPER TRADING $100K PATCH INSTALLER - SIMPLE
echo ========================================================================
echo.
echo This will update your paper trading account from $10,000 to $100,000
echo.
echo Press any key to start...
pause >nul
echo.

REM Check if we're in the right directory
echo Checking directory...
if not exist "finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo [ERROR] Wrong directory!
    echo Current: %CD%
    echo Expected: C:\Users\david\AATelS
    echo.
    echo Please:
    echo   1. Open NEW Command Prompt
    echo   2. Type: cd C:\Users\david\AATelS
    echo   3. Type: PAPER_TRADING_100K_PATCH\INSTALL_SIMPLE.bat
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Directory check passed
echo.

REM Check if patch files exist
echo Checking patch files...
if not exist "PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo [ERROR] Patch files not found!
    echo.
    echo Make sure you extracted PAPER_TRADING_100K_PATCH.zip to C:\Users\david\AATelS\
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Patch files found
echo.

REM Create backup
echo Creating backup...
set BACKUP_DIR=finbert_v4.4.4\BACKUP_SIMPLE_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%\models\trading" 2>nul
mkdir "%BACKUP_DIR%\templates" 2>nul

copy finbert_v4.4.4\models\trading\*.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\app_finbert_v4_dev.py "%BACKUP_DIR%\" >nul 2>&1
copy finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\templates\" >nul 2>&1
echo [OK] Backup created: %BACKUP_DIR%
echo.

REM Copy files
echo Installing files...
echo.

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] trade_database.py) else (echo [OK] trade_database.py)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\paper_trading_engine.py finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] paper_trading_engine.py) else (echo [OK] paper_trading_engine.py)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\portfolio_manager.py finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] portfolio_manager.py) else (echo [OK] portfolio_manager.py)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\app_finbert_v4_dev.py finbert_v4.4.4\ >nul 2>&1
if errorlevel 1 (echo [FAIL] app_finbert_v4_dev.py) else (echo [OK] app_finbert_v4_dev.py)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html finbert_v4.4.4\templates\ >nul 2>&1
if errorlevel 1 (echo [FAIL] finbert_v4_enhanced_ui.html) else (echo [OK] finbert_v4_enhanced_ui.html)

echo.

REM Clear cache
echo Clearing Python cache...
for /d /r finbert_v4.4.4\models\trading %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /q finbert_v4.4.4\models\trading\*.pyc 2>nul
echo [OK] Cache cleared
echo.

echo ========================================================================
echo    INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Backup saved to: %BACKUP_DIR%
echo.
echo NEXT: Reset your account to $100,000
echo.
echo Copy and run these commands:
echo.
echo   cd finbert_v4.4.4
echo   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Reset to $100,000')"
echo.
echo Then verify:
echo.
echo   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
echo.
echo Expected output: Cash: $100,000.00
echo.
echo ========================================================================
echo.
echo Press any key to close this window...
pause >nul
