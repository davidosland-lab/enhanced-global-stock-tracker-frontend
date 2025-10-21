#!/usr/bin/env python3
"""
Fixed Real Data Server - Working Yahoo Finance
"""

import os
import sys
import json
from datetime import datetime

os.environ['FLASK_SKIP_DOTENV'] = '1'

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    print("WARNING: yfinance not available")

try:
    from config import ALPHA_VANTAGE_API_KEY
except:
    ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

system_state = {
    'yahoo': 'checking',
    'alpha_vantage': 'configured',
    'last_fetch': {}
}

@app.route('/')
def index():
    """Serve interface"""
    if os.path.exists('unified_interface.html'):
        with open('unified_interface.html', 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/html')
    return jsonify({'status': 'running'})

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running',
        'data_sources': {
            'yahoo': system_state['yahoo'],
            'alpha_vantage': system_state['alpha_vantage'],
            'current': 'alpha_vantage' if system_state['yahoo'] == 'error' else 'yahoo',
            'last_switch': None
        },
        'ml_ready': False,
        'mcp_ready': False,
        'sentiment_ready': False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def fetch_data():
    """Fetch real stock data"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    period = data.get('period', '1y')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    print(f"\n{'='*60}")
    print(f"Fetching: {symbol} ({period})")
    
    # Method 1: Try downloading directly without Ticker object
    if YF_AVAILABLE:
        try:
            print(f"Method 1: Direct yfinance download for {symbol}")
            
            # Map period to days for download
            period_map = {
                '5d': '5d', '1mo': '1mo', '3mo': '3mo',
                '6mo': '6mo', '1y': '1y', '2y': '2y', '5y': '5y'
            }
            yf_period = period_map.get(period, '1y')
            
            # Try direct download - suppress auto_adjust warning
            df = yf.download(symbol, period=yf_period, progress=False, auto_adjust=True)
            
            if df is not None and not df.empty:
                print(f"✅ Method 1 SUCCESS: Got {len(df)} days")
                system_state['yahoo'] = 'available'
                
                # Handle both Series and DataFrame types
                if len(df.columns) == 5:  # Single ticker returns DataFrame with 5 columns
                    prices = df['Close'].values.tolist()
                    volumes = df['Volume'].values.tolist() if 'Volume' in df else []
                    latest_price = float(prices[-1])
                else:  # Multi-ticker returns multi-level columns
                    prices = df['Close'].squeeze().values.tolist()
                    volumes = df['Volume'].squeeze().values.tolist() if 'Volume' in df else []
                    latest_price = float(prices[-1])
                
                return jsonify({
                    'symbol': symbol,
                    'source': 'yahoo_direct',
                    'data_points': len(df),
                    'start_date': df.index[0].strftime('%Y-%m-%d'),
                    'end_date': df.index[-1].strftime('%Y-%m-%d'),
                    'latest_price': latest_price,
                    'prices': prices,
                    'dates': [d.strftime('%Y-%m-%d') for d in df.index],
                    'volume': volumes,
                    'is_real_data': True
                })
            else:
                print(f"Method 1: No data returned")
        except Exception as e:
            print(f"Method 1 error: {e}")
    
    # Method 2: Try with .AX for Australian stocks
    if YF_AVAILABLE and not '.' in symbol:
        aus_symbols = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']
        if symbol in aus_symbols:
            try:
                test_symbol = f"{symbol}.AX"
                print(f"Method 2: Trying Australian symbol {test_symbol}")
                
                df = yf.download(test_symbol, period=period, progress=False, auto_adjust=True)
                
                if df is not None and not df.empty:
                    print(f"✅ Method 2 SUCCESS: Got {len(df)} days for {test_symbol}")
                    system_state['yahoo'] = 'available'
                    
                    # Handle both Series and DataFrame types
                    if len(df.columns) == 5:  # Single ticker
                        prices = df['Close'].values.tolist()
                        volumes = df['Volume'].values.tolist() if 'Volume' in df else []
                        latest_price = float(prices[-1])
                    else:  # Multi-ticker
                        prices = df['Close'].squeeze().values.tolist()
                        volumes = df['Volume'].squeeze().values.tolist() if 'Volume' in df else []
                        latest_price = float(prices[-1])
                    
                    return jsonify({
                        'symbol': test_symbol,
                        'source': 'yahoo_direct',
                        'data_points': len(df),
                        'start_date': df.index[0].strftime('%Y-%m-%d'),
                        'end_date': df.index[-1].strftime('%Y-%m-%d'),
                        'latest_price': latest_price,
                        'prices': prices,
                        'dates': [d.strftime('%Y-%m-%d') for d in df.index],
                        'volume': volumes,
                        'is_real_data': True
                    })
            except Exception as e:
                print(f"Method 2 error: {e}")
    
    # Method 3: Try Alpha Vantage
    if ALPHA_VANTAGE_API_KEY:
        try:
            print(f"Method 3: Trying Alpha Vantage")
            from alpha_vantage_fetcher import AlphaVantageDataFetcher
            av = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
            
            # Use the correct method name
            av_data = av.fetch_daily_data(symbol)
            
            if av_data is not None and len(av_data) > 0:
                print(f"✅ Method 3 SUCCESS: Got {len(av_data)} days from Alpha Vantage")
                system_state['alpha_vantage'] = 'available'
                
                # Convert DataFrame columns to lists
                prices = av_data['Close'].values.tolist() if 'Close' in av_data else av_data['close'].values.tolist()
                volumes = av_data['Volume'].values.tolist() if 'Volume' in av_data else (av_data['volume'].values.tolist() if 'volume' in av_data else [])
                
                return jsonify({
                    'symbol': symbol,
                    'source': 'alpha_vantage',
                    'data_points': len(av_data),
                    'start_date': av_data.index[0].strftime('%Y-%m-%d'),
                    'end_date': av_data.index[-1].strftime('%Y-%m-%d'),
                    'latest_price': float(prices[-1]),
                    'prices': prices,
                    'dates': [d.strftime('%Y-%m-%d') for d in av_data.index],
                    'volume': volumes,
                    'is_real_data': True
                })
        except Exception as e:
            print(f"Method 3 Alpha Vantage error: {e}")
            system_state['alpha_vantage'] = 'error'
    
    # All methods failed
    system_state['yahoo'] = 'error'
    
    return jsonify({
        'error': f'Could not fetch data for {symbol}',
        'attempted_methods': [
            f'Yahoo Finance direct: {symbol}',
            f'Yahoo with .AX: {symbol}.AX' if symbol in ['CBA','BHP','CSL'] else None,
            'Alpha Vantage API' if ALPHA_VANTAGE_API_KEY else None
        ],
        'suggestions': [
            'Yahoo Finance may be blocking requests',
            'Try using a VPN',
            'Try symbols: SPY, QQQ, IWM (ETFs often work)',
            'Wait a few minutes and try again'
        ]
    }), 404

@app.route('/api/train', methods=['POST', 'OPTIONS'])
def train_model():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({'message': 'Training requires full ML implementation'}), 200

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({'message': 'Predictions require trained model'}), 200

@app.route('/api/backtest', methods=['POST', 'OPTIONS'])
def backtest():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({'message': 'Backtesting requires historical data'}), 200

@app.route('/api/mcp/tools')
def mcp_tools():
    return jsonify({'available': False})

def main():
    print("\n" + "="*60)
    print("🚀 YAHOO FIX - REAL DATA SERVER")
    print("="*60)
    print("✅ Fixed DataFrame .tolist() issue")
    print("✅ Using .values.tolist() for compatibility")
    print(f"✅ API Key: {ALPHA_VANTAGE_API_KEY[:8]}...")
    print("="*60)
    print("\n📊 Open: http://localhost:8000")
    print("📊 Try: SPY, QQQ, MSFT, GOOGL, AAPL\n")
    
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()