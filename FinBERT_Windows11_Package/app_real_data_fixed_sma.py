#!/usr/bin/env python3
"""
FinBERT Trading System - FIXED SMA ERROR VERSION
Handles stocks with limited historical data gracefully
"""

import os
import sys
import json
import time
import logging
import warnings
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')

# Core imports
import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Data source
import yfinance as yf

# Try additional sources
try:
    from alpha_vantage.timeseries import TimeSeries
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False

try:
    import pandas_datareader as pdr
    DATAREADER_AVAILABLE = True
except ImportError:
    DATAREADER_AVAILABLE = False

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Try FinBERT
FINBERT_AVAILABLE = False
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "ProsusAI/finbert"
    
    FINBERT_TOKENIZER = AutoTokenizer.from_pretrained(model_name, cache_dir="./models")
    FINBERT_MODEL = AutoModelForSequenceClassification.from_pretrained(
        model_name, cache_dir="./models"
    ).to(device)
    FINBERT_MODEL.eval()
    FINBERT_AVAILABLE = True
    logger.info("✓ FinBERT loaded successfully")
except Exception as e:
    logger.warning(f"FinBERT not available: {e}")

# Flask app
app = Flask(__name__)
CORS(app)

class RobustDataFetcher:
    """Fetches REAL data with robust error handling"""
    
    def __init__(self):
        self.cache_dir = Path("./cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_stock_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch REAL stock data"""
        
        logger.info(f"Fetching data for {symbol} ({period})")
        
        # Try multiple methods
        df = pd.DataFrame()
        
        # Method 1: Yahoo Finance Ticker
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if not df.empty:
                logger.info(f"✓ Yahoo Ticker: {len(df)} days fetched")
                return df
        except Exception as e:
            logger.warning(f"Yahoo Ticker failed: {e}")
        
        # Method 2: yfinance download
        try:
            df = yf.download(symbol, period=period, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            if not df.empty:
                logger.info(f"✓ Yahoo Download: {len(df)} days fetched")
                return df
        except Exception as e:
            logger.warning(f"Yahoo Download failed: {e}")
        
        # Method 3: Specific date range (get more data)
        try:
            end_date = datetime.now()
            # Try to get MORE data to ensure we have enough
            period_days = {
                '1mo': 60,    # Get 2 months for 1mo request
                '3mo': 120,   # Get 4 months for 3mo request
                '6mo': 365,   # Get 1 year for 6mo request
                '1y': 730,    # Get 2 years for 1y request
                '2y': 1095,   # Get 3 years for 2y request
                '5y': 2190,   # Get 6 years for 5y request
                'max': 3650   # Get 10 years for max
            }
            days = period_days.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            df = yf.download(
                symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            if not df.empty:
                logger.info(f"✓ Extended period: {len(df)} days fetched")
                return df
        except Exception as e:
            logger.warning(f"Extended period failed: {e}")
        
        logger.error(f"No data available for {symbol}")
        return pd.DataFrame()

class AdaptiveMLModel:
    """ML model that adapts to available data"""
    
    def __init__(self):
        self.fetcher = RobustDataFetcher()
        self.models = {}
        self.scalers = {}
        
    def prepare_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Prepare features adapting to data availability"""
        
        if df.empty:
            raise ValueError("No data available")
        
        data_length = len(df)
        logger.info(f"Preparing features for {data_length} data points")
        
        features = df.copy()
        
        # Basic features (always available)
        features['Returns'] = features['Close'].pct_change()
        features['Log_Returns'] = np.log(features['Close'] / features['Close'].shift(1))
        features['High_Low_Ratio'] = features['High'] / (features['Low'] + 0.0001)
        features['Close_Open_Ratio'] = features['Close'] / (features['Open'] + 0.0001)
        
        # Volume features
        if 'Volume' in features.columns:
            features['Volume_Change'] = features['Volume'].pct_change()
            # Adaptive volume ratio based on data length
            vol_period = min(20, data_length // 3)
            if vol_period > 1:
                features[f'Volume_Ratio_{vol_period}'] = features['Volume'] / features['Volume'].rolling(vol_period, min_periods=1).mean()
        
        # Adaptive Moving Averages - only add if we have enough data
        sma_periods = []
        if data_length >= 5:
            sma_periods.append(5)
        if data_length >= 10:
            sma_periods.append(10)
        if data_length >= 20:
            sma_periods.append(20)
        if data_length >= 50:
            sma_periods.append(50)
        if data_length >= 100:
            sma_periods.append(100)
        
        for period in sma_periods:
            features[f'SMA_{period}'] = features['Close'].rolling(period, min_periods=period//2).mean()
            features[f'Price_to_SMA_{period}'] = features['Close'] / (features[f'SMA_{period}'] + 0.0001)
        
        # RSI - adaptive period
        rsi_period = min(14, data_length // 3)
        if rsi_period > 2:
            delta = features['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(rsi_period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(rsi_period, min_periods=1).mean()
            rs = gain / (loss + 0.0001)
            features['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD - only if enough data
        if data_length >= 26:
            exp1 = features['Close'].ewm(span=12, adjust=False).mean()
            exp2 = features['Close'].ewm(span=26, adjust=False).mean()
            features['MACD'] = exp1 - exp2
            features['MACD_Signal'] = features['MACD'].ewm(span=9, adjust=False).mean()
            features['MACD_Histogram'] = features['MACD'] - features['MACD_Signal']
        
        # Bollinger Bands - adaptive period
        bb_period = min(20, data_length // 3)
        if bb_period > 2:
            sma_bb = features['Close'].rolling(bb_period, min_periods=1).mean()
            std_bb = features['Close'].rolling(bb_period, min_periods=1).std()
            features['BB_Upper'] = sma_bb + (std_bb * 2)
            features['BB_Lower'] = sma_bb - (std_bb * 2)
            features['BB_Width'] = features['BB_Upper'] - features['BB_Lower']
            features['BB_Position'] = (features['Close'] - features['BB_Lower']) / (features['BB_Width'] + 0.0001)
        
        # Volatility - adaptive period
        vol_period = min(20, data_length // 3)
        if vol_period > 1:
            features[f'Volatility_{vol_period}'] = features['Returns'].rolling(vol_period, min_periods=1).std()
        
        # ATR - adaptive period
        atr_period = min(14, data_length // 3)
        if atr_period > 1:
            high_low = features['High'] - features['Low']
            high_close = np.abs(features['High'] - features['Close'].shift())
            low_close = np.abs(features['Low'] - features['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            features['ATR'] = pd.Series(true_range).rolling(atr_period, min_periods=1).mean()
        
        # Add basic economic indicators
        try:
            # Get VIX
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d")
            if not vix_data.empty:
                features['VIX'] = float(vix_data['Close'].iloc[-1])
            else:
                features['VIX'] = 20  # Default VIX
        except:
            features['VIX'] = 20
        
        # Target variable
        features['Target'] = (features['Close'].shift(-1) > features['Close']).astype(int)
        
        # Clean up
        features = features.replace([np.inf, -np.inf], 0)
        features = features.fillna(0)
        
        return features
    
    def train(self, symbol: str, period: str = "6mo") -> dict:
        """Train model with adaptive feature selection"""
        
        try:
            # Fetch data
            df = self.fetcher.get_stock_data(symbol, period)
            
            if df.empty:
                return {
                    "error": "No data available",
                    "suggestions": [
                        "Check internet connection",
                        "Try a different symbol",
                        "Try a longer time period"
                    ]
                }
            
            data_length = len(df)
            
            # Adjust minimum requirements based on data
            min_required = 30  # Lowered from 50
            
            if data_length < min_required:
                return {
                    "error": f"Only {data_length} days available (need {min_required}+)",
                    "suggestions": [
                        f"Try a longer period (1y or 2y)",
                        "Try a major stock (AAPL, MSFT, SPY)",
                        "Check if symbol is correct"
                    ]
                }
            
            # Prepare features
            features = self.prepare_features(df, symbol)
            
            # Select only existing features (no missing columns error)
            feature_cols = []
            for col in features.columns:
                if col not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
                    if not features[col].isna().all():  # Skip all-NaN columns
                        feature_cols.append(col)
            
            logger.info(f"Using {len(feature_cols)} features: {feature_cols[:10]}...")
            
            if len(feature_cols) < 3:
                return {
                    "error": "Not enough features could be calculated",
                    "suggestions": ["Try a longer time period for more features"]
                }
            
            X = features[feature_cols].values[:-1]  # Remove last row
            y = features['Target'].values[:-1]
            
            # Ensure we have enough samples
            if len(X) < 20:
                return {
                    "error": f"Only {len(X)} samples after processing",
                    "suggestions": ["Need more historical data"]
                }
            
            # Split data
            split_idx = int(len(X) * 0.8)
            split_idx = max(10, split_idx)  # Ensure at least 10 training samples
            
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Scale
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model - use simpler model for less data
            if len(X_train) < 100:
                # Simpler model for small datasets
                model = RandomForestClassifier(
                    n_estimators=50,  # Fewer trees
                    max_depth=5,      # Shallower trees
                    min_samples_split=2,
                    min_samples_leaf=1,
                    random_state=42
                )
            else:
                # Standard model for larger datasets
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42
                )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test) if len(X_test) > 0 else train_score
            
            # Store model
            self.models[symbol] = {
                'model': model,
                'scaler': scaler,
                'features': feature_cols,
                'data_length': data_length
            }
            
            # Feature importance
            importance = sorted(
                zip(feature_cols, model.feature_importances_),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "data_days": data_length,
                "samples": len(X),
                "features": len(feature_cols),
                "train_accuracy": float(train_score),
                "test_accuracy": float(test_score),
                "feature_importance": [
                    {"feature": f, "importance": float(i)}
                    for f, i in importance
                ],
                "note": f"Model adapted to {data_length} days of data"
            }
            
        except Exception as e:
            logger.error(f"Training error: {traceback.format_exc()}")
            return {
                "error": str(e),
                "suggestions": [
                    "Try a different symbol",
                    "Try a longer time period",
                    "Check if markets are open"
                ]
            }
    
    def predict(self, symbol: str) -> dict:
        """Make prediction with stored model"""
        
        if symbol not in self.models:
            # Auto-train
            result = self.train(symbol)
            if "error" in result:
                return result
        
        try:
            # Get recent data - try to get extra to ensure features work
            df = self.fetcher.get_stock_data(symbol, "3mo")  # Get 3 months for prediction
            if df.empty:
                df = self.fetcher.get_stock_data(symbol, "1mo")  # Fallback to 1 month
            
            if df.empty:
                return {"error": "No recent data available"}
            
            features = self.prepare_features(df, symbol)
            
            model_data = self.models[symbol]
            model = model_data['model']
            scaler = model_data['scaler']
            feature_cols = model_data['features']
            
            # Get only the features that exist
            available_features = []
            missing_features = []
            for col in feature_cols:
                if col in features.columns:
                    available_features.append(col)
                else:
                    missing_features.append(col)
            
            if missing_features:
                logger.warning(f"Missing features for prediction: {missing_features}")
                # Add zero columns for missing features
                for col in missing_features:
                    features[col] = 0
            
            # Now we can safely get all features
            X = features[feature_cols].iloc[-1:].values
            X_scaled = scaler.transform(X)
            
            # Predict
            pred = model.predict(X_scaled)[0]
            prob = model.predict_proba(X_scaled)[0]
            
            return {
                "success": True,
                "symbol": symbol,
                "prediction": "BUY" if pred == 1 else "SELL",
                "confidence": float(max(prob)),
                "probability_up": float(prob[1]),
                "probability_down": float(prob[0]),
                "current_price": float(df['Close'].iloc[-1]),
                "data_days": len(df),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {traceback.format_exc()}")
            return {"error": str(e)}

# Initialize
ml_model = AdaptiveMLModel()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FinBERT Trading - Fixed SMA Error</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px; 
            margin: auto; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .info-box {
            background: #e8f5e9;
            border: 2px solid #4caf50;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        input, select {
            padding: 10px;
            margin: 5px;
            width: 250px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
        }
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .success {
            color: #155724;
            background: #d4edda;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .result {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .badge {
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 FinBERT Trading System</h1>
        <p style="color: #6c757d;">
            <span class="badge">FIXED SMA ERROR</span>
            Adaptive feature selection - works with any amount of data
        </p>
    </div>
    
    <div class="info-box">
        <strong>✅ SMA Error Fixed!</strong><br>
        This version automatically adapts to available data:
        <ul style="margin: 10px 0;">
            <li>Only uses SMA_50 if 50+ days available</li>
            <li>Falls back to shorter periods for newer stocks</li>
            <li>Minimum requirement reduced to 30 days</li>
            <li>Works with IPO stocks and limited history</li>
        </ul>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>🎯 Train Model</h2>
            <p style="color: #6c757d; font-size: 14px;">
                Automatically adapts to available data length
            </p>
            <div style="margin: 20px 0;">
                <input id="symbol" placeholder="Symbol (e.g., AAPL)" value="AAPL">
                <select id="period">
                    <option value="1mo">1 Month (Quick)</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo" selected>6 Months (Recommended)</option>
                    <option value="1y">1 Year</option>
                    <option value="2y">2 Years</option>
                </select>
                <button onclick="train()">Train Model</button>
            </div>
            <div id="trainResult"></div>
        </div>
        
        <div class="card">
            <h2>🔮 Make Prediction</h2>
            <p style="color: #6c757d; font-size: 14px;">
                Uses adaptive features for prediction
            </p>
            <div style="margin: 20px 0;">
                <input id="predictSymbol" placeholder="Symbol" value="AAPL">
                <button onclick="predict()">Get Prediction</button>
            </div>
            <div id="predictResult"></div>
        </div>
    </div>
    
    <div class="card">
        <h2>📊 Common Stocks to Test</h2>
        <p style="color: #6c757d;">Click to auto-fill symbol:</p>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px;">
            <button onclick="setSymbol('AAPL')" style="padding: 8px 15px;">AAPL</button>
            <button onclick="setSymbol('MSFT')" style="padding: 8px 15px;">MSFT</button>
            <button onclick="setSymbol('GOOGL')" style="padding: 8px 15px;">GOOGL</button>
            <button onclick="setSymbol('SPY')" style="padding: 8px 15px;">SPY</button>
            <button onclick="setSymbol('QQQ')" style="padding: 8px 15px;">QQQ</button>
            <button onclick="setSymbol('TSLA')" style="padding: 8px 15px;">TSLA</button>
            <button onclick="setSymbol('BTC-USD')" style="padding: 8px 15px;">BTC</button>
            <button onclick="setSymbol('^VIX')" style="padding: 8px 15px;">VIX</button>
            <button onclick="setSymbol('CBA.AX')" style="padding: 8px 15px;">CBA (ASX)</button>
            <button onclick="setSymbol('BHP.AX')" style="padding: 8px 15px;">BHP (ASX)</button>
        </div>
    </div>
    
    <script>
        function setSymbol(sym) {
            document.getElementById('symbol').value = sym;
            document.getElementById('predictSymbol').value = sym;
        }
        
        async function train() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const resultDiv = document.getElementById('trainResult');
            
            resultDiv.innerHTML = '<div style="color: #667eea;">⏳ Training with adaptive features...</div>';
            
            try {
                const response = await fetch('/api/train', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    let html = `<div class="error">❌ ${data.error}</div>`;
                    if (data.suggestions) {
                        html += '<ul>';
                        data.suggestions.forEach(s => html += `<li>${s}</li>`);
                        html += '</ul>';
                    }
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `
                        <div class="success">
                            ✅ Training Complete!
                            <div style="margin-top: 15px;">
                                <strong>Data:</strong> ${data.data_days} days<br>
                                <strong>Features:</strong> ${data.features} (adapted)<br>
                                <strong>Accuracy:</strong> ${(data.test_accuracy * 100).toFixed(2)}%<br>
                                <strong>Note:</strong> ${data.note}
                            </div>
                        </div>`;
                }
            } catch (e) {
                resultDiv.innerHTML = `<div class="error">Error: ${e}</div>`;
            }
        }
        
        async function predict() {
            const symbol = document.getElementById('predictSymbol').value;
            const resultDiv = document.getElementById('predictResult');
            
            resultDiv.innerHTML = '<div style="color: #667eea;">⏳ Making prediction...</div>';
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                } else {
                    const color = data.prediction === 'BUY' ? '#28a745' : '#dc3545';
                    resultDiv.innerHTML = `
                        <div class="result">
                            <div style="font-size: 28px; font-weight: bold; color: ${color};">
                                ${data.prediction}
                            </div>
                            <div style="margin-top: 15px;">
                                <strong>Price:</strong> $${data.current_price.toFixed(2)}<br>
                                <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%<br>
                                <strong>Up Probability:</strong> ${(data.probability_up * 100).toFixed(1)}%<br>
                                <strong>Data Used:</strong> ${data.data_days} days
                            </div>
                        </div>`;
                }
            } catch (e) {
                resultDiv.innerHTML = `<div class="error">Error: ${e}</div>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/train', methods=['POST'])
def train():
    data = request.json
    result = ml_model.train(data.get('symbol', 'AAPL'), data.get('period', '6mo'))
    return jsonify(result)

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    result = ml_model.predict(data.get('symbol', 'AAPL'))
    return jsonify(result)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("FinBERT Trading System - FIXED SMA ERROR VERSION")
    print("="*70)
    print("✓ Adaptive feature selection")
    print("✓ Works with limited data (30+ days)")
    print("✓ No more 'SMA_50 not in index' errors")
    print("✓ Automatically adjusts to available history")
    print("="*70)
    print("Server starting at http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)