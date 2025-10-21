@echo off
cls
echo ==============================================================================
echo                         EMERGENCY YAHOO FINANCE FIX
echo ==============================================================================
echo.
echo The server is running but Yahoo Finance data fetching is failing.
echo This script will apply multiple fixes to resolve the issue.
echo.
pause

echo.
echo STEP 1: Completely removing ALL yfinance versions...
echo ------------------------------------------------------------------------------
pip uninstall yfinance -y
pip uninstall yfinance -y
pip uninstall curl-cffi -y
pip uninstall curl_cffi -y

echo.
echo STEP 2: Clearing pip cache...
echo ------------------------------------------------------------------------------
pip cache purge

echo.
echo STEP 3: Installing specific working version...
echo ------------------------------------------------------------------------------
pip install yfinance==0.2.18 --no-cache-dir

echo.
echo STEP 4: Installing required dependencies...
echo ------------------------------------------------------------------------------
pip install pandas numpy requests urllib3 certifi --upgrade

echo.
echo STEP 5: Testing Yahoo Finance directly...
echo ------------------------------------------------------------------------------
python -c "import yfinance as yf; print(f'yfinance version: {yf.__version__}')"

echo.
echo Testing data fetch...
python -c "import warnings; warnings.filterwarnings('ignore'); import yfinance as yf; data = yf.download('MSFT', period='5d', progress=False, threads=False); print(f'Success! Got {len(data)} days of MSFT data'); print(f'Latest close: ${data[\"Close\"].iloc[-1]:.2f}')" 2>nul

if errorlevel 1 (
    echo.
    echo ------------------------------------------------------------------------------
    echo STILL HAVING ISSUES - Trying alternative fix...
    echo ------------------------------------------------------------------------------
    
    echo.
    echo Installing older stable version...
    pip uninstall yfinance -y
    pip install yfinance==0.1.74 --no-cache-dir
    
    echo.
    echo Testing with older version...
    python -c "import yfinance as yf; data = yf.download('AAPL', period='5d', progress=False); print(f'Version 0.1.74 works! Got {len(data)} days')" 2>nul
    
    if errorlevel 1 (
        echo.
        echo ------------------------------------------------------------------------------
        echo NETWORK ISSUE DETECTED
        echo ------------------------------------------------------------------------------
        echo.
        echo Yahoo Finance might be blocking your connection.
        echo.
        echo Try these solutions:
        echo 1. Disable VPN if you're using one
        echo 2. Check Windows Firewall settings
        echo 3. Try running as Administrator
        echo 4. Check if you're behind a corporate proxy
        echo.
        echo Testing direct web access to Yahoo...
        curl -s -o nul -w "HTTP Status: %%{http_code}\n" https://finance.yahoo.com
        
        echo.
        echo Alternative: Install yfinance with requests fallback...
        pip install yfinance==0.2.18 requests-cache --no-cache-dir
    )
) else (
    echo.
    echo ==============================================================================
    echo SUCCESS! Yahoo Finance is now working!
    echo ==============================================================================
    echo.
    echo You can now restart the server and it should work.
    echo.
)

echo.
pause