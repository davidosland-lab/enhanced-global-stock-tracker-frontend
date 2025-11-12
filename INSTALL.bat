@echo off
setlocal enabledelayedexpansion

:: =========================================
:: FinBERT v4.4.5 - Stock Screening System
:: Windows 11 Complete Installation Package
:: =========================================

color 0A
cls

echo.
echo  ============================================================
echo   FINBERT v4.4.5 - STOCK SCREENING SYSTEM INSTALLER
echo   Windows 11 Edition with All Latest Fixes
echo  ============================================================
echo.
echo  This installer will:
echo   1. Check Python installation (3.8+ required)
echo   2. Create virtual environment
echo   3. Install all dependencies
echo   4. Configure the application
echo   5. Create desktop shortcuts
echo   6. Test the installation
echo.
echo  ============================================================
echo.
pause

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo  [WARNING] Not running as Administrator
    echo  Some features may require admin privileges
    echo.
    pause
)

:: Set installation directory
set "INSTALL_DIR=%cd%"
echo  Installation Directory: %INSTALL_DIR%
echo.

:: Step 1: Check Python Installation
echo  [STEP 1/7] Checking Python installation...
echo  ------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH
    echo.
    echo  Please install Python 3.8 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo  [OK] Python !PYTHON_VERSION! detected
)

:: Step 2: Create Virtual Environment
echo.
echo  [STEP 2/7] Creating virtual environment...
echo  ------------------------------------------
if exist venv (
    echo  Virtual environment already exists. Removing old environment...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo  [OK] Virtual environment created

:: Step 3: Activate Virtual Environment and Upgrade pip
echo.
echo  [STEP 3/7] Activating environment and upgrading pip...
echo  ------------------------------------------
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo  [OK] Environment activated and pip upgraded

:: Step 4: Install Required Packages
echo.
echo  [STEP 4/7] Installing required packages...
echo  ------------------------------------------
echo  This may take 5-10 minutes...
echo.

:: Core dependencies
echo  Installing core dependencies...
pip install --no-cache-dir yfinance==0.2.33 pandas==2.1.3 numpy==1.24.3 requests==2.31.0 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Deep learning and ML
echo  Installing machine learning libraries...
pip install --no-cache-dir scikit-learn==1.3.2 tensorflow==2.15.0 keras==2.15.0 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: NLP and sentiment
echo  Installing NLP libraries...
pip install --no-cache-dir transformers==4.35.2 torch==2.1.1 sentencepiece==0.1.99 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Web scraping and APIs
echo  Installing web scraping libraries...
pip install --no-cache-dir beautifulsoup4==4.12.2 lxml==4.9.3 selenium==4.15.2 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Flask and web framework
echo  Installing web framework...
pip install --no-cache-dir flask==3.0.0 flask-cors==4.0.0 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

:: Utilities
echo  Installing additional utilities...
pip install --no-cache-dir pytz==2023.3 python-dateutil==2.8.2 openpyxl==3.1.2 >nul 2>&1
if %errorlevel% neq 0 goto :install_error

echo  [OK] All packages installed successfully

:: Step 5: Create Configuration
echo.
echo  [STEP 5/7] Creating configuration...
echo  ------------------------------------------

:: Create necessary directories
if not exist "logs\screening" mkdir logs\screening
if not exist "reports\morning_reports" mkdir reports\morning_reports
if not exist "reports\screening_results" mkdir reports\screening_results
if not exist "complete_deployment\cache" mkdir complete_deployment\cache

echo  [OK] Directories created

:: Step 6: Create Shortcuts and Batch Files
echo.
echo  [STEP 6/7] Creating shortcuts...
echo  ------------------------------------------

:: Create RUN_STOCK_SCREENER.bat
(
echo @echo off
echo :: FinBERT Stock Screener - Main Runner
echo color 0A
echo cls
echo.
echo ============================================================
echo  FINBERT STOCK SCREENER - OVERNIGHT SCREENING
echo ============================================================
echo.
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo.
echo echo Starting overnight stock screening...
echo echo.
echo echo This will:
echo echo   1. Check SPI market sentiment
echo echo   2. Scan ASX stocks across all sectors
echo echo   3. Generate ML predictions
echo echo   4. Score opportunities
echo echo   5. Create morning report
echo echo.
echo echo Press Ctrl+C to cancel
echo timeout /t 5 /nobreak
echo.
echo python complete_deployment\scripts\screening\run_overnight_screener.py
echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo.
echo     echo ============================================================
echo     echo  SCREENING COMPLETE!
echo     echo ============================================================
echo     echo.
echo     echo Check reports\morning_reports\ for your morning report
echo     echo.
echo ^) else ^(
echo     echo.
echo     echo [ERROR] Screening failed - check logs\screening\ for details
echo     echo.
echo ^)
echo.
echo pause
) > RUN_STOCK_SCREENER.bat

