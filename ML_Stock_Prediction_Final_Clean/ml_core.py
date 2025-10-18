#!/usr/bin/env python3
"""
ML Stock Prediction Core System
Clean, working version with proper imports
Version: 3.0 FINAL
"""

# ==================== CONFIGURATION ====================
try:
    from ml_config import *
except ImportError:
    # Default configuration
    USE_SENTIMENT_ANALYSIS = False
    PORT = 8000
    CACHE_DURATION = 300

# ==================== IMPORTS ====================
import os
import sys
import json
import pickle
import sqlite3
import hashlib
import logging
import warnings
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data processing
import pandas as pd
import numpy as np

# Yahoo Finance
import yfinance as yf
from requests import Session

# Technical Analysis
import ta

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Optional: XGBoost
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.info("XGBoost not available, using GradientBoosting")

# Optional: Sentiment (disabled by default)
SENTIMENT_AVAILABLE = False
if USE_SENTIMENT_ANALYSIS:
    try:
        from comprehensive_sentiment_analyzer_fixed import sentiment_analyzer
        SENTIMENT_AVAILABLE = True
        logger.info("Sentiment analyzer enabled")
    except ImportError:
        logger.warning("Sentiment analyzer not found")

# Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# ==================== CUSTOM JSON ENCODER ====================
class CustomJSONEncoder(json.JSONEncoder):
    """Handle pandas/numpy types in JSON"""
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif pd.api.types.is_datetime64_any_dtype(obj):
            return str(obj)
        return super().default(obj)

