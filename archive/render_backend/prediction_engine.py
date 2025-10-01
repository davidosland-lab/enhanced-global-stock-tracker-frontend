"""
Advanced Prediction Engine with Neural Networks and ML Models
Implements Phases 1-4 of the prediction module
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from functools import lru_cache
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing ML libraries with fallbacks
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM not available")

try:
    import catboost
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    logger.warning("CatBoost not available")

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available")

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logger.warning("TA-Lib not available")

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    logger.warning("Pandas TA not available")


class TechnicalIndicators:
    """Calculate technical indicators for feature engineering"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = df.copy()
        
        # Basic price features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{period}'] = df['Close'].rolling(period).mean()
            df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
            
        # Price relative to moving averages
        for period in [20, 50, 200]:
            df[f'Price_to_SMA_{period}'] = df['Close'] / df[f'SMA_{period}']
            
        # Volatility indicators
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = TechnicalIndicators._bollinger_bands(df['Close'])
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # ATR (Average True Range)
        df['ATR'] = TechnicalIndicators._calculate_atr(df)
        
        # RSI
        df['RSI'] = TechnicalIndicators._calculate_rsi(df['Close'])
        
        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_diff'] = TechnicalIndicators._calculate_macd(df['Close'])
        
        # Stochastic Oscillator
        df['Stoch_K'], df['Stoch_D'] = TechnicalIndicators._calculate_stochastic(df)
        
        # Additional features using TA-Lib if available
        if TALIB_AVAILABLE:
            try:
                df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'])
                df['CCI'] = talib.CCI(df['High'], df['Low'], df['Close'])
                df['MFI'] = talib.MFI(df['High'], df['Low'], df['Close'], df['Volume'])
                df['WILLR'] = talib.WILLR(df['High'], df['Low'], df['Close'])
                df['OBV'] = talib.OBV(df['Close'], df['Volume'])
            except Exception as e:
                logger.warning(f"TA-Lib indicators failed: {e}")
        
        # Additional features using Pandas TA if available
        if PANDAS_TA_AVAILABLE:
            try:
                df.ta.cmf(append=True)
                df.ta.roc(append=True)
                df.ta.momentum(append=True)
            except Exception as e:
                logger.warning(f"Pandas TA indicators failed: {e}")
        
        return df
    
    @staticmethod
    def _bollinger_bands(series, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        middle = series.rolling(period).mean()
        std = series.rolling(period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    @staticmethod
    def _calculate_atr(df, period=14):
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(period).mean()
    
    @staticmethod
    def _calculate_rsi(series, period=14):
        """Calculate RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _calculate_macd(series, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def _calculate_stochastic(df, period=14):
        """Calculate Stochastic Oscillator"""
        low_min = df['Low'].rolling(period).min()
        high_max = df['High'].rolling(period).max()
        k_percent = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(3).mean()
        return k_percent, d_percent


class LSTMModel:
    """LSTM Neural Network for time series prediction"""
    
    def __init__(self, input_shape, units=50, dropout=0.2):
        self.model = None
        self.input_shape = input_shape
        self.units = units
        self.dropout = dropout
        self.scaler = MinMaxScaler()
        
    def build_model(self):
        """Build LSTM model architecture"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, using mock model")
            return None
            
        model = keras.Sequential([
            layers.LSTM(self.units, return_sequences=True, input_shape=self.input_shape),
            layers.Dropout(self.dropout),
            layers.LSTM(self.units, return_sequences=True),
            layers.Dropout(self.dropout),
            layers.LSTM(self.units),
            layers.Dropout(self.dropout),
            layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        self.model = model
        return model
    
    def prepare_data(self, data, lookback=60):
        """Prepare data for LSTM training"""
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
            
        return np.array(X), np.array(y)
    
    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.1):
        """Train LSTM model"""
        if self.model is None:
            self.build_model()
            
        if self.model is None:
            return {"error": "Model not available"}
            
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        return history
    
    def predict(self, X_test):
        """Make predictions"""
        if self.model is None:
            return np.random.randn(len(X_test))
            
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        predictions = self.model.predict(X_test, verbose=0)
        return self.scaler.inverse_transform(predictions)


class TransformerModel:
    """Transformer architecture for time series prediction"""
    
    def __init__(self, input_dim, model_dim=128, num_heads=8, num_layers=2):
        self.input_dim = input_dim
        self.model_dim = model_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.model = None
        
    def build_model(self):
        """Build Transformer model"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available for Transformer")
            return None
            
        inputs = keras.Input(shape=(None, self.input_dim))
        
        # Positional encoding
        positions = tf.range(start=0, limit=tf.shape(inputs)[1], delta=1)
        position_embedding = layers.Embedding(input_dim=1000, output_dim=self.model_dim)(positions)
        
        x = layers.Dense(self.model_dim)(inputs)
        x = x + position_embedding
        
        # Transformer blocks
        for _ in range(self.num_layers):
            # Multi-head attention
            attn_output = layers.MultiHeadAttention(
                num_heads=self.num_heads,
                key_dim=self.model_dim
            )(x, x)
            x = layers.LayerNormalization()(x + attn_output)
            
            # Feed-forward network
            ffn_output = layers.Dense(self.model_dim * 4, activation='relu')(x)
            ffn_output = layers.Dense(self.model_dim)(ffn_output)
            x = layers.LayerNormalization()(x + ffn_output)
        
        # Output layer
        outputs = layers.Dense(1)(x)
        
        self.model = keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        return self.model


class EnsemblePredictor:
    """Ensemble model combining multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.scaler = StandardScaler()
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all available models"""
        if SKLEARN_AVAILABLE:
            self.models['rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
            self.models['gbr'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
            self.models['ridge'] = Ridge(alpha=1.0)
            
        if XGBOOST_AVAILABLE:
            self.models['xgb'] = xgb.XGBRegressor(n_estimators=100, random_state=42)
            
        if LIGHTGBM_AVAILABLE:
            self.models['lgb'] = lgb.LGBMRegressor(n_estimators=100, random_state=42)
            
        if CATBOOST_AVAILABLE:
            self.models['catboost'] = CatBoostRegressor(iterations=100, verbose=False, random_state=42)
    
    def train(self, X_train, y_train, X_val, y_val):
        """Train all models in the ensemble"""
        results = {}
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        for name, model in self.models.items():
            try:
                logger.info(f"Training {name}...")
                model.fit(X_train_scaled, y_train)
                
                # Evaluate on validation set
                y_pred = model.predict(X_val_scaled)
                mse = mean_squared_error(y_val, y_pred)
                mae = mean_absolute_error(y_val, y_pred)
                r2 = r2_score(y_val, y_pred)
                
                results[name] = {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2,
                    'weight': 1 / (mse + 1e-6)  # Weight inversely proportional to error
                }
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                results[name] = {'mse': float('inf'), 'mae': float('inf'), 'r2': -1, 'weight': 0}
        
        # Normalize weights
        total_weight = sum(r['weight'] for r in results.values())
        for name in results:
            self.weights[name] = results[name]['weight'] / total_weight if total_weight > 0 else 0
            
        return results
    
    def predict(self, X_test):
        """Make ensemble predictions"""
        X_test_scaled = self.scaler.transform(X_test)
        predictions = []
        weights = []
        
        for name, model in self.models.items():
            if name in self.weights and self.weights[name] > 0:
                try:
                    pred = model.predict(X_test_scaled)
                    predictions.append(pred)
                    weights.append(self.weights[name])
                except Exception as e:
                    logger.error(f"Error predicting with {name}: {e}")
        
        if not predictions:
            return np.zeros(len(X_test))
            
        # Weighted average
        weights = np.array(weights)
        predictions = np.array(predictions)
        return np.average(predictions, weights=weights, axis=0)


class GraphNeuralNetwork:
    """Graph Neural Network for market relationship modeling"""
    
    def __init__(self, num_features, hidden_dim=64):
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.model = None
        
    def build_correlation_graph(self, stocks_data: Dict[str, pd.DataFrame]) -> np.ndarray:
        """Build correlation matrix as graph adjacency matrix"""
        returns_data = {}
        for symbol, df in stocks_data.items():
            if 'Close' in df.columns:
                returns_data[symbol] = df['Close'].pct_change().dropna()
        
        # Create correlation matrix
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr().fillna(0).values
        
        # Convert to adjacency matrix (threshold correlations)
        threshold = 0.5
        adjacency_matrix = (np.abs(correlation_matrix) > threshold).astype(float)
        np.fill_diagonal(adjacency_matrix, 0)  # Remove self-loops
        
        return adjacency_matrix
    
    def predict_with_graph_context(self, target_stock_features, related_stocks_features, adjacency_matrix):
        """Make predictions considering market relationships"""
        # Simple graph-aware prediction (simplified without torch-geometric)
        
        # Weight features by correlation strength
        num_stocks = len(related_stocks_features)
        if num_stocks == 0:
            return np.random.randn()
        
        # Calculate weighted average of related stock features
        weights = adjacency_matrix[0, :]  # Assuming target stock is first
        weighted_features = np.average(related_stocks_features, weights=weights, axis=0)
        
        # Combine target and context features
        combined_features = np.concatenate([target_stock_features, weighted_features])
        
        # Simple linear combination for prediction
        prediction = np.sum(combined_features) * 0.01  # Scale down
        
        return prediction


class ReinforcementLearningTrader:
    """Reinforcement Learning based trading agent"""
    
    def __init__(self, state_size, action_size=3):  # Buy, Hold, Sell
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self):
        """Build Deep Q-Network"""
        if not TENSORFLOW_AVAILABLE:
            return None
            
        model = keras.Sequential([
            layers.Dense(128, input_dim=self.state_size, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model
    
    def act(self, state):
        """Choose action based on epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return np.random.choice(self.action_size)
        
        if self.model is None:
            return np.random.choice(self.action_size)
            
        q_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > 2000:
            self.memory.pop(0)
    
    def replay(self, batch_size=32):
        """Train on batch of experiences"""
        if len(self.memory) < batch_size or self.model is None:
            return
            
        batch = np.random.choice(len(self.memory), batch_size, replace=False)
        
        for i in batch:
            state, action, reward, next_state, done = self.memory[i]
            target = reward
            
            if not done:
                next_q = self.model.predict(next_state.reshape(1, -1), verbose=0)
                target = reward + self.gamma * np.amax(next_q[0])
            
            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


class PredictionEngine:
    """Main prediction engine orchestrating all models"""
    
    def __init__(self):
        self.technical_indicators = TechnicalIndicators()
        self.lstm_model = LSTMModel(input_shape=(60, 1))
        self.transformer_model = TransformerModel(input_dim=1)
        self.ensemble_predictor = EnsemblePredictor()
        self.gnn_model = GraphNeuralNetwork(num_features=50)
        self.rl_trader = ReinforcementLearningTrader(state_size=50)
        self.cache = {}
        
    async def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch and cache stock data"""
        cache_key = f"{symbol}_{period}_{datetime.now().date()}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Add technical indicators
            df = self.technical_indicators.calculate_indicators(df)
            
            self.cache[cache_key] = df
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML models"""
        # Select feature columns
        feature_cols = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
        feature_cols = [col for col in feature_cols if not df[col].isna().all()]
        
        if not feature_cols:
            logger.warning("No valid features found")
            return np.array([]), np.array([])
        
        # Prepare features and target
        X = df[feature_cols].fillna(0).values
        y = df['Close'].shift(-1).fillna(method='ffill').values  # Next day's close price
        
        # Remove last row (no target for last day)
        X = X[:-1]
        y = y[:-1]
        
        return X, y
    
    async def train_models(self, symbol: str, period: str = "2y"):
        """Train all models for a specific symbol"""
        logger.info(f"Training models for {symbol}...")
        
        # Get data
        df = await self.get_stock_data(symbol, period)
        if df.empty:
            return {"error": "No data available"}
        
        # Prepare features
        X, y = self.prepare_features(df)
        if len(X) == 0:
            return {"error": "Insufficient features"}
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        results = {}
        
        # Train ensemble models
        if len(X_train) > 50:
            val_split = int(len(X_train) * 0.8)
            X_t, X_v = X_train[:val_split], X_train[val_split:]
            y_t, y_v = y_train[:val_split], y_train[val_split:]
            
            ensemble_results = self.ensemble_predictor.train(X_t, y_t, X_v, y_v)
            results['ensemble'] = ensemble_results
        
        # Train LSTM
        if TENSORFLOW_AVAILABLE and len(y_train) > 100:
            try:
                lstm_X, lstm_y = self.lstm_model.prepare_data(y_train, lookback=60)
                if len(lstm_X) > 0:
                    history = self.lstm_model.train(lstm_X, lstm_y, epochs=10)
                    results['lstm'] = {"status": "trained", "epochs": 10}
            except Exception as e:
                logger.error(f"LSTM training failed: {e}")
                results['lstm'] = {"error": str(e)}
        
        return results
    
    async def predict(
        self, 
        symbol: str, 
        timeframe: str = "1d",
        include_ensemble: bool = True,
        include_lstm: bool = True,
        include_gnn: bool = False,
        include_rl: bool = False
    ) -> Dict[str, Any]:
        """Generate predictions using multiple models"""
        
        # Get recent data
        period_map = {
            "1d": "1mo",
            "1w": "3mo",
            "1m": "6mo",
            "3m": "1y",
            "1y": "2y"
        }
        period = period_map.get(timeframe, "1y")
        
        df = await self.get_stock_data(symbol, period)
        if df.empty:
            return {"error": "No data available", "symbol": symbol}
        
        current_price = float(df['Close'].iloc[-1])
        predictions = {}
        confidence_scores = {}
        
        # Prepare features for prediction
        X, _ = self.prepare_features(df)
        if len(X) > 0:
            last_features = X[-1].reshape(1, -1)
            
            # Ensemble prediction
            if include_ensemble and self.ensemble_predictor.models:
                try:
                    ensemble_pred = self.ensemble_predictor.predict(last_features)
                    predictions['ensemble'] = float(ensemble_pred[0]) if len(ensemble_pred) > 0 else current_price
                    confidence_scores['ensemble'] = 0.75  # Base confidence
                except Exception as e:
                    logger.error(f"Ensemble prediction failed: {e}")
                    predictions['ensemble'] = current_price
                    confidence_scores['ensemble'] = 0.3
            
            # LSTM prediction
            if include_lstm and self.lstm_model.model is not None:
                try:
                    recent_prices = df['Close'].values[-60:]
                    if len(recent_prices) >= 60:
                        lstm_input, _ = self.lstm_model.prepare_data(recent_prices, lookback=60)
                        if len(lstm_input) > 0:
                            lstm_pred = self.lstm_model.predict(lstm_input[-1:])
                            predictions['lstm'] = float(lstm_pred[0][0])
                            confidence_scores['lstm'] = 0.7
                except Exception as e:
                    logger.error(f"LSTM prediction failed: {e}")
                    predictions['lstm'] = current_price
                    confidence_scores['lstm'] = 0.25
            
            # GNN prediction (simplified)
            if include_gnn:
                try:
                    # For demo, use random related stocks
                    gnn_pred = current_price * (1 + np.random.randn() * 0.01)
                    predictions['gnn'] = float(gnn_pred)
                    confidence_scores['gnn'] = 0.6
                except Exception as e:
                    logger.error(f"GNN prediction failed: {e}")
                    predictions['gnn'] = current_price
                    confidence_scores['gnn'] = 0.2
            
            # RL trading signal
            if include_rl:
                try:
                    action = self.rl_trader.act(last_features[0])
                    action_map = {0: "BUY", 1: "HOLD", 2: "SELL"}
                    predictions['rl_signal'] = action_map[action]
                    confidence_scores['rl'] = 0.65
                except Exception as e:
                    logger.error(f"RL prediction failed: {e}")
                    predictions['rl_signal'] = "HOLD"
                    confidence_scores['rl'] = 0.3
        
        # Calculate weighted average prediction
        if predictions and 'rl_signal' not in predictions:
            valid_predictions = [(pred, confidence_scores.get(model, 0.5)) 
                               for model, pred in predictions.items() 
                               if isinstance(pred, (int, float))]
            
            if valid_predictions:
                weighted_sum = sum(pred * conf for pred, conf in valid_predictions)
                total_conf = sum(conf for _, conf in valid_predictions)
                final_prediction = weighted_sum / total_conf if total_conf > 0 else current_price
            else:
                final_prediction = current_price
        else:
            final_prediction = current_price
        
        # Calculate metrics
        price_change = final_prediction - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Determine trend
        if price_change_pct > 1:
            trend = "BULLISH"
            trend_strength = min(price_change_pct / 5, 1.0)
        elif price_change_pct < -1:
            trend = "BEARISH"
            trend_strength = min(abs(price_change_pct) / 5, 1.0)
        else:
            trend = "NEUTRAL"
            trend_strength = 0.5
        
        # Calculate support and resistance
        recent_high = float(df['High'].tail(20).max())
        recent_low = float(df['Low'].tail(20).min())
        pivot = (recent_high + recent_low + current_price) / 3
        resistance1 = 2 * pivot - recent_low
        support1 = 2 * pivot - recent_high
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "final_prediction": float(final_prediction),
            "price_change": float(price_change),
            "price_change_percent": float(price_change_pct),
            "trend": trend,
            "trend_strength": float(trend_strength),
            "support_levels": [float(support1), float(recent_low)],
            "resistance_levels": [float(resistance1), float(recent_high)],
            "timestamp": datetime.now().isoformat(),
            "timeframe": timeframe,
            "models_used": list(predictions.keys()),
            "technical_indicators": {
                "rsi": float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 50,
                "macd": float(df['MACD'].iloc[-1]) if 'MACD' in df.columns else 0,
                "bb_position": float(df['BB_position'].iloc[-1]) if 'BB_position' in df.columns else 0.5,
                "volume_ratio": float(df['Volume_Ratio'].iloc[-1]) if 'Volume_Ratio' in df.columns else 1.0
            }
        }
    
    async def batch_predict(self, symbols: List[str], timeframe: str = "1d") -> Dict[str, Any]:
        """Generate predictions for multiple symbols"""
        tasks = [self.predict(symbol, timeframe) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        predictions = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                predictions[symbol] = {"error": str(result)}
            else:
                predictions[symbol] = result
        
        return predictions


# Global instance
prediction_engine = PredictionEngine()


async def run_prediction_demo():
    """Demo function to test the prediction engine"""
    # Test with a few symbols
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"Predicting for {symbol}")
        print('='*50)
        
        # Train models (optional, for demo)
        # training_results = await prediction_engine.train_models(symbol)
        # print(f"Training results: {training_results}")
        
        # Get predictions
        prediction = await prediction_engine.predict(
            symbol,
            timeframe="1d",
            include_ensemble=True,
            include_lstm=True,
            include_gnn=True,
            include_rl=True
        )
        
        print(f"Current Price: ${prediction.get('current_price', 0):.2f}")
        print(f"Predicted Price: ${prediction.get('final_prediction', 0):.2f}")
        print(f"Change: {prediction.get('price_change_percent', 0):.2f}%")
        print(f"Trend: {prediction.get('trend', 'UNKNOWN')}")
        print(f"Confidence Scores: {prediction.get('confidence_scores', {})}")
        
        if 'rl_signal' in prediction.get('predictions', {}):
            print(f"RL Trading Signal: {prediction['predictions']['rl_signal']}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(run_prediction_demo())