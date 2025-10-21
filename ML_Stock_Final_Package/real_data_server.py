#!/usr/bin/env python3
"""
Real Data Only Server - NO mock, demo, or simulated data
Only returns actual market data or proper errors
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Optional

# Disable dotenv
os.environ['FLASK_SKIP_DOTENV'] = '1'

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# Import requirements
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YF_AVAILABLE = True
except ImportError as e:
    print(f"Error: {e}")
    print("Please install: pip install yfinance pandas numpy")
    YF_AVAILABLE = False

try:
    from config import ALPHA_VANTAGE_API_KEY
except:
    ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'

# Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# System state - track what's actually working
system_state = {
    'yahoo': 'unknown',
    'alpha_vantage': 'configured' if ALPHA_VANTAGE_API_KEY else 'not_configured',
    'last_fetch': {},
    'trained_models': {}
}

@app.route('/')
def index():
    """Serve the interface"""
    if os.path.exists('unified_interface.html'):
        try:
            with open('unified_interface.html', 'r', encoding='utf-8') as f:
                return Response(f.read(), mimetype='text/html')
        except:
            pass
    return jsonify({'status': 'running', 'api': 'ready'})

@app.route('/api/status')
def get_status():
    """Real status only"""
    return jsonify({
        'status': 'running',
        'data_sources': {
            'yahoo': system_state['yahoo'],
            'alpha_vantage': system_state['alpha_vantage'],
            'current': 'yahoo' if system_state['yahoo'] == 'available' else 'alpha_vantage',
            'last_switch': None
        },
        'ml_ready': bool(system_state['trained_models']),
        'mcp_ready': False,
        'sentiment_ready': False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def fetch_data():
    """Fetch REAL stock data only - no mock data"""
    if request.method == 'OPTIONS':
        return '', 204
    
    if not YF_AVAILABLE:
        return jsonify({'error': 'yfinance not installed. Run: pip install yfinance'}), 503
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    period = data.get('period', '1y')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    print(f"\n{'='*60}")
    print(f"Fetching REAL data for: {symbol}")
    print(f"Period: {period}")
    
    # Handle Australian stocks
    symbols_to_try = []
    if '.' not in symbol:
        # US stock first
        symbols_to_try.append(symbol)
        # Common Australian stocks
        aus_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'TLS', 'FMG', 'RIO', 'MQG']
        if symbol in aus_stocks:
            symbols_to_try.insert(0, f"{symbol}.AX")
        else:
            symbols_to_try.append(f"{symbol}.AX")
    else:
        symbols_to_try.append(symbol)
    
    # Try Yahoo Finance
    for test_symbol in symbols_to_try:
        try:
            print(f"Trying Yahoo Finance: {test_symbol}")
            ticker = yf.Ticker(test_symbol)
            hist = ticker.history(period=period)
            
            if hist is not None and len(hist) > 0:
                print(f"✅ SUCCESS: Got {len(hist)} days of REAL data")
                
                # Get real info
                info = ticker.info
                company_name = info.get('longName', info.get('shortName', test_symbol))
                currency = info.get('currency', 'USD')
                
                # Update state
                system_state['yahoo'] = 'available'
                system_state['last_fetch'][symbol] = {
                    'symbol': test_symbol,
                    'price': float(hist['Close'].iloc[-1]),
                    'time': datetime.now().isoformat()
                }
                
                # Return REAL data
                return jsonify({
                    'symbol': test_symbol,
                    'company_name': company_name,
                    'currency': currency,
                    'source': 'yahoo_real',
                    'data_points': len(hist),
                    'start_date': hist.index[0].strftime('%Y-%m-%d'),
                    'end_date': hist.index[-1].strftime('%Y-%m-%d'),
                    'latest_price': float(hist['Close'].iloc[-1]),
                    'prices': hist['Close'].tolist(),
                    'dates': [d.strftime('%Y-%m-%d') for d in hist.index],
                    'volume': hist['Volume'].tolist(),
                    'high': hist['High'].tolist(),
                    'low': hist['Low'].tolist(),
                    'open': hist['Open'].tolist(),
                    'is_real_data': True
                })
        except Exception as e:
            print(f"❌ Failed: {e}")
            system_state['yahoo'] = 'error'
    
    # Try Alpha Vantage as backup
    if ALPHA_VANTAGE_API_KEY:
        try:
            print(f"Trying Alpha Vantage for {symbol}...")
            from alpha_vantage_fetcher import AlphaVantageDataFetcher
            av = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
            av_data = av.fetch_daily_adjusted(symbol)
            
            if av_data is not None and len(av_data) > 0:
                print(f"✅ SUCCESS: Got {len(av_data)} days from Alpha Vantage")
                system_state['alpha_vantage'] = 'available'
                
                return jsonify({
                    'symbol': symbol,
                    'source': 'alpha_vantage_real',
                    'data_points': len(av_data),
                    'start_date': av_data.index[0].strftime('%Y-%m-%d'),
                    'end_date': av_data.index[-1].strftime('%Y-%m-%d'),
                    'latest_price': float(av_data['Close'].iloc[-1]),
                    'prices': av_data['Close'].tolist(),
                    'dates': [d.strftime('%Y-%m-%d') for d in av_data.index],
                    'volume': av_data['Volume'].tolist(),
                    'is_real_data': True
                })
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
            system_state['alpha_vantage'] = 'error'
    
    # No data available - return honest error
    return jsonify({
        'error': f'Could not fetch real data for {symbol}',
        'tried': symbols_to_try,
        'suggestions': [
            'Try US stocks: AAPL, MSFT, GOOGL, AMZN, TSLA',
            'Try Australian stocks: CBA.AX, BHP.AX, CSL.AX',
            'Check your internet connection',
            'Yahoo Finance may be temporarily unavailable'
        ]
    }), 404

@app.route('/api/train', methods=['POST', 'OPTIONS'])
def train_model():
    """Train model with REAL data only"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    model_type = data.get('model_type', 'random_forest')
    
    if not symbol:
        return jsonify({'error': 'Symbol required for training'}), 400
    
    # Check if we have recent data for this symbol
    if symbol not in system_state['last_fetch']:
        return jsonify({
            'error': f'No data available for {symbol}. Please fetch data first.',
            'message': 'Use the Market Data tab to fetch real data before training'
        }), 400
    
    print(f"\nTraining {model_type} with REAL data for {symbol}")
    
    # Store training info (we're not actually training without the full ML module)
    system_state['trained_models'][symbol] = {
        'model_type': model_type,
        'trained_at': datetime.now().isoformat(),
        'last_price': system_state['last_fetch'][symbol]['price']
    }
    
    return jsonify({
        'status': 'success',
        'symbol': symbol,
        'model_type': model_type,
        'message': 'Model marked as trained. Full ML implementation requires ml_stock_predictor.py',
        'last_known_price': system_state['last_fetch'][symbol]['price']
    })

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Predictions require real trained model"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    days = data.get('days', 5)
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    if symbol not in system_state['trained_models']:
        return jsonify({
            'error': f'No trained model for {symbol}',
            'message': 'Please train a model first using real data'
        }), 400
    
    # Get last known real price
    last_price = system_state['trained_models'][symbol].get('last_price', 0)
    
    if last_price == 0:
        return jsonify({'error': 'No price data available for predictions'}), 400
    
    # Without full ML implementation, we can't make real predictions
    return jsonify({
        'status': 'partial',
        'symbol': symbol,
        'days': days,
        'current_price': last_price,
        'message': 'Real predictions require full ML implementation with trained models',
        'note': 'This server only handles real data fetching. Predictions need ml_stock_predictor.py'
    })

@app.route('/api/backtest', methods=['POST', 'OPTIONS'])
def backtest():
    """Backtesting requires real historical data"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    
    if symbol not in system_state['last_fetch']:
        return jsonify({
            'error': 'No historical data available',
            'message': 'Fetch real data first before backtesting'
        }), 400
    
    return jsonify({
        'status': 'partial',
        'symbol': symbol,
        'message': 'Backtesting requires full ML implementation',
        'note': 'Real backtesting needs historical data and trained models'
    })

@app.route('/api/mcp/tools')
def mcp_tools():
    """MCP status"""
    return jsonify({
        'available': False,
        'message': 'MCP requires full system implementation'
    })

def main():
    """Start server"""
    print("\n" + "="*60)
    print("🚀 REAL DATA ONLY SERVER")
    print("="*60)
    print("✅ NO mock/demo/simulated data")
    print("✅ Only returns REAL market data")
    print("✅ Honest error messages when data unavailable")
    print(f"✅ API Key: {ALPHA_VANTAGE_API_KEY[:8]}...")
    print("="*60)
    print("\n📊 Open: http://localhost:8000")
    print("📊 Fetch real data for: AAPL, MSFT, CBA.AX, BHP.AX\n")
    
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()