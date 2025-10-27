"""
FinBERT Ultimate Trading System - API Server
Fixed version with proper REST API endpoints for charts
"""

import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

# Import the main FinBERT application
from app_finbert_ultimate import (
    TradingModel, 
    DataFetcher,
    app as original_app,
    FINBERT_AVAILABLE
)

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import yfinance as yf
import numpy as np

# Create new Flask app with proper API routes
app = Flask(__name__)
CORS(app, origins=['*'])

# Initialize trading model
trading_model = TradingModel()

# Simple HTML template for root
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FinBERT Ultimate API</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 50px auto; 
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        h1 { color: #4299e1; }
        .endpoint { 
            background: #2a2a2a; 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 5px;
            border-left: 3px solid #4299e1;
        }
        code { 
            background: #333; 
            padding: 2px 5px; 
            border-radius: 3px; 
            color: #4299e1;
        }
    </style>
</head>
<body>
    <h1>🚀 FinBERT Ultimate Trading System API</h1>
    <p>Version 3.0 - REST API Server</p>
    
    <h2>Available Endpoints:</h2>
    
    <div class="endpoint">
        <strong>GET /api/stock/{symbol}</strong><br>
        Get current stock data and technical indicators
    </div>
    
    <div class="endpoint">
        <strong>GET /api/predict/{symbol}</strong><br>
        Get AI prediction for a stock (auto-trains if needed)
    </div>
    
    <div class="endpoint">
        <strong>POST /api/train</strong><br>
        Train a new model<br>
        Body: <code>{"symbol": "AAPL", "period": "6mo"}</code>
    </div>
    
    <div class="endpoint">
        <strong>GET /api/historical/{symbol}</strong><br>
        Get historical data<br>
        Query params: <code>?period=1mo&interval=1d</code>
    </div>
    
    <div class="endpoint">
        <strong>GET /api/news/{symbol}</strong><br>
        Get news and sentiment for a symbol
    </div>
    
    <div class="endpoint">
        <strong>GET /api/economic</strong><br>
        Get economic indicators
    </div>
    
    <div class="endpoint">
        <strong>GET /status</strong><br>
        Check server status
    </div>
    
    <p><strong>FinBERT Status:</strong> ''' + ('✅ Enabled' if FINBERT_AVAILABLE else '❌ Disabled (using fallback)') + '''</p>
</body>
</html>
'''

# Root endpoint
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API endpoint
@app.route('/api')
def api_info():
    return jsonify({
        'name': 'FinBERT Ultimate Trading System API',
        'version': '3.0',
        'finbert_enabled': FINBERT_AVAILABLE,
        'endpoints': [
            '/api/stock/{symbol}',
            '/api/predict/{symbol}',
            '/api/train',
            '/api/historical/{symbol}',
            '/api/news/{symbol}',
            '/api/economic'
        ]
    })

# Status endpoint
@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'finbert': FINBERT_AVAILABLE,
        'models_loaded': len(trading_model.models),
        'numpy_version': np.__version__,
        'python_version': sys.version
    })

# Get stock data
@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        symbol = symbol.upper()
        
        # Fetch stock data using yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current data
        history = ticker.history(period="5d")
        if history.empty:
            return jsonify({'error': f'No data found for symbol {symbol}'})
        
        current_price = history['Close'].iloc[-1]
        previous_close = history['Close'].iloc[-2] if len(history) > 1 else current_price
        
        # Calculate technical indicators
        history_month = ticker.history(period="1mo")
        if not history_month.empty:
            closes = history_month['Close'].values
            
            # Calculate indicators
            rsi = calculate_rsi(closes) if len(closes) >= 14 else None
            sma_20 = closes[-20:].mean() if len(closes) >= 20 else None
            
            # Calculate ATR
            highs = history_month['High'].values
            lows = history_month['Low'].values
            atr = calculate_atr(highs, lows, closes) if len(closes) >= 14 else None
        else:
            rsi = sma_20 = atr = None
        
        # Prepare response
        response = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'currentPrice': float(current_price),
            'price': float(current_price),
            'previousClose': float(previous_close),
            'change': float(current_price - previous_close),
            'changePercent': float((current_price - previous_close) / previous_close * 100) if previous_close else 0,
            'volume': int(history['Volume'].iloc[-1]),
            'averageVolume': int(info.get('averageVolume', 0)),
            'marketCap': info.get('marketCap', 0),
            'rsi_14': float(rsi) if rsi else None,
            'sma_20': float(sma_20) if sma_20 else None,
            'atr_14': float(atr) if atr else None,
            'high': float(history['High'].iloc[-1]),
            'low': float(history['Low'].iloc[-1]),
            'open': float(history['Open'].iloc[-1])
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error fetching stock {symbol}: {str(e)}")
        return jsonify({'error': str(e)})

# Get prediction
@app.route('/api/predict/<symbol>')
def get_prediction(symbol):
    try:
        symbol = symbol.upper()
        
        # Check if model exists, train if not
        if symbol not in trading_model.models:
            print(f"No model for {symbol}, training now...")
            train_result = trading_model.train(symbol, period="6mo")
            if 'error' in train_result:
                return jsonify(train_result)
        
        # Get prediction
        result = trading_model.predict(symbol)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error predicting {symbol}: {str(e)}")
        return jsonify({'error': str(e)})

# Train model (POST)
@app.route('/api/train', methods=['POST'])
def train_model():
    try:
        data = request.json or {}
        symbol = data.get('symbol', '').upper()
        period = data.get('period', '6mo')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'})
        
        result = trading_model.train(symbol, period)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Get historical data
@app.route('/api/historical/<symbol>')
def get_historical(symbol):
    try:
        symbol = symbol.upper()
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            return jsonify({'error': f'No historical data for {symbol}'})
        
        # Convert to list of dicts
        data = []
        for date, row in history.iterrows():
            data.append({
                'date': date.isoformat(),
                'Date': date.isoformat(),
                'open': float(row['Open']),
                'Open': float(row['Open']),
                'high': float(row['High']),
                'High': float(row['High']),
                'low': float(row['Low']),
                'Low': float(row['Low']),
                'close': float(row['Close']),
                'Close': float(row['Close']),
                'volume': int(row['Volume']),
                'Volume': int(row['Volume'])
            })
        
        return jsonify({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': data
        })
        
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)})

# Get news
@app.route('/api/news/<symbol>')
def get_news(symbol):
    try:
        symbol = symbol.upper()
        
        # Get news from data fetcher
        news = trading_model.fetcher.fetch_news_sentiment(symbol)
        
        # Format news items
        items = []
        for article in news[:10]:  # Limit to 10 items
            items.append({
                'title': article.get('title', ''),
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'publisher': article.get('source', ''),
                'sentiment': article.get('sentiment', 0)
            })
        
        return jsonify({
            'symbol': symbol,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        print(f"Error fetching news for {symbol}: {str(e)}")
        return jsonify({'error': str(e), 'items': []})

# Get economic indicators
@app.route('/api/economic')
def get_economic():
    try:
        indicators = trading_model.fetcher.get_economic_indicators()
        return jsonify({'indicators': indicators})
    except Exception as e:
        return jsonify({'error': str(e), 'indicators': {}})

# Helper functions
def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    if len(prices) < period:
        return None
    
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    
    if down == 0:
        return 100
    
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(highs, lows, closes, period=14):
    """Calculate Average True Range"""
    if len(highs) < period + 1:
        return None
    
    tr_list = []
    for i in range(1, len(highs)):
        hl = highs[i] - lows[i]
        hc = abs(highs[i] - closes[i-1])
        lc = abs(lows[i] - closes[i-1])
        tr = max(hl, hc, lc)
        tr_list.append(tr)
    
    if len(tr_list) >= period:
        return np.mean(tr_list[-period:])
    return None

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  FinBERT Ultimate Trading System - API Server v3.0")
    print("="*60)
    print(f"\nFinBERT Status: {'ENABLED' if FINBERT_AVAILABLE else 'DISABLED (using fallback)'}")
    print(f"NumPy Version: {np.__version__}")
    print(f"Python Version: {sys.version.split()[0]}")
    print("\nStarting server on http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /api/stock/{symbol}     - Get stock data")
    print("  GET  /api/predict/{symbol}   - Get prediction")
    print("  POST /api/train              - Train model")
    print("  GET  /api/historical/{symbol} - Get historical data")
    print("  GET  /api/news/{symbol}      - Get news")
    print("  GET  /api/economic           - Get economic indicators")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)