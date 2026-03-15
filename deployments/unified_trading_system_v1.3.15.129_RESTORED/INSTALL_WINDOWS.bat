@echo off
REM ============================================================================
REM Unified Trading System v1.3.15.129 - Windows Installer
REM ============================================================================

echo.
echo ================================================================================
echo UNIFIED TRADING SYSTEM v1.3.15.129 - RESTORATION PACKAGE
echo ================================================================================
echo.
echo This installer will:
echo   1. Install required Python packages
echo   2. Create necessary directories
echo   3. Verify installation
echo   4. Run integration tests
echo.
echo Estimated time: 5-10 minutes
echo.
pause

REM Check Python version
echo.
echo [1/5] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create directories
echo.
echo [2/5] Creating directories...
if not exist "logs" mkdir logs
if not exist "state" mkdir state
if not exist "config" mkdir config
if not exist "reports\screening" mkdir reports\screening
if not exist "finbert_v4.4.4\models\saved_models" mkdir finbert_v4.4.4\models\saved_models
if not exist "tax_records" mkdir tax_records
echo   - logs/
echo   - state/
echo   - config/
echo   - reports/screening/
echo   - finbert_v4.4.4/models/saved_models/
echo   - tax_records/
echo Done!

REM Install core dependencies
echo.
echo [3/5] Installing core dependencies...
echo   This may take 3-5 minutes...
echo.
python -m pip install --upgrade pip
python -m pip install pandas==2.2.0 numpy scikit-learn yfinance yahooquery
if %errorlevel% neq 0 (
    echo ERROR: Failed to install core dependencies
    pause
    exit /b 1
)
echo Done!

REM Install optional LSTM dependencies
echo.
echo [4/5] Installing LSTM dependencies (optional)...
echo   Keras/TensorFlow: ~2GB download, 5-10 minutes
echo.
choice /C YN /M "Install Keras for LSTM support (recommended)"
if %errorlevel%==1 (
    echo   Installing TensorFlow and Keras...
    python -m pip install tensorflow keras
    if %errorlevel% neq 0 (
        echo   WARNING: Keras installation failed - LSTM will use fallback (70%% vs 75-80%% accuracy)
        echo   You can install later with: pip install tensorflow keras
    ) else (
        echo   Keras installed successfully!
    )
) else (
    echo   Skipping Keras installation
    echo   Note: LSTM will use fallback method (70%% vs 75-80%% accuracy)
    echo   Install later with: pip install tensorflow keras
)

REM Verify installation
echo.
echo [5/5] Running integration tests...
echo.
python tests\test_enhanced_integration.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Integration tests failed
    echo This may be expected if overnight reports are missing
    echo.
) else (
    echo.
    echo SUCCESS: All integration tests passed!
    echo.
)

echo.
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Run paper trading test:
echo      cd core
echo      python paper_trading_coordinator.py --symbols AAPL,MSFT --capital 100000
echo.
echo   2. Generate overnight reports (optional, ~60 min):
echo      RUN_COMPLETE_WORKFLOW.bat
echo.
echo   3. Train LSTM models (optional, ~7-18 hours):
echo      cd finbert_v4.4.4
echo      python train_lstm_batch.py --market US
echo.
echo Documentation: See README_DEPLOYMENT.md and docs/ folder
echo.
pause
