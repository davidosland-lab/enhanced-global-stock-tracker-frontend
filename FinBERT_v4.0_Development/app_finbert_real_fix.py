#!/usr/bin/env python3
"""
FinBERT v3.3 - REAL FIX - No fake data, just better handling of Yahoo responses
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
import hashlib

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

ALPHA_VANTAGE_KEY = '68ZFANK047DL0KSR'

for directory in ['cache', 'models']:
    os.makedirs(directory, exist_ok=True)

class MarketDataFetcher:
    """Fetches REAL market data only"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_KEY
        self.cache_dir = 'cache'
    
    def fetch_yahoo_intraday(self, symbol: str, interval: str = '5m', range_str: str = '1d'):
        """Fetch intraday data from Yahoo Finance"""
        try:
            # Yahoo doesn't support 3m, use 1m and aggregate
            if interval == '3m':
                yahoo_interval = '1m'
                needs_aggregation = True
            else:
                yahoo_interval = interval
                needs_aggregation = False
            
            # Map intervals to appropriate ranges
            if interval in ['1m', '3m', '5m']:
                range_str = '1d'
            elif interval in ['15m', '30m']:
                range_str = '5d'
            else:
                range_str = '1mo'
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={yahoo_interval}&range={range_str}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            logger.info(f"Fetching: {url}")
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if 'chart' not in data or 'result' not in data['chart']:
                logger.error(f"Invalid Yahoo response structure for {symbol}")
                return None
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            # Get current price - if regularMarketPrice is 0 or missing, try to get from data
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
            
            # Extract chart data first to get actual prices
            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            # If current price is 0 or missing, get it from the last data point
            if current_price == 0 and quote:
                closes = quote.get('close', [])
                # Find last non-null close price
                for i in range(len(closes) - 1, -1, -1):
                    if closes[i] is not None and closes[i] > 0:
                        current_price = closes[i]
                        logger.info(f"Using last close price: {current_price}")
                        break
            
            # If still no price, this symbol has no data
            if current_price == 0:
                logger.warning(f"No valid price data for {symbol}")
                return None
            
            response_data = {
                'symbol': symbol.upper(),
                'price': current_price,
                'previousClose': prev_close if prev_close > 0 else current_price,
                'change': current_price - prev_close if prev_close > 0 else 0,
                'changePercent': ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0,
                'volume': meta.get('regularMarketVolume', 0),
                'open': meta.get('regularMarketOpen', current_price),
                'high': meta.get('regularMarketDayHigh', current_price),
                'low': meta.get('regularMarketDayLow', current_price),
                'marketCap': meta.get('marketCap', 0),
                'currency': meta.get('currency', 'USD'),
                'interval': interval,
                'chartData': []
            }
            
            if timestamps and quote:
                closes = quote.get('close', [])
                opens = quote.get('open', [])
                highs = quote.get('high', [])
                lows = quote.get('low', [])
                volumes = quote.get('volume', [])
                
                temp_chart = []
                for i in range(len(timestamps)):
                    if i < len(closes) and closes[i] is not None:
                        timestamp = timestamps[i] * 1000
                        temp_chart.append({
                            'timestamp': timestamp,
                            'date': datetime.fromtimestamp(timestamps[i]).isoformat(),
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) and volumes[i] else 0
                        })
                
                # Aggregate to 3m if needed
                if needs_aggregation and temp_chart:
                    response_data['chartData'] = self.aggregate_to_interval(temp_chart, 3)
                else:
                    response_data['chartData'] = temp_chart
            
            logger.info(f"Successfully fetched {len(response_data['chartData'])} data points for {symbol}")
            return response_data
            
        except Exception as e:
            logger.error(f"Yahoo intraday error for {symbol}: {e}")
            return None
    
    def aggregate_to_interval(self, chart_data: List[Dict], interval_minutes: int) -> List[Dict]:
        """Aggregate data to specified interval"""
        if not chart_data or interval_minutes <= 1:
            return chart_data
        
        aggregated = []
        current_bucket = None
        bucket_data = []
        
        for point in chart_data:
            timestamp = point.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                bucket_key = dt.replace(
                    minute=(dt.minute // interval_minutes) * interval_minutes,
                    second=0,
                    microsecond=0
                )
                
                if current_bucket != bucket_key:
                    if bucket_data:
                        aggregated.append({
                            'timestamp': int(current_bucket.timestamp() * 1000),
                            'date': current_bucket.isoformat(),
                            'open': bucket_data[0]['open'],
                            'high': max(d['high'] for d in bucket_data),
                            'low': min(d['low'] for d in bucket_data),
                            'close': bucket_data[-1]['close'],
                            'volume': sum(d.get('volume', 0) for d in bucket_data)
                        })
                    current_bucket = bucket_key
                    bucket_data = [point]
                else:
                    bucket_data.append(point)
        
        if bucket_data and current_bucket:
            aggregated.append({
                'timestamp': int(current_bucket.timestamp() * 1000),
                'date': current_bucket.isoformat(),
                'open': bucket_data[0]['open'],
                'high': max(d['high'] for d in bucket_data),
                'low': min(d['low'] for d in bucket_data),
                'close': bucket_data[-1]['close'],
                'volume': sum(d.get('volume', 0) for d in bucket_data)
            })
        
        return aggregated
    
    def fetch_yahoo_daily(self, symbol: str, period: str = '1mo'):
        """Fetch daily data from Yahoo Finance"""
        try:
            period_map = {
                '1d': '5d', '5d': '5d', '1m': '1mo',
                '3m': '3mo', '6m': '6mo', '1y': '1y', '2y': '2y'
            }
            yahoo_period = period_map.get(period, '1mo')
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={yahoo_period}&interval=1d"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            logger.info(f"Fetching daily: {url}")
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
            
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
            
            # Get from historical data if current is 0
            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            if current_price == 0 and quote:
                closes = quote.get('close', [])
                for i in range(len(closes) - 1, -1, -1):
                    if closes[i] is not None and closes[i] > 0:
                        current_price = closes[i]
                        break
            
            if current_price == 0:
                return None
            
            response_data = {
                'symbol': symbol.upper(),
                'price': current_price,
                'previousClose': prev_close if prev_close > 0 else current_price,
                'change': current_price - prev_close if prev_close > 0 else 0,
                'changePercent': ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0,
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
        """Calculate technical indicators from REAL data"""
        if not chart_data or len(chart_data) < 2:
            return {
                'rsi': None,
                'sma_20': None,
                'vwap': None,
                'atr': None
            }
        
        try:
            df = pd.DataFrame(chart_data)
            close_prices = pd.to_numeric(df['close'], errors='coerce')
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # SMA
            sma_20 = close_prices.rolling(window=min(20, len(close_prices))).mean()
            
            # VWAP
            high_prices = pd.to_numeric(df['high'], errors='coerce')
            low_prices = pd.to_numeric(df['low'], errors='coerce')
            volumes = pd.to_numeric(df.get('volume', 0), errors='coerce').fillna(0)
            typical_price = (high_prices + low_prices + close_prices) / 3
            vwap = (typical_price * volumes).cumsum() / volumes.cumsum()
            
            return {
                'rsi': float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else None,
                'sma_20': float(sma_20.iloc[-1]) if not sma_20.empty and not pd.isna(sma_20.iloc[-1]) else None,
                'vwap': float(vwap.iloc[-1]) if not vwap.empty and not pd.isna(vwap.iloc[-1]) else None,
                'atr': None  # Calculate if needed
            }
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {'rsi': None, 'sma_20': None, 'vwap': None, 'atr': None}

data_fetcher = MarketDataFetcher()

@app.route('/')
def index():
    """Serve the HTML interface"""
    try:
        html_files = [
            'finbert_charts_v3.3_fixed.html',
            'finbert_charts_complete.html',
            'finbert_charts_enhanced.html'
        ]
        
        for html_file in html_files:
            if os.path.exists(html_file):
                with open(html_file, 'r') as f:
                    return f.read()
        
        return "<h1>Chart interface not found</h1>", 404
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get REAL stock data only - no fake data"""
    try:
        interval = request.args.get('interval', '1d')
        period = request.args.get('period', '1m')
        
        logger.info(f"Request for {symbol} - interval: {interval}, period: {period}")
        
        # Fetch real data
        if interval == '1d':
            stock_data = data_fetcher.fetch_yahoo_daily(symbol, period)
        else:
            stock_data = data_fetcher.fetch_yahoo_intraday(symbol, interval, period)
        
        if not stock_data:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        current_price = stock_data.get('price', 0)
        chart_data = stock_data.get('chartData', [])
        
        # Calculate real indicators
        indicators = data_fetcher.calculate_indicators(chart_data, current_price)
        
        # Prepare response with REAL data only
        response = {
            'symbol': symbol.upper(),
            'current_price': current_price,
            'price_change': stock_data.get('change', 0),
            'price_change_percent': stock_data.get('changePercent', 0),
            'volume': stock_data.get('volume', 0),
            'day_high': stock_data.get('high', current_price),
            'day_low': stock_data.get('low', current_price),
            'chart_data': chart_data,
            'indicators': indicators,
            'interval': interval,
            'period': period,
            
            # Empty placeholders for features not yet implemented
            'economic_indicators': {},
            'ml_prediction': None,
            'sentiment_analysis': None,
            'news': []
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '3.3-real-fix'}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("FinBERT v3.3 REAL FIX - Starting...")
    print("NO FAKE DATA - Real market data only")
    print("=" * 60)
    print("Fixes:")
    print("- Gets last close price when regularMarketPrice is 0")
    print("- Properly aggregates 3m interval from 1m data")
    print("- Returns error if no real data available")
    print()
    print("Access at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)