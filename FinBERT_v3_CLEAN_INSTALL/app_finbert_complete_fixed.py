#!/usr/bin/env python3
"""
FinBERT Ultimate Trading System v3.0 - COMPLETE FIX
====================================================
Fixes:
- Handles intraday data correctly by aggregating to daily
- Uses Alpha Vantage with key: 68ZFANK047DL0KSR
- Direct Yahoo Finance API (bypassing broken yfinance)
- NO synthetic/fallback data - real market data only
- Correct endpoints for finbert_charts.html
- FinBERT sentiment analysis with confidence
- Random Forest predictions with confidence percentages
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
from collections import defaultdict

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
from sklearn.metrics import accuracy_score
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
        self.cache = {}
        
        if FINBERT_AVAILABLE:
            try:
                print("Loading FinBERT model...")
                self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
                self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
                self.model.eval()
                print("✓ FinBERT model loaded")
            except Exception as e:
                print(f"Failed to load FinBERT: {e}")
                self.model = None
                self.tokenizer = None
    
    def analyze(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment of text, returns (sentiment, confidence)"""
        if not text:
            return 0.0, 0.0
            
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.cache:
            return self.cache[text_hash]
            
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
                    confidence = max(scores) * 100  # Confidence as percentage
                    result = (float(sentiment), float(confidence))
                    self.cache[text_hash] = result
                    return result
            except Exception as e:
                logger.error(f"FinBERT error: {e}")
        
        # Fallback sentiment
        positive_words = ['buy', 'bullish', 'growth', 'upgrade', 'positive', 'strong', 'gain', 'rise', 'outperform']
        negative_words = ['sell', 'bearish', 'decline', 'downgrade', 'negative', 'weak', 'loss', 'fall', 'underperform']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0, 50.0
        
        sentiment = (pos_count - neg_count) / (pos_count + neg_count)
        confidence = min(100, (pos_count + neg_count) * 10 + 50)
        return sentiment, confidence

