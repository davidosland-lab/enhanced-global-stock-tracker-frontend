#!/usr/bin/env python3
"""
Stock Analysis - Final Working Version
No date parsing issues, simple and reliable
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import warnings
import requests

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS - FINAL WORKING VERSION")
print("=" * 60)
print("Features:")
print("✓ Simple line/candlestick charts (no date issues)")
print("✓ Yahoo Finance with delays")
print("✓ Alpha Vantage fallback")
print("✓ Australian stocks")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Config
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
YAHOO_DELAY = 3
last_yahoo_request = 0

AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

def yahoo_delay():
    """Rate limit protection"""
    global last_yahoo_request
    now = time.time()
    elapsed = now - last_yahoo_request
    if elapsed < YAHOO_DELAY:
        time.sleep(YAHOO_DELAY - elapsed)
    last_yahoo_request = time.time()

def fetch_data(symbol, period="1mo"):
    """Fetch from Yahoo or Alpha Vantage"""
    
    # Try Yahoo first
    try:
        import yfinance as yf
        
        # Handle Australian stocks
        original = symbol.upper()
        if original in AUSTRALIAN_STOCKS and not original.endswith('.AX'):
            symbol = f"{original}.AX"
        
        yahoo_delay()
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if not df.empty:
            return df, "Yahoo Finance"
    except Exception as e:
        print(f"Yahoo error: {e}")
    
    # Try Alpha Vantage
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            ts = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(ts, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            return df, "Alpha Vantage"
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
    
    return None, None

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data"""
    try:
        period = request.args.get('period', '1mo')
        
        df, source = fetch_data(symbol, period)
        
        if df is None:
            return jsonify({
                'error': 'Unable to fetch data',
                'symbol': symbol
            }), 404
        
        # Prepare simple data (no complex date parsing)
        # Use index numbers instead of dates for x-axis
        chart_data = []
        labels = []
        
        for i, (index, row) in enumerate(df.tail(60).iterrows()):
            chart_data.append({
                'x': i,  # Simple index number
                'y': float(row['Close']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close'])
            })
            # Simple date label
            labels.append(index.strftime('%m/%d'))
        
        # Calculate indicators
        indicators = {}
        if len(df) >= 20:
            indicators['SMA_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['RSI'] = float(rsi.iloc[-1])
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            indicators['Change_%'] = float(change)
        
        return jsonify({
            'symbol': symbol,
            'source': source,
            'current_price': float(df['Close'].iloc[-1]),
            'data': chart_data,
            'labels': labels,
            'indicators': indicators
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        .controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 10px 15px;
            border-radius: 6px;
            border: 2px solid #e2e8f0;
            font-size: 14px;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover {
            opacity: 0.9;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container {
            position: relative;
            height: 400px;
        }
        .price {
            font-size: 2rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 10px;
        }
        .source {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        .indicator {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: #f7fafc;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        .loading {
            background: #bee3f8;
            color: #2c5282;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 12px;
            border-radius: 6px;
        }
        .success {
            background: #c6f6d5;
            color: #22543d;
            padding: 12px;
            border-radius: 6px;
        }
        .chart-type {
            display: flex;
            gap: 10px;
            margin-left: auto;
        }
        .chart-btn {
            padding: 6px 12px;
            background: #e2e8f0;
            color: #2d3748;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .chart-btn.active {
            background: #667eea;
            color: white;
        }
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📈 Stock Analysis Dashboard</h1>
            <p style="color: #718096; margin-bottom: 20px;">Real market data • No synthetic data</p>
            
            <div class="controls">
                <input type="text" id="symbol" placeholder="Symbol (e.g., AAPL, CBA)" value="AAPL">
                <select id="period">
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <button onclick="fetchData()">Get Data</button>
                
                <div class="chart-type">
                    <button class="chart-btn active" onclick="setChartType('line')">Line</button>
                    <button class="chart-btn" onclick="setChartType('candlestick')">Candlestick</button>
                </div>
            </div>
        </div>
        
        <div id="status"></div>
        
        <div class="main-grid">
            <div class="card">
                <div class="chart-container">
                    <canvas id="chart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <div class="price" id="price">--</div>
                <div class="source" id="source">Select a stock</div>
                
                <h3 style="margin-bottom: 10px;">Indicators</h3>
                <div id="indicators"></div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        let currentData = null;
        let chartType = 'line';
        
        function setChartType(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            if (currentData) {
                updateChart(currentData);
            }
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) return;
            
            document.getElementById('status').innerHTML = 
                '<div class="card loading">Loading... (Yahoo Finance → Alpha Vantage fallback)</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('status').innerHTML = 
                        `<div class="card error">Error: ${data.error}</div>`;
                    return;
                }
                
                currentData = data;
                
                document.getElementById('status').innerHTML = 
                    `<div class="card success">✓ Data loaded from ${data.source}</div>`;
                
                // Update info
                document.getElementById('price').textContent = '$' + data.current_price.toFixed(2);
                document.getElementById('source').textContent = data.symbol + ' • ' + data.source;
                
                // Update indicators
                let html = '';
                for (const [key, value] of Object.entries(data.indicators || {})) {
                    html += `
                        <div class="indicator">
                            <span>${key}</span>
                            <strong>${value.toFixed(2)}</strong>
                        </div>
                    `;
                }
                document.getElementById('indicators').innerHTML = html || 
                    '<div class="indicator">No indicators</div>';
                
                // Update chart
                updateChart(data);
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('status').innerHTML = 
                    `<div class="card error">Error: ${error.message}</div>`;
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            if (chartType === 'line') {
                // Simple line chart
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: data.symbol,
                            data: data.data.map(d => d.y),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            borderWidth: 2,
                            tension: 0.1,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            title: {
                                display: true,
                                text: data.symbol + ' Price Chart'
                            }
                        },
                        scales: {
                            y: {
                                title: {
                                    display: true,
                                    text: 'Price ($)'
                                }
                            }
                        }
                    }
                });
            } else {
                // Candlestick chart
                chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'High-Low',
                            data: data.data.map((d, i) => [d.low, d.high]),
                            backgroundColor: 'rgba(0,0,0,0.1)',
                            borderColor: 'rgba(0,0,0,0.3)',
                            borderWidth: 1,
                            barThickness: 2
                        }, {
                            label: 'Open-Close',
                            data: data.data.map((d, i) => {
                                const isGreen = d.close >= d.open;
                                return [
                                    Math.min(d.open, d.close),
                                    Math.max(d.open, d.close)
                                ];
                            }),
                            backgroundColor: data.data.map(d => 
                                d.close >= d.open ? 'rgba(0,255,0,0.5)' : 'rgba(255,0,0,0.5)'
                            ),
                            borderColor: data.data.map(d => 
                                d.close >= d.open ? 'green' : 'red'
                            ),
                            borderWidth: 1,
                            barThickness: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            title: {
                                display: true,
                                text: data.symbol + ' Candlestick Chart'
                            }
                        },
                        scales: {
                            y: {
                                title: {
                                    display: true,
                                    text: 'Price ($)'
                                }
                            }
                        }
                    }
                });
            }
        }
        
        // Auto-load
        setTimeout(() => fetchData(), 500);
        
        // Enter key
        document.getElementById('symbol').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') fetchData();
        });
    </script>
</body>
</html>
    ''')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)