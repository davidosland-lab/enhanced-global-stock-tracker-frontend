@echo off
echo ============================================================
echo    ML STOCK PREDICTOR - REAL DATA ONLY
echo ============================================================
echo.
echo NO mock, demo, simulated, or synthetic data!
echo Only REAL market data from Yahoo Finance & Alpha Vantage
echo.

:: Clean environment
del /q .env 2>nul
del /q .flaskenv 2>nul
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

echo [1/3] Cleaning environment...
echo       Done

echo [2/3] Checking dependencies...
python -c "import yfinance, pandas, flask" 2>nul
if errorlevel 1 (
    echo.
    echo Installing required packages...
    pip install yfinance pandas flask flask-cors numpy scikit-learn
)

echo [3/3] Starting REAL DATA server...
echo.
echo ============================================================
echo Server: http://localhost:8000
echo.
echo This server ONLY uses real market data:
echo   - Real-time prices from Yahoo Finance
echo   - Historical data from Alpha Vantage
echo   - NO mock/demo data whatsoever
echo.
echo Try these REAL symbols:
echo   US: AAPL, MSFT, GOOGL, AMZN, TSLA
echo   AU: CBA.AX, BHP.AX, CSL.AX, WBC.AX
echo ============================================================
echo.

python real_data_server.py

pause