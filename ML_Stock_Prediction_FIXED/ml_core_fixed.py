#!/usr/bin/env python3
"""
ML Core - FIXED VERSION with all endpoints
REAL DATA ONLY - Improved Yahoo Finance connection
"""

# Configuration
try:
    from config import *
except ImportError:
    PORT = 8000
    CACHE_ENABLED = True

import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

import pandas as pd
import numpy as np
import yfinance as yf

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

import ta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

class MLStockPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_size': 0,
            'last_update': datetime.now().isoformat()
        }
        self.initialize_cache()
        
    def initialize_cache(self):
        """Initialize SQLite cache database"""
        if CACHE_ENABLED:
            try:
                self.cache_db = sqlite3.connect('market_cache.db', check_same_thread=False)
                self.cache_db.execute('''
                    CREATE TABLE IF NOT EXISTS stock_cache (
                        symbol TEXT,
                        date TEXT,
                        data TEXT,
                        PRIMARY KEY (symbol, date)
                    )
                ''')
                self.cache_db.commit()
                logger.info("Cache database initialized")
            except Exception as e:
                logger.error(f"Cache initialization failed: {e}")
                self.cache_db = None
        else:
            self.cache_db = None
    
    def fetch_stock_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch stock data with improved Yahoo Finance connection"""
        logger.info(f"Fetching data for {symbol}, period={period}")
        
        # Update cache stats
        self.cache_stats['total_requests'] += 1
        
        # Try cache first
        if self.cache_db:
            try:
                cache_key = f"{symbol}_{period}_{datetime.now().date()}"
                cursor = self.cache_db.execute(
                    "SELECT data FROM stock_cache WHERE symbol=? AND date=?",
                    (symbol, cache_key)
                )
                cached = cursor.fetchone()
                if cached:
                    self.cache_stats['hits'] += 1
                    logger.info(f"Cache hit for {symbol}")
                    return pd.read_json(cached[0])
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        self.cache_stats['misses'] += 1
        
        # Try multiple methods to fetch from Yahoo Finance
        methods = [
            # Method 1: Download with specific parameters
            lambda: yf.download(
                symbol, 
                period=period, 
                progress=False, 
                threads=False,
                group_by=None,
                auto_adjust=True,
                prepost=False
            ),
            
            # Method 2: Ticker approach
            lambda: yf.Ticker(symbol).history(period=period, auto_adjust=True),
            
            # Method 3: Download with different interval
            lambda: yf.download(
                symbol,
                start=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d'),
                progress=False,
                threads=False
            ),
        ]
        
        df = None
        for i, method in enumerate(methods, 1):
            try:
                logger.info(f"Trying method {i} for {symbol}...")
                df = method()
                
                # Check if we got valid data
                if df is not None and not df.empty and len(df) > 0:
                    # Clean column names if multi-index
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    # Ensure we have required columns
                    required = ['Open', 'High', 'Low', 'Close', 'Volume']
                    if all(col in df.columns for col in required):
                        logger.info(f"Successfully fetched {len(df)} rows using method {i}")
                        
                        # Cache the data
                        if self.cache_db:
                            try:
                                cache_key = f"{symbol}_{period}_{datetime.now().date()}"
                                self.cache_db.execute(
                                    "INSERT OR REPLACE INTO stock_cache VALUES (?, ?, ?)",
                                    (symbol, cache_key, df.to_json())
                                )
                                self.cache_db.commit()
                                self.cache_stats['cache_size'] += 1
                            except Exception as e:
                                logger.warning(f"Cache write failed: {e}")
                        
                        return df
            except Exception as e:
                logger.warning(f"Method {i} failed: {e}")
                continue
        
        # If all methods failed
        raise ValueError(f"Unable to fetch data for {symbol}. Yahoo Finance may be temporarily unavailable.")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare technical indicators as features"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['price_change'] = df['Close'] - df['Open']
        features['high_low_ratio'] = df['High'] / df['Low']
        features['close_open_ratio'] = df['Close'] / df['Open']
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            features[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
            features[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        # Bollinger Bands
        try:
            bb = ta.volatility.BollingerBands(df['Close'])
            features['bb_high'] = bb.bollinger_hband()
            features['bb_low'] = bb.bollinger_lband()
            features['bb_mid'] = bb.bollinger_mavg()
        except:
            features['bb_high'] = df['Close'] * 1.02
            features['bb_low'] = df['Close'] * 0.98
            features['bb_mid'] = df['Close']
        
        # RSI
        try:
            features['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        except:
            features['rsi'] = 50
        
        # MACD
        try:
            macd = ta.trend.MACD(df['Close'])
            features['macd'] = macd.macd()
            features['macd_signal'] = macd.macd_signal()
            features['macd_diff'] = macd.macd_diff()
        except:
            features['macd'] = 0
            features['macd_signal'] = 0
            features['macd_diff'] = 0
        
        # Volume features
        features['volume_sma'] = df['Volume'].rolling(window=20).mean()
        features['volume_ratio'] = df['Volume'] / features['volume_sma'].fillna(df['Volume'].mean())
        
        # Fill NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def train_model(self, symbol: str, days: int = 180, ensemble_type: str = "voting"):
        """Train ML model on stock data"""
        try:
            logger.info(f"Training model for {symbol}...")
            
            # Fetch data
            df = self.fetch_stock_data(symbol, period=f"{days}d")
            
            if len(df) < 60:
                raise ValueError(f"Insufficient data: {len(df)} rows")
            
            # Prepare features
            features = self.prepare_features(df)
            
            # Target: next day return
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Clean data
            features = features[50:-1]  # Remove rows with NaN
            target = target[50:-1]
            
            if len(features) < 30:
                raise ValueError("Not enough data after cleaning")
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features[:split_idx]
            y_train = target[:split_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            
            # Create models
            models = []
            
            # RandomForest
            rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
            models.append(('rf', rf))
            
            # XGBoost or GradientBoosting
            if XGBOOST_AVAILABLE:
                xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.01, random_state=42)
                models.append(('xgb', xgb_model))
            else:
                gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.01, random_state=42)
                models.append(('gb', gb))
            
            # SVM
            svm = SVR(kernel='rbf', C=1.0, gamma='scale')
            models.append(('svm', svm))
            
            # Create ensemble
            if ensemble_type == "voting":
                weights = [0.5, 0.3, 0.2]
                ensemble = VotingRegressor(models, weights=weights)
            else:
                ensemble = VotingRegressor(models)
            
            # Train
            start_time = time.time()
            ensemble.fit(X_train_scaled, y_train)
            training_time = time.time() - start_time
            
            # Store
            self.models[symbol] = ensemble
            self.scalers[symbol] = scaler
            
            # Calculate score
            score = ensemble.score(X_train_scaled, y_train)
            
            result = {
                'symbol': symbol,
                'training_samples': len(X_train),
                'features_count': len(features.columns),
                'train_score': float(score),
                'training_time': float(training_time),
                'model_type': ensemble_type,
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_history[symbol] = result
            logger.info(f"Training complete! Score: {score:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def predict(self, symbol: str):
        """Make prediction for symbol"""
        try:
            if symbol not in self.models:
                raise ValueError(f"No model trained for {symbol}")
            
            # Get recent data
            df = self.fetch_stock_data(symbol, period="1mo")
            
            # Prepare features
            features = self.prepare_features(df)
            X = features.iloc[-1:].values
            X_scaled = self.scalers[symbol].transform(X)
            
            # Predict
            prediction = self.models[symbol].predict(X_scaled)[0]
            
            # Calculate confidence
            confidence = min(0.85, 0.5 + abs(prediction) * 10)
            
            return {
                'symbol': symbol,
                'prediction': float(prediction),
                'direction': 'UP' if prediction > 0 else 'DOWN',
                'confidence': float(confidence),
                'current_price': float(df['Close'].iloc[-1]),
                'predicted_price': float(df['Close'].iloc[-1] * (1 + prediction)),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def backtest(self, symbol: str, days: int = 30):
        """Run backtest on historical data"""
        try:
            if symbol not in self.models:
                raise ValueError(f"No model trained for {symbol}")
            
            # Get historical data
            df = self.fetch_stock_data(symbol, period=f"{days+60}d")
            features = self.prepare_features(df)
            
            # Prepare test data
            test_features = features.iloc[-days:]
            test_prices = df['Close'].iloc[-days:]
            
            # Make predictions
            predictions = []
            for i in range(len(test_features)):
                X = test_features.iloc[i:i+1].values
                X_scaled = self.scalers[symbol].transform(X)
                pred = self.models[symbol].predict(X_scaled)[0]
                predictions.append(pred)
            
            # Calculate metrics
            predictions = np.array(predictions)
            actual_returns = test_prices.pct_change().iloc[1:].values
            predicted_direction = np.sign(predictions[:-1])
            actual_direction = np.sign(actual_returns)
            
            accuracy = np.mean(predicted_direction == actual_direction)
            
            return {
                'symbol': symbol,
                'days': days,
                'accuracy': float(accuracy),
                'total_trades': len(predictions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Create FastAPI app
app = FastAPI(title="ML Stock Predictor")
predictor = MLStockPredictor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Serve the web interface"""
    try:
        with open("interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except:
        return {"message": "ML Stock Predictor API"}

@app.post("/api/train")
async def train_model(request: dict):
    """Train ML model"""
    symbol = request.get('symbol', 'AAPL').upper()
    days = request.get('days', 180)
    ensemble_type = request.get('ensemble_type', 'voting')
    
    result = predictor.train_model(symbol, days, ensemble_type)
    return JSONResponse(content=result)

@app.post("/api/predict")
async def predict(request: dict):
    """Make prediction"""
    symbol = request.get('symbol', 'AAPL').upper()
    result = predictor.predict(symbol)
    return JSONResponse(content=result)

@app.post("/api/backtest")
async def backtest(request: dict):
    """Run backtest"""
    symbol = request.get('symbol', 'AAPL').upper()
    days = request.get('days', 30)
    result = predictor.backtest(symbol, days)
    return JSONResponse(content=result)

@app.get("/api/models")
async def get_models():
    """Get list of trained models"""
    return {"models": list(predictor.models.keys())}

@app.get("/api/history/{symbol}")
async def get_history(symbol: str):
    """Get training history for symbol"""
    history = predictor.training_history.get(symbol.upper(), {})
    return JSONResponse(content=history)

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    predictor.cache_stats['last_update'] = datetime.now().isoformat()
    return JSONResponse(content=predictor.cache_stats)

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear the cache"""
    try:
        if predictor.cache_db:
            predictor.cache_db.execute("DELETE FROM stock_cache")
            predictor.cache_db.commit()
            predictor.cache_stats = {
                'hits': 0,
                'misses': 0, 
                'total_requests': 0,
                'cache_size': 0,
                'last_update': datetime.now().isoformat()
            }
        return {"status": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def status():
    """System status"""
    return {
        "status": "running",
        "models_loaded": len(predictor.models),
        "cache_enabled": CACHE_ENABLED,
        "cache_stats": predictor.cache_stats,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("="*60)
    print("ML Stock Prediction System - FIXED VERSION")
    print("="*60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print("Real data only - No fallback\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)