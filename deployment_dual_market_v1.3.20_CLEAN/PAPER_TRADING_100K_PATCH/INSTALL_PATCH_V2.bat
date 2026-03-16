@echo off
REM =====================================================================
REM PAPER TRADING $100K PATCH INSTALLER V2
REM =====================================================================
REM Simplified version with better verification
REM =====================================================================

echo.
echo ========================================================================
echo    PAPER TRADING $100K PATCH INSTALLER V2
echo ========================================================================
echo.
echo This patch will update your paper trading account limit:
echo   FROM: $10,000
echo   TO:   $100,000
echo.
pause

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo ======================================================================
    echo ERROR: Wrong directory!
    echo ======================================================================
    echo.
    echo Current directory: %CD%
    echo.
    echo This script must be run from: C:\Users\david\AATelS\
    echo.
    echo Please:
    echo   1. Open Command Prompt
    echo   2. Type: cd C:\Users\david\AATelS
    echo   3. Type: PAPER_TRADING_100K_PATCH\INSTALL_PATCH_V2.bat
    echo.
    pause
    exit /b 1
)

REM Check if patch directory exists
if not exist "PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo ======================================================================
    echo ERROR: Patch files not found!
    echo ======================================================================
    echo.
    echo Current directory: %CD%
    echo.
    echo Please ensure you extracted PAPER_TRADING_100K_PATCH.zip to C:\Users\david\AATelS\
    echo.
    pause
    exit /b 1
)

echo.
echo Step 1: Creating Backup
echo ========================================================================
set BACKUP_DIR=finbert_v4.4.4\BACKUP_PAPER_TRADING_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

mkdir "%BACKUP_DIR%\models\trading" 2>nul
mkdir "%BACKUP_DIR%\templates" 2>nul

echo Backing up original files...
copy finbert_v4.4.4\models\trading\trade_database.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\models\trading\paper_trading_engine.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\models\trading\portfolio_manager.py "%BACKUP_DIR%\models\trading\" >nul 2>&1
copy finbert_v4.4.4\app_finbert_v4_dev.py "%BACKUP_DIR%\" >nul 2>&1
copy finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\templates\" >nul 2>&1

echo Backup created: %BACKUP_DIR%
echo.

echo Step 2: Installing Updated Files
echo ========================================================================
echo Copying updated files...
echo.

REM Ensure target directories exist
mkdir finbert_v4.4.4\models\trading 2>nul
mkdir finbert_v4.4.4\templates 2>nul

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\
if errorlevel 1 (
    echo [X] Failed: trade_database.py
    goto :error
) else (
    echo [OK] Updated: models\trading\trade_database.py
)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\paper_trading_engine.py finbert_v4.4.4\models\trading\
if errorlevel 1 (
    echo [X] Failed: paper_trading_engine.py
    goto :error
) else (
    echo [OK] Updated: models\trading\paper_trading_engine.py
)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\portfolio_manager.py finbert_v4.4.4\models\trading\
if errorlevel 1 (
    echo [X] Failed: portfolio_manager.py
    goto :error
) else (
    echo [OK] Updated: models\trading\portfolio_manager.py
)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\app_finbert_v4_dev.py finbert_v4.4.4\
if errorlevel 1 (
    echo [X] Failed: app_finbert_v4_dev.py
    goto :error
) else (
    echo [OK] Updated: app_finbert_v4_dev.py
)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html finbert_v4.4.4\templates\
if errorlevel 1 (
    echo [X] Failed: finbert_v4_enhanced_ui.html
    goto :error
) else (
    echo [OK] Updated: templates\finbert_v4_enhanced_ui.html
)

echo.
echo Step 3: Clearing Python Cache
echo ========================================================================
for /d /r finbert_v4.4.4\models\trading %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /q finbert_v4.4.4\models\trading\*.pyc 2>nul
echo Python cache cleared
echo.

echo Step 4: Basic Verification
echo ========================================================================
echo Checking if files contain $100,000 references...
echo.

findstr /C:"100000" finbert_v4.4.4\models\trading\trade_database.py >nul
if errorlevel 1 (
    echo [!] Warning: trade_database.py may not contain 100000
) else (
    echo [OK] trade_database.py contains 100000
)

findstr /C:"100000" finbert_v4.4.4\models\trading\paper_trading_engine.py >nul
if errorlevel 1 (
    echo [!] Warning: paper_trading_engine.py may not contain 100000
) else (
    echo [OK] paper_trading_engine.py contains 100000
)

findstr /C:"$100,000" finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html >nul
if errorlevel 1 (
    echo [!] Warning: finbert_v4_enhanced_ui.html may not contain $100,000
) else (
    echo [OK] finbert_v4_enhanced_ui.html contains $100,000
)

echo.
echo ========================================================================
echo    INSTALLATION COMPLETE!
echo ========================================================================
echo.
echo Files have been updated successfully!
echo Backup location: %BACKUP_DIR%
echo.
echo NEXT STEPS:
echo ========================================================================
echo.
echo 1. Reset your paper trading account to $100,000:
echo.
echo    cd finbert_v4.4.4
echo    python -c "from models.trading.paper_trading_engine import PaperTradingEngine; PaperTradingEngine().reset_account(100000); print('Account reset to $100,000')"
echo.
echo 2. Verify the new balance:
echo.
echo    python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
echo.
echo    Expected: Cash: $100,000.00
echo.
echo 3. Test the Web UI:
echo.
echo    python app_finbert_v4_dev.py
echo    Open: http://localhost:5000
echo    Check: Paper Trading tab shows $100,000
echo.
echo ========================================================================
echo.
pause
exit /b 0

:error
echo.
echo ========================================================================
echo    ERROR DURING INSTALLATION
echo ========================================================================
echo.
echo Some files failed to copy.
echo.
echo Your original files are backed up in:
echo %BACKUP_DIR%
echo.
echo You can try:
echo 1. Running this script as Administrator
echo 2. Using the manual installation (see TROUBLESHOOTING.txt)
echo.
pause
exit /b 1
