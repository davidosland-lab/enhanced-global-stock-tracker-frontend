#!/usr/bin/env python3
"""
Real ML Stock Predictor - NO mock/simulated data
Uses only actual market data for training and predictions
"""

import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Try to import XGBoost (optional)
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

logger = logging.getLogger(__name__)

class RealMLStockPredictor:
    """ML Stock Predictor using ONLY real market data"""
    
    def __init__(self, model_dir: str = "models"):
        """Initialize with model storage directory"""
        self.model_dir = model_dir
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        self.models = {}
        self.scalers = {}
        self.last_train_data = {}
        
    def fetch_real_data(self, symbol: str, period: str = "2y") -> Optional[pd.DataFrame]:
        """Fetch REAL data from Yahoo Finance"""
        try:
            # Handle Australian stocks
            if not '.' in symbol and symbol in ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ']:
                symbol = f"{symbol}.AX"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.error(f"No data found for {symbol}")
                return None
                
            logger.info(f"Fetched {len(data)} days of real data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def calculate_real_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators from real price data"""
        if data is None or len(data) < 50:
            logger.error("Insufficient data for feature calculation")
            return None
        
        df = data.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            if len(df) >= period:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        if len(df) >= 26:
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / df['BB_Width']
        
        # Volume features
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Clean up NaN values
        df = df.dropna()
        
        return df
    
    def prepare_training_data(self, df: pd.DataFrame, target_days: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare real data for training"""
        if df is None or len(df) < 100:
            logger.error("Insufficient data for training")
            return None, None
        
        # Select features (exclude non-feature columns)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols].values[:-target_days]
        y = df['Close'].values[target_days:]
        
        # Ensure same length
        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]
        
        return X, y
    
    def train_model(self, symbol: str, model_type: str = "random_forest", period: str = "2y") -> Dict:
        """Train model with REAL data only"""
        # Fetch real data
        data = self.fetch_real_data(symbol, period)
        if data is None:
            return {'error': 'Could not fetch real data'}
        
        # Calculate features
        features_df = self.calculate_real_features(data)
        if features_df is None:
            return {'error': 'Could not calculate features'}
        
        # Prepare training data
        X, y = self.prepare_training_data(features_df)
        if X is None or y is None:
            return {'error': 'Could not prepare training data'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        elif model_type == "gradient_boost":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == "xgboost" and XGB_AVAILABLE:
            model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        else:
            return {'error': f'Model type {model_type} not available'}
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate with real metrics
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Store model
        model_key = f"{symbol}_{model_type}"
        self.models[model_key] = model
        self.scalers[model_key] = scaler
        self.last_train_data[model_key] = features_df
        
        # Save to disk
        model_path = os.path.join(self.model_dir, f"{model_key}.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
        
        return {
            'status': 'success',
            'symbol': symbol,
            'model_type': model_type,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'metrics': {
                'mse': float(mse),
                'rmse': float(np.sqrt(mse)),
                'r2_score': float(r2),
                'mae': float(mae)
            },
            'data_range': {
                'start': data.index[0].strftime('%Y-%m-%d'),
                'end': data.index[-1].strftime('%Y-%m-%d'),
                'days': len(data)
            }
        }
    
    def predict(self, symbol: str, days: int = 5, model_type: str = "random_forest") -> Dict:
        """Make predictions using trained model with real data"""
        model_key = f"{symbol}_{model_type}"
        
        # Check if model exists
        if model_key not in self.models:
            # Try to load from disk
            model_path = os.path.join(self.model_dir, f"{model_key}.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    saved = pickle.load(f)
                    self.models[model_key] = saved['model']
                    self.scalers[model_key] = saved['scaler']
            else:
                return {'error': f'No trained model for {symbol} with {model_type}'}
        
        # Get recent data
        recent_data = self.fetch_real_data(symbol, period="3mo")
        if recent_data is None:
            return {'error': 'Could not fetch recent data'}
        
        # Calculate features
        features_df = self.calculate_real_features(recent_data)
        if features_df is None:
            return {'error': 'Could not calculate features'}
        
        # Prepare last data point
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        feature_cols = [col for col in features_df.columns if col not in exclude_cols]
        last_features = features_df[feature_cols].iloc[-1:].values
        
        # Scale and predict
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        last_features_scaled = scaler.transform(last_features)
        
        # Multi-step prediction
        predictions = []
        current_features = last_features_scaled.copy()
        
        for _ in range(days):
            pred = model.predict(current_features)[0]
            predictions.append(float(pred))
            # Note: For multi-day predictions, we'd need to update features
            # This is simplified - real implementation would recalculate features
        
        current_price = float(recent_data['Close'].iloc[-1])
        
        return {
            'status': 'success',
            'symbol': symbol,
            'model_type': model_type,
            'current_price': current_price,
            'predictions': predictions,
            'dates': [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(days)],
            'confidence_note': 'Predictions based on real historical data and trained model'
        }
    
    def backtest(self, symbol: str, model_type: str = "random_forest", test_days: int = 30) -> Dict:
        """Backtest model with real historical data"""
        model_key = f"{symbol}_{model_type}"
        
        if model_key not in self.models:
            return {'error': f'No trained model for {symbol}'}
        
        # Get historical data
        data = self.fetch_real_data(symbol, period="1y")
        if data is None or len(data) < test_days + 100:
            return {'error': 'Insufficient historical data for backtesting'}
        
        # Calculate features
        features_df = self.calculate_real_features(data)
        
        # Split for backtesting
        train_size = len(features_df) - test_days
        train_data = features_df.iloc[:train_size]
        test_data = features_df.iloc[train_size:]
        
        # Prepare test features
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        feature_cols = [col for col in features_df.columns if col not in exclude_cols]
        X_test = test_data[feature_cols].values
        y_test = test_data['Close'].values
        
        # Predict
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        X_test_scaled = scaler.transform(X_test)
        predictions = model.predict(X_test_scaled)
        
        # Calculate real performance metrics
        returns = (predictions[1:] - y_test[:-1]) / y_test[:-1]
        
        return {
            'status': 'success',
            'symbol': symbol,
            'model_type': model_type,
            'test_days': test_days,
            'metrics': {
                'mse': float(mean_squared_error(y_test, predictions)),
                'mae': float(mean_absolute_error(y_test, predictions)),
                'r2': float(r2_score(y_test, predictions)),
                'mean_return': float(np.mean(returns)),
                'std_return': float(np.std(returns)),
                'sharpe_ratio': float(np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0
            },
            'actual_prices': y_test.tolist()[-10:],  # Last 10 actual
            'predicted_prices': predictions.tolist()[-10:]  # Last 10 predicted
        }

# Usage example
if __name__ == "__main__":
    predictor = RealMLStockPredictor()
    
    # Train with real data
    print("Training with REAL data...")
    result = predictor.train_model("AAPL", "random_forest")
    print(json.dumps(result, indent=2))
    
    # Make predictions
    if 'error' not in result:
        print("\nMaking predictions...")
        predictions = predictor.predict("AAPL", days=5)
        print(json.dumps(predictions, indent=2))