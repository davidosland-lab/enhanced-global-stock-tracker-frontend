@echo off
echo ======================================================================
echo INDICATOR DEBUGGING SCRIPT
echo ======================================================================
echo.
echo This will help diagnose why indicators aren't showing on Windows
echo.

set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

echo Testing indicator calculation directly...
echo.

python -c "import yfinance as yf; import numpy as np; df = yf.download('AAPL', period='1mo', progress=False); prices = df['Close'].tolist(); print(f'Data points: {len(prices)}'); sma = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices); print(f'SMA: ${sma:.2f}')"

echo.
echo If you see values above, the backend is working.
echo.
echo Now check the browser console (F12) when fetching data:
echo 1. Look for "Indicators received:" message
echo 2. Check if indicators object has values
echo 3. Look for any JavaScript errors
echo.
pause