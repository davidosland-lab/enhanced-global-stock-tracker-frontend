#!/usr/bin/env python3
"""
Simple test server to verify basic functionality
"""

import os
import sys

# Set environment
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

print("="*60)
print("SIMPLE TEST SERVER")
print("="*60)

try:
    print("Importing Flask...")
    from flask import Flask, jsonify
    from flask_cors import CORS
    print("✓ Flask imported successfully")
    
    print("Importing yfinance...")
    import yfinance as yf
    print("✓ yfinance imported successfully")
    
    print("Importing pandas...")
    import pandas as pd
    print("✓ pandas imported successfully")
    
    print("Importing numpy...")
    import numpy as np
    print("✓ numpy imported successfully")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install missing packages:")
    print("pip install flask flask-cors yfinance pandas numpy")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Create simple Flask app
app = Flask(__name__)
CORS(app)

# Alpha Vantage key
ALPHA_VANTAGE_KEY = '68ZFANK047DL0KSR'

@app.route('/')
def home():
    return jsonify({
        'status': 'Server is running',
        'endpoints': ['/api/stock/<symbol>', '/api/test']
    })

@app.route('/api/test')
def test():
    return jsonify({'message': 'API is working', 'timestamp': pd.Timestamp.now().isoformat()})

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        print(f"Fetching {symbol}...")
        
        # Try to fetch data using yfinance download (bypasses cache)
        data = yf.download(symbol, period='5d', progress=False)
        
        if data.empty:
            return jsonify({'error': f'No data for {symbol}'}), 404
        
        latest = data.iloc[-1]
        
        return jsonify({
            'symbol': symbol,
            'price': float(latest['Close']),
            'open': float(latest['Open']),
            'high': float(latest['High']),
            'low': float(latest['Low']),
            'volume': int(latest['Volume']),
            'date': data.index[-1].strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting simple test server...")
    print("Server URL: http://localhost:5000")
    print("Test endpoints:")
    print("  http://localhost:5000/")
    print("  http://localhost:5000/api/test")
    print("  http://localhost:5000/api/stock/AAPL")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"\nError starting server: {e}")
        input("\nPress Enter to exit...")