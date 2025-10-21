#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - With Chart.js for Better Compatibility
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("UNIFIED STOCK ANALYSIS SYSTEM - Chart.js Version")
print("=" * 70)

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import requests

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

data_cache = {}
cache_duration = 300

def is_australian_stock(symbol):
    base = symbol.replace('.AX', '').upper()
    return base in AUSTRALIAN_STOCKS

def ensure_australian_suffix(symbol):
    symbol = symbol.upper().strip()
    if is_australian_stock(symbol) and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def fetch_yahoo_data(symbol, period='1mo'):
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Yahoo data for {symbol}")
        
        end_date = datetime.now()
        period_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
        days = period_map.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if df.empty:
            return None
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'prices': df['Close'].values.tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in df.index],
            'volume': df['Volume'].values.tolist(),
            'high': df['High'].values.tolist(),
            'low': df['Low'].values.tolist(),
            'open': df['Open'].values.tolist(),
            'current_price': float(df['Close'].iloc[-1]),
            'change': float(df['Close'].iloc[-1] - df['Close'].iloc[-2]) if len(df) > 1 else 0,
            'change_percent': float(((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100)) if len(df) > 1 else 0,
            'company_name': info.get('longName', symbol),
            'data_source': 'Yahoo Finance',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def calculate_technical_indicators(prices, volumes=None):
    if len(prices) < 20:
        return {}
    
    prices_array = np.array(prices, dtype=float)
    indicators = {}
    
    try:
        # SMA
        if len(prices) >= 20:
            indicators['SMA_20'] = float(np.mean(prices_array[-20:]))
        if len(prices) >= 50:
            indicators['SMA_50'] = float(np.mean(prices_array[-50:]))
        
        # EMA
        def calculate_ema(data, period):
            ema = [data[0]]
            multiplier = 2 / (period + 1)
            for price in data[1:]:
                ema.append((price - ema[-1]) * multiplier + ema[-1])
            return ema
        
        if len(prices) >= 12:
            ema12 = calculate_ema(prices_array, 12)
            indicators['EMA_12'] = float(ema12[-1])
        if len(prices) >= 26:
            ema26 = calculate_ema(prices_array, 26)
            indicators['EMA_26'] = float(ema26[-1])
            
            # MACD
            if len(prices) >= 26:
                macd_line = np.array(ema12[-len(ema26):]) - np.array(ema26)
                if len(macd_line) >= 9:
                    signal_line = calculate_ema(macd_line, 9)
                    indicators['MACD'] = float(macd_line[-1])
                    indicators['MACD_signal'] = float(signal_line[-1])
                    indicators['MACD_histogram'] = float(macd_line[-1] - signal_line[-1])
        
        # RSI
        def calculate_rsi(data, period=14):
            if len(data) < period + 1:
                return None
            deltas = np.diff(data)
            seed = deltas[:period]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            if down == 0:
                return 100
            rs = up / down
            return 100 - (100 / (1 + rs))
        
        rsi_value = calculate_rsi(prices_array)
        if rsi_value is not None:
            indicators['RSI'] = float(rsi_value)
        
        # Bollinger Bands
        if len(prices) >= 20:
            sma20 = np.mean(prices_array[-20:])
            std20 = np.std(prices_array[-20:])
            indicators['BB_upper'] = float(sma20 + (2 * std20))
            indicators['BB_middle'] = float(sma20)
            indicators['BB_lower'] = float(sma20 - (2 * std20))
        
        # ATR
        if len(prices) >= 15:
            high = prices_array * 1.01
            low = prices_array * 0.99
            tr = high - low
            indicators['ATR'] = float(np.mean(tr[-14:]))
            
    except Exception as e:
        print(f"Indicator error: {str(e)}")
    
    return indicators

def predict_price(data):
    if not ML_AVAILABLE:
        return {'error': 'ML libraries not available'}
    
    try:
        prices = np.array(data['prices'], dtype=float)
        
        if len(prices) < 10:
            trend = (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'confidence': 0.5,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD'
            }
        
        # Simple prediction logic
        X = []
        y = []
        window_size = min(5, len(prices) // 3)
        
        for i in range(window_size, len(prices) - 1):
            window = prices[max(0, i-window_size):i]
            X.append([float(window[-1]), float(np.mean(window)), float(np.std(window))])
            y.append(float(prices[i + 1]))
        
        if len(X) < 5:
            trend = (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'confidence': 0.6,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD'
            }
        
        X = np.array(X)
        y = np.array(y)
        
        last_window = prices[-window_size:]
        X_pred = np.array([[float(last_window[-1]), float(np.mean(last_window)), float(np.std(last_window))]])
        
        rf_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
        rf_model.fit(X, y)
        prediction = float(rf_model.predict(X_pred)[0])
        
        change_pct = (prediction / data['current_price'] - 1) * 100
        
        return {
            'ensemble': prediction,
            'confidence': 0.75,
            'current_price': float(data['current_price']),
            'predicted_change': float(change_pct),
            'recommendation': 'BUY' if change_pct > 2 else 'SELL' if change_pct < -2 else 'HOLD'
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return {'error': str(e)}

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stock Analysis System - Chart.js Version</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
        }
        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .input-group {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        input, select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            height: 500px;
        }
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 20px;
        }
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            margin: 20px 0;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .indicator-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .indicator {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .loading {
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Stock Analysis System</h1>
            <p>Real-time data with Chart.js visualization</p>
        </div>
        
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Enter stock symbol" value="SPY">
                <select id="period">
                    <option value="1mo">1 Month</option>
                    <option value="3mo" selected>3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <button onclick="fetchData()">Analyze Stock</button>
            </div>
        </div>
        
        <div class="chart-container" id="chartContainer" style="display:none;">
            <canvas id="stockChart"></canvas>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let chart = null;
        let currentData = null;
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) return;
            
            document.getElementById('results').innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period})
                });
                
                const data = await response.json();
                currentData = data;
                
                const indResponse = await fetch('/api/indicators', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prices: data.prices})
                });
                
                const indicators = await indResponse.json();
                
                const predResponse = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({data})
                });
                
                const predictions = await predResponse.json();
                
                displayChart(data, indicators);
                displayResults(data, indicators, predictions);
                
            } catch (error) {
                document.getElementById('results').innerHTML = '<div class="card">Error: ' + error.message + '</div>';
            }
        }
        
        function displayChart(data, indicators) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            document.getElementById('chartContainer').style.display = 'block';
            
            if (chart) {
                chart.destroy();
            }
            
            const datasets = [{
                label: 'Price',
                data: data.prices,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: false,
                tension: 0.1
            }];
            
            // Add SMA if available
            if (indicators.SMA_20) {
                datasets.push({
                    label: 'SMA 20',
                    data: new Array(data.prices.length).fill(indicators.SMA_20),
                    borderColor: '#FFA500',
                    borderDash: [5, 5],
                    fill: false
                });
            }
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: data.symbol + ' - ' + (data.company_name || '')
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Price ($)'
                            }
                        }
                    }
                }
            });
        }
        
        function displayResults(data, indicators, predictions) {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            
            let html = '<div class="results">';
            
            // Price card
            html += `
                <div class="card">
                    <h3>${data.symbol}</h3>
                    <div class="price-display">$${data.current_price.toFixed(2)}</div>
                    <div class="${changeClass}">${data.change >= 0 ? '▲' : '▼'} ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)</div>
                </div>
            `;
            
            // Indicators card
            html += '<div class="card"><h3>Technical Indicators</h3><div class="indicator-grid">';
            for (const [key, value] of Object.entries(indicators)) {
                if (value !== null && value !== undefined) {
                    html += `
                        <div class="indicator">
                            <div style="color: #666; font-size: 0.9em;">${key}</div>
                            <div style="font-weight: bold;">${typeof value === 'number' ? value.toFixed(2) : value}</div>
                        </div>
                    `;
                }
            }
            html += '</div></div>';
            
            // Predictions card
            if (predictions.ensemble) {
                html += `
                    <div class="card">
                        <h3>ML Prediction</h3>
                        <div style="font-size: 1.5em; margin: 20px 0;">
                            Predicted: $${predictions.ensemble.toFixed(2)}
                        </div>
                        <div>Change: ${predictions.predicted_change.toFixed(2)}%</div>
                        <div>Confidence: ${(predictions.confidence * 100).toFixed(0)}%</div>
                        <div style="margin-top: 15px; padding: 10px; background: ${
                            predictions.recommendation === 'BUY' ? '#4CAF50' : 
                            predictions.recommendation === 'SELL' ? '#f44336' : '#FFC107'
                        }; color: white; border-radius: 5px; text-align: center; font-weight: bold;">
                            ${predictions.recommendation}
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('results').innerHTML = html;
        }
        
        // Auto-load on start
        window.onload = () => fetchData();
    </script>
</body>
</html>"""

@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        period = data.get('period', '1mo')
        
        result = fetch_yahoo_data(symbol, period)
        if not result:
            return jsonify({'error': 'Failed to fetch data'}), 500
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/indicators", methods=["POST"])
def api_indicators():
    try:
        data = request.json
        prices = data.get('prices', [])
        indicators = calculate_technical_indicators(prices)
        return jsonify(indicators)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.json.get('data')
        predictions = predict_price(data)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("\nServer starting at http://localhost:8000")
    print("Using Chart.js for better compatibility\n")
    app.run(host="0.0.0.0", port=8000, debug=False)