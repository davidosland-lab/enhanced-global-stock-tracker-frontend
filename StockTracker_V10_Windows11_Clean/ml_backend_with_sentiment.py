"""
ML Backend with Sentiment Integration
Combines technical indicators with sentiment data from web scraper
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import traceback
import asyncio

# SSL Fix for Windows
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Try to import XGBoost
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = "models"
MODELS_DB = "ml_models.db"

os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect(MODELS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            model_type TEXT NOT NULL,
            train_score REAL,
            test_score REAL,
            mae REAL,
            rmse REAL,
            created_at TEXT,
            file_path TEXT,
            features TEXT,
            data_points INTEGER,
            uses_sentiment INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="ML Backend with Sentiment", version="11.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for data and sentiment
data_cache = {}
sentiment_cache = {}
CACHE_DURATION = 300  # 5 minutes

class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"
    days_back: int = 365
    include_sentiment: bool = True  # New parameter

class PredictionRequest(BaseModel):
    symbol: str
    model_id: Optional[str] = None
    horizon: int = 1
    include_sentiment: bool = True  # New parameter

def get_sentiment_data(symbol: str) -> Dict:
    """Get sentiment data from web scraper"""
    try:
        # Check cache first
        cache_key = f"{symbol}_sentiment"
        if cache_key in sentiment_cache:
            cached_time, data = sentiment_cache[cache_key]
            if (datetime.now() - cached_time).seconds < CACHE_DURATION:
                logger.info(f"Using cached sentiment for {symbol}")
                return data
        
        # Call web scraper API
        response = requests.post(
            "http://localhost:8006/scrape",
            json={
                "symbol": symbol,
                "sources": ["yahoo", "finviz", "reddit", "google"],
                "analyze_sentiment": True
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract sentiment metrics
            sentiment_results = data.get('sentiment_results', [])
            
            if sentiment_results:
                # Calculate sentiment scores
                positive = sum(1 for s in sentiment_results if s.get('sentiment') == 'positive')
                negative = sum(1 for s in sentiment_results if s.get('sentiment') == 'negative')
                neutral = sum(1 for s in sentiment_results if s.get('sentiment') == 'neutral')
                total = len(sentiment_results)
                
                avg_score = data.get('average_score', 0.0)
                
                sentiment_data = {
                    'sentiment_score': avg_score,
                    'positive_ratio': positive / total if total > 0 else 0,
                    'negative_ratio': negative / total if total > 0 else 0,
                    'neutral_ratio': neutral / total if total > 0 else 0,
                    'article_count': total,
                    'aggregate_sentiment': data.get('aggregate_sentiment', 'neutral')
                }
                
                # Cache the result
                sentiment_cache[cache_key] = (datetime.now(), sentiment_data)
                
                return sentiment_data
            
        logger.warning(f"Could not get sentiment for {symbol}, using defaults")
        
    except Exception as e:
        logger.error(f"Error fetching sentiment: {e}")
    
    # Return default neutral sentiment
    return {
        'sentiment_score': 0.0,
        'positive_ratio': 0.33,
        'negative_ratio': 0.33,
        'neutral_ratio': 0.34,
        'article_count': 0,
        'aggregate_sentiment': 'neutral'
    }

def fetch_real_stock_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """Fetch real stock data from Yahoo Finance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        # Handle multi-level columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cannot fetch data: {str(e)}")

def create_features_with_sentiment(df: pd.DataFrame, symbol: str, include_sentiment: bool = True) -> pd.DataFrame:
    """Create technical features and add sentiment if requested"""
    try:
        # Technical features (same as before)
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        df['sma_5'] = df['Close'].rolling(window=5).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        
        # Price ratios
        df['high_low_ratio'] = df['High'] / df['Low']
        df['close_open_ratio'] = df['Close'] / df['Open']
        
        # Volume features
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = np.where(
            df['volume_sma'] > 0,
            df['Volume'] / df['volume_sma'],
            1.0
        )
        
        # Volatility
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = np.where(loss != 0, gain / loss, 0)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Add sentiment features if requested
        if include_sentiment:
            logger.info(f"Fetching sentiment data for {symbol}...")
            sentiment_data = get_sentiment_data(symbol)
            
            # Add sentiment features to dataframe
            df['sentiment_score'] = sentiment_data['sentiment_score']
            df['sentiment_positive'] = sentiment_data['positive_ratio']
            df['sentiment_negative'] = sentiment_data['negative_ratio']
            df['sentiment_neutral'] = sentiment_data['neutral_ratio']
            df['sentiment_articles'] = sentiment_data['article_count']
            
            # Add sentiment trend (rolling average)
            df['sentiment_ma_3'] = df['sentiment_score'].rolling(window=3, min_periods=1).mean()
            df['sentiment_ma_7'] = df['sentiment_score'].rolling(window=7, min_periods=1).mean()
            
            logger.info(f"Added sentiment features: score={sentiment_data['sentiment_score']:.3f}, articles={sentiment_data['article_count']}")
        
        # Remove NaN rows
        df = df.dropna()
        
        return df
        
    except Exception as e:
        logger.error(f"Feature creation failed: {str(e)}")
        raise

