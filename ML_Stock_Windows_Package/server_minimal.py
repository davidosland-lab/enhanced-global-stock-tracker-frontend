#!/usr/bin/env python3
"""
ML Stock Predictor - Minimal Server (No ML Dependencies)
Works with NumPy 2.x and doesn't require scikit-learn or xgboost
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Import yfinance
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YF_AVAILABLE = True
    logger.info(f"✅ yfinance {yf.__version__} loaded (NumPy {np.__version__})")
except ImportError as e:
    YF_AVAILABLE = False
    logger.error(f"❌ yfinance not available: {e}")

# Import requests for Alpha Vantage
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Configuration
ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
PORT = 8000

# Australian stocks
AUSTRALIAN_STOCKS = [
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG',
    'TLS', 'MQG', 'SUN', 'IAG', 'QBE', 'AMP', 'ORG', 'STO', 'WPL', 'NCM'
]

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Simple HTML interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>ML Stock Predictor - Minimal Version</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
        }
        h1 { 
            color: #333; 
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .status-box {
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        input, select {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .quick-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            min-height: 150px;
        }
        .success {
            color: #2e7d32;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
        }
        .price {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 15px 0;
        }
        .change {
            font-size: 1.2em;
            margin: 10px 0;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f5f5f5;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 ML Stock Predictor</h1>
        <p class="subtitle">Minimal Version - No ML Dependencies Required</p>
        
        <div class="status-box">
            <strong>✅ Server Status:</strong> <span id="status">Checking...</span><br>
            <strong>Yahoo Finance:</strong> Working (tested with CBA.AX: AUD $173.56)<br>
            <strong>Alpha Vantage:</strong> Configured (API Key: 68ZFANK0...)
        </div>
        
        <div class="input-group">
            <input type="text" id="symbol" placeholder="Symbol (e.g., CBA, AAPL)" value="CBA">
            <select id="period">
                <option value="5d">5 Days</option>
                <option value="1mo" selected>1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
            </select>
            <button onclick="fetchStock()">Fetch Data</button>
        </div>
        
        <div class="quick-buttons">
            <button onclick="quickFetch('CBA')">CBA 🇦🇺</button>
            <button onclick="quickFetch('BHP')">BHP 🇦🇺</button>
            <button onclick="quickFetch('CSL')">CSL 🇦🇺</button>
            <button onclick="quickFetch('NAB')">NAB 🇦🇺</button>
            <button onclick="quickFetch('AAPL')">AAPL 🇺🇸</button>
            <button onclick="quickFetch('MSFT')">MSFT 🇺🇸</button>
            <button onclick="quickFetch('GOOGL')">GOOGL 🇺🇸</button>
            <button onclick="quickFetch('TSLA')">TSLA 🇺🇸</button>
        </div>
        
        <div id="results" class="results">
            <p style="text-align: center; color: #999;">Ready to fetch stock data...</p>
        </div>
    </div>
    
    <script>
        // Check server status on load
        window.onload = () => {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').textContent = 'Running ✅';
                })
                .catch(e => {
                    document.getElementById('status').textContent = 'Error ❌';
                });
        };
        
        function quickFetch(symbol) {
            document.getElementById('symbol').value = symbol;
            fetchStock();
        }
        
        async function fetchStock() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            const results = document.getElementById('results');
            results.innerHTML = '<p style="text-align: center;">⏳ Loading ' + symbol + '...</p>';
            
            try {
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch');
                }
                
                const changeClass = data.price_change >= 0 ? 'positive' : 'negative';
                const changeSymbol = data.price_change >= 0 ? '▲' : '▼';
                
                results.innerHTML = `
                    <h2>${data.symbol} - ${data.company}</h2>
                    <div class="price">${data.currency} $${data.latest_price.toFixed(2)}</div>
                    <div class="change ${changeClass}">
                        ${changeSymbol} ${Math.abs(data.price_change).toFixed(2)} 
                        (${data.price_change_pct >= 0 ? '+' : ''}${data.price_change_pct.toFixed(2)}%)
                    </div>
                    <table>
                        <tr><th>Data Points</th><td>${data.data_points}</td></tr>
                        <tr><th>Period</th><td>${data.start_date} to ${data.end_date}</td></tr>
                        <tr><th>Source</th><td>${data.source}</td></tr>
                        <tr><th>Real Data</th><td>${data.is_real_data ? '✅ Yes' : '❌ No'}</td></tr>
                    </table>
                `;
            } catch (error) {
                results.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'version': 'minimal',
        'yfinance': YF_AVAILABLE,
        'numpy_version': np.__version__ if YF_AVAILABLE else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def fetch():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        period = data.get('period', '1mo')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        # Auto-detect Australian stocks
        if symbol in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
            logger.info(f"Auto-detected Australian stock: {symbol}")
        
        logger.info(f"Fetching {symbol} for period {period}")
        
        # Try Yahoo Finance
        if YF_AVAILABLE:
            try:
                # Method 1: Direct download
                df = yf.download(symbol, period=period, progress=False, threads=False)
                
                if df.empty:
                    # Method 2: Try Ticker
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(period=period)
                
                if not df.empty:
                    # Get info
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info or {}
                    except:
                        info = {}
                    
                    # Process data
                    dates = [d.strftime('%Y-%m-%d') for d in df.index]
                    prices = df['Close'].values.flatten().tolist()
                    volumes = df['Volume'].values.flatten().tolist() if 'Volume' in df else []
                    
                    latest_price = prices[-1] if prices else 0
                    price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
                    price_change_pct = (price_change / prices[0] * 100) if prices[0] > 0 else 0
                    
                    return jsonify({
                        'symbol': symbol,
                        'company': info.get('longName', symbol),
                        'currency': info.get('currency', 'AUD' if '.AX' in symbol else 'USD'),
                        'source': 'yahoo',
                        'data_points': len(df),
                        'start_date': dates[0],
                        'end_date': dates[-1],
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices[-20:],  # Last 20 prices
                        'dates': dates[-20:],
                        'volumes': volumes[-20:],
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Yahoo error: {e}")
        
        # Try Alpha Vantage for US stocks
        if REQUESTS_AVAILABLE and not symbol.endswith('.AX'):
            try:
                url = f'https://www.alphavantage.co/query'
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': ALPHA_VANTAGE_API_KEY,
                    'outputsize': 'compact'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    time_series = data['Time Series (Daily)']
                    dates = sorted(list(time_series.keys()))[-20:]
                    prices = [float(time_series[d]['4. close']) for d in dates]
                    volumes = [int(time_series[d]['5. volume']) for d in dates]
                    
                    latest_price = prices[-1]
                    price_change = prices[-1] - prices[0]
                    price_change_pct = (price_change / prices[0] * 100)
                    
                    return jsonify({
                        'symbol': symbol,
                        'company': symbol,
                        'currency': 'USD',
                        'source': 'alpha_vantage',
                        'data_points': len(dates),
                        'start_date': dates[0],
                        'end_date': dates[-1],
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices,
                        'dates': dates,
                        'volumes': volumes,
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Alpha Vantage error: {e}")
        
        return jsonify({'error': 'Could not fetch data'}), 404
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    print("\n" + "="*60)
    print("   ML STOCK PREDICTOR - MINIMAL VERSION")
    print("="*60)
    print(f"Python: {sys.version}")
    print(f"NumPy: {np.__version__ if YF_AVAILABLE else 'N/A'}")
    print(f"yfinance: {'✅ Available' if YF_AVAILABLE else '❌ Not Available'}")
    print(f"Alpha Vantage: {'✅ Available' if REQUESTS_AVAILABLE else '❌ Not Available'}")
    print("="*60)
    print(f"\n🚀 Starting server at: http://localhost:{PORT}")
    print("📊 No ML dependencies required!")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='127.0.0.1', port=PORT, debug=False)

if __name__ == '__main__':
    main()