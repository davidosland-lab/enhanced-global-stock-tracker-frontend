#!/usr/bin/env python3
"""
ML Core - REAL DATA ONLY - NO FALLBACK, NO DEMO, NO SIMULATION
This version will ONLY work with real Yahoo Finance data
If Yahoo Finance fails, the system stops - no fake data
"""

# ==================== CONFIGURATION ====================
USE_SENTIMENT = False
PORT = 8000

import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== IMPORTS ====================
import sys
import os
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import time
from requests import Session

# Data handling
import pandas as pd
import numpy as np
import yfinance as yf

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, StackingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.info("XGBoost not available, using GradientBoosting")

import ta

# Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

# ==================== NO FALLBACK - REAL DATA ONLY ====================

class RealDataOnly:
    """This class ONLY uses real Yahoo Finance data - NO FALLBACK"""
    
    @staticmethod
    def fetch_real_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
        """
        Fetch REAL data from Yahoo Finance only
        NO FALLBACK, NO SIMULATION, NO DEMO DATA
        """
        try:
            logger.info(f"Fetching REAL data for {symbol} from Yahoo Finance...")
            
            # Create session with proper headers to fix common issues
            session = Session()
            session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            
            # Try multiple methods to get data
            methods = [
                # Method 1: Download with session
                lambda: yf.download(symbol, period=period, progress=False, threads=False, session=session),
                
                # Method 2: Ticker with session
                lambda: yf.Ticker(symbol, session=session).history(period=period),
                
                # Method 3: Standard download
                lambda: yf.download(symbol, period=period, progress=False, threads=False),
                
                # Method 4: Standard Ticker
                lambda: yf.Ticker(symbol).history(period=period)
            ]
            
            for i, method in enumerate(methods, 1):
                try:
                    df = method()
                    if df is not None and not df.empty:
                        logger.info(f"✅ Successfully fetched {len(df)} days of REAL data using method {i}")
                        return df
                except Exception as e:
                    logger.warning(f"Method {i} failed: {e}")
                    continue
            
            # If we get here, all methods failed
            raise ValueError(f"Cannot fetch real data for {symbol}. Yahoo Finance is not accessible.")
            
        except Exception as e:
            logger.error(f"❌ REAL DATA FETCH FAILED: {e}")
            raise ValueError(f"NO FALLBACK: Cannot get real data for {symbol}. System requires Yahoo Finance to work.")

# ==================== ML SYSTEM - REAL DATA ONLY ====================

class MLStockPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        self.data_fetcher = RealDataOnly()
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate 35 REAL technical indicators from REAL data"""
        if df.empty:
            raise ValueError("No data to calculate features")
            
        try:
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
            bb = ta.volatility.BollingerBands(df['Close'])
            features['bb_high'] = bb.bollinger_hband()
            features['bb_low'] = bb.bollinger_lband()
            features['bb_mid'] = bb.bollinger_mavg()
            features['bb_width'] = features['bb_high'] - features['bb_low']
            
            # RSI
            features['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['Close'])
            features['macd'] = macd.macd()
            features['macd_signal'] = macd.macd_signal()
            features['macd_diff'] = macd.macd_diff()
            
            # Volume features
            features['volume_sma'] = df['Volume'].rolling(window=20).mean()
            features['volume_ratio'] = df['Volume'] / features['volume_sma']
            features['obv'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
            
            # Volatility
            features['atr'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            features['volatility'] = df['Close'].rolling(window=20).std()
            
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
            features['stoch_k'] = stoch.stoch()
            features['stoch_d'] = stoch.stoch_signal()
            
            # Support/Resistance
            features['resistance'] = df['High'].rolling(window=20).max()
            features['support'] = df['Low'].rolling(window=20).min()
            features['middle_point'] = (features['resistance'] + features['support']) / 2
            
            features = features.fillna(method='ffill').fillna(0)
            return features
            
        except Exception as e:
            logger.error(f"Feature calculation failed: {e}")
            raise ValueError(f"Cannot calculate features: {e}")
    
    def train_model(self, symbol: str, days: int = 180, ensemble_type: str = "voting"):
        """Train on REAL data only - NO FALLBACK"""
        try:
            logger.info(f"Training model for {symbol} with REAL data only...")
            
            # Get REAL data - will fail if Yahoo Finance doesn't work
            df = self.data_fetcher.fetch_real_data(symbol, period=f"{days}d")
            
            if len(df) < 60:
                raise ValueError(f"Need at least 60 days of data, got {len(df)}")
            
            # Calculate REAL features
            features = self.prepare_features(df)
            
            # Prepare target
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Remove invalid rows
            features = features[50:-1]
            target = target[50:-1]
            
            if len(features) < 30:
                raise ValueError("Not enough data after feature calculation")
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features[:split_idx]
            y_train = target[:split_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            
            logger.info(f"Training on {len(X_train)} samples of REAL data...")
            
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
            
            # Additional models
            gb2 = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
            models.append(('gb2', gb2))
            
            svm = SVR(kernel='rbf', C=1.0, gamma='scale')
            models.append(('svm', svm))
            
            nn = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
            models.append(('nn', nn))
            
            # Create ensemble
            if ensemble_type == "voting":
                weights = [0.30, 0.25, 0.25, 0.15, 0.05]
                ensemble = VotingRegressor(models, weights=weights)
            else:
                ensemble = StackingRegressor(
                    estimators=models,
                    final_estimator=RandomForestRegressor(n_estimators=50, random_state=42)
                )
            
            # Train with REAL data
            start_time = time.time()
            ensemble.fit(X_train_scaled, y_train)
            training_time = time.time() - start_time
            
            # Store model
            self.models[symbol] = ensemble
            self.scalers[symbol] = scaler
            
            # Calculate score
            train_score = ensemble.score(X_train_scaled, y_train)
            
            result = {
                'symbol': symbol,
                'training_samples': len(X_train),
                'features_count': len(features.columns),
                'train_score': float(train_score),
                'training_time': float(training_time),
                'data_source': 'Yahoo Finance (REAL)',
                'model_type': ensemble_type,
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_history[symbol] = result
            logger.info(f"✅ Training complete with REAL data. Score: {train_score:.4f}, Time: {training_time:.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise HTTPException(status_code=500, detail=f"Training failed - REAL DATA ONLY: {str(e)}")
    
    def predict(self, symbol: str):
        """Make prediction with REAL data only"""
        try:
            if symbol not in self.models:
                raise ValueError(f"No model trained for {symbol}")
            
            # Get REAL recent data
            df = self.data_fetcher.fetch_real_data(symbol, period="1mo")
            
            # Calculate features
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
                'data_source': 'Yahoo Finance (REAL)',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed - REAL DATA ONLY: {str(e)}")

# ==================== API ====================

app = FastAPI(title="ML Stock Predictor - REAL DATA ONLY")
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
        with open("ml_core_interface_clean.html", "r") as f:
            return HTMLResponse(content=f.read())
    except:
        return {"message": "ML Stock Predictor - REAL DATA ONLY - No interface file found"}

@app.post("/api/train")
async def train_model(request: dict):
    """Train model with REAL data only"""
    symbol = request.get('symbol', 'AAPL').upper()
    days = request.get('days', 180)
    ensemble_type = request.get('ensemble_type', 'voting')
    
    result = predictor.train_model(symbol, days, ensemble_type)
    return JSONResponse(content=result)

@app.post("/api/predict")
async def predict(request: dict):
    """Predict with REAL data only"""
    symbol = request.get('symbol', 'AAPL').upper()
    result = predictor.predict(symbol)
    return JSONResponse(content=result)

@app.get("/api/status")
async def status():
    """System status"""
    return {
        "status": "REAL DATA ONLY MODE",
        "data_source": "Yahoo Finance",
        "fallback": "DISABLED - NO FAKE DATA",
        "models_trained": list(predictor.models.keys())
    }

if __name__ == "__main__":
    print("="*60)
    print("ML Stock Prediction System - REAL DATA ONLY")
    print("NO FALLBACK - NO DEMO - NO SIMULATION")
    print("="*60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print("\n⚠️  This version ONLY works with Yahoo Finance")
    print("If Yahoo Finance is blocked, the system will NOT work")
    print("This is by design - NO FAKE DATA\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)