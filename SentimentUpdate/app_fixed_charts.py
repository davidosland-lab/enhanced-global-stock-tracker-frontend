#!/usr/bin/env python3
"""
Stock Analysis with Fixed Chart.js Date Adapter
Includes both Yahoo (with delays) and Alpha Vantage support
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
print("STOCK ANALYSIS - FIXED CHARTS VERSION")
print("=" * 60)
print("Features:")
print("✓ Fixed Chart.js date adapter")
print("✓ Yahoo Finance with rate limiting protection")
print("✓ Alpha Vantage as fallback")
print("✓ Australian stocks supported")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
YAHOO_DELAY = 3  # seconds between Yahoo requests
last_yahoo_request = 0

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

def yahoo_delay():
    """Enforce delay between Yahoo requests"""
    global last_yahoo_request
    now = time.time()
    elapsed = now - last_yahoo_request
    if elapsed < YAHOO_DELAY:
        wait = YAHOO_DELAY - elapsed
        print(f"Waiting {wait:.1f}s for rate limit...")
        time.sleep(wait)
    last_yahoo_request = time.time()

def fetch_yahoo(symbol, period="1mo"):
    """Try Yahoo Finance with delays"""
    try:
        import yfinance as yf
        
        # Handle Australian stocks
        original = symbol.upper()
        if original in AUSTRALIAN_STOCKS and not original.endswith('.AX'):
            symbol = f"{original}.AX"
        
        yahoo_delay()
        print(f"Trying Yahoo Finance for {symbol}...")
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if not df.empty:
            print(f"✓ Yahoo Finance: Got {len(df)} days for {symbol}")
            return df, "Yahoo Finance"
            
    except Exception as e:
        print(f"Yahoo Finance error: {e}")
    
    return None, None

def fetch_alpha_vantage(symbol):
    """Try Alpha Vantage"""
    try:
        # Handle Australian stocks
        symbol_base = symbol.upper().replace('.AX', '').replace('.AUS', '')
        if symbol_base in AUSTRALIAN_STOCKS:
            symbols_to_try = [f"{symbol_base}.AUS", symbol_base]
        else:
            symbols_to_try = [symbol]
        
        for test_symbol in symbols_to_try:
            print(f"Trying Alpha Vantage for {test_symbol}...")
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': test_symbol,
                'apikey': ALPHA_VANTAGE_KEY,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                print(f"✓ Alpha Vantage: Got data for {test_symbol}")
                ts = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(ts, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col])
                
                return df, "Alpha Vantage"
            
            time.sleep(0.2)  # Small delay between attempts
            
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
    
    return None, None

def calculate_indicators(df):
    """Calculate technical indicators"""
    if df is None or df.empty:
        return {}
    
    indicators = {}
    
    try:
        # Moving averages
        if len(df) >= 20:
            indicators['SMA_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        if len(df) >= 10:
            indicators['SMA_10'] = float(df['Close'].rolling(10).mean().iloc[-1])
        if len(df) >= 5:
            indicators['SMA_5'] = float(df['Close'].rolling(5).mean().iloc[-1])
        
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['RSI'] = float(rsi.iloc[-1])
        
        # Daily change
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            indicators['Daily_Change'] = float(change)
    
    except Exception as e:
        print(f"Indicator calculation error: {e}")
    
    return indicators

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data from available sources"""
    try:
        period = request.args.get('period', '1mo')
        
        # Try Yahoo first
        df, source = fetch_yahoo(symbol, period)
        
        # Fallback to Alpha Vantage
        if df is None:
            df, source = fetch_alpha_vantage(symbol)
        
        if df is None:
            return jsonify({
                'error': 'Unable to fetch data',
                'symbol': symbol,
                'message': 'Both Yahoo Finance and Alpha Vantage unavailable'
            }), 404
        
        # Calculate indicators
        indicators = calculate_indicators(df)
        
        # Simple predictions
        predictions = []
        if len(df) >= 5:
            current_price = float(df['Close'].iloc[-1])
            trend = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
            daily_trend = trend / 5
            
            for i in range(1, 6):
                pred_price = current_price * (1 + daily_trend * i)
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'predicted_price': round(pred_price, 2)
                })
        
        # Prepare data for chart (limit to last 60 days for performance)
        chart_data = []
        for index, row in df.tail(60).iterrows():
            chart_data.append({
                'x': index.strftime('%Y-%m-%d'),  # Simple date string
                'o': float(row['Open']),
                'h': float(row['High']),
                'l': float(row['Low']),
                'c': float(row['Close'])
            })
        
        return jsonify({
            'symbol': symbol,
            'source': source,
            'current_price': float(df['Close'].iloc[-1]),
            'data': chart_data,
            'indicators': indicators,
            'predictions': predictions
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'symbol': symbol}), 500

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Fixed Charts</title>
    <!-- Chart.js 3.x with all required components -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@2.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.min.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2rem;
        }
        .subtitle {
            color: #718096;
            font-size: 1rem;
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102,126,234,0.4);
        }
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            position: relative;
            height: 500px;
        }
        .info-panel {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .price-display {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 10px;
        }
        .source-info {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e2e8f0;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
            margin-top: 20px;
        }
        .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f7fafc;
            margin-bottom: 8px;
            border-radius: 6px;
        }
        .indicator-label {
            color: #4a5568;
            font-weight: 500;
        }
        .indicator-value {
            color: #2d3748;
            font-weight: 600;
        }
        .prediction-item {
            padding: 10px;
            background: linear-gradient(135deg, #f6f9fc 0%, #f1f5f9 100%);
            margin-bottom: 8px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
        }
        .loading {
            background: #bee3f8;
            color: #2c5282;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .success {
            background: #c6f6d5;
            color: #22543d;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        canvas {
            width: 100% !important;
            height: 100% !important;
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
        <div class="header">
            <h1>📈 Stock Analysis Dashboard</h1>
            <p class="subtitle">Real-time data from Yahoo Finance & Alpha Vantage</p>
        </div>
        
        <div class="controls">
            <input type="text" id="symbol" placeholder="Enter symbol (e.g., AAPL, CBA)" value="AAPL">
            <select id="period">
                <option value="1mo" selected>1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
            </select>
            <button onclick="fetchData()">Get Analysis</button>
        </div>
        
        <div id="status"></div>
        
        <div class="main-grid">
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
            
            <div class="info-panel">
                <div class="price-display" id="currentPrice">--</div>
                <div class="source-info" id="dataSource">Select a stock to begin</div>
                
                <div class="section-title">Technical Indicators</div>
                <div id="indicators"></div>
                
                <div class="section-title">5-Day Predictions</div>
                <div id="predictions"></div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                document.getElementById('status').innerHTML = 
                    '<div class="error">Please enter a stock symbol</div>';
                return;
            }
            
            document.getElementById('status').innerHTML = 
                '<div class="loading">Loading data... (Yahoo Finance with 3-second delay, then Alpha Vantage if needed)</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('status').innerHTML = 
                        `<div class="error">Error: ${data.error}<br>${data.message || ''}</div>`;
                    return;
                }
                
                document.getElementById('status').innerHTML = 
                    `<div class="success">✓ Data loaded from ${data.source}</div>`;
                
                // Update price
                document.getElementById('currentPrice').textContent = 
                    `$${data.current_price.toFixed(2)}`;
                document.getElementById('dataSource').textContent = 
                    `${data.symbol} • ${data.source}`;
                
                // Update chart
                updateChart(data);
                
                // Update indicators
                let indicatorsHtml = '';
                if (data.indicators) {
                    for (const [key, value] of Object.entries(data.indicators)) {
                        indicatorsHtml += `
                            <div class="indicator-item">
                                <span class="indicator-label">${key.replace('_', ' ')}</span>
                                <span class="indicator-value">${
                                    typeof value === 'number' ? value.toFixed(2) : value
                                }</span>
                            </div>
                        `;
                    }
                }
                document.getElementById('indicators').innerHTML = indicatorsHtml || 
                    '<div class="indicator-item">No indicators available</div>';
                
                // Update predictions
                let predictionsHtml = '';
                if (data.predictions && data.predictions.length > 0) {
                    data.predictions.forEach(pred => {
                        predictionsHtml += `
                            <div class="prediction-item">
                                <span>${pred.date}</span>
                                <span style="font-weight: 600;">$${pred.predicted_price}</span>
                            </div>
                        `;
                    });
                }
                document.getElementById('predictions').innerHTML = predictionsHtml || 
                    '<div class="prediction-item">No predictions available</div>';
                
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
                console.error('Fetch error:', error);
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            // Prepare the data
            const chartData = {
                datasets: [{
                    label: data.symbol,
                    data: data.data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                }]
            };
            
            // Create the chart
            chart = new Chart(ctx, {
                type: 'candlestick',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: data.symbol + ' Stock Price',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                parser: 'yyyy-MM-dd',
                                unit: 'day',
                                displayFormats: {
                                    day: 'MMM dd'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
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
        
        // Allow Enter key to submit
        document.getElementById('symbol').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                fetchData();
            }
        });
        
        // Auto-load on page load
        window.onload = function() {
            // Initial load after 1 second
            setTimeout(() => {
                fetchData();
            }, 1000);
        };
    </script>
</body>
</html>
    ''')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    try:
        import yfinance as yf
        print(f"✓ yfinance version {yf.__version__} loaded")
    except:
        print("⚠ yfinance not available, using Alpha Vantage only")
    
    app.run(host='0.0.0.0', port=5000, debug=False)