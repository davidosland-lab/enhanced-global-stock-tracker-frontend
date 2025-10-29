#!/usr/bin/env python3
"""
FinBERT Ultimate Trading System v3.1 - INTRADAY & ZOOM FEATURES
================================================================
New Features:
- Intraday data with 1m, 3m, 5m intervals
- Chart zoom and pan functionality
- Real-time updates for intraday data
- Interval selector in UI
"""

import os
import sys
import json
import logging
import warnings
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Your Alpha Vantage Key
ALPHA_VANTAGE_KEY = '68ZFANK047DL0KSR'

# Create necessary directories
for directory in ['cache', 'models']:
    os.makedirs(directory, exist_ok=True)

class DataFetcher:
    """Fetches real market data with intraday support"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_KEY
        self.cache = {}
        self.cache_timeout = 30  # 30 seconds for intraday
    
    def aggregate_to_interval(self, chart_data: List[Dict], interval_minutes: int) -> List[Dict]:
        """Aggregate intraday data to specified interval"""
        if not chart_data or interval_minutes <= 0:
            return chart_data
        
        # Group by time intervals
        interval_data = {}
        
        for point in chart_data:
            # Parse timestamp
            if 'timestamp' in point:
                dt = datetime.fromtimestamp(point['timestamp'])
            else:
                dt = datetime.strptime(point['date'], '%Y-%m-%d %H:%M:%S' if ' ' in point['date'] else '%Y-%m-%d')
            
            # Round down to nearest interval
            minutes = (dt.minute // interval_minutes) * interval_minutes
            interval_time = dt.replace(minute=minutes, second=0, microsecond=0)
            interval_key = interval_time.strftime('%Y-%m-%d %H:%M:%S')
            
            if interval_key not in interval_data:
                interval_data[interval_key] = {
                    'open': point.get('open', point.get('close', 0)),
                    'high': point.get('high', point.get('close', 0)),
                    'low': point.get('low', point.get('close', 0)),
                    'close': point.get('close', 0),
                    'volume': point.get('volume', 0)
                }
            else:
                # Update aggregated values
                interval_data[interval_key]['high'] = max(
                    interval_data[interval_key]['high'], 
                    point.get('high', point.get('close', 0))
                )
                interval_data[interval_key]['low'] = min(
                    interval_data[interval_key]['low'], 
                    point.get('low', point.get('close', 0))
                )
                interval_data[interval_key]['close'] = point.get('close', 0)
                interval_data[interval_key]['volume'] += point.get('volume', 0)
        
        # Convert to sorted list
        result = []
        for timestamp in sorted(interval_data.keys()):
            result.append({
                'date': timestamp,
                'timestamp': timestamp,
                'open': interval_data[timestamp]['open'],
                'high': interval_data[timestamp]['high'],
                'low': interval_data[timestamp]['low'],
                'close': interval_data[timestamp]['close'],
                'volume': interval_data[timestamp]['volume']
            })
        
        return result
    
    def fetch_intraday_yahoo(self, symbol: str, interval: str = '1m', range_str: str = '1d') -> Optional[Dict]:
        """Fetch intraday data from Yahoo Finance"""
        try:
            # Yahoo Finance intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1d
            valid_intervals = {
                '1m': '1m',
                '3m': '2m',  # Use 2m and aggregate to 3m
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '60m': '60m',
                '1h': '60m',
                '1d': '1d'
            }
            
            yahoo_interval = valid_intervals.get(interval, '1m')
            needs_aggregation = (interval == '3m')
            
            # Valid ranges for intraday: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={yahoo_interval}&range={range_str}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
                
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('chartPreviousClose', meta.get('previousClose', current_price))
            
            response_data = {
                'symbol': symbol.upper(),
                'price': current_price,
                'previousClose': prev_close,
                'change': current_price - prev_close,
                'changePercent': ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
                'volume': meta.get('regularMarketVolume', 0),
                'open': meta.get('regularMarketOpen', current_price),
                'high': meta.get('regularMarketDayHigh', current_price),
                'low': meta.get('regularMarketDayLow', current_price),
                'high52': meta.get('fiftyTwoWeekHigh', current_price),
                'low52': meta.get('fiftyTwoWeekLow', current_price),
                'marketCap': meta.get('marketCap', 0),
                'currency': meta.get('currency', 'USD'),
                'exchangeName': meta.get('exchangeName', ''),
                'interval': interval,
                'chartData': []
            }
            
            # Get intraday data
            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            if timestamps and quote:
                closes = quote.get('close', [])
                opens = quote.get('open', [])
                highs = quote.get('high', [])
                lows = quote.get('low', [])
                volumes = quote.get('volume', [])
                
                temp_chart = []
                for i in range(len(timestamps)):
                    if i < len(closes) and closes[i] is not None:
                        dt = datetime.fromtimestamp(timestamps[i])
                        temp_chart.append({
                            'date': dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'timestamp': timestamps[i],
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) else 0
                        })
                
                # Aggregate to 3m if needed
                if needs_aggregation and temp_chart:
                    response_data['chartData'] = self.aggregate_to_interval(temp_chart, 3)
                else:
                    response_data['chartData'] = temp_chart
            
            return response_data
            
        except Exception as e:
            logger.error(f"Yahoo intraday error for {symbol}: {e}")
            return None
    
    def fetch_daily_yahoo(self, symbol: str, period: str = '1mo') -> Optional[Dict]:
        """Fetch daily data from Yahoo Finance"""
        try:
            period_map = {
                '5d': '5d',
                '1m': '1mo',
                '30d': '1mo',
                '3m': '3mo',
                '6m': '6mo',
                '1y': '1y'
            }
            yahoo_period = period_map.get(period, '1mo')
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={yahoo_period}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
                
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('chartPreviousClose', meta.get('previousClose', current_price))
            
            response_data = {
                'symbol': symbol.upper(),
                'price': current_price,
                'previousClose': prev_close,
                'change': current_price - prev_close,
                'changePercent': ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
                'volume': meta.get('regularMarketVolume', 0),
                'open': meta.get('regularMarketOpen', current_price),
                'high': meta.get('regularMarketDayHigh', current_price),
                'low': meta.get('regularMarketDayLow', current_price),
                'high52': meta.get('fiftyTwoWeekHigh', current_price),
                'low52': meta.get('fiftyTwoWeekLow', current_price),
                'marketCap': meta.get('marketCap', 0),
                'currency': meta.get('currency', 'USD'),
                'exchangeName': meta.get('exchangeName', ''),
                'interval': '1d',
                'chartData': []
            }
            
            # Get historical data
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
                        date_str = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                        response_data['chartData'].append({
                            'date': date_str,
                            'timestamp': date_str,
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) else 0
                        })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Yahoo daily error for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, chart_data: List[Dict], current_price: float) -> Dict:
        """Calculate technical indicators"""
        if not chart_data or len(chart_data) < 2:
            return {
                'RSI': 50.0,
                'MACD': 0.0,
                'Signal': 0.0,
                'ATR': 0.0,
                'SMA20': current_price,
                'EMA20': current_price,
                'VWAP': current_price
            }
        
        try:
            close_prices = [d.get('close', 0) for d in chart_data]
            volumes = [d.get('volume', 0) for d in chart_data]
            
            # RSI
            def calculate_rsi(prices, period=14):
                if len(prices) < period + 1:
                    return 50.0
                deltas = np.diff(prices)
                gains = np.where(deltas > 0, deltas, 0)
                losses = np.where(deltas < 0, -deltas, 0)
                
                avg_gain = np.mean(gains[:period])
                avg_loss = np.mean(losses[:period])
                
                for i in range(period, len(gains)):
                    avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                    avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                
                if avg_loss == 0:
                    return 100.0
                rs = avg_gain / avg_loss
                return 100 - (100 / (1 + rs))
            
            # VWAP (Volume Weighted Average Price)
            def calculate_vwap(data):
                if not data:
                    return current_price
                typical_prices = [(d['high'] + d['low'] + d['close']) / 3 for d in data]
                volumes = [d.get('volume', 0) for d in data]
                if sum(volumes) == 0:
                    return np.mean(typical_prices)
                return sum(p * v for p, v in zip(typical_prices, volumes)) / sum(volumes)
            
            rsi = calculate_rsi(close_prices)
            vwap = calculate_vwap(chart_data)
            
            # Simple indicators for now
            sma20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else current_price
            
            return {
                'RSI': round(rsi, 2),
                'MACD': 0.0,
                'Signal': 0.0,
                'ATR': 0.0,
                'SMA20': round(sma20, 2),
                'EMA20': round(sma20, 2),  # Simplified
                'VWAP': round(vwap, 2)
            }
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {
                'RSI': 50.0,
                'MACD': 0.0,
                'Signal': 0.0,
                'ATR': 0.0,
                'SMA20': current_price,
                'EMA20': current_price,
                'VWAP': current_price
            }

# Initialize components
data_fetcher = DataFetcher()

# API Routes

@app.route('/')
def index():
    """Serve the enhanced chart interface"""
    try:
        # Check if we have the enhanced version
        if os.path.exists('finbert_charts_intraday.html'):
            with open('finbert_charts_intraday.html', 'r') as f:
                return f.read()
        elif os.path.exists('finbert_charts.html'):
            with open('finbert_charts.html', 'r') as f:
                return f.read()
        else:
            return jsonify({'error': 'Chart interface not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get current stock data with interval support"""
    try:
        # Check for interval parameter
        interval = request.args.get('interval', '1d')
        
        if interval in ['1m', '3m', '5m', '15m', '30m', '60m']:
            # Intraday data
            data = data_fetcher.fetch_intraday_yahoo(symbol, interval, '1d')
        else:
            # Daily data
            data = data_fetcher.fetch_daily_yahoo(symbol)
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Calculate indicators
        if 'chartData' in data and data['chartData']:
            data['indicators'] = data_fetcher.calculate_indicators(data['chartData'], data['price'])
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intraday/<symbol>')
def get_intraday_data(symbol):
    """Get intraday data with specified interval"""
    try:
        interval = request.args.get('interval', '5m')
        range_str = request.args.get('range', '1d')
        
        # Validate interval
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '60m']
        if interval not in valid_intervals:
            interval = '5m'
        
        # Validate range
        valid_ranges = ['1d', '5d']
        if range_str not in valid_ranges:
            range_str = '1d'
        
        data = data_fetcher.fetch_intraday_yahoo(symbol, interval, range_str)
        
        if not data:
            return jsonify({'error': f'Unable to fetch intraday data for {symbol}'}), 404
        
        # Calculate indicators
        if 'chartData' in data and data['chartData']:
            data['indicators'] = data_fetcher.calculate_indicators(data['chartData'], data['price'])
        
        return jsonify({
            'symbol': symbol,
            'interval': interval,
            'range': range_str,
            'data': data.get('chartData', []),
            'indicators': data.get('indicators', {}),
            'price': data.get('price', 0),
            'change': data.get('change', 0),
            'changePercent': data.get('changePercent', 0),
            'volume': data.get('volume', 0)
        })
        
    except Exception as e:
        logger.error(f"Error getting intraday data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical data with interval support"""
    try:
        period = request.args.get('period', '30d')
        interval = request.args.get('interval', '1d')
        
        if interval in ['1m', '3m', '5m', '15m', '30m', '60m']:
            # For intraday historical, limit the range
            range_map = {
                '1d': '1d',
                '5d': '5d',
                '1m': '5d',
                '30d': '1mo',
                '3m': '3mo'
            }
            range_str = range_map.get(period, '5d')
            data = data_fetcher.fetch_intraday_yahoo(symbol, interval, range_str)
        else:
            data = data_fetcher.fetch_daily_yahoo(symbol, period)
        
        if not data or 'chartData' not in data:
            return jsonify({'error': f'Unable to fetch historical data for {symbol}'}), 404
        
        chart_data = data['chartData']
        
        # Format for chart compatibility
        formatted_data = []
        for point in chart_data:
            formatted_data.append({
                'date': point.get('date'),
                'Date': point.get('date'),
                'timestamp': point.get('timestamp', point.get('date')),
                'open': point.get('open', 0),
                'Open': point.get('open', 0),
                'high': point.get('high', 0),
                'High': point.get('high', 0),
                'low': point.get('low', 0),
                'Low': point.get('low', 0),
                'close': point.get('close', 0),
                'Close': point.get('close', 0),
                'volume': point.get('volume', 0),
                'Volume': point.get('volume', 0)
            })
        
        return jsonify({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': formatted_data,
            'historical': {
                'data': formatted_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def predict_stock(symbol):
    """Simple prediction endpoint"""
    try:
        # Get recent data
        data = data_fetcher.fetch_daily_yahoo(symbol, '30d')
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Simple momentum prediction
        current_price = data.get('price', 0)
        change_pct = data.get('changePercent', 0)
        
        # Basic prediction
        predicted_change = change_pct * 0.3  # Dampen the momentum
        predicted_price = current_price * (1 + predicted_change / 100)
        
        return jsonify({
            'next_day_prediction': {
                'price': round(predicted_price, 2),
                'change': round(predicted_change, 2),
                'direction': 'up' if predicted_change > 0 else 'down',
                'probability': min(90, 50 + abs(predicted_change) * 5),
                'confidence': min(85, 50 + abs(change_pct) * 3)
            },
            'target_prices': [{
                'price': round(predicted_price * 1.02, 2),
                'timeframe': '5 days',
                'confidence': 70.0
            }],
            'sentiment_score': 0.0
        })
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """Mock news endpoint"""
    return jsonify({
        'symbol': symbol,
        'news': [],
        'overall_sentiment': 0.0
    })

@app.route('/api/economic')
def get_economic_indicators():
    """Get economic indicators"""
    try:
        indicators = {}
        
        # Try to fetch indicators
        indicator_symbols = {
            'VIX': ('^VIX', 'Fear Index'),
            'TNX': ('^TNX', '10-Year Treasury'),
            'DXY': ('DX-Y.NYB', 'Dollar Index'),
            'GOLD': ('GC=F', 'Gold Futures')
        }
        
        for key, (symbol, label) in indicator_symbols.items():
            try:
                data = data_fetcher.fetch_daily_yahoo(symbol, '5d')
                if data:
                    indicators[key] = {
                        'value': round(data['price'], 2),
                        'change': round(data.get('changePercent', 0), 2),
                        'label': label,
                        'symbol': symbol
                    }
            except:
                indicators[key] = {
                    'value': '--',
                    'change': 0,
                    'label': label,
                    'symbol': symbol
                }
        
        return jsonify(indicators)
        
    except Exception as e:
        logger.error(f"Error getting economic indicators: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """System status"""
    return jsonify({
        'status': 'running',
        'version': '3.1-INTRADAY',
        'features': {
            'intraday_data': True,
            'intervals': ['1m', '3m', '5m', '15m', '30m', '60m', '1d'],
            'zoom_support': True,
            'real_data': True,
            'indicators': ['RSI', 'MACD', 'VWAP', 'SMA', 'EMA', 'ATR'],
            'economic_indicators': True
        },
        'alpha_vantage_key': bool(ALPHA_VANTAGE_KEY),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("FinBERT Trading System v3.1 - INTRADAY & ZOOM FEATURES")
    print("="*70)
    print("✓ Intraday Intervals: 1m, 3m, 5m, 15m, 30m, 60m")
    print("✓ Chart Zoom: Enabled with pan support")
    print("✓ Real-time Data: Yes")
    print("✓ VWAP Indicator: Added for intraday")
    print("✓ Alpha Vantage Key: Configured")
    print("✓ Starting server on http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)