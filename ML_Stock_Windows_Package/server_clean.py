#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Server - No encoding issues
Works on Windows 11 with proper encoding handling
"""

import sys
import os

# Set default encoding for Windows
if sys.platform == 'win32':
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

print("Starting clean server...")
print(f"Python: {sys.version}")
print(f"Encoding: {sys.getdefaultencoding()}")

from flask import Flask, jsonify, request
from flask_cors import CORS

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Australian stocks list
AUSTRALIAN_STOCKS = [
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG'
]

# HTML interface as string (no file reading to avoid encoding issues)
HTML_INTERFACE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ML Stock Predictor - Clean Version</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
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
        }
        .status {
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
        }
        button:hover {
            transform: translateY(-2px);
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            min-height: 150px;
        }
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 15px 0;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ML Stock Predictor - Clean Server</h1>
        <p>No encoding issues version</p>
        
        <div class="status">
            <strong>Server Status:</strong> <span id="status">Checking...</span>
        </div>
        
        <div class="input-group">
            <input type="text" id="symbol" placeholder="Enter symbol (e.g., CBA, AAPL)" value="AAPL">
            <select id="period">
                <option value="1mo" selected>1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
            </select>
            <button onclick="fetchStock()">Fetch Data</button>
        </div>
        
        <div id="results" class="results">
            <p style="text-align: center; color: #999;">Enter a symbol and click Fetch Data</p>
        </div>
    </div>
    
    <script>
        window.onload = function() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').textContent = 'Running';
                    document.getElementById('status').style.color = '#4CAF50';
                })
                .catch(e => {
                    document.getElementById('status').textContent = 'Error';
                    document.getElementById('status').style.color = '#f44336';
                });
        };
        
        async function fetchStock() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            const results = document.getElementById('results');
            results.innerHTML = '<p>Loading ' + symbol + '...</p>';
            
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
                const changeSymbol = data.price_change >= 0 ? '+' : '';
                
                results.innerHTML = 
                    '<h2>' + data.symbol + ' - ' + data.company + '</h2>' +
                    '<div class="price-display">' + data.currency + ' $' + data.latest_price.toFixed(2) + '</div>' +
                    '<div class="' + changeClass + '" style="font-size: 1.2em;">' +
                    changeSymbol + data.price_change.toFixed(2) + ' (' + changeSymbol + data.price_change_pct.toFixed(2) + '%)' +
                    '</div>' +
                    '<p>Data Points: ' + data.data_points + '</p>' +
                    '<p>Period: ' + data.start_date + ' to ' + data.end_date + '</p>' +
                    '<p>Source: ' + data.source + '</p>';
                    
            } catch (error) {
                results.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_INTERFACE

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'encoding': sys.getdefaultencoding()
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def api_fetch():
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
        
        print(f"Fetching {symbol} for period {period}")
        
        # Try to fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            # Try download method
            df = yf.download(symbol, period=period, progress=False, threads=False, auto_adjust=True)
        
        if df.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Get info
        try:
            info = ticker.info or {}
        except:
            info = {}
        
        # Process data
        dates = [d.strftime('%Y-%m-%d') for d in df.index]
        prices = df['Close'].values.flatten().tolist()
        
        latest_price = prices[-1] if prices else 0
        price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
        price_change_pct = (price_change / prices[0] * 100) if prices[0] > 0 else 0
        
        return jsonify({
            'symbol': symbol,
            'company': info.get('longName', symbol),
            'currency': info.get('currency', 'AUD' if '.AX' in symbol else 'USD'),
            'source': 'yahoo',
            'data_points': len(df),
            'start_date': dates[0] if dates else '',
            'end_date': dates[-1] if dates else '',
            'latest_price': float(latest_price),
            'price_change': float(price_change),
            'price_change_pct': float(price_change_pct),
            'prices': prices[-20:],
            'dates': dates[-20:]
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ML STOCK PREDICTOR - CLEAN SERVER")
    print("="*60)
    print("No encoding issues version")
    print(f"Starting server at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        app.run(host='127.0.0.1', port=8000, debug=False)
    except Exception as e:
        print(f"\nServer error: {e}")
        input("\nPress Enter to exit...")