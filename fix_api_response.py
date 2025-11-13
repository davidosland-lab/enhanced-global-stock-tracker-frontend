#!/usr/bin/env python3
"""
Quick patch to fix the API response format issue
Run this INSTEAD of app_finbert_complete_v3.2.py
"""

import os
import sys
import json
import urllib.request
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the HTML interface"""
    try:
        for html_file in ['finbert_charts_complete.html', 'finbert_charts_v3.3_fixed.html']:
            if os.path.exists(html_file):
                with open(html_file, 'r') as f:
                    return f.read()
        return "<h1>HTML interface not found</h1>", 404
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with CORRECT field names"""
    try:
        interval = request.args.get('interval', '1d')
        period = request.args.get('period', '1m')
        
        print(f"API request for {symbol} - interval: {interval}, period: {period}")
        
        # Fetch from Yahoo
        if interval == '3m':
            interval = '5m'  # Yahoo doesn't support 3m
        
        range_map = {'1d': '5d', '5d': '5d', '1m': '1mo', '3m': '3mo', '6m': '6mo', '1y': '1y'}
        range_str = range_map.get(period, '1mo')
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_str}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        if 'chart' not in data or 'result' not in data['chart']:
            return jsonify({'error': 'Invalid response from Yahoo'}), 404
        
        result = data['chart']['result'][0]
        meta = result.get('meta', {})
        
        # Get current price
        current_price = meta.get('regularMarketPrice', 0)
        prev_close = meta.get('chartPreviousClose', meta.get('previousClose', current_price))
        
        # If current price is 0, get from last data point
        if current_price == 0:
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            closes = quote.get('close', [])
            for i in range(len(closes) - 1, -1, -1):
                if closes[i] is not None and closes[i] > 0:
                    current_price = closes[i]
                    break
        
        # Build chart data
        chart_data = []
        timestamps = result.get('timestamp', [])
        indicators = result.get('indicators', {})
        quote = indicators.get('quote', [{}])[0]
        
        if timestamps and quote:
            closes = quote.get('close', [])
            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            volumes = quote.get('volume', [])
            
            for i in range(len(timestamps)):
                if i < len(closes) and closes[i] is not None:
                    if interval == '1d':
                        date_str = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                        chart_data.append({
                            'date': date_str,
                            'timestamp': date_str,
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) and volumes[i] else 0
                        })
                    else:
                        chart_data.append({
                            'timestamp': timestamps[i] * 1000,
                            'date': datetime.fromtimestamp(timestamps[i]).isoformat(),
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) and volumes[i] else 0
                        })
        
        # Return with CORRECT field names
        response = {
            'symbol': symbol.upper(),
            'current_price': current_price,  # This was missing!
            'price_change': current_price - prev_close if prev_close else 0,
            'price_change_percent': ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
            'volume': meta.get('regularMarketVolume', 0),
            'day_high': meta.get('regularMarketDayHigh', current_price),
            'day_low': meta.get('regularMarketDayLow', current_price),
            'chart_data': chart_data,
            'interval': interval,
            'period': period,
            
            # Add these so frontend doesn't error
            'indicators': {
                'rsi': 50.0,
                'sma_20': current_price,
                'vwap': current_price
            },
            'economic_indicators': {},
            'ml_prediction': None,
            'sentiment_analysis': None,
            'news': []
        }
        
        print(f"Returning price: ${current_price} for {symbol}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': 'api-fix'}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("FinBERT API FIX - Starting...")
    print("This fixes the missing current_price field")
    print("=" * 60)
    print("Access at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)