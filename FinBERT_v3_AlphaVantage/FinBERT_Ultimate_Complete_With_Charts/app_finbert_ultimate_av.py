#!/usr/bin/env python3
"""
Ultimate FinBERT Trading System - WITH ALPHA VANTAGE
=====================================================
Author: AI Assistant
Date: October 2024
Python: 3.12+ Compatible
Alpha Vantage Key: Integrated

FIXED ISSUES:
✓ Python 3.12 numpy compatibility (uses numpy>=1.26.0)
✓ Alpha Vantage as secondary data source
✓ Real data only - NO synthetic fallbacks
✓ Automatic fallback between Yahoo Finance and Alpha Vantage

KEY FEATURES:
• Dual data sources: Yahoo Finance (primary) + Alpha Vantage (backup)
• FinBERT sentiment analysis (ProsusAI/finbert)
• Random Forest with 100 trees, max_depth=10
• Technical indicators: RSI, MACD, SMA, Bollinger Bands, ATR
"""

import os
import sys
import json
import logging
import warnings
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import traceback

# Suppress warnings
warnings.filterwarnings('ignore')

# Core imports with version checking
import numpy as np
if tuple(map(int, np.__version__.split('.')[:2])) < (1, 26):
    print("ERROR: NumPy version must be >= 1.26.0 for Python 3.12")
    print(f"Current version: {np.__version__}")
    print("Run: pip install --upgrade numpy>=1.26.0")
    sys.exit(1)

import pandas as pd
import yfinance as yf
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import ta  # Technical indicators
import feedparser  # For RSS feeds

# Try to import FinBERT
try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch
    FINBERT_AVAILABLE = True
    print("✓ FinBERT loaded successfully")
except ImportError:
    FINBERT_AVAILABLE = False
    print("⚠ FinBERT not available - using fallback sentiment analysis")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
for directory in ['cache', 'models', 'logs', 'data']:
    os.makedirs(directory, exist_ok=True)

