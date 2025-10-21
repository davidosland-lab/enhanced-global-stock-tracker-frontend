#!/usr/bin/env python3
"""
Simple Flask server that bypasses .env file issues
Direct startup without dotenv loading
"""

import os
import sys
import json
from datetime import datetime

# Disable dotenv loading completely
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Now import Flask
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Import our components safely
try:
    import yfinance as yf
    YF_AVAILABLE = True
except:
    YF_AVAILABLE = False

try:
    from config import ALPHA_VANTAGE_API_KEY
    API_KEY = ALPHA_VANTAGE_API_KEY
except:
    API_KEY = '68ZFANK047DL0KSR'

# Create Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    """Serve the interface"""
    # Check if unified_interface.html exists
    if os.path.exists('unified_interface.html'):
        try:
            with open('unified_interface.html', 'r', encoding='utf-8') as f:
                return f.read()
        except:
            pass
    
    # Fallback HTML
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Stock Predictor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .status-card {
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .status-card.success {
                border-left-color: #28a745;
            }
            .status-card.warning {
                border-left-color: #ffc107;
            }
            .test-section {
                margin: 30px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            button {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover {
                opacity: 0.9;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                font-family: monospace;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ML Stock Predictor - Running!</h1>
            
            <div class="status-grid">
                <div class="status-card success">
                    <h3>✅ Server Status</h3>
                    <p>Flask server running on port 8000</p>
                </div>
                <div class="status-card">
                    <h3>🔑 API Key</h3>
                    <p>Configured: ''' + API_KEY[:8] + '''...</p>
                </div>
                <div class="status-card">
                    <h3>📊 Yahoo Finance</h3>
                    <p>''' + ('Available' if YF_AVAILABLE else 'Not Available') + '''</p>
                </div>
                <div class="status-card">
                    <h3>⏰ Server Time</h3>
                    <p>''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🧪 Test API Endpoints</h2>
                <button onclick="testStatus()">Test Status</button>
                <button onclick="testFetch()">Test Data Fetch</button>
                <button onclick="testYahoo()">Test Yahoo Finance</button>
                <div id="result"></div>
            </div>
        </div>
        
        <script>
            async function testStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
            
            async function testFetch() {
                try {
                    const response = await fetch('/api/fetch', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol: 'AAPL', period: '5d'})
                    });
                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
            
            async function testYahoo() {
                try {
                    const response = await fetch('/api/test-yahoo');
                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/status')
def status():
    """Return system status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'api_key_configured': bool(API_KEY),
        'yahoo_finance': YF_AVAILABLE,
        'server': 'simple_server.py',
        'port': 8000
    })

@app.route('/api/test-yahoo')
def test_yahoo():
    """Test Yahoo Finance directly"""
    if not YF_AVAILABLE:
        return jsonify({'error': 'Yahoo Finance not available'}), 503
    
    try:
        ticker = yf.Ticker('MSFT')  # Try Microsoft instead of Apple
        info = ticker.info
        hist = ticker.history(period='5d')
        
        return jsonify({
            'success': True,
            'symbol': 'MSFT',
            'name': info.get('longName', 'Microsoft Corporation'),
            'price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            'history_days': len(hist),
            'last_close': float(hist['Close'].iloc[-1]) if not hist.empty else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch', methods=['POST'])
def fetch_data():
    """Fetch stock data"""
    if not YF_AVAILABLE:
        return jsonify({'error': 'Data fetching not available'}), 503
    
    data = request.json
    symbol = data.get('symbol', 'MSFT')
    period = data.get('period', '1mo')
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            # Try with .AX suffix for Australian stocks
            if not symbol.endswith('.AX'):
                ticker = yf.Ticker(f"{symbol}.AX")
                hist = ticker.history(period=period)
        
        if hist.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data_points': len(hist),
            'start_date': hist.index[0].strftime('%Y-%m-%d'),
            'end_date': hist.index[-1].strftime('%Y-%m-%d'),
            'latest_close': float(hist['Close'].iloc[-1]),
            'prices': hist['Close'].tail(10).tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 ML STOCK PREDICTOR - SIMPLE SERVER")
    print("="*60)
    print(f"✅ API Key configured: {API_KEY[:8]}...")
    print(f"✅ Yahoo Finance: {'Available' if YF_AVAILABLE else 'Not Available'}")
    print(f"✅ Starting server on http://localhost:8000")
    print("="*60)
    print("\n📊 Open your browser to: http://localhost:8000\n")
    
    # Run without debug mode and without reloader
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()