#!/usr/bin/env python3
"""
Stock Analysis with Slow Yahoo Finance Requests
Avoids rate limiting by adding significant delays
"""

import os
import sys
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import warnings

warnings.filterwarnings('ignore')

os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS - YAHOO FINANCE WITH DELAYS")
print("=" * 60)
print("Using 3-second delays to avoid rate limiting")
print("This will be slower but should work")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Track last request time
last_yahoo_request = 0
REQUEST_DELAY = 3  # 3 seconds between Yahoo requests

def yahoo_delay():
    """Ensure minimum delay between Yahoo requests"""
    global last_yahoo_request
    now = time.time()
    elapsed = now - last_yahoo_request
    if elapsed < REQUEST_DELAY:
        wait_time = REQUEST_DELAY - elapsed
        print(f"Waiting {wait_time:.1f}s to avoid rate limit...")
        time.sleep(wait_time)
    last_yahoo_request = time.time()

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

class SlowYahooFetcher:
    """Yahoo Finance with aggressive rate limiting protection"""
    
    def fetch_data(self, symbol, period="1mo"):
        """Fetch with long delays"""
        
        # Handle Australian stocks
        original = symbol.upper()
        if original in AUSTRALIAN_STOCKS and not original.endswith('.AX'):
            symbol = f"{original}.AX"
            print(f"Australian stock detected: {original} -> {symbol}")
        
        # Wait before request
        yahoo_delay()
        
        try:
            print(f"Fetching {symbol} from Yahoo Finance...")
            ticker = yf.Ticker(symbol)
            
            # Try to get history with delay
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"No data returned for {symbol}")
                # Try without .AX if it was Australian
                if symbol.endswith('.AX'):
                    yahoo_delay()
                    symbol = original
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period)
                    
            if not hist.empty:
                print(f"✓ Got {len(hist)} days of data for {symbol}")
                current_price = float(hist['Close'].iloc[-1])
                
                # Try to get info (might fail due to rate limit)
                info = {}
                try:
                    yahoo_delay()
                    info = ticker.info
                except:
                    print("Info endpoint blocked, using history data only")
                
                return hist, current_price, info
            
        except Exception as e:
            print(f"Yahoo error: {e}")
            
        return None, None, {}
    
class SimpleAnalysis:
    """Basic technical analysis"""
    
    def calculate(self, df):
        if df is None or df.empty:
            return {}
            
        indicators = {}
        
        # Basic indicators
        if len(df) >= 20:
            indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        if len(df) >= 10:
            indicators['sma_10'] = float(df['Close'].rolling(10).mean().iloc[-1])
        if len(df) >= 5:
            indicators['sma_5'] = float(df['Close'].rolling(5).mean().iloc[-1])
            
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = float(rsi.iloc[-1])
        
        # Daily change
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            indicators['daily_change'] = float(change)
            
        return indicators

# Global instances
fetcher = SlowYahooFetcher()
analyzer = SimpleAnalysis()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with delays"""
    try:
        period = request.args.get('period', '1mo')
        
        # Fetch with delays
        df, current_price, info = fetcher.fetch_data(symbol, period)
        
        if df is None:
            # If Yahoo fails, suggest Alpha Vantage
            return jsonify({
                'error': 'Yahoo Finance blocked or unavailable',
                'symbol': symbol,
                'suggestion': 'Try Alpha Vantage version instead',
                'message': 'Run: python app_alphavantage_primary.py'
            }), 404
        
        # Calculate indicators
        indicators = analyzer.calculate(df)
        
        # Simple predictions
        predictions = []
        if len(df) >= 5:
            trend = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
            daily_trend = trend / 5
            
            for i in range(1, 6):
                pred_price = current_price * (1 + daily_trend * i)
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'predicted_price': round(pred_price, 2),
                    'trend': 'Bullish' if daily_trend > 0 else 'Bearish'
                })
        
        # Prepare data
        candlestick_data = []
        for index, row in df.iterrows():
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return jsonify({
            'symbol': symbol,
            'source': 'Yahoo Finance (with delays)',
            'current_price': current_price,
            'data': candlestick_data,
            'indicators': indicators,
            'predictions': predictions,
            'info': info if info else {}
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

@app.route('/api/test')
def test_yahoo():
    """Test Yahoo connection"""
    yahoo_delay()
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        if not hist.empty:
            return jsonify({
                'status': 'Yahoo Finance is working',
                'price': float(hist['Close'].iloc[-1]),
                'delay': f'{REQUEST_DELAY} seconds between requests'
            })
    except Exception as e:
        return jsonify({
            'status': 'Yahoo Finance blocked',
            'error': str(e),
            'suggestion': 'Use Alpha Vantage version'
        }), 503

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Yahoo with Delays</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
        }
        h1 { color: #333; }
        .warning {
            background: #fef3c7;
            color: #92400e;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .controls {
            display: flex;
            gap: 15px;
            margin: 20px 0;
        }
        input, button {
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
        }
        .loading {
            background: #dbeafe;
            color: #1e40af;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .chart-container {
            height: 400px;
            margin-top: 20px;
        }
        .info {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Stock Analysis - Yahoo Finance with Rate Limit Protection</h1>
        
        <div class="warning">
            ⚠️ Using 3-second delays between requests to avoid rate limiting.
            Requests will be slower but should work. For faster service, use Alpha Vantage version.
        </div>
        
        <div class="controls">
            <input type="text" id="symbol" placeholder="Stock symbol (e.g., AAPL, CBA)" value="AAPL">
            <button onclick="testConnection()">Test Yahoo</button>
            <button onclick="fetchData()">Get Data (Slow)</button>
        </div>
        
        <div id="status"></div>
        
        <div class="info">
            <div class="chart-container">
                <canvas id="chart"></canvas>
            </div>
            <div>
                <h3>Info</h3>
                <div id="info">Ready</div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        
        async function testConnection() {
            document.getElementById('status').innerHTML = 
                '<div class="loading">Testing Yahoo Finance connection...</div>';
            
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('status').innerHTML = 
                        `<div class="warning">✓ ${data.status} - AAPL: $${data.price}</div>`;
                } else {
                    document.getElementById('status').innerHTML = 
                        `<div class="warning">✗ ${data.status}: ${data.suggestion}</div>`;
                }
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    `<div class="warning">Error: ${error.message}</div>`;
            }
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            
            document.getElementById('status').innerHTML = 
                '<div class="loading">Fetching data with 3-second delays... This will take a moment...</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=1mo`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('status').innerHTML = 
                        `<div class="warning">Error: ${data.error}<br>${data.message || ''}</div>`;
                    return;
                }
                
                document.getElementById('status').innerHTML = 
                    `<div class="warning">✓ Data received from ${data.source}</div>`;
                
                // Update chart
                updateChart(data);
                
                // Update info
                let html = `<strong>$${data.current_price.toFixed(2)}</strong><br><br>`;
                
                if (data.indicators) {
                    html += '<strong>Indicators:</strong><br>';
                    for (const [key, value] of Object.entries(data.indicators)) {
                        html += `${key}: ${value.toFixed(2)}<br>`;
                    }
                }
                
                document.getElementById('info').innerHTML = html;
                
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    `<div class="warning">Error: ${error.message}</div>`;
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            
            if (chart) chart.destroy();
            
            chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: data.data.map(d => ({
                            x: new Date(d.date).getTime(),
                            o: d.open,
                            h: d.high,
                            l: d.low,
                            c: d.close
                        }))
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    </script>
</body>
</html>
    ''')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)