@echo off
echo ============================================================
echo  Stock Tracker Pro - Windows 11 Complete Setup
echo  Version 7.0 - One-Click Solution
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to CHECK "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python is installed:
python --version
echo.

echo Starting Stock Tracker Pro...
echo This will:
echo  1. Install required packages automatically
echo  2. Start both backend servers
echo  3. Open your browser to the dashboard
echo.
echo Please wait, this may take a minute on first run...
echo.

REM Run the complete setup Python script
python COMPLETE_WINDOWS_SETUP.py

REM If the Python script doesn't exist, create it inline
if errorlevel 1 (
    echo.
    echo Creating setup file...
    
    REM Create a minimal version inline
    echo import subprocess, sys, os > quick_setup.py
    echo print("Installing packages...") >> quick_setup.py
    echo subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "flask", "flask-cors", "yfinance"]) >> quick_setup.py
    echo print("Packages installed!") >> quick_setup.py
    echo. >> quick_setup.py
    echo from flask import Flask, jsonify >> quick_setup.py
    echo from flask_cors import CORS >> quick_setup.py
    echo import yfinance as yf >> quick_setup.py
    echo. >> quick_setup.py
    echo app = Flask(__name__) >> quick_setup.py
    echo CORS(app) >> quick_setup.py
    echo. >> quick_setup.py
    echo @app.route('/') >> quick_setup.py
    echo def home(): >> quick_setup.py
    echo     return """^<h1^>Stock Tracker Running!^</h1^>^<p^>Try: ^<a href="/api/stock/AAPL"^>/api/stock/AAPL^</a^>^</p^>""" >> quick_setup.py
    echo. >> quick_setup.py
    echo @app.route('/api/stock/^<symbol^>') >> quick_setup.py
    echo def get_stock(symbol): >> quick_setup.py
    echo     ticker = yf.Ticker(symbol) >> quick_setup.py
    echo     info = ticker.info >> quick_setup.py
    echo     return jsonify({'symbol': symbol, 'price': info.get('regularMarketPrice', 'N/A')}) >> quick_setup.py
    echo. >> quick_setup.py
    echo print("Server starting on http://localhost:8002") >> quick_setup.py
    echo app.run(host='0.0.0.0', port=8002) >> quick_setup.py
    
    echo.
    echo Running quick setup...
    python quick_setup.py
)

pause