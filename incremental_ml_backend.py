"""
Incremental ML Backend for Stock Tracker
Implements real-time learning models that update continuously
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
import yfinance as yf

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# Try to import advanced libraries
try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

try:
    from river import linear_model, preprocessing, metrics
    HAS_RIVER = True
except ImportError:
    HAS_RIVER = False

# Create FastAPI app
app = FastAPI(title="Incremental ML Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncrementalModel:
    """Base class for incremental learning models"""
    
    def __init__(self, model_type: str = "sgd"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.performance_history = deque(maxlen=100)
        self.training_samples = 0
        self.last_update = datetime.now()
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the incremental model"""
        if self.model_type == "sgd":
            self.model = SGDRegressor(
                loss='huber',  # Robust to outliers
                penalty='elasticnet',
                alpha=0.0001,
                l1_ratio=0.15,
                learning_rate='invscaling',
                eta0=0.01,
                power_t=0.25,
                max_iter=1000,
                tol=0.001,
                random_state=42,
                warm_start=True  # Continue from previous fit
            )
        
        elif self.model_type == "passive_aggressive":
            self.model = PassiveAggressiveRegressor(
                C=1.0,
                epsilon=0.1,
                max_iter=1000,
                random_state=42,
                warm_start=True
            )
        
        elif self.model_type == "neural" and HAS_TENSORFLOW:
            self.model = self._build_neural_network()
        
        elif self.model_type == "river" and HAS_RIVER:
            # River models for true online learning
            self.model = preprocessing.StandardScaler() | linear_model.LinearRegression(
                optimizer=linear_model.SGD(lr=0.01),
                intercept_lr=0.001
            )
            self.river_metric = metrics.MAE()
        
        else:
            # Default to SGD
            self.model = SGDRegressor(random_state=42, warm_start=True)
    
    def _build_neural_network(self):
        """Build adaptive neural network"""
        if not HAS_TENSORFLOW:
            return None
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(None,)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        
        # Use adaptive learning rate
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=tf.keras.optimizers.schedules.ExponentialDecay(
                initial_learning_rate=0.001,
                decay_steps=1000,
                decay_rate=0.9
            )
        )
        
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        return model
    
    def update(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Update model with new data incrementally"""
        
        if self.model_type == "river" and HAS_RIVER:
            # River handles one sample at a time
            results = []
            for xi, yi in zip(X, y):
                # Make prediction before learning
                xi_dict = {f'feature_{i}': float(v) for i, v in enumerate(xi)}
                y_pred = self.model.predict_one(xi_dict)
                
                # Update model
                self.model.learn_one(xi_dict, float(yi))
                
                # Update metrics
                if y_pred is not None:
                    self.river_metric.update(float(yi), y_pred)
                    results.append(y_pred)
            
            self.training_samples += len(X)
            score = 1 - self.river_metric.get() / np.std(y) if np.std(y) > 0 else 0
            
            return {
                "samples_processed": len(X),
                "total_samples": self.training_samples,
                "score": float(score),
                "model_type": self.model_type
            }
        
        # Scale features
        if not self.is_fitted:
            X_scaled = self.scaler.fit_transform(X)
            self.is_fitted = True
        else:
            # Update scaler incrementally
            self.scaler.partial_fit(X)
            X_scaled = self.scaler.transform(X)
        
        if self.model_type == "neural" and HAS_TENSORFLOW:
            # Neural network incremental update
            history = self.model.fit(
                X_scaled, y,
                epochs=1,
                batch_size=min(32, len(X)),
                verbose=0
            )
            score = -history.history['loss'][0]  # Negative loss as score
        else:
            # SKLearn incremental models
            if not hasattr(self.model, 'partial_fit'):
                raise ValueError(f"Model {self.model_type} doesn't support incremental learning")
            
            # Partial fit
            self.model.partial_fit(X_scaled, y)
            
            # Calculate score on current batch
            y_pred = self.model.predict(X_scaled)
            score = r2_score(y, y_pred)
        
        # Track performance
        self.performance_history.append(score)
        self.training_samples += len(X)
        self.last_update = datetime.now()
        
        return {
            "samples_processed": len(X),
            "total_samples": self.training_samples,
            "score": float(score),
            "avg_recent_score": float(np.mean(self.performance_history)),
            "model_type": self.model_type
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted and self.model_type != "river":
            raise ValueError("Model not fitted yet")
        
        if self.model_type == "river" and HAS_RIVER:
            predictions = []
            for xi in X:
                xi_dict = {f'feature_{i}': float(v) for i, v in enumerate(xi)}
                pred = self.model.predict_one(xi_dict)
                predictions.append(pred if pred is not None else 0)
            return np.array(predictions)
        
        X_scaled = self.scaler.transform(X)
        
        if self.model_type == "neural" and HAS_TENSORFLOW:
            return self.model.predict(X_scaled, verbose=0).flatten()
        else:
            return self.model.predict(X_scaled)
    
    def get_info(self) -> Dict:
        """Get model information"""
        return {
            "model_type": self.model_type,
            "is_fitted": self.is_fitted,
            "training_samples": self.training_samples,
            "last_update": self.last_update.isoformat(),
            "recent_performance": float(np.mean(self.performance_history)) if self.performance_history else None,
            "performance_trend": self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate performance trend"""
        if len(self.performance_history) < 10:
            return "insufficient_data"
        
        recent = np.mean(list(self.performance_history)[-5:])
        older = np.mean(list(self.performance_history)[-10:-5])
        
        if recent > older * 1.1:
            return "improving"
        elif recent < older * 0.9:
            return "degrading"
        else:
            return "stable"


class StreamingStockPredictor:
    """Main class for streaming stock prediction"""
    
    def __init__(self):
        self.models = {}
        self.data_buffer = {}
        self.update_threshold = 10  # Update after N new samples
        
    def get_or_create_model(self, symbol: str, model_type: str) -> IncrementalModel:
        """Get existing model or create new one"""
        key = f"{symbol}_{model_type}"
        if key not in self.models:
            self.models[key] = IncrementalModel(model_type)
            self.data_buffer[key] = {'X': [], 'y': []}
        return self.models[key]
    
    def add_data(self, symbol: str, model_type: str, X: np.ndarray, y: np.ndarray) -> Dict:
        """Add data to buffer and update model if threshold reached"""
        key = f"{symbol}_{model_type}"
        model = self.get_or_create_model(symbol, model_type)
        
        # Add to buffer
        self.data_buffer[key]['X'].extend(X)
        self.data_buffer[key]['y'].extend(y)
        
        # Check if we should update
        buffer_size = len(self.data_buffer[key]['X'])
        
        if buffer_size >= self.update_threshold:
            # Convert buffer to arrays
            X_buffer = np.array(self.data_buffer[key]['X'])
            y_buffer = np.array(self.data_buffer[key]['y'])
            
            # Update model
            result = model.update(X_buffer, y_buffer)
            
            # Clear buffer
            self.data_buffer[key] = {'X': [], 'y': []}
            
            return {
                "status": "updated",
                "buffer_processed": buffer_size,
                **result
            }
        else:
            return {
                "status": "buffering",
                "buffer_size": buffer_size,
                "threshold": self.update_threshold
            }
    
    def force_update(self, symbol: str, model_type: str) -> Dict:
        """Force model update with buffered data"""
        key = f"{symbol}_{model_type}"
        
        if key not in self.data_buffer or not self.data_buffer[key]['X']:
            return {"status": "no_data_to_process"}
        
        model = self.get_or_create_model(symbol, model_type)
        
        X_buffer = np.array(self.data_buffer[key]['X'])
        y_buffer = np.array(self.data_buffer[key]['y'])
        
        result = model.update(X_buffer, y_buffer)
        self.data_buffer[key] = {'X': [], 'y': []}
        
        return {
            "status": "force_updated",
            **result
        }


# Global predictor instance
predictor = StreamingStockPredictor()

# Request models
class StreamUpdateRequest(BaseModel):
    symbol: str
    model_type: str = "sgd"
    features: List[List[float]]
    targets: List[float]
    force_update: bool = False

class StreamPredictRequest(BaseModel):
    symbol: str
    model_type: str = "sgd"
    features: List[List[float]]

@app.get("/")
async def root():
    return {
        "service": "Incremental ML Backend",
        "version": "1.0",
        "available_models": ["sgd", "passive_aggressive", "neural", "river"],
        "tensorflow_available": HAS_TENSORFLOW,
        "river_available": HAS_RIVER
    }

@app.post("/api/stream/update")
async def stream_update(request: StreamUpdateRequest):
    """Update model with streaming data"""
    try:
        X = np.array(request.features)
        y = np.array(request.targets)
        
        if request.force_update:
            result = predictor.force_update(request.symbol, request.model_type)
        else:
            result = predictor.add_data(request.symbol, request.model_type, X, y)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stream/predict")
async def stream_predict(request: StreamPredictRequest):
    """Make predictions with incremental model"""
    try:
        model = predictor.get_or_create_model(request.symbol, request.model_type)
        
        if not model.is_fitted:
            return {
                "error": "Model not fitted yet",
                "suggestion": "Send training data first via /api/stream/update"
            }
        
        X = np.array(request.features)
        predictions = model.predict(X)
        
        return {
            "predictions": predictions.tolist(),
            "model_info": model.get_info()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/models")
async def get_models():
    """Get information about all streaming models"""
    models_info = {}
    
    for key, model in predictor.models.items():
        models_info[key] = model.get_info()
    
    return {
        "models": models_info,
        "count": len(models_info)
    }

@app.delete("/api/stream/models/{symbol}/{model_type}")
async def delete_model(symbol: str, model_type: str):
    """Delete a streaming model"""
    key = f"{symbol}_{model_type}"
    
    if key in predictor.models:
        del predictor.models[key]
        if key in predictor.data_buffer:
            del predictor.data_buffer[key]
        return {"message": f"Model {key} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Model not found")

if __name__ == "__main__":
    import uvicorn
    print("Starting Incremental ML Backend on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)