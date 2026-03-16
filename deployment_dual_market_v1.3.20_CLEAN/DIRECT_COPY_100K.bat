@echo off
REM =====================================================================
REM DIRECT COPY - PAPER TRADING $100K PATCH
REM =====================================================================
REM This copies files directly from PAPER_TRADING_100K_PATCH folder
REM Run this from C:\Users\david\AATelS\
REM =====================================================================

echo.
echo ========================================================================
echo    DIRECT COPY - PAPER TRADING $100K PATCH
echo ========================================================================
echo.
echo This will copy files from:
echo   C:\Users\david\AATelS\PAPER_TRADING_100K_PATCH\finbert_v4.4.4\
echo.
echo To:
echo   C:\Users\david\AATelS\finbert_v4.4.4\
echo.
pause

REM Check if we're in AATelS directory
if not exist "finbert_v4.4.4\models\trading\trade_database.py" (
    echo [ERROR] Not in C:\Users\david\AATelS directory
    echo Current: %CD%
    pause
    exit /b 1
)
echo [OK] In correct directory
echo.

REM Check if patch folder exists
if not exist "PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py" (
    echo [ERROR] Cannot find patch files!
    echo Looking for: PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py
    echo.
    echo Please check:
    echo   1. PAPER_TRADING_100K_PATCH folder exists in C:\Users\david\AATelS\
    echo   2. It contains finbert_v4.4.4\models\trading\ subfolders
    echo.
    dir PAPER_TRADING_100K_PATCH 2>nul
    echo.
    pause
    exit /b 1
)
echo [OK] Found patch files
echo.

REM Create backup
echo Creating backup...
set BACKUP_DIR=finbert_v4.4.4\BACKUP_DIRECT_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%\models\trading" 2>nul
mkdir "%BACKUP_DIR%\templates" 2>nul

copy finbert_v4.4.4\models\trading\trade_database.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\models\trading\paper_trading_engine.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\models\trading\portfolio_manager.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\app_finbert_v4_dev.py "%BACKUP_DIR%\" >nul 2>&1
copy finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\templates\" >nul 2>&1
echo [OK] Backup: %BACKUP_DIR%
echo.

REM Copy files one by one
echo Copying files...
echo.

echo Copying trade_database.py...
copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\
if errorlevel 1 (echo [FAIL] trade_database.py & pause & exit /b 1) else (echo [OK] trade_database.py)

echo Copying paper_trading_engine.py...
copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\paper_trading_engine.py finbert_v4.4.4\models\trading\
if errorlevel 1 (echo [FAIL] paper_trading_engine.py & pause & exit /b 1) else (echo [OK] paper_trading_engine.py)

echo Copying portfolio_manager.py...
copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\portfolio_manager.py finbert_v4.4.4\models\trading\
if errorlevel 1 (echo [FAIL] portfolio_manager.py & pause & exit /b 1) else (echo [OK] portfolio_manager.py)

echo Copying app_finbert_v4_dev.py...
copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\app_finbert_v4_dev.py finbert_v4.4.4\
if errorlevel 1 (echo [FAIL] app_finbert_v4_dev.py & pause & exit /b 1) else (echo [OK] app_finbert_v4_dev.py)

echo Copying finbert_v4_enhanced_ui.html...
copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html finbert_v4.4.4\templates\
if errorlevel 1 (echo [FAIL] finbert_v4_enhanced_ui.html & pause & exit /b 1) else (echo [OK] finbert_v4_enhanced_ui.html)

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
echo All 5 files copied successfully!
echo Backup: %BACKUP_DIR%
echo.
echo NEXT: Reset account to $100,000
echo.
echo Copy these commands:
echo.
echo   cd finbert_v4.4.4
echo   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Account reset to $100,000')"
echo.
echo Then verify:
echo.
echo   python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
echo.
echo Expected: Cash: $100,000.00
echo.
echo ========================================================================
echo.
pause
