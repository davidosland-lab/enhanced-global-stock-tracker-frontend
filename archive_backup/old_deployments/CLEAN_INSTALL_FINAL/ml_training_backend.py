#!/usr/bin/env python3
"""
ML Training Backend for Stock Prediction
Real neural network training with TensorFlow/Keras
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
import yfinance as yf

# ML Libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Web framework
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

app = FastAPI(title="ML Training Backend", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for models and training status
MODELS_DIR = "trained_models"
os.makedirs(MODELS_DIR, exist_ok=True)

trained_models = {}
training_status = {}
training_history = {}

# Pydantic models
class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "lstm"  # lstm, gru, cnn_lstm, transformer
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    sequence_length: int = 60
    training_period: str = "1y"
    features: List[str] = ["close", "volume", "high", "low", "open"]

class PredictionRequest(BaseModel):
    symbol: str
    model_id: Optional[str] = None
    days_ahead: int = 5

class ModelInfo(BaseModel):
    model_id: str
    symbol: str
    model_type: str
    trained_at: str
    metrics: Dict[str, float]
    status: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ml-training-backend",
        "timestamp": datetime.now().isoformat(),
        "tensorflow_version": tf.__version__
    }

# Data preparation functions
def prepare_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetch and prepare stock data for training"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Add technical indicators
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = calculate_rsi(df['Close'])
        df['MACD'] = calculate_macd(df['Close'])
        
        # Add volume ratio
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Add price change
        df['Price_Change'] = df['Close'].pct_change()
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info(f"Prepared {len(df)} data points for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error preparing data for {symbol}: {e}")
        raise

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    return macd

def create_sequences(data, seq_length=60):
    """Create sequences for LSTM training"""
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i])
        y.append(data[i, 0])  # Predict closing price
    return np.array(X), np.array(y)

# Model architectures
def build_lstm_model(input_shape, units=[128, 64, 32], dropout=0.2, learning_rate=0.001):
    """Build LSTM model"""
    model = keras.Sequential([
        layers.LSTM(units[0], return_sequences=True, input_shape=input_shape),
        layers.Dropout(dropout),
        layers.LSTM(units[1], return_sequences=True),
        layers.Dropout(dropout),
        layers.LSTM(units[2], return_sequences=False),
        layers.Dropout(dropout),
        layers.Dense(25),
        layers.Dense(1)
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=['mae']
    )
    
    return model

def build_gru_model(input_shape, units=[100, 50, 25], dropout=0.2, learning_rate=0.001):
    """Build GRU model"""
    model = keras.Sequential([
        layers.GRU(units[0], return_sequences=True, input_shape=input_shape),
        layers.Dropout(dropout),
        layers.GRU(units[1], return_sequences=True),
        layers.Dropout(dropout),
        layers.GRU(units[2]),
        layers.Dropout(dropout),
        layers.Dense(25),
        layers.Dense(1)
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=['mae']
    )
    
    return model

def build_cnn_lstm_model(input_shape, filters=64, kernel_size=3, lstm_units=50, learning_rate=0.001):
    """Build CNN-LSTM hybrid model"""
    model = keras.Sequential([
        layers.Conv1D(filters=filters, kernel_size=kernel_size, activation='relu', input_shape=input_shape),
        layers.MaxPooling1D(pool_size=2),
        layers.LSTM(lstm_units, return_sequences=True),
        layers.LSTM(lstm_units),
        layers.Dropout(0.2),
        layers.Dense(25),
        layers.Dense(1)
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=['mae']
    )
    
    return model

def build_transformer_model(input_shape, d_model=64, num_heads=4, ff_dim=128, learning_rate=0.001):
    """Build Transformer model for time series"""
    inputs = keras.Input(shape=input_shape)
    
    # Positional encoding
    positions = tf.range(start=0, limit=input_shape[0], delta=1)
    position_embeddings = layers.Embedding(input_dim=input_shape[0], output_dim=d_model)(positions)
    
    # Add positional encoding
    x = layers.Dense(d_model)(inputs)
    x = x + position_embeddings
    
    # Transformer block
    attention = layers.MultiHeadAttention(num_heads=num_heads, key_dim=d_model)(x, x)
    attention = layers.Dropout(0.1)(attention)
    x = layers.LayerNormalization(epsilon=1e-6)(x + attention)
    
    # Feed forward
    ff = layers.Dense(ff_dim, activation="relu")(x)
    ff = layers.Dense(d_model)(ff)
    ff = layers.Dropout(0.1)(ff)
    x = layers.LayerNormalization(epsilon=1e-6)(x + ff)
    
    # Global pooling and output
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(25, activation="relu")(x)
    outputs = layers.Dense(1)(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=['mae']
    )
    
    return model

# Training callback
class TrainingCallback(callbacks.Callback):
    def __init__(self, model_id):
        self.model_id = model_id
        
    def on_epoch_end(self, epoch, logs=None):
        if self.model_id in training_status:
            training_status[self.model_id]["current_epoch"] = epoch + 1
            training_status[self.model_id]["loss"] = float(logs.get('loss', 0))
            training_status[self.model_id]["mae"] = float(logs.get('mae', 0))
            training_status[self.model_id]["val_loss"] = float(logs.get('val_loss', 0))
            training_status[self.model_id]["val_mae"] = float(logs.get('val_mae', 0))
            
            # Store history
            if self.model_id not in training_history:
                training_history[self.model_id] = {
                    "loss": [], "mae": [], "val_loss": [], "val_mae": []
                }
            training_history[self.model_id]["loss"].append(float(logs.get('loss', 0)))
            training_history[self.model_id]["mae"].append(float(logs.get('mae', 0)))
            training_history[self.model_id]["val_loss"].append(float(logs.get('val_loss', 0)))
            training_history[self.model_id]["val_mae"].append(float(logs.get('val_mae', 0)))

# Background training task
async def train_model_task(model_id: str, request: TrainingRequest):
    """Background task for model training"""
    try:
        training_status[model_id]["status"] = "preparing_data"
        
        # Prepare data
        df = prepare_stock_data(request.symbol, request.training_period)
        
        # Select features
        feature_columns = [col for col in request.features if col.lower() in df.columns.str.lower()]
        if not feature_columns:
            feature_columns = ['Close', 'Volume', 'High', 'Low', 'Open']
        
        # Scale data
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(df[feature_columns].values)
        
        # Create sequences
        X, y = create_sequences(scaled_data, request.sequence_length)
        
        # Split data
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        training_status[model_id]["status"] = "building_model"
        training_status[model_id]["total_samples"] = len(X)
        
        # Build model based on type
        input_shape = (X_train.shape[1], X_train.shape[2])
        
        if request.model_type == "lstm":
            model = build_lstm_model(input_shape, learning_rate=request.learning_rate)
        elif request.model_type == "gru":
            model = build_gru_model(input_shape, learning_rate=request.learning_rate)
        elif request.model_type == "cnn_lstm":
            model = build_cnn_lstm_model(input_shape, learning_rate=request.learning_rate)
        elif request.model_type == "transformer":
            model = build_transformer_model(input_shape, learning_rate=request.learning_rate)
        else:
            model = build_lstm_model(input_shape, learning_rate=request.learning_rate)
        
        training_status[model_id]["status"] = "training"
        training_status[model_id]["total_epochs"] = request.epochs
        
        # Training callbacks
        early_stopping = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        training_callback = TrainingCallback(model_id)
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=request.epochs,
            batch_size=request.batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping, training_callback],
            verbose=0
        )
        
        # Evaluate model
        training_status[model_id]["status"] = "evaluating"
        
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(
            np.concatenate([predictions, np.zeros((len(predictions), len(feature_columns)-1))], axis=1)
        )[:, 0]
        
        y_test_rescaled = scaler.inverse_transform(
            np.concatenate([y_test.reshape(-1, 1), np.zeros((len(y_test), len(feature_columns)-1))], axis=1)
        )[:, 0]
        
        # Calculate metrics
        mae = mean_absolute_error(y_test_rescaled, predictions)
        rmse = np.sqrt(mean_squared_error(y_test_rescaled, predictions))
        r2 = r2_score(y_test_rescaled, predictions)
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f"{model_id}.h5")
        model.save(model_path)
        
        # Save scaler
        scaler_path = os.path.join(MODELS_DIR, f"{model_id}_scaler.npy")
        np.save(scaler_path, scaler.scale_)
        
        # Store model info
        trained_models[model_id] = {
            "model": model,
            "scaler": scaler,
            "symbol": request.symbol,
            "model_type": request.model_type,
            "trained_at": datetime.now().isoformat(),
            "metrics": {
                "mae": float(mae),
                "rmse": float(rmse),
                "r2": float(r2),
                "final_loss": float(history.history['loss'][-1]),
                "final_val_loss": float(history.history['val_loss'][-1])
            },
            "input_shape": input_shape,
            "feature_columns": feature_columns,
            "sequence_length": request.sequence_length
        }
        
        training_status[model_id]["status"] = "completed"
        training_status[model_id]["metrics"] = trained_models[model_id]["metrics"]
        
        logger.info(f"Model {model_id} trained successfully. MAE: {mae:.4f}, R2: {r2:.4f}")
        
    except Exception as e:
        logger.error(f"Training error for {model_id}: {e}")
        training_status[model_id]["status"] = "failed"
        training_status[model_id]["error"] = str(e)

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "ML Training Backend",
        "status": "active",
        "models_trained": len(trained_models),
        "active_training": sum(1 for s in training_status.values() if s.get("status") == "training")
    }

@app.post("/api/ml/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Start model training"""
    model_id = f"{request.symbol}_{request.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize training status
    training_status[model_id] = {
        "model_id": model_id,
        "status": "initializing",
        "symbol": request.symbol,
        "model_type": request.model_type,
        "started_at": datetime.now().isoformat(),
        "current_epoch": 0,
        "total_epochs": request.epochs
    }
    
    # Start training in background
    background_tasks.add_task(train_model_task, model_id, request)
    
    return {
        "model_id": model_id,
        "message": "Training started",
        "status": training_status[model_id]
    }

