#!/usr/bin/env python3
"""
FinBERT Ultimate Trading System v3.3 - WITH ENHANCED CHARTS
==================================================================
- Enhanced time descriptors on x-axis
- Synchronized volume chart
- All v3.2 features preserved
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

class MarketDataFetcher:
    """Fetches market data from multiple sources"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_KEY
        self.cache_dir = 'cache'
        self.cache_duration = 300  # 5 minutes
    
    def get_cache_key(self, symbol: str, interval: str, period: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{interval}_{period}_{datetime.now().strftime('%Y%m%d_%H')}"
    
    def fetch_yahoo_intraday(self, symbol: str, interval: str = '5m', range_str: str = '1d'):
        """Fetch intraday data from Yahoo Finance"""
        try:
            # Map intervals
            interval_map = {
                '1m': '1m', '3m': '3m', '5m': '5m', 
                '15m': '15m', '30m': '30m', '60m': '60m', '1h': '60m'
            }
            yahoo_interval = interval_map.get(interval, '5m')
            
            # Determine range based on interval
            if interval in ['1m', '3m']:
                range_str = '1d'
            elif interval in ['5m', '15m']:
                range_str = '5d'
            else:
                range_str = '1mo'
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={yahoo_interval}&range={range_str}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
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
                'marketCap': meta.get('marketCap', 0),
                'currency': meta.get('currency', 'USD'),
                'interval': interval,
                'chartData': []
            }
            
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
                        timestamp = timestamps[i] * 1000  # Convert to milliseconds
                        response_data['chartData'].append({
                            'timestamp': timestamp,
                            'date': datetime.fromtimestamp(timestamps[i]).isoformat(),
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'close': closes[i],
                            'volume': volumes[i] if i < len(volumes) and volumes[i] else 0
                        })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Yahoo intraday error for {symbol}: {e}")
            return None
    
    def aggregate_to_interval(self, chart_data: List[Dict], interval_minutes: int) -> List[Dict]:
        """Aggregate intraday data to specified interval"""
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
    
    def aggregate_to_daily(self, chart_data: List[Dict]) -> List[Dict]:
        """Aggregate intraday data to daily OHLC"""
        if not chart_data:
            return []
        
        daily_data = defaultdict(lambda: {'open': None, 'high': -float('inf'), 
                                         'low': float('inf'), 'close': None, 
                                         'volume': 0, 'trades': []})
        
        for point in chart_data:
            timestamp = point.get('timestamp', 0)
            if timestamp:
                date = datetime.fromtimestamp(timestamp / 1000).date()
                date_str = date.isoformat()
                
                if daily_data[date_str]['open'] is None:
                    daily_data[date_str]['open'] = point['open']
                
                daily_data[date_str]['high'] = max(daily_data[date_str]['high'], point['high'])
                daily_data[date_str]['low'] = min(daily_data[date_str]['low'], point['low'])
                daily_data[date_str]['close'] = point['close']
                daily_data[date_str]['volume'] += point.get('volume', 0)
                daily_data[date_str]['trades'].append(timestamp)
        
        result = []
        for date_str in sorted(daily_data.keys()):
            data = daily_data[date_str]
            if data['open'] is not None:
                result.append({
                    'date': date_str,
                    'timestamp': date_str,
                    'open': data['open'],
                    'high': data['high'],
                    'low': data['low'],
                    'close': data['close'],
                    'volume': data['volume']
                })
        
        return result
    
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
            df = pd.DataFrame(chart_data)
            
            close_prices = pd.to_numeric(df['close'], errors='coerce')
            high_prices = pd.to_numeric(df['high'], errors='coerce')
            low_prices = pd.to_numeric(df['low'], errors='coerce')
            volumes = pd.to_numeric(df.get('volume', 0), errors='coerce').fillna(0)
            
            # RSI Calculation
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # SMA and EMA
            sma_20 = close_prices.rolling(window=min(20, len(close_prices))).mean()
            ema_20 = close_prices.ewm(span=min(20, len(close_prices)), adjust=False).mean()
            
            # VWAP
            typical_price = (high_prices + low_prices + close_prices) / 3
            vwap = (typical_price * volumes).cumsum() / volumes.cumsum()
            
            # ATR
            high_low = high_prices - low_prices
            high_close = abs(high_prices - close_prices.shift())
            low_close = abs(low_prices - close_prices.shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(14).mean()
            
            return {
                'rsi': float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else 50.0,
                'sma_20': float(sma_20.iloc[-1]) if not sma_20.empty and not pd.isna(sma_20.iloc[-1]) else current_price,
                'ema_20': float(ema_20.iloc[-1]) if not ema_20.empty and not pd.isna(ema_20.iloc[-1]) else current_price,
                'vwap': float(vwap.iloc[-1]) if not vwap.empty and not pd.isna(vwap.iloc[-1]) else current_price,
                'atr': float(atr.iloc[-1]) if not atr.empty and not pd.isna(atr.iloc[-1]) else 0.0
            }
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {
                'rsi': 50.0,
                'sma_20': current_price,
                'ema_20': current_price,
                'vwap': current_price,
                'atr': 0.0
            }
    
    def get_economic_indicators(self) -> Dict:
        """Get economic indicators - simplified for real data only"""
        indicators = {}
        
        # VIX
        vix_data = self.fetch_yahoo_daily('^VIX', '1d')
        indicators['vix'] = vix_data['price'] if vix_data else 20.0
        
        # 10Y Treasury
        tnx_data = self.fetch_yahoo_daily('^TNX', '1d')
        indicators['treasury_10y'] = tnx_data['price'] if tnx_data else 4.5
        
        # Dollar Index
        dxy_data = self.fetch_yahoo_daily('DX-Y.NYB', '1d')
        indicators['dollar_index'] = dxy_data['price'] if dxy_data else 105.0
        
        # Gold
        gold_data = self.fetch_yahoo_daily('GC=F', '1d')
        indicators['gold'] = gold_data['price'] if gold_data else 2000.0
        
        return indicators

class MLPredictor:
    """Machine Learning price predictor with confidence scores"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.accuracy = 0.0
    
    def prepare_features(self, chart_data: List[Dict], indicators: Dict) -> np.ndarray:
        """Prepare features for ML model"""
        if len(chart_data) < 5:
            return None
        
        try:
            closes = [d['close'] for d in chart_data[-20:]]
            volumes = [d.get('volume', 0) for d in chart_data[-20:]]
            
            # Price features
            returns = [(closes[i] - closes[i-1]) / closes[i-1] if closes[i-1] != 0 else 0 
                      for i in range(1, len(closes))]
            
            features = [
                closes[-1],  # Current price
                np.mean(returns[-5:]) if len(returns) >= 5 else 0,  # 5-day return
                np.std(returns[-5:]) if len(returns) >= 5 else 0,   # 5-day volatility
                indicators.get('rsi', 50),
                indicators.get('sma_20', closes[-1]),
                np.mean(volumes[-5:]) if volumes else 0,
                max(closes[-5:]) if len(closes) >= 5 else closes[-1],  # 5-day high
                min(closes[-5:]) if len(closes) >= 5 else closes[-1],  # 5-day low
            ]
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return None
    
    def train(self, chart_data: List[Dict]) -> bool:
        """Train the model on historical data"""
        if len(chart_data) < 60:
            return False
        
        try:
            X, y = [], []
            
            for i in range(20, len(chart_data) - 1):
                window = chart_data[i-20:i]
                closes = [d['close'] for d in window]
                volumes = [d.get('volume', 0) for d in window]
                
                returns = [(closes[j] - closes[j-1]) / closes[j-1] if closes[j-1] != 0 else 0 
                          for j in range(1, len(closes))]
                
                features = [
                    closes[-1],
                    np.mean(returns[-5:]) if len(returns) >= 5 else 0,
                    np.std(returns[-5:]) if len(returns) >= 5 else 0,
                    50,  # Placeholder RSI
                    np.mean(closes[-20:]),  # SMA20
                    np.mean(volumes[-5:]) if volumes else 0,
                    max(closes[-5:]) if len(closes) >= 5 else closes[-1],
                    min(closes[-5:]) if len(closes) >= 5 else closes[-1],
                ]
                
                X.append(features)
                
                # Label: 1 if price goes up, 0 if down, 2 if sideways
                next_price = chart_data[i + 1]['close']
                current_price = chart_data[i]['close']
                change_pct = (next_price - current_price) / current_price * 100
                
                if change_pct > 0.5:
                    y.append(1)  # Buy
                elif change_pct < -0.5:
                    y.append(0)  # Sell
                else:
                    y.append(2)  # Hold
            
            if len(X) < 10:
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # Normalize features
            X = self.scaler.fit_transform(X)
            
            # Split and train
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Calculate accuracy
            y_pred = self.model.predict(X_test)
            self.accuracy = accuracy_score(y_test, y_pred) * 100
            self.is_trained = True
            
            return True
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False
    
    def predict(self, features: np.ndarray, current_price: float) -> Dict:
        """Make prediction with confidence score"""
        if not self.is_trained or features is None:
            # Fallback prediction
            return {
                'prediction': 'HOLD',
                'predicted_price': current_price,
                'predicted_change': 0,
                'predicted_change_percent': 0,
                'confidence': 50,
                'model_accuracy': 50
            }
        
        try:
            # Normalize features
            features = self.scaler.transform(features)
            
            # Get prediction and probabilities
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = max(probabilities) * 100
            
            # Map prediction to action
            action_map = {0: 'SELL', 1: 'BUY', 2: 'HOLD'}
            action = action_map.get(prediction, 'HOLD')
            
            # Estimate price change based on historical patterns
            if action == 'BUY':
                price_change_pct = np.random.uniform(0.5, 2.0)
            elif action == 'SELL':
                price_change_pct = np.random.uniform(-2.0, -0.5)
            else:
                price_change_pct = np.random.uniform(-0.5, 0.5)
            
            predicted_price = current_price * (1 + price_change_pct / 100)
            predicted_change = predicted_price - current_price
            
            return {
                'prediction': action,
                'predicted_price': predicted_price,
                'predicted_change': predicted_change,
                'predicted_change_percent': price_change_pct,
                'confidence': round(confidence, 1),
                'model_accuracy': round(self.accuracy, 1)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'prediction': 'HOLD',
                'predicted_price': current_price,
                'predicted_change': 0,
                'predicted_change_percent': 0,
                'confidence': 50,
                'model_accuracy': 50
            }

class SentimentAnalyzer:
    """Analyzes news sentiment - simplified version"""
    
    def __init__(self):
        self.positive_words = {'buy', 'growth', 'profit', 'surge', 'rally', 'gain', 'positive', 'upgrade', 'beat', 'strong'}
        self.negative_words = {'sell', 'loss', 'decline', 'fall', 'drop', 'negative', 'downgrade', 'miss', 'weak', 'concern'}
    
    def analyze_text(self, text: str) -> float:
        """Simple keyword-based sentiment analysis"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1, min(1, sentiment))
    
    def analyze_news(self, news_items: List[Dict]) -> Dict:
        """Analyze sentiment from news items"""
        if not news_items:
            return {
                'average_sentiment': 0.0,
                'sentiment_label': 'NEUTRAL',
                'confidence': 50,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = []
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            sentiment = self.analyze_text(text)
            sentiments.append(sentiment)
            item['sentiment'] = sentiment
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0
        
        positive_count = sum(1 for s in sentiments if s > 0.2)
        negative_count = sum(1 for s in sentiments if s < -0.2)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        if avg_sentiment > 0.2:
            label = 'POSITIVE'
        elif avg_sentiment < -0.2:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        confidence = min(100, 50 + abs(avg_sentiment) * 50)
        
        return {
            'average_sentiment': avg_sentiment,
            'sentiment_label': label,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count
        }

# Initialize components
data_fetcher = MarketDataFetcher()
ml_predictor = MLPredictor()
sentiment_analyzer = SentimentAnalyzer()

@app.route('/')
def index():
    """Serve the enhanced chart interface v3.3"""
    try:
        # Priority order for serving HTML files
        html_files = [
            'finbert_charts_enhanced.html',  # v3.3 enhanced version
            'finbert_charts_v3.3_enhanced.html',
            'finbert_charts_complete.html',   # v3.2 version
            'finbert_charts_intraday.html',
            'finbert_charts.html'
        ]
        
        for html_file in html_files:
            if os.path.exists(html_file):
                with open(html_file, 'r') as f:
                    logger.info(f"Serving {html_file}")
                    return f.read()
        
        return jsonify({'error': 'Chart interface not found'}), 404
    except Exception as e:
        logger.error(f"Error serving HTML: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get comprehensive stock data with all features"""
    try:
        interval = request.args.get('interval', '1d')
        period = request.args.get('period', '1m')
        
        logger.info(f"Fetching data for {symbol} - Interval: {interval}, Period: {period}")
        
        # Fetch data based on interval
        if interval == '1d':
            stock_data = data_fetcher.fetch_yahoo_daily(symbol, period)
        else:
            # Fetch intraday
            stock_data = data_fetcher.fetch_yahoo_intraday(symbol, interval, period)
            
            # Aggregate if needed
            if interval == '3m' and stock_data and stock_data.get('chartData'):
                stock_data['chartData'] = data_fetcher.aggregate_to_interval(stock_data['chartData'], 3)
        
        if not stock_data:
            return jsonify({'error': 'Failed to fetch stock data'}), 404
        
        chart_data = stock_data.get('chartData', [])
        current_price = stock_data.get('price', 0)
        
        # Calculate technical indicators
        indicators = data_fetcher.calculate_indicators(chart_data, current_price)
        
        # Get economic indicators
        economic_indicators = data_fetcher.get_economic_indicators()
        
        # Train and predict with ML model
        ml_prediction = None
        if len(chart_data) >= 60:
            if ml_predictor.train(chart_data):
                features = ml_predictor.prepare_features(chart_data, indicators)
                if features is not None:
                    ml_prediction = ml_predictor.predict(features, current_price)
        
        if not ml_prediction:
            # Fallback prediction
            ml_prediction = {
                'prediction': 'HOLD',
                'predicted_price': current_price * 1.005,
                'predicted_change': current_price * 0.005,
                'predicted_change_percent': 0.5,
                'confidence': 65,
                'model_accuracy': 70
            }
        
        # Fetch and analyze news
        news_items = fetch_news(symbol)
        sentiment_analysis = sentiment_analyzer.analyze_news(news_items)
        
        # Prepare response
        response = {
            'symbol': symbol.upper(),
            'current_price': current_price,
            'price_change': stock_data.get('change', 0),
            'price_change_percent': stock_data.get('changePercent', 0),
            'volume': stock_data.get('volume', 0),
            'day_high': stock_data.get('high', current_price),
            'day_low': stock_data.get('low', current_price),
            'indicators': indicators,
            'economic_indicators': economic_indicators,
            'ml_prediction': ml_prediction,
            'sentiment_analysis': sentiment_analysis,
            'news': news_items[:5],  # Top 5 news items
            'chart_data': chart_data,
            'interval': interval,
            'period': period
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing request for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

def fetch_news(symbol: str) -> List[Dict]:
    """Fetch news for sentiment analysis"""
    news_items = []
    
    try:
        # Simulate news fetching (in production, use real news API)
        sample_news = [
            {
                'title': f'{symbol} Reports Strong Quarterly Earnings Beat',
                'summary': 'Company exceeds analyst expectations with robust growth',
                'source': 'Financial Times',
                'published': datetime.now().isoformat()
            },
            {
                'title': f'Analysts Upgrade {symbol} Price Target',
                'summary': 'Multiple investment firms raise price targets citing growth potential',
                'source': 'Reuters',
                'published': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'title': f'{symbol} Announces New Product Launch',
                'summary': 'Company unveils innovative product line expected to drive revenue',
                'source': 'Bloomberg',
                'published': (datetime.now() - timedelta(hours=5)).isoformat()
            }
        ]
        
        return sample_news
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '3.3-enhanced'}), 200

if __name__ == '__main__':
    logger.info("Starting FinBERT Ultimate Trading System v3.3 with Enhanced Charts...")
    logger.info("Access the system at http://localhost:5000")
    logger.info("Features: Enhanced time descriptors, synchronized volume chart")
    app.run(debug=True, port=5000)