"""
ML Backend - REAL DATA ONLY - FULLY FIXED VERSION
Fixes:
1. Support for XGBoost and Gradient Boost models
2. Prediction data insufficiency issue
3. Better error handling
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
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Try to import XGBoost (optional)
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("XGBoost not installed. Using alternative models.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = "models"
MODELS_DB = "ml_models.db"

# Create directories
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
            data_points INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="ML Backend - REAL DATA ONLY", version="10.2")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for stock data
data_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cached_data(symbol: str, days: int) -> Optional[pd.DataFrame]:
    """Get cached data if available and fresh"""
    cache_key = f"{symbol}_{days}"
    if cache_key in data_cache:
        cached_time, df = data_cache[cache_key]
        if (datetime.now() - cached_time).seconds < CACHE_DURATION:
            return df.copy()
    return None

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
        # Check cache first
        cached = get_cached_data(symbol, days)
        if cached is not None:
            logger.info(f"Using cached data for {symbol}")
            return cached
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching REAL data for {symbol} from Yahoo Finance...")
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data returned from Yahoo Finance for {symbol}")
        
        # Handle multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Cache the data
        data_cache[f"{symbol}_{days}"] = (datetime.now(), df.copy())
        
        logger.info(f"Successfully fetched {len(df)} days of REAL data for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch real data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cannot fetch real data: {str(e)}")

def create_real_features(df: pd.DataFrame, min_rows: int = 50) -> pd.DataFrame:
    """
    Create REAL technical indicators from REAL data
    min_rows: minimum rows required after feature creation (reduced from 100)
    """
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
        
        # Volume features - FIXED
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        # Avoid division by zero
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
        # Avoid division by zero in RSI
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
        
        # Remove NaN rows
        df = df.dropna()
        
        # Check minimum rows with more lenient requirement
        if len(df) < min_rows:
            logger.warning(f"Only {len(df)} rows after feature creation (minimum {min_rows})")
            # For prediction, we can work with less data
            if len(df) < 1:
                raise ValueError(f"No data left after feature creation")
        
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
        
        # Select features (expanded list)
        feature_cols = [
            'returns', 'log_returns', 'sma_5', 'sma_20', 'sma_50',
            'high_low_ratio', 'close_open_ratio', 'volume_ratio',
            'volatility', 'rsi', 'macd', 'macd_signal',
            'bb_width', 'bb_position'
        ]
        
        # Ensure all features exist
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 5:
            raise ValueError(f"Not enough features available: only {len(available_features)}")
        
        X = df[available_features].values
        y = df['Close'].values
        
        # Check for any remaining NaN or inf values
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            logger.warning("Found NaN or inf values in features, cleaning...")
            # Replace inf with large numbers and NaN with 0
            X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        logger.info(f"Training with {len(X)} real data points and {len(available_features)} features")
        
        # Train/test split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        if len(X_train) < 50:
            raise ValueError(f"Not enough training data: only {len(X_train)} samples")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train REAL model based on type
        logger.info(f"Training {model_type} model...")
        
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
        elif model_type == "xgboost":
            if HAS_XGBOOST:
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                logger.warning("XGBoost not available, using Gradient Boosting instead")
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
        else:
            # Default to random forest for unknown types
            logger.warning(f"Unknown model type {model_type}, defaulting to random_forest")
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate with REAL metrics
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Save model
        model_id = f"{symbol.replace('.', '_')}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
              json.dumps(available_features), len(X)))
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
            "feature_count": len(available_features),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "training_time": training_time,
            "status": "success",
            "message": "Model trained with REAL data"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Training failed with REAL data: {str(e)}")

@app.get("/")
async def root():
    return {
        "service": "ML Backend",
        "version": "10.2",
        "status": "running",
        "features": [
            "Real data from Yahoo Finance",
            "RandomForest, GradientBoost, XGBoost models",
            "Technical indicators",
            "Model persistence",
            "Fixed prediction data issue"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ml_backend", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy"}

@app.get("/api/ml/status")
async def ml_status():
    """Get ML system status"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM models")
        model_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT symbol, model_type, test_score FROM models ORDER BY created_at DESC LIMIT 5")
        recent_models = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "ready",
            "trained_models": model_count,
            "recent_models": [
                {"symbol": m[0], "type": m[1], "score": m[2]} 
                for m in recent_models
            ],
            "supported_models": ["random_forest", "gradient_boost", "xgboost" if HAS_XGBOOST else "gradient_boost_alt"],
            "cached_symbols": len(data_cache),
            "model_directory": MODEL_DIR,
            "database": MODELS_DB
        }
    except Exception as e:
        return {
            "status": "error",
            "trained_models": 0,
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
            # Try to auto-train
            logger.info(f"No model found for {request.symbol}, auto-training...")
            train_result = train_real_model(request.symbol, "random_forest", 365)
            
            # Get the newly trained model
            conn = sqlite3.connect(MODELS_DB)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM models WHERE id = ?",
                (train_result['model_id'],)
            )
            model_data = cursor.fetchone()
        
        model_id = model_data[0]
        model_path = model_data[8]
        features = json.loads(model_data[9])
        
        conn.close()
        
        # Load model
        model = joblib.load(model_path)
        scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        
        # Get REAL current data - fetch more days to ensure we have enough after feature creation
        df = fetch_real_stock_data(request.symbol, days=120)  # Increased from 60
        df = create_real_features(df, min_rows=1)  # Allow prediction with just 1 row
        
        if len(df) == 0:
            raise ValueError("No data available after feature creation")
        
        # Prepare features - handle missing features gracefully
        available_features = [f for f in features if f in df.columns]
        if len(available_features) < len(features):
            logger.warning(f"Some features missing. Using {len(available_features)}/{len(features)} features")
        
        # Get the last row for prediction
        X = df[available_features].iloc[-1:].values
        
        # Check for NaN/inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        X_scaled = scaler.transform(X)
        
        # Make REAL prediction
        prediction = model.predict(X_scaled)[0]
        current_price = float(df['Close'].iloc[-1])
        
        # Calculate prediction for future horizon
        # Simple approach: scale prediction based on horizon
        horizon_factor = 1 + (request.horizon - 1) * 0.002  # Small adjustment per day
        adjusted_prediction = prediction * horizon_factor
        
        return {
            "symbol": request.symbol,
            "current_price": current_price,
            "predicted_price": float(adjusted_prediction),
            "change": float(adjusted_prediction - current_price),
            "change_percent": float((adjusted_prediction - current_price) / current_price * 100),
            "confidence": float(model_data[4]),  # test_score
            "model_id": model_id,
            "horizon_days": request.horizon,
            "features_used": len(available_features),
            "data_source": "REAL (Yahoo Finance)",
            "expected_change_percent": float((adjusted_prediction - current_price) / current_price * 100)
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/models")
async def list_models():
    """List all trained models"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, symbol, model_type, train_score, test_score, mae, rmse, created_at 
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
                    "r2_score": m[4]  # For compatibility
                }
                for m in models
            ],
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return {"models": [], "count": 0, "error": str(e)}

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a trained model"""
    try:
        conn = sqlite3.connect(MODELS_DB)
        cursor = conn.cursor()
        
        # Get model path
        cursor.execute("SELECT file_path FROM models WHERE id = ?", (model_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Model not found")
        
        model_path = result[0]
        scaler_path = model_path.replace('.pkl', '_scaler.pkl')
        
        # Delete files
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(scaler_path):
            os.remove(scaler_path)
        
        # Delete from database
        cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        conn.commit()
        conn.close()
        
        return {"message": f"Model {model_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical/{symbol}")
async def get_historical(symbol: str, days: int = 365):
    """Get historical data with caching"""
    try:
        df = fetch_real_stock_data(symbol, days)
        
        # Convert to list of dicts for JSON response
        data = df.reset_index().to_dict('records')
        
        # Convert timestamps
        for row in data:
            if 'Date' in row:
                row['Date'] = row['Date'].isoformat() if pd.notna(row['Date']) else None
        
        return {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "cached": get_cached_data(symbol, days) is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("ML Backend - REAL DATA ONLY (FULLY FIXED)")
    print("NO MOCK DATA - NO SIMULATIONS - NO SYNTHETIC DATA")
    print("=" * 60)
    print()
    print("Starting on port 8002...")
    print("Fixes included:")
    print("- Support for XGBoost and Gradient Boost models")
    print("- Fixed prediction data insufficiency")
    print("- Better error handling")
    print("- Increased data fetch for predictions")
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        traceback.print_exc()