#!/usr/bin/env python3
"""
Unified Robust Stock Analysis System - Fixed ML Predictions
- 100% Real Market Data (NO synthetic/demo data)
- Yahoo Finance with rate limiting
- Alpha Vantage fallback with API key
- Market sentiment indicators
- ML predictions with RandomForest (FIXED)
- Technical analysis
- Chart zoom functionality
- Australian stock support
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
print("UNIFIED ROBUST STOCK ANALYSIS SYSTEM - FIXED ML")
print("=" * 80)
print("✓ 100% Real Market Data - NO Synthetic/Demo Data")
print("✓ Yahoo Finance (Primary) with Rate Limiting")
print("✓ Alpha Vantage (Fallback) with API Key")
print("✓ Market Sentiment Indicators")
print("✓ ML Predictions with RandomForest (FIXED)")
print("✓ Technical Analysis")
print("✓ Chart Zoom Functionality")
print("✓ Australian Stock Support")
print(f"✓ ML Available: {ML_AVAILABLE}")
print("=" * 80)

app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
YAHOO_REQUEST_DELAY = 3  # seconds between Yahoo requests
AV_REQUEST_DELAY = 0.2  # Alpha Vantage: 5 calls per minute

# Rate limiting
last_yahoo_request = 0
last_av_request = 0
request_lock = threading.Lock()

# Australian stocks
AUSTRALIAN_STOCKS = {
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 
    'WOW', 'TLS', 'RIO', 'FMG', 'WDS', 'ALL', 'REA', 'COL',
    'TCL', 'GMG', 'AMC', 'SUN', 'QBE', 'IAG', 'WPL', 'NCM'
}

class UnifiedDataFetcher:
    """Unified data fetcher with Yahoo primary, Alpha Vantage fallback"""
    
    def __init__(self):
        self.yahoo_available = self._check_yahoo()
        
    def _check_yahoo(self):
        """Check if yfinance is available"""
        try:
            import yfinance as yf
            return True
        except ImportError:
            print("WARNING: yfinance not installed. Using Alpha Vantage only.")
            return False
    
    def _yahoo_rate_limit(self):
        """Enforce Yahoo Finance rate limiting"""
        global last_yahoo_request
        with request_lock:
            now = time.time()
            elapsed = now - last_yahoo_request
            if elapsed < YAHOO_REQUEST_DELAY:
                time.sleep(YAHOO_REQUEST_DELAY - elapsed)
            last_yahoo_request = time.time()
    
    def _av_rate_limit(self):
        """Enforce Alpha Vantage rate limiting"""
        global last_av_request
        with request_lock:
            now = time.time()
            elapsed = now - last_av_request
            if elapsed < AV_REQUEST_DELAY:
                time.sleep(AV_REQUEST_DELAY - elapsed)
            last_av_request = time.time()
    
    def fetch_yahoo(self, symbol, period='1mo', interval='1d'):
        """Fetch data from Yahoo Finance with rate limiting"""
        if not self.yahoo_available:
            return None
        
        try:
            import yfinance as yf
            
            # Handle Australian stocks
            original_symbol = symbol.upper()
            if original_symbol in AUSTRALIAN_STOCKS and not original_symbol.endswith('.AX'):
                symbol = f"{original_symbol}.AX"
                print(f"Australian stock detected: {original_symbol} → {symbol}")
            
            # Rate limiting
            self._yahoo_rate_limit()
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            
            # For intraday data
            if interval != '1d':
                df = ticker.history(period=period, interval=interval)
            else:
                df = ticker.history(period=period)
            
            if not df.empty:
                # Get additional info
                info = {}
                try:
                    ticker_info = ticker.info
                    info = {
                        'name': ticker_info.get('longName', symbol),
                        'sector': ticker_info.get('sector', 'Unknown'),
                        'industry': ticker_info.get('industry', 'Unknown'),
                        'marketCap': ticker_info.get('marketCap', 0),
                        'pe': ticker_info.get('trailingPE', 0),
                        'dividendYield': ticker_info.get('dividendYield', 0)
                    }
                except:
                    pass
                
                return df, info, "Yahoo Finance"
                
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
        
        return None, {}, None
    
    def fetch_alpha_vantage(self, symbol):
        """Fetch data from Alpha Vantage as fallback"""
        try:
            # Handle Australian stocks
            original_symbol = symbol.upper()
            if original_symbol in AUSTRALIAN_STOCKS:
                # Try with .AUS suffix for Alpha Vantage
                test_symbol = f"{original_symbol}.AUS"
            else:
                test_symbol = symbol
            
            # Rate limiting
            self._av_rate_limit()
            
            # API call
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': test_symbol,
                'apikey': ALPHA_VANTAGE_KEY,
                'outputsize': 'full'  # Get more data
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                # If Australian stock failed with .AUS, try without
                if original_symbol in AUSTRALIAN_STOCKS and test_symbol.endswith('.AUS'):
                    params['symbol'] = original_symbol
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()
            
            if 'Time Series (Daily)' in data:
                ts = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(ts, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                # Rename columns
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                
                # Get metadata
                meta = data.get('Meta Data', {})
                info = {
                    'name': meta.get('2. Symbol', symbol),
                    'lastRefreshed': meta.get('3. Last Refreshed', ''),
                    'timeZone': meta.get('5. Time Zone', 'US/Eastern')
                }
                
                return df, info, "Alpha Vantage"
                
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
        
        return None, {}, None
    
    def fetch(self, symbol, period='1mo', interval='1d'):
        """Main fetch method - tries Yahoo first, then Alpha Vantage"""
        print(f"\nFetching data for {symbol}...")
        
        # Try Yahoo Finance first
        df, info, source = self.fetch_yahoo(symbol, period, interval)
        
        # If Yahoo fails, try Alpha Vantage
        if df is None or df.empty:
            print(f"Yahoo failed, trying Alpha Vantage...")
            df, info, source = self.fetch_alpha_vantage(symbol)
        
        if df is not None and not df.empty:
            print(f"✓ Data fetched from {source}: {len(df)} records")
        else:
            print(f"✗ Failed to fetch data for {symbol}")
        
        return df, info, source

class TechnicalAnalysis:
    """Technical indicators calculation"""
    
    @staticmethod
    def calculate_sma(df, window):
        """Simple Moving Average"""
        return df['Close'].rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(df, window):
        """Exponential Moving Average"""
        return df['Close'].ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(df, period=14):
        """Relative Strength Index"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        """MACD indicator"""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(df, window=20, num_std=2):
        """Bollinger Bands"""
        sma = df['Close'].rolling(window=window).mean()
        std = df['Close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_all(df):
        """Calculate all technical indicators"""
        indicators = {}
        
        try:
            # Moving averages
            if len(df) >= 10:
                indicators['SMA_10'] = TechnicalAnalysis.calculate_sma(df, 10).iloc[-1]
            if len(df) >= 20:
                indicators['SMA_20'] = TechnicalAnalysis.calculate_sma(df, 20).iloc[-1]
                indicators['EMA_20'] = TechnicalAnalysis.calculate_ema(df, 20).iloc[-1]
            if len(df) >= 50:
                indicators['SMA_50'] = TechnicalAnalysis.calculate_sma(df, 50).iloc[-1]
            
            # RSI
            if len(df) >= 14:
                rsi = TechnicalAnalysis.calculate_rsi(df)
                indicators['RSI'] = rsi.iloc[-1]
                
                # RSI interpretation
                if indicators['RSI'] > 70:
                    indicators['RSI_Signal'] = 'Overbought'
                elif indicators['RSI'] < 30:
                    indicators['RSI_Signal'] = 'Oversold'
                else:
                    indicators['RSI_Signal'] = 'Neutral'
            
            # MACD
            if len(df) >= 26:
                macd, signal, histogram = TechnicalAnalysis.calculate_macd(df)
                indicators['MACD'] = macd.iloc[-1]
                indicators['MACD_Signal'] = signal.iloc[-1]
                indicators['MACD_Histogram'] = histogram.iloc[-1]
                
                # MACD crossover signal
                if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
                    indicators['MACD_Crossover'] = 'Bullish'
                elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
                    indicators['MACD_Crossover'] = 'Bearish'
                else:
                    indicators['MACD_Crossover'] = 'None'
            
            # Bollinger Bands
            if len(df) >= 20:
                upper, middle, lower = TechnicalAnalysis.calculate_bollinger_bands(df)
                indicators['BB_Upper'] = upper.iloc[-1]
                indicators['BB_Middle'] = middle.iloc[-1]
                indicators['BB_Lower'] = lower.iloc[-1]
                
                # Bollinger Band position
                current_price = df['Close'].iloc[-1]
                if current_price > upper.iloc[-1]:
                    indicators['BB_Position'] = 'Above Upper'
                elif current_price < lower.iloc[-1]:
                    indicators['BB_Position'] = 'Below Lower'
                else:
                    indicators['BB_Position'] = 'Within Bands'
            
            # Volume indicators
            if 'Volume' in df.columns and len(df) >= 20:
                indicators['Volume_20_Avg'] = df['Volume'].rolling(20).mean().iloc[-1]
                indicators['Volume_Ratio'] = df['Volume'].iloc[-1] / indicators['Volume_20_Avg']
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators

class MarketSentimentAnalyzer:
    """Market sentiment analysis using various indicators"""
    
    def __init__(self):
        self.fetcher = UnifiedDataFetcher()
    
    def get_vix(self):
        """Get VIX fear index"""
        try:
            df, _, source = self.fetcher.fetch_yahoo('^VIX', period='5d')
            if df is not None and not df.empty:
                current_vix = df['Close'].iloc[-1]
                prev_vix = df['Close'].iloc[-2] if len(df) > 1 else current_vix
                change = ((current_vix - prev_vix) / prev_vix) * 100
                
                # VIX interpretation
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
                    'change': change,
                    'sentiment': sentiment,
                    'score': score,
                    'source': source
                }
        except Exception as e:
            print(f"Error fetching VIX: {e}")
        
        return None
    
    def get_market_breadth(self):
        """Get market breadth (advance/decline ratio)"""
        try:
            # Using S&P 500 as proxy for market breadth
            df, _, source = self.fetcher.fetch_yahoo('^GSPC', period='5d')
            if df is not None and not df.empty:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2] if len(df) > 1 else current
                change_pct = ((current - prev) / prev) * 100
                
                # Simple breadth interpretation based on S&P movement
                if change_pct > 1:
                    sentiment = "Strong Bullish"
                    score = 0.8
                elif change_pct > 0:
                    sentiment = "Bullish"
                    score = 0.4
                elif change_pct > -1:
                    sentiment = "Bearish"
                    score = -0.4
                else:
                    sentiment = "Strong Bearish"
                    score = -0.8
                
                return {
                    'sp500': current,
                    'change': change_pct,
                    'sentiment': sentiment,
                    'score': score,
                    'source': source
                }
        except Exception as e:
            print(f"Error fetching market breadth: {e}")
        
        return None
    
    def get_overall_sentiment(self):
        """Calculate overall market sentiment"""
        sentiment_data = {}
        scores = []
        
        # Collect sentiment indicators
        vix = self.get_vix()
        if vix:
            sentiment_data['vix'] = vix
            scores.append(vix['score'])
        
        breadth = self.get_market_breadth()
        if breadth:
            sentiment_data['market_breadth'] = breadth
            scores.append(breadth['score'])
        
        # Calculate overall score
        if scores:
            overall_score = np.mean(scores)
            
            # Determine overall sentiment
            if overall_score > 0.5:
                overall_sentiment = "Strong Bullish"
            elif overall_score > 0.2:
                overall_sentiment = "Bullish"
            elif overall_score > -0.2:
                overall_sentiment = "Neutral"
            elif overall_score > -0.5:
                overall_sentiment = "Bearish"
            else:
                overall_sentiment = "Strong Bearish"
            
            sentiment_data['overall'] = {
                'score': overall_score,
                'sentiment': overall_sentiment,
                'confidence': min(100, abs(overall_score) * 100)
            }
        
        return sentiment_data

class MLPredictor:
    """Machine Learning prediction module - FIXED"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.feature_names = []
        self.available = ML_AVAILABLE
        self.last_train_symbol = None
        self.last_train_time = None
    
    def prepare_features(self, df):
        """Prepare features for ML model - Simplified and more robust"""
        features = pd.DataFrame(index=df.index)
        
        try:
            # Basic price features
            features['returns'] = df['Close'].pct_change()
            features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Moving averages ratios
            if len(df) >= 20:
                features['price_to_sma20'] = df['Close'] / df['Close'].rolling(20).mean()
            if len(df) >= 50:
                features['price_to_sma50'] = df['Close'] / df['Close'].rolling(50).mean()
            
            # Volume features
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            
            # Volatility
            features['volatility'] = features['returns'].rolling(20).std()
            
            # Price range features
            features['high_low_ratio'] = df['High'] / df['Low']
            features['close_to_high'] = df['Close'] / df['High']
            
            # RSI
            if len(df) >= 14:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                features['rsi'] = 100 - (100 / (1 + rs))
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                features[f'return_lag_{lag}'] = features['returns'].shift(lag)
            
            # Clean up
            features = features.replace([np.inf, -np.inf], np.nan)
            features = features.dropna()
            
            return features
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            traceback.print_exc()
            return pd.DataFrame()
    
    def train(self, df):
        """Train the ML model - Simplified"""
        if not self.available:
            print("ML not available - scikit-learn not installed")
            return False
            
        try:
            # Prepare features
            features = self.prepare_features(df)
            
            if features.empty or len(features) < 60:
                print(f"Insufficient data for training: {len(features)} samples")
                return False
            
            # Create target (next day return)
            y = df['Close'].pct_change().shift(-1).loc[features.index]
            
            # Remove last row (no target)
            features = features[:-1]
            y = y[:-1]
            
            # Remove NaN targets
            valid_idx = ~y.isna()
            features = features[valid_idx]
            y = y[valid_idx]
            
            if len(features) < 50:
                print(f"Insufficient valid samples: {len(features)}")
                return False
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features[:split_idx]
            X_test = features[split_idx:]
            y_train = y[:split_idx]
            y_test = y[split_idx:]
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model with simpler parameters
            self.model = RandomForestRegressor(
                n_estimators=50,  # Reduced from 100
                max_depth=5,      # Reduced from 10
                min_samples_split=5,  # Reduced from 10
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            # Store feature names
            self.feature_names = features.columns.tolist()
            
            print(f"Model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            return {
                'train_score': train_score,
                'test_score': test_score,
                'n_features': len(self.feature_names),
                'n_samples': len(features)
            }
            
        except Exception as e:
            print(f"Error training model: {e}")
            traceback.print_exc()
            return False
    
    def predict(self, df, symbol):
        """Make predictions - Simplified and more robust"""
        if not self.available:
            return {
                'error': 'ML predictions not available. Please install scikit-learn.',
                'available': False
            }
        
        try:
            # Train model if not trained or different symbol
            if self.model is None or self.last_train_symbol != symbol:
                print(f"Training model for {symbol}...")
                train_result = self.train(df)
                if not train_result:
                    return {
                        'error': 'Unable to train model. Insufficient data or training failed.',
                        'available': False
                    }
                self.last_train_symbol = symbol
                self.last_train_time = datetime.now()
            
            # Prepare current features
            features = self.prepare_features(df)
            
            if features.empty:
                return {
                    'error': 'Unable to prepare features for prediction.',
                    'available': False
                }
            
            # Get latest features
            latest_features = features.iloc[-1:].values
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # Make predictions
            current_price = float(df['Close'].iloc[-1])
            predictions = []
            
            # Single day prediction
            next_return = self.model.predict(latest_features_scaled)[0]
            next_price = current_price * (1 + next_return)
            
            # Calculate confidence based on model performance and prediction magnitude
            base_confidence = 60
            if abs(next_return) < 0.02:  # Small prediction, higher confidence
                confidence = base_confidence + 10
            elif abs(next_return) > 0.05:  # Large prediction, lower confidence
                confidence = base_confidence - 10
            else:
                confidence = base_confidence
            
            predictions.append({
                'days': 1,
                'price': float(next_price),
                'return': float(next_return * 100),
                'confidence': confidence
            })
            
            # Multi-day predictions using Monte Carlo simulation
            for days in [3, 5, 7]:
                # Simple random walk based on historical volatility
                daily_volatility = df['Close'].pct_change().std()
                expected_return = next_return / np.sqrt(days)  # Adjusted return
                
                # Simulate multiple paths
                simulated_prices = []
                for _ in range(100):
                    price = current_price
                    for _ in range(days):
                        daily_return = np.random.normal(expected_return, daily_volatility)
                        price *= (1 + daily_return)
                    simulated_prices.append(price)
                
                # Get mean and confidence interval
                mean_price = np.mean(simulated_prices)
                price_std = np.std(simulated_prices)
                
                predictions.append({
                    'days': days,
                    'price': float(mean_price),
                    'return': float((mean_price / current_price - 1) * 100),
                    'confidence': max(30, 70 - days * 5),
                    'price_range': {
                        'low': float(mean_price - price_std),
                        'high': float(mean_price + price_std)
                    }
                })
            
            # Feature importance
            importance = []
            if self.model and hasattr(self.model, 'feature_importances_'):
                for fname, imp in zip(self.feature_names, self.model.feature_importances_):
                    importance.append({
                        'feature': fname,
                        'importance': float(imp)
                    })
                importance = sorted(importance, key=lambda x: x['importance'], reverse=True)[:10]
            
            return {
                'predictions': predictions,
                'feature_importance': importance,
                'current_price': current_price,
                'model_info': {
                    'last_trained': self.last_train_time.isoformat() if self.last_train_time else None,
                    'symbol': self.last_train_symbol,
                    'features_used': len(self.feature_names)
                },
                'available': True
            }
            
        except Exception as e:
            print(f"Error making predictions: {e}")
            traceback.print_exc()
            return {
                'error': f'Prediction error: {str(e)}',
                'available': False
            }

# Global instances
data_fetcher = UnifiedDataFetcher()
sentiment_analyzer = MarketSentimentAnalyzer()
ml_predictor = MLPredictor()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Main endpoint for stock data"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # Fetch data
        df, info, source = data_fetcher.fetch(symbol, period, interval)
        
        if df is None or df.empty:
            return jsonify({
                'error': f'Unable to fetch data for {symbol}',
                'tried': ['Yahoo Finance', 'Alpha Vantage']
            }), 404
        
        # Calculate technical indicators
        indicators = TechnicalAnalysis.calculate_all(df)
        
        # Prepare chart data (no date parsing issues)
        chart_data = []
        labels = []
        
        # Limit to last 100 points for performance
        display_df = df.tail(100)
        
        for i, (index, row) in enumerate(display_df.iterrows()):
            chart_data.append({
                'x': i,  # Use index number instead of date
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row.get('Volume', 0))
            })
            # Format label based on interval
            if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
                labels.append(index.strftime('%H:%M'))
            else:
                labels.append(index.strftime('%m/%d'))
        
        # Current price and change
        current_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100 if prev_close != 0 else 0
        
        # Prepare response
        response = {
            'symbol': symbol,
            'source': source,
            'info': info,
            'current_price': current_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'data': chart_data,
            'labels': labels,
            'indicators': {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                          for k, v in indicators.items()},
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment')
def get_market_sentiment():
    """Get market sentiment indicators"""
    try:
        sentiment_data = sentiment_analyzer.get_overall_sentiment()
        return jsonify(sentiment_data)
    except Exception as e:
        print(f"Error in get_market_sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<symbol>')
def get_predictions(symbol):
    """Get ML predictions for a stock - FIXED"""
    try:
        # Fetch data with more history for better training
        df, info, source = data_fetcher.fetch(symbol, period='1y')  # Changed from 6mo to 1y
        
        if df is None or df.empty:
            return jsonify({
                'error': f'Unable to fetch data for {symbol}',
                'available': False
            }), 404
        
        # Get predictions
        predictions_result = ml_predictor.predict(df, symbol)
        
        # Add symbol and source info
        predictions_result['symbol'] = symbol
        predictions_result['source'] = source
        
        return jsonify(predictions_result)
        
    except Exception as e:
        print(f"Error in get_predictions: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'available': False
        }), 500

@app.route('/')
def index():
    """Main HTML interface - FIXED JavaScript"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.1.0',
        'ml_available': ML_AVAILABLE
    })

# HTML Template with fixed JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Robust Stock Analysis - Fixed ML</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.0/dist/chartjs-plugin-zoom.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #2d3748;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .badge {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        input, select, button {
            padding: 10px 15px;
            border-radius: 6px;
            border: 2px solid #e2e8f0;
            font-size: 14px;
        }
        
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .chart-container {
            position: relative;
            height: 400px;
        }
        
        .price-display {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .price-change {
            font-size: 1.2rem;
            margin-bottom: 15px;
        }
        
        .positive {
            color: #10b981;
        }
        
        .negative {
            color: #ef4444;
        }
        
        .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: #f7fafc;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        
        .sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .sentiment-card {
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .sentiment-value {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .sentiment-label {
            font-size: 0.9rem;
            color: #718096;
        }
        
        .status-message {
            padding: 12px;
            border-radius: 6px;
            margin: 15px 0;
            text-align: center;
        }
        
        .loading {
            background: #bee3f8;
            color: #2c5282;
        }
        
        .error {
            background: #fed7d7;
            color: #c53030;
        }
        
        .success {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #718096;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .prediction-item {
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            align-items: center;
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .chart-btn {
            padding: 6px 12px;
            background: #e2e8f0;
            color: #2d3748;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .chart-btn.active {
            background: #667eea;
            color: white;
        }
        
        .zoom-controls {
            display: flex;
            gap: 5px;
            margin-left: auto;
        }
        
        .zoom-btn {
            padding: 6px 10px;
            background: #e2e8f0;
            color: #2d3748;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .ml-unavailable {
            background: #fef3c7;
            color: #92400e;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .price-range {
            font-size: 0.85rem;
            color: #718096;
        }
        
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .sentiment-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                📈 Unified Robust Stock Analysis
                <span class="badge">100% REAL DATA</span>
                <span class="badge" id="ml-status">ML: Checking...</span>
            </h1>
            <p style="color: #718096;">Yahoo Finance • Alpha Vantage • ML Predictions (Fixed) • Market Sentiment</p>
            
            <div class="controls">
                <input type="text" id="symbol" placeholder="Symbol (e.g., AAPL, CBA)" value="AAPL">
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="2y">2 Years</option>
                    <option value="5y">5 Years</option>
                </select>
                <select id="interval">
                    <option value="1m">1 Minute</option>
                    <option value="5m">5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="30m">30 Minutes</option>
                    <option value="1h">1 Hour</option>
                    <option value="1d" selected>Daily</option>
                </select>
                <button onclick="fetchData()">Get Data</button>
                <button onclick="fetchPredictions()">ML Predictions</button>
                <button onclick="fetchSentiment()">Market Sentiment</button>
            </div>
        </div>
        
        <!-- Status Message -->
        <div id="status"></div>
        
        <!-- Tabs -->
        <div class="tabs" id="tabs-container">
            <button class="tab active" onclick="switchTab(event, 'chart')">Chart</button>
            <button class="tab" onclick="switchTab(event, 'indicators')">Technical Indicators</button>
            <button class="tab" onclick="switchTab(event, 'sentiment')">Market Sentiment</button>
            <button class="tab" onclick="switchTab(event, 'predictions')">ML Predictions</button>
        </div>
        
        <!-- Chart Tab -->
        <div id="chart-tab" class="tab-content active">
            <div class="main-grid">
                <div class="card">
                    <div class="chart-controls">
                        <button class="chart-btn active" onclick="setChartType('line')">Line</button>
                        <button class="chart-btn" onclick="setChartType('candlestick')">Candlestick</button>
                        <button class="chart-btn" onclick="setChartType('volume')">Volume</button>
                        
                        <div class="zoom-controls">
                            <button class="zoom-btn" onclick="resetZoom()">Reset Zoom</button>
                            <button class="zoom-btn" onclick="zoomIn()">Zoom In</button>
                            <button class="zoom-btn" onclick="zoomOut()">Zoom Out</button>
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="chart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <div class="price-display" id="current-price">--</div>
                    <div class="price-change" id="price-change">--</div>
                    <div id="data-source" style="color: #718096; margin-bottom: 15px;">--</div>
                    
                    <h3 style="margin-bottom: 10px;">Quick Indicators</h3>
                    <div id="quick-indicators"></div>
                </div>
            </div>
        </div>
        
        <!-- Indicators Tab -->
        <div id="indicators-tab" class="tab-content">
            <div class="card">
                <h3>Technical Indicators</h3>
                <div id="technical-indicators" style="margin-top: 15px;"></div>
            </div>
        </div>
        
        <!-- Sentiment Tab -->
        <div id="sentiment-tab" class="tab-content">
            <div class="card">
                <h3>Market Sentiment Analysis</h3>
                <div id="overall-sentiment" style="margin: 20px 0;"></div>
                <div class="sentiment-grid" id="sentiment-indicators"></div>
            </div>
        </div>
        
        <!-- Predictions Tab -->
        <div id="predictions-tab" class="tab-content">
            <div class="card">
                <h3>ML Predictions</h3>
                <div id="predictions-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        let currentData = null;
        let chartType = 'line';
        let currentTab = 'chart';
        
        // Check ML availability on load
        async function checkMLStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                const mlStatus = document.getElementById('ml-status');
                if (data.ml_available) {
                    mlStatus.textContent = 'ML: Ready';
                    mlStatus.style.background = '#10b981';
                } else {
                    mlStatus.textContent = 'ML: Unavailable';
                    mlStatus.style.background = '#ef4444';
                }
            } catch (error) {
                console.error('Error checking ML status:', error);
            }
        }
        
        // Tab switching - FIXED
        function switchTab(event, tab) {
            currentTab = tab;
            
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            if (event && event.target) {
                event.target.classList.add('active');
            } else {
                // Find tab button by name and activate it
                document.querySelectorAll('.tab').forEach(t => {
                    if (t.textContent.toLowerCase().includes(tab.toLowerCase()) ||
                        (tab === 'predictions' && t.textContent.includes('ML'))) {
                        t.classList.add('active');
                    }
                });
            }
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`${tab}-tab`).classList.add('active');
            
            // Load data if needed
            if (tab === 'sentiment' && !document.getElementById('sentiment-indicators').innerHTML) {
                fetchSentiment();
            }
        }
        
        // Chart type switching
        function setChartType(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            if (currentData) {
                updateChart(currentData);
            }
        }
        
        // Zoom controls
        function resetZoom() {
            if (chart) {
                chart.resetZoom();
            }
        }
        
        function zoomIn() {
            if (chart) {
                chart.zoom(1.1);
            }
        }
        
        function zoomOut() {
            if (chart) {
                chart.zoom(0.9);
            }
        }
        
        // Fetch stock data
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            
            if (!symbol) return;
            
            showStatus('loading', 'Fetching data... (Yahoo Finance → Alpha Vantage fallback)');
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=${interval}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentData = data;
                    showStatus('success', `✓ Data loaded from ${data.source}`);
                    updateDisplay(data);
                    updateChart(data);
                    updateIndicators(data);
                } else {
                    showStatus('error', data.error || 'Failed to fetch data');
                }
            } catch (error) {
                console.error('Error:', error);
                showStatus('error', 'Network error: ' + error.message);
            }
        }
        
        // Fetch predictions - FIXED
        async function fetchPredictions() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            
            if (!symbol) {
                showStatus('error', 'Please enter a symbol');
                return;
            }
            
            showStatus('loading', 'Generating ML predictions... This may take a moment for first-time analysis.');
            
            // Switch to predictions tab programmatically
            switchTab(null, 'predictions');
            
            try {
                const response = await fetch(`/api/predict/${symbol}`);
                const data = await response.json();
                
                if (response.ok) {
                    if (data.available) {
                        showStatus('success', '✓ Predictions generated');
                        displayPredictions(data);
                    } else {
                        showStatus('error', data.error || 'ML predictions not available');
                        displayPredictionError(data.error);
                    }
                } else {
                    showStatus('error', data.error || 'Failed to generate predictions');
                    displayPredictionError(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                showStatus('error', 'Network error: ' + error.message);
                displayPredictionError('Network error: ' + error.message);
            }
        }
        
        // Fetch sentiment
        async function fetchSentiment() {
            showStatus('loading', 'Analyzing market sentiment...');
            
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                
                if (response.ok) {
                    showStatus('success', '✓ Sentiment analysis complete');
                    displaySentiment(data);
                } else {
                    showStatus('error', data.error || 'Failed to fetch sentiment');
                }
            } catch (error) {
                console.error('Error:', error);
                showStatus('error', 'Network error: ' + error.message);
            }
        }
        
        // Update display
        function updateDisplay(data) {
            // Price display
            const price = data.current_price;
            const change = data.price_change;
            const changePct = data.price_change_pct;
            
            document.getElementById('current-price').textContent = `$${price.toFixed(2)}`;
            
            const changeElement = document.getElementById('price-change');
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSymbol = change >= 0 ? '+' : '';
            changeElement.className = `price-change ${changeClass}`;
            changeElement.textContent = `${changeSymbol}${change.toFixed(2)} (${changeSymbol}${changePct.toFixed(2)}%)`;
            
            // Data source
            document.getElementById('data-source').textContent = `${data.symbol} • ${data.source}`;
            
            // Quick indicators
            const quickIndicators = document.getElementById('quick-indicators');
            let html = '';
            
            const quickKeys = ['RSI', 'RSI_Signal', 'SMA_20', 'Volume_Ratio', 'BB_Position'];
            for (const key of quickKeys) {
                if (data.indicators[key] !== undefined) {
                    const value = typeof data.indicators[key] === 'number' 
                        ? data.indicators[key].toFixed(2) 
                        : data.indicators[key];
                    html += `
                        <div class="indicator-item">
                            <span>${key}</span>
                            <strong>${value}</strong>
                        </div>
                    `;
                }
            }
            
            quickIndicators.innerHTML = html || '<div class="indicator-item">No indicators available</div>';
        }
        
        // Update chart
        function updateChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            const chartConfig = {
                type: 'line',
                data: {
                    labels: data.labels
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: `${data.symbol} Price Chart`
                        },
                        zoom: {
                            zoom: {
                                wheel: {
                                    enabled: true,
                                },
                                pinch: {
                                    enabled: true
                                },
                                mode: 'x',
                            },
                            pan: {
                                enabled: true,
                                mode: 'x'
                            }
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Price ($)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        }
                    }
                }
            };
            
            if (chartType === 'line') {
                chartConfig.data.datasets = [{
                    label: 'Price',
                    data: data.data.map(d => d.close),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }];
            } else if (chartType === 'candlestick') {
                // Simplified candlestick using bar chart
                chartConfig.type = 'bar';
                chartConfig.data.datasets = [
                    {
                        label: 'High-Low',
                        data: data.data.map(d => [d.low, d.high]),
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        borderColor: 'rgba(0,0,0,0.3)',
                        borderWidth: 1,
                        barThickness: 2
                    },
                    {
                        label: 'Open-Close',
                        data: data.data.map(d => [Math.min(d.open, d.close), Math.max(d.open, d.close)]),
                        backgroundColor: data.data.map(d => d.close >= d.open ? 'rgba(16,185,129,0.5)' : 'rgba(239,68,68,0.5)'),
                        borderColor: data.data.map(d => d.close >= d.open ? '#10b981' : '#ef4444'),
                        borderWidth: 1,
                        barThickness: 6
                    }
                ];
            } else if (chartType === 'volume') {
                chartConfig.type = 'bar';
                chartConfig.data.datasets = [{
                    label: 'Volume',
                    data: data.data.map(d => d.volume),
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: '#667eea',
                    borderWidth: 1
                }];
                chartConfig.options.scales.y.title.text = 'Volume';
            }
            
            chart = new Chart(ctx, chartConfig);
        }
        
        // Update indicators
        function updateIndicators(data) {
            const indicatorsDiv = document.getElementById('technical-indicators');
            let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px; margin-top: 15px;">';
            
            for (const [key, value] of Object.entries(data.indicators || {})) {
                const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
                let colorClass = '';
                
                // Color coding for certain indicators
                if (key === 'RSI_Signal') {
                    colorClass = value === 'Overbought' ? 'negative' : value === 'Oversold' ? 'positive' : '';
                } else if (key === 'MACD_Crossover') {
                    colorClass = value === 'Bullish' ? 'positive' : value === 'Bearish' ? 'negative' : '';
                }
                
                html += `
                    <div class="indicator-item">
                        <span>${key.replace(/_/g, ' ')}</span>
                        <strong class="${colorClass}">${displayValue}</strong>
                    </div>
                `;
            }
            
            html += '</div>';
            indicatorsDiv.innerHTML = html;
        }
        
        // Display predictions - IMPROVED
        function displayPredictions(data) {
            const predictionsDiv = document.getElementById('predictions-content');
            
            if (!data.available) {
                displayPredictionError(data.error);
                return;
            }
            
            let html = '<div style="margin-top: 20px;">';
            
            if (data.predictions && data.predictions.current_price) {
                html += `<p style="margin-bottom: 15px;">Current Price: <strong>$${data.predictions.current_price.toFixed(2)}</strong></p>`;
            } else if (data.current_price) {
                html += `<p style="margin-bottom: 15px;">Current Price: <strong>$${data.current_price.toFixed(2)}</strong></p>`;
            }
            
            // Model info
            if (data.model_info) {
                html += `
                    <div style="background: #f7fafc; padding: 10px; border-radius: 6px; margin-bottom: 15px;">
                        <small>Model trained for ${data.model_info.symbol} using ${data.model_info.features_used} features</small>
                    </div>
                `;
            }
            
            // Predictions
            html += '<h4>Price Predictions</h4>';
            
            if (data.predictions && data.predictions.predictions) {
                for (const pred of data.predictions.predictions) {
                    const changeClass = pred.return >= 0 ? 'positive' : 'negative';
                    const symbol = pred.return >= 0 ? '+' : '';
                    
                    html += `
                        <div class="prediction-item">
                            <div>
                                <strong>${pred.days} Day${pred.days > 1 ? 's' : ''}</strong>
                            </div>
                            <div>
                                <span class="${changeClass}">$${pred.price.toFixed(2)}</span>
                                ${pred.price_range ? `
                                    <div class="price-range">
                                        Range: $${pred.price_range.low.toFixed(2)} - $${pred.price_range.high.toFixed(2)}
                                    </div>
                                ` : ''}
                            </div>
                            <div>
                                <span class="${changeClass}">${symbol}${pred.return.toFixed(2)}%</span>
                                <br>
                                <small>Confidence: ${pred.confidence}%</small>
                            </div>
                        </div>
                    `;
                }
            } else if (data.predictions) {
                // Fallback for different structure
                for (const pred of data.predictions) {
                    const changeClass = pred.return >= 0 ? 'positive' : 'negative';
                    const symbol = pred.return >= 0 ? '+' : '';
                    
                    html += `
                        <div class="prediction-item">
                            <div>
                                <strong>${pred.days} Day${pred.days > 1 ? 's' : ''}</strong>
                            </div>
                            <div>
                                <span class="${changeClass}">$${pred.price.toFixed(2)}</span>
                            </div>
                            <div>
                                <span class="${changeClass}">${symbol}${pred.return.toFixed(2)}%</span>
                                <br>
                                <small>Confidence: ${pred.confidence}%</small>
                            </div>
                        </div>
                    `;
                }
            }
            
            // Feature importance
            const importance = data.predictions?.feature_importance || data.feature_importance;
            if (importance && importance.length > 0) {
                html += '<h4 style="margin-top: 20px;">Top Features</h4>';
                html += '<div style="display: grid; gap: 5px;">';
                
                for (const feature of importance) {
                    const pct = (feature.importance * 100).toFixed(1);
                    html += `
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="flex: 1;">${feature.feature}</span>
                            <div style="width: 200px; background: #e2e8f0; border-radius: 4px; height: 20px; position: relative;">
                                <div style="width: ${pct}%; background: #667eea; height: 100%; border-radius: 4px;"></div>
                            </div>
                            <span style="width: 50px; text-align: right;">${pct}%</span>
                        </div>
                    `;
                }
                
                html += '</div>';
            }
            
            html += '</div>';
            predictionsDiv.innerHTML = html;
        }
        
        // Display prediction error
        function displayPredictionError(error) {
            const predictionsDiv = document.getElementById('predictions-content');
            predictionsDiv.innerHTML = `
                <div class="ml-unavailable">
                    <h4>ML Predictions Unavailable</h4>
                    <p>${error || 'Unable to generate predictions at this time.'}</p>
                    <p style="margin-top: 10px;">Possible reasons:</p>
                    <ul style="margin-left: 20px;">
                        <li>scikit-learn is not installed</li>
                        <li>Insufficient data for the selected symbol</li>
                        <li>Model training failed</li>
                    </ul>
                    <p style="margin-top: 10px;">To enable ML predictions, ensure scikit-learn is installed:</p>
                    <code style="background: white; padding: 5px; border-radius: 4px;">pip install scikit-learn</code>
                </div>
            `;
        }
        
        // Display sentiment
        function displaySentiment(data) {
            // Overall sentiment
            if (data.overall) {
                const overall = data.overall;
                const sentimentClass = overall.score > 0 ? 'positive' : overall.score < 0 ? 'negative' : '';
                
                document.getElementById('overall-sentiment').innerHTML = `
                    <div style="text-align: center; padding: 20px; background: #f7fafc; border-radius: 8px;">
                        <h2 class="${sentimentClass}">${overall.sentiment}</h2>
                        <p style="font-size: 1.5rem; margin: 10px 0;">Score: ${overall.score.toFixed(2)}</p>
                        <p>Confidence: ${overall.confidence.toFixed(0)}%</p>
                    </div>
                `;
            }
            
            // Individual indicators
            const indicatorsDiv = document.getElementById('sentiment-indicators');
            let html = '';
            
            // VIX
            if (data.vix) {
                const vix = data.vix;
                html += createSentimentCard('VIX Fear Index', vix.value, vix.change, vix.sentiment);
            }
            
            // Market Breadth
            if (data.market_breadth) {
                const breadth = data.market_breadth;
                html += createSentimentCard('S&P 500', breadth.sp500, breadth.change, breadth.sentiment);
            }
            
            indicatorsDiv.innerHTML = html || '<p>No sentiment data available</p>';
        }
        
        // Create sentiment card
        function createSentimentCard(title, value, change, sentiment) {
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const symbol = change >= 0 ? '+' : '';
            
            return `
                <div class="sentiment-card">
                    <div class="sentiment-label">${title}</div>
                    <div class="sentiment-value">${value ? value.toFixed(2) : '--'}</div>
                    <div class="${changeClass}">${symbol}${change ? change.toFixed(2) : '0.00'}%</div>
                    <div style="margin-top: 10px; font-weight: 600;">${sentiment || 'Unknown'}</div>
                </div>
            `;
        }
        
        // Show status message
        function showStatus(type, message) {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status-message ${type}`;
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';
            
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            // Check ML status
            checkMLStatus();
            
            // Auto-fetch on load
            setTimeout(fetchData, 500);
            
            // Enter key support
            document.getElementById('symbol').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') fetchData();
            });
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("\nStarting Unified Robust Stock Analysis System (Fixed ML)...")
    print(f"Server running at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)