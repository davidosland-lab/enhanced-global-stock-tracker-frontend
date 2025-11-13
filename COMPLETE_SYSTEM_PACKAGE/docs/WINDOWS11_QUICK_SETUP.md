# 🚀 Windows 11 Quick Setup Instructions

## Step 1: Create Project Directory

Open Command Prompt or PowerShell and run:

```cmd
mkdir C:\StockTracker
cd C:\StockTracker
```

## Step 2: Create requirements.txt

Copy and save this as `requirements.txt` in C:\StockTracker:

```txt
flask==2.3.3
flask-cors==4.0.0
werkzeug==2.3.7
fastapi==0.103.1
uvicorn==0.23.2
yfinance==0.2.28
pandas==2.0.3
numpy==1.24.3
python-dateutil==2.8.2
pytz==2023.3
requests==2.31.0
urllib3==2.0.4
certifi==2023.7.22
ta==0.10.2
scikit-learn==1.3.0
scipy==1.11.2
xgboost==1.7.6
joblib==1.3.2
cachetools==5.3.1
ratelimit==2.2.1
waitress==2.1.2
```

## Step 3: Install Dependencies

Now run this command in C:\StockTracker:

```cmd
pip install -r requirements.txt --user
```

Or if that fails, try:

```cmd
python -m pip install -r requirements.txt --user
```

## Step 4: Create a Simple Test Backend

Create a file named `test_backend.py` in C:\StockTracker:

```python
import yfinance as yf
from flask import Flask, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "message": "Stock Tracker Backend Running",
        "version": "7.0"
    })

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return jsonify({
            "symbol": symbol,
            "price": info.get('regularMarketPrice', 'N/A'),
            "name": info.get('longName', 'N/A')
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("Starting Stock Tracker Backend on http://localhost:8002")
    app.run(host='0.0.0.0', port=8002, debug=True)
```

## Step 5: Run the Test Backend

```cmd
python test_backend.py
```

Then open your browser to: http://localhost:8002

## Troubleshooting

### If pip is not recognized:
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### If you get permission errors:
```cmd
python -m pip install --user -r requirements.txt
```

### If Python is not found:
1. Download Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt after installation

### To check Python version:
```cmd
python --version
```
Should show Python 3.8 or higher

## Alternative: Minimal Requirements

If you're having trouble with all packages, start with just these essentials:

```cmd
pip install --user yfinance flask flask-cors
```

This will be enough to get the basic backend running.

## Need the Full Package?

The complete Stock Tracker Pro v7.0 package with all modules is available as:
`StockTracker_Windows11_v7_Clean_Install.zip`

It includes:
- All working modules (Technical Analysis, Market Tracker, ML Predictions)
- Both backend servers
- One-click Windows launcher
- Complete documentation

Let me know if you need help accessing the full package!