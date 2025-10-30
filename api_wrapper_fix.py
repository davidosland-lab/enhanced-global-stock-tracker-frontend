#!/usr/bin/env python3
"""
API Wrapper - Fixes field name mismatches between backend and frontend
"""

from flask import Flask, request, jsonify
import urllib.request
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Proxy to backend"""
    try:
        response = urllib.request.urlopen('http://localhost:5001/')
        return response.read().decode('utf-8')
    except:
        return "Backend not running on port 5001", 503

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Wrap the backend API and fix field names"""
    try:
        # Get params
        interval = request.args.get('interval', '1d')
        period = request.args.get('period', '1m')
        
        # Call the original backend (running on port 5001)
        url = f'http://localhost:5001/api/stock/{symbol}?interval={interval}&period={period}'
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        
        # Fix field name mismatches
        # Backend returns 'price', frontend expects 'current_price'
        if 'price' in data and 'current_price' not in data:
            data['current_price'] = data['price']
        
        # Backend returns 'change', frontend expects 'price_change'
        if 'change' in data and 'price_change' not in data:
            data['price_change'] = data['change']
        
        # Backend returns 'changePercent', frontend expects 'price_change_percent'
        if 'changePercent' in data and 'price_change_percent' not in data:
            data['price_change_percent'] = data['changePercent']
        
        # Backend returns 'high', frontend expects 'day_high'
        if 'high' in data and 'day_high' not in data:
            data['day_high'] = data.get('high', data.get('price', 0))
        
        # Backend returns 'low', frontend expects 'day_low'
        if 'low' in data and 'day_low' not in data:
            data['day_low'] = data.get('low', data.get('price', 0))
        
        # Ensure chart_data exists
        if 'chartData' in data and 'chart_data' not in data:
            data['chart_data'] = data['chartData']
        
        # Add missing fields with defaults
        if 'indicators' not in data:
            data['indicators'] = {}
        
        if 'economic_indicators' not in data:
            data['economic_indicators'] = {}
        
        if 'ml_prediction' not in data:
            data['ml_prediction'] = None
        
        if 'sentiment_analysis' not in data:
            data['sentiment_analysis'] = None
        
        if 'news' not in data:
            data['news'] = []
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("API WRAPPER - Fixes field name mismatches")
    print("=" * 60)
    print("This wrapper:")
    print("1. Runs on port 5000 (what frontend expects)")
    print("2. Calls backend on port 5001")
    print("3. Fixes field name mismatches")
    print()
    print("To use:")
    print("1. Start original backend on port 5001:")
    print("   python app_finbert_complete_v3.2.py")
    print("   (Change port to 5001 in the file)")
    print()
    print("2. Start this wrapper on port 5000:")
    print("   python api_wrapper_fix.py")
    print("=" * 60)
    
    app.run(debug=True, port=5000)