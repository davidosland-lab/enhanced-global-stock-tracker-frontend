#!/usr/bin/env python3
"""
Real Data Only - Yahoo Finance + Alpha Vantage
NO FAKE/DEMO/MOCK DATA
"""

import os
import sys
import json
import warnings
import requests
warnings.filterwarnings('ignore')

os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Your Alpha Vantage Key
ALPHA_VANTAGE_KEY = '68ZFANK047DL0KSR'

def fetch_from_alpha_vantage(symbol):
    """Fetch REAL data from Alpha Vantage"""
    try:
        print(f"Fetching {symbol} from Alpha Vantage...")
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol.replace('.AX', ''),  # Remove .AX for Alpha Vantage
            'apikey': ALPHA_VANTAGE_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Alpha Vantage error: {data['Error Message']}")
            return None
            
        if 'Time Series (Daily)' not in data:
            print(f"No data in Alpha Vantage response")
            return None
            
        time_series = data['Time Series (Daily)']
        
        # Convert to DataFrame
        df_data = []
        for date, values in list(time_series.items())[:90]:  # Get 90 days
            df_data.append({
                'Date': pd.to_datetime(date),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': float(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        print(f"Alpha Vantage returned {len(df)} rows of REAL data")
        return df
        
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
        return None

def clear_yfinance_cache():
    """Try to clear yfinance cache"""
    try:
        import shutil
        cache_dir = os.path.expanduser('~/.cache/py-yfinance')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("Cleared yfinance cache")
    except:
        pass

@app.route('/')
def home():
    return jsonify({
        'status': 'FinBERT Trading System - REAL DATA ONLY',
        'version': '3.0',
        'data_sources': {
            'primary': 'Yahoo Finance',
            'secondary': f'Alpha Vantage (Key: {ALPHA_VANTAGE_KEY[:8]}...)'
        },
        'endpoints': [
            '/api/stock/<symbol>',
            '/api/predict/<symbol>',
            '/api/sentiment/<symbol>'
        ]
    })

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """Get REAL stock data only"""
    try:
        print(f"\nFetching REAL data for {symbol}...")
        
        # Clear cache and try yfinance
        clear_yfinance_cache()
        data = yf.download(symbol, period='3mo', progress=False, threads=False)
        
        # If yfinance fails, try Alpha Vantage
        if data.empty:
            print(f"Yahoo Finance failed, trying Alpha Vantage with key {ALPHA_VANTAGE_KEY[:8]}...")
            data = fetch_from_alpha_vantage(symbol)
            
            if data is None or data.empty:
                # NO FAKE DATA - Return error
                return jsonify({
                    'error': f'No real data available for {symbol}',
                    'tried': ['Yahoo Finance', 'Alpha Vantage'],
                    'message': 'Both data sources failed. Please check internet connection or try again later.'
                }), 404
        
        # Process REAL data
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # Calculate REAL indicators from REAL data
        close_prices = data['Close'].values
        
        # RSI calculation from REAL prices
        def calculate_rsi(prices, period=14):
            if len(prices) < period:
                return 50.0
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        rsi = calculate_rsi(close_prices)
        
        # MACD from REAL prices
        if len(close_prices) >= 26:
            exp1 = pd.Series(close_prices).ewm(span=12, adjust=False).mean()
            exp2 = pd.Series(close_prices).ewm(span=26, adjust=False).mean()
            macd = exp1.iloc[-1] - exp2.iloc[-1]
            signal = (exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1]
        else:
            macd = signal = 0
        
        # Return REAL data
        response = {
            'symbol': symbol,
            'price': float(latest['Close']),
            'change': float(latest['Close'] - prev['Close']),
            'changePercent': float((latest['Close'] - prev['Close']) / prev['Close'] * 100) if prev['Close'] != 0 else 0,
            'volume': int(latest['Volume']),
            'open': float(latest['Open']),
            'high': float(latest['High']),
            'low': float(latest['Low']),
            'previousClose': float(prev['Close']),
            'marketCap': 0,  # Would require additional API
            'pe': 0,  # Would require additional API
            'high52': float(data['High'].max()),
            'low52': float(data['Low'].min()),
            'indicators': {
                'RSI': round(rsi, 2),
                'MACD': round(macd, 4),
                'Signal': round(signal, 4),
                'SMA20': round(data['Close'].rolling(20).mean().iloc[-1], 2) if len(data) >= 20 else float(latest['Close']),
                'EMA20': round(data['Close'].ewm(span=20).mean().iloc[-1], 2) if len(data) >= 20 else float(latest['Close'])
            },
            'chartData': [],
            'data_source': 'REAL Market Data'
        }
        
        # Add REAL chart data
        chart_data = data.tail(30)
        for idx, row in chart_data.iterrows():
            response['chartData'].append({
                'date': idx.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        print(f"Returning {len(response['chartData'])} days of REAL data")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch real data'
        }), 500

@app.route('/api/predict/<symbol>')
def predict(symbol):
    """Prediction based on REAL data only"""
    try:
        # Get REAL current price
        data = yf.download(symbol, period='1mo', progress=False)
        if data.empty:
            data = fetch_from_alpha_vantage(symbol)
        
        if data is None or data.empty:
            return jsonify({'error': 'No real data for prediction'}), 404
        
        current_price = float(data['Close'].iloc[-1])
        
        # Calculate prediction based on REAL technical indicators
        close_prices = data['Close'].values
        
        # Simple trend analysis from REAL data
        sma_20 = data['Close'].rolling(20).mean().iloc[-1] if len(data) >= 20 else current_price
        trend = 'up' if current_price > sma_20 else 'down'
        
        # Confidence based on REAL volatility
        volatility = data['Close'].pct_change().std()
        confidence = max(0.5, min(0.85, 1 - volatility * 10))
        
        # Target based on REAL historical moves
        avg_move = abs(data['Close'].pct_change().mean())
        if trend == 'up':
            target = current_price * (1 + avg_move * 5)
        else:
            target = current_price * (1 - avg_move * 5)
        
        return jsonify({
            'symbol': symbol,
            'currentPrice': round(current_price, 2),
            'prediction': trend.upper(),
            'targetPrice': round(target, 2),
            'confidence': round(confidence * 100, 1),
            'changePercent': round((target - current_price) / current_price * 100, 2),
            'modelType': 'Technical Analysis (Real Data)',
            'data_points': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<symbol>')
def sentiment(symbol):
    """Sentiment based on REAL price action"""
    try:
        # Get REAL data
        data = yf.download(symbol, period='1mo', progress=False)
        if data.empty:
            data = fetch_from_alpha_vantage(symbol)
        
        if data is None or data.empty:
            return jsonify({'error': 'No real data for sentiment'}), 404
        
        # Calculate sentiment from REAL price momentum
        returns = data['Close'].pct_change()
        recent_return = returns.tail(5).mean()
        
        if recent_return > 0.01:
            label = 'Bullish'
            sentiment_value = min(1.0, recent_return * 10)
        elif recent_return < -0.01:
            label = 'Bearish'
            sentiment_value = max(-1.0, recent_return * 10)
        else:
            label = 'Neutral'
            sentiment_value = recent_return * 10
        
        return jsonify({
            'symbol': symbol,
            'sentiment': round(sentiment_value, 3),
            'label': label,
            'based_on': 'Real price momentum',
            'data_points': len(data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FinBERT Trading System - REAL DATA ONLY")
    print("="*60)
    print("NO FAKE/DEMO/MOCK DATA")
    print(f"Alpha Vantage Key: {ALPHA_VANTAGE_KEY[:8]}...")
    print("\nData sources:")
    print("  1. Yahoo Finance (primary)")
    print("  2. Alpha Vantage (secondary)")
    print("  If both fail, returns error - NO FAKE DATA")
    print("="*60)
    print("\nStarting server on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)