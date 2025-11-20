@echo off
REM ============================================================================
REM Regime Engine Diagnostic Script
REM ============================================================================
REM This script runs comprehensive diagnostics on the Market Regime Engine
REM to identify why it's returning UNKNOWN regime and none method
REM ============================================================================

REM Ensure window stays open even if there's an error
setlocal EnableDelayedExpansion

echo.
echo ================================================================================
echo MARKET REGIME ENGINE - COMPREHENSIVE DIAGNOSTICS
echo ================================================================================
echo.
echo This diagnostic will run 7 tests to identify issues with the regime engine.
echo The window will NOT close until you press a key at the end.
echo.

REM Check Python version
echo [1/7] Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python not found in PATH
    echo.
    echo Please ensure Python is installed and added to PATH.
    echo.
    goto :END
)
echo.
echo Press any key to continue to package check...
pause >nul
echo.

REM Check required packages
echo [2/7] Checking required packages...
python -c "import pandas; print(f'pandas: {pandas.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
python -c "import yfinance; print(f'yfinance: {yfinance.__version__}')"
python -c "import sys; exec('try:\n    import hmmlearn\n    print(f\"hmmlearn: {hmmlearn.__version__}\")\nexcept:\n    print(\"hmmlearn: NOT INSTALLED (will use GMM fallback)\")')"
python -c "import sys; exec('try:\n    import arch\n    print(f\"arch: {arch.__version__}\")\nexcept:\n    print(\"arch: NOT INSTALLED (will use EWMA fallback)\")')"
echo.
echo Press any key to continue to next check...
pause >nul
echo.

REM Check if regime engine module exists
echo [3/7] Checking regime engine modules...
if exist "models\screening\market_regime_engine.py" (
    echo ✓ market_regime_engine.py found
) else (
    echo.
    echo ✗ market_regime_engine.py NOT FOUND
    echo.
    echo ERROR: Core regime engine file is missing!
    echo Please ensure you're running from the correct directory.
    echo.
    goto :END
)
if exist "models\screening\regime_detector.py" (
    echo ✓ regime_detector.py found
) else (
    echo ✗ regime_detector.py NOT FOUND
)
if exist "models\screening\volatility_forecaster.py" (
    echo ✓ volatility_forecaster.py found
) else (
    echo ✗ volatility_forecaster.py NOT FOUND
)
echo.
echo Press any key to continue to detailed diagnostic...
pause >nul
echo.

REM Run detailed diagnostic
echo [4/7] Running detailed regime engine diagnostic...
echo.
python -c "
import sys
sys.path.insert(0, '.')

print('='*80)
print('STEP 1: Import Test')
print('='*80)
try:
    from models.screening.market_regime_engine import MarketRegimeEngine
    print('✓ MarketRegimeEngine imported successfully')