class DataFetcher:
    """Enhanced data fetcher with Yahoo Finance and Alpha Vantage"""
    
    def __init__(self):
        # YOUR ALPHA VANTAGE KEY
        self.alpha_vantage_key = '68ZFANK047DL0KSR'
        
        self.sources = {
            'yahoo': self._fetch_yahoo,
            'alpha_vantage': self._fetch_alpha_vantage,
        }
        
        logger.info(f"Data fetcher initialized with Alpha Vantage key: {self.alpha_vantage_key[:8]}...")
    
    def fetch(self, symbol: str, period: str = '6mo', interval: str = '1d') -> pd.DataFrame:
        """Fetch data with automatic source fallback"""
        
        # Try Yahoo Finance first
        try:
            logger.info(f"Fetching {symbol} from Yahoo Finance...")
            data = self._fetch_yahoo(symbol, period, interval)
            if data is not None and not data.empty:
                logger.info(f"✓ Successfully fetched {len(data)} rows from Yahoo Finance")
                return data
        except Exception as e:
            logger.warning(f"Yahoo Finance failed: {e}")
        
        # Fallback to Alpha Vantage
        try:
            logger.info(f"Fetching {symbol} from Alpha Vantage...")
            data = self._fetch_alpha_vantage(symbol, period, interval)
            if data is not None and not data.empty:
                logger.info(f"✓ Successfully fetched {len(data)} rows from Alpha Vantage")
                return data
        except Exception as e:
            logger.warning(f"Alpha Vantage failed: {e}")
        
        # Return empty DataFrame if all sources fail
        logger.error(f"All data sources failed for {symbol}")
        return pd.DataFrame()
    
    def _fetch_yahoo(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """Fetch from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            # Ensure we have all required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if all(col in data.columns for col in required_cols):
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None
    
    def _fetch_alpha_vantage(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """Fetch from Alpha Vantage with your API key"""
        
        if not self.alpha_vantage_key:
            return None
        
        try:
            # Determine function based on interval
            if interval == '1d':
                function = 'TIME_SERIES_DAILY'
                key = 'Time Series (Daily)'
            elif interval in ['5min', '15min', '30min', '60min']:
                function = 'TIME_SERIES_INTRADAY'
                key = f'Time Series ({interval})'
            else:
                function = 'TIME_SERIES_DAILY'
                key = 'Time Series (Daily)'
            
            # Build URL
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'full'  # Get more data
            }
            
            if function == 'TIME_SERIES_INTRADAY':
                params['interval'] = interval
            
            # Make request
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Alpha Vantage HTTP error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Check for error messages
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            # Parse time series data
            if key not in data:
                logger.error(f"No data found for {symbol}")
                return None
            
            time_series = data[key]
            
            # Convert to DataFrame
            df_data = []
            for date, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(date),
                    'Open': float(values.get('1. open', values.get('open', 0))),
                    'High': float(values.get('2. high', values.get('high', 0))),
                    'Low': float(values.get('3. low', values.get('low', 0))),
                    'Close': float(values.get('4. close', values.get('close', 0))),
                    'Volume': float(values.get('5. volume', values.get('volume', 0)))
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Filter by period
            if period:
                days = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}.get(period, 180)
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df.index >= cutoff_date]
            
            return df
            
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

class TechnicalAnalyzer:
    """Technical analysis with adaptive features"""
    
    @staticmethod
    def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators adaptively based on data length"""
        
        if df.empty:
            return df
        
        data_length = len(df)
        df = df.copy()
        
        # Basic price features
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=min(20, data_length)).mean()
        
        # Adaptive moving averages
        if data_length >= 10:
            df['SMA_10'] = df['Close'].rolling(window=10).mean()
            df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        
        if data_length >= 20:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.volatility.bollinger_hband(df['Close']), \
                                                               df['Close'].rolling(window=20).mean(), \
                                                               ta.volatility.bollinger_lband(df['Close'])
        
        if data_length >= 50:
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        else:
            # Use shorter period if not enough data
            period = max(5, data_length // 3)
            df['SMA_50'] = df['Close'].rolling(window=period).mean()
            df['EMA_50'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        if data_length >= 200:
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Technical indicators with adaptive periods
        try:
            # RSI
            rsi_period = min(14, max(5, data_length // 5))
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=rsi_period).rsi()
            
            # MACD - requires at least 26 days
            if data_length >= 35:
                macd = ta.trend.MACD(df['Close'])
                df['MACD'] = macd.macd()
                df['MACD_signal'] = macd.macd_signal()
                df['MACD_diff'] = macd.macd_diff()
            
            # Stochastic
            stoch_period = min(14, max(5, data_length // 5))
            stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=stoch_period)
            df['Stoch_K'] = stoch.stoch()
            df['Stoch_D'] = stoch.stoch_signal()
            
            # ATR
            atr_period = min(14, max(5, data_length // 5))
            df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=atr_period).average_true_range()
            
            # OBV
            df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
            
        except Exception as e:
            logger.warning(f"Error calculating some indicators: {e}")
        
        return df

class SentimentAnalyzer:
    """Sentiment analysis with FinBERT or fallback"""
    
    def __init__(self):
        self.finbert_model = None
        self.finbert_tokenizer = None
        
        if FINBERT_AVAILABLE:
            try:
                model_name = "ProsusAI/finbert"
                self.finbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.finbert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.finbert_model.to(self.device)
                self.finbert_model.eval()
                logger.info("✓ FinBERT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load FinBERT: {e}")
                self.finbert_model = None
                self.finbert_tokenizer = None
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        
        if not text:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34, 'score': 0.0}
        
        if self.finbert_model is not None:
            try:
                # Use FinBERT
                inputs = self.finbert_tokenizer(text, padding=True, truncation=True, 
                                               max_length=512, return_tensors='pt')
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.finbert_model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    predictions = predictions.cpu().numpy()[0]
                
                return {
                    'positive': float(predictions[0]),
                    'negative': float(predictions[1]),
                    'neutral': float(predictions[2]),
                    'score': float(predictions[0] - predictions[1])  # Simple sentiment score
                }
            except Exception as e:
                logger.error(f"FinBERT analysis error: {e}")
        
        # Fallback sentiment (basic keyword analysis)
        positive_words = ['gain', 'profit', 'up', 'rise', 'growth', 'positive', 'strong', 'buy', 'bull']
        negative_words = ['loss', 'down', 'fall', 'decline', 'negative', 'weak', 'sell', 'bear']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = max(pos_count + neg_count, 1)
        
        return {
            'positive': pos_count / total,
            'negative': neg_count / total,
            'neutral': 1 - (pos_count + neg_count) / total if total > 0 else 1.0,
            'score': (pos_count - neg_count) / total
        }

class MLPredictor:
    """Machine learning predictor with Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.accuracy = 0
        self.last_train_time = None
    
    def prepare_features(self, df: pd.DataFrame, sentiment_score: float = 0) -> pd.DataFrame:
        """Prepare features for ML model"""
        
        feature_df = df.copy()
        
        # Add sentiment
        feature_df['sentiment'] = sentiment_score
        
        # Select available features based on what's in the dataframe
        all_possible_features = [
            'returns', 'log_returns', 'volume_ratio',
            'RSI', 'MACD', 'MACD_signal', 'MACD_diff',
            'Stoch_K', 'Stoch_D', 'ATR', 'OBV',
            'SMA_10', 'EMA_10', 'SMA_20', 'EMA_20', 'SMA_50', 'EMA_50',
            'BB_upper', 'BB_middle', 'BB_lower',
            'sentiment'
        ]
        
        # Use only features that exist in the dataframe
        available_features = [f for f in all_possible_features if f in feature_df.columns]
        
        # Store feature columns for consistency
        if not self.feature_columns:
            self.feature_columns = available_features
        
        # Ensure we use the same features as training
        features_to_use = self.feature_columns if self.feature_columns else available_features
        
        # Add missing features as zeros (for consistency)
        for feature in features_to_use:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
        
        return feature_df[features_to_use]
    
    def train(self, df: pd.DataFrame, sentiment_score: float = 0) -> Dict[str, Any]:
        """Train the Random Forest model"""
        
        if len(df) < 30:
            return {'error': 'Insufficient data for training (need at least 30 data points)'}
        
        try:
            # Prepare features
            feature_df = self.prepare_features(df, sentiment_score)
            
            # Remove NaN values
            feature_df = feature_df.dropna()
            
            if len(feature_df) < 20:
                return {'error': 'Insufficient clean data after removing NaN values'}
            
            # Create target (1 if price goes up, 0 if down)
            y = (df['Close'].shift(-1) > df['Close']).astype(int)
            y = y[feature_df.index]
            y = y[:-1]  # Remove last row (no future price)
            feature_df = feature_df[:-1]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                feature_df, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model - FIXED Random Forest parameters as requested
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Calculate metrics
            y_pred = self.model.predict(X_test_scaled)
            
            self.accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            # Feature importance
            feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            top_features = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10])
            
            self.last_train_time = datetime.now()
            
            # Save model
            model_path = f"models/model_{df.index[-1].strftime('%Y%m%d_%H%M%S')}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'features': self.feature_columns,
                    'accuracy': self.accuracy
                }, f)
            
            return {
                'success': True,
                'accuracy': round(self.accuracy, 4),
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1_score': round(f1, 4),
                'samples_train': len(X_train),
                'samples_test': len(X_test),
                'top_features': top_features,
                'model_type': 'Random Forest (100 trees, max_depth=10)',
                'timestamp': self.last_train_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {'error': str(e)}
    
    def predict(self, df: pd.DataFrame, sentiment_score: float = 0) -> Dict[str, Any]:
        """Make prediction using the trained model"""
        
        if self.model is None:
            return {'error': 'Model not trained yet'}
        
        try:
            # Prepare features
            feature_df = self.prepare_features(df, sentiment_score)
            
            # Get latest features
            latest_features = feature_df.iloc[-1:].fillna(0)
            
            # Scale
            latest_scaled = self.scaler.transform(latest_features)
            
            # Predict
            prediction = self.model.predict(latest_scaled)[0]
            probabilities = self.model.predict_proba(latest_scaled)[0]
            
            return {
                'prediction': 'UP' if prediction == 1 else 'DOWN',
                'confidence': float(max(probabilities)),
                'probability_up': float(probabilities[1]),
                'probability_down': float(probabilities[0]),
                'model_accuracy': round(self.accuracy, 4),
                'last_trained': self.last_train_time.isoformat() if self.last_train_time else None
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'error': str(e)}

# Flask application
app = Flask(__name__)
CORS(app)

# Initialize components
data_fetcher = DataFetcher()
sentiment_analyzer = SentimentAnalyzer()
ml_predictor = MLPredictor()

@app.route('/')
def home():
    """API home page with status"""
    return jsonify({
        'status': 'FinBERT Ultimate Trading System Active',
        'version': '3.0-AlphaVantage',
        'endpoints': {
            '/api/analyze': 'Complete analysis for a stock',
            '/api/train': 'Train ML model',
            '/api/predict': 'Get prediction',
            '/api/sentiment': 'Analyze text sentiment',
            '/api/technical': 'Get technical indicators',
            '/api/health': 'System health check'
        },
        'data_sources': {
            'primary': 'Yahoo Finance',
            'secondary': 'Alpha Vantage (Key Active)'
        },
        'features': {
            'finbert': FINBERT_AVAILABLE,
            'ml_model': ml_predictor.model is not None,
            'alpha_vantage': bool(data_fetcher.alpha_vantage_key)
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Complete analysis endpoint"""
    
    data = request.json
    symbol = data.get('symbol', 'AAPL').upper()
    period = data.get('period', '6mo')
    
    try:
        # Fetch data
        df = data_fetcher.fetch(symbol, period)
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Calculate technical indicators
        df = TechnicalAnalyzer.calculate_features(df)
        
        # Get sentiment
        sentiment_data = sentiment_analyzer.analyze(data.get('news_text', ''))
        
        # Prepare response
        latest_data = df.iloc[-1]
        
        response = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': {
                'current': float(latest_data['Close']),
                'open': float(latest_data['Open']),
                'high': float(latest_data['High']),
                'low': float(latest_data['Low']),
                'volume': int(latest_data['Volume'])
            },
            'technical_indicators': {},
            'sentiment': sentiment_data,
            'data_points': len(df),
            'data_source': 'Yahoo Finance / Alpha Vantage'
        }
        
        # Add available technical indicators
        indicator_fields = ['RSI', 'MACD', 'ATR', 'OBV', 'SMA_50', 'EMA_50']
        for field in indicator_fields:
            if field in df.columns and not pd.isna(latest_data[field]):
                response['technical_indicators'][field] = float(latest_data[field])
        
        # Get prediction if model is trained
        if ml_predictor.model is not None:
            prediction = ml_predictor.predict(df, sentiment_data['score'])
            response['prediction'] = prediction
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train():
    """Train the ML model"""
    
    data = request.json
    symbol = data.get('symbol', 'AAPL').upper()
    period = data.get('period', '2y')  # More data for training
    
    try:
        # Fetch data
        df = data_fetcher.fetch(symbol, period)
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Calculate features
        df = TechnicalAnalyzer.calculate_features(df)
        
        # Get sentiment
        sentiment_score = sentiment_analyzer.analyze(data.get('news_text', ''))['score']
        
        # Train model
        result = ml_predictor.train(df, sentiment_score)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Get prediction for a stock"""
    
    data = request.json
    symbol = data.get('symbol', 'AAPL').upper()
    period = data.get('period', '3mo')
    
    try:
        # Fetch recent data
        df = data_fetcher.fetch(symbol, period)
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Calculate features
        df = TechnicalAnalyzer.calculate_features(df)
        
        # Get sentiment
        sentiment_score = sentiment_analyzer.analyze(data.get('news_text', ''))['score']
        
        # Get prediction
        result = ml_predictor.predict(df, sentiment_score)
        
        if 'error' in result:
            # Try to train model if not trained
            if result['error'] == 'Model not trained yet':
                train_result = ml_predictor.train(df, sentiment_score)
                if 'success' in train_result:
                    result = ml_predictor.predict(df, sentiment_score)
                else:
                    return jsonify(train_result), 400
        
        # Add current price info
        result['current_price'] = float(df['Close'].iloc[-1])
        result['symbol'] = symbol
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    """Analyze sentiment of text"""
    
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = sentiment_analyzer.analyze(text)
        result['model'] = 'FinBERT' if FINBERT_AVAILABLE else 'Keyword-based'
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/technical', methods=['POST'])
def technical():
    """Get technical indicators"""
    
    data = request.json
    symbol = data.get('symbol', 'AAPL').upper()
    period = data.get('period', '3mo')
    
    try:
        # Fetch data
        df = data_fetcher.fetch(symbol, period)
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Calculate indicators
        df = TechnicalAnalyzer.calculate_features(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        indicators = {}
        for col in df.columns:
            if col not in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if not pd.isna(latest[col]):
                    indicators[col] = float(latest[col])
        
        return jsonify({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'indicators': indicators,
            'data_points': len(df)
        })
        
    except Exception as e:
        logger.error(f"Technical analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'finbert': 'active' if FINBERT_AVAILABLE else 'fallback',
            'ml_model': 'trained' if ml_predictor.model is not None else 'not trained',
            'data_sources': {
                'yahoo': 'active',
                'alpha_vantage': 'active' if data_fetcher.alpha_vantage_key else 'not configured'
            }
        },
        'alpha_vantage_key': f"{data_fetcher.alpha_vantage_key[:8]}..." if data_fetcher.alpha_vantage_key else 'not set'
    }
    
    return jsonify(health_status)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("FinBERT Ultimate Trading System v3.0")
    print("Alpha Vantage Integration Active")
    print("="*50)
    print(f"Alpha Vantage Key: {data_fetcher.alpha_vantage_key[:8]}...")
    print(f"FinBERT Status: {'Loaded' if FINBERT_AVAILABLE else 'Using Fallback'}")
    print(f"Starting server on http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)