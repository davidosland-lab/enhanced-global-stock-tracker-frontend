#!/usr/bin/env python3
"""
Stock Analysis with Market Sentiment - Robust Version
Enhanced error handling for network issues and API failures
"""

import os
import sys
import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from functools import lru_cache
import warnings
import time
import requests

warnings.filterwarnings('ignore')

# Skip dotenv to avoid encoding issues on Windows
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS WITH MARKET SENTIMENT - ROBUST VERSION")
print("=" * 60)
print("Features:")
print("✓ Enhanced error handling")
print("✓ Fallback data sources")
print("✓ Retry mechanisms")
print("✓ Graceful degradation")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("Press Ctrl+C to stop")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Australian stock symbols
AUSTRALIAN_SYMBOLS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 'GMG', 'TCL',
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL', 'IAG', 'QBE'
}

class RobustMarketSentimentAnalyzer:
    """Market sentiment analyzer with robust error handling"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes cache
        
    def safe_fetch_ticker(self, symbol, period="1d", max_retries=2):
        """Safely fetch ticker data with retries"""
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    return hist
                time.sleep(0.5)  # Small delay between retries
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {symbol} after {max_retries} attempts: {e}")
        return pd.DataFrame()
    
    def get_vix_fear_gauge(self):
        """Get VIX with fallback values"""
        try:
            hist = self.safe_fetch_ticker("^VIX", "1d")
            if not hist.empty:
                current_vix = hist['Close'].iloc[-1]
                
                if current_vix < 12:
                    sentiment = "Extreme Greed"
                    score = 0.9
                elif current_vix < 20:
                    sentiment = "Low Fear/Greed"
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
                    'value': float(current_vix),
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"VIX at {current_vix:.2f} indicates {sentiment.lower()}"
                }
        except Exception as e:
            print(f"VIX error: {e}")
        
        # Return neutral fallback
        return {
            'value': 20.0,
            'sentiment': 'Data Unavailable - Using Neutral',
            'score': 0,
            'description': 'VIX data temporarily unavailable'
        }
    
    def get_market_breadth(self):
        """Get market breadth with fallback"""
        try:
            indices = ['^GSPC', '^DJI', '^IXIC']
            advances = 0
            declines = 0
            
            for idx in indices:
                hist = self.safe_fetch_ticker(idx, "2d")
                if len(hist) >= 2:
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                        advances += 1
                    else:
                        declines += 1
            
            if advances + declines > 0:
                breadth_ratio = advances / (advances + declines)
                
                if breadth_ratio > 0.7:
                    sentiment = "Bullish Breadth"
                    score = 0.5
                elif breadth_ratio > 0.3:
                    sentiment = "Neutral Breadth"
                    score = 0
                else:
                    sentiment = "Bearish Breadth"
                    score = -0.5
                    
                return {
                    'advances': advances,
                    'declines': declines,
                    'ratio': breadth_ratio,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"{advances} advancing vs {declines} declining"
                }
        except Exception as e:
            print(f"Market breadth error: {e}")
            
        return {
            'advances': 1,
            'declines': 1,
            'ratio': 0.5,
            'sentiment': 'Neutral - Data Limited',
            'score': 0,
            'description': 'Market breadth data limited'
        }
    
    def get_bond_yields(self):
        """Get bond yields with fallback"""
        try:
            hist = self.safe_fetch_ticker("^TNX", "5d")
            if not hist.empty:
                current_yield = hist['Close'].iloc[-1]
                week_ago_yield = hist['Close'].iloc[0] if len(hist) > 1 else current_yield
                yield_change = current_yield - week_ago_yield
                
                if abs(yield_change) < 0.05:
                    sentiment = "Stable Yields"
                    score = 0
                elif yield_change > 0.1:
                    sentiment = "Rising Yields"
                    score = 0.3
                elif yield_change < -0.1:
                    sentiment = "Falling Yields"
                    score = -0.3
                else:
                    sentiment = "Stable Yields"
                    score = 0
                    
                return {
                    'current': float(current_yield),
                    'change': float(yield_change),
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"10Y yield at {current_yield:.2f}%, change: {yield_change:+.2f}%"
                }
        except Exception as e:
            print(f"Bond yields error: {e}")
            
        return {
            'current': 4.0,
            'change': 0,
            'sentiment': 'Yields Stable - Data Limited',
            'score': 0,
            'description': 'Bond yield data limited'
        }
    
    def get_dollar_strength(self):
        """Get dollar index with fallback"""
        try:
            hist = self.safe_fetch_ticker("DX-Y.NYB", "5d")
            if not hist.empty:
                current_dxy = hist['Close'].iloc[-1]
                week_ago_dxy = hist['Close'].iloc[0] if len(hist) > 1 else current_dxy
                dxy_change = ((current_dxy - week_ago_dxy) / week_ago_dxy) * 100
                
                if abs(dxy_change) < 0.5:
                    sentiment = "Dollar Stable"
                    score = 0
                elif dxy_change > 1:
                    sentiment = "Dollar Strengthening"
                    score = -0.3
                elif dxy_change < -1:
                    sentiment = "Dollar Weakening"
                    score = 0.3
                else:
                    sentiment = "Dollar Stable"
                    score = 0
                    
                return {
                    'value': float(current_dxy),
                    'change': float(dxy_change),
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"DXY at {current_dxy:.2f}, change: {dxy_change:+.2f}%"
                }
        except Exception as e:
            print(f"Dollar index error: {e}")
            
        return {
            'value': 100.0,
            'change': 0,
            'sentiment': 'Dollar Stable - Data Limited',
            'score': 0,
            'description': 'Dollar index data limited'
        }
    
    def get_sector_rotation(self):
        """Get sector rotation with fallback"""
        try:
            sectors = {
                'Technology': 'XLK',
                'Financials': 'XLF',
                'Healthcare': 'XLV',
                'Energy': 'XLE',
                'Consumer Disc.': 'XLY'
            }
            
            performances = {}
            for name, ticker in sectors.items():
                hist = self.safe_fetch_ticker(ticker, "5d")
                if len(hist) >= 2:
                    perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    performances[name] = perf
            
            if performances:
                sorted_sectors = sorted(performances.items(), key=lambda x: x[1], reverse=True)
                top = sorted_sectors[:2] if len(sorted_sectors) >= 2 else sorted_sectors
                
                leaders = [s[0] for s in top]
                if 'Technology' in leaders:
                    sentiment = "Growth Leading"
                    score = 0.3
                elif 'Energy' in leaders:
                    sentiment = "Energy Leading"
                    score = 0.1
                else:
                    sentiment = "Mixed Sectors"
                    score = 0
                    
                return {
                    'top_performers': top,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"Leading: {', '.join(leaders)}" if leaders else "Sector data limited"
                }
        except Exception as e:
            print(f"Sector rotation error: {e}")
            
        return {
            'top_performers': [],
            'sentiment': 'Sector Analysis Limited',
            'score': 0,
            'description': 'Sector rotation data limited'
        }
    
    def get_combined_sentiment(self):
        """Get combined sentiment with safe handling"""
        components = {
            'vix': self.get_vix_fear_gauge(),
            'market_breadth': self.get_market_breadth(),
            'bond_yields': self.get_bond_yields(),
            'dollar_index': self.get_dollar_strength(),
            'sector_rotation': self.get_sector_rotation()
        }
        
        weights = {
            'vix': 0.30,
            'market_breadth': 0.20,
            'bond_yields': 0.15,
            'dollar_index': 0.15,
            'sector_rotation': 0.20
        }
        
        total_score = 0
        valid_components = 0
        
        for key, component in components.items():
            if component and 'score' in component:
                total_score += component['score'] * weights.get(key, 0.2)
                valid_components += 1
        
        # Normalize if not all components available
        if valid_components > 0 and valid_components < len(components):
            total_score = total_score * (len(components) / valid_components)
        
        if total_score > 0.3:
            overall = "Bullish"
        elif total_score < -0.3:
            overall = "Bearish"
        else:
            overall = "Neutral"
            
        return {
            'score': float(total_score),
            'sentiment': overall,
            'components': components,
            'data_quality': f"{valid_components}/{len(components)} indicators available",
            'timestamp': datetime.now().isoformat()
        }

class RobustDataFetcher:
    """Data fetcher with multiple fallback options"""
    
    def __init__(self):
        self.alpha_vantage_key = "68ZFANK047DL0KSR"
        self.cache = {}
        
    def fetch_data(self, symbol, period="1mo", interval="1d"):
        """Fetch with multiple fallbacks"""
        original_symbol = symbol
        
        # Handle Australian stocks
        if symbol.upper() in AUSTRALIAN_SYMBOLS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
        
        # Try Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not current_price and not df.empty:
                    current_price = df['Close'].iloc[-1]
                return df, "Yahoo Finance", float(current_price) if current_price else None
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
        
        # Try Alpha Vantage
        try:
            return self._fetch_alpha_vantage(original_symbol)
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        # Generate demo data as last resort
        return self._generate_demo_data(symbol)
    
    def _fetch_alpha_vantage(self, symbol):
        """Alpha Vantage fallback"""
        try:
            url = f"https://www.alphavantage.co/query"
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
                current_price = df['Close'].iloc[-1]
                return df, "Alpha Vantage", float(current_price)
        except Exception as e:
            print(f"Alpha Vantage failed: {e}")
            
        return pd.DataFrame(), "None", None
    
    def _generate_demo_data(self, symbol):
        """Generate realistic demo data when APIs fail"""
        print(f"Generating demo data for {symbol}")
        
        # Base prices for known symbols
        base_prices = {
            'AAPL': 175.0,
            'MSFT': 380.0,
            'GOOGL': 140.0,
            'AMZN': 155.0,
            'TSLA': 250.0,
            'CBA': 110.0,
            'BHP': 45.0
        }
        
        base_price = base_prices.get(symbol.replace('.AX', ''), 100.0)
        
        # Generate 30 days of data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        data = []
        
        current = base_price
        for date in dates:
            # Random walk
            change = np.random.normal(0, 0.02)
            current = current * (1 + change)
            
            high = current * (1 + abs(np.random.normal(0, 0.01)))
            low = current * (1 - abs(np.random.normal(0, 0.01)))
            open_price = current * (1 + np.random.normal(0, 0.005))
            volume = int(10000000 * (1 + np.random.normal(0, 0.3)))
            
            data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': current,
                'Volume': volume
            })
        
        df = pd.DataFrame(data, index=dates)
        return df, "Demo Data (APIs Unavailable)", float(current)

class SimpleTechnicalAnalyzer:
    """Technical analysis with safe calculations"""
    
    def calculate_all(self, df):
        """Calculate indicators safely"""
        if df.empty:
            return {}
        
        indicators = {}
        
        try:
            # RSI
            indicators['rsi'] = self.calculate_rsi(df)
            
            # Moving Averages
            if len(df) >= 20:
                indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
            if len(df) >= 10:
                indicators['sma_10'] = float(df['Close'].rolling(10).mean().iloc[-1])
            if len(df) >= 5:
                indicators['sma_5'] = float(df['Close'].rolling(5).mean().iloc[-1])
                
            # Simple MACD
            if len(df) >= 26:
                exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                indicators['macd'] = {
                    'macd': float(macd.iloc[-1]),
                    'signal': float(signal.iloc[-1]),
                    'histogram': float((macd - signal).iloc[-1])
                }
        except Exception as e:
            print(f"Indicator calculation error: {e}")
            
        return indicators
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI safely"""
        try:
            if len(df) < period:
                return 50.0  # Neutral RSI
                
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            
            if loss.iloc[-1] == 0:
                return 100.0
                
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0

