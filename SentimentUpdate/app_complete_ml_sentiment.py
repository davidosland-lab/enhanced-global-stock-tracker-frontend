#!/usr/bin/env python3
"""
COMPLETE Stock Analysis with ML, Sentiment, and Charts
All features integrated with proper rate limiting
"""

import os
import sys
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from functools import lru_cache
import warnings
import requests

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("COMPLETE STOCK ANALYSIS WITH ML & SENTIMENT")
print("=" * 60)
print("Features:")
print("✓ Full charting with candlesticks and line charts")
print("✓ ML predictions with RandomForest")
print("✓ Market sentiment analysis")
print("✓ Technical indicators")
print("✓ Rate limiting protection")
print("✓ Australian stocks support")
print("=" * 60)
print("Starting server at http://localhost:5000")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Rate limiting
last_request = {}
MIN_DELAY = 2.0  # 2 seconds between requests

def rate_limit(symbol):
    """Enforce rate limiting"""
    global last_request
    now = time.time()
    key = symbol.upper()
    
    if key in last_request:
        elapsed = now - last_request[key]
        if elapsed < MIN_DELAY:
            wait = MIN_DELAY - elapsed
            print(f"Rate limit: waiting {wait:.1f}s...")
            time.sleep(wait)
    
    last_request[key] = time.time()

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG',
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL'
}

# Try to import sklearn
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
    print("✓ ML with scikit-learn available")
except ImportError:
    ML_AVAILABLE = False
    print("⚠ scikit-learn not available - using simple predictions")

