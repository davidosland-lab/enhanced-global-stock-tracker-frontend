@echo off
REM ============================================================================
REM FinBERT v4.0 - Installation and Environment Diagnostic Tool
REM ============================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 - Diagnostic Tool
echo ========================================================================
echo.
echo This script will check your installation and diagnose any issues.
echo.
echo ========================================================================
echo.

REM Set color codes (optional)
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "RESET=[0m"

REM Store results
set "ALL_PASSED=1"

echo [DIAGNOSTIC 1/10] Checking Python Installation...
echo -----------------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%FAILED: Python is not installed or not in PATH%RESET%
    echo.
    echo Solution:
    echo   1. Download Python 3.8+ from https://www.python.org/downloads/
    echo   2. During installation, CHECK "Add Python to PATH"
    echo   3. Restart this script after installation
    echo.
    set "ALL_PASSED=0"
) else (
    python --version
    echo %GREEN%PASSED: Python is installed%RESET%
)
echo.

echo [DIAGNOSTIC 2/10] Checking Python Version (Requires 3.8+)...
echo -----------------------------------------------------------------------
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'); exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo %RED%FAILED: Python 3.8 or higher is required%RESET%
    python --version
    echo.
    echo Solution:
    echo   - Upgrade Python to version 3.8 or higher
    echo   - Download from https://www.python.org/downloads/
    echo.
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: Python version is compatible%RESET%
)
echo.

echo [DIAGNOSTIC 3/10] Checking pip Installation...
echo -----------------------------------------------------------------------
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%FAILED: pip is not installed%RESET%
    echo.
    echo Solution:
    echo   - Run: python -m ensurepip --upgrade
    echo   - Or reinstall Python with pip included
    echo.
    set "ALL_PASSED=0"
) else (
    python -m pip --version
    echo %GREEN%PASSED: pip is installed%RESET%
)
echo.

echo [DIAGNOSTIC 4/10] Checking Core Dependencies...
echo -----------------------------------------------------------------------
echo Checking Flask...
python -c "import flask; print(f'Flask {flask.__version__}')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: Flask not installed%RESET%
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: Flask is installed%RESET%
)

echo Checking pandas...
python -c "import pandas; print(f'pandas {pandas.__version__}')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: pandas not installed%RESET%
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: pandas is installed%RESET%
)

echo Checking yfinance...
python -c "import yfinance; print('yfinance installed')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: yfinance not installed%RESET%
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: yfinance is installed%RESET%
)

echo Checking torch...
python -c "import torch; print(f'PyTorch {torch.__version__}')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: PyTorch not installed%RESET%
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: PyTorch is installed%RESET%
)

echo Checking transformers...
python -c "import transformers; print(f'transformers {transformers.__version__}')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: transformers not installed%RESET%
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: transformers is installed%RESET%
)
echo.

echo [DIAGNOSTIC 5/10] Checking Required Files...
echo -----------------------------------------------------------------------
if exist app_finbert_v4_dev.py (
    echo %GREEN%PASSED: app_finbert_v4_dev.py found%RESET%
) else (
    echo %RED%FAILED: app_finbert_v4_dev.py not found%RESET%
    set "ALL_PASSED=0"
)

if exist templates\finbert_v4_enhanced_ui.html (
    echo %GREEN%PASSED: UI template found%RESET%
) else (
    echo %RED%FAILED: UI template not found%RESET%
    set "ALL_PASSED=0"
)

if exist models\backtesting\data_loader.py (
    echo %GREEN%PASSED: Data loader found%RESET%
) else (
    echo %RED%FAILED: Data loader not found%RESET%
    set "ALL_PASSED=0"
)

if exist models\backtesting\prediction_engine.py (
    echo %GREEN%PASSED: Prediction engine found%RESET%
) else (
    echo %RED%FAILED: Prediction engine not found%RESET%
    set "ALL_PASSED=0"
)

if exist models\backtesting\trading_simulator.py (
    echo %GREEN%PASSED: Trading simulator found%RESET%
) else (
    echo %RED%FAILED: Trading simulator not found%RESET%
    set "ALL_PASSED=0"
)
echo.

echo [DIAGNOSTIC 6/10] Checking Directory Structure...
echo -----------------------------------------------------------------------
if exist models (
    echo %GREEN%PASSED: models directory exists%RESET%
) else (
    echo %RED%FAILED: models directory missing%RESET%
    set "ALL_PASSED=0"
)

if exist templates (
    echo %GREEN%PASSED: templates directory exists%RESET%
) else (
    echo %RED%FAILED: templates directory missing%RESET%
    set "ALL_PASSED=0"
)

if not exist cache (
    echo %YELLOW%WARNING: cache directory missing - creating it...%RESET%
    mkdir cache
)
echo %GREEN%PASSED: cache directory exists%RESET%

