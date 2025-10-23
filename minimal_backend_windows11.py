#!/usr/bin/env python3
"""
Minimal Stock Tracker Backend for Windows 11
Version: 7.0 Minimal
Just copy this file and run it!
"""

import json
import logging
from datetime import datetime, timedelta

# Check for required packages
try:
    import yfinance as yf
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError as e:
    print("\n" + "="*60)
    print("ERROR: Required packages not installed!")
    print("="*60)
    print("\nPlease run the following command:")
    print("\npip install --user yfinance flask flask-cors")
    print("\nOr if pip is not recognized:")
    print("\npython -m pip install --user yfinance flask flask-cors")
    print("="*60 + "\n")
    exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# Simple cache dictionary
cache = {}
cache_timeout = 300  # 5 minutes

def get_cache(key):
    """Simple cache getter with timeout"""
    if key in cache:
        data, timestamp = cache[key]
        if (datetime.now() - timestamp).seconds < cache_timeout:
            return data
    return None

def set_cache(key, data):
    """Simple cache setter"""
    cache[key] = (data, datetime.now())

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "active",
        "message": "Stock Tracker Backend Running on Windows 11",
        "version": "7.0-minimal",
        "endpoints": [
            "/api/stock/{symbol} - Get stock data (e.g., /api/stock/AAPL)",
            "/api/indices - Get major market indices",
            "/api/test - Test Yahoo Finance connection"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test')
def test_connection():
    """Test Yahoo Finance connection"""
    try:
        # Try to fetch Apple stock as a test
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        return jsonify({
            "status": "success",
            "message": "Yahoo Finance connection working!",
            "test_stock": "AAPL",
            "price": info.get('regularMarketPrice', 'N/A')
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Yahoo Finance connection failed: {str(e)}"
        }), 500

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """Get stock data for a given symbol"""
    try:
        # Check cache first
        cache_key = f"stock_{symbol}"
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Returning cached data for {symbol}")
            return jsonify(cached)
        
        logger.info(f"Fetching data for {symbol}")
        
        # Fetch from Yahoo Finance
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get recent history for more accurate data
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            if len(hist) > 1:
                previous_close = float(hist['Close'].iloc[-2])
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                previous_close = info.get('regularMarketPreviousClose', current_price)
                change = 0
                change_percent = 0
        else:
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('regularMarketPreviousClose', current_price)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
        
        # Prepare response
        stock_data = {
            "symbol": symbol.upper(),
            "longName": info.get('longName', symbol.upper()),
            "price": round(current_price, 2),
            "previousClose": round(previous_close, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "dayHigh": info.get('dayHigh'),
            "dayLow": info.get('dayLow'),
            "volume": info.get('volume'),
            "marketCap": info.get('marketCap'),
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow'),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        set_cache(cache_key, stock_data)
        
        return jsonify(stock_data)
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return jsonify({
            "error": f"Failed to fetch data for {symbol}",
            "details": str(e)
        }), 500

@app.route('/api/indices')
def get_indices():
    """Get major market indices"""
    indices = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^FTSE": "FTSE 100",
        "^AORD": "ASX All Ord"
    }
    
    results = []
    
    for symbol, name in indices.items():
        try:
            # Check cache
            cache_key = f"index_{symbol}"
            cached = get_cache(cache_key)
            if cached:
                results.append(cached)
                continue
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                current = float(hist['Close'].iloc[-1])
                if len(hist) > 1:
                    previous = float(hist['Close'].iloc[-2])
                    change = current - previous
                    change_percent = (change / previous) * 100
                else:
                    change = 0
                    change_percent = 0
                
                index_data = {
                    "symbol": symbol,
                    "name": name,
                    "value": round(current, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2)
                }
                
                # Cache it
                set_cache(cache_key, index_data)
                results.append(index_data)
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            results.append({
                "symbol": symbol,
                "name": name,
                "error": "Failed to fetch"
            })
    
    return jsonify({
        "indices": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/historical/<symbol>')
def get_historical(symbol):
    """Get historical data for a symbol"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return jsonify({"error": "No data available"}), 404
        
        # Convert to simple format
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.isoformat(),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return jsonify({
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data
        })
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return jsonify({
            "error": f"Failed to fetch historical data for {symbol}",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print(" Stock Tracker Backend - Windows 11 Minimal Version")
    print("="*60)
    print(f" Starting server on http://localhost:8002")
    print(" Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Test Yahoo Finance connection
        print("Testing Yahoo Finance connection...")
        test = yf.Ticker("AAPL")
        test.info
        print("✅ Yahoo Finance connection successful!\n")
    except Exception as e:
        print(f"⚠️  Warning: Yahoo Finance test failed: {e}\n")
    
    print("Available endpoints:")
    print("  http://localhost:8002/")
    print("  http://localhost:8002/api/test")
    print("  http://localhost:8002/api/stock/AAPL")
    print("  http://localhost:8002/api/stock/CBA.AX")
    print("  http://localhost:8002/api/indices")
    print("  http://localhost:8002/api/historical/AAPL?period=1mo&interval=1d")
    print("\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=8002, debug=False)