"""
Local Model Training Engine
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging

logger = logging.getLogger(__name__)


class LocalTrainer:
    """Train models locally on user's computer"""
    
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
    def train(self, symbol: str, period: str) -> Dict[str, Any]:
        """Train models for a symbol"""
        
        logger.info(f"Starting training for {symbol}")
        
        # Convert period to yfinance format
        period_map = {
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "10 Years": "10y"
        }
        yf_period = period_map.get(period, "2y")
        
        # Fetch data
        data = self.fetch_training_data(symbol, yf_period)
        
        if data.empty:
            return {"error": "No data available"}
        
        # Prepare features and targets
        X, y = self.prepare_features(data)
        
        if len(X) < 100:
            return {"error": "Insufficient data for training"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        results = {}
        
        # Train Random Forest
        rf_result = self.train_random_forest(X_train, y_train, X_test, y_test, symbol)
        results["random_forest"] = rf_result
        
        # Train Gradient Boosting
        gb_result = self.train_gradient_boosting(X_train, y_train, X_test, y_test, symbol)
        results["gradient_boosting"] = gb_result
        
        # Train XGBoost if available
        try:
            import xgboost as xgb
            xgb_result = self.train_xgboost(X_train, y_train, X_test, y_test, symbol)
            results["xgboost"] = xgb_result
        except ImportError:
            logger.info("XGBoost not available")
        
        return {
            "symbol": symbol,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "models": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_training_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch historical data for training"""
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    
    def prepare_features(self, data: pd.DataFrame) -> tuple:
        """Prepare features and target for training"""
        df = data.copy()
        
        # Calculate features
        # Returns
        df['returns'] = df['Close'].pct_change()
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'sma_ratio_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Volatility
        df['volatility'] = df['returns'].rolling(20).std()
        
        # Volume
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Target: Next day return
        df['target'] = df['returns'].shift(-1)
        
        # Select features
        feature_cols = [
            'returns', 'log_returns', 'volatility', 'volume_ratio', 'rsi',
            'macd', 'macd_signal'
        ] + [f'sma_ratio_{p}' for p in [5, 10, 20, 50]]
        
        # Drop NaN values
        df = df.dropna()
        
        X = df[feature_cols].values
        y = df['target'].values
        
        return X, y
    
    def train_random_forest(self, X_train, y_train, X_test, y_test, symbol):
        """Train Random Forest model"""
        logger.info(f"Training Random Forest for {symbol}")
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Save model
        model_path = os.path.join(self.models_dir, f"{symbol}_rf.pkl")
        joblib.dump(model, model_path)
        
        return {
            "train_mse": float(train_mse),
            "test_mse": float(test_mse),
            "test_r2": float(test_r2),
            "model_path": model_path
        }
    
    def train_gradient_boosting(self, X_train, y_train, X_test, y_test, symbol):
        """Train Gradient Boosting model"""
        logger.info(f"Training Gradient Boosting for {symbol}")
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        test_pred = model.predict(X_test)
        test_mse = mean_squared_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Save model
        model_path = os.path.join(self.models_dir, f"{symbol}_gb.pkl")
        joblib.dump(model, model_path)
        
        return {
            "test_mse": float(test_mse),
            "test_r2": float(test_r2),
            "model_path": model_path
        }
    
    def train_xgboost(self, X_train, y_train, X_test, y_test, symbol):
        """Train XGBoost model"""
        import xgboost as xgb
        
        logger.info(f"Training XGBoost for {symbol}")
        
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        test_pred = model.predict(X_test)
        test_mse = mean_squared_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Save model
        model_path = os.path.join(self.models_dir, f"{symbol}_xgb.pkl")
        joblib.dump(model, model_path)
        
        return {
            "test_mse": float(test_mse),
            "test_r2": float(test_r2),
            "model_path": model_path
        }