#!/usr/bin/env python3
"""
Stock Analysis with Market Sentiment - No sklearn required
This version works without scikit-learn, providing sentiment analysis
but using simpler prediction methods.
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
warnings.filterwarnings('ignore')

# Skip dotenv to avoid encoding issues on Windows
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS WITH MARKET SENTIMENT - NO SKLEARN VERSION")
print("=" * 60)
print("Features:")
print("✓ VIX Fear Gauge integration")
print("✓ Market breadth analysis")
print("✓ Bond yield tracking")
print("✓ Dollar strength indicator")
print("✓ Sector rotation analysis")
print("✓ Simple trend-based predictions")
print("✓ Works without scikit-learn")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("Press Ctrl+C to stop")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Australian stock symbols that need .AX suffix
AUSTRALIAN_SYMBOLS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 'GMG', 'TCL',
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL', 'IAG', 'QBE',
    'STO', 'NCM', 'AMC', 'BXB', 'SCG', 'GPT', 'MGR', 'DXS', 'LLC', 'VCX',
    'APT', 'XRO', 'WPL', 'ORG', 'APA', 'SUN', 'QAN', 'RHC', 'AMP', 'MPL'
}

class MarketSentimentAnalyzer:
    """Phase 1: Market sentiment using readily available indicators"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes cache
        
    @lru_cache(maxsize=10)
    def get_vix_fear_gauge(self):
        """Get VIX fear index - market volatility expectations"""
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="1d")
            if not hist.empty:
                current_vix = hist['Close'].iloc[-1]
                
                # VIX interpretation
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
                    'value': current_vix,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"VIX at {current_vix:.2f} indicates {sentiment.lower()}"
                }
        except Exception as e:
            print(f"Error fetching VIX: {e}")
            return {'value': None, 'sentiment': 'Unknown', 'score': 0, 'description': 'VIX data unavailable'}
    
    def get_market_breadth(self):
        """Get market breadth - advancing vs declining stocks"""
        try:
            # Use major indices as proxy
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow, Nasdaq
            advances = 0
            declines = 0
            
            for idx in indices:
                ticker = yf.Ticker(idx)
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                        advances += 1
                    else:
                        declines += 1
            
            # Calculate breadth ratio
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
            print(f"Error calculating market breadth: {e}")
            return {'ratio': 0.5, 'sentiment': 'Unknown', 'score': 0, 'description': 'Market breadth unavailable'}
    
    def get_bond_yields(self):
        """Get 10-year Treasury yield as risk sentiment indicator"""
        try:
            # 10-Year Treasury Yield
            tny = yf.Ticker("^TNX")
            hist = tny.history(period="5d")
            if not hist.empty:
                current_yield = hist['Close'].iloc[-1]
                week_ago_yield = hist['Close'].iloc[0] if len(hist) > 1 else current_yield
                yield_change = current_yield - week_ago_yield
                
                # Rising yields = risk-on, falling = risk-off
                if abs(yield_change) < 0.05:
                    sentiment = "Stable Yields"
                    score = 0
                elif yield_change > 0.1:
                    sentiment = "Rising Yields (Risk-On)"
                    score = 0.3
                elif yield_change < -0.1:
                    sentiment = "Falling Yields (Risk-Off)"
                    score = -0.3
                else:
                    sentiment = "Stable Yields"
                    score = 0
                    
                return {
                    'current': current_yield,
                    'change': yield_change,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"10Y yield at {current_yield:.2f}%, change: {yield_change:+.2f}%"
                }
        except Exception as e:
            print(f"Error fetching bond yields: {e}")
            return {'current': None, 'change': 0, 'sentiment': 'Unknown', 'score': 0}
    
    def get_dollar_strength(self):
        """Get Dollar Index (DXY) as risk sentiment"""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="5d")
            if not hist.empty:
                current_dxy = hist['Close'].iloc[-1]
                week_ago_dxy = hist['Close'].iloc[0] if len(hist) > 1 else current_dxy
                dxy_change = ((current_dxy - week_ago_dxy) / week_ago_dxy) * 100
                
                # Strong dollar = risk-off, weak = risk-on
                if abs(dxy_change) < 0.5:
                    sentiment = "Dollar Stable"
                    score = 0
                elif dxy_change > 1:
                    sentiment = "Dollar Strengthening (Risk-Off)"
                    score = -0.3
                elif dxy_change < -1:
                    sentiment = "Dollar Weakening (Risk-On)"
                    score = 0.3
                else:
                    sentiment = "Dollar Stable"
                    score = 0
                    
                return {
                    'value': current_dxy,
                    'change': dxy_change,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"DXY at {current_dxy:.2f}, change: {dxy_change:+.2f}%"
                }
        except Exception as e:
            print(f"Error fetching dollar index: {e}")
            return {'value': None, 'change': 0, 'sentiment': 'Unknown', 'score': 0}
    
    def get_sector_rotation(self):
        """Analyze sector performance for rotation signals"""
        try:
            sectors = {
                'Technology': 'XLK',
                'Financials': 'XLF',
                'Healthcare': 'XLV',
                'Energy': 'XLE',
                'Consumer Disc.': 'XLY',
                'Industrials': 'XLI',
                'Materials': 'XLB',
                'Real Estate': 'XLRE',
                'Utilities': 'XLU',
                'Cons. Staples': 'XLP',
                'Communications': 'XLC'
            }
            
            performances = {}
            for name, ticker in sectors.items():
                try:
                    etf = yf.Ticker(ticker)
                    hist = etf.history(period="5d")
                    if len(hist) >= 2:
                        perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        performances[name] = perf
                except:
                    pass
            
            if performances:
                sorted_sectors = sorted(performances.items(), key=lambda x: x[1], reverse=True)
                top_3 = sorted_sectors[:3]
                bottom_3 = sorted_sectors[-3:]
                
                # Determine market regime based on leading sectors
                leaders = [s[0] for s in top_3]
                if 'Technology' in leaders or 'Consumer Disc.' in leaders:
                    sentiment = "Growth Leading (Risk-On)"
                    score = 0.4
                elif 'Utilities' in leaders or 'Cons. Staples' in leaders:
                    sentiment = "Defensive Leading (Risk-Off)"
                    score = -0.4
                else:
                    sentiment = "Mixed Sector Performance"
                    score = 0
                    
                return {
                    'top_performers': top_3,
                    'bottom_performers': bottom_3,
                    'sentiment': sentiment,
                    'score': score,
                    'description': f"Leading: {', '.join([s[0] for s in top_3[:2]])}"
                }
        except Exception as e:
            print(f"Error analyzing sectors: {e}")
            return {'sentiment': 'Unknown', 'score': 0, 'description': 'Sector data unavailable'}
    
    def get_combined_sentiment(self):
        """Combine all sentiment indicators into overall market sentiment"""
        indicators = {
            'vix': self.get_vix_fear_gauge(),
            'market_breadth': self.get_market_breadth(),
            'bond_yields': self.get_bond_yields(),
            'dollar_index': self.get_dollar_strength(),
            'sector_rotation': self.get_sector_rotation()
        }
        
        # Calculate weighted average score
        weights = {
            'vix': 0.30,
            'market_breadth': 0.20,
            'bond_yields': 0.15,
            'dollar_index': 0.15,
            'sector_rotation': 0.20
        }
        
        total_score = 0
        for key, indicator in indicators.items():
            if indicator and 'score' in indicator:
                total_score += indicator['score'] * weights.get(key, 0.2)
        
        # Determine overall sentiment
        if total_score > 0.3:
            overall = "Bullish"
        elif total_score < -0.3:
            overall = "Bearish"
        else:
            overall = "Neutral"
            
        return {
            'score': total_score,
            'sentiment': overall,
            'components': indicators,
            'timestamp': datetime.now().isoformat()
        }

