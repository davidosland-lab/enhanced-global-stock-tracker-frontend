@echo off
echo ====================================
echo Stock Tracker v8.2 ENHANCED
echo With CBA Document/News Analysis
echo ====================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install --quiet flask flask-cors yfinance pandas numpy scikit-learn beautifulsoup4 requests cachetools aiohttp

echo [2/3] Starting enhanced backend...
start /min cmd /c "python backend.py"

echo [3/3] Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:8002

echo.
echo ====================================
echo Stock Tracker ENHANCED is running!
echo.
echo FEATURES:
echo - CBA Enhanced Analysis
echo - Candlestick Charts
echo - News Sentiment Analysis
echo - Document Import & Analysis
echo - ML Predictions
echo ====================================
pause