except Exception as e:
    print(f'✗ Import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print('='*80)
print('STEP 2: Initialization Test')
print('='*80)
try:
    engine = MarketRegimeEngine()
    print('✓ MarketRegimeEngine instance created')
    print(f'  - Index symbol: {engine.config.index_symbol}')
    print(f'  - VIX symbol: {engine.config.vol_symbol}')
    print(f'  - FX symbol: {engine.config.fx_symbol}')
    print(f'  - Lookback days: {engine.config.lookback_days}')
except Exception as e:
    print(f'✗ Initialization failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print('='*80)
print('STEP 3: Data Fetch Test')
print('='*80)
print('Fetching market data (this may take 10-30 seconds)...')
print()

try:
    result = engine.analyse()
    
    print('✓ Analysis completed')
    print()
    print('='*80)
    print('RESULTS:')
    print('='*80)
    print(f'  Regime Label: {result.get(\"regime_label\", \"N/A\").upper()}')
    print(f'  Volatility Method: {result.get(\"vol_method\", \"N/A\")}')
    print(f'  Volatility (1-day): {result.get(\"vol_1d\", \"N/A\")}')
    print(f'  Volatility (annual): {result.get(\"vol_annual\", \"N/A\")}')
    print(f'  Crash Risk Score: {result.get(\"crash_risk_score\", 0.0):.2f}/1.0')
    print(f'  Data Window: {result.get(\"data_window\", {})}')
    
    if result.get('error'):
        print(f'  ERROR: {result[\"error\"]}')
    if result.get('warning'):
        print(f'  WARNING: {result[\"warning\"]}')
    
    print()
    print('='*80)
    print('DIAGNOSTIC SUMMARY:')
    print('='*80)
    
    regime = result.get('regime_label', 'unknown')
    method = result.get('vol_method', 'none')
    
    if regime == 'unknown' and method == 'none':
        print('✗ ISSUE DETECTED: Regime engine not working')
        print()
        print('Possible causes:')
        print('  1. Data fetch failed (check network/internet)')
        print('  2. Insufficient data after feature engineering')
        print('  3. yfinance returned empty dataframe')
        print('  4. Column extraction issue (MultiIndex problem)')
        print()
        print('Check the logs above for specific error messages.')
    else:
        print('✓ Regime engine working correctly!')
        print(f'  Detected regime: {regime.upper()}')
        print(f'  Using method: {method}')
    
except Exception as e:
    print(f'✗ Analysis failed: {e}')
    import traceback
    print()
    print('Full traceback:')
    traceback.print_exc()
    sys.exit(1)

print()
print('='*80)
" 2>&1

echo.
echo Press any key to continue to yfinance data test...
pause >nul
echo.
echo [5/7] Checking yfinance data fetch directly...
echo.
python -c "
import yfinance as yf
from datetime import datetime, timedelta

end = datetime.now().date()
start = end - timedelta(days=180)

print(f'Fetching ASX 200 (^AXJO) from {start} to {end}...')
try:
    data = yf.download('^AXJO', start=start, end=end, progress=False)
    print(f'✓ Got {len(data)} rows of data')
    if len(data) > 0:
        print(f'  Columns: {list(data.columns)}')
        print(f'  First date: {data.index[0]}')
        print(f'  Last date: {data.index[-1]}')
    else:
        print('✗ Empty dataframe returned')
except Exception as e:
    print(f'✗ Fetch failed: {e}')
" 2>&1

echo.
echo Press any key to continue to MultiIndex test...
pause >nul
echo.
echo [6/7] Checking MultiIndex extraction...
echo.
python -c "
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

end = datetime.now().date()
start = end - timedelta(days=180)

print('Fetching multiple tickers (^AXJO, AUDUSD=X)...')
try:
    data = yf.download(['^AXJO', 'AUDUSD=X'], start=start, end=end, progress=False)
    print(f'✓ Got {len(data)} rows')
    print(f'  DataFrame shape: {data.shape}')
    print(f'  Column type: {type(data.columns)}')
    
    if isinstance(data.columns, pd.MultiIndex):
        print(f'  MultiIndex levels: {data.columns.nlevels}')
        print(f'  Level 0 (should be tickers): {list(data.columns.get_level_values(0).unique())}')
        print(f'  Level 1 (should be price types): {list(data.columns.get_level_values(1).unique())}')
        
        # Try to extract Close prices
        if 'Close' in data.columns.get_level_values(1):
            close = data.xs('Close', level=1, axis=1)
            print(f'✓ Successfully extracted Close prices: shape={close.shape}')
            print(f'  Close columns: {list(close.columns)}')
        else:
            print('✗ Cannot find Close in level 1')
    else:
        print(f'  Regular columns: {list(data.columns)}')
        
except Exception as e:
    print(f'✗ Fetch failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

echo.
echo Press any key to check file paths...
pause >nul
echo.
echo [7/7] Checking Windows file path...
echo.
echo Current directory: %CD%
echo Python path:
python -c "import sys; print('\n'.join(sys.path))"

echo.

:END
REM ==============================================================================
REM Final summary and exit (always reaches here)
REM ==============================================================================
echo.
echo ================================================================================
echo DIAGNOSTICS COMPLETE
echo ================================================================================
echo.
echo SUMMARY OF CHECKS:
echo   [1/7] Python Installation
echo   [2/7] Required Packages
echo   [3/7] Regime Engine Modules
echo   [4/7] Regime Engine Analysis (MAIN TEST)
echo   [5/7] yfinance Single Ticker
echo   [6/7] yfinance Multiple Tickers (MultiIndex)
echo   [7/7] File Paths
echo.
echo If you see "UNKNOWN" regime and "none" method, check the diagnostic output
echo above to identify the specific issue.
echo.
echo Common fixes:
echo   - Internet connection issue: Check network/firewall
echo   - Empty data: yfinance might be rate-limited, try again later
echo   - MultiIndex issue: File might not have latest fix (commit 91783bb)
echo   - Import error: Check Python path and module structure
echo.
echo ================================================================================
echo.
echo DIAGNOSTICS FINISHED!
echo.
echo Please review the output above carefully.
echo You can scroll up to see all the test results.
echo.
echo Press ANY KEY to exit (window will close after you press a key)...
echo ================================================================================
pause >nul
echo.
echo Window closing...
timeout /t 2 >nul
exit /b 0
