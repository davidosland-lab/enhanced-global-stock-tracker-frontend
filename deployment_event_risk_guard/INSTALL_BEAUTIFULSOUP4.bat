@echo off
REM ====================================================================
REM Install beautifulsoup4 - Standalone Installer
REM ====================================================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ========================================================================
echo   BEAUTIFULSOUP4 INSTALLER
echo ========================================================================
echo.
echo This script will install beautifulsoup4 (HTML parsing library)
echo Required for: Web scraping, news parsing, ASX announcements
echo.
echo Installing beautifulsoup4...
echo.

REM Try method 1: Standard pip install
python -m pip install beautifulsoup4>=4.12.0

if errorlevel 1 (
    echo.
    echo [WARNING] Standard installation failed. Trying alternative method...
    echo.
    
    REM Try method 2: pip without -m flag
    pip install beautifulsoup4>=4.12.0
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Both installation methods failed.
        echo.
        echo Possible solutions:
        echo   1. Run Command Prompt as Administrator
        echo   2. Clear pip cache: pip cache purge
        echo   3. Upgrade pip: python -m pip install --upgrade pip
        echo   4. Install specific version: pip install beautifulsoup4==4.12.3
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================================================
echo   VERIFYING INSTALLATION
echo ========================================================================
echo.

REM Verify installation
python -c "import bs4; print('✓ beautifulsoup4 version:', bs4.__version__)" 2>nul

if errorlevel 1 (
    echo [ERROR] Installation completed but verification failed.
    echo beautifulsoup4 may not be properly installed.
    echo.
    echo Try running VERIFY_INSTALLATION.bat to check all packages.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   INSTALLATION SUCCESSFUL
echo ========================================================================
echo.
echo beautifulsoup4 has been successfully installed.
echo.
echo Next steps:
echo   1. Run VERIFY_INSTALLATION.bat to confirm all packages
echo   2. Run TRAIN_LSTM_SINGLE.bat CBA.AX to test training
echo   3. Run RUN_OVERNIGHT_PIPELINE.bat for production scan
echo.
pause
