@echo off
echo ================================================================================
echo FINBERT ULTIMATE TRADING SYSTEM - REAL DATA ONLY
echo ================================================================================
echo.

echo Step 1: Cleaning environment...
REM Remove corrupted files
if exist ".env" del /f /q ".env"
RMDIR /S /Q "%USERPROFILE%\.cache\py-yfinance" 2>nul
RMDIR /S /Q "%LOCALAPPDATA%\py-yfinance" 2>nul

echo.
echo Step 2: Installing real indicators module...
copy /Y "australian_market_indicators_REAL.py" "australian_market_indicators.py" 2>nul

echo.
echo Step 3: Setting environment...
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUNBUFFERED=1

echo.
echo ================================================================================
echo Starting FinBERT with 100%% REAL MARKET DATA
echo ================================================================================
echo.
echo Features:
echo   ✓ Real-time stock prices (US and Australian)
echo   ✓ Live ASX200, All Ordinaries indices
echo   ✓ Actual commodity prices (Gold, Oil, Iron Ore)
echo   ✓ Real currency rates (AUD/USD, AUD/CNY)
echo   ✓ Live technical indicators (RSI, MACD, Bollinger Bands)
echo   ✓ Top ASX stocks (CBA, BHP, CSL, banks, miners)
echo   ✓ China market data (Shanghai, Hang Seng)
echo   ✓ NO FAKE/SYNTHETIC/FALLBACK DATA
echo.
echo Server starting on: http://localhost:5000
echo.
echo To view charts:
echo   - Open finbert_charts.html for standard view
echo   - Open finbert_charts_australian.html for ASX focus
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

python app_finbert_api_FINAL_FIX.py