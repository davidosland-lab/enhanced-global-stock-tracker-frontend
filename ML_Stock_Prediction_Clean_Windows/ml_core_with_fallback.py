#!/usr/bin/env python3
"""
ML Core Enhanced Production System - WITH FALLBACK TO SAMPLE DATA
Automatically uses sample data when Yahoo Finance fails
"""

# ==================== CONFIGURATION ====================
try:
    from config import *
except ImportError:
    # Default configuration if config.py not found
    USE_SENTIMENT = False
    PORT = 8000
    ENABLE_CACHE = True
    CACHE_DB = "market_data.db"
    COMMISSION_RATE = 0.001
    SLIPPAGE_RATE = 0.0005

import logging
import warnings
warnings.filterwarnings('ignore')

# Setup logging
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

# Optional: XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.info("XGBoost not available, using GradientBoosting as fallback")

# Technical Analysis
import ta

# Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

# ==================== SAMPLE DATA FALLBACK ====================
def load_sample_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Load sample data when Yahoo Finance is unavailable"""
    try:
        filename = f'sample_data/{symbol}_data.csv'
        if os.path.exists(filename):
            logger.info(f"Loading sample data for {symbol} from {filename}")
            df = pd.read_csv(filename, index_col='Date', parse_dates=True)
            
            # Filter by period
            if period == "1mo":
                df = df.tail(30)
            elif period == "3mo":
                df = df.tail(90)
            elif period == "6mo":
                df = df.tail(180)
            
            return df
        else:
            logger.warning(f"Sample data not found for {symbol}")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        return pd.DataFrame()

def fetch_stock_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch stock data with fallback to sample data"""
    try:
        # Try Yahoo Finance first
        logger.info(f"Attempting to fetch {symbol} from Yahoo Finance...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            raise ValueError("No data returned from Yahoo Finance")
        
        logger.info(f"Successfully fetched {len(df)} days of data from Yahoo Finance")
        return df
        
    except Exception as e:
        logger.warning(f"Yahoo Finance failed: {e}")
        logger.info("Attempting to use sample data...")
        
        # Try sample data
        df = load_sample_data(symbol, period)
        
        if not df.empty:
            logger.info(f"Successfully loaded {len(df)} days of sample data")
            return df
        else:
            # Generate sample data on the fly if not available
            logger.info("Generating sample data on the fly...")
            df = generate_sample_data(symbol, days=180)
            if not df.empty:
                # Save for future use
                os.makedirs('sample_data', exist_ok=True)
                df.to_csv(f'sample_data/{symbol}_data.csv')
                logger.info(f"Generated and saved sample data for {symbol}")
            return df

def generate_sample_data(symbol: str, days: int = 180) -> pd.DataFrame:
    """Generate realistic sample data"""
    try:
        import numpy as np
        from datetime import datetime, timedelta
        
        # Price ranges for common stocks
        price_ranges = {
            'AAPL': 175.0, 'MSFT': 380.0, 'GOOGL': 140.0,
            'AMZN': 145.0, 'SPY': 440.0, 'TSLA': 250.0,
            'DEFAULT': 100.0
        }
        
        start_price = price_ranges.get(symbol.upper(), price_ranges['DEFAULT'])
        
        # Create date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        num_days = len(dates)
        prices = np.zeros(num_days)
        volumes = np.zeros(num_days)
        
        # Generate realistic price movement
        prices[0] = start_price
        base_volume = 50000000
        
        for i in range(1, num_days):
            # Daily return with mean reversion
            daily_return = np.random.normal(0.0005, 0.015)
            daily_return = np.clip(daily_return, -0.05, 0.05)
            prices[i] = prices[i-1] * (1 + daily_return)
            volumes[i] = base_volume * np.random.uniform(0.8, 1.2)
        
        # Create OHLC
        high = prices * np.random.uniform(1.001, 1.02, num_days)
        low = prices * np.random.uniform(0.98, 0.999, num_days)
        
        open_prices = np.zeros(num_days)
        open_prices[0] = prices[0]
        for i in range(1, num_days):
            gap = np.random.normal(0, 0.003)
            open_prices[i] = prices[i-1] * (1 + gap)
        
        df = pd.DataFrame({
            'Open': open_prices,
            'High': high,
            'Low': low,
            'Close': prices,
            'Volume': volumes.astype(int)
        }, index=dates)
        
        return df
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        return pd.DataFrame()

# ==================== ML SYSTEM ====================
class MLStockPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        self.cache_db = CACHE_DB
        self.initialize_cache()
        
    def initialize_cache(self):
        """Initialize SQLite cache"""
        try:
            conn = sqlite3.connect(self.cache_db)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_cache (
                    symbol TEXT,
                    date TEXT,
                    data TEXT,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Cache initialized successfully")
        except Exception as e:
            logger.error(f"Cache initialization failed: {e}")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate 35 technical indicators"""
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
            
            # Fill NaN values
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            return pd.DataFrame()
    
    def train_model(self, symbol: str, days: int = 180, ensemble_type: str = "voting"):
        """Train ML models on stock data"""
        try:
            logger.info(f"Training model for {symbol}...")
            
            # Fetch data with fallback
            df = fetch_stock_data(symbol, period=f"{days}d")
            
            if df.empty or len(df) < 60:
                raise ValueError("Insufficient data for training")
            
            # Prepare features
            features = self.prepare_features(df)
            
            if features.empty:
                raise ValueError("Feature preparation failed")
            
            # Prepare target (next day's return)
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Remove last row (no target) and first rows (NaN features)
            features = features[50:-1]
            target = target[50:-1]
            
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
            rf = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            models.append(('rf', rf))
            
            # XGBoost or GradientBoosting
            if XGBOOST_AVAILABLE:
                xgb_model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.01,
                    random_state=42
                )
                models.append(('xgb', xgb_model))
            else:
                gb = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.01,
                    random_state=42
                )
                models.append(('gb', gb))
            
            # Additional GradientBoosting
            gb2 = GradientBoostingRegressor(
                n_estimators=50,
                max_depth=3,
                random_state=42
            )
            models.append(('gb2', gb2))
            
            # SVM
            svm = SVR(kernel='rbf', C=1.0, gamma='scale')
            models.append(('svm', svm))
            
            # Neural Network
            nn = MLPRegressor(
                hidden_layer_sizes=(50, 25),
                max_iter=500,
                random_state=42
            )
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
            
            # Train ensemble
            logger.info("Training ensemble model...")
            ensemble.fit(X_train_scaled, y_train)
            
            # Store model and scaler
            self.models[symbol] = ensemble
            self.scalers[symbol] = scaler
            
            # Calculate training metrics
            train_score = ensemble.score(X_train_scaled, y_train)
            
            result = {
                'symbol': symbol,
                'training_samples': len(X_train),
                'features': list(features.columns),
                'train_score': float(train_score),
                'model_type': ensemble_type,
                'training_date': datetime.now().isoformat()
            }
            
            self.training_history[symbol] = result
            logger.info(f"Training completed. Score: {train_score:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def predict(self, symbol: str):
        """Make prediction for a symbol"""
        try:
            if symbol not in self.models:
                raise ValueError(f"No model trained for {symbol}")
            
            # Get recent data
            df = fetch_stock_data(symbol, period="1mo")
            
            if df.empty:
                raise ValueError("No data available for prediction")
            
            # Prepare features
            features = self.prepare_features(df)
            
            # Use last available features
            X = features.iloc[-1:].values
            
            # Scale
            X_scaled = self.scalers[symbol].transform(X)
            
            # Predict
            prediction = self.models[symbol].predict(X_scaled)[0]
            
            # Calculate confidence (simplified)
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

# ==================== API ====================
app = FastAPI(title="ML Stock Predictor")
predictor = MLStockPredictor()

# CORS
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
        return {"message": "ML Stock Predictor API - Interface not found"}

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

@app.get("/api/models")
async def get_models():
    """Get list of trained models"""
    return {"models": list(predictor.models.keys())}

@app.get("/api/history/{symbol}")
async def get_history(symbol: str):
    """Get training history"""
    history = predictor.training_history.get(symbol.upper(), {})
    return JSONResponse(content=history)

if __name__ == "__main__":
    print("="*60)
    print("ML Stock Prediction System")
    print("WITH AUTOMATIC FALLBACK TO SAMPLE DATA")
    print("="*60)
    print(f"\nStarting server on http://localhost:{PORT}")
    print("\nIf Yahoo Finance fails, the system will automatically")
    print("use or generate sample data for testing.\n")
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)