# ==================== DATABASE MANAGER ====================
class DatabaseManager:
    """Manage all database operations"""
    
    def __init__(self):
        self.cache_db = "ml_cache.db"
        self.models_db = "ml_models.db"
        self.backtest_db = "ml_backtest.db"
        self.init_databases()
    
    def init_databases(self):
        """Initialize all databases"""
        # Cache database
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_cache (
                    cache_key TEXT PRIMARY KEY,
                    data BLOB,
                    expires_at TIMESTAMP
                )
            """)
        
        # Models database
        with sqlite3.connect(self.models_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    model_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    model_type TEXT,
                    model_data BLOB,
                    metrics TEXT,
                    created_at TIMESTAMP
                )
            """)
        
        # Backtest database
        with sqlite3.connect(self.backtest_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backtest_results (
                    test_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    strategy TEXT,
                    results TEXT,
                    created_at TIMESTAMP
                )
            """)

# ==================== DATA FETCHER ====================
class DataFetcher:
    """Fetch and cache market data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def fetch_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """Fetch data with caching"""
        
        # Check cache
        cache_key = f"{symbol}_{period}_{interval}"
        cached = self.get_cached_data(cache_key)
        if cached is not None:
            logger.info(f"Using cached data for {symbol}")
            return cached
        
        # Fetch fresh data
        logger.info(f"Fetching fresh data for {symbol}")
        try:
            ticker = yf.Ticker(symbol, session=self.session)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                # Try alternative method
                df = yf.download(symbol, period=period, interval=interval, 
                               progress=False, session=self.session)
            
            if not df.empty:
                # Cache the data
                self.cache_data(cache_key, df)
                return df
            else:
                raise ValueError(f"No data available for {symbol}")
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise HTTPException(status_code=404, detail=f"Failed to fetch data for {symbol}")
    
    def get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Get data from cache"""
        with sqlite3.connect(self.db.cache_db) as conn:
            cursor = conn.execute(
                "SELECT data FROM data_cache WHERE cache_key = ? AND expires_at > datetime('now')",
                (cache_key,)
            )
            row = cursor.fetchone()
            if row:
                return pickle.loads(row[0])
        return None
    
    def cache_data(self, cache_key: str, data: pd.DataFrame):
        """Store data in cache"""
        expires_at = datetime.now() + timedelta(seconds=CACHE_DURATION)
        with sqlite3.connect(self.db.cache_db) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO data_cache (cache_key, data, expires_at) VALUES (?, ?, ?)",
                (cache_key, pickle.dumps(data), expires_at)
            )

# ==================== FEATURE ENGINEERING ====================
class FeatureEngineer:
    """Calculate technical indicators"""
    
    FEATURES = [
        'Returns', 'Log_Returns', 'Volatility',
        'RSI', 'MACD', 'MACD_Signal', 'MACD_Diff',
        'BB_High', 'BB_Low', 'BB_Mid', 'BB_Percent',
        'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
        'ATR', 'OBV', 'Volume_Ratio',
        'High_Low_Ratio', 'Close_Open_Ratio'
    ]
    
    def calculate_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Calculate all technical features"""
        
        df = df.copy()
        
        # Price features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'], window=20)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Mid'] = bb.bollinger_mavg()
        df['BB_Percent'] = (df['Close'] - df['BB_Low']) / (df['BB_High'] - df['BB_Low'])
        
        # Moving Averages
        df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        df['EMA_12'] = ta.trend.EMAIndicator(df['Close'], window=12).ema_indicator()
        df['EMA_26'] = ta.trend.EMAIndicator(df['Close'], window=26).ema_indicator()
        
        # ATR
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        
        # Volume indicators
        df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Price ratios
        df['High_Low_Ratio'] = df['High'] / df['Low']
        df['Close_Open_Ratio'] = df['Close'] / df['Open']
        
        # Optional: Add sentiment
        if SENTIMENT_AVAILABLE and symbol:
            try:
                sentiment_score = sentiment_analyzer.calculate_comprehensive_sentiment(symbol)
                df['Sentiment'] = sentiment_score
                self.FEATURES.append('Sentiment')
            except:
                df['Sentiment'] = 0.5  # Neutral if fails
        
        # Drop NaN values
        df = df.dropna()
        
        return df

# ==================== ML TRAINER ====================
class MLTrainer:
    """Train and manage ML models"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.scaler = StandardScaler()
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, model_type: str = "ensemble") -> Dict:
        """Train ML model"""
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )
        
        # Select model
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            if HAS_XGBOOST:
                model = xgb.XGBRegressor(n_estimators=100, random_state=42)
            else:
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:  # ensemble
            models = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=50, random_state=42))
            ]
            model = VotingRegressor(models)
        
        # Train
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        return {
            'model': model,
            'scaler': self.scaler,
            'train_score': train_score,
            'test_score': test_score,
            'mse': mse,
            'mae': mae,
            'features': list(X.columns)
        }
    
    def save_model(self, model_data: Dict, symbol: str, model_type: str):
        """Save model to database"""
        model_id = f"{symbol}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with sqlite3.connect(self.db.models_db) as conn:
            conn.execute(
                "INSERT INTO models (model_id, symbol, model_type, model_data, metrics, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (model_id, symbol, model_type, 
                 pickle.dumps(model_data['model']),
                 json.dumps({
                     'train_score': model_data['train_score'],
                     'test_score': model_data['test_score'],
                     'mse': model_data['mse'],
                     'mae': model_data['mae']
                 }),
                 datetime.now())
            )
        
        return model_id

# ==================== MAIN ORCHESTRATOR ====================
class MLOrchestrator:
    """Main system orchestrator"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.fetcher = DataFetcher(self.db)
        self.engineer = FeatureEngineer()
        self.trainer = MLTrainer(self.db)
        self.models_cache = {}
    
    def train(self, symbol: str, model_type: str = "ensemble") -> Dict:
        """Complete training pipeline"""
        
        # Fetch data
        df = self.fetcher.fetch_data(symbol)
        
        # Calculate features
        df_features = self.engineer.calculate_features(df, symbol)
        
        # Prepare data
        feature_cols = [col for col in self.engineer.FEATURES if col in df_features.columns]
        X = df_features[feature_cols]
        y = df_features['Close'].shift(-1)  # Predict next day
        
        # Remove last row (no target)
        X = X[:-1]
        y = y[:-1]
        
        # Train model
        result = self.trainer.train_model(X, y, model_type)
        
        # Save model
        model_id = self.trainer.save_model(result, symbol, model_type)
        result['model_id'] = model_id
        
        # Cache model
        self.models_cache[symbol] = result
        
        return {
            'success': True,
            'model_id': model_id,
            'symbol': symbol,
            'model_type': model_type,
            'train_score': result['train_score'],
            'test_score': result['test_score'],
            'mse': result['mse'],
            'mae': result['mae']
        }
    
    def predict(self, symbol: str, days: int = 1) -> Dict:
        """Make prediction"""
        
        # Get model
        if symbol not in self.models_cache:
            # Try to train
            self.train(symbol)
        
        if symbol not in self.models_cache:
            raise HTTPException(status_code=404, detail=f"No model for {symbol}")
        
        model_data = self.models_cache[symbol]
        
        # Get latest data
        df = self.fetcher.fetch_data(symbol, period="1mo")
        df_features = self.engineer.calculate_features(df, symbol)
        
        # Get latest features
        feature_cols = model_data['features']
        X_latest = df_features[feature_cols].iloc[-1:].values
        
        # Scale
        X_scaled = model_data['scaler'].transform(X_latest)
        
        # Predict
        prediction = model_data['model'].predict(X_scaled)[0]
        current_price = df['Close'].iloc[-1]
        
        change = ((prediction - current_price) / current_price) * 100
        
        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'predicted_price': float(prediction),
            'change_percent': float(change),
            'direction': 'UP' if change > 0 else 'DOWN',
            'confidence': float(model_data['test_score']),
            'prediction_date': (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        }

# ==================== FastAPI APP ====================
app = FastAPI(title="ML Stock Prediction", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create orchestrator
orchestrator = MLOrchestrator()

# ==================== API ENDPOINTS ====================

@app.get("/")
def root():
    """System info"""
    return {
        "system": "ML Stock Prediction",
        "version": "3.0 FINAL",
        "status": "operational",
        "sentiment": "ENABLED" if SENTIMENT_AVAILABLE else "DISABLED"
    }

@app.get("/interface")
def interface():
    """Serve web interface"""
    if os.path.exists("interface.html"):
        return FileResponse("interface.html")
    return HTMLResponse("<h1>Interface not found</h1>")

class TrainRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    model_type: str = Field(default="ensemble", description="Model type")

@app.post("/api/train")
def train_model(request: TrainRequest):
    """Train model endpoint"""
    try:
        result = orchestrator.train(request.symbol, request.model_type)
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PredictRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    days: int = Field(default=1, description="Days ahead")

@app.post("/api/predict")
def predict(request: PredictRequest):
    """Prediction endpoint"""
    try:
        result = orchestrator.predict(request.symbol, request.days)
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
def list_models():
    """List available models"""
    with sqlite3.connect(orchestrator.db.models_db) as conn:
        cursor = conn.execute("SELECT model_id, symbol, model_type, created_at FROM models")
        models = [
            {"model_id": row[0], "symbol": row[1], "type": row[2], "created": row[3]}
            for row in cursor.fetchall()
        ]
    return models

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("Starting ML Stock Prediction System...")
    logger.info(f"Sentiment: {'ENABLED' if SENTIMENT_AVAILABLE else 'DISABLED'}")
    logger.info(f"XGBoost: {'AVAILABLE' if HAS_XGBOOST else 'NOT AVAILABLE'}")
    uvicorn.run(app, host="127.0.0.1", port=PORT)