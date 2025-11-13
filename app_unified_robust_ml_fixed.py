#!/usr/bin/env python3
"""
Unified Robust Stock Analysis System - ML ACTUALLY FIXED
- ML predictions work WITHOUT fetching sentiment data during training
- Sentiment is a separate feature, not required for ML
- 100% Real Market Data (NO synthetic/demo data)
"""

import os
import sys
import time
import json
import warnings
import traceback
import threading
from datetime import datetime, timedelta
from functools import lru_cache
import requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Import sklearn components conditionally
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: scikit-learn not available. ML predictions disabled.")

print("=" * 80)
print("UNIFIED ROBUST STOCK ANALYSIS SYSTEM - ML ACTUALLY FIXED")
print("=" * 80)
print("✓ ML predictions work INDEPENDENTLY from sentiment")
print("✓ No API calls during ML training")
print("✓ 100% Real Market Data")
print("✓ Yahoo Finance + Alpha Vantage")
print(f"✓ ML Available: {ML_AVAILABLE}")
print("=" * 80)

app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
YAHOO_REQUEST_DELAY = 3
AV_REQUEST_DELAY = 0.2

# Rate limiting
last_yahoo_request = 0
last_av_request = 0
request_lock = threading.Lock()

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

class UnifiedDataFetcher:
    """Data fetcher - unchanged from working version"""
    
    def __init__(self):
        self.yahoo_available = self._check_yahoo()
        
    def _check_yahoo(self):
        try:
            import yfinance as yf
            return True
        except ImportError:
            print("WARNING: yfinance not installed.")
            return False
    
    def _yahoo_rate_limit(self):
        global last_yahoo_request
        with request_lock:
            now = time.time()
            elapsed = now - last_yahoo_request
            if elapsed < YAHOO_REQUEST_DELAY:
                time.sleep(YAHOO_REQUEST_DELAY - elapsed)
            last_yahoo_request = time.time()
    
    def fetch_yahoo(self, symbol, period='1mo'):
        if not self.yahoo_available:
            return None
        
        try:
            import yfinance as yf
            
            original_symbol = symbol.upper()
            if original_symbol in AUSTRALIAN_STOCKS and not original_symbol.endswith('.AX'):
                symbol = f"{original_symbol}.AX"
            
            self._yahoo_rate_limit()
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if not df.empty:
                return df, "Yahoo Finance"
                
        except Exception as e:
            print(f"Yahoo error for {symbol}: {e}")
        
        return None, None
    
    def fetch_alpha_vantage(self, symbol):
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_KEY,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                ts = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(ts, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                return df, "Alpha Vantage"
                
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
        
        return None, None
    
    def fetch(self, symbol, period='1mo'):
        print(f"Fetching data for {symbol}...")
        
        df, source = self.fetch_yahoo(symbol, period)
        
        if df is None or df.empty:
            print(f"Yahoo failed, trying Alpha Vantage...")
            df, source = self.fetch_alpha_vantage(symbol)
        
        if df is not None and not df.empty:
            print(f"✓ Data fetched from {source}: {len(df)} records")
        
        return df, source

class TechnicalAnalysis:
    """Technical indicators - working version"""
    
    @staticmethod
    def calculate_all(df):
        indicators = {}
        
        try:
            # RSI
            if len(df) >= 14:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / (loss + 1e-10)
                indicators['RSI'] = float(100 - (100 / (1 + rs)).iloc[-1])
            
            # Moving averages
            if len(df) >= 20:
                indicators['SMA_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
            if len(df) >= 50:
                indicators['SMA_50'] = float(df['Close'].rolling(50).mean().iloc[-1])
            
            # Price change
            if len(df) >= 2:
                change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
                indicators['Change_%'] = float(change)
                
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators

class SimpleMLPredictor:
    """FIXED ML Predictor - works independently, no sentiment fetching during training"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.available = ML_AVAILABLE
        self.last_symbol = None
        self.training_in_progress = False
    
    def prepare_features(self, df):
        """Prepare ONLY technical features - NO API calls"""
        if len(df) < 50:
            return None
            
        features = pd.DataFrame(index=df.index)
        
        try:
            # Basic features
            features['returns'] = df['Close'].pct_change()
            features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Moving averages
            features['sma_5'] = df['Close'].rolling(5).mean()
            features['sma_20'] = df['Close'].rolling(20).mean()
            features['price_to_sma5'] = df['Close'] / features['sma_5']
            features['price_to_sma20'] = df['Close'] / features['sma_20']
            
            # Volatility
            features['volatility'] = features['returns'].rolling(20).std()
            
            # RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            features['rsi'] = 100 - (100 / (1 + rs))
            
            # Volume features (if available)
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            
            # Price features
            features['high_low_ratio'] = df['High'] / (df['Low'] + 1e-10)
            features['close_to_high'] = df['Close'] / (df['High'] + 1e-10)
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                features[f'return_lag_{lag}'] = features['returns'].shift(lag)
            
            # Clean up
            features = features.replace([np.inf, -np.inf], np.nan)
            features = features.dropna()
            
            return features
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            return None
    
    def train_and_predict(self, df, symbol):
        """Train model and make predictions in one go"""
        if not self.available:
            return {
                'error': 'ML not available (install scikit-learn)',
                'available': False
            }
        
        if self.training_in_progress:
            return {
                'error': 'Training already in progress',
                'available': False
            }
        
        try:
            self.training_in_progress = True
            print(f"Training model for {symbol}...")
            
            # Prepare features
            features = self.prepare_features(df)
            if features is None or len(features) < 60:
                return {
                    'error': 'Insufficient data for training',
                    'available': False
                }
            
            # Create target
            y = df['Close'].pct_change().shift(-1).loc[features.index]
            
            # Remove last row (no target)
            features = features[:-1]
            y = y[:-1]
            
            # Remove NaN targets
            valid_idx = ~y.isna()
            features = features[valid_idx]
            y = y[valid_idx]
            
            if len(features) < 50:
                return {
                    'error': 'Insufficient valid samples',
                    'available': False
                }
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features[:split_idx]
            y_train = y[:split_idx]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Train simple model
            self.model = RandomForestRegressor(
                n_estimators=30,  # Reduced for speed
                max_depth=5,
                min_samples_split=10,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)
            
            print(f"Model trained for {symbol}")
            
            # Make predictions
            latest_features = features.iloc[-1:].values
            latest_features_scaled = self.scaler.transform(latest_features)
            
            current_price = float(df['Close'].iloc[-1])
            next_return = self.model.predict(latest_features_scaled)[0]
            
            # Simple predictions
            predictions = []
            for days in [1, 3, 5, 7]:
                # Simple projection
                projected_return = next_return * np.sqrt(days)
                projected_price = current_price * (1 + projected_return)
                
                predictions.append({
                    'days': days,
                    'price': float(projected_price),
                    'return': float(projected_return * 100),
                    'confidence': max(30, 70 - days * 5)
                })
            
            return {
                'predictions': predictions,
                'current_price': current_price,
                'symbol': symbol,
                'available': True
            }
            
        except Exception as e:
            print(f"ML error: {e}")
            traceback.print_exc()
            return {
                'error': str(e),
                'available': False
            }
        finally:
            self.training_in_progress = False

class MarketSentimentAnalyzer:
    """Sentiment analyzer - SEPARATE from ML, called only when needed"""
    
    def __init__(self):
        self.fetcher = UnifiedDataFetcher()
    
    def get_vix(self):
        """Get VIX - only when explicitly requested"""
        try:
            df, source = self.fetcher.fetch_yahoo('^VIX', period='5d')
            if df is not None and not df.empty:
                current_vix = df['Close'].iloc[-1]
                
                if current_vix < 20:
                    sentiment = "Low Fear"
                elif current_vix < 30:
                    sentiment = "Moderate Fear"
                else:
                    sentiment = "High Fear"
                
                return {
                    'value': float(current_vix),
                    'sentiment': sentiment
                }
        except Exception as e:
            print(f"VIX error: {e}")
        return None
    
    def get_market_breadth(self):
        """Get S&P 500 as market breadth proxy"""
        try:
            df, source = self.fetcher.fetch_yahoo('^GSPC', period='5d')
            if df is not None and not df.empty:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2] if len(df) > 1 else current
                change = ((current - prev) / prev) * 100
                
                return {
                    'sp500': float(current),
                    'change': float(change),
                    'sentiment': 'Bullish' if change > 0 else 'Bearish'
                }
        except Exception as e:
            print(f"Market breadth error: {e}")
        return None

# Global instances
data_fetcher = UnifiedDataFetcher()
ml_predictor = SimpleMLPredictor()
sentiment_analyzer = MarketSentimentAnalyzer()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data"""
    try:
        period = request.args.get('period', '1mo')
        
        df, source = data_fetcher.fetch(symbol, period)
        
        if df is None or df.empty:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Calculate indicators
        indicators = TechnicalAnalysis.calculate_all(df)
        
        # Prepare chart data
        chart_data = []
        labels = []
        
        for i, (index, row) in enumerate(df.tail(60).iterrows()):
            chart_data.append({
                'x': i,
                'close': float(row['Close']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': float(row.get('Volume', 0))
            })
            labels.append(index.strftime('%m/%d'))
        
        current_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
        
        return jsonify({
            'symbol': symbol,
            'source': source,
            'current_price': current_price,
            'price_change': current_price - prev_close,
            'price_change_pct': ((current_price - prev_close) / prev_close) * 100,
            'data': chart_data,
            'labels': labels,
            'indicators': indicators
        })
        
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def get_predictions(symbol):
    """ML predictions - FIXED to work independently"""
    try:
        print(f"\n=== ML Prediction Request for {symbol} ===")
        
        # Fetch MORE data for better training
        df, source = data_fetcher.fetch(symbol, period='1y')
        
        if df is None or df.empty:
            print(f"No data available for {symbol}")
            return jsonify({
                'error': f'No data available for {symbol}',
                'available': False
            }), 404
        
        print(f"Data fetched: {len(df)} records from {source}")
        
        # Train and predict
        result = ml_predictor.train_and_predict(df, symbol)
        
        # Add source
        result['source'] = source
        
        if result.get('available'):
            print(f"✓ ML predictions generated for {symbol}")
        else:
            print(f"✗ ML failed: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR in get_predictions: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'available': False
        }), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Get market sentiment - SEPARATE from ML"""
    try:
        sentiment_data = {}
        
        vix = sentiment_analyzer.get_vix()
        if vix:
            sentiment_data['vix'] = vix
        
        breadth = sentiment_analyzer.get_market_breadth()
        if breadth:
            sentiment_data['market_breadth'] = breadth
        
        return jsonify(sentiment_data)
        
    except Exception as e:
        print(f"Sentiment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ml_available': ML_AVAILABLE,
        'version': '2.0-fixed'
    })

@app.route('/')
def index():
    """Simple working interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - ML Fixed</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; }
        .controls { margin: 20px 0; }
        input, button { padding: 10px; margin: 5px; font-size: 16px; }
        button { background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #764ba2; }
        #results { background: #f0f0f0; padding: 20px; border-radius: 10px; min-height: 200px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Stock Analysis - ML Actually Fixed</h1>
        <p>ML works independently from sentiment • No API calls during training</p>
    </div>
    
    <div class="controls">
        <input type="text" id="symbol" value="AAPL" placeholder="Symbol">
        <button onclick="getStock()">Get Stock</button>
        <button onclick="getPredictions()">Get ML Predictions</button>
        <button onclick="getSentiment()">Get Sentiment</button>
    </div>
    
    <div id="results"></div>
    
    <script>
        async function getStock() {
            const symbol = document.getElementById('symbol').value;
            const res = document.getElementById('results');
            res.innerHTML = 'Loading stock data...';
            
            try {
                const response = await fetch('/api/stock/' + symbol);
                const data = await response.json();
                
                if (response.ok) {
                    res.innerHTML = '<div class="success">✓ Stock Data</div>' +
                        '<p>Price: $' + data.current_price.toFixed(2) + '</p>' +
                        '<p>Change: ' + data.price_change_pct.toFixed(2) + '%</p>' +
                        '<p>Source: ' + data.source + '</p>';
                } else {
                    res.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                }
            } catch (e) {
                res.innerHTML = '<div class="error">Network error: ' + e + '</div>';
            }
        }
        
        async function getPredictions() {
            const symbol = document.getElementById('symbol').value;
            const res = document.getElementById('results');
            res.innerHTML = 'Training ML model and generating predictions... (10-15 seconds)';
            
            try {
                console.log('Fetching predictions for', symbol);
                const response = await fetch('/api/predict/' + symbol);
                console.log('Response status:', response.status);
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok && data.available) {
                    let html = '<div class="success">✓ ML Predictions Generated</div>';
                    html += '<p>Current Price: $' + data.current_price.toFixed(2) + '</p>';
                    data.predictions.forEach(p => {
                        html += '<p>' + p.days + ' Day: $' + p.price.toFixed(2) + 
                                ' (' + (p.return >= 0 ? '+' : '') + p.return.toFixed(2) + '%)</p>';
                    });
                    res.innerHTML = html;
                } else {
                    res.innerHTML = '<div class="error">ML Error: ' + (data.error || 'Unknown') + '</div>';
                }
            } catch (e) {
                console.error('Error:', e);
                res.innerHTML = '<div class="error">Network error: ' + e + '</div>';
            }
        }
        
        async function getSentiment() {
            const res = document.getElementById('results');
            res.innerHTML = 'Loading sentiment...';
            
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                
                let html = '<div class="success">✓ Market Sentiment</div>';
                if (data.vix) {
                    html += '<p>VIX: ' + data.vix.value.toFixed(2) + ' (' + data.vix.sentiment + ')</p>';
                }
                if (data.market_breadth) {
                    html += '<p>S&P 500: ' + data.market_breadth.sp500.toFixed(2) + 
                            ' (' + data.market_breadth.change.toFixed(2) + '%)</p>';
                }
                res.innerHTML = html;
            } catch (e) {
                res.innerHTML = '<div class="error">Error: ' + e + '</div>';
            }
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    print("\nStarting server on http://localhost:5000")
    print("ML predictions now work INDEPENDENTLY from sentiment")
    print("No API calls during ML training\n")
    app.run(host='0.0.0.0', port=5000, debug=False)