def train_model_with_sentiment(symbol: str, model_type: str, days_back: int, include_sentiment: bool = True) -> Dict:
    """Train model with technical and sentiment features"""
    try:
        start_time = datetime.now()
        
        # Fetch data
        df = fetch_real_stock_data(symbol, days_back)
        
        # Create features with sentiment
        df = create_features_with_sentiment(df, symbol, include_sentiment)
        
        # Select features
        feature_cols = [
            'returns', 'log_returns', 'sma_5', 'sma_20', 'sma_50',
            'high_low_ratio', 'close_open_ratio', 'volume_ratio',
            'volatility', 'rsi', 'macd', 'macd_signal',
            'bb_width', 'bb_position'
        ]
        
        # Add sentiment features if included
        if include_sentiment:
            sentiment_features = [
                'sentiment_score', 'sentiment_positive', 'sentiment_negative',
                'sentiment_neutral', 'sentiment_ma_3', 'sentiment_ma_7'
            ]
            # Only add sentiment features that exist in the dataframe
            for feat in sentiment_features:
                if feat in df.columns:
                    feature_cols.append(feat)
        
        # Filter available features
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features].values
        y = df['Close'].values
        
        # Handle NaN/inf
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        logger.info(f"Training with {len(X)} samples and {len(available_features)} features")
        if include_sentiment:
            logger.info(f"Including sentiment features in model")
        
        # Train/test split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == "random_forest":
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boost":
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == "xgboost" and HAS_XGBOOST:
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Feature importance (for tree-based models)
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            for feat, importance in zip(available_features, model.feature_importances_):
                feature_importance[feat] = float(importance)
        
        # Save model
        model_id = f"{symbol}_{model_type}_{'with_sentiment' if include_sentiment else 'no_sentiment'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")
        scaler_path = os.path.join(MODEL_DIR, f"{model_id}_scaler.pkl")
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Save to database
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO models (id, symbol, model_type, train_score, test_score,
                              mae, rmse, created_at, file_path, features, data_points, uses_sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, symbol, model_type, train_score, test_score,
              mae, rmse, datetime.now().isoformat(), model_path,
              json.dumps(available_features), len(X), 1 if include_sentiment else 0))
        conn.commit()
        conn.close()
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "model_id": model_id,
            "symbol": symbol,
            "model_type": model_type,
            "train_score": float(train_score),
            "test_score": float(test_score),
            "mae": float(mae),
            "rmse": float(rmse),
            "data_points": len(X),
            "feature_count": len(available_features),
            "uses_sentiment": include_sentiment,
            "sentiment_features": [f for f in available_features if 'sentiment' in f],
            "feature_importance": feature_importance,
            "training_time": training_time,
            "status": "success",
            "message": f"Model trained with {'sentiment and ' if include_sentiment else ''}technical features"
        }
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "service": "ML Backend with Sentiment Integration",
        "version": "11.0",
        "status": "running",
        "features": [
            "Technical indicators",
            "Sentiment analysis integration",
            "Web scraper connection",
            "RandomForest, GradientBoost, XGBoost",
            "Feature importance analysis"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ml_backend_sentiment", "timestamp": datetime.now().isoformat()}

@app.get("/api/ml/status")
async def ml_status():
    """Get ML system status with sentiment integration info"""
    try:
        # Check if web scraper is available
        scraper_available = False
        try:
            response = requests.get("http://localhost:8006/health", timeout=2)
            scraper_available = response.status_code == 200
        except:
            pass
        
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM models")
        model_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM models WHERE uses_sentiment = 1")
        sentiment_model_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        conn.close()
        
        return {
            "status": "ready",
            "trained_models": model_count,
            "sentiment_models": sentiment_model_count,
            "scraper_connected": scraper_available,
            "sentiment_cache_size": len(sentiment_cache),
            "supported_models": ["random_forest", "gradient_boost", "xgboost" if HAS_XGBOOST else "gradient_boost_alt"]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/train")
async def train(request: TrainingRequest):
    """Train model with optional sentiment integration"""
    logger.info(f"Training request for {request.symbol} with sentiment={request.include_sentiment}")
    return train_model_with_sentiment(
        request.symbol, 
        request.model_type, 
        request.days_back,
        request.include_sentiment
    )

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Generate prediction with optional sentiment data"""
    try:
        # Get model from database
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        
        if request.model_id:
            cursor.execute("SELECT * FROM models WHERE id = ?", (request.model_id,))
        else:
            # Prefer models with sentiment if requested
            if request.include_sentiment:
                cursor.execute(
                    "SELECT * FROM models WHERE symbol = ? AND uses_sentiment = 1 ORDER BY created_at DESC LIMIT 1",
                    (request.symbol,)
                )
                model_data = cursor.fetchone()
                
                if not model_data:
                    # Fall back to non-sentiment model
                    cursor.execute(
                        "SELECT * FROM models WHERE symbol = ? ORDER BY created_at DESC LIMIT 1",
                        (request.symbol,)
                    )
                    model_data = cursor.fetchone()
            else:
                cursor.execute(
                    "SELECT * FROM models WHERE symbol = ? ORDER BY created_at DESC LIMIT 1",
                    (request.symbol,)
                )
                model_data = cursor.fetchone()
        
        if not model_data:
            conn.close()
            # Auto-train new model
            logger.info(f"No model found for {request.symbol}, auto-training...")
            train_result = train_model_with_sentiment(
                request.symbol, "random_forest", 365, request.include_sentiment
            )
            return {
                "message": "Model auto-trained",
                "model_id": train_result['model_id'],
                "train_score": train_result['train_score'],
                "prediction": "Please retry prediction with new model"
            }
        
        model_id = model_data[0]
        model_path = model_data[8]
        features = json.loads(model_data[9])
        uses_sentiment = model_data[11] if len(model_data) > 11 else 0
        
        conn.close()
        
        # Load model
        model = joblib.load(model_path)
        scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        # Get current data
        df = fetch_real_stock_data(request.symbol, days=120)
        df = create_features_with_sentiment(df, request.symbol, uses_sentiment)
        
        # Prepare features
        available_features = [f for f in features if f in df.columns]
        X = df[available_features].iloc[-1:].values
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        X_scaled = scaler.transform(X)
        
        # Make prediction
        prediction = model.predict(X_scaled)[0]
        current_price = float(df['Close'].iloc[-1])
        
        # Get current sentiment if model uses it
        sentiment_info = {}
        if uses_sentiment:
            sentiment_data = get_sentiment_data(request.symbol)
            sentiment_info = {
                "current_sentiment": sentiment_data['aggregate_sentiment'],
                "sentiment_score": sentiment_data['sentiment_score'],
                "article_count": sentiment_data['article_count']
            }
        
        # Adjust prediction based on horizon
        horizon_factor = 1 + (request.horizon - 1) * 0.002
        adjusted_prediction = prediction * horizon_factor
        
        return {
            "symbol": request.symbol,
            "current_price": current_price,
            "predicted_price": float(adjusted_prediction),
            "change": float(adjusted_prediction - current_price),
            "change_percent": float((adjusted_prediction - current_price) / current_price * 100),
            "confidence": float(model_data[4]),  # test_score
            "model_id": model_id,
            "uses_sentiment": bool(uses_sentiment),
            "sentiment_info": sentiment_info,
            "horizon_days": request.horizon,
            "features_used": len(available_features),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/models")
async def list_models():
    """List all trained models with sentiment info"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, symbol, model_type, train_score, test_score, mae, rmse, created_at, uses_sentiment 
            FROM models 
            ORDER BY created_at DESC
        """)
        models = cursor.fetchall()
        conn.close()
        
        return {
            "models": [
                {
                    "id": m[0],
                    "symbol": m[1],
                    "model_type": m[2],
                    "train_score": m[3],
                    "test_score": m[4],
                    "mae": m[5],
                    "rmse": m[6],
                    "created_at": m[7],
                    "uses_sentiment": bool(m[8]) if len(m) > 8 else False,
                    "label": f"{m[1]} - {m[2]} {'[+Sentiment]' if (len(m) > 8 and m[8]) else ''}"
                }
                for m in models
            ],
            "count": len(models)
        }
    except Exception as e:
        return {"models": [], "count": 0, "error": str(e)}

@app.get("/api/sentiment/{symbol}")
async def get_current_sentiment(symbol: str):
    """Get current sentiment for a symbol"""
    sentiment_data = get_sentiment_data(symbol)
    return {
        "symbol": symbol,
        "sentiment_data": sentiment_data,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("ML Backend with Sentiment Integration")
    print("=" * 60)
    print("Features:")
    print("✓ Technical indicators (RSI, MACD, Bollinger Bands, etc.)")
    print("✓ Sentiment analysis from web scraper")
    print("✓ Combined prediction model")
    print("✓ Feature importance analysis")
    print()
    print("Starting on port 8002...")
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except Exception as e:
        print(f"Failed to start: {e}")