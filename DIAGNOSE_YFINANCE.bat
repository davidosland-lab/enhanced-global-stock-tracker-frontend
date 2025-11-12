@echo off
:: FinBERT Diagnostic Tool - yfinance Issues
color 0E
cls

echo ============================================================
echo  FINBERT DIAGNOSTIC TOOL - YFINANCE TROUBLESHOOTING
echo ============================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo [TEST 1] Checking yfinance installation...
echo --------------------------------------------------------
python -c "import yfinance as yf; print('yfinance version:', yf.__version__)"
if %errorlevel% neq 0 (
    echo [FAILED] yfinance not installed properly
    echo.
    echo Attempting to reinstall...
    pip uninstall -y yfinance
    pip install yfinance==0.2.40
    echo.
    pause
    exit /b 1
)
echo [OK] yfinance is installed
echo.

echo [TEST 2] Testing direct Yahoo Finance connection...
echo --------------------------------------------------------
python -c "import requests; r = requests.get('https://finance.yahoo.com', timeout=10); print('Status:', r.status_code)"
if %errorlevel% neq 0 (
    echo [FAILED] Cannot reach Yahoo Finance
    echo.
    echo Possible causes:
    echo   - Firewall blocking access
    echo   - Proxy/VPN interfering
    echo   - Yahoo Finance temporarily down
    echo.
    pause
    exit /b 1
)
echo [OK] Can reach Yahoo Finance
echo.

echo [TEST 3] Testing simple stock fetch...
echo --------------------------------------------------------
python << EOF
import yfinance as yf
import sys

print("Attempting to fetch AAPL (simple US stock)...")
try:
    ticker = yf.Ticker("AAPL")
    info = ticker.fast_info
    print(f"  Last Price: ${info.last_price:.2f}")
    print("  [OK] Basic stock fetch works")
except Exception as e:
    print(f"  [FAILED] {str(e)}")
    sys.exit(1)
EOF

if %errorlevel% neq 0 (
    echo.
    echo [FAILED] Cannot fetch stock data
    echo.
    echo Try upgrading yfinance:
    echo   pip install --upgrade yfinance
    echo.
    pause
    exit /b 1
)
echo.

echo [TEST 4] Testing ASX stock fetch...
echo --------------------------------------------------------
python << EOF
import yfinance as yf
import sys

print("Attempting to fetch CBA.AX (ASX stock)...")
try:
    ticker = yf.Ticker("CBA.AX")
    hist = ticker.history(period="5d")
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        print(f"  Last Price: ${price:.2f}")
        print("  [OK] ASX stock fetch works")
    else:
        print("  [FAILED] No data returned")
        sys.exit(1)
except Exception as e:
    print(f"  [FAILED] {str(e)}")
    sys.exit(1)
EOF

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] ASX stocks may not be accessible
    echo This could be normal during weekends or holidays
    echo.
)
echo.

echo [TEST 5] Testing market indices...
echo --------------------------------------------------------
python << EOF
import yfinance as yf
import sys

indices = {
    "^AXJO": "ASX 200",
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "^DJI": "Dow Jones"
}

failed = []
for symbol, name in indices.items():
    print(f"Testing {name} ({symbol})...")
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            print(f"  [OK] {name}: {price:.2f}")
        else:
            print(f"  [FAILED] No data for {name}")
            failed.append(name)
    except Exception as e:
        print(f"  [FAILED] {name}: {str(e)[:60]}")
        failed.append(name)
    print()

if failed:
    print(f"Failed indices: {', '.join(failed)}")
    print()
    print("This is the exact error you're seeing!")
    print()
    print("SOLUTIONS:")
    print("  1. Upgrade yfinance: pip install --upgrade yfinance")
    print("  2. Check if markets are open (indices only update during trading hours)")
    print("  3. Try with a VPN if Yahoo Finance is blocked in your region")
    print("  4. Use Alpha Vantage fallback (automatic in the system)")
    sys.exit(1)
else:
    print("  [OK] All indices accessible")
EOF

echo.
echo ============================================================
echo  DIAGNOSTIC COMPLETE
echo ============================================================
echo.

if %errorlevel% equ 0 (
    echo [SUCCESS] All tests passed!
    echo.
    echo Your system should work fine. If you're still seeing errors:
    echo   1. Markets may be closed (weekend/holiday)
    echo   2. Run screener during market hours
    echo   3. Check logs in logs\screening\ for details
) else (
    echo [ISSUES DETECTED] See recommendations above
    echo.
    echo Common fixes:
    echo   1. pip install --upgrade yfinance
    echo   2. pip install --upgrade requests
    echo   3. Check your firewall/antivirus settings
    echo   4. Try running during market hours
)

echo.
pause
