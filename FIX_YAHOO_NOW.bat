@echo off
cls
echo ==============================================================================
echo                    YAHOO FINANCE WINDOWS FIX - IMMEDIATE SOLUTION
echo ==============================================================================
echo.
echo This will fix the "Expecting value: line 1 column 1 (char 0)" error
echo.
echo IDENTIFIED ISSUE: curl_cffi doesn't work on Windows Python 3.12.9
echo SOLUTION: Downgrade to yfinance 0.2.18 which doesn't need curl_cffi
echo.
echo ==============================================================================
echo.
pause

echo.
echo Step 1: Removing problematic packages...
echo ------------------------------------------------------------------------------
pip uninstall yfinance curl-cffi curl_cffi -y

echo.
echo Step 2: Installing working version (yfinance 0.2.18)...
echo ------------------------------------------------------------------------------
pip install yfinance==0.2.18

echo.
echo Step 3: Installing other required packages...
echo ------------------------------------------------------------------------------
pip install pandas numpy ta scikit-learn fastapi uvicorn pydantic

echo.
echo Step 4: Quick Test...
echo ------------------------------------------------------------------------------
python -c "import yfinance as yf; t = yf.Ticker('AAPL'); h = t.history(period='5d'); print(f'SUCCESS! AAPL: ${h[\"Close\"].iloc[-1]:.2f}')"

echo.
echo ==============================================================================
echo                                 FIX COMPLETE!
echo ==============================================================================
echo.
echo Yahoo Finance should now work correctly!
echo.
echo To test the ML system:
echo   cd ML_Stock_Windows_Clean
echo   python ml_core_windows.py
echo.
echo The API will be available at: http://localhost:8000
echo.
echo ==============================================================================
pause