class MarketSentimentAnalyzer:
    """Market sentiment with rate limiting"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_fetch = {}
        
    @lru_cache(maxsize=10)
    def get_vix_fear_gauge(self):
        """Get VIX with caching"""
        try:
            rate_limit("^VIX")
            ticker = yf.Ticker("^VIX")
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                vix = float(hist['Close'].iloc[-1])
                
                if vix < 12:
                    sentiment = "Extreme Greed"
                    score = 0.9
                elif vix < 20:
                    sentiment = "Low Fear"
                    score = 0.5
                elif vix < 30:
                    sentiment = "Moderate Fear"
                    score = -0.3
                elif vix < 40:
                    sentiment = "High Fear"
                    score = -0.7
                else:
                    sentiment = "Extreme Fear"
                    score = -0.9
                    
                return {
                    'value': vix,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"VIX at {vix:.2f}"
                }
        except Exception as e:
            print(f"VIX error: {e}")
            
        return {
            'value': 20.0,
            'sentiment': 'Neutral',
            'score': 0,
            'description': 'VIX unavailable'
        }
    
    def get_market_breadth(self):
        """Get market breadth"""
        try:
            indices = ['^GSPC', '^DJI', '^IXIC']
            advances = 0
            declines = 0
            
            for idx in indices:
                try:
                    rate_limit(idx)
                    ticker = yf.Ticker(idx)
                    hist = ticker.history(period="2d")
                    
                    if len(hist) >= 2:
                        if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                            advances += 1
                        else:
                            declines += 1
                except:
                    pass
            
            if advances + declines > 0:
                ratio = advances / (advances + declines)
                
                if ratio > 0.7:
                    sentiment = "Bullish"
                    score = 0.5
                elif ratio > 0.3:
                    sentiment = "Neutral"
                    score = 0
                else:
                    sentiment = "Bearish"
                    score = -0.5
                    
                return {
                    'advances': advances,
                    'declines': declines,
                    'ratio': ratio,
                    'sentiment': sentiment,
                    'score': score
                }
        except Exception as e:
            print(f"Breadth error: {e}")
            
        return {
            'advances': 1,
            'declines': 1,
            'ratio': 0.5,
            'sentiment': 'Neutral',
            'score': 0
        }
    
    def get_combined_sentiment(self):
        """Combine all sentiment indicators"""
        vix = self.get_vix_fear_gauge()
        breadth = self.get_market_breadth()
        
        # Calculate weighted score
        total_score = (vix['score'] * 0.6 + breadth['score'] * 0.4)
        
        if total_score > 0.3:
            sentiment = "Bullish"
        elif total_score < -0.3:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"
            
        return {
            'score': total_score,
            'sentiment': sentiment,
            'components': {
                'vix': vix,
                'market_breadth': breadth
            },
            'timestamp': datetime.now().isoformat()
        }

class DataFetcher:
    """Fetch data with fallbacks"""
    
    def __init__(self):
        self.alpha_vantage_key = "68ZFANK047DL0KSR"
        
    def fetch_yahoo(self, symbol, period="1mo", interval="1d"):
        """Try Yahoo Finance first"""
        try:
            # Handle Australian stocks
            original = symbol.upper()
            if original in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
                symbol = f"{original}.AX"
                print(f"Australian stock: {original} -> {symbol}")
            
            rate_limit(symbol)
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                current_price = float(df['Close'].iloc[-1])
                return df, "Yahoo Finance", current_price
                
        except Exception as e:
            print(f"Yahoo error: {e}")
            
        return None, None, None
    
    def fetch_alpha_vantage(self, symbol):
        """Fallback to Alpha Vantage"""
        try:
            time.sleep(1)  # Alpha Vantage rate limit
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
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
                current_price = float(df['Close'].iloc[-1])
                return df, "Alpha Vantage", current_price
                
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
            
        return None, None, None
    
    def fetch_data(self, symbol, period="1mo", interval="1d"):
        """Fetch with fallback"""
        # Try Yahoo first
        df, source, price = self.fetch_yahoo(symbol, period, interval)
        
        # Fallback to Alpha Vantage
        if df is None:
            print(f"Yahoo failed, trying Alpha Vantage...")
            df, source, price = self.fetch_alpha_vantage(symbol)
            
        return df, source, price

class TechnicalAnalyzer:
    """Technical indicators"""
    
    def calculate_all(self, df):
        if df is None or df.empty:
            return {}
            
        indicators = {}
        
        # RSI
        if len(df) >= 14:
            indicators['rsi'] = self.calculate_rsi(df)
            
        # Moving averages
        if len(df) >= 20:
            indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        if len(df) >= 50:
            indicators['sma_50'] = float(df['Close'].rolling(50).mean().iloc[-1])
        if len(df) >= 10:
            indicators['sma_10'] = float(df['Close'].rolling(10).mean().iloc[-1])
            
        # MACD
        if len(df) >= 26:
            exp12 = df['Close'].ewm(span=12).mean()
            exp26 = df['Close'].ewm(span=26).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9).mean()
            indicators['macd'] = {
                'macd': float(macd.iloc[-1]),
                'signal': float(signal.iloc[-1]),
                'histogram': float((macd - signal).iloc[-1])
            }
            
        # Bollinger Bands
        if len(df) >= 20:
            sma = df['Close'].rolling(20).mean()
            std = df['Close'].rolling(20).std()
            indicators['bollinger'] = {
                'upper': float(sma.iloc[-1] + 2 * std.iloc[-1]),
                'middle': float(sma.iloc[-1]),
                'lower': float(sma.iloc[-1] - 2 * std.iloc[-1])
            }
            
        return indicators
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        
        if loss.iloc[-1] == 0:
            return 100.0
            
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

class MLPredictor:
    """ML predictions with sentiment"""
    
    def __init__(self):
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        if ML_AVAILABLE:
            self.model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
            self.scaler = StandardScaler()
            
    def prepare_features(self, df):
        """Prepare features for ML"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Technical features
        features['rsi'] = self.calculate_rsi_series(df)
        features['sma_ratio'] = df['Close'] / df['Close'].rolling(20).mean()
        
        # Price patterns
        features['high_low'] = (df['High'] - df['Low']) / df['Close']
        features['close_open'] = (df['Close'] - df['Open']) / df['Open']
        
        return features.fillna(0)
    
    def calculate_rsi_series(self, df, period=14):
        """RSI as series"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def train_and_predict(self, df, days=5):
        """Train model and predict"""
        if not ML_AVAILABLE or df is None or len(df) < 30:
            return self.simple_predict(df, days)
            
        try:
            # Prepare features
            X = self.prepare_features(df)
            y = df['Close'].shift(-1)
            
            # Remove NaN
            valid = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid]
            y = y[valid]
            
            if len(X) < 20:
                return self.simple_predict(df, days)
                
            # Scale and train
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            
            # Get sentiment
            sentiment = self.sentiment_analyzer.get_combined_sentiment()
            
            # Predict
            predictions = []
            last_features = X.iloc[-1:].values
            current_price = float(df['Close'].iloc[-1])
            
            for i in range(1, days + 1):
                # Predict next price
                pred = self.model.predict(self.scaler.transform(last_features))[0]
                
                # Apply sentiment adjustment
                sentiment_factor = 1 + (sentiment['score'] * 0.02)
                pred = pred * sentiment_factor
                
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'predicted_price': round(pred, 2),
                    'confidence': 0.7 + min(0.2, abs(sentiment['score']) * 0.2),
                    'method': 'RandomForest + Sentiment'
                })
                
                # Update features
                last_features[0][0] = (pred - current_price) / current_price
                current_price = pred
                
            # Add feature importance
            importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return predictions, importance.to_dict('records')
            
        except Exception as e:
            print(f"ML error: {e}")
            return self.simple_predict(df, days), []
    
    def simple_predict(self, df, days):
        """Simple trend prediction"""
        if df is None or df.empty:
            return [], []
            
        # Calculate trend
        if len(df) >= 5:
            trend = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
            daily_trend = trend / 5
        else:
            daily_trend = 0
            
        # Get sentiment
        sentiment = self.sentiment_analyzer.get_combined_sentiment()
        sentiment_factor = 1 + (sentiment['score'] * 0.01)
        
        predictions = []
        current_price = float(df['Close'].iloc[-1])
        
        for i in range(1, days + 1):
            pred = current_price * (1 + daily_trend * i) * sentiment_factor
            predictions.append({
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(pred, 2),
                'confidence': 0.5,
                'method': 'Trend + Sentiment'
            })
            
        return predictions, []

# Global instances
data_fetcher = DataFetcher()
tech_analyzer = TechnicalAnalyzer()
ml_predictor = MLPredictor()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Complete stock analysis endpoint"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch data
        df, source, current_price = data_fetcher.fetch_data(symbol, period, interval)
        
        if df is None:
            return jsonify({
                'error': 'Unable to fetch data',
                'symbol': symbol,
                'message': 'Try again or check symbol'
            }), 404
            
        # Technical indicators
        indicators = tech_analyzer.calculate_all(df)
        
        # ML predictions with sentiment
        predictions, feature_importance = ml_predictor.train_and_predict(df, days=5)
        
        # Get sentiment
        sentiment = ml_predictor.sentiment_analyzer.get_combined_sentiment()
        
        # Prepare candlestick data
        candlestick_data = []
        for index, row in df.iterrows():
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
            
        return jsonify({
            'symbol': symbol,
            'source': source,
            'current_price': current_price,
            'data': candlestick_data,
            'indicators': indicators,
            'predictions': predictions,
            'feature_importance': feature_importance,
            'sentiment': sentiment
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Get market sentiment"""
    try:
        analyzer = MarketSentimentAnalyzer()
        sentiment = analyzer.get_combined_sentiment()
        return jsonify(sentiment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    """Main page with full charts"""
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Complete Stock Analysis - ML & Sentiment</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        .sentiment-dashboard {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .sentiment-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .sentiment-value {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .bullish { color: #10b981; }
        .bearish { color: #ef4444; }
        .neutral { color: #f59e0b; }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .input-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            padding: 12px 30px;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .chart-controls {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .chart-btn {
            padding: 8px 16px;
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            cursor: pointer;
        }
        .chart-btn.active {
            background: #667eea;
            color: white;
        }
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            height: 500px;
        }
        .info-panel {
            background: white;
            padding: 20px;
            border-radius: 15px;
        }
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .indicator-item {
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .prediction-item {
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Complete Stock Analysis</h1>
            <p>ML Predictions + Market Sentiment + Full Charts</p>
        </div>
        
        <!-- Market Sentiment Dashboard -->
        <div class="sentiment-dashboard">
            <h2>Market Sentiment</h2>
            <div class="sentiment-grid" id="sentimentGrid">
                <div class="sentiment-card">
                    <div>Overall Sentiment</div>
                    <div class="sentiment-value neutral" id="overallSentiment">Loading...</div>
                </div>
            </div>
        </div>
        
        <!-- Controls -->
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Symbol (e.g., AAPL, CBA)" value="AAPL">
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <select id="interval">
                    <option value="1m">1 Minute</option>
                    <option value="5m">5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="1h">1 Hour</option>
                    <option value="1d" selected>Daily</option>
                </select>
                <button onclick="fetchData()">Get Analysis</button>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div>
                <!-- Chart Type Controls -->
                <div class="chart-controls">
                    <button class="chart-btn active" onclick="switchChart('candlestick')">Candlestick</button>
                    <button class="chart-btn" onclick="switchChart('line')">Line</button>
                    <button class="chart-btn" onclick="switchChart('volume')">Volume</button>
                    <button class="chart-btn" onclick="resetZoom()">Reset Zoom</button>
                </div>
                
                <div class="chart-container">
                    <canvas id="stockChart"></canvas>
                </div>
            </div>
            
            <div class="info-panel">
                <div class="price-display" id="priceDisplay">--</div>
                <div id="source" style="color: #666; margin-bottom: 20px;">--</div>
                
                <h3>Technical Indicators</h3>
                <div id="indicators"></div>
                
                <h3 style="margin-top: 20px;">ML Predictions</h3>
                <div id="predictions"></div>
                
                <h3 style="margin-top: 20px;">Feature Importance</h3>
                <div id="features"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentChart = null;
        let chartType = 'candlestick';
        let currentData = null;
        
        // Load sentiment on start
        window.onload = function() {
            loadSentiment();
            setInterval(loadSentiment, 60000); // Refresh every minute
        };
        
        async function loadSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                updateSentiment(data);
            } catch (error) {
                console.error('Sentiment error:', error);
            }
        }
        
        function updateSentiment(data) {
            const element = document.getElementById('overallSentiment');
            element.textContent = data.sentiment + ' (' + data.score.toFixed(2) + ')';
            element.className = 'sentiment-value ' + 
                (data.score > 0.3 ? 'bullish' : data.score < -0.3 ? 'bearish' : 'neutral');
            
            // Update grid with components
            const grid = document.getElementById('sentimentGrid');
            let html = `
                <div class="sentiment-card">
                    <div>Overall</div>
                    <div class="sentiment-value ${data.score > 0.3 ? 'bullish' : data.score < -0.3 ? 'bearish' : 'neutral'}">
                        ${data.sentiment}
                    </div>
                </div>
            `;
            
            if (data.components) {
                if (data.components.vix) {
                    html += `
                        <div class="sentiment-card">
                            <div>VIX Fear</div>
                            <div class="sentiment-value">${data.components.vix.value?.toFixed(2) || 'N/A'}</div>
                            <small>${data.components.vix.sentiment}</small>
                        </div>
                    `;
                }
                if (data.components.market_breadth) {
                    const b = data.components.market_breadth;
                    html += `
                        <div class="sentiment-card">
                            <div>Market Breadth</div>
                            <div class="sentiment-value">${b.advances}/${b.declines}</div>
                            <small>${b.sentiment}</small>
                        </div>
                    `;
                }
            }
            
            grid.innerHTML = html;
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=${interval}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                currentData = data;
                
                // Update display
                document.getElementById('priceDisplay').textContent = '$' + data.current_price.toFixed(2);
                document.getElementById('source').textContent = 'Source: ' + data.source;
                
                // Update chart
                updateChart();
                
                // Update indicators
                let indicatorHtml = '';
                if (data.indicators) {
                    for (const [key, value] of Object.entries(data.indicators)) {
                        if (typeof value === 'number') {
                            indicatorHtml += `
                                <div class="indicator-item">
                                    <strong>${key}:</strong> ${value.toFixed(2)}
                                </div>
                            `;
                        } else if (value.macd) {
                            indicatorHtml += `
                                <div class="indicator-item">
                                    <strong>MACD:</strong> ${value.macd.toFixed(2)}
                                </div>
                            `;
                        }
                    }
                }
                document.getElementById('indicators').innerHTML = indicatorHtml || 'No indicators';
                
                // Update predictions
                let predHtml = '';
                if (data.predictions && data.predictions.length > 0) {
                    data.predictions.forEach(p => {
                        predHtml += `
                            <div class="prediction-item">
                                <strong>${p.date}</strong><br>
                                $${p.predicted_price} 
                                (${(p.confidence * 100).toFixed(0)}% conf)<br>
                                <small>${p.method || ''}</small>
                            </div>
                        `;
                    });
                }
                document.getElementById('predictions').innerHTML = predHtml || 'No predictions';
                
                // Update features
                let featureHtml = '';
                if (data.feature_importance && data.feature_importance.length > 0) {
                    data.feature_importance.slice(0, 5).forEach(f => {
                        const width = (f.importance * 100 / data.feature_importance[0].importance);
                        featureHtml += `
                            <div class="indicator-item">
                                ${f.feature}
                                <div style="background: linear-gradient(90deg, #667eea ${width}%, #f0f0f0 ${width}%); height: 4px; margin-top: 4px;"></div>
                            </div>
                        `;
                    });
                }
                document.getElementById('features').innerHTML = featureHtml || 'Using simple predictions';
                
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        function updateChart() {
            if (!currentData) return;
            
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (currentChart) {
                currentChart.destroy();
            }
            
            if (chartType === 'candlestick') {
                currentChart = new Chart(ctx, {
                    type: 'candlestick',
                    data: {
                        datasets: [{
                            label: currentData.symbol,
                            data: currentData.data.map(d => ({
                                x: new Date(d.date).getTime(),
                                o: d.open,
                                h: d.high,
                                l: d.low,
                                c: d.close
                            }))
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            zoom: {
                                zoom: {
                                    enabled: true,
                                    mode: 'x'
                                },
                                pan: {
                                    enabled: true,
                                    mode: 'x'
                                }
                            }
                        }
                    }
                });
            } else if (chartType === 'line') {
                currentChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: currentData.data.map(d => new Date(d.date).toLocaleDateString()),
                        datasets: [{
                            label: 'Close Price',
                            data: currentData.data.map(d => d.close),
                            borderColor: '#667eea',
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            zoom: {
                                zoom: {
                                    enabled: true,
                                    mode: 'x'
                                },
                                pan: {
                                    enabled: true,
                                    mode: 'x'
                                }
                            }
                        }
                    }
                });
            } else if (chartType === 'volume') {
                currentChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: currentData.data.map(d => new Date(d.date).toLocaleDateString()),
                        datasets: [{
                            label: 'Volume',
                            data: currentData.data.map(d => d.volume),
                            backgroundColor: '#667eea'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        }
        
        function switchChart(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            updateChart();
        }
        
        function resetZoom() {
            if (currentChart) {
                currentChart.resetZoom();
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)