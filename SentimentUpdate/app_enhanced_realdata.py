#!/usr/bin/env python3
"""
Stock Analysis with Market Sentiment - REAL DATA ONLY
No synthetic, demo, or fake data - only real market information
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

# Skip dotenv to avoid encoding issues on Windows
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS WITH MARKET SENTIMENT - REAL DATA ONLY")
print("=" * 60)
print("Features:")
print("✓ 100% Real market data")
print("✓ Rate limiting protection")
print("✓ Proper error reporting")
print("✓ No synthetic/demo data")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("Press Ctrl+C to stop")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Rate limiting
last_request_time = {}
MIN_REQUEST_INTERVAL = 0.5  # Half second between requests

def rate_limit_check(symbol):
    """Enforce rate limiting"""
    global last_request_time
    now = time.time()
    if symbol in last_request_time:
        elapsed = now - last_request_time[symbol]
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    last_request_time[symbol] = time.time()

# Australian stock symbols
AUSTRALIAN_SYMBOLS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 'GMG', 'TCL',
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL', 'IAG', 'QBE'
}

class MarketSentimentAnalyzer:
    """Real market sentiment from actual data sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def get_vix_fear_gauge(self):
        """Get real VIX data"""
        try:
            rate_limit_check("^VIX")
            ticker = yf.Ticker("^VIX")
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
                
            current_vix = float(hist['Close'].iloc[-1])
            
            # Real VIX interpretation
            if current_vix < 12:
                sentiment = "Extreme Greed"
                score = 0.9
            elif current_vix < 20:
                sentiment = "Low Fear"
                score = 0.5
            elif current_vix < 30:
                sentiment = "Moderate Fear"
                score = -0.3
            elif current_vix < 40:
                sentiment = "High Fear"
                score = -0.7
            else:
                sentiment = "Extreme Fear"
                score = -0.9
                
            return {
                'value': current_vix,
                'sentiment': sentiment,
                'score': score,
                'description': f"VIX at {current_vix:.2f}"
            }
        except Exception as e:
            print(f"VIX fetch error: {e}")
            return None
    
    def get_market_breadth(self):
        """Get real market breadth"""
        try:
            indices = ['^GSPC', '^DJI', '^IXIC']
            advances = 0
            declines = 0
            
            for idx in indices:
                rate_limit_check(idx)
                ticker = yf.Ticker(idx)
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2:
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                        advances += 1
                    else:
                        declines += 1
            
            if advances + declines == 0:
                return None
                
            ratio = advances / (advances + declines)
            
            if ratio > 0.7:
                sentiment = "Bullish Breadth"
                score = 0.5
            elif ratio > 0.3:
                sentiment = "Neutral Breadth"
                score = 0
            else:
                sentiment = "Bearish Breadth"
                score = -0.5
                
            return {
                'advances': advances,
                'declines': declines,
                'ratio': ratio,
                'sentiment': sentiment,
                'score': score,
                'description': f"{advances} advancing vs {declines} declining"
            }
        except Exception as e:
            print(f"Breadth error: {e}")
            return None
    
    def get_bond_yields(self):
        """Get real Treasury yields"""
        try:
            rate_limit_check("^TNX")
            ticker = yf.Ticker("^TNX")
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
                
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[0]) if len(hist) > 1 else current
            change = current - prev
            
            if abs(change) < 0.05:
                sentiment = "Stable"
                score = 0
            elif change > 0.1:
                sentiment = "Rising"
                score = 0.3
            else:
                sentiment = "Falling"
                score = -0.3
                
            return {
                'current': current,
                'change': change,
                'sentiment': sentiment,
                'score': score,
                'description': f"10Y at {current:.2f}%"
            }
        except Exception as e:
            print(f"Yield error: {e}")
            return None
    
    def get_combined_sentiment(self):
        """Combine available sentiment indicators"""
        vix = self.get_vix_fear_gauge()
        breadth = self.get_market_breadth()
        yields = self.get_bond_yields()
        
        components = {}
        total_score = 0
        count = 0
        
        if vix:
            components['vix'] = vix
            total_score += vix['score'] * 0.4
            count += 1
            
        if breadth:
            components['market_breadth'] = breadth
            total_score += breadth['score'] * 0.3
            count += 1
            
        if yields:
            components['bond_yields'] = yields
            total_score += yields['score'] * 0.3
            count += 1
        
        if count > 0:
            # Normalize score
            total_score = total_score * (3 / count) / 3
            
            if total_score > 0.3:
                sentiment = "Bullish"
            elif total_score < -0.3:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"
        else:
            sentiment = "No Data"
            total_score = 0
            
        return {
            'score': total_score,
            'sentiment': sentiment,
            'components': components,
            'indicators_available': count,
            'timestamp': datetime.now().isoformat()
        }