class SimpleTrendPredictor:
    """Simple trend-based prediction without sklearn"""
    
    def __init__(self):
        self.sentiment_analyzer = MarketSentimentAnalyzer()
    
    def predict_trend(self, df, days=5, include_sentiment=True):
        """Simple trend prediction based on moving averages and momentum"""
        if df is None or df.empty or len(df) < 20:
            return []
        
        # Calculate simple indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=min(50, len(df))).mean()
        df['Momentum'] = df['Close'].pct_change(periods=5)
        
        # Get latest values
        latest_close = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df else latest_close
        sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df else latest_close
        momentum = df['Momentum'].iloc[-1] if 'Momentum' in df else 0
        
        # Simple trend calculation
        trend_score = 0
        if latest_close > sma_20:
            trend_score += 0.3
        if latest_close > sma_50:
            trend_score += 0.2
        if momentum > 0:
            trend_score += 0.3
        
        # Add sentiment if available
        if include_sentiment:
            sentiment = self.sentiment_analyzer.get_combined_sentiment()
            trend_score += sentiment['score'] * 0.2
        
        # Calculate daily return based on trend
        if trend_score > 0.5:
            daily_return = 0.002  # 0.2% daily increase
        elif trend_score < -0.5:
            daily_return = -0.002  # 0.2% daily decrease
        else:
            daily_return = 0.0001  # Nearly flat
        
        # Generate predictions
        predictions = []
        current_price = latest_close
        
        for i in range(1, days + 1):
            # Add some randomness for realism
            noise = np.random.normal(0, 0.001)
            current_price = current_price * (1 + daily_return + noise)
            
            predictions.append({
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(current_price, 2),
                'confidence': max(0.5, min(0.9, 0.7 + trend_score * 0.1)),
                'trend': 'Bullish' if trend_score > 0 else 'Bearish' if trend_score < 0 else 'Neutral'
            })
        
        return predictions

