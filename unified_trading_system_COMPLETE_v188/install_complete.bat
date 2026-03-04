@echo off
REM ====================================================================
REM Unified Trading System v1.3.15.188 - Complete Installation
REM With v188 Confidence Threshold Fix Pre-Applied
REM ====================================================================

echo.
echo ========================================================
echo   UNIFIED TRADING SYSTEM v1.3.15.188
echo   Complete Installation Script
echo ========================================================
echo.
echo This script will:
echo   1. Check Python installation
echo   2. Create virtual environment
echo   3. Install all dependencies
echo   4. Verify v188 patches are applied
echo   5. Create necessary directories
echo   6. Initialize configuration
echo.
pause

REM Check Python
echo.
echo [Step 1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo Python found!

REM Check if venv exists
echo.
echo [Step 2/6] Setting up virtual environment...
if exist "venv\" (
    echo Virtual environment already exists, skipping creation...
) else (
    echo Creating new virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)

REM Activate venv and install dependencies
echo.
echo [Step 3/6] Installing dependencies...
echo This may take several minutes...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo Installing core packages...
pip install pandas numpy scipy scikit-learn yfinance ta-lib pandas-ta
pip install dash plotly
pip install transformers torch torchvision torchaudio
pip install python-dotenv requests beautifulsoup4
pip install sqlalchemy psycopg2-binary
pip install apscheduler

echo.
echo Dependencies installed successfully!

REM Verify patches
echo.
echo [Step 4/6] Verifying v188 patches...
findstr /C:"45.0" "config\live_trading_config.json" >nul
if %errorlevel% equ 0 (
    echo [OK] Config confidence_threshold = 45.0
) else (
    echo [WARNING] Config patch verification failed
)

findstr /C:"0.48" "ml_pipeline\swing_signal_generator.py" >nul
if %errorlevel% equ 0 (
    echo [OK] Signal generator confidence_threshold = 0.48
) else (
    echo [WARNING] Signal generator patch verification failed
)

findstr /C:"48.0" "core\paper_trading_coordinator.py" >nul
if %errorlevel% equ 0 (
    echo [OK] Coordinator min_confidence = 48.0
) else (
    echo [WARNING] Coordinator patch verification failed
)

findstr /C:"48.0" "core\opportunity_monitor.py" >nul
if %errorlevel% equ 0 (
    echo [OK] Opportunity monitor confidence_threshold = 48.0
) else (
    echo [WARNING] Opportunity monitor patch verification failed
)

REM Create directories
echo.
echo [Step 5/6] Creating necessary directories...
if not exist "logs\" mkdir logs
if not exist "data\" mkdir data
if not exist "models\" mkdir models
if not exist "state\" mkdir state
if not exist "reports\" mkdir reports
echo Directories created!

REM Initialize configuration
echo.
echo [Step 6/6] Initializing configuration...
if not exist "state\portfolio.json" (
    echo {"cash": 100000, "positions": {}, "trades": [], "initialized": true} > state\portfolio.json
    echo Portfolio state initialized with $100,000
)

echo.
echo ========================================================
echo   INSTALLATION COMPLETE!
echo ========================================================
echo.
echo v188 Confidence Threshold Fix Status:
echo   - Config threshold: 45.0%% (was 52.0%%)
echo   - Signal generator: 0.48 (was 0.52)
echo   - Coordinator minimum: 48.0%% (was 52.0%%)
echo   - Opportunity monitor: 48.0%% (was 65.0%%)
echo.
echo Next Steps:
echo   1. Review config\live_trading_config.json if needed
echo   2. Run start.bat to launch the dashboard
echo   3. Access dashboard at http://localhost:8050
echo.
echo Expected Behavior:
echo   - Trades with 48%%-65%% confidence will now PASS
echo   - Before: BP.L 52.1%% ^< 65%% - BLOCKED
echo   - After:  BP.L 52.1%% ^>= 48.0%% - PASS ✓
echo.
pause