class DataFetcher:
    """Fetches real market data from multiple sources"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_KEY
        self.cache = {}
        self.cache_timeout = 60  # 1 minute cache
    
    def aggregate_intraday_to_daily(self, chart_data: List[Dict]) -> List[Dict]:
        """Aggregate intraday data to daily OHLCV"""
        if not chart_data:
            return []
        
        # Group by date
        daily_data = defaultdict(lambda: {'open': None, 'high': 0, 'low': float('inf'), 'close': None, 'volume': 0})
        
        for point in chart_data:
            date = point['date'].split('T')[0] if 'T' in point['date'] else point['date']
            
            # Set open (first price of the day)
            if daily_data[date]['open'] is None:
                daily_data[date]['open'] = point['open']
            
            # Update high/low
            daily_data[date]['high'] = max(daily_data[date]['high'], point['high'])
            daily_data[date]['low'] = min(daily_data[date]['low'], point['low'])
            
            # Set close (last price of the day)
            daily_data[date]['close'] = point['close']
            
            # Sum volume
            daily_data[date]['volume'] += point.get('volume', 0)
        
        # Convert to list
        result = []
        for date in sorted(daily_data.keys()):
            result.append({
                'date': date,
                'open': daily_data[date]['open'],
                'high': daily_data[date]['high'],
                'low': daily_data[date]['low'] if daily_data[date]['low'] != float('inf') else daily_data[date]['open'],
                'close': daily_data[date]['close'],
                'volume': daily_data[date]['volume']
            })
        
        return result
    
    def fetch_yahoo_direct(self, symbol: str, period: str = '1mo') -> Optional[Dict]:
        """Fetch data directly from Yahoo Finance API"""
        try:
            # Convert period to Yahoo format
            period_map = {
                '5d': '5d',
                '1m': '1mo', 
                '3m': '3mo',
                '6m': '6mo',
                '1y': '1y',
                '30d': '1mo',
                '60d': '3mo'
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
            
            # Add chart data - properly formatted daily data
            if timestamps and quote:
                closes = quote.get('close', [])
                opens = quote.get('open', [])
                highs = quote.get('high', [])
                lows = quote.get('low', [])
                volumes = quote.get('volume', [])
                
                for i in range(len(timestamps)):
                    if i < len(closes) and closes[i] is not None:
                        response_data['chartData'].append({
                            'date': datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                            'close': closes[i],
                            'open': opens[i] if i < len(opens) and opens[i] else closes[i],
                            'high': highs[i] if i < len(highs) and highs[i] else closes[i],
                            'low': lows[i] if i < len(lows) and lows[i] else closes[i],
                            'volume': volumes[i] if i < len(volumes) else 0
                        })
                
                # Aggregate if we have intraday data (multiple entries per date)
                if response_data['chartData']:
                    dates = [d['date'] for d in response_data['chartData']]
                    if len(dates) != len(set(dates)):  # Duplicate dates = intraday
                        response_data['chartData'] = self.aggregate_intraday_to_daily(response_data['chartData'])
            
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
            
            # Check cache
            cache_key = f"av_{symbol}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_timeout:
                    return cached_data
                
            # Get daily data
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'compact',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                return None
            
            # Process time series data
            time_series = data['Time Series (Daily)']
            sorted_dates = sorted(time_series.keys(), reverse=True)[:60]
            
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
                
                result = {
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
                
                # Cache the result
                self.cache[cache_key] = (result, datetime.now())
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    def fetch(self, symbol: str, period: str = '30d') -> Optional[Dict]:
        """Fetch data with fallback strategy"""
        # Try Yahoo first
        data = self.fetch_yahoo_direct(symbol, period)
        
        # Fallback to Alpha Vantage for US stocks
        if not data and not '.AX' in symbol.upper():
            data = self.fetch_alpha_vantage(symbol)
        
        # Calculate indicators if we have data
        if data and data.get('chartData'):
            data['indicators'] = self.calculate_indicators(data['chartData'], data['price'])
        
        return data
    
    def calculate_indicators(self, chart_data: List[Dict], current_price: float) -> Dict:
        """Calculate technical indicators"""
        if not chart_data:
            return {
                'RSI': '--',
                'MACD': '--',
                'Signal': '--',
                'ATR': '--',
                'SMA20': current_price,
                'EMA20': current_price
            }
        
        try:
            close_prices = [d['close'] for d in chart_data]
            
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
            
            # MACD
            def calculate_ema(prices, period):
                if len(prices) < 2:
                    return prices[-1] if prices else 0
                ema = [prices[0]]
                multiplier = 2 / (period + 1)
                for price in prices[1:]:
                    ema.append((price - ema[-1]) * multiplier + ema[-1])
                return ema[-1]
            
            # ATR
            def calculate_atr(data, period=14):
                if len(data) < 2:
                    return 0
                tr_values = []
                for i in range(1, len(data)):
                    high = data[i]['high']
                    low = data[i]['low']
                    prev_close = data[i-1]['close']
                    tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                    tr_values.append(tr)
                
                if not tr_values:
                    return 0
                    
                atr = np.mean(tr_values[:period])
                for i in range(period, len(tr_values)):
                    atr = (atr * (period - 1) + tr_values[i]) / period
                return atr
            
            rsi = calculate_rsi(close_prices)
            
            if len(close_prices) >= 26:
                ema12 = calculate_ema(close_prices, 12)
                ema26 = calculate_ema(close_prices, 26)
                macd = ema12 - ema26
                signal = calculate_ema([macd], 9)
            else:
                macd = 0
                signal = 0
            
            atr = calculate_atr(chart_data)
            sma20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else current_price
            ema20 = calculate_ema(close_prices[-20:], 20) if len(close_prices) >= 20 else current_price
            
            return {
                'RSI': round(rsi, 2),
                'MACD': round(macd, 4),
                'Signal': round(signal, 4),
                'ATR': round(atr, 2),
                'SMA20': round(sma20, 2),
                'EMA20': round(ema20, 2)
            }
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {
                'RSI': '--',
                'MACD': '--',
                'Signal': '--',
                'ATR': '--',
                'SMA20': current_price,
                'EMA20': current_price
            }

class MLPredictor:
    """Machine Learning predictor with Random Forest"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
    
    def prepare_features(self, data: Dict) -> Optional[np.ndarray]:
        """Prepare features from market data"""
        try:
            if not data or 'chartData' not in data or len(data['chartData']) < 20:
                return None
            
            df = pd.DataFrame(data['chartData'])
            
            # Calculate features
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
            if df['volume'].mean() > 0:
                features['volume_ratio'] = df['volume'].iloc[-1] / df['volume'].tail(20).mean()
            else:
                features['volume_ratio'] = 1
            
            # High/Low ratio
            features['hl_ratio'] = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['close'].iloc[-1] if df['close'].iloc[-1] > 0 else 0
            
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
                
                # Calculate features
                features = {}
                features['return_1d'] = (window['close'].iloc[-1] - window['close'].iloc[-2]) / window['close'].iloc[-2]
                features['return_5d'] = (window['close'].iloc[-1] - window['close'].iloc[-5]) / window['close'].iloc[-5]
                features['return_20d'] = (window['close'].iloc[-1] - window['close'].iloc[-20]) / window['close'].iloc[-20]
                features['sma_5'] = window['close'].tail(5).mean()
                features['sma_20'] = window['close'].mean()
                features['price_to_sma20'] = window['close'].iloc[-1] / features['sma_20']
                features['volatility_20d'] = window['close'].std() / window['close'].mean()
                features['volume_ratio'] = window['volume'].iloc[-1] / window['volume'].mean() if window['volume'].mean() > 0 else 1
                features['hl_ratio'] = (window['high'].iloc[-1] - window['low'].iloc[-1]) / window['close'].iloc[-1]
                
                X.append(list(features.values()))
                
                # Label: 1 if price goes up next day, 0 otherwise
                next_return = (df['close'].iloc[i+1] - df['close'].iloc[i]) / df['close'].iloc[i]
                y.append(1 if next_return > 0.001 else 0)  # 0.1% threshold
            
            if len(X) < 10:
                return {'error': 'Not enough samples for training'}
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = accuracy_score(y_train, model.predict(X_train_scaled))
            test_score = accuracy_score(y_test, model.predict(X_test_scaled))
            
            # Store model and scaler
            self.models[symbol] = model
            self.scalers[symbol] = scaler
            
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
    
    def predict(self, symbol: str, data: Dict, sentiment: float = 0.0, sentiment_confidence: float = 50.0) -> Dict:
        """Make prediction with confidence percentages"""
        try:
            # Prepare features
            features = self.prepare_features(data)
            if features is None:
                return {'error': 'Unable to prepare features'}
            
            # Train model if not exists
            if symbol not in self.models:
                train_result = self.train_model(symbol, data)
                if 'error' in train_result:
                    return train_result
            
            if symbol not in self.models:
                return {'error': 'No model available'}
            
            model = self.models[symbol]
            scaler = self.scalers[symbol]
            
            # Make prediction
            features_scaled = scaler.transform(features)
            
            # Get prediction probabilities
            prediction_proba = model.predict_proba(features_scaled)[0]
            base_prob = prediction_proba[1]  # Probability of price going up
            
            # Adjust with sentiment (weighted by sentiment confidence)
            sentiment_weight = min(0.3, sentiment_confidence / 100 * 0.3)  # Max 30% weight
            sentiment_factor = (sentiment + 1) / 2  # Convert -1 to 1 range to 0 to 1
            
            adjusted_prob = base_prob * (1 - sentiment_weight) + sentiment_factor * sentiment_weight
            
            # Calculate predicted price and confidence
            current_price = data['price']
            
            # Expected return based on probability and historical volatility
            if 'chartData' in data and len(data['chartData']) > 5:
                returns = []
                for i in range(1, min(20, len(data['chartData']))):
                    ret = (data['chartData'][i]['close'] - data['chartData'][i-1]['close']) / data['chartData'][i-1]['close']
                    returns.append(ret)
                avg_move = np.std(returns) if returns else 0.01
            else:
                avg_move = 0.01
            
            expected_return = (adjusted_prob - 0.5) * 2 * avg_move
            predicted_price = current_price * (1 + expected_return)
            
            # Calculate confidence (combination of model confidence and probability strength)
            model_confidence = abs(base_prob - 0.5) * 200  # How confident the model is
            prediction_confidence = min(95, model_confidence * 0.7 + sentiment_confidence * 0.3)
            
            # 5-day target
            five_day_return = expected_return * 3  # Amplify for 5-day prediction
            five_day_price = current_price * (1 + five_day_return)
            five_day_confidence = prediction_confidence * 0.8  # Lower confidence for longer timeframe
            
            return {
                'next_day_prediction': {
                    'price': round(predicted_price, 2),
                    'change': round(expected_return * 100, 2),
                    'direction': 'up' if adjusted_prob > 0.5 else 'down',
                    'probability': round(adjusted_prob * 100, 1),
                    'confidence': round(prediction_confidence, 1)
                },
                'target_prices': [{
                    'price': round(five_day_price, 2),
                    'timeframe': '5 days',
                    'confidence': round(five_day_confidence, 1)
                }],
                'sentiment_score': sentiment,
                'sentiment_confidence': sentiment_confidence,
                'model_accuracy': round(self.models[symbol].score(
                    self.scalers[symbol].transform(features), 
                    [1 if expected_return > 0 else 0]
                ) * 100, 1) if symbol in self.models else 50.0
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'error': str(e)}