:: Create RUN_STOCK_SCREENER_TEST.bat
(
echo @echo off
echo :: FinBERT Stock Screener - Test Mode ^(Fast^)
echo color 0A
echo cls
echo.
echo ============================================================
echo  FINBERT STOCK SCREENER - TEST MODE
echo ============================================================
echo.
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo.
echo echo Running screener in TEST MODE...
echo echo ^(Scans only 5 stocks per sector for quick testing^)
echo echo.
echo timeout /t 3 /nobreak
echo.
echo python complete_deployment\scripts\screening\run_overnight_screener.py --test
echo.
echo pause
) > RUN_STOCK_SCREENER_TEST.bat

:: Create START_FINBERT_WEB.bat
(
echo @echo off
echo :: FinBERT Web Application Launcher
echo color 0A
echo cls
echo.
echo ============================================================
echo  FINBERT WEB APPLICATION
echo ============================================================
echo.
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo cd complete_deployment\finbert_v4.4.4
echo.
echo echo Starting FinBERT web application...
echo echo.
echo echo Server will run at: http://localhost:5000
echo echo.
echo echo Press Ctrl+C to stop the server
echo echo.
echo timeout /t 2 /nobreak
echo.
echo python app_finbert_v4_dev.py
echo.
echo pause
) > START_FINBERT_WEB.bat

:: Create OPEN_DASHBOARD.bat
(
echo @echo off
echo echo Opening FinBERT Dashboard in your default browser...
echo timeout /t 2 /nobreak ^>nul
echo start http://localhost:5000
) > OPEN_DASHBOARD.bat

:: Create STOP_ALL.bat
(
echo @echo off
echo echo Stopping all FinBERT processes...
echo taskkill /F /IM python.exe 2^>nul
echo echo All processes stopped.
echo pause
) > STOP_ALL.bat

:: Create Desktop Shortcut (if desktop exists)
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    echo Creating desktop shortcuts...
    
    :: Create VBS script to make shortcuts
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%DESKTOP%\FinBERT Stock Screener.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "%INSTALL_DIR%\RUN_STOCK_SCREENER.bat"
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.Description = "Run FinBERT Overnight Stock Screener"
    echo oLink.IconLocation = "%%SystemRoot%%\System32\SHELL32.dll, 138"
    echo oLink.Save
    ) > CreateShortcut.vbs
    
    cscript CreateShortcut.vbs >nul 2>&1
    del CreateShortcut.vbs
    
    echo  [OK] Desktop shortcut created
) else (
    echo  [INFO] Desktop not found, skipping shortcut creation
)

echo  [OK] Batch files and shortcuts created

:: Step 7: Test Installation
echo.
echo  [STEP 7/7] Testing installation...
echo  ------------------------------------------
python -c "import yfinance, pandas, numpy, sklearn, transformers; print('[OK] All critical imports successful')" 2>nul
if %errorlevel% neq 0 (
    echo  [WARNING] Some imports failed, but installation may still work
) else (
    echo  [OK] Installation test passed
)

:: Installation Complete
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  To use the application:
echo.
echo  1. RUN STOCK SCREENER (Overnight):
echo     Double-click: RUN_STOCK_SCREENER.bat
echo     Or use desktop shortcut: "FinBERT Stock Screener"
echo.
echo  2. TEST MODE (Quick):
echo     Double-click: RUN_STOCK_SCREENER_TEST.bat
echo     ^(Scans only 5 stocks per sector for testing^)
echo.
echo  3. START WEB APPLICATION:
echo     Double-click: START_FINBERT_WEB.bat
echo     Then open: http://localhost:5000
echo.
echo  4. STOP ALL PROCESSES:
echo     Double-click: STOP_ALL.bat
echo.
echo  ============================================================
echo.
echo  Important Notes:
echo  - First run will be slower as it downloads data
echo  - Stock screener is designed for overnight use ^(10PM-7AM^)
echo  - Alpha Vantage API has 500 calls/day limit
echo  - Check logs\screening\ if you encounter issues
echo.
echo  ============================================================
echo.
pause
exit /b 0

:install_error
echo  [ERROR] Package installation failed
echo  Please check your internet connection and try again
echo.
echo  If the problem persists:
echo  1. Make sure you have Python 3.8 or higher
echo  2. Try running as Administrator
echo  3. Check your antivirus isn't blocking pip
echo.
pause
exit /b 1
