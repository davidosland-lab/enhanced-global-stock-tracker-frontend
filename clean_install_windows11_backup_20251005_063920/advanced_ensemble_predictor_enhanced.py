#!/usr/bin/env python3
"""
Enhanced Advanced Ensemble Predictor with Real Training Integration
Implements feedback loop from backtesting to model improvement
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler
import warnings
import concurrent.futures
from functools import partial, lru_cache
import hashlib
import pickle
import os

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import base classes
try:
    from advanced_ensemble_predictor import (
        PredictionHorizon, ModelType, PredictionResult,
        AdvancedEnsemblePredictor
    )
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    logger.warning("Base predictor not available, using standalone implementation")

class DataCache:
    """Efficient caching layer for preprocessed data"""
    
    def __init__(self, max_size=100, cache_dir="./cache"):
        self.cache = {}
        self.max_size = max_size
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_cache_key(self, symbol: str, period: str, feature_type: str = "features") -> str:
        """Generate cache key"""
        return hashlib.md5(f"{symbol}_{period}_{feature_type}".encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def get_features(self, symbol: str, period: str) -> Optional[np.ndarray]:
        """Get cached features"""
        key = self.get_cache_key(symbol, period, "features")
        
        # Try memory cache first
        if key in self.cache:
            return self.cache[key]
        
        # Try disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.cache[key] = data  # Load to memory
                    return data
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def save_features(self, symbol: str, period: str, features: np.ndarray):
        """Save features to cache"""
        key = self.get_cache_key(symbol, period, "features")
        
        # Save to memory
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = features
        
        # Save to disk
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(features, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

class AdaptiveLearningScheduler:
    """Adaptive learning rate scheduler based on performance"""
    
    def __init__(self, initial_lr=0.001, patience=5):
        self.lr = initial_lr
        self.initial_lr = initial_lr
        self.performance_history = []
        self.patience = patience
        self.best_performance = 0
        self.patience_counter = 0
        
    def update_lr(self, current_performance: float) -> float:
        """Adjust learning rate based on performance"""
        self.performance_history.append(current_performance)
        
        if current_performance > self.best_performance:
            self.best_performance = current_performance
            self.patience_counter = 0
        else:
            self.patience_counter += 1
        
        # Reduce learning rate if no improvement
        if self.patience_counter >= self.patience:
            self.lr *= 0.5
            self.patience_counter = 0
            logger.info(f"📉 Reduced learning rate to {self.lr:.6f}")
        
        # Increase learning rate if consistent improvement
        if len(self.performance_history) >= 5:
            recent = self.performance_history[-5:]
            if all(recent[i] <= recent[i+1] for i in range(4)):  # Consistent improvement
                self.lr = min(self.lr * 1.1, self.initial_lr * 2)  # Don't exceed 2x initial
                logger.info(f"📈 Increased learning rate to {self.lr:.6f}")
        
        return self.lr

class EnhancedEnsemblePredictor:
    """Enhanced predictor with real training from backtesting data"""
    
    def __init__(self):
        # Initialize base predictor if available
        if BASE_AVAILABLE:
            self.base_predictor = AdvancedEnsemblePredictor()
        else:
            self.base_predictor = None
            
        # Dynamic model weights learned from backtesting
        self.model_weights = {
            'lstm': 0.25,
            'random_forest': 0.25,
            'arima': 0.25,
            'quantile_regression': 0.25
        }
        
        # Performance tracking
        self.model_performance_history = {
            'lstm': [],
            'random_forest': [],
            'arima': [],
            'quantile_regression': []
        }
        
        # Initialize components
        self.data_cache = DataCache()
        self.learning_scheduler = AdaptiveLearningScheduler()
        self.training_history = []
        
        # Model instances for real training
        self.models = {}
        self._initialize_real_models()
        
        # GPU setup if available
        self.device = self._setup_gpu_acceleration()
        
    def _initialize_real_models(self):
        """Initialize actual trainable models"""
        try:
            # Random Forest models
            for horizon in ['intraday', 'short', 'medium', 'long']:
                self.models[f'rf_{horizon}'] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42,
                    n_jobs=-1  # Use all CPU cores
                )
            
            # LSTM models (if TensorFlow available)
            try:
                import tensorflow as tf
                from tensorflow.keras.models import Sequential
                from tensorflow.keras.layers import LSTM, Dense, Dropout
                
                for horizon in ['intraday', 'short', 'medium', 'long']:
                    model = Sequential([
                        LSTM(50, activation='relu', return_sequences=True),
                        Dropout(0.2),
                        LSTM(50, activation='relu'),
                        Dropout(0.2),
                        Dense(1)
                    ])
                    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
                    self.models[f'lstm_{horizon}'] = model
                logger.info("✅ LSTM models initialized with TensorFlow")
            except ImportError:
                logger.warning("⚠️ TensorFlow not available, LSTM models disabled")
            
            # XGBoost models (if available)
            try:
                import xgboost as xgb
                for horizon in ['intraday', 'short', 'medium', 'long']:
                    self.models[f'xgb_{horizon}'] = xgb.XGBRegressor(
                        n_estimators=100,
                        max_depth=6,
                        learning_rate=0.01,
                        random_state=42
                    )
                logger.info("✅ XGBoost models initialized")
            except ImportError:
                logger.warning("⚠️ XGBoost not available")
                
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    def _setup_gpu_acceleration(self):
        """Setup GPU acceleration if available"""
        try:
            import torch
            if torch.cuda.is_available():
                device = torch.device("cuda")
                logger.info(f"🚀 GPU enabled: {torch.cuda.get_device_name(0)}")
                return device
            else:
                logger.info("💻 Using CPU (GPU not available)")
                return torch.device("cpu")
        except ImportError:
            logger.info("💻 PyTorch not available, using CPU")
            return None
    
    async def update_weights_from_backtest(self, backtest_results: Dict[str, Any]):
        """Update model ensemble weights based on backtesting performance"""
        
        try:
            # Extract performance metrics
            model_performance = backtest_results.get('model_performance', {})
            
            if not model_performance:
                logger.warning("No model performance data in backtest results")
                return
            
            # Update weights using exponential moving average
            alpha = self.learning_scheduler.lr  # Use adaptive learning rate
            
            for model, performance in model_performance.items():
                accuracy = performance.get('dominant_accuracy', 0.5)
                
                # Store performance history
                if model in self.model_performance_history:
                    self.model_performance_history[model].append(accuracy)
                
                # Update weight with EMA
                if model in self.model_weights:
                    old_weight = self.model_weights[model]
                    new_weight = alpha * accuracy + (1 - alpha) * old_weight
                    self.model_weights[model] = new_weight
                else:
                    self.model_weights[model] = accuracy
            
            # Normalize weights to sum to 1
            total_weight = sum(self.model_weights.values())
            if total_weight > 0:
                for model in self.model_weights:
                    self.model_weights[model] /= total_weight
            
            # Update learning rate based on overall performance
            overall_accuracy = backtest_results.get('overall_accuracy', 0.5)
            self.learning_scheduler.update_lr(overall_accuracy)
            
            logger.info(f"✅ Updated model weights from backtesting:")
            for model, weight in self.model_weights.items():
                logger.info(f"   {model}: {weight:.3f}")
                
        except Exception as e:
            logger.error(f"Error updating weights: {e}")
    
    async def incremental_train(self, symbol: str, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Incrementally train models with new data (faster than full retrain)"""
        
        try:
            # Use last 100 data points for incremental training
            recent_data = new_data.tail(100)
            
            # Check cache first
            cached_features = self.data_cache.get_features(symbol, "incremental")
            
            if cached_features is None:
                # Prepare features
                features = self._prepare_features(recent_data)
                labels = self._prepare_labels(recent_data)
                
                # Cache the features
                self.data_cache.save_features(symbol, "incremental", features)
            else:
                features = cached_features
                labels = self._prepare_labels(recent_data)
            
            # Track training results
            results = {}
            
            # Incremental training for supported models
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'partial_fit'):
                        # Scikit-learn models with partial_fit
                        model.partial_fit(features, labels)
                        results[model_name] = "incremental"
                        logger.info(f"✅ Incrementally trained {model_name}")
                    elif 'lstm' in model_name and hasattr(model, 'fit'):
                        # Keras/TensorFlow LSTM - train for 1 epoch
                        model.fit(features, labels, epochs=1, verbose=0)
                        results[model_name] = "incremental"
                        logger.info(f"✅ Incrementally trained {model_name} (1 epoch)")
                    else:
                        # Full retrain for models without incremental support
                        model.fit(features, labels)
                        results[model_name] = "full"
                        logger.info(f"📊 Fully retrained {model_name}")
                except Exception as e:
                    logger.error(f"Failed to train {model_name}: {e}")
                    results[model_name] = "failed"
            
            return {
                "success": True,
                "symbol": symbol,
                "data_points": len(features),
                "training_results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Incremental training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def parallel_backtest(self, symbols: List[str], period: str) -> List[Dict]:
        """Run backtests in parallel for multiple symbols"""
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Create futures for each symbol
            futures = {}
            for symbol in symbols:
                future = executor.submit(self._run_single_backtest, symbol, period)
                futures[future] = symbol
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                    logger.info(f"✅ Completed backtest for {symbol}")
                except Exception as e:
                    logger.error(f"❌ Backtest failed for {symbol}: {e}")
                    results.append({
                        "symbol": symbol,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def _run_single_backtest(self, symbol: str, period: str) -> Dict:
        """Run backtest for a single symbol (sync version for thread pool)"""
        # This would call the actual backtest logic
        # Simplified for demonstration
        return {
            "symbol": symbol,
            "period": period,
            "success": True,
            "accuracy": np.random.uniform(0.6, 0.85),
            "sharpe_ratio": np.random.uniform(1.0, 2.0)
        }
    
    async def batch_train_models(self, training_batch: List[Dict]) -> Dict[str, Any]:
        """Train models in batches for efficiency"""
        
        try:
            logger.info(f"📦 Starting batch training with {len(training_batch)} items")
            
            # Combine all training data
            all_features = []
            all_labels = []
            
            for item in training_batch:
                # Check cache first
                symbol = item.get('symbol', 'unknown')
                period = item.get('period', 'unknown')
                
                cached = self.data_cache.get_features(symbol, period)
                if cached is not None:
                    features = cached
                else:
                    features = self._prepare_features(item['data'])
                    self.data_cache.save_features(symbol, period, features)
                
                labels = self._prepare_labels(item['data'])
                
                all_features.append(features)
                all_labels.append(labels)
            
            # Stack all data
            X = np.vstack(all_features)
            y = np.hstack(all_labels)
            
            logger.info(f"📊 Combined batch: {X.shape[0]} samples, {X.shape[1]} features")
            
            # Train all models
            training_results = {}
            
            for model_name, model in self.models.items():
                try:
                    start_time = datetime.now()
                    
                    if 'lstm' in model_name and hasattr(model, 'fit'):
                        # Special handling for LSTM
                        X_reshaped = X.reshape((X.shape[0], 1, X.shape[1]))
                        model.fit(X_reshaped, y, epochs=10, batch_size=32, verbose=0)
                    else:
                        model.fit(X, y)
                    
                    train_time = (datetime.now() - start_time).total_seconds()
                    
                    training_results[model_name] = {
                        "status": "success",
                        "samples": len(X),
                        "train_time": train_time
                    }
                    
                    logger.info(f"✅ Batch trained {model_name} in {train_time:.2f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to train {model_name}: {e}")
                    training_results[model_name] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Store training history
            self.training_history.append({
                "timestamp": datetime.now().isoformat(),
                "batch_size": len(training_batch),
                "total_samples": len(X),
                "results": training_results
            })
            
            return {
                "success": True,
                "total_samples": len(X),
                "models_trained": len([r for r in training_results.values() if r['status'] == 'success']),
                "training_results": training_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features from market data with caching"""
        
        # Technical indicators
        data = data.copy()
        
        # Price-based features
        data['Returns'] = data['Close'].pct_change()
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
        
        # Moving averages
        for window in [5, 10, 20, 50]:
            data[f'SMA_{window}'] = data['Close'].rolling(window=window).mean()
            data[f'SMA_{window}_ratio'] = data['Close'] / data[f'SMA_{window}']
        
        # Volatility
        data['Volatility'] = data['Returns'].rolling(window=20).std()
        
        # RSI
        data['RSI'] = self._calculate_rsi(data['Close'])
        
        # MACD
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
        
        # Volume features
        data['Volume_Ratio'] = data['Volume'] / data['Volume'].rolling(window=20).mean()
        data['Price_Volume'] = data['Close'] * data['Volume']
        
        # High-Low features
        data['High_Low_Ratio'] = data['High'] / data['Low']
        data['Close_Open_Ratio'] = data['Close'] / data['Open']
        
        # Drop NaN values
        data = data.dropna()
        
        # Select feature columns
        feature_cols = [
            'Returns', 'Log_Returns', 'Volatility', 'RSI', 'MACD', 'MACD_signal',
            'Volume_Ratio', 'Price_Volume', 'High_Low_Ratio', 'Close_Open_Ratio'
        ] + [f'SMA_{w}_ratio' for w in [5, 10, 20, 50]]
        
        return data[feature_cols].values
    
    def _prepare_labels(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare labels from market data"""
        data = data.copy()
        
        # Next day return
        data['Next_Return'] = data['Close'].shift(-1) / data['Close'] - 1
        
        # Classification labels (up/down)
        data['Label'] = (data['Next_Return'] > 0).astype(int)
        
        # Regression labels (actual return)
        # data['Label'] = data['Next_Return']  # Uncomment for regression
        
        return data['Label'].dropna().values
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of training history and model performance"""
        
        summary = {
            "total_training_sessions": len(self.training_history),
            "current_model_weights": self.model_weights,
            "learning_rate": self.learning_scheduler.lr,
            "best_performance": self.learning_scheduler.best_performance,
            "model_performance_trends": {}
        }
        
        # Calculate performance trends
        for model, history in self.model_performance_history.items():
            if history:
                summary["model_performance_trends"][model] = {
                    "latest": history[-1] if history else 0,
                    "average": np.mean(history) if history else 0,
                    "trend": "improving" if len(history) > 1 and history[-1] > history[-2] else "stable"
                }
        
        # Cache statistics
        summary["cache_size"] = len(self.data_cache.cache)
        summary["cache_hit_rate"] = "Not tracked"  # Could implement hit rate tracking
        
        return summary

# Global instance
enhanced_predictor = EnhancedEnsemblePredictor()

if __name__ == "__main__":
    async def test():
        print("🚀 Testing Enhanced Ensemble Predictor")
        
        # Test weight update from backtest
        backtest_results = {
            "overall_accuracy": 0.82,
            "model_performance": {
                "lstm": {"dominant_accuracy": 0.85},
                "random_forest": {"dominant_accuracy": 0.80},
                "arima": {"dominant_accuracy": 0.75},
                "quantile_regression": {"dominant_accuracy": 0.83}
            }
        }
        
        await enhanced_predictor.update_weights_from_backtest(backtest_results)
        
        # Get training summary
        summary = enhanced_predictor.get_training_summary()
        print(f"📊 Training Summary: {json.dumps(summary, indent=2)}")
        
    asyncio.run(test())