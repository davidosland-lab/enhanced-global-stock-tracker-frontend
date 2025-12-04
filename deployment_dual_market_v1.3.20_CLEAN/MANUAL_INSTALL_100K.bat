@echo off
REM =====================================================================
REM MANUAL INSTALLATION - PAPER TRADING $100K PATCH
REM =====================================================================
REM This script copies files manually without needing the ZIP structure
REM Run this from C:\Users\david\AATelS\
REM =====================================================================

echo.
echo ========================================================================
echo    MANUAL INSTALLATION - PAPER TRADING $100K PATCH
echo ========================================================================
echo.
echo This will manually copy the updated files from wherever you extracted them.
echo.
pause

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo [ERROR] Wrong directory!
    echo Current: %CD%
    echo Expected: C:\Users\david\AATelS
    echo.
    echo Please: cd C:\Users\david\AATelS
    echo Then run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] In correct directory
echo.

REM Ask user where they extracted the ZIP
echo Where did you extract PAPER_TRADING_100K_PATCH.zip?
echo.
echo Common locations:
echo   1. C:\Users\david\AATelS\PAPER_TRADING_100K_PATCH
echo   2. C:\Users\david\Downloads\PAPER_TRADING_100K_PATCH
echo   3. C:\Users\david\Desktop\PAPER_TRADING_100K_PATCH
echo.
set /p PATCH_DIR="Enter the full path (or press Enter for option 1): "

if "%PATCH_DIR%"=="" set PATCH_DIR=C:\Users\david\AATelS\PAPER_TRADING_100K_PATCH

echo.
echo Using patch directory: %PATCH_DIR%
echo.

REM Check if patch files exist
if not exist "%PATCH_DIR%\finbert_v4.4.4\models\trading\trade_database.py" (
    echo [ERROR] Files not found in: %PATCH_DIR%
    echo.
    echo Please check:
    echo   1. You extracted the ZIP
    echo   2. The path is correct
    echo   3. The finbert_v4.4.4 folder exists inside
    echo.
    pause
    exit /b 1
)

echo [OK] Found patch files
echo.

REM Create backup
echo Creating backup...
set BACKUP_DIR=finbert_v4.4.4\BACKUP_MANUAL_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%\models\trading" 2>nul
mkdir "%BACKUP_DIR%\templates" 2>nul

copy finbert_v4.4.4\models\trading\*.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\app_finbert_v4_dev.py "%BACKUP_DIR%\" >nul 2>&1
copy finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\templates\" >nul 2>&1
echo [OK] Backup: %BACKUP_DIR%
echo.

REM Copy files
echo Copying updated files...
echo.

copy /Y "%PATCH_DIR%\finbert_v4.4.4\models\trading\trade_database.py" finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] trade_database.py) else (echo [OK] trade_database.py)

copy /Y "%PATCH_DIR%\finbert_v4.4.4\models\trading\paper_trading_engine.py" finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] paper_trading_engine.py) else (echo [OK] paper_trading_engine.py)

copy /Y "%PATCH_DIR%\finbert_v4.4.4\models\trading\portfolio_manager.py" finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (echo [FAIL] portfolio_manager.py) else (echo [OK] portfolio_manager.py)

copy /Y "%PATCH_DIR%\finbert_v4.4.4\app_finbert_v4_dev.py" finbert_v4.4.4\ >nul 2>&1
if errorlevel 1 (echo [FAIL] app_finbert_v4_dev.py) else (echo [OK] app_finbert_v4_dev.py)

copy /Y "%PATCH_DIR%\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html" finbert_v4.4.4\templates\ >nul 2>&1
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
echo Backup: %BACKUP_DIR%
echo.
echo NEXT STEPS:
echo.
echo 1. Reset account to $100,000:
echo    cd finbert_v4.4.4
echo    python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Reset to $100,000')"
echo.
echo 2. Verify:
echo    python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
echo.
echo    Expected: Cash: $100,000.00
echo.
echo ========================================================================
echo.
pause