class SimplePrediction:
    """Simple trend-based prediction"""
    
    def __init__(self):
        self.sentiment_analyzer = RobustMarketSentimentAnalyzer()
    
    def predict(self, df, days=5):
        """Generate simple predictions"""
        if df.empty:
            return []
        
        try:
            # Calculate trend
            if len(df) >= 5:
                recent_trend = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
            else:
                recent_trend = 0
            
            # Get sentiment
            sentiment = self.sentiment_analyzer.get_combined_sentiment()
            sentiment_factor = 1 + (sentiment['score'] * 0.05)
            
            # Generate predictions
            predictions = []
            current_price = float(df['Close'].iloc[-1])
            
            for i in range(1, days + 1):
                # Simple projection with sentiment
                daily_change = (recent_trend / 5) * sentiment_factor
                predicted_price = current_price * (1 + daily_change * i)
                
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'predicted_price': round(predicted_price, 2),
                    'confidence': 0.6 + min(0.3, abs(sentiment['score']) * 0.3),
                    'trend': 'Bullish' if daily_change > 0 else 'Bearish' if daily_change < 0 else 'Neutral'
                })
            
            return predictions
        except Exception as e:
            print(f"Prediction error: {e}")
            return []

# Global instances
data_fetcher = RobustDataFetcher()
tech_analyzer = SimpleTechnicalAnalyzer()
predictor = SimplePrediction()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with fallbacks"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch data
        df, source, current_price = data_fetcher.fetch_data(symbol, period, interval)
        
        if df is None or df.empty:
            # Return with demo data
            df, source, current_price = data_fetcher._generate_demo_data(symbol)
        
        # Calculate indicators
        indicators = tech_analyzer.calculate_all(df)
        
        # Get predictions
        predictions = predictor.predict(df, days=5)
        
        # Get sentiment
        sentiment = predictor.sentiment_analyzer.get_combined_sentiment()
        
        # Prepare data
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
            'data': candlestick_data[-50:],  # Limit to last 50 points
            'indicators': indicators,
            'predictions': predictions,
            'sentiment': sentiment
        })
    except Exception as e:
        print(f"API error in get_stock_data: {e}")
        return jsonify({
            'error': 'Service temporarily unavailable',
            'message': 'Using cached or demo data',
            'symbol': symbol
        }), 200  # Return 200 with error message instead of 500

