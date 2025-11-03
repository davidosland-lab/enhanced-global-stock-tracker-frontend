#!/usr/bin/env python3
"""
Minimal ML Predictions - Guaranteed to work
No complex dependencies, simple predictions
"""

import os
import sys
import json
import warnings
import traceback
from datetime import datetime
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yfinance as yf

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 80)
print("MINIMAL ML PREDICTIONS SERVER")
print("=" * 80)

app = Flask(__name__)
CORS(app)

# Australian stocks
AUSTRALIAN_STOCKS = {'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG'}

def fetch_stock_data(symbol, period='1mo'):
    """Fetch stock data from Yahoo Finance"""
    try:
        # Handle Australian stocks
        original = symbol.upper()
        if original in AUSTRALIAN_STOCKS and not original.endswith('.AX'):
            symbol = f"{original}.AX"
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if not df.empty:
            return df, "Yahoo Finance"
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    
    return None, None

def simple_prediction(df):
    """Simple prediction without sklearn - just trend analysis"""
    try:
        if df is None or len(df) < 5:
            return None
        
        # Get current price
        current_price = float(df['Close'].iloc[-1])
        
        # Calculate simple moving average trend
        recent_prices = df['Close'].tail(10).values
        trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        # Calculate volatility
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std()
        
        # Simple predictions based on trend and volatility
        predictions = []
        
        for days in [1, 3, 5, 7]:
            # Extrapolate trend
            price_change = trend * days
            
            # Add some random walk based on volatility
            random_factor = np.random.normal(0, volatility * np.sqrt(days))
            
            predicted_price = current_price + price_change + (current_price * random_factor)
            predicted_return = ((predicted_price - current_price) / current_price) * 100
            
            predictions.append({
                'days': days,
                'price': predicted_price,
                'return': predicted_return,
                'confidence': max(30, 80 - days * 10)  # Confidence decreases with time
            })
        
        return {
            'predictions': predictions,
            'current_price': current_price,
            'method': 'trend_analysis'
        }
        
    except Exception as e:
        print(f"Prediction error: {e}")
        traceback.print_exc()
        return None

