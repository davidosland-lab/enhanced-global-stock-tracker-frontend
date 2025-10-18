#!/usr/bin/env python3
"""
ML Core - DEBUG VERSION to identify the exact error
REAL DATA ONLY - Shows detailed error messages
"""

PORT = 8000

import logging
import warnings
warnings.filterwarnings('ignore')

# Enhanced logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import sys
import traceback
import json
from datetime import datetime, timedelta
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
        
    def fetch_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch data with detailed error reporting"""
        logger.info(f"Fetching data for {symbol}, period={period}")
        
        try:
            # Method 1: Direct download
            logger.debug("Trying yf.download...")
            df = yf.download(symbol, period=period, progress=False, threads=False)
            
            if df.empty:
                logger.error(f"yf.download returned empty dataframe for {symbol}")
                # Try ticker method
                logger.debug("Trying yf.Ticker...")
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
                
            logger.info(f"Successfully fetched {len(df)} rows of data")
            logger.debug(f"Data columns: {df.columns.tolist()}")
            logger.debug(f"Date range: {df.index[0]} to {df.index[-1]}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch data: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate features with error handling"""
        logger.info(f"Preparing features from {len(df)} rows")
        
        try:
            features = pd.DataFrame(index=df.index)
            
            # Basic price features
            features['returns'] = df['Close'].pct_change()
            features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            features['price_change'] = df['Close'] - df['Open']
            features['high_low_ratio'] = df['High'] / df['Low']
            features['close_open_ratio'] = df['Close'] / df['Open']
            
            # Moving averages
            for period in [5, 10, 20, 50]:
                features[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
                features[f'ema_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
            
            # Technical indicators
            try:
                # Bollinger Bands
                bb = ta.volatility.BollingerBands(df['Close'])
                features['bb_high'] = bb.bollinger_hband()
                features['bb_low'] = bb.bollinger_lband()
                features['bb_mid'] = bb.bollinger_mavg()
                features['bb_width'] = features['bb_high'] - features['bb_low']
            except Exception as e:
                logger.warning(f"Bollinger Bands failed: {e}")
                features['bb_high'] = df['Close'] * 1.02
                features['bb_low'] = df['Close'] * 0.98
                features['bb_mid'] = df['Close']
                features['bb_width'] = features['bb_high'] - features['bb_low']
            
            try:
                # RSI
                features['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            except Exception as e:
                logger.warning(f"RSI failed: {e}")
                features['rsi'] = 50  # Neutral RSI
            
            try:
                # MACD
                macd = ta.trend.MACD(df['Close'])
                features['macd'] = macd.macd()
                features['macd_signal'] = macd.macd_signal()
                features['macd_diff'] = macd.macd_diff()
            except Exception as e:
                logger.warning(f"MACD failed: {e}")
                features['macd'] = 0
                features['macd_signal'] = 0
                features['macd_diff'] = 0
            
            # Volume features
            features['volume_sma'] = df['Volume'].rolling(window=20).mean()
            features['volume_ratio'] = df['Volume'] / features['volume_sma'].fillna(df['Volume'].mean())
            
            try:
                features['obv'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
            except Exception as e:
                logger.warning(f"OBV failed: {e}")
                features['obv'] = df['Volume'].cumsum()
            
            # Volatility
            try:
                features['atr'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            except Exception as e:
                logger.warning(f"ATR failed: {e}")
                features['atr'] = (df['High'] - df['Low']).rolling(window=14).mean()
            
            features['volatility'] = df['Close'].rolling(window=20).std()
            
            try:
                # Stochastic
                stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
                features['stoch_k'] = stoch.stoch()
                features['stoch_d'] = stoch.stoch_signal()
            except Exception as e:
                logger.warning(f"Stochastic failed: {e}")
                features['stoch_k'] = 50
                features['stoch_d'] = 50
            
            # Support/Resistance
            features['resistance'] = df['High'].rolling(window=20).max()
            features['support'] = df['Low'].rolling(window=20).min()
            features['middle_point'] = (features['resistance'] + features['support']) / 2
            
            # Fill NaN values
            features = features.fillna(method='ffill').fillna(0)
            
            logger.info(f"Prepared {len(features.columns)} features")
            logger.debug(f"Feature columns: {features.columns.tolist()}")
            
            return features
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
    
    def train_model(self, symbol: str, days: int = 180, ensemble_type: str = "voting"):
        """Train with detailed error reporting"""
        logger.info(f"Starting training for {symbol}, days={days}, ensemble={ensemble_type}")
        
        try:
            # Fetch data
            df = self.fetch_data(symbol, period=f"{days}d")
            
            if len(df) < 60:
                raise ValueError(f"Insufficient data: got {len(df)} days, need at least 60")
            
            # Prepare features
            features = self.prepare_features(df)
            
            # Prepare target
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Remove NaN rows
            min_rows = 50
            features = features[min_rows:-1]
            target = target[min_rows:-1]
            
            if len(features) < 30:
                raise ValueError(f"Not enough data after cleaning: {len(features)} rows")
            
            # Split data
            split_idx = int(len(features) * 0.8)
            X_train = features[:split_idx]
            y_train = target[:split_idx]
            
            logger.info(f"Training on {len(X_train)} samples with {len(features.columns)} features")
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            
            # Create models
            models = []
            
            # RandomForest
            logger.debug("Creating RandomForest...")
            rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
            models.append(('rf', rf))
            
            # XGBoost or GradientBoosting
            if XGBOOST_AVAILABLE:
                logger.debug("Creating XGBoost...")
                xgb_model = xgb.XGBRegressor(n_estimators=50, max_depth=5, learning_rate=0.01, random_state=42)
                models.append(('xgb', xgb_model))
            else:
                logger.debug("Creating GradientBoosting...")
                gb = GradientBoostingRegressor(n_estimators=50, max_depth=5, learning_rate=0.01, random_state=42)
                models.append(('gb', gb))
            
            # Simple SVM
            logger.debug("Creating SVM...")
            svm = SVR(kernel='rbf', C=1.0, gamma='scale')
            models.append(('svm', svm))
            
            # Create ensemble
            if ensemble_type == "voting":
                weights = [0.5, 0.3, 0.2]  # Simplified weights
                ensemble = VotingRegressor(models, weights=weights)
            else:
                ensemble = VotingRegressor(models)  # Equal weights
            
            # Train
            logger.info("Training ensemble model...")
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
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"Training complete! Score: {train_score:.4f}, Time: {training_time:.1f}s")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Training failed: {error_msg}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            
            # Return error details for debugging
            return {
                'status': 'error',
                'error': error_msg,
                'traceback': traceback.format_exc(),
                'symbol': symbol
            }
    
    def predict(self, symbol: str):
        """Make prediction with error handling"""
        try:
            if symbol not in self.models:
                raise ValueError(f"No model trained for {symbol}")
            
            # Get recent data
            df = self.fetch_data(symbol, period="1mo")
            
            # Prepare features
            features = self.prepare_features(df)
            X = features.iloc[-1:].values
            X_scaled = self.scalers[symbol].transform(X)
            
            # Predict
            prediction = self.models[symbol].predict(X_scaled)[0]
            
            return {
                'symbol': symbol,
                'prediction': float(prediction),
                'direction': 'UP' if prediction > 0 else 'DOWN',
                'confidence': min(0.85, 0.5 + abs(prediction) * 10),
                'current_price': float(df['Close'].iloc[-1]),
                'predicted_price': float(df['Close'].iloc[-1] * (1 + prediction)),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Prediction failed: {error_msg}")
            
            return {
                'status': 'error',
                'error': error_msg,
                'symbol': symbol
            }

# Create FastAPI app
app = FastAPI(title="ML Stock Predictor - DEBUG MODE")
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
        return {"message": "ML Stock Predictor - DEBUG MODE"}

@app.post("/api/train")
async def train_model(request: dict):
    """Train model with detailed error reporting"""
    try:
        symbol = request.get('symbol', 'AAPL').upper()
        days = request.get('days', 180)
        ensemble_type = request.get('ensemble_type', 'voting')
        
        logger.info(f"Training request: symbol={symbol}, days={days}, ensemble={ensemble_type}")
        
        result = predictor.train_model(symbol, days, ensemble_type)
        
        if result.get('status') == 'error':
            # Return error with details
            logger.error(f"Training error details: {result}")
            raise HTTPException(status_code=500, detail=result)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        logger.error(f"API error: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@app.post("/api/predict")
async def predict(request: dict):
    """Make prediction"""
    symbol = request.get('symbol', 'AAPL').upper()
    result = predictor.predict(symbol)
    
    if result.get('status') == 'error':
        raise HTTPException(status_code=500, detail=result)
    
    return JSONResponse(content=result)

@app.get("/api/test")
async def test():
    """Test endpoint to verify API is working"""
    return {"status": "API is running", "debug_mode": True}

if __name__ == "__main__":
    print("="*60)
    print("ML Stock Prediction System - DEBUG MODE")
    print("="*60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print("\nThis version shows detailed error messages")
    print("Check the console for debugging information\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="debug")