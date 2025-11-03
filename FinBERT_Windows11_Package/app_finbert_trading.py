#!/usr/bin/env python3
"""
FinBERT-Enhanced Stock Trading System for Windows 11
Complete implementation with proper dependency handling and fallback mechanisms
"""

import os
import sys
import json
import time
import logging
import warnings
import datetime as dt
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/finbert_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Import standard libraries
import numpy as np
import pandas as pd
import yfinance as yf
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from tqdm import tqdm

# Import ML libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler

# Try to import FinBERT dependencies with proper error handling
FINBERT_AVAILABLE = False
FINBERT_MODEL = None
FINBERT_TOKENIZER = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"PyTorch device: {device}")
    
    # Try to load FinBERT model
    try:
        model_name = "ProsusAI/finbert"
        cache_dir = "./models"
        
        logger.info("Loading FinBERT model...")
        FINBERT_TOKENIZER = AutoTokenizer.from_pretrained(
            model_name, 
            cache_dir=cache_dir,
            local_files_only=False
        )
        FINBERT_MODEL = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            local_files_only=False
        ).to(device)
        FINBERT_MODEL.eval()
        FINBERT_AVAILABLE = True
        logger.info("✓ FinBERT model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load FinBERT model: {e}")
        logger.info("Will use fallback sentiment analysis")
        
except ImportError as e:
    logger.warning(f"FinBERT dependencies not available: {e}")
    logger.info("Using fallback sentiment analysis (install torch and transformers for FinBERT)")

# Configuration
app = Flask(__name__)
CORS(app)

CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(exist_ok=True)

# Australian stocks for default portfolio
DEFAULT_SYMBOLS = [
    "CBA.AX", "BHP.AX", "CSL.AX", "NAB.AX", "WBC.AX",
    "ANZ.AX", "WES.AX", "MQG.AX", "GMG.AX", "WOW.AX",
    "TLS.AX", "RIO.AX", "FMG.AX", "TCL.AX", "WDS.AX"
]

