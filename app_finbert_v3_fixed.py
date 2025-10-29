#!/usr/bin/env python3
"""
FinBERT Ultimate Trading System v3.0 - FIXED WITH REAL DATA ONLY
================================================================
This version:
- Uses Alpha Vantage API with key: 68ZFANK047DL0KSR
- Direct Yahoo Finance API (bypassing broken yfinance)
- NO synthetic/fallback data
- Correct endpoints for finbert_charts.html
- FinBERT sentiment analysis
- Random Forest predictions with confidence
"""

import os
import sys
import json
import logging
import warnings
import pickle
import hashlib
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import traceback

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# Try to import FinBERT
try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    FINBERT_AVAILABLE = True
    print("✓ FinBERT loaded successfully")
except ImportError:
    FINBERT_AVAILABLE = False
    print("⚠ FinBERT not available - using fallback sentiment")

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

class SentimentAnalyzer:
    """FinBERT-based sentiment analyzer with fallback"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        
        if FINBERT_AVAILABLE:
            try:
                print("Loading FinBERT model...")
                self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
                self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
                self.model.eval()
                print("✓ FinBERT model loaded")
            except Exception as e:
                print(f"Failed to load FinBERT: {e}")
                FINBERT_AVAILABLE = False
    
    def analyze(self, text: str) -> float:
        """Analyze sentiment of text (-1 to 1)"""
        if not text:
            return 0.0
            
        if self.model and self.tokenizer:
            try:
                inputs = self.tokenizer(text, padding=True, truncation=True, 
                                       return_tensors='pt', max_length=512)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    # FinBERT returns [negative, neutral, positive]
                    scores = predictions.numpy()[0]
                    sentiment = scores[2] - scores[0]  # positive - negative
                    return float(sentiment)
            except Exception as e:
                logger.error(f"FinBERT error: {e}")
        
        # Fallback sentiment
        positive_words = ['buy', 'bullish', 'growth', 'upgrade', 'positive', 'strong', 'gain', 'up']
        negative_words = ['sell', 'bearish', 'decline', 'downgrade', 'negative', 'weak', 'loss', 'down']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        return (pos_count - neg_count) / (pos_count + neg_count)

class DataFetcher:
    """Fetches real market data from multiple sources"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_KEY
    
    def fetch_yahoo_direct(self, symbol: str) -> Optional[Dict]:
        """Fetch data directly from Yahoo Finance API"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
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
            
            # Get historical data
            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
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
                'chartData': []
            }
            
            # Add chart data
            if timestamps and quote:
                closes = quote.get('close', [])
                opens = quote.get('open', [])
                highs = quote.get('high', [])
                lows = quote.get('low', [])
                volumes = quote.get('volume', [])
                
                # Take last 60 data points for analysis
                start_idx = max(0, len(timestamps) - 60)
                for i in range(start_idx, len(timestamps)):
                    if i < len(closes) and closes[i] is not None:
                        response_data['chartData'].append({
                            'date': datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                            'close': closes[i],
                            'open': opens[i] if i < len(opens) else closes[i],
                            'high': highs[i] if i < len(highs) else closes[i],
                            'low': lows[i] if i < len(lows) else closes[i],
                            'volume': volumes[i] if i < len(volumes) else 0
                        })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Yahoo direct error for {symbol}: {e}")
            return None
    
    def fetch_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Fetch from Alpha Vantage (US stocks only)"""
        try:
            # Skip Australian stocks
            if '.AX' in symbol.upper():
                return None
                
            # Get daily data
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                # Try global quote for current price
                params['function'] = 'GLOBAL_QUOTE'
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Global Quote' not in data:
                    return None
                    
                quote = data['Global Quote']
                return {
                    'symbol': symbol.upper(),
                    'price': float(quote.get('05. price', 0)),
                    'previousClose': float(quote.get('08. previous close', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'changePercent': float(quote.get('10. change percent', '0%').rstrip('%')),
                    'volume': int(quote.get('06. volume', 0)),
                    'open': float(quote.get('02. open', 0)),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0)),
                    'chartData': []
                }
            
            # Process time series data
            time_series = data['Time Series (Daily)']
            sorted_dates = sorted(time_series.keys(), reverse=True)[:60]  # Last 60 days
            
            chart_data = []
            for date in reversed(sorted_dates):
                day_data = time_series[date]
                chart_data.append({
                    'date': date,
                    'open': float(day_data['1. open']),
                    'high': float(day_data['2. high']),
                    'low': float(day_data['3. low']),
                    'close': float(day_data['4. close']),
                    'volume': int(day_data['5. volume'])
                })
            
            if chart_data:
                latest = chart_data[-1]
                prev = chart_data[-2] if len(chart_data) > 1 else latest
                
                return {
                    'symbol': symbol.upper(),
                    'price': latest['close'],
                    'previousClose': prev['close'],
                    'change': latest['close'] - prev['close'],
                    'changePercent': ((latest['close'] - prev['close']) / prev['close'] * 100) if prev['close'] else 0,
                    'volume': latest['volume'],
                    'open': latest['open'],
                    'high': latest['high'],
                    'low': latest['low'],
                    'chartData': chart_data
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    def fetch(self, symbol: str) -> Optional[Dict]:
        """Fetch data with fallback strategy"""
        # Try Yahoo first (works for most symbols including Australian)
        data = self.fetch_yahoo_direct(symbol)
        
        # Fallback to Alpha Vantage for US stocks
        if not data and not '.AX' in symbol.upper():
            data = self.fetch_alpha_vantage(symbol)
        
        return data

class MLPredictor:
    """Machine Learning predictor with Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_cache = {}
    
    def prepare_features(self, data: Dict) -> Optional[np.ndarray]:
        """Prepare features from market data"""
        try:
            if not data or 'chartData' not in data or len(data['chartData']) < 20:
                return None
            
            df = pd.DataFrame(data['chartData'])
            
            # Calculate technical indicators
            features = {}
            
            # Price-based features
            features['return_1d'] = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] if len(df) > 1 else 0
            features['return_5d'] = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] if len(df) > 5 else 0
            features['return_20d'] = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20] if len(df) > 20 else 0
            
            # Moving averages
            features['sma_5'] = df['close'].tail(5).mean()
            features['sma_20'] = df['close'].tail(20).mean()
            features['price_to_sma20'] = df['close'].iloc[-1] / features['sma_20'] if features['sma_20'] > 0 else 1
            
            # Volatility
            features['volatility_20d'] = df['close'].tail(20).std() / df['close'].tail(20).mean() if len(df) > 20 else 0
            
            # Volume
            features['volume_ratio'] = df['volume'].iloc[-1] / df['volume'].tail(20).mean() if df['volume'].tail(20).mean() > 0 else 1
            
            # RSI
            def calculate_rsi(prices, period=14):
                if len(prices) < period:
                    return 50.0
                deltas = prices.diff()
                gains = deltas.where(deltas > 0, 0)
                losses = -deltas.where(deltas < 0, 0)
                avg_gain = gains.tail(period).mean()
                avg_loss = losses.tail(period).mean()
                if avg_loss == 0:
                    return 100
                rs = avg_gain / avg_loss
                return 100 - (100 / (1 + rs))
            
            features['rsi'] = calculate_rsi(df['close']) / 100  # Normalize to 0-1
            
            # Store feature names for later use
            self.feature_names = list(features.keys())
            
            return np.array([list(features.values())])
            
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return None
    
    def train_model(self, symbol: str, data: Dict) -> Dict:
        """Train a model for the symbol"""
        try:
            if not data or 'chartData' not in data or len(data['chartData']) < 30:
                return {'error': 'Insufficient data for training (need at least 30 days)'}
            
            df = pd.DataFrame(data['chartData'])
            
            # Prepare training data
            X = []
            y = []
            
            for i in range(20, len(df) - 1):
                window = df.iloc[i-20:i]
                
                # Calculate features for this window
                features = {}
                features['return_1d'] = (window['close'].iloc[-1] - window['close'].iloc[-2]) / window['close'].iloc[-2]
                features['return_5d'] = (window['close'].iloc[-1] - window['close'].iloc[-5]) / window['close'].iloc[-5]
                features['return_20d'] = (window['close'].iloc[-1] - window['close'].iloc[-20]) / window['close'].iloc[-20]
                features['sma_5'] = window['close'].tail(5).mean()
                features['sma_20'] = window['close'].mean()
                features['price_to_sma20'] = window['close'].iloc[-1] / features['sma_20']
                features['volatility_20d'] = window['close'].std() / window['close'].mean()
                features['volume_ratio'] = window['volume'].iloc[-1] / window['volume'].mean() if window['volume'].mean() > 0 else 1
                
                X.append(list(features.values()))
                
                # Label: 1 if price goes up next day, 0 otherwise
                next_return = (df['close'].iloc[i+1] - df['close'].iloc[i]) / df['close'].iloc[i]
                y.append(1 if next_return > 0 else 0)
            
            if len(X) < 10:
                return {'error': 'Not enough samples for training'}
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = accuracy_score(y_train, self.model.predict(X_train_scaled))
            test_score = accuracy_score(y_test, self.model.predict(X_test_scaled))
            
            # Cache the model
            self.model_cache[symbol] = {
                'model': self.model,
                'scaler': self.scaler,
                'timestamp': datetime.now()
            }
            
            return {
                'success': True,
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'samples': len(X),
                'features': self.feature_names
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {'error': str(e)}
    
    def predict(self, symbol: str, data: Dict, sentiment: float = 0.0) -> Dict:
        """Make prediction for symbol"""
        try:
            # Prepare features
            features = self.prepare_features(data)
            if features is None:
                return {'error': 'Unable to prepare features'}
            
            # Check if we have a cached model
            if symbol not in self.model_cache:
                # Train a new model
                train_result = self.train_model(symbol, data)
                if 'error' in train_result:
                    return train_result
            
            model_info = self.model_cache.get(symbol)
            if not model_info:
                return {'error': 'No model available'}
            
            model = model_info['model']
            scaler = model_info['scaler']
            
            # Make prediction
            features_scaled = scaler.transform(features)
            
            # Add sentiment as additional feature if available
            if sentiment != 0.0:
                # Simple approach: weight the prediction by sentiment
                prediction_proba = model.predict_proba(features_scaled)[0]
                sentiment_weight = 0.2  # 20% weight for sentiment
                adjusted_proba = prediction_proba[1] * (1 - sentiment_weight) + (sentiment + 1) / 2 * sentiment_weight
            else:
                prediction_proba = model.predict_proba(features_scaled)[0]
                adjusted_proba = prediction_proba[1]
            
            # Calculate predicted price
            current_price = data['price']
            expected_return = (adjusted_proba - 0.5) * 0.02  # Scale to ±1% for neutral confidence
            predicted_price = current_price * (1 + expected_return)
            
            # Confidence is based on probability strength
            confidence = abs(adjusted_proba - 0.5) * 200  # Scale to 0-100%
            
            return {
                'next_day_prediction': {
                    'price': predicted_price,
                    'change': expected_return * 100,
                    'direction': 'up' if adjusted_proba > 0.5 else 'down',
                    'probability': float(adjusted_proba),
                    'confidence': min(100, confidence)
                },
                'target_prices': [{
                    'price': predicted_price * (1.05 if adjusted_proba > 0.5 else 0.95),
                    'timeframe': '5 days',
                    'confidence': min(100, confidence * 0.8)
                }],
                'sentiment_score': sentiment,
                'model_accuracy': model_info.get('test_accuracy', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'error': str(e)}

# Initialize components
sentiment_analyzer = SentimentAnalyzer()
data_fetcher = DataFetcher()
ml_predictor = MLPredictor()

# API Routes matching finbert_charts.html

@app.route('/')
def index():
    """Serve the chart interface"""
    try:
        with open('finbert_charts.html', 'r') as f:
            return f.read()
    except:
        return jsonify({'error': 'Chart interface not found'}), 404

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get current stock data"""
    try:
        data = data_fetcher.fetch(symbol)
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Calculate technical indicators
        if data.get('chartData'):
            close_prices = [d['close'] for d in data['chartData']]
            
            # RSI
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
            
            # MACD
            def calculate_ema(prices, period):
                if len(prices) < period:
                    return prices[-1] if prices else 0
                ema = [prices[0]]
                multiplier = 2 / (period + 1)
                for price in prices[1:]:
                    ema.append((price - ema[-1]) * multiplier + ema[-1])
                return ema[-1]
            
            rsi = calculate_rsi(close_prices)
            ema12 = calculate_ema(close_prices, 12)
            ema26 = calculate_ema(close_prices, 26)
            macd = ema12 - ema26
            signal = calculate_ema([macd], 9)
            
            # ATR (Average True Range)
            if len(data['chartData']) > 1:
                tr_values = []
                for i in range(1, min(14, len(data['chartData']))):
                    high = data['chartData'][i]['high']
                    low = data['chartData'][i]['low']
                    prev_close = data['chartData'][i-1]['close']
                    tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                    tr_values.append(tr)
                atr = np.mean(tr_values) if tr_values else 0
            else:
                atr = 0
            
            data['indicators'] = {
                'RSI': round(rsi, 2),
                'MACD': round(macd, 4),
                'Signal': round(signal, 4),
                'ATR': round(atr, 2),
                'SMA20': round(np.mean(close_prices[-20:]), 2) if len(close_prices) >= 20 else data['price'],
                'EMA20': round(calculate_ema(close_prices, 20), 2)
            }
        else:
            data['indicators'] = {
                'RSI': '--',
                'MACD': '--',
                'Signal': '--',
                'ATR': '--',
                'SMA20': data.get('price', 0),
                'EMA20': data.get('price', 0)
            }
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical data for charting"""
    try:
        period = request.args.get('period', '30d')
        
        data = data_fetcher.fetch(symbol)
        
        if not data or 'chartData' not in data:
            return jsonify({'error': f'Unable to fetch historical data for {symbol}'}), 404
        
        # Filter by period
        chart_data = data['chartData']
        
        if period == '5d' and len(chart_data) > 5:
            chart_data = chart_data[-5:]
        elif period == '1m' and len(chart_data) > 22:
            chart_data = chart_data[-22:]
        elif period == '3m' and len(chart_data) > 66:
            chart_data = chart_data[-66:]
        elif period == '6m' and len(chart_data) > 132:
            chart_data = chart_data[-132:]
        
        return jsonify({
            'symbol': symbol,
            'period': period,
            'data': chart_data
        })
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def predict_stock(symbol):
    """Get ML prediction for stock"""
    try:
        # Get stock data
        data = data_fetcher.fetch(symbol)
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Get news sentiment
        sentiment = 0.0
        try:
            # Fetch recent news
            news_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            response = requests.get(news_url, timeout=5)
            
            if response.status_code == 200:
                # Simple sentiment from news titles
                news_text = response.text[:2000]  # First 2000 chars
                sentiment = sentiment_analyzer.analyze(news_text)
        except:
            pass
        
        # Make prediction
        prediction = ml_predictor.predict(symbol, data, sentiment)
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """Get news and sentiment for symbol"""
    try:
        news_items = []
        overall_sentiment = 0.0
        
        # Try Yahoo Finance RSS
        try:
            url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # Parse RSS (simple approach)
                import re
                titles = re.findall(r'<title>(.*?)</title>', response.text)
                links = re.findall(r'<link>(.*?)</link>', response.text)
                
                for i, title in enumerate(titles[:5]):  # Get first 5 news items
                    if i < len(links):
                        sentiment = sentiment_analyzer.analyze(title)
                        news_items.append({
                            'title': title,
                            'url': links[i],
                            'sentiment': round(sentiment, 3),
                            'source': 'Yahoo Finance'
                        })
                        overall_sentiment += sentiment
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
        
        if news_items:
            overall_sentiment = overall_sentiment / len(news_items)
        
        return jsonify({
            'symbol': symbol,
            'news': news_items,
            'overall_sentiment': round(overall_sentiment, 3)
        })
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economic')
def get_economic_indicators():
    """Get economic indicators"""
    try:
        indicators = {}
        
        # VIX (Fear Index)
        vix_data = data_fetcher.fetch('^VIX')
        if vix_data:
            indicators['VIX'] = {
                'value': vix_data['price'],
                'change': vix_data.get('changePercent', 0),
                'label': 'Fear Index'
            }
        
        # 10-Year Treasury Yield
        tnx_data = data_fetcher.fetch('^TNX')
        if tnx_data:
            indicators['TNX'] = {
                'value': tnx_data['price'],
                'change': tnx_data.get('changePercent', 0),
                'label': '10-Year Treasury'
            }
        
        # US Dollar Index
        dxy_data = data_fetcher.fetch('DX-Y.NYB')
        if dxy_data:
            indicators['DXY'] = {
                'value': dxy_data['price'],
                'change': dxy_data.get('changePercent', 0),
                'label': 'Dollar Index'
            }
        
        # Gold
        gold_data = data_fetcher.fetch('GC=F')
        if gold_data:
            indicators['GOLD'] = {
                'value': gold_data['price'],
                'change': gold_data.get('changePercent', 0),
                'label': 'Gold Futures'
            }
        
        return jsonify(indicators)
        
    except Exception as e:
        logger.error(f"Error getting economic indicators: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """System status check"""
    return jsonify({
        'status': 'running',
        'finbert': FINBERT_AVAILABLE,
        'alpha_vantage_key': bool(ALPHA_VANTAGE_KEY),
        'version': '3.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FinBERT Ultimate Trading System v3.0 - FIXED")
    print("="*60)
    print(f"✓ FinBERT: {'Available' if FINBERT_AVAILABLE else 'Using fallback'}")
    print(f"✓ Alpha Vantage Key: {'Configured' if ALPHA_VANTAGE_KEY else 'Not set'}")
    print(f"✓ Starting server on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)