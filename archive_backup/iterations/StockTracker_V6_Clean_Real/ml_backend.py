"""
ML Backend - Real Machine Learning Implementation
No fake data, no simulations - just real ML
"""

import os
import json
import logging
import sqlite3
import joblib
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
# Optional imports - will work without them
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    
try:
    import ta
    HAS_TA = True
except ImportError:
    HAS_TA = False

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ML Backend - Real Implementation", version="6.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "models.db"
MODEL_DIR = "saved_models"
os.makedirs(MODEL_DIR, exist_ok=True)

def init_database():
    """Initialize database for model tracking"""
    conn = sqlite3.connect(DB_PATH)
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
            features TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            predicted_price REAL,
            actual_price REAL,
            predicted_at TEXT NOT NULL,
            horizon_days INTEGER,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"
    days_back: int = 365

class PredictionRequest(BaseModel):
    symbol: str
    model_id: Optional[str] = None
    horizon: int = 1

def fetch_stock_data(symbol: str, days_back: int = 365) -> pd.DataFrame:
    """Fetch real stock data from Yahoo Finance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise

def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators as features"""
    # Price features
    df['returns'] = df['Close'].pct_change()
    df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Simple moving averages (manual calculation if ta not available)
    df['sma_5'] = df['Close'].rolling(window=5).mean()
    df['sma_20'] = df['Close'].rolling(window=20).mean()
    df['sma_50'] = df['Close'].rolling(window=50).mean()
    
    if HAS_TA:
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        df['bb_mid'] = bb.bollinger_mavg()
    else:
        # Simple RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Simple MACD
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp12 - exp26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        # Simple Bollinger Bands
        df['bb_mid'] = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        df['bb_high'] = df['bb_mid'] + (std * 2)
        df['bb_low'] = df['bb_mid'] - (std * 2)
    
    # Volume moving average
    df['volume_sma'] = df['Volume'].rolling(window=20).mean()
    
    # Remove NaN values
    df = df.dropna()
    
    return df

def train_model(symbol: str, model_type: str, days_back: int = 365) -> Dict:
    """Train a real ML model"""
    try:
        # Fetch real data
        logger.info(f"Fetching {days_back} days of data for {symbol}...")
        df = fetch_stock_data(symbol, days_back)
        
        # Calculate features
        logger.info("Calculating technical indicators...")
        df = calculate_features(df)
        
        # Prepare features and target
        feature_cols = ['Open', 'High', 'Low', 'Volume', 'returns', 'sma_5', 'sma_20', 
                       'rsi', 'macd', 'macd_signal', 'bb_high', 'bb_low']
        
        # Filter to available features
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        X = df[feature_cols].values
        y = df['Close'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Select and train model
        logger.info(f"Training {model_type} model...")
        
        if model_type == "random_forest":
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "xgboost":
            if HAS_XGBOOST:
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                # Fallback to GradientBoosting if XGBoost not available
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
        elif model_type == "gradient_boost":
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Train the model
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Save model
        model_id = f"{symbol}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.pkl")
        scaler_path = os.path.join(MODEL_DIR, f"{model_id}_scaler.pkl")
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO models (id, symbol, model_type, train_score, test_score, 
                              mae, rmse, created_at, file_path, features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, symbol, model_type, train_score, test_score, 
              mae, rmse, datetime.now().isoformat(), model_path, json.dumps(feature_cols)))
        conn.commit()
        conn.close()
        
        logger.info(f"Model trained successfully: {model_id}")
        
        return {
            "model_id": model_id,
            "symbol": symbol,
            "model_type": model_type,
            "train_score": train_score,
            "test_score": test_score,
            "mae": mae,
            "rmse": rmse,
            "feature_count": len(feature_cols),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "ML Backend - Real Implementation",
        "version": "6.0",
        "status": "operational",
        "models_available": ["random_forest", "xgboost", "gradient_boost"]
    }

@app.get("/api/ml/status")
async def get_status():
    """Get ML backend status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM models")
    model_count = cursor.fetchone()[0]
    conn.close()
    
    return {
        "status": "ready",
        "models_available": ["random_forest", "xgboost", "gradient_boost"],
        "trained_models": model_count,
        "training_supported": True,
        "prediction_supported": True
    }

@app.post("/api/train")
async def train(request: TrainingRequest):
    """Train a new model with real data"""
    result = train_model(request.symbol, request.model_type, request.days_back)
    return result

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Generate real prediction from trained model"""
    try:
        # Get latest model if not specified
        conn = sqlite3.connect(DB_PATH)
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
            raise HTTPException(status_code=404, detail="No model found")
        
        model_id = model_data[0]
        model_path = model_data[8]
        features = json.loads(model_data[9])
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        # Get latest data
        df = fetch_stock_data(request.symbol, days_back=60)
        df = calculate_features(df)
        
        # Prepare features
        X = df[features].iloc[-1:].values
        X_scaled = scaler.transform(X)
        
        # Predict
        prediction = model.predict(X_scaled)[0]
        current_price = df['Close'].iloc[-1]
        
        # Calculate confidence based on model performance
        confidence = model_data[4]  # test_score
        
        # Save prediction
        cursor.execute('''
            INSERT INTO predictions (model_id, symbol, predicted_price, 
                                   predicted_at, horizon_days)
            VALUES (?, ?, ?, ?, ?)
        ''', (model_id, request.symbol, prediction, 
              datetime.now().isoformat(), request.horizon))
        conn.commit()
        conn.close()
        
        return {
            "symbol": request.symbol,
            "current_price": float(current_price),
            "predicted_price": float(prediction),
            "change": float(prediction - current_price),
            "change_percent": float((prediction - current_price) / current_price * 100),
            "confidence": float(confidence),
            "model_id": model_id,
            "horizon_days": request.horizon
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """Get all trained models"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, symbol, model_type, train_score, test_score, 
               mae, created_at FROM models 
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
            "created_at": row[6]
        })
    
    conn.close()
    return {"models": models, "count": len(models)}

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get model file path
    cursor.execute("SELECT file_path FROM models WHERE id = ?", (model_id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Delete files
    try:
        os.remove(result[0])
        os.remove(result[0].replace('.pkl', '_scaler.pkl'))
    except:
        pass
    
    # Delete from database
    cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()
    
    return {"message": f"Model {model_id} deleted"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Backend on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)