#!/usr/bin/env python3
"""
ML Stock Predictor - Clean Windows Version
Complete system with all fixes applied
"""

import os
import sys
import json
import pickle
import sqlite3
import logging
import warnings
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data processing
import pandas as pd
import numpy as np

# Yahoo Finance
import yfinance as yf

# Technical indicators
try:
    import ta
    HAS_TA = True
except ImportError:
    HAS_TA = False
    logger.warning("TA library not available, using basic indicators")

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

# Optional XGBoost
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.info("XGBoost not available, using GradientBoosting")

# ==================== CONFIGURATION ====================
PORT = 8000
CACHE_DURATION = 300  # 5 minutes
DB_PATH = "ml_models.db"

# ==================== DATA FETCHER ====================
class DataFetcher:
    """Fetch data from Yahoo Finance with robust error handling"""
    
    @staticmethod
    def clear_cache():
        """Clear any cached data that might be corrupted"""
        cache_dirs = [
            os.path.join(os.path.expanduser('~'), '.cache', 'py-yfinance'),
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'py-yfinance'),
        ]
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    logger.info(f"Cleared cache: {cache_dir}")
                except:
                    pass
    
    @staticmethod
    def fetch_stock_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance with multiple fallback methods
        """
        max_retries = 3
        retry_delay = 2
        
        # Clear cache on first failure
        cache_cleared = False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching data for {symbol} (attempt {attempt + 1}/{max_retries})")
                
                # Method 1: Use download (most reliable)
                data = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    threads=False
                )
                
                if data is not None and not data.empty:
                    logger.info(f"✓ Successfully fetched {len(data)} records for {symbol}")
                    
                    # Handle column format
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                    
                    # Ensure column names are strings
                    data.columns = [str(col) for col in data.columns]
                    
                    # Clean data
                    data = data.dropna()
                    
                    # Add symbol column
                    data['Symbol'] = symbol
                    
                    return data
                
                # If empty, clear cache and try again
                if not cache_cleared:
                    DataFetcher.clear_cache()
                    cache_cleared = True
                    continue
                
                # Method 2: Try Ticker
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                if data is not None and not data.empty:
                    logger.info(f"✓ Successfully fetched {len(data)} records using Ticker")
                    data['Symbol'] = symbol
                    return data
                    
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
        
        raise ValueError(f"Failed to fetch data for {symbol} after {max_retries} attempts")

# ==================== FEATURE ENGINEERING ====================
class FeatureEngineer:
    """Calculate technical indicators"""
    
    @staticmethod
    def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add basic technical features without TA library"""
        
        # Price features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['High_Low_Pct'] = (df['High'] - df['Low']) / df['Close'] * 100
        df['Price_Change'] = df['Close'] - df['Open']
        
        # Volume features
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Moving averages
        for period in [5, 10, 20, 50]:
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
        
        # Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_High'] = df['BB_Mid'] + (bb_std * 2)
        df['BB_Low'] = df['BB_Mid'] - (bb_std * 2)
        df['BB_Width'] = df['BB_High'] - df['BB_Low']
        df['BB_Position'] = (df['Close'] - df['BB_Low']) / (df['BB_High'] - df['BB_Low'])
        
        # Price position
        df['Price_to_SMA20'] = df['Close'] / df['SMA_20']
        df['Price_to_SMA50'] = df['Close'] / df['SMA_50']
        
        # Support and Resistance
        df['Resistance'] = df['High'].rolling(window=20).max()
        df['Support'] = df['Low'].rolling(window=20).min()
        
        return df
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        
        if len(df) < 50:
            raise ValueError("Insufficient data for technical indicators")
        
        # Use TA library if available, otherwise use basic
        if HAS_TA:
            try:
                # Use TA library for comprehensive indicators
                df = FeatureEngineer.add_basic_features(df)
                
                # Additional TA indicators
                df['MACD'] = ta.trend.MACD(df['Close']).macd()
                df['MACD_Signal'] = ta.trend.MACD(df['Close']).macd_signal()
                df['MACD_Diff'] = ta.trend.MACD(df['Close']).macd_diff()
                
                df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
                df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
                df['ADX'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close']).adx()
                
            except Exception as e:
                logger.warning(f"TA library error: {e}, using basic features")
                df = FeatureEngineer.add_basic_features(df)
        else:
            df = FeatureEngineer.add_basic_features(df)
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info(f"✓ Added {len(df.columns) - 7} technical indicators")
        
        return df

# ==================== ML MODELS ====================
class MLModels:
    """Machine Learning models for prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        
        # Define feature columns (exclude OHLCV and target)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', 'Symbol', 'Date']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Store feature columns
        self.feature_columns = feature_cols
        
        # Prepare features and target
        X = df[feature_cols].values
        y = df['Close'].shift(-1).fillna(method='ffill').values  # Next day's close price
        
        # Remove last row (no target for it)
        X = X[:-1]
        y = y[:-1]
        
        return X, y
    
    def train_models(self, X: np.ndarray, y: np.ndarray, symbol: str):
        """Train multiple models"""
        
        # Split data (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[symbol] = scaler
        
        models_config = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boost': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        if HAS_XGBOOST:
            models_config['xgboost'] = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                verbosity=0
            )
        
        trained_models = {}
        scores = {}
        
        for name, model in models_config.items():
            logger.info(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            predictions = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, predictions)
            mae = mean_absolute_error(y_test, predictions)
            
            trained_models[name] = model
            scores[name] = {
                'train_score': train_score,
                'test_score': test_score,
                'mse': mse,
                'mae': mae
            }
            
            logger.info(f"  {name} - Train: {train_score:.4f}, Test: {test_score:.4f}")
        
        # Create ensemble
        if len(trained_models) > 1:
            ensemble = VotingRegressor(
                list(trained_models.items()),
                weights=[1.0] * len(trained_models)
            )
            ensemble.fit(X_train_scaled, y_train)
            
            ensemble_train_score = ensemble.score(X_train_scaled, y_train)
            ensemble_test_score = ensemble.score(X_test_scaled, y_test)
            
            trained_models['ensemble'] = ensemble
            scores['ensemble'] = {
                'train_score': ensemble_train_score,
                'test_score': ensemble_test_score
            }
            
            logger.info(f"  Ensemble - Train: {ensemble_train_score:.4f}, Test: {ensemble_test_score:.4f}")
        
        self.models[symbol] = trained_models
        return scores
    
    def predict(self, symbol: str, df: pd.DataFrame, days: int = 5) -> Dict:
        """Make predictions"""
        
        if symbol not in self.models:
            raise ValueError(f"No model trained for {symbol}")
        
        # Prepare features
        feature_data = df[self.feature_columns].values
        
        # Use last row for prediction
        last_features = feature_data[-1].reshape(1, -1)
        
        # Scale
        scaler = self.scalers[symbol]
        last_features_scaled = scaler.transform(last_features)
        
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.models[symbol].items():
            pred = model.predict(last_features_scaled)[0]
            predictions[name] = float(pred)
        
        # Calculate average prediction
        avg_prediction = np.mean(list(predictions.values()))
        
        # Calculate confidence (based on model agreement)
        std_dev = np.std(list(predictions.values()))
        confidence = max(0, min(100, 100 - (std_dev / avg_prediction * 100)))
        
        current_price = float(df['Close'].iloc[-1])
        
        # Simple multi-day prediction (momentum-based)
        daily_change = (avg_prediction - current_price) / current_price
        
        multi_day_predictions = []
        price = current_price
        
        for day in range(1, days + 1):
            price = price * (1 + daily_change * (1 - day * 0.1))  # Decay factor
            multi_day_predictions.append({
                'day': day,
                'price': round(price, 2)
            })
        
        return {
            'current_price': current_price,
            'predictions': predictions,
            'average_prediction': round(avg_prediction, 2),
            'confidence': round(confidence, 2),
            'multi_day_predictions': multi_day_predictions,
            'recommendation': 'Buy' if avg_prediction > current_price * 1.02 else 'Hold' if avg_prediction > current_price * 0.98 else 'Sell'
        }

# ==================== DATABASE ====================
class DatabaseManager:
    """Manage model persistence"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                symbol TEXT PRIMARY KEY,
                model_data BLOB,
                scaler_data BLOB,
                feature_columns TEXT,
                trained_at TIMESTAMP,
                scores TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_model(self, symbol: str, ml_models: MLModels, scores: Dict):
        """Save trained model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        model_data = pickle.dumps(ml_models.models[symbol])
        scaler_data = pickle.dumps(ml_models.scalers[symbol])
        feature_columns = json.dumps(ml_models.feature_columns)
        scores_json = json.dumps(scores)
        
        cursor.execute("""
            INSERT OR REPLACE INTO models (symbol, model_data, scaler_data, feature_columns, trained_at, scores)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, model_data, scaler_data, feature_columns, datetime.now(), scores_json))
        
        conn.commit()
        conn.close()
    
    def load_model(self, symbol: str, ml_models: MLModels) -> bool:
        """Load saved model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT model_data, scaler_data, feature_columns, trained_at
            FROM models WHERE symbol = ?
        """, (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            ml_models.models[symbol] = pickle.loads(row[0])
            ml_models.scalers[symbol] = pickle.loads(row[1])
            ml_models.feature_columns = json.loads(row[2])
            
            # Check if model is recent (less than 24 hours old)
            trained_at = datetime.fromisoformat(row[3])
            age_hours = (datetime.now() - trained_at).total_seconds() / 3600
            
            if age_hours < 24:
                logger.info(f"Loaded cached model for {symbol} (age: {age_hours:.1f} hours)")
                return True
            else:
                logger.info(f"Model for {symbol} is outdated ({age_hours:.1f} hours old)")
                return False
        
        return False

# ==================== MAIN ML SYSTEM ====================
class MLStockPredictor:
    """Main ML system orchestrator"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.feature_engineer = FeatureEngineer()
        self.ml_models = MLModels()
        self.db_manager = DatabaseManager()
        self.cache = {}
        self.cache_timestamps = {}
    
    def train_and_predict(self, symbol: str, period: str = "6mo", use_cache: bool = True) -> Dict:
        """Train model and make predictions"""
        
        # Check cache
        cache_key = f"{symbol}_{period}"
        if use_cache and cache_key in self.cache:
            cache_age = (datetime.now() - self.cache_timestamps[cache_key]).total_seconds()
            if cache_age < CACHE_DURATION:
                logger.info(f"Using cached results for {symbol} (age: {cache_age:.0f}s)")
                return self.cache[cache_key]
        
        try:
            # Try to load existing model
            if use_cache and self.db_manager.load_model(symbol, self.ml_models):
                # Just fetch recent data for prediction
                df = self.data_fetcher.fetch_stock_data(symbol, period="1mo")
                df = self.feature_engineer.add_technical_indicators(df)
                result = self.ml_models.predict(symbol, df)
                
                # Cache result
                self.cache[cache_key] = result
                self.cache_timestamps[cache_key] = datetime.now()
                
                return result
            
            # Fetch data
            logger.info(f"Fetching full training data for {symbol}...")
            df = self.data_fetcher.fetch_stock_data(symbol, period)
            
            # Add technical indicators
            df = self.feature_engineer.add_technical_indicators(df)
            
            # Prepare features
            X, y = self.ml_models.prepare_features(df)
            
            # Train models
            scores = self.ml_models.train_models(X, y, symbol)
            
            # Save model
            self.db_manager.save_model(symbol, self.ml_models, scores)
            
            # Make predictions
            result = self.ml_models.predict(symbol, df)
            result['model_scores'] = scores
            
            # Cache result
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in train_and_predict: {e}")
            raise

# ==================== WEB INTERFACE HTML ====================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Stock Predictor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 30px; text-align: center; }
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
            background: #d4f4dd;
            color: #00aa00;
        }
        .input-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-weight: 600;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #5a67d8; }
        .quick-symbols {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        .symbol-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 20px;
            cursor: pointer;
        }
        .symbol-btn:hover {
            background: #667eea;
            color: white;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .results.show { display: block; }
        .error {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 5px;
        }
        .success {
            background: #efe;
            color: #060;
            padding: 15px;
            border-radius: 5px;
        }
        .price-card {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .recommendation {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }
        .recommendation.buy { background: #d4f4dd; color: #00aa00; }
        .recommendation.sell { background: #fdd4d4; color: #aa0000; }
        .recommendation.hold { background: #fdf4d4; color: #aa7700; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ML Stock Predictor</h1>
        
        <div class="status">✅ Server Running - Ready for Predictions</div>
        
        <div class="input-group">
            <label for="symbol">Stock Symbol</label>
            <input type="text" id="symbol" placeholder="Enter stock symbol (e.g., AAPL)" value="AAPL">
            
            <div class="quick-symbols">
                <div class="symbol-btn" onclick="setSymbol('AAPL')">AAPL</div>
                <div class="symbol-btn" onclick="setSymbol('MSFT')">MSFT</div>
                <div class="symbol-btn" onclick="setSymbol('GOOGL')">GOOGL</div>
                <div class="symbol-btn" onclick="setSymbol('AMZN')">AMZN</div>
                <div class="symbol-btn" onclick="setSymbol('TSLA')">TSLA</div>
                <div class="symbol-btn" onclick="setSymbol('META')">META</div>
                <div class="symbol-btn" onclick="setSymbol('NVDA')">NVDA</div>
                <div class="symbol-btn" onclick="setSymbol('SPY')">SPY</div>
            </div>
        </div>
        
        <div class="input-group">
            <label for="period">Training Period</label>
            <select id="period">
                <option value="1mo">1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo" selected>6 Months</option>
                <option value="1y">1 Year</option>
            </select>
        </div>
        
        <div class="button-group">
            <button onclick="testConnection()">Test Connection</button>
            <button onclick="getPrediction()">Get Prediction</button>
        </div>
        
        <div id="results" class="results"></div>
    </div>
    
    <script>
        function setSymbol(symbol) {
            document.getElementById('symbol').value = symbol;
        }
        
        async function testConnection() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            showLoading();
            try {
                const response = await fetch(`/test/${symbol}`);
                const data = await response.json();
                
                if (data.success) {
                    showSuccess(`
                        <h3>✅ Connection Successful!</h3>
                        <p><strong>${symbol}</strong></p>
                        <p>Latest Price: $${data.latest_price.toFixed(2)}</p>
                        <p>Records: ${data.records}</p>
                        <p>Date: ${data.date}</p>
                    `);
                } else {
                    showError(data.detail || 'Failed to fetch data');
                }
            } catch (error) {
                showError('Connection error: ' + error.message);
            }
        }
        
        async function getPrediction() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            showLoading();
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, days: 5})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayPrediction(data.data, symbol);
                } else {
                    showError(data.detail || 'Prediction failed');
                }
            } catch (error) {
                showError('Prediction error: ' + error.message);
            }
        }
        
        function displayPrediction(data, symbol) {
            const recClass = data.recommendation.toLowerCase();
            
            let html = `
                <h2>Prediction for ${symbol}</h2>
                
                <div class="price-card">
                    <div>Current Price: <strong>$${data.current_price.toFixed(2)}</strong></div>
                    <div>Predicted Price: <strong>$${data.average_prediction.toFixed(2)}</strong></div>
                    <div>Confidence: <strong>${data.confidence.toFixed(1)}%</strong></div>
                </div>
                
                <div class="recommendation ${recClass}">
                    ${data.recommendation}
                </div>
                
                <h3>5-Day Forecast</h3>
                <ul>`;
            
            for (const pred of data.multi_day_predictions) {
                const change = ((pred.price - data.current_price) / data.current_price * 100).toFixed(1);
                const sign = change > 0 ? '+' : '';
                html += `<li>Day ${pred.day}: $${pred.price.toFixed(2)} (${sign}${change}%)</li>`;
            }
            
            html += '</ul>';
            
            if (data.model_scores) {
                html += '<h3>Model Performance</h3><ul>';
                for (const [model, scores] of Object.entries(data.model_scores)) {
                    html += `<li>${model}: Test Score ${(scores.test_score * 100).toFixed(1)}%</li>`;
                }
                html += '</ul>';
            }
            
            showResults(html);
        }
        
        function showLoading() {
            document.getElementById('results').innerHTML = '<div>Loading...</div>';
            document.getElementById('results').className = 'results show';
        }
        
        function showError(message) {
            showResults(`<div class="error">${message}</div>`);
        }
        
        function showSuccess(message) {
            showResults(`<div class="success">${message}</div>`);
        }
        
        function showResults(html) {
            document.getElementById('results').innerHTML = html;
            document.getElementById('results').className = 'results show';
        }
    </script>
</body>
</html>
"""

# ==================== FAST API ====================
app = FastAPI(title="ML Stock Predictor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML system
ml_system = MLStockPredictor()

# ==================== API ENDPOINTS ====================

class PredictionRequest(BaseModel):
    symbol: str
    period: str = "6mo"
    days: int = 5

@app.get("/")
async def root():
    return HTMLResponse(HTML_INTERFACE)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0",
        "yfinance_version": yf.__version__
    }

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Main prediction endpoint"""
    try:
        result = ml_system.train_and_predict(
            symbol=request.symbol.upper(),
            period=request.period
        )
        
        return JSONResponse({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return JSONResponse({
            "success": False,
            "detail": str(e)
        }, status_code=500)

@app.get("/test/{symbol}")
async def test_symbol(symbol: str):
    """Quick test endpoint"""
    try:
        # Clear cache before testing
        ml_system.data_fetcher.clear_cache()
        
        # Fetch data
        df = ml_system.data_fetcher.fetch_stock_data(symbol.upper(), period="5d")
        
        # Get latest price safely
        if 'Close' in df.columns:
            latest_price = float(df['Close'].iloc[-1])
        else:
            latest_price = 0.0
        
        # Format date safely
        try:
            date_str = df.index[-1].strftime("%Y-%m-%d")
        except:
            date_str = str(df.index[-1])[:10]
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "records": len(df),
            "latest_price": latest_price,
            "date": date_str
        }
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "detail": str(e)
        }, status_code=500)

# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*60)
    print("ML Stock Predictor - Starting")
    print("="*60)
    print(f"yfinance version: {yf.__version__}")
    print(f"Server starting on http://localhost:{PORT}")
    print("="*60)
    
    # Clear cache on startup
    DataFetcher.clear_cache()
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=PORT)