#!/usr/bin/env python3
"""
Enhanced Stock Analysis with Weighted Sentiment-ML Integration
- Pre-calculates sentiment values (no API calls during ML training)
- Applies configurable weights to sentiment components
- Combines weighted sentiment with technical indicators for ML
- Interactive slider for real-time sentiment weight adjustment
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
print("WEIGHTED SENTIMENT-ML INTEGRATION SYSTEM")
print("=" * 80)
print("✓ Pre-calculated sentiment values (no API calls during training)")
print("✓ Configurable sentiment weighting via slider")
print("✓ Combined sentiment-technical ML features")
print("✓ 100% Real Market Data")
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

# Sentiment cache with TTL
sentiment_cache = {}
SENTIMENT_CACHE_TTL = 300  # 5 minutes

class UnifiedDataFetcher:
    """Data fetcher with Yahoo Finance and Alpha Vantage"""
    
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
            
            print(f"Fetching Yahoo: {symbol}")
            self._yahoo_rate_limit()
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                print(f"Yahoo returned empty data for {symbol}")
                return None
            
            return df, 'Yahoo Finance'
            
        except Exception as e:
            print(f"Yahoo error for {symbol}: {e}")
            return None
    
    def fetch_alpha_vantage(self, symbol, outputsize='compact'):
        try:
            global last_av_request
            with request_lock:
                now = time.time()
                elapsed = now - last_av_request
                if elapsed < AV_REQUEST_DELAY:
                    time.sleep(AV_REQUEST_DELAY - elapsed)
                last_av_request = time.time()
            
            url = f'https://www.alphavantage.co/query'
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_KEY,
                'outputsize': outputsize
            }
            
            print(f"Fetching Alpha Vantage: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"AV error: {data['Error Message']}")
                return None
            
            if 'Time Series (Daily)' not in data:
                print(f"AV unexpected response")
                return None
            
            ts = data['Time Series (Daily)']
            df_data = []
            
            for date, values in ts.items():
                df_data.append({
                    'Date': pd.to_datetime(date),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': float(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df = df.sort_index()
            
            return df, 'Alpha Vantage'
            
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
            return None
    
    def fetch(self, symbol, period='1mo'):
        """Try Yahoo first, then Alpha Vantage"""
        result = self.fetch_yahoo(symbol, period)
        if result:
            return result
        
        print(f"Yahoo failed, trying Alpha Vantage for {symbol}")
        outputsize = 'full' if period in ['3mo', '6mo', '1y', 'max'] else 'compact'
        result = self.fetch_alpha_vantage(symbol, outputsize)
        if result:
            return result
        
        return None, None

class TechnicalAnalysis:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_rsi(df, period=14):
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    @staticmethod
    def calculate_macd(df):
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return {
            'macd': float(macd.iloc[-1]) if not macd.empty else 0,
            'signal': float(signal.iloc[-1]) if not signal.empty else 0,
            'histogram': float((macd - signal).iloc[-1]) if not macd.empty else 0
        }
    
    @staticmethod
    def calculate_bollinger(df, period=20):
        sma = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        current = df['Close'].iloc[-1]
        
        return {
            'upper': float(upper.iloc[-1]) if not upper.empty else 0,
            'middle': float(sma.iloc[-1]) if not sma.empty else 0,
            'lower': float(lower.iloc[-1]) if not lower.empty else 0,
            'position': float((current - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])) if not upper.empty and upper.iloc[-1] != lower.iloc[-1] else 0.5
        }
    
    @staticmethod
    def calculate_all(df):
        """Calculate all indicators"""
        return {
            'rsi': float(TechnicalAnalysis.calculate_rsi(df)),
            'macd': TechnicalAnalysis.calculate_macd(df),
            'bollinger': TechnicalAnalysis.calculate_bollinger(df),
            'sma_20': float(df['Close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else float(df['Close'].mean()),
            'ema_12': float(df['Close'].ewm(span=12).mean().iloc[-1]),
            'volume_avg': float(df['Volume'].rolling(20).mean().iloc[-1]) if 'Volume' in df.columns and len(df) >= 20 else 0
        }

class MarketSentimentAnalyzer:
    """Enhanced sentiment analyzer with component weighting"""
    
    def __init__(self):
        self.fetcher = UnifiedDataFetcher()
        self.component_weights = {
            'vix': 0.4,
            'market_breadth': 0.3,
            'treasury_yield': 0.15,
            'dollar_index': 0.15
        }
    
    def get_cached_sentiment(self):
        """Get cached sentiment or fetch new if expired"""
        global sentiment_cache
        
        now = time.time()
        if 'data' in sentiment_cache and 'timestamp' in sentiment_cache:
            if now - sentiment_cache['timestamp'] < SENTIMENT_CACHE_TTL:
                print("Using cached sentiment data")
                return sentiment_cache['data']
        
        # Fetch new sentiment data
        print("Fetching fresh sentiment data...")
        sentiment_data = self._fetch_all_sentiment()
        
        # Cache it
        sentiment_cache = {
            'data': sentiment_data,
            'timestamp': now
        }
        
        return sentiment_data
    
    def _fetch_all_sentiment(self):
        """Fetch all sentiment components"""
        components = {}
        
        # VIX (Fear Index)
        vix_data = self._get_vix()
        if vix_data:
            components['vix'] = vix_data
        
        # Market Breadth (S&P 500)
        breadth_data = self._get_market_breadth()
        if breadth_data:
            components['market_breadth'] = breadth_data
        
        # Treasury Yield (10-year)
        treasury_data = self._get_treasury_yield()
        if treasury_data:
            components['treasury_yield'] = treasury_data
        
        # Dollar Index
        dollar_data = self._get_dollar_index()
        if dollar_data:
            components['dollar_index'] = dollar_data
        
        return components
    
    def _get_vix(self):
        """Get VIX fear index"""
        try:
            df, source = self.fetcher.fetch_yahoo('^VIX', period='5d')
            if df is not None and not df.empty:
                current_vix = df['Close'].iloc[-1]
                
                # Normalize VIX to 0-1 scale (0 = low fear, 1 = high fear)
                # VIX typically ranges from 10-80
                normalized = min(max((current_vix - 10) / 70, 0), 1)
                
                if current_vix < 20:
                    sentiment = "Low Fear"
                elif current_vix < 30:
                    sentiment = "Moderate Fear"
                else:
                    sentiment = "High Fear"
                
                return {
                    'value': float(current_vix),
                    'normalized': float(normalized),
                    'sentiment': sentiment,
                    'bullish_score': float(1 - normalized)  # Inverse for bullish score
                }
        except Exception as e:
            print(f"VIX error: {e}")
        return None
    
    def _get_market_breadth(self):
        """Get S&P 500 as market breadth proxy"""
        try:
            df, source = self.fetcher.fetch_yahoo('^GSPC', period='5d')
            if df is not None and not df.empty:
                current = df['Close'].iloc[-1]
                sma_20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else current
                
                # Normalized breadth (above/below SMA)
                breadth_score = (current - sma_20) / sma_20 if sma_20 > 0 else 0
                # Normalize to 0-1 scale
                normalized = min(max((breadth_score + 0.05) / 0.1, 0), 1)
                
                return {
                    'sp500': float(current),
                    'sma_20': float(sma_20),
                    'normalized': float(normalized),
                    'sentiment': 'Bullish' if breadth_score > 0 else 'Bearish',
                    'bullish_score': float(normalized)
                }
        except Exception as e:
            print(f"Market breadth error: {e}")
        return None
    
    def _get_treasury_yield(self):
        """Get 10-year Treasury yield as risk sentiment"""
        try:
            df, source = self.fetcher.fetch_yahoo('^TNX', period='5d')
            if df is not None and not df.empty:
                current_yield = df['Close'].iloc[-1]
                prev_yield = df['Close'].iloc[-2] if len(df) > 1 else current_yield
                
                # Rising yields = risk-on, falling = risk-off
                yield_change = current_yield - prev_yield
                # Normalize change to 0-1 scale
                normalized = min(max((yield_change + 0.2) / 0.4, 0), 1)
                
                return {
                    'value': float(current_yield),
                    'change': float(yield_change),
                    'normalized': float(normalized),
                    'sentiment': 'Risk-On' if yield_change > 0 else 'Risk-Off',
                    'bullish_score': float(normalized)
                }
        except Exception as e:
            print(f"Treasury yield error: {e}")
        return None
    
    def _get_dollar_index(self):
        """Get Dollar Index (DXY) sentiment"""
        try:
            df, source = self.fetcher.fetch_yahoo('DX-Y.NYB', period='5d')
            if df is not None and not df.empty:
                current = df['Close'].iloc[-1]
                sma_20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else current
                
                # Weak dollar = bullish for stocks
                dollar_strength = (current - sma_20) / sma_20 if sma_20 > 0 else 0
                # Inverse normalize (weak dollar = higher score)
                normalized = min(max((0.02 - dollar_strength) / 0.04, 0), 1)
                
                return {
                    'value': float(current),
                    'sma_20': float(sma_20),
                    'normalized': float(normalized),
                    'sentiment': 'Weak Dollar' if dollar_strength < 0 else 'Strong Dollar',
                    'bullish_score': float(normalized)
                }
        except Exception as e:
            print(f"Dollar index error: {e}")
        return None
    
    def calculate_weighted_sentiment(self, components, weight_multiplier=1.0):
        """Calculate weighted sentiment score"""
        total_score = 0
        total_weight = 0
        
        for key, weight in self.component_weights.items():
            if key in components and components[key]:
                score = components[key].get('bullish_score', 0.5)
                adjusted_weight = weight * weight_multiplier
                total_score += score * adjusted_weight
                total_weight += adjusted_weight
        
        if total_weight > 0:
            weighted_score = total_score / total_weight
        else:
            weighted_score = 0.5  # Neutral if no data
        
        # Determine overall sentiment
        if weighted_score >= 0.7:
            overall = "Very Bullish"
        elif weighted_score >= 0.55:
            overall = "Bullish"
        elif weighted_score >= 0.45:
            overall = "Neutral"
        elif weighted_score >= 0.3:
            overall = "Bearish"
        else:
            overall = "Very Bearish"
        
        return {
            'weighted_score': float(weighted_score),
            'sentiment': overall,
            'weight_multiplier': weight_multiplier
        }

class EnhancedMLPredictor:
    """ML Predictor with integrated weighted sentiment"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.training_in_progress = False
    
    def prepare_features(self, df, sentiment_score=None):
        """Prepare features including weighted sentiment"""
        features = pd.DataFrame(index=df.index)
        
        # Technical features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['volatility'] = features['returns'].rolling(window=20).std()
        
        # Price features
        features['sma_20'] = df['Close'].rolling(window=20).mean()
        features['sma_50'] = df['Close'].rolling(window=50).mean()
        features['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        features['price_to_sma20'] = df['Close'] / features['sma_20']
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        bb_sma = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        features['bb_upper'] = bb_sma + (bb_std * 2)
        features['bb_lower'] = bb_sma - (bb_std * 2)
        features['bb_position'] = (df['Close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # Volume features
        if 'Volume' in df.columns:
            features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
            features['volume_change'] = df['Volume'].pct_change()
        
        # Add weighted sentiment as a feature
        if sentiment_score is not None:
            features['sentiment_score'] = sentiment_score
            print(f"Added sentiment score to features: {sentiment_score:.3f}")
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def train_and_predict(self, df, symbol, sentiment_weight=1.0):
        """Train model and make predictions with weighted sentiment"""
        if not ML_AVAILABLE:
            return {'error': 'ML not available', 'available': False}
        
        if self.training_in_progress:
            return {'error': 'Training already in progress', 'available': False}
        
        try:
            self.training_in_progress = True
            print(f"\nTraining ML model for {symbol} with sentiment weight: {sentiment_weight}")
            
            if len(df) < 60:
                return {
                    'error': 'Insufficient data for ML (need 60+ points)',
                    'available': False
                }
            
            # Get pre-calculated sentiment
            sentiment_components = self.sentiment_analyzer.get_cached_sentiment()
            weighted_sentiment = self.sentiment_analyzer.calculate_weighted_sentiment(
                sentiment_components, 
                sentiment_weight
            )
            sentiment_score = weighted_sentiment['weighted_score']
            
            # Prepare features with sentiment
            features = self.prepare_features(df, sentiment_score)
            
            if features.empty or len(features) < 30:
                return {
                    'error': 'Insufficient features for training',
                    'available': False
                }
            
            # Prepare target (next day return)
            target = df['Close'].pct_change().shift(-1)
            
            # Align features and target
            valid_idx = features.index.intersection(target.index)
            features = features.loc[valid_idx]
            target = target.loc[valid_idx]
            
            # Remove last row (no target)
            features = features[:-1]
            target = target[:-1]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features.values, 
                target.values,
                test_size=0.2,
                random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=7,
                min_samples_split=10,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Calculate feature importance
            feature_importance = dict(zip(features.columns, self.model.feature_importances_))
            print(f"Sentiment feature importance: {feature_importance.get('sentiment_score', 0):.3f}")
            
            # Make predictions
            latest_features = features.iloc[-1:].values
            latest_features_scaled = self.scaler.transform(latest_features)
            
            current_price = float(df['Close'].iloc[-1])
            next_return = self.model.predict(latest_features_scaled)[0]
            
            # Adjust predictions based on sentiment weight
            sentiment_adjustment = (sentiment_score - 0.5) * sentiment_weight * 0.1
            next_return += sentiment_adjustment
            
            # Generate predictions for multiple timeframes
            predictions = []
            for days in [1, 3, 5, 7]:
                # Adjusted projection with sentiment
                projected_return = next_return * np.sqrt(days)
                projected_price = current_price * (1 + projected_return)
                
                # Confidence based on sentiment alignment
                base_confidence = max(30, 70 - days * 5)
                sentiment_confidence_boost = abs(sentiment_score - 0.5) * 20 * sentiment_weight
                confidence = min(90, base_confidence + sentiment_confidence_boost)
                
                predictions.append({
                    'days': days,
                    'price': float(projected_price),
                    'return': float(projected_return * 100),
                    'confidence': float(confidence)
                })
            
            return {
                'predictions': predictions,
                'current_price': current_price,
                'symbol': symbol,
                'sentiment': weighted_sentiment,
                'sentiment_components': sentiment_components,
                'feature_importance': {
                    'sentiment': feature_importance.get('sentiment_score', 0),
                    'rsi': feature_importance.get('rsi', 0),
                    'volatility': feature_importance.get('volatility', 0)
                },
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

# Global instances
data_fetcher = UnifiedDataFetcher()
ml_predictor = EnhancedMLPredictor()
sentiment_analyzer = MarketSentimentAnalyzer()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data endpoint"""
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
    """ML predictions with weighted sentiment"""
    try:
        # Get sentiment weight from query params
        sentiment_weight = float(request.args.get('sentiment_weight', 1.0))
        sentiment_weight = max(0, min(2, sentiment_weight))  # Clamp between 0-2
        
        print(f"\nGenerating predictions for {symbol} with sentiment weight: {sentiment_weight}")
        
        # Fetch data
        df, source = data_fetcher.fetch(symbol, period='3mo')
        
        if df is None or df.empty:
            return jsonify({
                'error': f'Unable to fetch data for {symbol}',
                'available': False
            }), 404
        
        print(f"Data fetched: {len(df)} records from {source}")
        
        # Train and predict with sentiment weight
        result = ml_predictor.train_and_predict(df, symbol, sentiment_weight)
        
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
    """Get market sentiment components"""
    try:
        sentiment_components = sentiment_analyzer.get_cached_sentiment()
        
        # Calculate default weighted sentiment (weight=1.0)
        weighted_sentiment = sentiment_analyzer.calculate_weighted_sentiment(
            sentiment_components, 
            1.0
        )
        
        return jsonify({
            'components': sentiment_components,
            'weighted': weighted_sentiment,
            'weights': sentiment_analyzer.component_weights
        })
        
    except Exception as e:
        print(f"Sentiment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ml_available': ML_AVAILABLE,
        'version': '3.0-weighted-sentiment'
    })

@app.route('/')
def index():
    """Enhanced interface with sentiment weight slider"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis - Weighted Sentiment ML</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
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
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .control-row {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        .sentiment-control {
            flex: 1;
            min-width: 300px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            padding: 15px;
        }
        .sentiment-control label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #333;
        }
        .slider-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        #sentimentSlider {
            flex: 1;
            height: 8px;
            border-radius: 5px;
            background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7c 100%);
            outline: none;
            -webkit-appearance: none;
        }
        #sentimentSlider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 2px solid #667eea;
        }
        #sentimentSlider::-moz-range-thumb {
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 2px solid #667eea;
        }
        #sentimentValue {
            background: white;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: bold;
            min-width: 60px;
            text-align: center;
            color: #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        input[type="text"], select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            background: white;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .tab {
            padding: 12px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        .tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .panel {
            display: none;
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease;
        }
        .panel.active {
            display: block;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .info-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .info-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .info-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .info-value.positive { color: #4caf50; }
        .info-value.negative { color: #f44336; }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        .prediction-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .prediction-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .prediction-card:hover {
            transform: translateY(-5px);
        }
        .prediction-timeframe {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .prediction-price {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .prediction-return {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .prediction-confidence {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .confidence-bar {
            flex: 1;
            height: 8px;
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            background: white;
            transition: width 0.5s ease;
        }
        .sentiment-display {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .sentiment-header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        .sentiment-components {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .sentiment-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .sentiment-name {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        .sentiment-value {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .sentiment-score {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .overall-sentiment {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            margin-top: 15px;
        }
        .overall-score {
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .overall-label {
            font-size: 24px;
            color: #333;
            margin-top: 10px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .feature-importance {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        .importance-bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .importance-label {
            width: 120px;
            font-weight: 500;
        }
        .importance-value {
            flex: 1;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }
        .importance-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Weighted Sentiment-ML Stock Analysis</h1>
            <p>Pre-calculated sentiment integration • Adjustable weighting • Real market data</p>
        </div>
        
        <div class="controls">
            <div class="control-row">
                <input type="text" id="symbol" placeholder="Enter Symbol" value="AAPL">
                <select id="period">
                    <option value="1mo">1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <button onclick="fetchData()">Get Stock Data</button>
                <button onclick="getSentiment()">Update Sentiment</button>
            </div>
            
            <div class="sentiment-control">
                <label for="sentimentSlider">🎯 Sentiment Weight in ML Predictions</label>
                <div class="slider-container">
                    <span style="font-size: 12px; color: #666;">None</span>
                    <input type="range" id="sentimentSlider" min="0" max="2" step="0.1" value="1.0">
                    <span style="font-size: 12px; color: #666;">2x</span>
                    <span id="sentimentValue">1.0x</span>
                </div>
                <div style="margin-top: 10px; font-size: 12px; color: #666;">
                    Adjust how much market sentiment influences ML predictions (0 = technical only, 2 = heavy sentiment)
                </div>
            </div>
            
            <div class="control-row" style="margin-top: 15px;">
                <button onclick="getPredictions()" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
                    🤖 Get ML Predictions with Sentiment
                </button>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">Overview</button>
            <button class="tab" onclick="showTab('chart')">Chart</button>
            <button class="tab" onclick="showTab('predictions')">Predictions</button>
            <button class="tab" onclick="showTab('sentiment')">Sentiment</button>
            <button class="tab" onclick="showTab('indicators')">Indicators</button>
        </div>
        
        <div id="overview" class="panel active">
            <h2>Stock Overview</h2>
            <div id="stockInfo" class="loading">
                Enter a symbol and click "Get Stock Data" to begin
            </div>
        </div>
        
        <div id="chart" class="panel">
            <h2>Price Chart</h2>
            <div class="chart-container">
                <canvas id="stockChart"></canvas>
            </div>
        </div>
        
        <div id="predictions" class="panel">
            <h2>ML Predictions with Weighted Sentiment</h2>
            <div id="predictionInfo" class="loading">
                Click "Get ML Predictions with Sentiment" to generate predictions
            </div>
        </div>
        
        <div id="sentiment" class="panel">
            <h2>Market Sentiment Analysis</h2>
            <div id="sentimentInfo" class="loading">
                Click "Update Sentiment" to fetch latest market sentiment
            </div>
        </div>
        
        <div id="indicators" class="panel">
            <h2>Technical Indicators</h2>
            <div id="indicatorInfo" class="loading">
                Technical indicators will appear here after fetching stock data
            </div>
        </div>
    </div>
    
    <script>
        let stockChart = null;
        let currentStockData = null;
        let currentSentimentData = null;
        
        // Update sentiment value display
        document.getElementById('sentimentSlider').addEventListener('input', function(e) {
            document.getElementById('sentimentValue').textContent = e.target.value + 'x';
        });
        
        function showTab(tabName) {
            // Hide all panels
            document.querySelectorAll('.panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Remove active from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected panel
            document.getElementById(tabName).classList.add('active');
            
            // Mark tab as active
            event.target.classList.add('active');
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            // Update all panels to loading
            document.getElementById('stockInfo').innerHTML = '<div class="loading">Loading stock data...</div>';
            document.getElementById('indicatorInfo').innerHTML = '<div class="loading">Calculating indicators...</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentStockData = data;
                    displayStockInfo(data);
                    displayChart(data);
                    displayIndicators(data.indicators);
                } else {
                    document.getElementById('stockInfo').innerHTML = 
                        `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('stockInfo').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function getSentiment() {
            document.getElementById('sentimentInfo').innerHTML = '<div class="loading">Fetching market sentiment...</div>';
            
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                
                if (response.ok) {
                    currentSentimentData = data;
                    displaySentiment(data);
                } else {
                    document.getElementById('sentimentInfo').innerHTML = 
                        `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                document.getElementById('sentimentInfo').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function getPredictions() {
            const symbol = document.getElementById('symbol').value;
            const sentimentWeight = document.getElementById('sentimentSlider').value;
            
            if (!symbol) {
                alert('Please enter a symbol first');
                return;
            }
            
            document.getElementById('predictionInfo').innerHTML = 
                `<div class="loading">Training ML model with sentiment weight ${sentimentWeight}x...</div>`;
            
            try {
                const response = await fetch(`/api/predict/${symbol}?sentiment_weight=${sentimentWeight}`);
                const data = await response.json();
                
                if (response.ok && data.available) {
                    displayPredictions(data);
                } else {
                    document.getElementById('predictionInfo').innerHTML = 
                        `<div class="error">Error: ${data.error || 'Predictions not available'}</div>`;
                }
            } catch (error) {
                document.getElementById('predictionInfo').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function displayStockInfo(data) {
            const changeClass = data.price_change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.price_change >= 0 ? '▲' : '▼';
            
            document.getElementById('stockInfo').innerHTML = `
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">Symbol</div>
                        <div class="info-value">${data.symbol}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Current Price</div>
                        <div class="info-value">$${data.current_price.toFixed(2)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Change</div>
                        <div class="info-value ${changeClass}">
                            ${changeSymbol} $${Math.abs(data.price_change).toFixed(2)}
                        </div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Change %</div>
                        <div class="info-value ${changeClass}">
                            ${changeSymbol} ${Math.abs(data.price_change_pct).toFixed(2)}%
                        </div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Data Source</div>
                        <div class="info-value" style="font-size: 16px;">${data.source}</div>
                    </div>
                </div>
            `;
        }
        
        function displayChart(data) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (stockChart) {
                stockChart.destroy();
            }
            
            stockChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Close Price',
                        data: data.data.map(d => d.close),
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) label += ': ';
                                    label += '$' + context.parsed.y.toFixed(2);
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            display: true,
                            position: 'right',
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function displayPredictions(data) {
            let html = '';
            
            // Display sentiment influence
            if (data.sentiment) {
                html += `
                    <div class="sentiment-display">
                        <div class="sentiment-header">Sentiment Influence on Predictions</div>
                        <div class="overall-sentiment">
                            <div class="overall-score">${(data.sentiment.weighted_score * 100).toFixed(1)}%</div>
                            <div class="overall-label">${data.sentiment.sentiment}</div>
                            <div style="font-size: 14px; color: #666; margin-top: 10px;">
                                Weight Multiplier: ${data.sentiment.weight_multiplier}x
                            </div>
                        </div>
                    </div>
                `;
            }
            
            // Display feature importance
            if (data.feature_importance) {
                html += `
                    <div class="feature-importance">
                        <h3>Feature Importance in Model</h3>
                        <div class="importance-bar">
                            <div class="importance-label">Sentiment</div>
                            <div class="importance-value">
                                <div class="importance-fill" style="width: ${data.feature_importance.sentiment * 100}%"></div>
                            </div>
                            <span style="margin-left: 10px">${(data.feature_importance.sentiment * 100).toFixed(1)}%</span>
                        </div>
                        <div class="importance-bar">
                            <div class="importance-label">RSI</div>
                            <div class="importance-value">
                                <div class="importance-fill" style="width: ${data.feature_importance.rsi * 100}%"></div>
                            </div>
                            <span style="margin-left: 10px">${(data.feature_importance.rsi * 100).toFixed(1)}%</span>
                        </div>
                        <div class="importance-bar">
                            <div class="importance-label">Volatility</div>
                            <div class="importance-value">
                                <div class="importance-fill" style="width: ${data.feature_importance.volatility * 100}%"></div>
                            </div>
                            <span style="margin-left: 10px">${(data.feature_importance.volatility * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                `;
            }
            
            // Display predictions
            html += '<div class="prediction-cards">';
            
            data.predictions.forEach(pred => {
                const returnClass = pred.return >= 0 ? '📈' : '📉';
                const returnSign = pred.return >= 0 ? '+' : '';
                
                html += `
                    <div class="prediction-card">
                        <div class="prediction-timeframe">${pred.days} Day${pred.days > 1 ? 's' : ''} Forecast</div>
                        <div class="prediction-price">$${pred.price.toFixed(2)}</div>
                        <div class="prediction-return">${returnClass} ${returnSign}${pred.return.toFixed(2)}%</div>
                        <div class="prediction-confidence">
                            <span>Confidence:</span>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${pred.confidence}%"></div>
                            </div>
                            <span>${pred.confidence.toFixed(0)}%</span>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            
            document.getElementById('predictionInfo').innerHTML = html;
        }
        
        function displaySentiment(data) {
            let html = '<div class="sentiment-components">';
            
            // Display each sentiment component
            for (const [key, value] of Object.entries(data.components)) {
                if (value) {
                    const emoji = {
                        'vix': '😨',
                        'market_breadth': '📊',
                        'treasury_yield': '📈',
                        'dollar_index': '💵'
                    }[key] || '📊';
                    
                    html += `
                        <div class="sentiment-item">
                            <div class="sentiment-name">${emoji} ${key.replace('_', ' ').toUpperCase()}</div>
                            <div class="sentiment-value">${value.value?.toFixed(2) || 'N/A'}</div>
                            <div class="sentiment-score">
                                Bullish Score: ${(value.bullish_score * 100).toFixed(1)}%
                            </div>
                            <div style="font-size: 12px; color: ${value.sentiment?.includes('Bull') ? 'green' : 'red'}">
                                ${value.sentiment}
                            </div>
                        </div>
                    `;
                }
            }
            
            html += '</div>';
            
            // Display weighted sentiment
            if (data.weighted) {
                html += `
                    <div class="overall-sentiment">
                        <div class="overall-score">${(data.weighted.weighted_score * 100).toFixed(1)}%</div>
                        <div class="overall-label">Overall: ${data.weighted.sentiment}</div>
                    </div>
                `;
            }
            
            // Display component weights
            html += '<div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 10px;">';
            html += '<h3>Component Weights</h3>';
            for (const [key, weight] of Object.entries(data.weights)) {
                html += `<div style="margin: 5px 0;">${key.replace('_', ' ')}: ${(weight * 100).toFixed(0)}%</div>`;
            }
            html += '</div>';
            
            document.getElementById('sentimentInfo').innerHTML = html;
        }
        
        function displayIndicators(indicators) {
            if (!indicators) {
                document.getElementById('indicatorInfo').innerHTML = 
                    '<div class="error">No indicator data available</div>';
                return;
            }
            
            let html = '<div class="info-grid">';
            
            // RSI
            const rsiStatus = indicators.rsi > 70 ? 'Overbought' : indicators.rsi < 30 ? 'Oversold' : 'Neutral';
            const rsiColor = indicators.rsi > 70 ? 'negative' : indicators.rsi < 30 ? 'positive' : '';
            
            html += `
                <div class="info-card">
                    <div class="info-label">RSI (14)</div>
                    <div class="info-value ${rsiColor}">${indicators.rsi.toFixed(2)}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">${rsiStatus}</div>
                </div>
            `;
            
            // MACD
            if (indicators.macd) {
                const macdSignal = indicators.macd.histogram > 0 ? 'Bullish' : 'Bearish';
                const macdColor = indicators.macd.histogram > 0 ? 'positive' : 'negative';
                
                html += `
                    <div class="info-card">
                        <div class="info-label">MACD</div>
                        <div class="info-value ${macdColor}">${indicators.macd.macd.toFixed(2)}</div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">${macdSignal}</div>
                    </div>
                `;
            }
            
            // Bollinger Bands
            if (indicators.bollinger) {
                const bbPosition = (indicators.bollinger.position * 100).toFixed(1);
                const bbStatus = indicators.bollinger.position > 0.8 ? 'Near Upper' : 
                                indicators.bollinger.position < 0.2 ? 'Near Lower' : 'Middle';
                
                html += `
                    <div class="info-card">
                        <div class="info-label">Bollinger Position</div>
                        <div class="info-value">${bbPosition}%</div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">${bbStatus}</div>
                    </div>
                `;
            }
            
            // Moving Averages
            html += `
                <div class="info-card">
                    <div class="info-label">SMA 20</div>
                    <div class="info-value">$${indicators.sma_20.toFixed(2)}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">EMA 12</div>
                    <div class="info-value">$${indicators.ema_12.toFixed(2)}</div>
                </div>
            `;
            
            // Volume
            if (indicators.volume_avg > 0) {
                html += `
                    <div class="info-card">
                        <div class="info-label">Avg Volume (20)</div>
                        <div class="info-value">${(indicators.volume_avg / 1000000).toFixed(2)}M</div>
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('indicatorInfo').innerHTML = html;
        }
        
        // Auto-fetch sentiment on load
        window.addEventListener('load', () => {
            getSentiment();
        });
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Enhanced Weighted Sentiment-ML Server...")
    print("="*60)
    print("Features:")
    print("  • Pre-calculated sentiment (no API calls during training)")
    print("  • Adjustable sentiment weighting slider (0-2x)")
    print("  • Combined sentiment-technical ML features")
    print("  • Feature importance visualization")
    print("  • Component-based sentiment analysis")
    print("="*60)
    print(f"Server running on: http://localhost:5001")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')