if not exist logs (
    echo %YELLOW%WARNING: logs directory missing - creating it...%RESET%
    mkdir logs
)
echo %GREEN%PASSED: logs directory exists%RESET%
echo.

echo [DIAGNOSTIC 7/10] Testing Python Module Imports...
echo -----------------------------------------------------------------------
python -c "import sys; import os; sys.path.insert(0, os.path.join(os.getcwd(), 'models')); from backtesting import HistoricalDataLoader, BacktestPredictionEngine, TradingSimulator; print('SUCCESS: All backtesting modules imported')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: Cannot import backtesting modules%RESET%
    echo.
    echo This means the backtesting framework is not properly installed.
    echo.
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: All backtesting modules can be imported%RESET%
)
echo.

echo [DIAGNOSTIC 8/10] Testing Yahoo Finance Connection...
echo -----------------------------------------------------------------------
python -c "import yfinance as yf; ticker = yf.Ticker('AAPL'); data = ticker.history(period='1d'); print(f'SUCCESS: Downloaded {len(data)} rows for AAPL')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: Cannot connect to Yahoo Finance%RESET%
    echo.
    echo Possible causes:
    echo   - No internet connection
    echo   - Firewall blocking connection
    echo   - yfinance library issue
    echo.
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: Yahoo Finance connection working%RESET%
)
echo.

echo [DIAGNOSTIC 9/10] Testing Data Loader...
echo -----------------------------------------------------------------------
python -c "import sys; import os; from datetime import datetime, timedelta; sys.path.insert(0, os.path.join(os.getcwd(), 'models')); from backtesting import HistoricalDataLoader; start = (datetime.now() - timedelta(days=30)).strftime('%%Y-%%m-%%d'); end = datetime.now().strftime('%%Y-%%m-%%d'); loader = HistoricalDataLoader('AAPL', start, end); data = loader.load_price_data(); print(f'SUCCESS: Loaded {len(data)} rows of AAPL data')" 2>nul
if errorlevel 1 (
    echo %RED%FAILED: Data loader test failed%RESET%
    echo.
    echo Running detailed error check...
    python -c "import sys; import os; from datetime import datetime, timedelta; sys.path.insert(0, os.path.join(os.getcwd(), 'models')); from backtesting import HistoricalDataLoader; start = (datetime.now() - timedelta(days=30)).strftime('%%Y-%%m-%%d'); end = datetime.now().strftime('%%Y-%%m-%%d'); loader = HistoricalDataLoader('AAPL', start, end); data = loader.load_price_data(); print(f'Loaded {len(data)} rows')"
    echo.
    set "ALL_PASSED=0"
) else (
    echo %GREEN%PASSED: Data loader is working correctly%RESET%
)
echo.

echo [DIAGNOSTIC 10/10] Testing Flask Application Startup...
echo -----------------------------------------------------------------------
echo Starting Flask app for 5 seconds to test...
timeout /t 1 >nul
start /B python app_finbert_v4_dev.py >flask_test.log 2>&1
timeout /t 5 >nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FinBERT*" >nul 2>&1

if exist flask_test.log (
    findstr /C:"Running on" flask_test.log >nul
    if errorlevel 1 (
        echo %RED%FAILED: Flask app failed to start%RESET%
        echo.
        echo Error log:
        type flask_test.log
        echo.
        set "ALL_PASSED=0"
    ) else (
        echo %GREEN%PASSED: Flask app started successfully%RESET%
    )
    del flask_test.log >nul 2>&1
) else (
    echo %YELLOW%WARNING: Could not test Flask startup%RESET%
)
echo.

REM Final summary
echo ========================================================================
echo   DIAGNOSTIC SUMMARY
echo ========================================================================
echo.

if "%ALL_PASSED%"=="1" (
    echo %GREEN%ALL DIAGNOSTICS PASSED!%RESET%
    echo.
    echo Your FinBERT v4.0 installation is ready to use.
    echo.
    echo Next steps:
    echo   1. Run START_PARAMETER_OPTIMIZATION.bat to start the application
    echo   2. Open http://localhost:5001 in your browser
    echo   3. Try running a backtest on AAPL with default settings
    echo.
) else (
    echo %RED%SOME DIAGNOSTICS FAILED!%RESET%
    echo.
    echo Please fix the issues listed above and run this diagnostic again.
    echo.
    echo Common solutions:
    echo   - If dependencies are missing, run: INSTALL.bat
    echo   - If Python is not found, install Python 3.8+ and add to PATH
    echo   - If files are missing, re-extract the deployment ZIP
    echo.
)

echo ========================================================================
echo.

REM Save diagnostic results to file
echo Diagnostic completed on %DATE% at %TIME% > diagnostic_results.txt
echo. >> diagnostic_results.txt
echo See console output above for details. >> diagnostic_results.txt

echo Diagnostic results saved to: diagnostic_results.txt
echo.
pause