@app.route('/api/sentiment')
def get_market_sentiment():
    """Get market sentiment with fallbacks"""
    try:
        analyzer = RobustMarketSentimentAnalyzer()
        sentiment = analyzer.get_combined_sentiment()
        return jsonify(sentiment)
    except Exception as e:
        print(f"Sentiment API error: {e}")
        return jsonify({
            'score': 0,
            'sentiment': 'Neutral',
            'components': {},
            'data_quality': 'Limited data available',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# HTML Template (simplified for robustness)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis - Robust Version</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .controls input, .controls select {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
        }
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .chart-container, .info-box {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .sentiment-box {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .sentiment-score {
            font-size: 1.5em;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .bullish { background: #d4f4dd; color: #0f5132; }
        .bearish { background: #f8d7da; color: #842029; }
        .neutral { background: #fff3cd; color: #664d03; }
        .error-message {
            background: #fff3cd;
            color: #664d03;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        }
        @media (max-width: 1024px) {
            .main-content { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis with Market Sentiment</h1>
            <p style="color: #666;">Robust version with fallback data sources</p>
        </div>
        
        <div class="sentiment-box">
            <h3>Market Sentiment</h3>
            <div id="sentimentDisplay" class="sentiment-score neutral">Loading...</div>
            <div id="dataQuality" style="text-align: center; color: #666; margin-top: 10px;"></div>
        </div>
        
        <div class="controls">
            <input type="text" id="symbol" placeholder="Stock Symbol" value="AAPL">
            <select id="period">
                <option value="1d">1 Day</option>
                <option value="5d">5 Days</option>
                <option value="1mo" selected>1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="1y">1 Year</option>
            </select>
            <button onclick="fetchData()">Get Analysis</button>
        </div>
        
        <div id="errorMessage"></div>
        
        <div class="main-content">
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
            
            <div>
                <div class="info-box" style="margin-bottom: 20px;">
                    <h3>Price Info</h3>
                    <div id="priceInfo">-</div>
                </div>
                
                <div class="info-box">
                    <h3>Predictions</h3>
                    <div id="predictions">-</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentChart = null;
        
        async function loadSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                
                const display = document.getElementById('sentimentDisplay');
                const quality = document.getElementById('dataQuality');
                
                display.textContent = data.sentiment + ' (' + (data.score > 0 ? '+' : '') + data.score.toFixed(2) + ')';
                display.className = 'sentiment-score ' + 
                    (data.score > 0.3 ? 'bullish' : data.score < -0.3 ? 'bearish' : 'neutral');
                
                quality.textContent = data.data_quality || '';
            } catch (error) {
                console.error('Sentiment error:', error);
                document.getElementById('sentimentDisplay').textContent = 'Data Limited';
            }
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=1d`);
                const data = await response.json();
                
                // Show any warnings
                if (data.source && data.source.includes('Demo')) {
                    document.getElementById('errorMessage').innerHTML = 
                        '<div class="error-message">Note: Using fallback data due to API limitations</div>';
                } else {
                    document.getElementById('errorMessage').innerHTML = '';
                }
                
                // Update chart
                if (data.data && data.data.length > 0) {
                    updateChart(data);
                }
                
                // Update info
                updateInfo(data);
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('errorMessage').innerHTML = 
                    '<div class="error-message">Error loading data. Please try again.</div>';
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (currentChart) {
                currentChart.destroy();
            }
            
            const chartData = {
                datasets: [{
                    label: data.symbol,
                    data: data.data.map(item => ({
                        x: new Date(item.date).getTime(),
                        o: item.open,
                        h: item.high,
                        l: item.low,
                        c: item.close
                    }))
                }]
            };
            
            currentChart = new Chart(ctx, {
                type: 'candlestick',
                data: chartData,
                options: {
                    responsive: true,
                    plugins: {
                        zoom: {
                            zoom: { enabled: true, mode: 'x' },
                            pan: { enabled: true, mode: 'x' }
                        }
                    }
                }
            });
        }
        
        function updateInfo(data) {
            // Price info
            document.getElementById('priceInfo').innerHTML = `
                <div style="font-size: 1.5em; font-weight: bold;">
                    $${data.current_price ? data.current_price.toFixed(2) : 'N/A'}
                </div>
                <div style="color: #666;">Source: ${data.source || 'Unknown'}</div>
            `;
            
            // Predictions
            let predHtml = '';
            if (data.predictions && data.predictions.length > 0) {
                data.predictions.forEach(p => {
                    predHtml += `
                        <div style="padding: 5px 0; border-bottom: 1px solid #eee;">
                            ${p.date}: $${p.predicted_price.toFixed(2)}
                            <span style="color: ${p.trend === 'Bullish' ? 'green' : p.trend === 'Bearish' ? 'red' : 'gray'}">
                                ${p.trend}
                            </span>
                        </div>
                    `;
                });
            } else {
                predHtml = 'No predictions available';
            }
            document.getElementById('predictions').innerHTML = predHtml;
        }
        
        // Load on start
        window.onload = function() {
            loadSentiment();
            setInterval(loadSentiment, 60000); // Update every minute
        };
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)