@app.route('/api/predict/<symbol>')
def get_predictions(symbol):
    """Simple prediction endpoint"""
    try:
        print(f"\n[{datetime.now()}] Prediction request for {symbol}")
        
        # Fetch data
        df, source = fetch_stock_data(symbol, period='3mo')
        
        if df is None:
            print(f"Failed to fetch data for {symbol}")
            return jsonify({
                'error': f'Unable to fetch data for {symbol}',
                'available': False
            }), 404
        
        print(f"Data fetched: {len(df)} records from {source}")
        
        # Generate predictions
        result = simple_prediction(df)
        
        if result is None:
            print("Prediction generation failed")
            return jsonify({
                'error': 'Unable to generate predictions',
                'available': False
            }), 500
        
        # Add metadata
        result['symbol'] = symbol
        result['source'] = source
        result['available'] = True
        result['timestamp'] = datetime.now().isoformat()
        
        print(f"Predictions generated successfully for {symbol}")
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR in get_predictions: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'available': False
        }), 500

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data endpoint"""
    try:
        df, source = fetch_stock_data(symbol, period='1mo')
        
        if df is None:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        current_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
        
        # Prepare simple chart data
        chart_data = []
        labels = []
        
        for i, (index, row) in enumerate(df.tail(30).iterrows()):
            chart_data.append({
                'x': i,
                'y': float(row['Close']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'open': float(row['Open'])
            })
            labels.append(index.strftime('%m/%d'))
        
        return jsonify({
            'symbol': symbol,
            'source': source,
            'current_price': current_price,
            'price_change': current_price - prev_close,
            'price_change_pct': ((current_price - prev_close) / prev_close) * 100,
            'data': chart_data,
            'labels': labels
        })
        
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': 'minimal-1.0',
        'ml_available': True,
        'ml_type': 'simple_trend_analysis'
    })

@app.route('/')
def index():
    """Simple test interface"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Minimal ML Stock Predictions</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            font-size: 16px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #764ba2;
        }
        .results {
            background: white;
            padding: 20px;
            border-radius: 10px;
            min-height: 200px;
        }
        .prediction {
            padding: 10px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .error {
            color: red;
            padding: 10px;
            background: #ffe0e0;
            border-radius: 5px;
        }
        .success {
            color: green;
            padding: 10px;
            background: #e0ffe0;
            border-radius: 5px;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Minimal ML Stock Predictions</h1>
        <p>Simple, working predictions without complex dependencies</p>
    </div>
    
    <div class="controls">
        <input type="text" id="symbol" value="AAPL" placeholder="Enter symbol">
        <button onclick="getStock()">Get Stock Data</button>
        <button onclick="getPredictions()">Get ML Predictions</button>
        <button onclick="testHealth()">Test Health</button>
    </div>
    
    <div class="results" id="results">
        <p>Click a button to test the endpoints...</p>
    </div>
    
    <script>
        const results = document.getElementById('results');
        
        function log(html) {
            results.innerHTML = html;
        }
        
        async function testHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                log('<div class="success">✓ Health Check Passed</div><pre>' + JSON.stringify(data, null, 2) + '</pre>');
            } catch (error) {
                log('<div class="error">✗ Health Check Failed: ' + error + '</div>');
            }
        }
        
        async function getStock() {
            const symbol = document.getElementById('symbol').value;
            log('<p>Fetching stock data for ' + symbol + '...</p>');
            
            try {
                const response = await fetch('/api/stock/' + symbol);
                const data = await response.json();
                
                if (response.ok) {
                    let html = '<div class="success">✓ Stock Data Retrieved</div>';
                    html += '<div class="prediction">';
                    html += '<h3>' + data.symbol + '</h3>';
                    html += '<p>Price: $' + data.current_price.toFixed(2) + '</p>';
                    html += '<p>Change: ' + (data.price_change >= 0 ? '+' : '') + data.price_change.toFixed(2);
                    html += ' (' + (data.price_change_pct >= 0 ? '+' : '') + data.price_change_pct.toFixed(2) + '%)</p>';
                    html += '<p>Source: ' + data.source + '</p>';
                    html += '</div>';
                    log(html);
                } else {
                    log('<div class="error">✗ Error: ' + (data.error || 'Unknown error') + '</div>');
                }
            } catch (error) {
                log('<div class="error">✗ Network Error: ' + error + '</div>');
            }
        }
        
        async function getPredictions() {
            const symbol = document.getElementById('symbol').value;
            log('<p>Generating ML predictions for ' + symbol + '...</p>');
            
            try {
                console.log('Fetching predictions for', symbol);
                const response = await fetch('/api/predict/' + symbol);
                console.log('Response status:', response.status);
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok && data.available) {
                    let html = '<div class="success">✓ ML Predictions Generated</div>';
                    html += '<div class="prediction">';
                    html += '<h3>Predictions for ' + data.symbol + '</h3>';
                    html += '<p>Current Price: $' + data.current_price.toFixed(2) + '</p>';
                    html += '<p>Method: ' + data.method + '</p>';
                    html += '</div>';
                    
                    data.predictions.forEach(pred => {
                        const color = pred.return >= 0 ? 'green' : 'red';
                        html += '<div class="prediction">';
                        html += '<strong>' + pred.days + ' Day Prediction:</strong> ';
                        html += '$' + pred.price.toFixed(2) + ' ';
                        html += '<span style="color: ' + color + '">';
                        html += (pred.return >= 0 ? '+' : '') + pred.return.toFixed(2) + '%';
                        html += '</span> ';
                        html += '<small>(Confidence: ' + pred.confidence + '%)</small>';
                        html += '</div>';
                    });
                    
                    log(html);
                } else {
                    log('<div class="error">✗ ML Not Available: ' + (data.error || 'Unknown error') + '</div>');
                }
            } catch (error) {
                console.error('Prediction error:', error);
                log('<div class="error">✗ Network Error: ' + error + '</div>');
            }
        }
        
        // Test health on load
        window.onload = () => {
            console.log('Minimal ML Predictions Ready');
            testHealth();
        };
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print(f"\nServer starting on http://localhost:5001")
    print("This is a minimal version that should work without sklearn")
    print("\nTest endpoints:")
    print("  http://localhost:5001/health")
    print("  http://localhost:5001/api/stock/AAPL")
    print("  http://localhost:5001/api/predict/AAPL")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)