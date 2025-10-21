#!/usr/bin/env python3
"""
ML Stock Predictor Server - Fixed for Yahoo Finance "Invalid Crumb" Error
Windows 11 Optimized Version with yfinance workarounds
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta
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

# CRITICAL FIX: Update yfinance and clear cache
logger.info("Initializing with yfinance fixes...")

# Try importing and updating yfinance
try:
    # First, try to clear yfinance cache
    import shutil
    import tempfile
    cache_dir = os.path.join(tempfile.gettempdir(), 'yfinance')
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            logger.info("✅ Cleared yfinance cache")
        except:
            logger.warning("Could not clear yfinance cache")
    
    # Import yfinance with latest version
    import yfinance as yf
    
    # IMPORTANT: Disable yfinance progress bars and threading
    yf.set_tz_cache_location(None)
    
    import pandas as pd
    import numpy as np
    
    YF_AVAILABLE = True
    logger.info(f"✅ yfinance version {yf.__version__} loaded successfully")
    
    # Test yfinance immediately
    try:
        test = yf.download("AAPL", period="1d", progress=False, threads=False)
        if not test.empty:
            logger.info("✅ yfinance test successful")
        else:
            logger.warning("⚠️ yfinance test returned empty data")
    except Exception as e:
        logger.warning(f"⚠️ yfinance test failed: {e}")
    
except ImportError as e:
    YF_AVAILABLE = False
    logger.error(f"❌ yfinance not available: {e}")
    logger.error("Please run: pip install --upgrade yfinance")

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
    'last_fetch': {},
    'cache': {}
}

def fetch_with_yfinance_fallback(symbol, period='1mo'):
    """
    Fetch stock data with multiple fallback methods to handle Invalid Crumb error
    """
    logger.info(f"Attempting to fetch {symbol} with fallback methods...")
    
    # Method 1: Try standard yf.download
    try:
        logger.info(f"Method 1: Using yf.download for {symbol}")
        df = yf.download(
            tickers=symbol,
            period=period,
            interval='1d',
            auto_adjust=True,
            prepost=False,
            threads=False,
            progress=False
        )
        
        if df is not None and not df.empty:
            logger.info(f"✅ Method 1 successful for {symbol}")
            return df, None
    except Exception as e:
        logger.warning(f"Method 1 failed: {e}")
    
    # Method 2: Try using Ticker object with history
    try:
        logger.info(f"Method 2: Using Ticker.history for {symbol}")
        ticker = yf.Ticker(symbol)
        
        # Map period to days
        period_days = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
        }
        days = period_days.get(period, 30)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Try history method
        df = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1d',
            auto_adjust=True
        )
        
        if df is not None and not df.empty:
            logger.info(f"✅ Method 2 successful for {symbol}")
            # Get info separately
            try:
                info = ticker.info
                return df, info
            except:
                return df, None
    except Exception as e:
        logger.warning(f"Method 2 failed: {e}")
    
    # Method 3: Try with explicit parameters and retry
    try:
        logger.info(f"Method 3: Retry with session reset for {symbol}")
        
        # Create a new Ticker with fresh session
        ticker = yf.Ticker(symbol)
        
        # Force session reset
        ticker._reset_session()
        
        # Try to get data with minimal parameters
        df = ticker.history(period=period)
        
        if df is not None and not df.empty:
            logger.info(f"✅ Method 3 successful for {symbol}")
            return df, None
    except Exception as e:
        logger.warning(f"Method 3 failed: {e}")
    
    # Method 4: Use different period format
    try:
        logger.info(f"Method 4: Alternative period format for {symbol}")
        
        # Try different period specifications
        alternative_periods = {
            '1mo': '30d',
            '3mo': '90d',
            '6mo': '180d',
            '1y': '365d'
        }
        
        alt_period = alternative_periods.get(period, period)
        
        df = yf.download(
            symbol,
            period=alt_period,
            progress=False,
            threads=False
        )
        
        if df is not None and not df.empty:
            logger.info(f"✅ Method 4 successful for {symbol}")
            return df, None
    except Exception as e:
        logger.warning(f"Method 4 failed: {e}")
    
    logger.error(f"All yfinance methods failed for {symbol}")
    return None, None

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
    if os.path.exists('interface.html'):
        return send_from_directory('.', 'interface.html')
    
    # Return embedded simple interface
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Stock Predictor - Fixed for Invalid Crumb</title>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.2); 
            }
            h1 { color: #333; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .status { 
                padding: 15px; 
                background: #e8f5e9; 
                border-radius: 8px; 
                margin: 20px 0; 
                border-left: 4px solid #4CAF50;
            }
            .warning {
                padding: 15px;
                background: #fff3e0;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #ff9800;
            }
            .error { 
                background: #ffebee; 
                color: #c62828; 
                border-left-color: #f44336;
            }
            .success { 
                background: #e8f5e9; 
                color: #2e7d32; 
            }
            button { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 5px; 
                font-size: 16px;
                transition: transform 0.2s;
            }
            button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            input, select { 
                padding: 12px; 
                margin: 10px; 
                border: 2px solid #e0e0e0; 
                border-radius: 8px; 
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            #results { 
                margin-top: 30px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 10px; 
                min-height: 150px; 
            }
            .stock-btn-group {
                margin: 20px 0;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .price-display {
                font-size: 2em;
                font-weight: bold;
                color: #333;
                margin: 15px 0;
            }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .info-item {
                padding: 10px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            .info-label {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            .info-value {
                color: #333;
                font-size: 1.1em;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 ML Stock Predictor</h1>
            <p class="subtitle">Fixed for Yahoo Finance "Invalid Crumb" Error</p>
            
            <div class="warning">
                <strong>⚠️ Yahoo Finance Fix Applied:</strong><br>
                This server includes multiple fallback methods to handle the "Invalid Crumb" error.
                If one method fails, it automatically tries alternatives.
            </div>
            
            <div class="status">
                Server Status: <span id="status">Checking...</span>
            </div>
            
            <div>
                <input type="text" id="symbol" placeholder="Stock Symbol (e.g., CBA, AAPL)" value="AAPL">
                <select id="period">
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <button onclick="fetchData()">Fetch Data</button>
            </div>
            
            <div class="stock-btn-group">
                <button onclick="testSymbol('AAPL')">Test AAPL 🇺🇸</button>
                <button onclick="testSymbol('MSFT')">Test MSFT 🇺🇸</button>
                <button onclick="testSymbol('CBA')">Test CBA 🇦🇺</button>
                <button onclick="testSymbol('BHP')">Test BHP 🇦🇺</button>
                <button onclick="checkStatus()">Check Status</button>
            </div>
            
            <div id="results"></div>
        </div>
        
        <script>
            async function checkStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    document.getElementById('status').innerHTML = 
                        '<span style="color: #4CAF50;">✅ Running</span>';
                    document.getElementById('results').innerHTML = 
                        '<div class="success"><strong>Server is running!</strong><br>' +
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                } catch (error) {
                    document.getElementById('status').innerHTML = 
                        '<span style="color: #f44336;">❌ Error</span>';
                    document.getElementById('results').innerHTML = 
                        '<div class="error">Error: ' + error + '</div>';
                }
            }
            
            async function fetchData() {
                const symbol = document.getElementById('symbol').value;
                testSymbol(symbol);
            }
            
            async function testSymbol(symbol) {
                document.getElementById('results').innerHTML = 
                    '<div style="text-align: center; padding: 40px;">⏳ Loading ' + symbol + '...</div>';
                try {
                    const period = document.getElementById('period').value;
                    const response = await fetch('/api/fetch', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol: symbol, period: period})
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        const changeColor = data.price_change >= 0 ? '#4CAF50' : '#f44336';
                        const changeSymbol = data.price_change >= 0 ? '▲' : '▼';
                        
                        document.getElementById('results').innerHTML = 
                            '<div class="success">' +
                            '<h2>' + data.symbol + ' - ' + data.company + '</h2>' +
                            '<div class="price-display">' + 
                            data.currency + ' $' + data.latest_price.toFixed(2) + 
                            '</div>' +
                            '<div style="color: ' + changeColor + '; font-size: 1.2em;">' +
                            changeSymbol + ' ' + Math.abs(data.price_change).toFixed(2) + 
                            ' (' + data.price_change_pct.toFixed(2) + '%)' +
                            '</div>' +
                            '<div class="info-grid">' +
                            '<div class="info-item">' +
                            '<div class="info-label">Data Points</div>' +
                            '<div class="info-value">' + data.data_points + '</div>' +
                            '</div>' +
                            '<div class="info-item">' +
                            '<div class="info-label">Date Range</div>' +
                            '<div class="info-value">' + data.start_date + ' to ' + data.end_date + '</div>' +
                            '</div>' +
                            '<div class="info-item">' +
                            '<div class="info-label">Source</div>' +
                            '<div class="info-value">' + data.source + '</div>' +
                            '</div>' +
                            '<div class="info-item">' +
                            '<div class="info-label">Method</div>' +
                            '<div class="info-value">' + (data.fetch_method || 'standard') + '</div>' +
                            '</div>' +
                            '</div>' +
                            '</div>';
                    } else {
                        document.getElementById('results').innerHTML = 
                            '<div class="error"><strong>Error:</strong> ' + 
                            (data.error || 'Unknown error') + 
                            '<br><br>Debug Info:<br>' +
                            '<pre>' + JSON.stringify(data, null, 2) + '</pre>' +
                            '</div>';
                    }
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        '<div class="error"><strong>Network Error:</strong> ' + error + 
                        '<br><br>Make sure the server is running.</div>';
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
        'version': '2.0.0',
        'platform': 'Windows 11 - Invalid Crumb Fix',
        'timestamp': datetime.now().isoformat(),
        'server_uptime': system_state['server_start'],
        'requests_served': system_state['requests_count'],
        'components': {
            'yahoo_finance': YF_AVAILABLE,
            'alpha_vantage': REQUESTS_AVAILABLE,
            'yahoo_status': system_state['yahoo_status'],
            'alpha_vantage_status': system_state['alpha_vantage_status']
        },
        'fixes_applied': [
            'Multiple yfinance fallback methods',
            'Cache clearing on startup',
            'Session reset on failures',
            'Alternative period formats',
            'Thread safety disabled'
        ]
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def api_fetch():
    """Fetch stock data endpoint with Invalid Crumb fixes"""
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
        
        # Check cache first (1 minute cache)
        cache_key = f"{symbol}_{period}"
        if cache_key in system_state['cache']:
            cached_data, cache_time = system_state['cache'][cache_key]
            if (datetime.now() - cache_time).seconds < 60:
                logger.info(f"📦 Returning cached data for {symbol}")
                cached_data['from_cache'] = True
                return jsonify(cached_data)
        
        # Try Yahoo Finance with multiple fallback methods
        if YF_AVAILABLE:
            try:
                logger.info(f"Attempting Yahoo Finance fetch for {symbol}")
                
                # Use our fallback method
                df, info = fetch_with_yfinance_fallback(symbol, period)
                
                if df is not None and not df.empty:
                    system_state['yahoo_status'] = 'active'
                    
                    # Get company info if not provided
                    if info is None:
                        try:
                            ticker = yf.Ticker(symbol)
                            info = ticker.info or {}
                        except:
                            info = {}
                    
                    company_name = info.get('longName', symbol)
                    currency = info.get('currency', 'AUD' if '.AX' in symbol else 'USD')
                    
                    # Process data
                    dates = [d.strftime('%Y-%m-%d') for d in df.index]
                    
                    # Handle different column names
                    close_col = 'Close' if 'Close' in df.columns else 'close'
                    volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
                    
                    prices = df[close_col].values.flatten().tolist() if close_col in df.columns else []
                    volumes = df[volume_col].values.flatten().tolist() if volume_col in df.columns else []
                    
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
                        'fetch_method': 'fallback_methods',
                        'data_points': len(df),
                        'start_date': dates[0] if dates else '',
                        'end_date': dates[-1] if dates else '',
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices[-30:] if len(prices) > 30 else prices,
                        'dates': dates[-30:] if len(dates) > 30 else dates,
                        'volumes': volumes[-30:] if len(volumes) > 30 else volumes,
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat(),
                        'from_cache': False
                    }
                    
                    # Cache the successful response
                    system_state['cache'][cache_key] = (response_data, datetime.now())
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
                    dates = sorted(list(time_series.keys()))[-30:]
                    
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
                        'fetch_method': 'api',
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
                        'fetch_time': datetime.now().isoformat(),
                        'from_cache': False
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
            'debug_info': {
                'yahoo_status': system_state['yahoo_status'],
                'alpha_vantage_status': system_state['alpha_vantage_status'],
                'symbol_tried': symbol,
                'original_symbol': original_symbol
            },
            'suggestions': [
                'Try updating yfinance: pip install --upgrade yfinance',
                'Check if the symbol is correct',
                'Try again in a few moments',
                'Check server.log for detailed error messages'
            ]
        }), 404
        
    except Exception as e:
        logger.error(f"Server error in api_fetch: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/diagnose', methods=['GET'])
def api_diagnose():
    """Enhanced diagnostic endpoint"""
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
        'cache_entries': len(system_state['cache'])
    }
    
    # Test yfinance with different methods
    if YF_AVAILABLE:
        diagnostics['yfinance_version'] = yf.__version__
        
        test_results = []
        
        # Test method 1: Standard download
        try:
            df = yf.download("AAPL", period="5d", progress=False, threads=False)
            test_results.append("Method 1 (download): SUCCESS" if not df.empty else "Method 1 (download): EMPTY")
        except Exception as e:
            test_results.append(f"Method 1 (download): FAILED - {str(e)[:50]}")
        
        # Test method 2: Ticker.history
        try:
            ticker = yf.Ticker("AAPL")
            df = ticker.history(period="5d")
            test_results.append("Method 2 (history): SUCCESS" if not df.empty else "Method 2 (history): EMPTY")
        except Exception as e:
            test_results.append(f"Method 2 (history): FAILED - {str(e)[:50]}")
        
        # Test method 3: Ticker.info
        try:
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            test_results.append("Method 3 (info): SUCCESS" if info else "Method 3 (info): EMPTY")
        except Exception as e:
            test_results.append(f"Method 3 (info): FAILED - {str(e)[:50]}")
        
        diagnostics['yfinance_tests'] = test_results
    
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
    print("   ML STOCK PREDICTOR SERVER - INVALID CRUMB FIX")
    print("="*70)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working Directory: {os.getcwd()}")
    print("-"*70)
    
    if YF_AVAILABLE:
        print(f"Yahoo Finance: ✅ AVAILABLE (version {yf.__version__})")
        print("Fixes Applied:")
        print("  • Multiple fallback fetch methods")
        print("  • Cache clearing on startup")
        print("  • Session reset on failures")
        print("  • Threading disabled for stability")
    else:
        print("Yahoo Finance: ❌ NOT INSTALLED")
        print("Please run: pip install --upgrade yfinance")
    
    print(f"Alpha Vantage: {'✅ AVAILABLE' if REQUESTS_AVAILABLE else '❌ NOT INSTALLED'}")
    print(f"API Key: {ALPHA_VANTAGE_API_KEY[:8]}...")
    print("="*70)
    print(f"\n🚀 Starting server on: http://localhost:{PORT}")
    print(f"📊 Access interface at: http://localhost:{PORT}")
    print(f"📝 Logs written to: server.log")
    print(f"🔧 Diagnostics at: http://localhost:{PORT}/api/diagnose")
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