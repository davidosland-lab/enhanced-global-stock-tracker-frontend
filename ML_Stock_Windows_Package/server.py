#!/usr/bin/env python3
"""
ML Stock Predictor Server - Windows 11 Optimized Version
Fixed for Windows 11 compatibility with proper CORS and routing
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try importing yfinance
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YF_AVAILABLE = True
    logger.info("✅ yfinance loaded successfully")
except ImportError as e:
    YF_AVAILABLE = False
    logger.error(f"❌ yfinance not available: {e}")

# Try importing requests for Alpha Vantage
try:
    import requests
    REQUESTS_AVAILABLE = True
    logger.info("✅ requests loaded successfully")
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - Alpha Vantage disabled")

# Configuration
ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
PORT = 8000

# Australian stocks list
AUSTRALIAN_STOCKS = [
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG',
    'TLS', 'MQG', 'SUN', 'IAG', 'QBE', 'AMP', 'ORG', 'STO', 'WPL', 'NCM'
]

# Create Flask app
app = Flask(__name__)

# Configure CORS for Windows browsers
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept", "Authorization"]
    }
})

# System state
system_state = {
    'server_start': datetime.now().isoformat(),
    'yahoo_status': 'checking',
    'alpha_vantage_status': 'checking',
    'requests_count': 0,
    'last_fetch': {}
}

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/')
def index():
    """Serve the main interface"""
    interface_files = ['interface.html', 'index.html']
    for filename in interface_files:
        if os.path.exists(filename):
            return send_from_directory('.', filename)
    
    # Return embedded interface if no file found
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Stock Predictor - Windows 11</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .status { padding: 10px; background: #e8f5e9; border-radius: 5px; margin: 20px 0; }
            .error { background: #ffebee; color: #c62828; }
            .success { background: #e8f5e9; color: #2e7d32; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #45a049; }
            input { padding: 10px; margin: 10px; border: 1px solid #ddd; border-radius: 5px; }
            #results { margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 5px; min-height: 100px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ML Stock Predictor - Windows 11 Edition</h1>
            <div class="status">
                Server Status: <span id="status">Checking...</span>
            </div>
            
            <div>
                <input type="text" id="symbol" placeholder="Stock Symbol (e.g., CBA)" value="CBA">
                <button onclick="fetchData()">Fetch Data</button>
                <button onclick="checkStatus()">Check Status</button>
            </div>
            
            <div>
                <button onclick="testSymbol('CBA')">Test CBA</button>
                <button onclick="testSymbol('AAPL')">Test AAPL</button>
                <button onclick="testSymbol('BHP')">Test BHP</button>
            </div>
            
            <div id="results"></div>
        </div>
        
        <script>
            async function checkStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    document.getElementById('status').textContent = '✅ Running';
                    document.getElementById('results').innerHTML = 
                        '<div class="success">Server is running!<br>' + 
                        JSON.stringify(data, null, 2) + '</div>';
                } catch (error) {
                    document.getElementById('status').textContent = '❌ Error';
                    document.getElementById('results').innerHTML = 
                        '<div class="error">Error: ' + error + '</div>';
                }
            }
            
            async function fetchData() {
                const symbol = document.getElementById('symbol').value;
                testSymbol(symbol);
            }
            
            async function testSymbol(symbol) {
                document.getElementById('results').innerHTML = '<div>Loading...</div>';
                try {
                    const response = await fetch('/api/fetch', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol: symbol, period: '1mo'})
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('results').innerHTML = 
                            '<div class="success"><h3>' + data.symbol + ' - ' + data.company + '</h3>' +
                            '<p>Price: ' + data.currency + ' $' + data.latest_price.toFixed(2) + '</p>' +
                            '<p>Change: ' + data.price_change_pct.toFixed(2) + '%</p>' +
                            '<p>Data Points: ' + data.data_points + '</p>' +
                            '<p>Source: ' + data.source + '</p></div>';
                    } else {
                        document.getElementById('results').innerHTML = 
                            '<div class="error">Error: ' + (data.error || 'Unknown error') + '</div>';
                    }
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        '<div class="error">Network Error: ' + error + '</div>';
                }
            }
            
            // Check status on load
            window.onload = checkStatus;
        </script>
    </body>
    </html>
    """

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def api_status():
    """System status endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    system_state['requests_count'] += 1
    
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'platform': 'Windows 11 Optimized',
        'timestamp': datetime.now().isoformat(),
        'server_uptime': system_state['server_start'],
        'requests_served': system_state['requests_count'],
        'components': {
            'yahoo_finance': YF_AVAILABLE,
            'alpha_vantage': REQUESTS_AVAILABLE,
            'yahoo_status': system_state['yahoo_status'],
            'alpha_vantage_status': system_state['alpha_vantage_status']
        },
        'features': {
            'australian_stocks': True,
            'us_stocks': True,
            'auto_detection': True,
            'real_time_data': YF_AVAILABLE
        }
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def api_fetch():
    """Fetch stock data endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        system_state['requests_count'] += 1
        
        # Parse request
        data = request.get_json()
        if not data:
            logger.warning("No JSON data in request")
            return jsonify({'error': 'No data provided'}), 400
        
        symbol = data.get('symbol', '').upper().strip()
        period = data.get('period', '1mo')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        logger.info(f"📊 Fetching {symbol} for period {period}")
        
        # Auto-detect Australian stocks
        original_symbol = symbol
        if symbol in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
            logger.info(f"🇦🇺 Auto-detected Australian stock: {original_symbol} -> {symbol}")
        
        # Try Yahoo Finance first
        if YF_AVAILABLE:
            try:
                logger.info(f"Attempting Yahoo Finance fetch for {symbol}")
                
                # Download data
                df = yf.download(
                    symbol, 
                    period=period, 
                    progress=False,
                    auto_adjust=True,
                    threads=False,
                    timeout=10
                )
                
                if df is not None and not df.empty:
                    system_state['yahoo_status'] = 'active'
                    
                    # Get company info
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info or {}
                        company_name = info.get('longName', symbol)
                        currency = info.get('currency', 'AUD' if '.AX' in symbol else 'USD')
                    except:
                        company_name = symbol
                        currency = 'AUD' if '.AX' in symbol else 'USD'
                    
                    # Process data
                    dates = [d.strftime('%Y-%m-%d') for d in df.index]
                    prices = df['Close'].values.flatten().tolist() if 'Close' in df.columns else []
                    volumes = df['Volume'].values.flatten().tolist() if 'Volume' in df.columns else []
                    
                    # Calculate statistics
                    latest_price = prices[-1] if prices else 0
                    price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
                    price_change_pct = (price_change / prices[0] * 100) if prices and prices[0] > 0 else 0
                    
                    response_data = {
                        'symbol': symbol,
                        'original_symbol': original_symbol,
                        'company': company_name,
                        'currency': currency,
                        'source': 'yahoo',
                        'data_points': len(df),
                        'start_date': dates[0] if dates else '',
                        'end_date': dates[-1] if dates else '',
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices[:30],  # Limit to last 30 for response size
                        'dates': dates[:30],
                        'volumes': volumes[:30],
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat()
                    }
                    
                    system_state['last_fetch'][symbol] = datetime.now().isoformat()
                    logger.info(f"✅ Success: {symbol} @ {currency} {latest_price:.2f}")
                    
                    return jsonify(response_data)
                else:
                    logger.warning(f"No data returned from Yahoo for {symbol}")
                    system_state['yahoo_status'] = 'no_data'
                    
            except Exception as e:
                logger.error(f"Yahoo Finance error: {str(e)}")
                system_state['yahoo_status'] = 'error'
        
        # Try Alpha Vantage as fallback (only for US stocks)
        if REQUESTS_AVAILABLE and not symbol.endswith('.AX'):
            try:
                logger.info(f"Attempting Alpha Vantage fetch for {symbol}")
                
                url = 'https://www.alphavantage.co/query'
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': ALPHA_VANTAGE_API_KEY,
                    'outputsize': 'compact'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    system_state['alpha_vantage_status'] = 'active'
                    time_series = data['Time Series (Daily)']
                    dates = sorted(list(time_series.keys()))[-30:]  # Last 30 days
                    
                    prices = [float(time_series[d]['4. close']) for d in dates]
                    volumes = [int(time_series[d]['5. volume']) for d in dates]
                    
                    latest_price = prices[-1] if prices else 0
                    price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
                    price_change_pct = (price_change / prices[0] * 100) if prices and prices[0] > 0 else 0
                    
                    response_data = {
                        'symbol': symbol,
                        'original_symbol': original_symbol,
                        'company': symbol,
                        'currency': 'USD',
                        'source': 'alpha_vantage',
                        'data_points': len(dates),
                        'start_date': dates[0] if dates else '',
                        'end_date': dates[-1] if dates else '',
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices,
                        'dates': dates,
                        'volumes': volumes,
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat()
                    }
                    
                    logger.info(f"✅ Alpha Vantage success: {symbol} @ ${latest_price:.2f}")
                    return jsonify(response_data)
                else:
                    if 'Note' in data:
                        logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                        system_state['alpha_vantage_status'] = 'rate_limited'
                    else:
                        logger.warning(f"No data from Alpha Vantage for {symbol}")
                        system_state['alpha_vantage_status'] = 'no_data'
                        
            except Exception as e:
                logger.error(f"Alpha Vantage error: {str(e)}")
                system_state['alpha_vantage_status'] = 'error'
        
        # If all sources failed
        return jsonify({
            'error': f'Could not fetch data for {symbol}',
            'message': 'Both Yahoo Finance and Alpha Vantage failed',
            'suggestions': [
                'Check if the symbol is correct',
                'For Australian stocks, they will auto-add .AX',
                'Try again in a few moments',
                'Check server.log for details'
            ],
            'yahoo_status': system_state['yahoo_status'],
            'alpha_vantage_status': system_state['alpha_vantage_status']
        }), 404
        
    except Exception as e:
        logger.error(f"Server error in api_fetch: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/diagnose', methods=['GET'])
def api_diagnose():
    """Diagnostic endpoint for troubleshooting"""
    diagnostics = {
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'yfinance_available': YF_AVAILABLE,
        'requests_available': REQUESTS_AVAILABLE,
        'server_start_time': system_state['server_start'],
        'total_requests': system_state['requests_count'],
        'last_fetches': system_state['last_fetch'],
        'yahoo_status': system_state['yahoo_status'],
        'alpha_vantage_status': system_state['alpha_vantage_status'],
        'environment_variables': {
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
            'PATH': os.environ.get('PATH', 'Not set')[:200] + '...'  # Truncate for security
        }
    }
    
    # Test Yahoo Finance
    if YF_AVAILABLE:
        try:
            test_ticker = yf.Ticker('AAPL')
            test_info = test_ticker.info
            diagnostics['yahoo_test'] = 'SUCCESS' if test_info else 'FAILED'
        except Exception as e:
            diagnostics['yahoo_test'] = f'ERROR: {str(e)}'
    else:
        diagnostics['yahoo_test'] = 'NOT_AVAILABLE'
    
    return jsonify(diagnostics)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.path}")
    return jsonify({
        'error': 'Endpoint not found',
        'path': request.path,
        'available_endpoints': [
            '/api/status',
            '/api/fetch',
            '/api/diagnose'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Check server.log for details'
    }), 500

def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("   ML STOCK PREDICTOR SERVER - WINDOWS 11 OPTIMIZED")
    print("="*70)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working Directory: {os.getcwd()}")
    print("-"*70)
    print(f"Yahoo Finance: {'✅ AVAILABLE' if YF_AVAILABLE else '❌ NOT INSTALLED'}")
    print(f"Alpha Vantage: {'✅ AVAILABLE' if REQUESTS_AVAILABLE else '❌ NOT INSTALLED'}")
    print(f"API Key: {ALPHA_VANTAGE_API_KEY[:8]}...")
    print("="*70)
    print(f"\n🚀 Starting server on: http://localhost:{PORT}")
    print(f"📊 Access interface at: http://localhost:{PORT}")
    print(f"📝 Logs written to: server.log")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Start the server
    try:
        app.run(
            host='127.0.0.1',
            port=PORT,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped gracefully")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        logger.error(f"Server startup error: {e}", exc_info=True)

if __name__ == '__main__':
    main()