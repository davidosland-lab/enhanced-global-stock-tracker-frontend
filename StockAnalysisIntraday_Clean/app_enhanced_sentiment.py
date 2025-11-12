#!/usr/bin/env python3
"""
Stock Analysis System with Enhanced Sentiment & Macro Indicators - Phase 1
Adds VIX (fear gauge), market breadth, bond yields, and dollar strength
"""

import yfinance as yf
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import traceback
import sys
import os
import threading
import time
from functools import lru_cache

warnings.filterwarnings('ignore')

# Flask app setup
app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"

# Australian stock list
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW', 
                     'RIO', 'FMG', 'TCL', 'ALL', 'REA', 'GMG', 'AMC', 'SUN', 'QBE', 'IAG']

# Intraday interval mappings
INTRADAY_INTERVALS = {
    '1m': {'yahoo': '1m', 'display': '1 Minute', 'max_period': '7d'},
    '2m': {'yahoo': '2m', 'display': '2 Minutes', 'max_period': '60d'},
    '5m': {'yahoo': '5m', 'display': '5 Minutes', 'max_period': '60d'},
    '15m': {'yahoo': '15m', 'display': '15 Minutes', 'max_period': '60d'},
    '30m': {'yahoo': '30m', 'display': '30 Minutes', 'max_period': '60d'},
    '60m': {'yahoo': '60m', 'display': '1 Hour', 'max_period': '730d'},
    '90m': {'yahoo': '90m', 'display': '90 Minutes', 'max_period': '60d'},
    '1h': {'yahoo': '1h', 'display': '1 Hour', 'max_period': '730d'},
    '1d': {'yahoo': '1d', 'display': '1 Day', 'max_period': 'max'},
    '5d': {'yahoo': '5d', 'display': '5 Days', 'max_period': 'max'},
    '1wk': {'yahoo': '1wk', 'display': '1 Week', 'max_period': 'max'},
    '1mo': {'yahoo': '1mo', 'display': '1 Month', 'max_period': 'max'}
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
                if yield_change > 0.1:
                    sentiment = "Risk-On (Rising Yields)"
                    score = 0.3
                elif yield_change < -0.1:
                    sentiment = "Risk-Off (Falling Yields)"
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
            return {'current': None, 'sentiment': 'Unknown', 'score': 0, 'description': 'Yield data unavailable'}
    
    def get_dollar_strength(self):
        """Get US Dollar Index as global risk indicator"""
        try:
            # DXY - US Dollar Index
            dxy = yf.Ticker("DX-Y.NYB")
            hist = dxy.history(period="5d")
            if not hist.empty:
                current_dxy = hist['Close'].iloc[-1]
                week_ago_dxy = hist['Close'].iloc[0] if len(hist) > 1 else current_dxy
                dxy_change = ((current_dxy - week_ago_dxy) / week_ago_dxy) * 100
                
                # Strong dollar = risk-off, weak = risk-on
                if dxy_change > 1:
                    sentiment = "Risk-Off (Dollar Strengthening)"
                    score = -0.3
                elif dxy_change < -1:
                    sentiment = "Risk-On (Dollar Weakening)"
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
            return {'value': None, 'sentiment': 'Unknown', 'score': 0, 'description': 'DXY data unavailable'}
    
    def get_sector_rotation(self):
        """Analyze sector performance for rotation insights"""
        try:
            # Key sector ETFs
            sectors = {
                'XLK': 'Technology',
                'XLF': 'Financials',
                'XLE': 'Energy',
                'XLV': 'Healthcare',
                'XLI': 'Industrials',
                'XLY': 'Consumer Discretionary',
                'XLP': 'Consumer Staples',
                'XLRE': 'Real Estate',
                'XLU': 'Utilities'
            }
            
            performances = {}
            for symbol, name in sectors.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    perf = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    performances[name] = perf
            
            # Sort by performance
            sorted_sectors = sorted(performances.items(), key=lambda x: x[1], reverse=True)
            
            # Analyze rotation
            top_sectors = sorted_sectors[:3]
            bottom_sectors = sorted_sectors[-3:]
            
            # Risk-on vs Risk-off sectors
            risk_on = ['Technology', 'Consumer Discretionary', 'Financials']
            risk_off = ['Utilities', 'Consumer Staples', 'Healthcare']
            
            risk_on_avg = np.mean([performances.get(s, 0) for s in risk_on])
            risk_off_avg = np.mean([performances.get(s, 0) for s in risk_off])
            
            if risk_on_avg > risk_off_avg + 1:
                sentiment = "Risk-On Rotation"
                score = 0.4
            elif risk_off_avg > risk_on_avg + 1:
                sentiment = "Risk-Off Rotation"
                score = -0.4
            else:
                sentiment = "Mixed Rotation"
                score = 0
                
            return {
                'top_performers': top_sectors,
                'bottom_performers': bottom_sectors,
                'sentiment': sentiment,
                'score': score,
                'risk_on_avg': risk_on_avg,
                'risk_off_avg': risk_off_avg,
                'description': f"Top: {top_sectors[0][0]} ({top_sectors[0][1]:+.2f}%)"
            }
        except Exception as e:
            print(f"Error analyzing sectors: {e}")
            return {'sentiment': 'Unknown', 'score': 0, 'description': 'Sector data unavailable'}
    
    def get_combined_sentiment(self):
        """Combine all sentiment indicators into overall score"""
        vix = self.get_vix_fear_gauge()
        breadth = self.get_market_breadth()
        yields = self.get_bond_yields()
        dollar = self.get_dollar_strength()
        sectors = self.get_sector_rotation()
        
        # Weighted average of scores
        weights = {
            'vix': 0.35,      # Most important - direct fear measure
            'breadth': 0.20,  # Market participation
            'yields': 0.15,   # Risk sentiment
            'dollar': 0.15,   # Global risk
            'sectors': 0.15   # Rotation patterns
        }
        
        combined_score = (
            vix['score'] * weights['vix'] +
            breadth['score'] * weights['breadth'] +
            yields['score'] * weights['yields'] +
            dollar['score'] * weights['dollar'] +
            sectors['score'] * weights['sectors']
        )
        
        # Determine overall sentiment
        if combined_score > 0.5:
            overall = "Strong Bullish"
        elif combined_score > 0.2:
            overall = "Bullish"
        elif combined_score > -0.2:
            overall = "Neutral"
        elif combined_score > -0.5:
            overall = "Bearish"
        else:
            overall = "Strong Bearish"
            
        return {
            'score': combined_score,
            'sentiment': overall,
            'components': {
                'vix': vix,
                'market_breadth': breadth,
                'bond_yields': yields,
                'dollar_index': dollar,
                'sector_rotation': sectors
            },
            'timestamp': datetime.now().isoformat()
        }

class EnhancedMLPredictor:
    """Enhanced ML predictor with sentiment indicators"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=150,  # Increased for more features
            max_depth=7,       # Slightly deeper for complex patterns
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.is_trained = False
        self.feature_importance = None
    
    def prepare_features(self, df, include_sentiment=True):
        """Prepare features including technical and sentiment indicators"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['volatility'] = features['returns'].rolling(20).std()
        
        # Moving averages
        features['sma_5'] = df['Close'].rolling(5).mean()
        features['sma_20'] = df['Close'].rolling(20).mean()
        features['sma_50'] = df['Close'].rolling(50).mean()
        features['sma_ratio_5_20'] = features['sma_5'] / features['sma_20']
        features['sma_ratio_20_50'] = features['sma_20'] / features['sma_50']
        
        # Price relative to moving averages
        features['price_to_sma5'] = df['Close'] / features['sma_5']
        features['price_to_sma20'] = df['Close'] / features['sma_20']
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        features['macd'] = ema12 - ema26
        features['macd_signal'] = features['macd'].ewm(span=9).mean()
        features['macd_diff'] = features['macd'] - features['macd_signal']
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        sma = df['Close'].rolling(bb_period).mean()
        std = df['Close'].rolling(bb_period).std()
        features['bb_upper'] = sma + (bb_std * std)
        features['bb_lower'] = sma - (bb_std * std)
        features['bb_position'] = (df['Close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'] + 1e-10)
        
        # Volume features
        if 'Volume' in df.columns and df['Volume'].sum() > 0:
            features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            features['volume_trend'] = df['Volume'].rolling(5).mean() / df['Volume'].rolling(20).mean()
        else:
            features['volume_ratio'] = 1.0
            features['volume_trend'] = 1.0
        
        # Price position
        features['high_low_ratio'] = df['High'] / (df['Low'] + 1e-10)
        features['close_to_high'] = df['Close'] / (df['High'] + 1e-10)
        features['close_to_low'] = df['Close'] / (df['Low'] + 1e-10)
        
        # Add sentiment features if requested
        if include_sentiment:
            try:
                sentiment = self.sentiment_analyzer.get_combined_sentiment()
                
                # Add sentiment scores as features
                features['sentiment_overall'] = sentiment['score']
                features['vix_score'] = sentiment['components']['vix']['score']
                features['breadth_score'] = sentiment['components']['market_breadth']['score']
                features['yield_score'] = sentiment['components']['bond_yields']['score']
                features['dollar_score'] = sentiment['components']['dollar_index']['score']
                features['sector_score'] = sentiment['components']['sector_rotation']['score']
                
                # Add raw values where available
                if sentiment['components']['vix']['value']:
                    features['vix_level'] = sentiment['components']['vix']['value'] / 100  # Normalize
                if sentiment['components']['market_breadth']['ratio']:
                    features['breadth_ratio'] = sentiment['components']['market_breadth']['ratio']
                    
                print(f"Sentiment features added. Overall sentiment: {sentiment['sentiment']}")
            except Exception as e:
                print(f"Error adding sentiment features: {e}")
                # Add neutral values if sentiment fails
                features['sentiment_overall'] = 0
                features['vix_score'] = 0
                features['breadth_score'] = 0
                features['yield_score'] = 0
                features['dollar_score'] = 0
                features['sector_score'] = 0
        
        # Forward fill missing values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def train(self, df, include_sentiment=True):
        """Train the model with enhanced features"""
        if len(df) < 100:
            return False
        
        try:
            # Prepare features
            X = self.prepare_features(df, include_sentiment)
            
            # Prepare target (next period's return)
            y = df['Close'].shift(-1) / df['Close'] - 1
            
            # Remove last row (no target) and first rows (NaN features)
            valid_idx = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) < 50:
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Store feature importance
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Calculate accuracy
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            print(f"Model trained. Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            # Print top features
            print("\nTop 5 Important Features:")
            for idx, row in self.feature_importance.head(5).iterrows():
                print(f"  {row['feature']}: {row['importance']:.3f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            print(f"Training error: {e}")
            return False
    
    def predict(self, df, days=5, include_sentiment=True):
        """Make predictions with sentiment adjustment"""
        if not self.is_trained:
            return []
        
        try:
            predictions = []
            current_price = df['Close'].iloc[-1]
            
            # Get features for last row
            X = self.prepare_features(df, include_sentiment)
            X_last = X.iloc[-1:].fillna(0)
            X_scaled = self.scaler.transform(X_last)
            
            # Get sentiment for adjustment
            sentiment = self.sentiment_analyzer.get_combined_sentiment()
            sentiment_multiplier = 1 + (sentiment['score'] * 0.1)  # ±10% max adjustment
            
            # Predict next N days
            for i in range(days):
                # Predict return
                pred_return = self.model.predict(X_scaled)[0]
                
                # Apply sentiment adjustment
                adjusted_return = pred_return * sentiment_multiplier
                
                # Calculate price
                pred_price = current_price * (1 + adjusted_return)
                predictions.append(float(pred_price))
                
                # Update current price for next prediction
                current_price = pred_price
            
            return predictions
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return []

# Keep the rest of the classes the same
class UnifiedDataFetcher:
    """Unified data fetcher with Yahoo Finance and Alpha Vantage fallback"""
    
    def fetch_data(self, symbol, period='1mo', interval='1d'):
        """Fetch data with automatic source selection"""
        # Handle Australian stocks
        original_symbol = symbol
        if symbol.upper() in AUSTRALIAN_STOCKS:
            symbol = f"{symbol.upper()}.AX"
        
        # Try Yahoo Finance first
        df, source, current_price = self.fetch_yahoo(symbol, period, interval)
        
        # If Yahoo fails, try Alpha Vantage
        if df is None or df.empty:
            print(f"Yahoo failed for {symbol}, trying Alpha Vantage...")
            df, source, current_price = self.fetch_alpha_vantage(original_symbol)
        
        return df, source, current_price
    
    def fetch_yahoo(self, symbol, period='1mo', interval='1d'):
        """Fetch from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Map interval to Yahoo format
            yahoo_interval = interval
            if interval in INTRADAY_INTERVALS:
                yahoo_interval = INTRADAY_INTERVALS[interval]['yahoo']
            
            # Fetch data based on interval
            if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
                # For intraday, use appropriate period
                max_period = INTRADAY_INTERVALS[interval]['max_period']
                if period == 'max':
                    period = max_period
                hist = ticker.history(period=period, interval=yahoo_interval)
            else:
                # For daily and above
                hist = ticker.history(period=period)
            
            if hist.empty:
                return None, None, None
            
            # Get current price
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
            except:
                current_price = hist['Close'].iloc[-1]
            
            return hist, 'Yahoo Finance', float(current_price)
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None, None, None
    
    def fetch_alpha_vantage(self, symbol, outputsize='compact'):
        """Fetch from Alpha Vantage as fallback"""
        try:
            url = f'https://www.alphavantage.co/query'
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_API_KEY,
                'outputsize': outputsize
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                print(f"Alpha Vantage error: {data.get('Error Message', 'Unknown error')}")
                return None, None, None
            
            # Convert to DataFrame
            time_series = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match Yahoo format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df.astype(float)
            
            current_price = df['Close'].iloc[-1]
            
            return df, 'Alpha Vantage', float(current_price)
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return None, None, None

class TechnicalAnalyzer:
    """Technical analysis calculations"""
    
    def calculate_all(self, df):
        """Calculate all technical indicators"""
        indicators = {}
        
        try:
            # RSI
            indicators['rsi'] = self.calculate_rsi(df)
            
            # MACD
            indicators['macd'] = self.calculate_macd(df)
            
            # Bollinger Bands
            indicators['bollinger'] = self.calculate_bollinger(df)
            
            # Moving Averages
            indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
            indicators['sma_50'] = float(df['Close'].rolling(50).mean().iloc[-1])
            indicators['ema_12'] = float(df['Close'].ewm(span=12).mean().iloc[-1])
            indicators['ema_26'] = float(df['Close'].ewm(span=26).mean().iloc[-1])
            
            # Support and Resistance
            indicators['support'] = float(df['Low'].rolling(20).min().iloc[-1])
            indicators['resistance'] = float(df['High'].rolling(20).max().iloc[-1])
            
            # Average True Range (ATR)
            indicators['atr'] = self.calculate_atr(df)
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators
    
    def calculate_rsi(self, df, period=14):
        """Calculate RSI"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    
    def calculate_macd(self, df):
        """Calculate MACD"""
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        return {
            'macd': float(macd.iloc[-1]),
            'signal': float(signal.iloc[-1]),
            'histogram': float(macd.iloc[-1] - signal.iloc[-1])
        }
    
    def calculate_bollinger(self, df, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = df['Close'].rolling(period).mean()
        std = df['Close'].rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return {
            'upper': float(upper.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower.iloc[-1]),
            'width': float(upper.iloc[-1] - lower.iloc[-1])
        }
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()
        return float(atr.iloc[-1])

# Create global instances
data_fetcher = UnifiedDataFetcher()
ml_predictor = EnhancedMLPredictor()  # Using enhanced predictor
tech_analyzer = TechnicalAnalyzer()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with technical indicators and ML predictions"""
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
        sentiment = ml_predictor.sentiment_analyzer.get_combined_sentiment()
        
        # Train ML model and get predictions
        predictions = []
        if ml_predictor.train(df, include_sentiment=True):
            predictions = ml_predictor.predict(df, days=5, include_sentiment=True)
        
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
        
        response = {
            'symbol': symbol,
            'source': source,
            'period': period,
            'interval': interval,
            'current_price': current_price,
            'indicators': indicators,
            'predictions': predictions,
            'candlestick_data': candlestick_data,
            'sentiment': sentiment,
            'feature_importance': ml_predictor.feature_importance.to_dict('records') if ml_predictor.feature_importance is not None else []
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        traceback.print_exc()
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

# Continue with the HTML template in the next part...
@app.route('/favicon.ico')
def favicon():
    """Handle favicon request to prevent 404"""
    return '', 204

@app.route('/')
def home():
    """Serve the main HTML interface with sentiment dashboard"""
    return render_template_string(HTML_TEMPLATE)

# Enhanced HTML Template with Sentiment Dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis with Market Sentiment</title>
    <!-- WORKING VERSION IMPORTS WITH ZOOM -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <!-- ZOOM PLUGIN -->
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
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
            border-radius: 16px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        /* Sentiment Dashboard Styles */
        .sentiment-dashboard {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .sentiment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .sentiment-title {
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }
        
        .sentiment-score {
            font-size: 24px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 8px;
        }
        
        .sentiment-score.bullish {
            color: #10b981;
            background: rgba(16, 185, 129, 0.1);
        }
        
        .sentiment-score.bearish {
            color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }
        
        .sentiment-score.neutral {
            color: #6b7280;
            background: rgba(107, 114, 128, 0.1);
        }
        
        .sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .sentiment-indicator {
            background: #f9fafb;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #e5e7eb;
            transition: transform 0.2s;
        }
        
        .sentiment-indicator:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .indicator-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .indicator-value {
            font-size: 20px;
            font-weight: bold;
            color: #111827;
            margin-bottom: 4px;
        }
        
        .indicator-change {
            font-size: 14px;
        }
        
        .indicator-change.positive {
            color: #10b981;
        }
        
        .indicator-change.negative {
            color: #ef4444;
        }
        
        .indicator-description {
            font-size: 11px;
            color: #9ca3af;
            margin-top: 4px;
        }
        
        /* VIX Gauge Special Styling */
        .vix-gauge {
            background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
            border: none;
        }
        
        .vix-gauge.fear {
            background: linear-gradient(135deg, #fee2e2 0%, #ef4444 100%);
        }
        
        .vix-gauge.greed {
            background: linear-gradient(135deg, #d1fae5 0%, #10b981 100%);
        }
        
        /* Original styles continue */
        .controls {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .input-wrapper {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .input-wrapper label {
            font-size: 12px;
            color: #666;
            font-weight: 600;
        }
        
        input, select {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-height: 500px;
            position: relative;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .zoom-controls {
            display: flex;
            gap: 8px;
            margin-left: 20px;
            padding-left: 20px;
            border-left: 1px solid #e0e0e0;
        }
        
        .zoom-btn {
            width: 36px;
            height: 36px;
            background: #f0f2f5;
            color: #333;
            border: none;
            border-radius: 50%;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .zoom-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: #333;
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .error {
            background: #fee2e2;
            color: #dc2626;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .success {
            background: #d1fae5;
            color: #065f46;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .feature-importance {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .feature-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .feature-bar {
            height: 20px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis with Market Sentiment</h1>
            <p style="color: #666;">Enhanced with VIX, Market Breadth, Bond Yields & Sector Analysis</p>
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
                    <input type="text" id="symbol" placeholder="e.g., AAPL, MSFT" value="AAPL">
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
                        <option value="2y">2 Years</option>
                        <option value="5y">5 Years</option>
                        <option value="max">Max</option>
                    </select>
                </div>
                <div class="input-wrapper">
                    <label>Interval</label>
                    <select id="interval">
                        <option value="1m">1 Minute</option>
                        <option value="2m">2 Minutes</option>
                        <option value="5m">5 Minutes</option>
                        <option value="15m">15 Minutes</option>
                        <option value="30m">30 Minutes</option>
                        <option value="60m">1 Hour</option>
                        <option value="1d" selected>Daily</option>
                        <option value="1wk">Weekly</option>
                        <option value="1mo">Monthly</option>
                    </select>
                </div>
                <div class="input-wrapper">
                    <label>&nbsp;</label>
                    <button onclick="fetchStockData()">Get Analysis</button>
                </div>
                <div class="input-wrapper">
                    <label>&nbsp;</label>
                    <button onclick="refreshSentiment()">↻ Refresh Sentiment</button>
                </div>
            </div>
        </div>
        
        <!-- Chart -->
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title" id="chartTitle">Price Chart</div>
                <div class="chart-controls">
                    <button onclick="switchChartType('candlestick')">Candlestick</button>
                    <button onclick="switchChartType('line')">Line</button>
                    <div class="zoom-controls">
                        <button class="zoom-btn" onclick="zoomIn()">🔍+</button>
                        <button class="zoom-btn" onclick="zoomOut()">🔍-</button>
                        <button class="zoom-btn" onclick="resetZoom()">↺</button>
                    </div>
                </div>
            </div>
            <canvas id="priceChart"></canvas>
        </div>
        
        <!-- Content Grid -->
        <div class="content-grid">
            <div class="card">
                <h2>📊 Technical Indicators</h2>
                <div id="indicators" class="loading">Select a stock to view indicators</div>
            </div>
            
            <div class="card">
                <h2>🤖 ML Predictions (Sentiment-Enhanced)</h2>
                <div id="predictions" class="loading">Select a stock to view predictions</div>
            </div>
            
            <div class="card">
                <h2>📈 Feature Importance</h2>
                <div id="featureImportance" class="feature-importance loading">
                    Model will show important features after training
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let chartInstance = null;
        let currentData = null;
        let currentChartType = 'candlestick';
        
        // Load market sentiment on page load
        window.onload = function() {
            loadMarketSentiment();
            // Auto-refresh sentiment every 5 minutes
            setInterval(loadMarketSentiment, 300000);
        };
        
        async function loadMarketSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                const sentiment = await response.json();
                updateSentimentDashboard(sentiment);
            } catch (error) {
                console.error('Error loading sentiment:', error);
            }
        }
        
        function updateSentimentDashboard(sentiment) {
            // Update overall sentiment
            const overallElement = document.getElementById('overallSentiment');
            overallElement.textContent = sentiment.sentiment + ' (' + (sentiment.score > 0 ? '+' : '') + sentiment.score.toFixed(2) + ')';
            
            // Update color based on sentiment
            overallElement.className = 'sentiment-score';
            if (sentiment.score > 0.2) {
                overallElement.className += ' bullish';
            } else if (sentiment.score < -0.2) {
                overallElement.className += ' bearish';
            } else {
                overallElement.className += ' neutral';
            }
            
            // Update individual indicators
            const grid = document.getElementById('sentimentGrid');
            grid.innerHTML = '';
            
            // VIX Indicator
            if (sentiment.components.vix) {
                const vix = sentiment.components.vix;
                const vixClass = vix.score < -0.3 ? 'fear' : vix.score > 0.3 ? 'greed' : '';
                grid.innerHTML += `
                    <div class="sentiment-indicator vix-gauge ${vixClass}">
                        <div class="indicator-label">VIX Fear Gauge</div>
                        <div class="indicator-value">${vix.value ? vix.value.toFixed(2) : 'N/A'}</div>
                        <div class="indicator-change">${vix.sentiment}</div>
                        <div class="indicator-description">${vix.description}</div>
                    </div>
                `;
            }
            
            // Market Breadth
            if (sentiment.components.market_breadth) {
                const breadth = sentiment.components.market_breadth;
                grid.innerHTML += `
                    <div class="sentiment-indicator">
                        <div class="indicator-label">Market Breadth</div>
                        <div class="indicator-value">${(breadth.ratio * 100).toFixed(0)}%</div>
                        <div class="indicator-change ${breadth.score > 0 ? 'positive' : 'negative'}">${breadth.sentiment}</div>
                        <div class="indicator-description">${breadth.description}</div>
                    </div>
                `;
            }
            
            // Bond Yields
            if (sentiment.components.bond_yields) {
                const yields = sentiment.components.bond_yields;
                grid.innerHTML += `
                    <div class="sentiment-indicator">
                        <div class="indicator-label">10Y Treasury</div>
                        <div class="indicator-value">${yields.current ? yields.current.toFixed(2) + '%' : 'N/A'}</div>
                        <div class="indicator-change ${yields.change > 0 ? 'positive' : 'negative'}">${yields.change > 0 ? '+' : ''}${yields.change.toFixed(2)}%</div>
                        <div class="indicator-description">${yields.sentiment}</div>
                    </div>
                `;
            }
            
            // Dollar Index
            if (sentiment.components.dollar_index) {
                const dollar = sentiment.components.dollar_index;
                grid.innerHTML += `
                    <div class="sentiment-indicator">
                        <div class="indicator-label">Dollar Index</div>
                        <div class="indicator-value">${dollar.value ? dollar.value.toFixed(2) : 'N/A'}</div>
                        <div class="indicator-change ${dollar.change > 0 ? 'positive' : 'negative'}">${dollar.change > 0 ? '+' : ''}${dollar.change.toFixed(2)}%</div>
                        <div class="indicator-description">${dollar.sentiment}</div>
                    </div>
                `;
            }
            
            // Sector Rotation
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
        
        async function fetchStockData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            // Show loading
            document.getElementById('indicators').innerHTML = '<div class="loading">Loading...</div>';
            document.getElementById('predictions').innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=${interval}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentData = data;
                    updateUI(data);
                    drawChart(data);
                    updateFeatureImportance(data.feature_importance);
                } else {
                    showError(data.error || 'Failed to fetch data');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            }
        }
        
        function updateUI(data) {
            // Update indicators
            const indicatorsDiv = document.getElementById('indicators');
            if (data.indicators) {
                let html = '<div style="display: grid; gap: 10px;">';
                html += `<div>RSI: <strong>${data.indicators.rsi?.toFixed(2) || 'N/A'}</strong></div>`;
                html += `<div>MACD: <strong>${data.indicators.macd?.macd?.toFixed(2) || 'N/A'}</strong></div>`;
                html += `<div>Signal: <strong>${data.indicators.macd?.signal?.toFixed(2) || 'N/A'}</strong></div>`;
                html += `<div>SMA 20: <strong>$${data.indicators.sma_20?.toFixed(2) || 'N/A'}</strong></div>`;
                html += `<div>SMA 50: <strong>$${data.indicators.sma_50?.toFixed(2) || 'N/A'}</strong></div>`;
                html += `<div>ATR: <strong>${data.indicators.atr?.toFixed(2) || 'N/A'}</strong></div>`;
                html += '</div>';
                indicatorsDiv.innerHTML = html;
            }
            
            // Update predictions with sentiment note
            const predictionsDiv = document.getElementById('predictions');
            if (data.predictions && data.predictions.length > 0) {
                let html = '<div style="display: grid; gap: 10px;">';
                html += '<div style="color: #666; font-size: 12px;">Enhanced with market sentiment</div>';
                data.predictions.forEach((pred, i) => {
                    const change = ((pred - data.current_price) / data.current_price * 100).toFixed(2);
                    const color = change > 0 ? '#10b981' : '#ef4444';
                    html += `<div>Day ${i+1}: <strong style="color: ${color}">$${pred.toFixed(2)} (${change > 0 ? '+' : ''}${change}%)</strong></div>`;
                });
                html += '</div>';
                predictionsDiv.innerHTML = html;
            } else {
                predictionsDiv.innerHTML = 'Insufficient data for predictions';
            }
        }
        
        function updateFeatureImportance(features) {
            const div = document.getElementById('featureImportance');
            if (features && features.length > 0) {
                let html = '';
                features.slice(0, 10).forEach(f => {
                    const width = (f.importance * 300).toFixed(0);
                    html += `
                        <div class="feature-item">
                            <span>${f.feature}</span>
                            <span>${(f.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div class="feature-bar" style="width: ${width}px"></div>
                    `;
                });
                div.innerHTML = html;
            }
        }
        
        function drawChart(data) {
            const ctx = document.getElementById('priceChart').getContext('2d');
            
            if (chartInstance) {
                chartInstance.destroy();
            }
            
            if (!data.candlestick_data || data.candlestick_data.length === 0) {
                return;
            }
            
            if (currentChartType === 'line') {
                drawLineChart(ctx, data);
            } else {
                drawCandlestickChart(ctx, data);
            }
        }
        
        function drawCandlestickChart(ctx, data) {
            const candlestickData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                o: item.open,
                h: item.high,
                l: item.low,
                c: item.close
            }));
            
            chartInstance = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: candlestickData
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        zoom: {
                            zoom: {
                                wheel: { enabled: true },
                                pinch: { enabled: true },
                                mode: 'xy'
                            },
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            }
                        }
                    }
                }
            });
        }
        
        function drawLineChart(ctx, data) {
            const lineData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                y: item.close
            }));
            
            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: data.symbol + ' Price',
                        data: lineData,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        zoom: {
                            zoom: {
                                wheel: { enabled: true },
                                pinch: { enabled: true },
                                mode: 'xy'
                            },
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            }
                        }
                    }
                }
            });
        }
        
        function switchChartType(type) {
            currentChartType = type;
            if (currentData) {
                drawChart(currentData);
            }
        }
        
        function zoomIn() {
            if (chartInstance) chartInstance.zoom(1.1);
        }
        
        function zoomOut() {
            if (chartInstance) chartInstance.zoom(0.9);
        }
        
        function resetZoom() {
            if (chartInstance) chartInstance.resetZoom();
        }
        
        function refreshSentiment() {
            loadMarketSentiment();
            if (currentData) {
                fetchStockData();
            }
        }
        
        function showError(message) {
            alert('Error: ' + message);
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("STOCK ANALYSIS WITH MARKET SENTIMENT - PHASE 1")
    print("=" * 60)
    print("Enhanced Features:")
    print("✓ VIX Fear Gauge integration")
    print("✓ Market breadth analysis")
    print("✓ Bond yield tracking")
    print("✓ Dollar strength indicator")
    print("✓ Sector rotation analysis")
    print("✓ Sentiment-enhanced ML predictions")
    print("✓ Feature importance display")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Disable dotenv loading to avoid encoding issues
    import os
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    
    app.run(host='0.0.0.0', port=5000, debug=False)
