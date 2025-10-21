@echo off
cls
echo ==============================================================================
echo                         ML STOCK PREDICTOR - START SERVER
echo ==============================================================================
echo.

REM First, make sure we're using the right yfinance version
echo Checking yfinance installation...
python -c "import yfinance as yf; print(f'yfinance version: {yf.__version__}')"
echo.

REM Quick connectivity test
echo Testing Yahoo Finance connection...
python -c "import yfinance as yf; t = yf.Ticker('AAPL'); h = t.history(period='1d'); print(f'Connection OK! AAPL: ${h[\"Close\"].iloc[-1]:.2f}')" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Yahoo Finance connection failed!
    echo Please run INSTALL_WINDOWS.bat first
    echo.
    pause
    exit /b 1
)

echo.
echo Starting ML Stock Prediction Server...
echo ------------------------------------------------------------------------------
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ==============================================================================
echo.

REM Start the server
python ml_core_windows.py

REM If server stops or crashes
echo.
echo ==============================================================================
echo Server stopped.
echo.
pause