#!/usr/bin/env python3
"""
Stock Analysis System with Enhanced Sentiment & Macro Indicators - Phase 1
Clean version with proper indentation
"""

# Disable Flask dotenv to prevent encoding issues
import os
os.environ['FLASK_SKIP_DOTENV'] = '1'

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

# Continue with the rest of the file content...