class RealDataFetcher:
    """Fetch only real market data"""
    
    def __init__(self):
        self.alpha_vantage_key = "68ZFANK047DL0KSR"
        
    def fetch_data(self, symbol, period="1mo", interval="1d"):
        """Fetch real data only"""
        original_symbol = symbol
        
        # Handle Australian stocks
        if symbol.upper() in AUSTRALIAN_SYMBOLS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
        
        # Try Yahoo Finance with rate limiting
        try:
            rate_limit_check(symbol)
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                # Get current price
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not current_price and not df.empty:
                    current_price = float(df['Close'].iloc[-1])
                    
                return df, "Yahoo Finance", current_price
        except Exception as e:
            print(f"Yahoo error for {symbol}: {e}")
        
        # Try Alpha Vantage as backup
        try:
            time.sleep(1)  # Rate limit protection
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': original_symbol,
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
            elif 'Note' in data:
                print("Alpha Vantage rate limit")
            elif 'Error Message' in data:
                print(f"Alpha Vantage error: {data['Error Message']}")
                
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        # Return None - no fake data
        return None, None, None

class TechnicalAnalyzer:
    """Real technical analysis"""
    
    def calculate_all(self, df):
        """Calculate real indicators"""
        if df is None or df.empty:
            return {}
        
        indicators = {}
        
        try:
            # RSI
            if len(df) >= 14:
                indicators['rsi'] = self.calculate_rsi(df)
            
            # Moving averages
            if len(df) >= 20:
                indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
            if len(df) >= 50:
                indicators['sma_50'] = float(df['Close'].rolling(50).mean().iloc[-1])
            
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
                
        except Exception as e:
            print(f"Indicator error: {e}")
            
        return indicators
    
    def calculate_rsi(self, df, period=14):
        """Calculate real RSI"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        
        if loss.iloc[-1] == 0:
            return 100.0
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

# Try sklearn, fall back to simple if not available
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
    print("✓ ML with sklearn available")
except ImportError:
    ML_AVAILABLE = False
    print("⚠ sklearn not available - using simple predictions")

class Predictor:
    """Real predictions based on available tools"""
    
    def __init__(self):
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        if ML_AVAILABLE:
            self.model = RandomForestRegressor(n_estimators=100, max_depth=5)
            self.scaler = StandardScaler()
        
    def predict(self, df, days=5):
        """Generate real predictions"""
        if df is None or df.empty or len(df) < 20:
            return []
        
        try:
            # Get sentiment
            sentiment = self.sentiment_analyzer.get_combined_sentiment()
            
            if ML_AVAILABLE and len(df) >= 30:
                # Use ML if available and enough data
                return self._ml_predict(df, days, sentiment)
            else:
                # Use simple trend analysis
                return self._simple_predict(df, days, sentiment)
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return []
    
    def _simple_predict(self, df, days, sentiment):
        """Simple trend-based prediction"""
        # Calculate recent trend
        recent_change = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
        
        predictions = []
        current_price = float(df['Close'].iloc[-1])
        
        for i in range(1, days + 1):
            # Project trend with sentiment adjustment
            sentiment_factor = 1 + (sentiment['score'] * 0.02)
            daily_change = (recent_change / 5) * sentiment_factor
            predicted_price = current_price * (1 + daily_change * i)
            
            predictions.append({
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(predicted_price, 2),
                'confidence': 0.6,
                'method': 'Trend Analysis'
            })
        
        return predictions
    
    def _ml_predict(self, df, days, sentiment):
        """ML-based prediction"""
        # Prepare features
        df['returns'] = df['Close'].pct_change()
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['high_low'] = (df['High'] - df['Low']) / df['Close']
        
        # Create feature matrix
        features = ['returns', 'volume_ratio', 'high_low']
        X = df[features].dropna()
        y = df['Close'].shift(-1).dropna()
        
        # Align X and y
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y.iloc[:min_len]
        
        if len(X) < 20:
            return self._simple_predict(df, days, sentiment)
        
        # Train model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        # Generate predictions
        predictions = []
        current_features = X.iloc[-1:].values
        current_price = float(df['Close'].iloc[-1])
        
        for i in range(1, days + 1):
            # Predict next price
            pred_price = self.model.predict(self.scaler.transform(current_features))[0]
            
            # Apply sentiment adjustment
            sentiment_factor = 1 + (sentiment['score'] * 0.01)
            pred_price = pred_price * sentiment_factor
            
            predictions.append({
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(pred_price, 2),
                'confidence': 0.75,
                'method': 'Machine Learning'
            })
            
            # Update features for next prediction
            current_features[0][0] = (pred_price - current_price) / current_price
            current_price = pred_price
        
        return predictions

# Global instances
data_fetcher = RealDataFetcher()
tech_analyzer = TechnicalAnalyzer()
predictor = Predictor()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get real stock data only"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch real data
        df, source, current_price = data_fetcher.fetch_data(symbol, period, interval)
        
        if df is None:
            return jsonify({
                'error': 'Unable to fetch real market data',
                'symbol': symbol,
                'message': 'Please check symbol or try again later'
            }), 404
        
        # Real indicators
        indicators = tech_analyzer.calculate_all(df)
        
        # Real predictions
        predictions = predictor.predict(df, days=5)
        
        # Real sentiment
        sentiment = predictor.sentiment_analyzer.get_combined_sentiment()
        
        # Prepare response
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
            'sentiment': sentiment,
            'real_data': True  # Confirm this is real data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Get real market sentiment"""
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
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Real Data Only</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input, select, button {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        button {
            background: #667eea;
            color: white;
            cursor: pointer;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .info {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container {
            height: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Stock Analysis - Real Market Data Only</h1>
        <p>100% real data from Yahoo Finance and Alpha Vantage</p>
        
        <div class="controls">
            <input type="text" id="symbol" placeholder="Symbol" value="AAPL">
            <select id="period">
                <option value="1d">1 Day</option>
                <option value="5d">5 Days</option>
                <option value="1mo" selected>1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="1y">1 Year</option>
            </select>
            <button onclick="fetchData()">Get Data</button>
        </div>
        
        <div id="error"></div>
        
        <div class="info">
            <div class="chart-container">
                <canvas id="chart"></canvas>
            </div>
            <div>
                <h3>Info</h3>
                <div id="info">Select a stock to begin</div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('error').innerHTML = 
                        `<div class="error">${data.error}: ${data.message || ''}</div>`;
                    return;
                }
                
                document.getElementById('error').innerHTML = '';
                
                // Update chart
                updateChart(data);
                
                // Update info
                let info = `<strong>$${data.current_price?.toFixed(2) || 'N/A'}</strong><br>`;
                info += `Source: ${data.source}<br><br>`;
                
                if (data.predictions && data.predictions.length > 0) {
                    info += '<strong>Predictions:</strong><br>';
                    data.predictions.forEach(p => {
                        info += `${p.date}: $${p.predicted_price}<br>`;
                    });
                }
                
                document.getElementById('info').innerHTML = info;
                
            } catch (error) {
                document.getElementById('error').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            
            if (chart) chart.destroy();
            
            chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: data.data.map(d => ({
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
                    maintainAspectRatio: false
                }
            });
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)