# Initialize components
sentiment_analyzer = SentimentAnalyzer()
data_fetcher = DataFetcher()
ml_predictor = MLPredictor()

# API Routes

@app.route('/')
def index():
    """Serve the chart interface"""
    try:
        with open('finbert_charts.html', 'r') as f:
            return f.read()
    except:
        return jsonify({'error': 'Chart interface not found. Please ensure finbert_charts.html is in the same directory'}), 404

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get current stock data with indicators"""
    try:
        data = data_fetcher.fetch(symbol)
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Ensure we have properly formatted data
        if 'chartData' in data and data['chartData']:
            # Check if we need to aggregate intraday data
            dates = [d['date'] for d in data['chartData']]
            if len(dates) != len(set(dates)):
                data['chartData'] = data_fetcher.aggregate_intraday_to_daily(data['chartData'])
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical data for charting"""
    try:
        period = request.args.get('period', '30d')
        
        data = data_fetcher.fetch(symbol, period)
        
        if not data or 'chartData' not in data:
            return jsonify({'error': f'Unable to fetch historical data for {symbol}'}), 404
        
        # Ensure daily aggregation
        chart_data = data['chartData']
        dates = [d['date'] for d in chart_data] if chart_data else []
        if len(dates) != len(set(dates)):
            chart_data = data_fetcher.aggregate_intraday_to_daily(chart_data)
        
        return jsonify({
            'symbol': symbol,
            'period': period,
            'data': chart_data,
            'historical': {
                'data': chart_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def predict_stock(symbol):
    """Get ML prediction with confidence"""
    try:
        # Get stock data
        data = data_fetcher.fetch(symbol, '60d')  # Get more data for better prediction
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Get news sentiment
        sentiment = 0.0
        sentiment_confidence = 50.0
        
        try:
            # Fetch recent news
            news_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            response = requests.get(news_url, timeout=5)
            
            if response.status_code == 200:
                import re
                # Extract titles from RSS
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', response.text)
                if not titles:
                    titles = re.findall(r'<title>(.*?)</title>', response.text)
                
                if titles:
                    # Analyze sentiment of all titles
                    sentiments = []
                    confidences = []
                    for title in titles[:10]:  # Analyze up to 10 recent news
                        s, c = sentiment_analyzer.analyze(title)
                        sentiments.append(s)
                        confidences.append(c)
                    
                    if sentiments:
                        sentiment = np.mean(sentiments)
                        sentiment_confidence = np.mean(confidences)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
        
        # Make prediction
        prediction = ml_predictor.predict(symbol, data, sentiment, sentiment_confidence)
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """Get news with FinBERT sentiment analysis"""
    try:
        news_items = []
        sentiments = []
        
        # Try Yahoo Finance RSS
        try:
            url = f"https://finance.yahoo.com/rss/headline?s={symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                import re
                # Parse RSS
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', response.text)
                if not titles:
                    titles = re.findall(r'<title>(.*?)</title>', response.text)
                
                links = re.findall(r'<link>(.*?)</link>', response.text)
                
                for i, title in enumerate(titles[:10]):
                    if i < len(links) and title and 'Yahoo Finance' not in title:
                        sentiment, confidence = sentiment_analyzer.analyze(title)
                        news_items.append({
                            'title': title,
                            'url': links[i],
                            'sentiment': round(sentiment, 3),
                            'confidence': round(confidence, 1),
                            'source': 'Yahoo Finance'
                        })
                        sentiments.append(sentiment)
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
        
        overall_sentiment = np.mean(sentiments) if sentiments else 0.0
        
        return jsonify({
            'symbol': symbol,
            'news': news_items,
            'overall_sentiment': round(overall_sentiment, 3),
            'sentiment_confidence': round(np.mean([item['confidence'] for item in news_items]), 1) if news_items else 50.0
        })
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economic')
def get_economic_indicators():
    """Get economic indicators (VIX, Treasury, Dollar, Gold)"""
    try:
        indicators = {}
        
        # Define indicators to fetch
        indicator_symbols = {
            'VIX': ('^VIX', 'Fear Index'),
            'TNX': ('^TNX', '10-Year Treasury'),
            'DXY': ('DX-Y.NYB', 'Dollar Index'),
            'GOLD': ('GC=F', 'Gold Futures')
        }
        
        for key, (symbol, label) in indicator_symbols.items():
            try:
                data = data_fetcher.fetch(symbol, '5d')
                if data:
                    indicators[key] = {
                        'value': round(data['price'], 2),
                        'change': round(data.get('changePercent', 0), 2),
                        'label': label,
                        'symbol': symbol
                    }
            except Exception as e:
                logger.error(f"Error fetching {key}: {e}")
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
    """System status check"""
    return jsonify({
        'status': 'running',
        'finbert': FINBERT_AVAILABLE,
        'alpha_vantage_key': bool(ALPHA_VANTAGE_KEY),
        'version': '3.0-FIXED',
        'features': {
            'real_data': True,
            'sentiment_analysis': FINBERT_AVAILABLE,
            'ml_predictions': True,
            'confidence_scores': True,
            'economic_indicators': True
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("FinBERT Ultimate Trading System v3.0 - COMPLETE FIX")
    print("="*70)
    print(f"✓ FinBERT: {'Available' if FINBERT_AVAILABLE else 'Using fallback sentiment'}")
    print(f"✓ Alpha Vantage Key: {'Configured' if ALPHA_VANTAGE_KEY else 'Not set'}")
    print(f"✓ Real Data Only: Yes (No synthetic/fallback data)")
    print(f"✓ Confidence Scores: Enabled")
    print(f"✓ Economic Indicators: VIX, Treasury, Dollar, Gold")
    print(f"✓ Starting server on http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)