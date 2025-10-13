@echo off
echo ============================================================
echo    Stock Tracker Complete - Windows 11 Installation
echo    Version 2.0 with ML Integration
echo ============================================================
echo.
echo This will install all required Python packages for the
echo Stock Tracker system including ML integration features.
echo.
echo Prerequisites:
echo - Python 3.8 or higher installed
echo - pip package manager available
echo.
pause

echo.
echo [1/4] Installing core dependencies...
pip install --upgrade pip
pip install fastapi uvicorn yfinance pandas numpy
pip install scikit-learn joblib cachetools pytz
pip install httpx pydantic python-multipart

echo.
echo [2/4] Installing ML dependencies...
pip install tensorflow torch transformers
pip install ta technical plotly matplotlib

echo.
echo [3/4] Installing integration dependencies...
pip install aiofiles websockets requests
pip install sqlite3-api python-dotenv

echo.
echo [4/4] Installing optional enhancements...
pip install streamlit gradio flask
pip install beautifulsoup4 lxml

echo.
echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Run START_SYSTEM.bat to start all services
echo 2. Open http://localhost:8000 in your browser
echo 3. (Optional) Run START_WITH_INTEGRATION.bat for ML features
echo.
pause