class UnifiedDataFetcher:
    """Unified data fetcher with Yahoo Finance and Alpha Vantage fallback"""
    
    def __init__(self):
        self.alpha_vantage_key = "68ZFANK047DL0KSR"
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def fetch_data(self, symbol, period="1mo", interval="1d"):
        """Fetch data with automatic Australian stock handling"""
        # Check if it's an Australian stock and add .AX if needed
        original_symbol = symbol
        if symbol.upper() in AUSTRALIAN_SYMBOLS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
        
        # Try Yahoo Finance first
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                # Get current price
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if not current_price and not df.empty:
                    current_price = df['Close'].iloc[-1]
                
                return df, "Yahoo Finance", current_price
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
        
        # Fallback to Alpha Vantage
        return self._fetch_alpha_vantage(original_symbol)
    
    def _fetch_alpha_vantage(self, symbol):
        """Fallback to Alpha Vantage"""
        try:
            import requests
            
            # Determine function based on symbol
            if symbol.upper() in AUSTRALIAN_SYMBOLS:
                symbol = f"{symbol}.AX"
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                ts = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(ts, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                # Rename columns to match yfinance format
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                
                current_price = df['Close'].iloc[-1]
                return df, "Alpha Vantage", current_price
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        return pd.DataFrame(), "None", None

class TechnicalAnalyzer:
    """Technical analysis indicators"""
    
    def calculate_all(self, df):
        """Calculate all technical indicators"""
        if df.empty:
            return {}
        
        indicators = {}
        
        # RSI
        indicators['rsi'] = self.calculate_rsi(df)
        
        # MACD
        indicators['macd'] = self.calculate_macd(df)
        
        # Bollinger Bands
        indicators['bollinger'] = self.calculate_bollinger_bands(df)
        
        # Moving Averages
        indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
        indicators['sma_50'] = float(df['Close'].rolling(50).mean().iloc[-1]) if len(df) >= 50 else None
        indicators['ema_12'] = float(df['Close'].ewm(span=12).mean().iloc[-1]) if len(df) >= 12 else None
        indicators['ema_26'] = float(df['Close'].ewm(span=26).mean().iloc[-1]) if len(df) >= 26 else None
        
        # ATR
        indicators['atr'] = self.calculate_atr(df)
        
        return indicators
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI"""
        if len(df) < period:
            return None
            
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    
    def calculate_macd(self, df):
        """Calculate MACD"""
        if len(df) < 26:
            return {}
            
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': float(macd.iloc[-1]),
            'signal': float(signal.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }
    
    def calculate_bollinger_bands(self, df, period=20, std=2):
        """Calculate Bollinger Bands"""
        if len(df) < period:
            return {}
            
        sma = df['Close'].rolling(period).mean()
        std_dev = df['Close'].rolling(period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        return {
            'upper': float(upper.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower.iloc[-1])
        }
    
    def calculate_atr(self, df, period=14):
        """Calculate ATR"""
        if len(df) < period:
            return None
            
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()
        return float(atr.iloc[-1])

# Create global instances
data_fetcher = UnifiedDataFetcher()
tech_analyzer = TechnicalAnalyzer()
trend_predictor = SimpleTrendPredictor()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with technical indicators and predictions"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch data
        df, source, current_price = data_fetcher.fetch_data(symbol, period, interval)
        
        if df is None or df.empty:
            return jsonify({
                'error': 'Failed to fetch data',
                'symbol': symbol,
                'source': 'None'
            }), 404
        
        # Calculate technical indicators
        indicators = tech_analyzer.calculate_all(df)
        
        # Get sentiment analysis
        sentiment = trend_predictor.sentiment_analyzer.get_combined_sentiment()
        
        # Get trend predictions
        predictions = trend_predictor.predict_trend(df, days=5, include_sentiment=True)
        
        # Prepare candlestick data for frontend
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
            'sentiment': sentiment
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

@app.route('/api/sentiment')
def get_market_sentiment():
    """Get current market sentiment analysis"""
    try:
        analyzer = MarketSentimentAnalyzer()
        sentiment = analyzer.get_combined_sentiment()
        return jsonify(sentiment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/vix')
def get_vix():
    """Get VIX fear gauge"""
    try:
        analyzer = MarketSentimentAnalyzer()
        vix = analyzer.get_vix_fear_gauge()
        return jsonify(vix)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/breadth')
def get_breadth():
    """Get market breadth"""
    try:
        analyzer = MarketSentimentAnalyzer()
        breadth = analyzer.get_market_breadth()
        return jsonify(breadth)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/sectors')
def get_sectors():
    """Get sector rotation analysis"""
    try:
        analyzer = MarketSentimentAnalyzer()
        sectors = analyzer.get_sector_rotation()
        return jsonify(sectors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Handle favicon request to prevent 404"""
    return '', 204

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis with Market Sentiment - No sklearn</title>
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
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
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .sentiment-dashboard {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .sentiment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .sentiment-title {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        
        .sentiment-score {
            font-size: 1.3em;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
        }
        
        .sentiment-score.bullish {
            background: linear-gradient(135deg, #00c853, #00e676);
            color: white;
        }
        
        .sentiment-score.bearish {
            background: linear-gradient(135deg, #d32f2f, #f44336);
            color: white;
        }
        
        .sentiment-score.neutral {
            background: linear-gradient(135deg, #ffa000, #ffb300);
            color: white;
        }
        
        .sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .sentiment-indicator {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        
        .indicator-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .indicator-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
        
        .indicator-change {
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .indicator-change.positive {
            color: #00c853;
        }
        
        .indicator-change.negative {
            color: #d32f2f;
        }
        
        .controls {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .input-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .input-wrapper {
            flex: 1;
            min-width: 150px;
        }
        
        .input-wrapper label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-size: 0.9em;
        }
        
        .input-wrapper input,
        .input-wrapper select {
            width: 100%;
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
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
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
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .info-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .info-box h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .price-display {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .price-change {
            font-size: 1.2em;
        }
        
        .price-change.positive {
            color: #00c853;
        }
        
        .price-change.negative {
            color: #d32f2f;
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
            <h1>📈 Stock Analysis with Market Sentiment</h1>
            <p style="color: #666;">No sklearn required - Simple trend analysis with market sentiment</p>
        </div>
        
        <!-- Market Sentiment Dashboard -->
        <div class="sentiment-dashboard" id="sentimentDashboard">
            <div class="sentiment-header">
                <div class="sentiment-title">🎯 Market Sentiment Analysis</div>
                <div class="sentiment-score neutral" id="overallSentiment">Loading...</div>
            </div>
            <div class="sentiment-grid" id="sentimentGrid">
                <!-- Sentiment indicators will be populated here -->
            </div>
        </div>
        
        <!-- Controls -->
        <div class="controls">
            <div class="input-group">
                <div class="input-wrapper">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" placeholder="e.g., AAPL, MSFT, CBA" value="AAPL">
                </div>
                <div class="input-wrapper">
                    <label>Time Period</label>
                    <select id="period">
                        <option value="1d">1 Day</option>
                        <option value="5d">5 Days</option>
                        <option value="1mo" selected>1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                    </select>
                </div>
                <div class="input-wrapper">
                    <label>Interval</label>
                    <select id="interval">
                        <option value="1m">1 Minute</option>
                        <option value="5m">5 Minutes</option>
                        <option value="15m">15 Minutes</option>
                        <option value="1h">1 Hour</option>
                        <option value="1d" selected>Daily</option>
                    </select>
                </div>
                <div class="input-wrapper">
                    <label>&nbsp;</label>
                    <button onclick="fetchStockData()">Get Analysis</button>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
            
            <div class="info-panel">
                <div class="info-box" id="priceInfo">
                    <h3>Current Price</h3>
                    <div id="priceDisplay">-</div>
                </div>
                
                <div class="info-box" id="indicators">
                    <h3>Technical Indicators</h3>
                    <div id="indicatorsList">-</div>
                </div>
                
                <div class="info-box" id="predictions">
                    <h3>Trend Predictions</h3>
                    <div id="predictionsList">-</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentChart = null;
        
        window.onload = function() {
            loadMarketSentiment();
            // Auto-refresh sentiment every 5 minutes
            setInterval(loadMarketSentiment, 300000);
        };
        
        async function loadMarketSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const sentiment = await response.json();
                console.log('Sentiment data received:', sentiment);
                updateSentimentDashboard(sentiment);
            } catch (error) {
                console.error('Error loading sentiment:', error);
                const overallElement = document.getElementById('overallSentiment');
                if (overallElement) {
                    overallElement.textContent = 'Failed to load sentiment';
                    overallElement.className = 'sentiment-score neutral';
                }
            }
        }
        
        function updateSentimentDashboard(sentiment) {
            // Update overall sentiment
            const overallElement = document.getElementById('overallSentiment');
            if (!sentiment || sentiment.error) {
                overallElement.textContent = 'Error loading sentiment';
                overallElement.className = 'sentiment-score neutral';
                return;
            }
            
            const score = sentiment.score || 0;
            const sentimentText = sentiment.sentiment || 'Unknown';
            overallElement.textContent = sentimentText + ' (' + (score > 0 ? '+' : '') + score.toFixed(2) + ')';
            
            // Update color based on sentiment
            overallElement.className = 'sentiment-score';
            if (score > 0.2) {
                overallElement.className += ' bullish';
            } else if (score < -0.2) {
                overallElement.className += ' bearish';
            } else {
                overallElement.className += ' neutral';
            }
            
            // Update individual indicators
            const grid = document.getElementById('sentimentGrid');
            grid.innerHTML = '';
            
            // VIX Indicator
            if (sentiment.components && sentiment.components.vix) {
                const vix = sentiment.components.vix;
                const vixClass = vix.score < -0.3 ? 'fear' : vix.score > 0.3 ? 'greed' : '';
                grid.innerHTML += `
                    <div class="sentiment-indicator vix-gauge ${vixClass}">
                        <div class="indicator-label">VIX Fear Gauge</div>
                        <div class="indicator-value">${vix.value ? vix.value.toFixed(2) : 'N/A'}</div>
                        <div class="indicator-change">${vix.sentiment || ''}</div>
                        <div class="indicator-description">${vix.description || ''}</div>
                    </div>
                `;
            }
            
            // Market Breadth
            if (sentiment.components && sentiment.components.market_breadth) {
                const breadth = sentiment.components.market_breadth;
                const ratioPercent = breadth.ratio ? (breadth.ratio * 100).toFixed(0) : '0';
                grid.innerHTML += `
                    <div class="sentiment-indicator">
                        <div class="indicator-label">Market Breadth</div>
                        <div class="indicator-value">${ratioPercent}%</div>
                        <div class="indicator-change ${breadth.score > 0 ? 'positive' : 'negative'}">${breadth.sentiment}</div>
                        <div class="indicator-description">${breadth.description}</div>
                    </div>
                `;
            }
            
            // Other indicators...
            if (sentiment.components) {
                // Bond Yields
                if (sentiment.components.bond_yields) {
                    const yields = sentiment.components.bond_yields;
                    grid.innerHTML += `
                        <div class="sentiment-indicator">
                            <div class="indicator-label">10Y Treasury Yield</div>
                            <div class="indicator-value">${yields.current ? yields.current.toFixed(2) + '%' : 'N/A'}</div>
                            <div class="indicator-change">${yields.sentiment}</div>
                        </div>
                    `;
                }
                
                // Dollar Index
                if (sentiment.components.dollar_index) {
                    const dollar = sentiment.components.dollar_index;
                    grid.innerHTML += `
                        <div class="sentiment-indicator">
                            <div class="indicator-label">Dollar Index (DXY)</div>
                            <div class="indicator-value">${dollar.value ? dollar.value.toFixed(2) : 'N/A'}</div>
                            <div class="indicator-change">${dollar.sentiment}</div>
                        </div>
                    `;
                }
                
                // Sectors
                if (sentiment.components.sector_rotation) {
                    const sectors = sentiment.components.sector_rotation;
                    grid.innerHTML += `
                        <div class="sentiment-indicator">
                            <div class="indicator-label">Sector Rotation</div>
                            <div class="indicator-value">${sectors.sentiment}</div>
                            <div class="indicator-description">${sectors.description}</div>
                        </div>
                    `;
                }
            }
        }
        
        async function fetchStockData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=${interval}`);
                const data = await response.json();
                
                if (response.ok) {
                    updateChart(data);
                    updatePriceInfo(data);
                    updateIndicators(data);
                    updatePredictions(data);
                } else {
                    alert('Error fetching data: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error: ' + error.message);
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
                    maintainAspectRatio: false,
                    plugins: {
                        zoom: {
                            pan: {
                                enabled: true,
                                mode: 'x'
                            },
                            zoom: {
                                enabled: true,
                                mode: 'x'
                            }
                        }
                    }
                }
            });
        }
        
        function updatePriceInfo(data) {
            const priceDisplay = document.getElementById('priceDisplay');
            priceDisplay.innerHTML = `
                <div class="price-display">$${data.current_price?.toFixed(2) || 'N/A'}</div>
                <div>Source: ${data.source}</div>
            `;
        }
        
        function updateIndicators(data) {
            const list = document.getElementById('indicatorsList');
            const indicators = data.indicators;
            
            let html = '';
            if (indicators.rsi) html += `<div>RSI: <strong>${indicators.rsi.toFixed(2)}</strong></div>`;
            if (indicators.sma_20) html += `<div>SMA 20: <strong>${indicators.sma_20.toFixed(2)}</strong></div>`;
            if (indicators.sma_50) html += `<div>SMA 50: <strong>${indicators.sma_50.toFixed(2)}</strong></div>`;
            if (indicators.atr) html += `<div>ATR: <strong>${indicators.atr.toFixed(2)}</strong></div>`;
            
            list.innerHTML = html || '<div>No indicators available</div>';
        }
        
        function updatePredictions(data) {
            const list = document.getElementById('predictionsList');
            
            if (data.predictions && data.predictions.length > 0) {
                let html = '';
                data.predictions.forEach(pred => {
                    html += `
                        <div class="prediction-item">
                            <div>${pred.date}: $${pred.predicted_price}</div>
                            <div style="font-size: 0.9em; color: #666;">
                                Trend: ${pred.trend} (${(pred.confidence * 100).toFixed(0)}% confidence)
                            </div>
                        </div>
                    `;
                });
                list.innerHTML = html;
            } else {
                list.innerHTML = '<div>No predictions available</div>';
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)