class FinBERTSentimentAnalyzer:
    """FinBERT-based sentiment analyzer with fallback"""
    
    def __init__(self):
        self.use_finbert = FINBERT_AVAILABLE
        self.model = FINBERT_MODEL
        self.tokenizer = FINBERT_TOKENIZER
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if self.use_finbert else None
        
        # Fallback sentiment words
        self.positive_words = {
            'positive', 'gain', 'gains', 'rise', 'rises', 'growth', 'surge', 'surges',
            'profit', 'profits', 'beat', 'beats', 'strong', 'strength', 'bullish',
            'outperform', 'upgrade', 'upgraded', 'buy', 'accumulate', 'recovery',
            'improve', 'improvement', 'boost', 'boosted', 'rally', 'rallies'
        }
        
        self.negative_words = {
            'negative', 'loss', 'losses', 'fall', 'falls', 'decline', 'declines',
            'drop', 'drops', 'weak', 'weakness', 'bearish', 'underperform',
            'downgrade', 'downgraded', 'sell', 'reduce', 'recession', 'crisis',
            'concern', 'concerns', 'risk', 'risks', 'threat', 'threats', 'miss', 'misses'
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment with FinBERT or fallback"""
        if not text or not isinstance(text, str):
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "score": 0.0}
        
        if self.use_finbert:
            try:
                return self._finbert_sentiment(text)
            except Exception as e:
                logger.error(f"FinBERT analysis failed: {e}")
                return self._fallback_sentiment(text)
        else:
            return self._fallback_sentiment(text)
    
    def _finbert_sentiment(self, text: str) -> Dict[str, float]:
        """Use FinBERT for sentiment analysis"""
        # Truncate text to model's max length
        max_length = 512
        if len(text) > max_length * 4:  # Rough character to token ratio
            text = text[:max_length * 4]
        
        # Tokenize and get predictions
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=max_length
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predictions = predictions.cpu().numpy()[0]
        
        # FinBERT output order: positive, negative, neutral
        sentiment_scores = {
            "positive": float(predictions[0]),
            "negative": float(predictions[1]),
            "neutral": float(predictions[2])
        }
        
        # Calculate overall score (-1 to 1)
        score = sentiment_scores["positive"] - sentiment_scores["negative"]
        sentiment_scores["score"] = score
        
        return sentiment_scores
    
    def _fallback_sentiment(self, text: str) -> Dict[str, float]:
        """Fallback keyword-based sentiment analysis"""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        positive_count = len(words.intersection(self.positive_words))
        negative_count = len(words.intersection(self.negative_words))
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "score": 0.0}
        
        positive_ratio = positive_count / total_count
        negative_ratio = negative_count / total_count
        
        # Create probability-like scores
        if positive_ratio > negative_ratio:
            pos_score = 0.4 + (positive_ratio * 0.4)
            neg_score = 0.2 - (positive_ratio * 0.1)
            neu_score = 1 - pos_score - neg_score
        elif negative_ratio > positive_ratio:
            neg_score = 0.4 + (negative_ratio * 0.4)
            pos_score = 0.2 - (negative_ratio * 0.1)
            neu_score = 1 - pos_score - neg_score
        else:
            pos_score = neg_score = 0.3
            neu_score = 0.4
        
        return {
            "positive": max(0, min(1, pos_score)),
            "negative": max(0, min(1, neg_score)),
            "neutral": max(0, min(1, neu_score)),
            "score": pos_score - neg_score
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Analyze multiple texts"""
        results = []
        for text in tqdm(texts, desc="Analyzing sentiment"):
            results.append(self.analyze_sentiment(text))
        return results

class StockDataManager:
    """Manage stock data fetching and caching"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "stock_data_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """Fetch stock data with caching"""
        cache_key = f"{symbol}_{period}_{dt.date.today()}"
        
        if cache_key in self.cache:
            logger.info(f"Using cached data for {symbol}")
            df = pd.DataFrame(self.cache[cache_key])
            df.index = pd.to_datetime(df.index)
            return df
        
        try:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            # Cache the data
            self.cache[cache_key] = df.to_dict()
            self._save_cache()
            
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def get_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Fetch news for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:limit] if hasattr(ticker, 'news') else []
            return news
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

class MLTradingModel:
    """Machine Learning trading model with sentiment integration"""
    
    def __init__(self, sentiment_analyzer: FinBERTSentimentAnalyzer):
        self.sentiment_analyzer = sentiment_analyzer
        self.data_manager = StockDataManager()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
    
    def prepare_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Prepare features including technical indicators and sentiment"""
        features = df.copy()
        
        # Technical indicators
        features['Returns'] = features['Close'].pct_change()
        features['SMA_20'] = features['Close'].rolling(20).mean()
        features['SMA_50'] = features['Close'].rolling(50).mean()
        features['RSI'] = self._calculate_rsi(features['Close'])
        features['Volume_Ratio'] = features['Volume'] / features['Volume'].rolling(20).mean()
        
        # Price ratios
        features['Price_SMA20_Ratio'] = features['Close'] / features['SMA_20']
        features['Price_SMA50_Ratio'] = features['Close'] / features['SMA_50']
        
        # Volatility
        features['Volatility'] = features['Returns'].rolling(20).std()
        
        # MACD
        exp1 = features['Close'].ewm(span=12, adjust=False).mean()
        exp2 = features['Close'].ewm(span=26, adjust=False).mean()
        features['MACD'] = exp1 - exp2
        features['MACD_Signal'] = features['MACD'].ewm(span=9, adjust=False).mean()
        
        # Sentiment features (if symbol provided)
        if symbol:
            news = self.data_manager.get_news(symbol)
            if news:
                sentiments = []
                for article in news[:5]:  # Use last 5 news items
                    text = f"{article.get('title', '')} {article.get('summary', '')}"
                    sentiment = self.sentiment_analyzer.analyze_sentiment(text)
                    sentiments.append(sentiment['score'])
                
                features['Sentiment_Score'] = np.mean(sentiments) if sentiments else 0
                features['Sentiment_Std'] = np.std(sentiments) if len(sentiments) > 1 else 0
            else:
                features['Sentiment_Score'] = 0
                features['Sentiment_Std'] = 0
        
        # Target variable (1 if price goes up, 0 otherwise)
        features['Target'] = (features['Close'].shift(-1) > features['Close']).astype(int)
        
        return features
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_model(self, symbol: str) -> Dict:
        """Train a model for a specific symbol"""
        logger.info(f"Training model for {symbol}")
        
        # Get data
        df = self.data_manager.get_stock_data(symbol, period="6mo")
        if df.empty:
            return {"error": f"No data available for {symbol}"}
        
        # Prepare features
        features = self.prepare_features(df, symbol)
        features = features.dropna()
        
        if len(features) < 50:
            return {"error": f"Insufficient data for {symbol}"}
        
        # Select feature columns
        feature_cols = [
            'Returns', 'SMA_20', 'SMA_50', 'RSI', 'Volume_Ratio',
            'Price_SMA20_Ratio', 'Price_SMA50_Ratio', 'Volatility',
            'MACD', 'MACD_Signal', 'Sentiment_Score', 'Sentiment_Std'
        ]
        
        X = features[feature_cols]
        y = features['Target']
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model and scaler
        self.models[symbol] = model
        self.scalers[symbol] = scaler
        self.feature_importance[symbol] = importance
        
        return {
            "symbol": symbol,
            "train_accuracy": float(train_score),
            "test_accuracy": float(test_score),
            "feature_importance": importance.to_dict('records'),
            "finbert_enabled": FINBERT_AVAILABLE
        }
    
    def predict(self, symbol: str) -> Dict:
        """Make prediction for a symbol"""
        if symbol not in self.models:
            # Train model if not exists
            result = self.train_model(symbol)
            if "error" in result:
                return result
        
        # Get latest data
        df = self.data_manager.get_stock_data(symbol, period="1mo")
        if df.empty:
            return {"error": f"No data available for {symbol}"}
        
        # Prepare features
        features = self.prepare_features(df, symbol)
        features = features.dropna()
        
        if features.empty:
            return {"error": "Insufficient data for prediction"}
        
        # Get latest features
        feature_cols = [
            'Returns', 'SMA_20', 'SMA_50', 'RSI', 'Volume_Ratio',
            'Price_SMA20_Ratio', 'Price_SMA50_Ratio', 'Volatility',
            'MACD', 'MACD_Signal', 'Sentiment_Score', 'Sentiment_Std'
        ]
        
        X = features[feature_cols].iloc[-1:].values
        X_scaled = self.scalers[symbol].transform(X)
        
        # Make prediction
        prediction = self.models[symbol].predict(X_scaled)[0]
        probability = self.models[symbol].predict_proba(X_scaled)[0]
        
        # Get current price and calculate potential
        current_price = float(df['Close'].iloc[-1])
        
        return {
            "symbol": symbol,
            "prediction": "BUY" if prediction == 1 else "SELL",
            "probability": {
                "up": float(probability[1]),
                "down": float(probability[0])
            },
            "current_price": current_price,
            "sentiment_score": float(features['Sentiment_Score'].iloc[-1]),
            "rsi": float(features['RSI'].iloc[-1]),
            "finbert_enabled": FINBERT_AVAILABLE,
            "timestamp": dt.datetime.now().isoformat()
        }

# Initialize components
sentiment_analyzer = FinBERTSentimentAnalyzer()
trading_model = MLTradingModel(sentiment_analyzer)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinBERT Trading System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-right: 10px;
        }
        
        .status-active {
            background: #10b981;
            color: white;
        }
        
        .status-fallback {
            background: #f59e0b;
            color: white;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #666;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .results {
            margin-top: 20px;
        }
        
        .result-item {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .result-label {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 5px;
        }
        
        .result-value {
            color: #1e293b;
            font-size: 18px;
            font-weight: 600;
        }
        
        .prediction-buy {
            color: #10b981;
        }
        
        .prediction-sell {
            color: #ef4444;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e2e8f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
            transition: width 0.5s ease;
        }
        
        .feature-importance {
            margin-top: 20px;
        }
        
        .feature-bar {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .feature-name {
            width: 150px;
            font-size: 14px;
            color: #64748b;
        }
        
        .feature-bar-bg {
            flex: 1;
            height: 20px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .feature-bar-fill {
            height: 100%;
            background: #667eea;
            transition: width 0.5s ease;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #94a3b8;
        }
        
        .spinner {
            border: 3px solid #e2e8f0;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 FinBERT Trading System</h1>
            <p style="color: #666; margin-bottom: 15px;">Advanced sentiment-aware stock prediction</p>
            <div id="status"></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Train Model</h2>
                <div class="form-group">
                    <label>Stock Symbol</label>
                    <select id="trainSymbol">
                        <option value="CBA.AX">CBA - Commonwealth Bank</option>
                        <option value="BHP.AX">BHP - BHP Group</option>
                        <option value="CSL.AX">CSL - CSL Limited</option>
                        <option value="NAB.AX">NAB - National Australia Bank</option>
                        <option value="WBC.AX">WBC - Westpac</option>
                        <option value="ANZ.AX">ANZ - ANZ Bank</option>
                        <option value="WES.AX">WES - Wesfarmers</option>
                        <option value="MQG.AX">MQG - Macquarie Group</option>
                        <option value="custom">Custom Symbol...</option>
                    </select>
                </div>
                <div class="form-group" id="customSymbolGroup" style="display: none;">
                    <label>Enter Symbol</label>
                    <input type="text" id="customTrainSymbol" placeholder="e.g., AAPL, MSFT">
                </div>
                <button class="btn" onclick="trainModel()">🚀 Train Model</button>
                <div id="trainResults" class="results"></div>
            </div>
            
            <div class="card">
                <h2>🔮 Make Prediction</h2>
                <div class="form-group">
                    <label>Stock Symbol</label>
                    <select id="predictSymbol">
                        <option value="CBA.AX">CBA - Commonwealth Bank</option>
                        <option value="BHP.AX">BHP - BHP Group</option>
                        <option value="CSL.AX">CSL - CSL Limited</option>
                        <option value="NAB.AX">NAB - National Australia Bank</option>
                        <option value="WBC.AX">WBC - Westpac</option>
                        <option value="custom">Custom Symbol...</option>
                    </select>
                </div>
                <div class="form-group" id="customPredictGroup" style="display: none;">
                    <label>Enter Symbol</label>
                    <input type="text" id="customPredictSymbol" placeholder="e.g., AAPL, MSFT">
                </div>
                <button class="btn" onclick="makePrediction()">📈 Predict</button>
                <div id="predictResults" class="results"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>💬 Sentiment Analysis Test</h2>
            <div class="form-group">
                <label>Enter Financial Text</label>
                <input type="text" id="sentimentText" placeholder="e.g., Company beats earnings expectations...">
            </div>
            <button class="btn" onclick="analyzeSentiment()">Analyze Sentiment</button>
            <div id="sentimentResults" class="results"></div>
        </div>
    </div>
    
    <script>
        // Check system status on load
        window.addEventListener('load', checkStatus);
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                if (data.finbert_enabled) {
                    statusDiv.innerHTML = '<span class="status-badge status-active">✓ FinBERT Active</span>';
                } else {
                    statusDiv.innerHTML = '<span class="status-badge status-fallback">⚠ Fallback Mode</span>';
                }
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }
        
        // Handle custom symbol selection
        document.getElementById('trainSymbol').addEventListener('change', function(e) {
            document.getElementById('customSymbolGroup').style.display = 
                e.target.value === 'custom' ? 'block' : 'none';
        });
        
        document.getElementById('predictSymbol').addEventListener('change', function(e) {
            document.getElementById('customPredictGroup').style.display = 
                e.target.value === 'custom' ? 'block' : 'none';
        });
        
        async function trainModel() {
            const select = document.getElementById('trainSymbol');
            let symbol = select.value;
            
            if (symbol === 'custom') {
                symbol = document.getElementById('customTrainSymbol').value;
                if (!symbol) {
                    alert('Please enter a symbol');
                    return;
                }
            }
            
            const resultsDiv = document.getElementById('trainResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Training model...</div>';
            
            try {
                const response = await fetch('/api/train', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="result-item" style="border-color: #ef4444;">
                        <div class="result-label">Error</div>
                        <div class="result-value">${data.error}</div>
                    </div>`;
                    return;
                }
                
                let html = `
                    <div class="result-item">
                        <div class="result-label">Symbol</div>
                        <div class="result-value">${data.symbol}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Training Accuracy</div>
                        <div class="result-value">${(data.train_accuracy * 100).toFixed(2)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Testing Accuracy</div>
                        <div class="result-value">${(data.test_accuracy * 100).toFixed(2)}%</div>
                    </div>
                `;
                
                // Add feature importance
                if (data.feature_importance) {
                    html += '<div class="feature-importance"><h3 style="margin-bottom: 15px;">Feature Importance</h3>';
                    const maxImportance = Math.max(...data.feature_importance.map(f => f.importance));
                    
                    data.feature_importance.slice(0, 5).forEach(feature => {
                        const width = (feature.importance / maxImportance) * 100;
                        html += `
                            <div class="feature-bar">
                                <div class="feature-name">${feature.feature}</div>
                                <div class="feature-bar-bg">
                                    <div class="feature-bar-fill" style="width: ${width}%"></div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item" style="border-color: #ef4444;">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
        
        async function makePrediction() {
            const select = document.getElementById('predictSymbol');
            let symbol = select.value;
            
            if (symbol === 'custom') {
                symbol = document.getElementById('customPredictSymbol').value;
                if (!symbol) {
                    alert('Please enter a symbol');
                    return;
                }
            }
            
            const resultsDiv = document.getElementById('predictResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Making prediction...</div>';
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="result-item" style="border-color: #ef4444;">
                        <div class="result-label">Error</div>
                        <div class="result-value">${data.error}</div>
                    </div>`;
                    return;
                }
                
                const predictionClass = data.prediction === 'BUY' ? 'prediction-buy' : 'prediction-sell';
                const upProb = data.probability.up * 100;
                
                resultsDiv.innerHTML = `
                    <div class="result-item">
                        <div class="result-label">Prediction</div>
                        <div class="result-value ${predictionClass}">${data.prediction}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Current Price</div>
                        <div class="result-value">$${data.current_price.toFixed(2)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Probability</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${upProb}%"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span style="color: #ef4444;">Down: ${(data.probability.down * 100).toFixed(1)}%</span>
                            <span style="color: #10b981;">Up: ${upProb.toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Sentiment Score</div>
                        <div class="result-value">${data.sentiment_score.toFixed(3)}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">RSI</div>
                        <div class="result-value">${data.rsi.toFixed(2)}</div>
                    </div>
                `;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item" style="border-color: #ef4444;">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
        
        async function analyzeSentiment() {
            const text = document.getElementById('sentimentText').value;
            if (!text) {
                alert('Please enter some text');
                return;
            }
            
            const resultsDiv = document.getElementById('sentimentResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Analyzing...</div>';
            
            try {
                const response = await fetch('/api/sentiment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                const data = await response.json();
                
                const maxScore = Math.max(data.positive, data.negative, data.neutral);
                let dominantSentiment = 'neutral';
                if (maxScore === data.positive) dominantSentiment = 'positive';
                else if (maxScore === data.negative) dominantSentiment = 'negative';
                
                resultsDiv.innerHTML = `
                    <div class="result-item">
                        <div class="result-label">Dominant Sentiment</div>
                        <div class="result-value" style="color: ${
                            dominantSentiment === 'positive' ? '#10b981' : 
                            dominantSentiment === 'negative' ? '#ef4444' : '#f59e0b'
                        };">${dominantSentiment.toUpperCase()}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Positive</div>
                        <div class="result-value" style="color: #10b981;">${(data.positive * 100).toFixed(1)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Negative</div>
                        <div class="result-value" style="color: #ef4444;">${(data.negative * 100).toFixed(1)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Neutral</div>
                        <div class="result-value" style="color: #f59e0b;">${(data.neutral * 100).toFixed(1)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Overall Score</div>
                        <div class="result-value">${data.score.toFixed(3)}</div>
                    </div>
                `;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item" style="border-color: #ef4444;">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
    </script>
</body>
</html>
'''

# Flask routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        "finbert_enabled": FINBERT_AVAILABLE,
        "pytorch_available": 'torch' in sys.modules,
        "device": str(sentiment_analyzer.device) if FINBERT_AVAILABLE else "cpu",
        "timestamp": dt.datetime.now().isoformat()
    })

@app.route('/api/train', methods=['POST'])
def train():
    """Train model endpoint"""
    data = request.json
    symbol = data.get('symbol', 'CBA.AX')
    
    result = trading_model.train_model(symbol)
    return jsonify(result)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    data = request.json
    symbol = data.get('symbol', 'CBA.AX')
    
    result = trading_model.predict(symbol)
    return jsonify(result)

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    """Sentiment analysis endpoint"""
    data = request.json
    text = data.get('text', '')
    
    result = sentiment_analyzer.analyze_sentiment(text)
    return jsonify(result)

@app.route('/api/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    """Analyze multiple stocks"""
    data = request.json
    symbols = data.get('symbols', DEFAULT_SYMBOLS[:5])
    
    results = []
    for symbol in symbols:
        pred = trading_model.predict(symbol)
        results.append(pred)
    
    return jsonify(results)

if __name__ == '__main__':
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("cache").mkdir(exist_ok=True)
    
    # Print startup info
    print("\n" + "="*60)
    print("FinBERT Trading System - Windows 11 Edition")
    print("="*60)
    print(f"FinBERT Status: {'✓ ENABLED' if FINBERT_AVAILABLE else '✗ FALLBACK MODE'}")
    print(f"PyTorch Device: {sentiment_analyzer.device if FINBERT_AVAILABLE else 'N/A'}")
    print("="*60)
    print("Server starting at http://localhost:5000")
    print("="*60 + "\n")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=False)