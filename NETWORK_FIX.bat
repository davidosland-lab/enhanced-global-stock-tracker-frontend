@echo off
cls
echo ==============================================================================
echo                    YAHOO FINANCE NETWORK CONNECTION FIX
echo ==============================================================================
echo.
echo Yahoo Finance is blocking ALL requests - even for AAPL and MSFT!
echo This indicates a network/connection issue, not a code problem.
echo.
pause

echo.
echo STEP 1: Checking System Date/Time
echo ------------------------------------------------------------------------------
echo Current system time:
date /t
time /t
echo.
echo If the date is wrong, Yahoo Finance will reject requests!
echo Make sure your system date and time are correct.
echo.

echo STEP 2: Testing Direct Internet Connection
echo ------------------------------------------------------------------------------
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo ERROR: No internet connection!
) else (
    echo OK: Internet connection is working
)

echo.
echo STEP 3: Testing Connection to Yahoo Finance
echo ------------------------------------------------------------------------------
curl -I https://finance.yahoo.com 2>nul | findstr "HTTP"
if errorlevel 1 (
    echo Cannot reach Yahoo Finance directly
    echo Trying with PowerShell...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://finance.yahoo.com' -UseBasicParsing -Method Head; Write-Host 'Yahoo Finance is reachable - Status:' $response.StatusCode } catch { Write-Host 'ERROR: Cannot reach Yahoo Finance -' $_.Exception.Message }"
) else (
    echo Yahoo Finance website is reachable
)

echo.
echo STEP 4: Checking for VPN/Proxy
echo ------------------------------------------------------------------------------
echo Checking proxy settings...
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" | findstr "ProxyEnable ProxyServer"

set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

echo.
echo Proxy environment variables cleared.

echo.
echo STEP 5: Testing with Different User Agent
echo ------------------------------------------------------------------------------
echo Testing Yahoo Finance API with browser user agent...

echo import yfinance as yf > test_yahoo_network.py
echo import requests >> test_yahoo_network.py
echo. >> test_yahoo_network.py
echo # Test 1: Direct URL test >> test_yahoo_network.py
echo print("Test 1: Checking if we can reach Yahoo Finance...") >> test_yahoo_network.py
echo try: >> test_yahoo_network.py
echo     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'} >> test_yahoo_network.py
echo     response = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/AAPL', headers=headers, timeout=10) >> test_yahoo_network.py
echo     print(f"  Response status: {response.status_code}") >> test_yahoo_network.py
echo     if response.status_code == 200: >> test_yahoo_network.py
echo         print("  ✓ Can reach Yahoo Finance API") >> test_yahoo_network.py
echo     else: >> test_yahoo_network.py
echo         print(f"  ✗ Yahoo returned status {response.status_code}") >> test_yahoo_network.py
echo except Exception as e: >> test_yahoo_network.py
echo     print(f"  ✗ Cannot reach Yahoo Finance: {e}") >> test_yahoo_network.py
echo. >> test_yahoo_network.py
echo # Test 2: Try with different method >> test_yahoo_network.py
echo print("\nTest 2: Trying alternative download method...") >> test_yahoo_network.py
echo import warnings >> test_yahoo_network.py
echo warnings.filterwarnings('ignore') >> test_yahoo_network.py
echo. >> test_yahoo_network.py
echo # Clear any cached data >> test_yahoo_network.py
echo import os >> test_yahoo_network.py
echo cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'py-yfinance') >> test_yahoo_network.py
echo if os.path.exists(cache_dir): >> test_yahoo_network.py
echo     import shutil >> test_yahoo_network.py
echo     shutil.rmtree(cache_dir, ignore_errors=True) >> test_yahoo_network.py
echo     print("  Cleared yfinance cache") >> test_yahoo_network.py
echo. >> test_yahoo_network.py
echo # Try download with explicit parameters >> test_yahoo_network.py
echo try: >> test_yahoo_network.py
echo     data = yf.download('AAPL', start='2024-01-01', end='2024-12-31', progress=False, threads=False) >> test_yahoo_network.py
echo     if not data.empty: >> test_yahoo_network.py
echo         print(f"  ✓ SUCCESS! Got {len(data)} days of AAPL data") >> test_yahoo_network.py
echo         print(f"  Latest price: ${data['Close'].iloc[-1]:.2f}") >> test_yahoo_network.py
echo     else: >> test_yahoo_network.py
echo         print("  ✗ Download returned empty") >> test_yahoo_network.py
echo except Exception as e: >> test_yahoo_network.py
echo     print(f"  ✗ Failed: {e}") >> test_yahoo_network.py

python test_yahoo_network.py

echo.
echo STEP 6: Alternative Solution - Using Different yfinance Version
echo ------------------------------------------------------------------------------
echo.
echo If all tests above failed, Yahoo might be blocking yfinance 0.2.18
echo Let's try the latest version that might have better anti-blocking measures:
echo.

choice /C YN /M "Do you want to try upgrading to latest yfinance (may need curl_cffi)?"
if errorlevel 2 goto :skip_upgrade
if errorlevel 1 goto :do_upgrade

:do_upgrade
echo.
echo Installing latest yfinance...
pip uninstall yfinance -y >nul 2>&1
pip install yfinance --upgrade
echo.
echo Testing latest version...
python -c "import yfinance as yf; print(f'Installed version: {yf.__version__}'); d = yf.download('AAPL', period='5d', progress=False); print(f'Success! Got {len(d)} days') if not d.empty else print('Failed')"
goto :end_upgrade

:skip_upgrade
echo Skipping upgrade.

:end_upgrade

echo.
echo ==============================================================================
echo DIAGNOSIS COMPLETE
echo ==============================================================================
echo.
echo If Yahoo Finance is still not working, try these solutions:
echo.
echo 1. RESTART YOUR ROUTER/MODEM (Yahoo may have temporarily blocked your IP)
echo.
echo 2. USE A VPN (if not using one) or DISABLE VPN (if using one)
echo.
echo 3. FLUSH DNS CACHE:
echo    Run as Administrator: ipconfig /flushdns
echo.
echo 4. CHANGE DNS SERVERS to Google DNS:
echo    - Go to Network Settings
echo    - Set DNS to: 8.8.8.8 and 8.8.4.4
echo.
echo 5. DISABLE WINDOWS FIREWALL temporarily to test
echo.
echo 6. WAIT 1 HOUR (Yahoo rate limiting may reset)
echo.
echo 7. Try from a DIFFERENT NETWORK (mobile hotspot, etc.)
echo.
echo ==============================================================================
pause

del test_yahoo_network.py 2>nul