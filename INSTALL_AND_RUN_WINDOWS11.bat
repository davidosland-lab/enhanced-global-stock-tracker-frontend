@echo off
echo ============================================================
echo  Stock Tracker Pro - Windows 11 Quick Install and Run
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to CHECK "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [1/4] Python is installed
python --version
echo.

echo [2/4] Installing required packages...
echo This may take a few minutes on first run...
echo.

REM Install minimal required packages
python -m pip install --user --quiet yfinance flask flask-cors

if errorlevel 1 (
    echo.
    echo Warning: Some packages may have failed to install.
    echo Trying alternative installation method...
    pip install --user yfinance flask flask-cors
)

echo.
echo [3/4] Creating minimal backend file...

REM Create a minimal backend Python file
echo import yfinance as yf > backend_minimal.py
echo from flask import Flask, jsonify >> backend_minimal.py
echo from flask_cors import CORS >> backend_minimal.py
echo. >> backend_minimal.py
echo app = Flask(__name__) >> backend_minimal.py
echo CORS(app) >> backend_minimal.py
echo. >> backend_minimal.py
echo @app.route('/') >> backend_minimal.py
echo def home(): >> backend_minimal.py
echo     return jsonify({"status": "active", "message": "Stock Tracker Running"}) >> backend_minimal.py
echo. >> backend_minimal.py
echo @app.route('/api/stock/^<symbol^>') >> backend_minimal.py
echo def get_stock(symbol): >> backend_minimal.py
echo     try: >> backend_minimal.py
echo         ticker = yf.Ticker(symbol) >> backend_minimal.py
echo         info = ticker.info >> backend_minimal.py
echo         return jsonify({"symbol": symbol, "price": info.get('regularMarketPrice', 'N/A'), "name": info.get('longName', 'N/A')}) >> backend_minimal.py
echo     except Exception as e: >> backend_minimal.py
echo         return jsonify({"error": str(e)}) >> backend_minimal.py
echo. >> backend_minimal.py
echo if __name__ == '__main__': >> backend_minimal.py
echo     print("Starting on http://localhost:8002") >> backend_minimal.py
echo     app.run(host='0.0.0.0', port=8002, debug=True) >> backend_minimal.py

echo.
echo [4/4] Starting Stock Tracker Backend...
echo.
echo ============================================================
echo  Server starting on http://localhost:8002
echo  Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the server
python backend_minimal.py

pause