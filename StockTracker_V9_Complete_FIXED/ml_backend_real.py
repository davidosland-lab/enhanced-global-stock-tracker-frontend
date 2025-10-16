"""
ML Backend - REAL DATA ONLY - NO MOCK DATA
If data cannot be fetched, it returns an error - NO FAKE DATA
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import traceback

# SSL Fix for Windows
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ML Backend - REAL DATA ONLY", version="10.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database and directories
MODELS_DB = "models_real.db"
CACHE_DB = "cache_real.db"
MODEL_DIR = "saved_models_real"
os.makedirs(MODEL_DIR, exist_ok=True)

def init_databases():
    """Initialize databases for REAL data only"""
    # Models database
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
            created_at TEXT NOT NULL,
            file_path TEXT,
            features TEXT,
            data_points INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    
    # Cache database
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_cache (
            symbol TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    
    logger.info("Databases initialized")

init_databases()

class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"
    days_back: int = 365

class PredictionRequest(BaseModel):
    symbol: str
    model_id: Optional[str] = None
    horizon: int = 1

def fetch_real_stock_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """
    Fetch REAL stock data - NO MOCK DATA
    If it fails, it raises an error - doesn't return fake data
    """
    try:
        logger.info(f"Fetching REAL data for {symbol}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Method 1: Using download function
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, threads=False)
        
        if df.empty:
            # Method 2: Using Ticker object
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No real data available for {symbol}. Check if symbol exists.")
        
        logger.info(f"Successfully fetched {len(df)} days of REAL data for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch real data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot fetch real data for {symbol}. Error: {str(e)}. Please check the symbol and try again."
        )

def create_real_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create features from REAL data only"""
    try:
        # Basic features
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
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Volatility
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Remove NaN rows
        df = df.dropna()
        
        if len(df) < 100:
            raise ValueError("Insufficient data after feature creation")
        
        return df
        
    except Exception as e:
        logger.error(f"Feature creation failed: {str(e)}")
        raise

def train_real_model(symbol: str, model_type: str, days_back: int) -> Dict:
    """Train model with REAL data only - NO MOCK DATA"""
    try:
        start_time = datetime.now()
        
        # Fetch REAL data
        df = fetch_real_stock_data(symbol, days_back)
        
        # Create REAL features
        df = create_real_features(df)
        
        # Select features
        feature_cols = [
            'returns', 'log_returns', 'sma_5', 'sma_20', 'sma_50',
            'high_low_ratio', 'close_open_ratio', 'volume_ratio',
            'volatility', 'rsi'
        ]
        
        # Ensure all features exist
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        if len(feature_cols) < 5:
            raise ValueError("Not enough features available")
        
        X = df[feature_cols].values
        y = df['Close'].values
        
        logger.info(f"Training with {len(X)} real data points and {len(feature_cols)} features")
        
        # Train/test split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train REAL model
        if model_type == "random_forest":
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate with REAL metrics
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Save model
        model_id = f"{symbol}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")
        scaler_path = os.path.join(MODEL_DIR, f"{model_id}_scaler.pkl")
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Save to database
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO models (id, symbol, model_type, train_score, test_score,
                              mae, rmse, created_at, file_path, features, data_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, symbol, model_type, train_score, test_score,
              mae, rmse, datetime.now().isoformat(), model_path,
              json.dumps(feature_cols), len(X)))
        conn.commit()
        conn.close()
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Successfully trained REAL model in {training_time:.1f} seconds")
        
        return {
            "model_id": model_id,
            "symbol": symbol,
            "model_type": model_type,
            "train_score": float(train_score),
            "test_score": float(test_score),
            "mae": float(mae),
            "rmse": float(rmse),
            "data_points": len(X),
            "training_time": training_time,
            "status": "success",
            "message": "Model trained with REAL data"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Training failed with REAL data: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "service": "ML Backend - REAL DATA ONLY",
        "version": "10.0",
        "status": "operational",
        "mock_data": "NEVER",
        "real_data": "ALWAYS",
        "message": "This backend uses ONLY real data from Yahoo Finance"
    }

@app.get("/api/ml/status")
async def get_status():
    """Get ML backend status"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM models")
        model_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "ready",
            "models_available": ["random_forest"],
            "trained_models": model_count,
            "data_source": "Yahoo Finance (REAL)",
            "mock_data": False,
            "training_supported": True,
            "prediction_supported": True
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/train")
async def train(request: TrainingRequest):
    """Train model with REAL data only"""
    logger.info(f"Training request for {request.symbol}")
    return train_real_model(request.symbol, request.model_type, request.days_back)

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Generate prediction from REAL model with REAL data"""
    try:
        # Get model
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        
        if request.model_id:
            cursor.execute("SELECT * FROM models WHERE id = ?", (request.model_id,))
        else:
            cursor.execute(
                "SELECT * FROM models WHERE symbol = ? ORDER BY created_at DESC LIMIT 1",
                (request.symbol,)
            )
        
        model_data = cursor.fetchone()
        
        if not model_data:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"No trained model for {request.symbol}. Train a model first."
            )
        
        model_id = model_data[0]
        model_path = model_data[8]
        features = json.loads(model_data[9])
        
        conn.close()
        
        # Load model
        model = joblib.load(model_path)
        scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        # Get REAL current data
        df = fetch_real_stock_data(request.symbol, days=60)
        df = create_real_features(df)
        
        # Prepare features
        X = df[features].iloc[-1:].values
        X_scaled = scaler.transform(X)
        
        # Make REAL prediction
        prediction = model.predict(X_scaled)[0]
        current_price = float(df['Close'].iloc[-1])
        
        return {
            "symbol": request.symbol,
            "current_price": current_price,
            "predicted_price": float(prediction),
            "change": float(prediction - current_price),
            "change_percent": float((prediction - current_price) / current_price * 100),
            "confidence": float(model_data[4]),  # test_score
            "model_id": model_id,
            "horizon_days": request.horizon,
            "data_source": "REAL"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/api/models")
async def get_models():
    """Get all trained models"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, model_type, train_score, test_score,
                   mae, rmse, created_at, data_points
            FROM models
            ORDER BY created_at DESC
        ''')
        
        models = []
        for row in cursor.fetchall():
            models.append({
                "id": row[0],
                "symbol": row[1],
                "model_type": row[2],
                "train_score": row[3],
                "test_score": row[4],
                "mae": row[5],
                "rmse": row[6],
                "created_at": row[7],
                "data_points": row[8]
            })
        
        conn.close()
        return {"models": models, "count": len(models)}
        
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        return {"models": [], "count": 0, "error": str(e)}

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path FROM models WHERE id = ?", (model_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Delete files
        try:
            os.remove(result[0])
            os.remove(result[0].replace('.pkl', '_scaler.pkl'))
        except:
            pass
        
        cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        conn.commit()
        conn.close()
        
        return {"message": f"Model {model_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("ML Backend - REAL DATA ONLY")
    print("NO MOCK DATA - NO SIMULATIONS - NO SYNTHETIC DATA")
    print("=" * 60)
    print()
    print("Starting on port 8003...")
    print("If this crashes, run diagnose_crash.py to see why")
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        print("\nTry running: python diagnose_crash.py")
        traceback.print_exc()