@app.get("/api/ml/status/{model_id}")
async def get_training_status(model_id: str):
    """Get training status"""
    if model_id not in training_status:
        raise HTTPException(status_code=404, detail="Model not found")
    
    status = training_status[model_id].copy()
    
    # Add training history if available
    if model_id in training_history:
        status["history"] = training_history[model_id]
    
    return status

@app.get("/api/ml/models")
async def list_models():
    """List all trained models"""
    models = []
    for model_id, model_info in trained_models.items():
        models.append({
            "model_id": model_id,
            "symbol": model_info["symbol"],
            "model_type": model_info["model_type"],
            "trained_at": model_info["trained_at"],
            "metrics": model_info["metrics"]
        })
    return {"models": models}

@app.post("/api/ml/predict")
async def predict(request: PredictionRequest):
    """Generate prediction using trained model"""
    # Find appropriate model
    model_id = request.model_id
    if not model_id:
        # Find latest model for symbol
        symbol_models = [
            (mid, info) for mid, info in trained_models.items() 
            if info["symbol"] == request.symbol
        ]
        if not symbol_models:
            raise HTTPException(status_code=404, detail=f"No trained model found for {request.symbol}")
        model_id = max(symbol_models, key=lambda x: x[1]["trained_at"])[0]
    
    if model_id not in trained_models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_info = trained_models[model_id]
    model = model_info["model"]
    scaler = model_info["scaler"]
    
    try:
        # Get recent data
        df = prepare_stock_data(model_info["symbol"], period="3mo")
        
        # Prepare features
        feature_data = df[model_info["feature_columns"]].values[-model_info["sequence_length"]:]
        scaled_data = scaler.transform(feature_data)
        
        # Reshape for prediction
        X = scaled_data.reshape(1, model_info["sequence_length"], len(model_info["feature_columns"]))
        
        # Generate predictions
        predictions = []
        current_sequence = X.copy()
        
        for day in range(request.days_ahead):
            pred = model.predict(current_sequence, verbose=0)
            
            # Inverse transform prediction
            pred_rescaled = scaler.inverse_transform(
                np.concatenate([pred, np.zeros((1, len(model_info["feature_columns"])-1))], axis=1)
            )[0, 0]
            
            predictions.append({
                "day": day + 1,
                "predicted_price": float(pred_rescaled),
                "confidence": float(0.7 + model_info["metrics"]["r2"] * 0.3)  # Based on model R2
            })
            
            # Update sequence for next prediction
            new_row = np.zeros((1, len(model_info["feature_columns"])))
            new_row[0, 0] = pred[0, 0]
            current_sequence = np.concatenate([current_sequence[:, 1:, :], new_row.reshape(1, 1, -1)], axis=1)
        
        current_price = float(df['Close'].iloc[-1])
        
        return {
            "model_id": model_id,
            "symbol": model_info["symbol"],
            "model_type": model_info["model_type"],
            "current_price": current_price,
            "predictions": predictions,
            "model_metrics": model_info["metrics"],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.delete("/api/ml/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a trained model"""
    if model_id not in trained_models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Remove model files
    model_path = os.path.join(MODELS_DIR, f"{model_id}.h5")
    scaler_path = os.path.join(MODELS_DIR, f"{model_id}_scaler.npy")
    
    if os.path.exists(model_path):
        os.remove(model_path)
    if os.path.exists(scaler_path):
        os.remove(scaler_path)
    
    # Remove from memory
    del trained_models[model_id]
    
    if model_id in training_status:
        del training_status[model_id]
    if model_id in training_history:
        del training_history[model_id]
    
    return {"message": f"Model {model_id} deleted successfully"}

if __name__ == "__main__":
    logger.info("Starting ML Training Backend on port 8003")
    logger.info("TensorFlow version: " + tf.__version__)
    logger.info("GPU Available: " + str(tf.config.list_physical_devices('GPU')))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )