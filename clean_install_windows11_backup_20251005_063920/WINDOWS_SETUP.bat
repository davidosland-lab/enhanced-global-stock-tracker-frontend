@echo off
echo ============================================
echo   Complete Stock Tracker - Windows Setup
echo ============================================
echo.

echo [1/4] Installing core dependencies...
pip install Flask flask-cors fastapi uvicorn --user

echo.
echo [2/4] Installing data packages...
pip install yfinance pandas numpy pytz cachetools requests aiohttp python-dotenv pydantic colorama --user

echo.
echo [3/4] Installing optional packages (may skip if errors)...
pip install scikit-learn xgboost lightgbm ta textblob vaderSentiment PyPDF2 openpyxl python-docx --user 2>nul

echo.
echo [4/4] Installing pandas-ta (latest version)...
pip install pandas-ta --user 2>nul

echo.
echo ============================================
echo   Setup Complete!
echo   Run: python backend.py
echo   Then open: http://localhost:8002
echo ============================================
echo.
pause