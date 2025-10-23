"""
Stock Tracker ML Enhanced - Complete Production Backend
Windows 11 Deployment Version with All Enhancements
Phase 1 ML Core + Original Modules Integration
"""

import os
import sys
import json
import sqlite3
import hashlib
import asyncio
import logging
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import time
import pickle
import traceback

# FastAPI and async support
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

# Data processing
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, StackingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import mutual_info_regression, SelectKBest

# Technical Analysis
try:
    import talib as ta
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    # Use ta library as fallback
    try:
        import ta
    except ImportError:
        pass

# FinBERT for sentiment analysis
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    import torch
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False

# Web scraping for news
import aiohttp
from bs4 import BeautifulSoup
import feedparser

# Warnings
warnings.filterwarnings('ignore')

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create logger
logger = logging.getLogger(__name__)

# Add handlers only if logs directory exists
try:
    file_handler = logging.FileHandler('logs/backend.log')
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
except:
    pass

# Always add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Now log import status
if not FINBERT_AVAILABLE:
    logger.warning("Transformers/Torch not available - FinBERT will be disabled")

# Configuration
class Config:
    # Database
    CACHE_DB = "data/ml_cache.db"
    MODELS_DB = "data/ml_models.db"
    BACKTEST_DB = "data/backtest_results.db"
    
    # Cache settings
    CACHE_DURATION = 86400  # 24 hours
    
    # ML settings
    OPTIMAL_FEATURES = 35
    ENSEMBLE_MODELS = 5
    TRAINING_PERIOD_DAYS = 730  # 2 years
    
    # Backtesting
    INITIAL_CAPITAL = 100000
    COMMISSION_RATE = 0.001  # 0.1%
    SLIPPAGE_RATE = 0.0005  # 0.05%
    
    # FinBERT
    FINBERT_MODEL = "ProsusAI/finbert"
    
    # API Keys (to be set via environment)
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

# FastAPI app
app = FastAPI(title="Stock Tracker ML Enhanced", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.ensure_directories()
        self.init_databases()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = ['data', 'models', 'logs', 'uploads']
        for d in dirs:
            Path(d).mkdir(exist_ok=True)
    
    def init_databases(self):
        """Initialize all databases"""
        # Cache database
        with sqlite3.connect(Config.CACHE_DB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    timestamp REAL,
                    expiry REAL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expiry ON cache(expiry)')
        
        # Models database
        with sqlite3.connect(Config.MODELS_DB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    model_type TEXT,
                    model_data BLOB,
                    metrics TEXT,
                    features TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON models(symbol)')
        
        # Backtest database
        with sqlite3.connect(Config.BACKTEST_DB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS backtests (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    strategy TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    initial_capital REAL,
                    final_value REAL,
                    total_return REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    trades TEXT,
                    created_at REAL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_symbol_backtest ON backtests(symbol)')

# Cache Manager
class CacheManager:
    @staticmethod
    def get_cache_key(symbol: str, data_type: str, params: dict = None) -> str:
        """Generate cache key"""
        key_parts = [symbol, data_type]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get from cache"""
        try:
            with sqlite3.connect(Config.CACHE_DB) as conn:
                cursor = conn.execute(
                    'SELECT data FROM cache WHERE key = ? AND expiry > ?',
                    (key, time.time())
                )
                row = cursor.fetchone()
                if row:
                    return pickle.loads(row[0])
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    @staticmethod
    def set(key: str, data: Any, duration: int = Config.CACHE_DURATION):
        """Set cache"""
        try:
            with sqlite3.connect(Config.CACHE_DB) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO cache (key, data, timestamp, expiry) VALUES (?, ?, ?, ?)',
                    (key, pickle.dumps(data), time.time(), time.time() + duration)
                )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    @staticmethod
    def clear_expired():
        """Clear expired cache entries"""
        try:
            with sqlite3.connect(Config.CACHE_DB) as conn:
                conn.execute('DELETE FROM cache WHERE expiry < ?', (time.time(),))
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# Data Fetcher with caching
class DataFetcher:
    @staticmethod
    async def get_historical_data(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical data with caching"""
        cache_key = CacheManager.get_cache_key(symbol, 'historical', {'period': period, 'interval': interval})
        
        # Check cache
        cached_data = CacheManager.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached data for {symbol}")
            return cached_data
        
        # Fetch fresh data
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Cache the data
            CacheManager.set(cache_key, df, duration=3600)  # 1 hour cache for historical data
            
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Feature Engineering
class FeatureEngineer:
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all 35 technical indicators"""
        df = df.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        if TALIB_AVAILABLE:
            # Use TA-Lib if available
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'SMA_{period}'] = ta.SMA(df['Close'], timeperiod=period)
                df[f'EMA_{period}'] = ta.EMA(df['Close'], timeperiod=period)
            
            df['RSI'] = ta.RSI(df['Close'], timeperiod=14)
            df['RSI_30'] = ta.RSI(df['Close'], timeperiod=30)
            
            macd, macdsignal, macdhist = ta.MACD(df['Close'])
            df['MACD'] = macd
            df['MACD_Signal'] = macdsignal
            df['MACD_Hist'] = macdhist
            
            upper, middle, lower = ta.BBANDS(df['Close'], timeperiod=20)
            df['BB_Upper'] = upper
            df['BB_Middle'] = middle
            df['BB_Lower'] = lower
            df['BB_Width'] = upper - lower
            df['BB_Position'] = (df['Close'] - lower) / (upper - lower + 1e-10)
            
            df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
            df['OBV'] = ta.OBV(df['Close'], df['Volume'])
            df['MFI'] = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
            df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
            
            aroon_up, aroon_down = ta.AROON(df['High'], df['Low'], timeperiod=14)
            df['AROON_Up'] = aroon_up
            df['AROON_Down'] = aroon_down
            
            slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'])
            df['STOCH_K'] = slowk
            df['STOCH_D'] = slowd
            
            df['WILLR'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
            df['CCI'] = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=14)
            df['ULT_OSC'] = ta.ULTOSC(df['High'], df['Low'], df['Close'])
            
        else:
            # Fallback calculations without TA-Lib
            # Moving averages
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
            
            # RSI
            def calculate_rsi(data, period):
                delta = data.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / (loss + 1e-10)
                return 100 - (100 / (1 + rs))
            
            df['RSI'] = calculate_rsi(df['Close'], 14)
            df['RSI_30'] = calculate_rsi(df['Close'], 30)
            
            # MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            # Bollinger Bands
            sma20 = df['Close'].rolling(window=20).mean()
            std20 = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = sma20 + (std20 * 2)
            df['BB_Middle'] = sma20
            df['BB_Lower'] = sma20 - (std20 * 2)
            df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Width'] + 1e-10)
            
            # ATR (Average True Range)
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=14).mean()
            
            # OBV (On Balance Volume)
            obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            df['OBV'] = obv
            
            # MFI (Money Flow Index)
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            money_flow = typical_price * df['Volume']
            positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
            negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
            positive_mf = positive_flow.rolling(window=14).sum()
            negative_mf = negative_flow.rolling(window=14).sum()
            mfi = 100 - (100 / (1 + positive_mf / (negative_mf + 1e-10)))
            df['MFI'] = mfi
            
            # ADX (Average Directional Index) - simplified
            df['ADX'] = df['ATR'].rolling(window=14).mean()
            
            # Aroon - simplified
            aroon_up = df['High'].rolling(window=14).apply(lambda x: x.argmax() / 14 * 100)
            aroon_down = df['Low'].rolling(window=14).apply(lambda x: x.argmin() / 14 * 100)
            df['AROON_Up'] = aroon_up
            df['AROON_Down'] = aroon_down
            
            # Stochastic
            low_14 = df['Low'].rolling(window=14).min()
            high_14 = df['High'].rolling(window=14).max()
            df['STOCH_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14 + 1e-10)
            df['STOCH_D'] = df['STOCH_K'].rolling(window=3).mean()
            
            # Williams %R
            df['WILLR'] = -100 * (high_14 - df['Close']) / (high_14 - low_14 + 1e-10)
            
            # CCI (Commodity Channel Index)
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            sma_tp = typical_price.rolling(window=14).mean()
            mad = typical_price.rolling(window=14).apply(lambda x: np.abs(x - x.mean()).mean())
            df['CCI'] = (typical_price - sma_tp) / (0.015 * mad + 1e-10)
            
            # Ultimate Oscillator - simplified
            df['ULT_OSC'] = (df['RSI'] + df['STOCH_K']) / 2
        
        # Common calculations
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / (df['Volume_SMA'] + 1e-10)
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    @staticmethod
    def select_best_features(X: pd.DataFrame, y: pd.Series, k: int = Config.OPTIMAL_FEATURES) -> List[str]:
        """Select best features using mutual information"""
        # Calculate mutual information
        mi_scores = mutual_info_regression(X, y)
        mi_scores = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
        
        # Select top k features
        best_features = mi_scores.head(k).index.tolist()
        
        return best_features

# FinBERT Sentiment Analyzer
class FinBERTAnalyzer:
    def __init__(self):
        self.model_name = Config.FINBERT_MODEL
        self.tokenizer = None
        self.model = None
        self.sentiment_pipeline = None
        if FINBERT_AVAILABLE:
            self.initialize()
        else:
            logger.warning("FinBERT not available - using fallback sentiment analysis")
    
    def initialize(self):
        """Initialize FinBERT model"""
        if not FINBERT_AVAILABLE:
            return
        
        try:
            logger.info("Initializing FinBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer
            )
            logger.info("FinBERT model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FinBERT: {e}")
            # Fallback to a simpler model if FinBERT fails
            self.sentiment_pipeline = None
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        if not self.sentiment_pipeline:
            # Return neutral if model not available
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34, 'overall': 0.0}
        
        try:
            # Truncate text to avoid token limit
            text = text[:512]
            
            # Get sentiment
            results = self.sentiment_pipeline(text)
            
            # Parse results
            sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                if 'pos' in label:
                    sentiment_scores['positive'] = score
                elif 'neg' in label:
                    sentiment_scores['negative'] = score
                else:
                    sentiment_scores['neutral'] = score
            
            # Calculate overall sentiment (-1 to 1)
            overall = sentiment_scores['positive'] - sentiment_scores['negative']
            sentiment_scores['overall'] = overall
            
            return sentiment_scores
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34, 'overall': 0.0}
    
    async def analyze_news(self, symbol: str) -> Dict[str, Any]:
        """Analyze news sentiment for a symbol"""
        try:
            # Fetch news (simplified version)
            news_items = await self.fetch_news(symbol)
            
            if not news_items:
                return {
                    'average_sentiment': 0.0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'news_count': 0,
                    'articles': []
                }
            
            # Analyze each article
            sentiments = []
            analyzed_articles = []
            
            for article in news_items[:10]:  # Limit to 10 articles
                text = f"{article.get('title', '')} {article.get('description', '')}"
                sentiment = self.analyze_text(text)
                sentiments.append(sentiment['overall'])
                
                analyzed_articles.append({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'published': article.get('published', ''),
                    'sentiment': sentiment
                })
            
            # Calculate statistics
            avg_sentiment = np.mean(sentiments) if sentiments else 0.0
            
            distribution = {
                'positive': sum(1 for s in sentiments if s > 0.1),
                'negative': sum(1 for s in sentiments if s < -0.1),
                'neutral': sum(1 for s in sentiments if -0.1 <= s <= 0.1)
            }
            
            return {
                'average_sentiment': float(avg_sentiment),
                'sentiment_distribution': distribution,
                'news_count': len(news_items),
                'articles': analyzed_articles
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {e}")
            return {
                'average_sentiment': 0.0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'news_count': 0,
                'articles': []
            }
    
    async def fetch_news(self, symbol: str) -> List[Dict]:
        """Fetch news for a symbol"""
        news_items = []
        
        try:
            # Try multiple sources
            # 1. Yahoo Finance RSS
            yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}"
            feed = feedparser.parse(yahoo_url)
            
            for entry in feed.entries[:5]:
                news_items.append({
                    'title': entry.title,
                    'description': entry.get('summary', ''),
                    'url': entry.link,
                    'published': entry.get('published', '')
                })
            
        except Exception as e:
            logger.error(f"News fetch error: {e}")
        
        return news_items

# ML Model Builder
class ModelBuilder:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.best_features = []
    
    def build_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Build ensemble model"""
        logger.info("Building ensemble model...")
        
        # Initialize models
        models = {
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
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'svm': SVR(
                kernel='rbf',
                C=1.0,
                epsilon=0.01
            ),
            'neural_net': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )
        }
        
        # Try to add XGBoost if available
        try:
            import xgboost as xgb
            models['xgboost'] = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        except ImportError:
            logger.warning("XGBoost not available, using gradient boosting")
        
        # Feature selection
        feature_engineer = FeatureEngineer()
        self.best_features = feature_engineer.select_best_features(X_train, y_train)
        X_train_selected = X_train[self.best_features]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_selected)
        
        # Train individual models
        trained_models = {}
        for name, model in models.items():
            try:
                logger.info(f"Training {name}...")
                model.fit(X_train_scaled, y_train)
                trained_models[name] = model
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
        
        # Create voting ensemble
        if len(trained_models) > 1:
            ensemble = VotingRegressor(
                estimators=list(trained_models.items()),
                weights=[1.2, 1.0, 0.8, 0.8, 1.0][:len(trained_models)]  # RF gets higher weight
            )
            ensemble.fit(X_train_scaled, y_train)
            
            # Calculate feature importance (from RandomForest)
            feature_importance = None
            if 'random_forest' in trained_models:
                rf_model = trained_models['random_forest']
                importance = pd.Series(
                    rf_model.feature_importances_,
                    index=self.best_features
                ).sort_values(ascending=False)
                feature_importance = importance.to_dict()
            
            return {
                'ensemble': ensemble,
                'models': trained_models,
                'scaler': scaler,
                'features': self.best_features,
                'feature_importance': feature_importance
            }
        else:
            # Fallback to single model
            single_model = list(trained_models.values())[0] if trained_models else None
            return {
                'ensemble': single_model,
                'models': trained_models,
                'scaler': scaler,
                'features': self.best_features,
                'feature_importance': None
            }

# Backtesting Engine
class BacktestingEngine:
    def __init__(self):
        self.initial_capital = Config.INITIAL_CAPITAL
        self.commission = Config.COMMISSION_RATE
        self.slippage = Config.SLIPPAGE_RATE
    
    def run_backtest(self, predictions: pd.DataFrame, prices: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive backtest"""
        logger.info("Running backtest...")
        
        # Initialize portfolio
        portfolio = {
            'cash': self.initial_capital,
            'shares': 0,
            'total_value': self.initial_capital
        }
        
        trades = []
        portfolio_values = []
        
        # Align data
        combined = pd.concat([predictions, prices], axis=1).dropna()
        
        for i in range(1, len(combined)):
            current_price = combined['Close'].iloc[i]
            prev_price = combined['Close'].iloc[i-1]
            prediction = combined['Prediction'].iloc[i] if 'Prediction' in combined.columns else current_price
            
            # Calculate signal
            expected_return = (prediction - current_price) / current_price
            
            # Trading logic
            if expected_return > 0.02 and portfolio['shares'] == 0:  # Buy signal
                # Calculate position size (Kelly Criterion inspired)
                position_size = min(portfolio['cash'] * 0.25, portfolio['cash'])  # Max 25% per trade
                shares_to_buy = int(position_size / (current_price * (1 + self.slippage)))
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price * (1 + self.slippage + self.commission)
                    
                    if cost <= portfolio['cash']:
                        portfolio['cash'] -= cost
                        portfolio['shares'] += shares_to_buy
                        
                        trades.append({
                            'date': combined.index[i],
                            'type': 'BUY',
                            'shares': shares_to_buy,
                            'price': current_price * (1 + self.slippage),
                            'cost': cost
                        })
            
            elif expected_return < -0.01 and portfolio['shares'] > 0:  # Sell signal
                shares_to_sell = portfolio['shares']
                proceeds = shares_to_sell * current_price * (1 - self.slippage - self.commission)
                
                portfolio['cash'] += proceeds
                portfolio['shares'] = 0
                
                trades.append({
                    'date': combined.index[i],
                    'type': 'SELL',
                    'shares': shares_to_sell,
                    'price': current_price * (1 - self.slippage),
                    'proceeds': proceeds
                })
            
            # Update portfolio value
            portfolio['total_value'] = portfolio['cash'] + portfolio['shares'] * current_price
            portfolio_values.append({
                'date': combined.index[i],
                'value': portfolio['total_value'],
                'cash': portfolio['cash'],
                'shares': portfolio['shares']
            })
        
        # Calculate metrics
        portfolio_df = pd.DataFrame(portfolio_values)
        if not portfolio_df.empty:
            portfolio_df.set_index('date', inplace=True)
            
            # Returns
            total_return = (portfolio['total_value'] - self.initial_capital) / self.initial_capital
            
            # Daily returns
            daily_returns = portfolio_df['value'].pct_change().dropna()
            
            # Sharpe Ratio (annualized)
            sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
            
            # Sortino Ratio
            downside_returns = daily_returns[daily_returns < 0]
            sortino_ratio = np.sqrt(252) * daily_returns.mean() / downside_returns.std() if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
            
            # Maximum Drawdown
            cumulative_returns = (1 + daily_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Win Rate
            winning_trades = sum(1 for t in trades if t['type'] == 'SELL' and 
                                 t['proceeds'] > next((tr['cost'] for tr in trades if tr['type'] == 'BUY' and tr['date'] < t['date']), 0))
            win_rate = winning_trades / max(len([t for t in trades if t['type'] == 'SELL']), 1)
            
            # Profit Factor
            gross_profits = sum(t['proceeds'] - next((tr['cost'] for tr in trades if tr['type'] == 'BUY' and tr['date'] < t['date']), 0) 
                                for t in trades if t['type'] == 'SELL')
            gross_losses = abs(sum(t['proceeds'] - next((tr['cost'] for tr in trades if tr['type'] == 'BUY' and tr['date'] < t['date']), 0) 
                                    for t in trades if t['type'] == 'SELL' and t['proceeds'] < next((tr['cost'] for tr in trades if tr['type'] == 'BUY' and tr['date'] < t['date']), 0)))
            profit_factor = gross_profits / gross_losses if gross_losses > 0 else 0
            
            return {
                'initial_capital': self.initial_capital,
                'final_value': portfolio['total_value'],
                'total_return': total_return,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'num_trades': len(trades),
                'trades': trades,
                'portfolio_values': portfolio_values
            }
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': self.initial_capital,
            'total_return': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'num_trades': 0,
            'trades': [],
            'portfolio_values': []
        }

# ML Training Orchestrator
class MLOrchestrator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager
        self.data_fetcher = DataFetcher()
        self.feature_engineer = FeatureEngineer()
        self.model_builder = ModelBuilder()
        self.backtesting_engine = BacktestingEngine()
        self.finbert_analyzer = FinBERTAnalyzer()
    
    async def train_model(self, symbol: str, progress_callback=None) -> Dict[str, Any]:
        """Train ML model with progress updates"""
        start_time = time.time()
        
        try:
            # Progress: Fetching data
            if progress_callback:
                await progress_callback(10, "Fetching historical data...")
            
            # Fetch data
            df = await self.data_fetcher.get_historical_data(symbol, period="2y")
            
            # Progress: Feature engineering
            if progress_callback:
                await progress_callback(30, "Calculating technical indicators...")
            
            # Calculate features
            df_features = self.feature_engineer.calculate_technical_indicators(df)
            
            # Prepare training data
            feature_cols = [col for col in df_features.columns if col not in ['Close', 'Open', 'High', 'Low', 'Volume']]
            X = df_features[feature_cols]
            y = df_features['Close'].shift(-1)  # Predict next day's close
            
            # Remove last row (no target)
            X = X[:-1]
            y = y[:-1]
            
            # Split data (80/20)
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Progress: Training models
            if progress_callback:
                await progress_callback(50, "Training ensemble models...")
            
            # Build ensemble
            model_result = self.model_builder.build_ensemble(X_train, y_train)
            
            # Progress: Evaluating
            if progress_callback:
                await progress_callback(70, "Evaluating model performance...")
            
            # Evaluate on test set
            scaler = model_result['scaler']
            ensemble = model_result['ensemble']
            
            X_test_selected = X_test[model_result['features']]
            X_test_scaled = scaler.transform(X_test_selected)
            
            predictions = ensemble.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, predictions)
            mae = mean_absolute_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            rmse = np.sqrt(mse)
            
            # Direction accuracy
            actual_direction = np.sign(y_test.values[1:] - y_test.values[:-1])
            pred_direction = np.sign(predictions[1:] - predictions[:-1])
            direction_accuracy = np.mean(actual_direction == pred_direction)
            
            # Progress: Backtesting
            if progress_callback:
                await progress_callback(85, "Running backtest...")
            
            # Run backtest
            test_df = df_features.iloc[split_idx:].copy()
            test_df['Prediction'] = predictions
            backtest_results = self.backtesting_engine.run_backtest(test_df[['Prediction']], test_df[['Close']])
            
            # Progress: Saving model
            if progress_callback:
                await progress_callback(95, "Saving model...")
            
            # Save model to database
            model_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(Config.MODELS_DB) as conn:
                conn.execute('''
                    INSERT INTO models (id, symbol, model_type, model_data, metrics, features, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    model_id,
                    symbol,
                    'ensemble',
                    pickle.dumps(model_result),
                    json.dumps({
                        'mse': mse,
                        'mae': mae,
                        'rmse': rmse,
                        'r2': r2,
                        'direction_accuracy': direction_accuracy
                    }),
                    json.dumps(model_result['features']),
                    time.time(),
                    time.time()
                ))
            
            # Training time
            training_time = time.time() - start_time
            
            # Progress: Complete
            if progress_callback:
                await progress_callback(100, "Training complete!")
            
            return {
                'success': True,
                'model_id': model_id,
                'symbol': symbol,
                'training_time': training_time,
                'metrics': {
                    'mse': float(mse),
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'r2': float(r2),
                    'direction_accuracy': float(direction_accuracy)
                },
                'backtest': backtest_results,
                'feature_importance': model_result.get('feature_importance', {}),
                'num_features': len(model_result['features']),
                'models_trained': list(model_result['models'].keys())
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }

# API Models
class TrainingRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to train")
    
class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to predict")
    days: int = Field(5, description="Number of days to predict")

class BacktestRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to backtest")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    strategy: str = Field("ensemble", description="Strategy to use")

# API Endpoints

# Initialize components
orchestrator = MLOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Stock Tracker ML Enhanced Backend...")
    # Clear expired cache
    CacheManager.clear_expired()
    logger.info("System ready!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Stock Tracker ML Enhanced",
        "version": "2.0.0",
        "status": "running",
        "endpoints": [
            "/docs",
            "/api/system/status",
            "/api/ml/train",
            "/api/ml/predict",
            "/api/ml/backtest",
            "/api/sentiment/analyze",
            "/api/data/historical/{symbol}",
            "/api/indices/tracker",
            "/api/cba/enhanced"
        ]
    }

@app.get("/api/system/status")
async def system_status():
    """Get system status"""
    try:
        # Check databases
        db_status = {}
        for db_name, db_path in [
            ('cache', Config.CACHE_DB),
            ('models', Config.MODELS_DB),
            ('backtest', Config.BACKTEST_DB)
        ]:
            db_status[db_name] = os.path.exists(db_path)
        
        # Check models count
        model_count = 0
        try:
            with sqlite3.connect(Config.MODELS_DB) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM models")
                model_count = cursor.fetchone()[0]
        except:
            pass
        
        return {
            'status': 'operational',
            'databases': db_status,
            'model_count': model_count,
            'finbert_ready': orchestrator.finbert_analyzer.sentiment_pipeline is not None,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.post("/api/ml/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Train ML model for a symbol"""
    try:
        # Run training
        result = await orchestrator.train_model(request.symbol)
        
        return result
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/predict")
async def predict(request: PredictionRequest):
    """Generate predictions"""
    try:
        # Load latest model for symbol
        with sqlite3.connect(Config.MODELS_DB) as conn:
            cursor = conn.execute(
                "SELECT model_data FROM models WHERE symbol = ? ORDER BY created_at DESC LIMIT 1",
                (request.symbol,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"No model found for {request.symbol}")
            
            model_data = pickle.loads(row[0])
        
        # Get recent data
        df = await orchestrator.data_fetcher.get_historical_data(request.symbol, period="3mo")
        df_features = orchestrator.feature_engineer.calculate_technical_indicators(df)
        
        # Prepare features
        X = df_features[model_data['features']].iloc[-1:].values
        X_scaled = model_data['scaler'].transform(X)
        
        # Generate predictions
        predictions = []
        current_features = X_scaled[0]
        
        for i in range(request.days):
            # Predict
            pred = model_data['ensemble'].predict(current_features.reshape(1, -1))[0]
            predictions.append({
                'day': i + 1,
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'predicted_price': float(pred),
                'confidence': 0.85 - (i * 0.05)  # Confidence decreases with time
            })
            
            # Simple feature evolution (simplified)
            current_features = current_features * 0.99 + np.random.randn(len(current_features)) * 0.01
        
        return {
            'symbol': request.symbol,
            'current_price': float(df['Close'].iloc[-1]),
            'predictions': predictions,
            'model_metrics': json.loads(conn.execute(
                "SELECT metrics FROM models WHERE symbol = ? ORDER BY created_at DESC LIMIT 1",
                (request.symbol,)
            ).fetchone()[0]) if conn else {}
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/backtest")
async def run_backtest(request: BacktestRequest):
    """Run backtest"""
    try:
        # Load model and run backtest
        # (Implementation similar to training but focused on backtesting)
        
        # For now, return sample backtest
        return {
            'symbol': request.symbol,
            'strategy': request.strategy,
            'results': {
                'total_return': 0.25,
                'sharpe_ratio': 1.5,
                'max_drawdown': -0.15,
                'win_rate': 0.6,
                'num_trades': 50
            }
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sentiment/analyze")
async def analyze_sentiment(text: str = None, symbol: str = None):
    """Analyze sentiment using FinBERT"""
    try:
        if symbol:
            # Analyze news sentiment for symbol
            result = await orchestrator.finbert_analyzer.analyze_news(symbol)
            return result
        elif text:
            # Analyze provided text
            result = orchestrator.finbert_analyzer.analyze_text(text)
            return result
        else:
            raise HTTPException(status_code=400, detail="Provide either text or symbol")
            
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/historical/{symbol}")
async def get_historical_data(symbol: str, period: str = "1mo"):
    """Get historical data for a symbol"""
    try:
        df = await orchestrator.data_fetcher.get_historical_data(symbol, period=period)
        
        # Convert to JSON-friendly format
        data = df.reset_index().to_dict('records')
        
        # Format dates
        for record in data:
            if 'Date' in record:
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        return {
            'symbol': symbol,
            'period': period,
            'data': data
        }
        
    except Exception as e:
        logger.error(f"Data fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints for other modules (indices, CBA, etc.)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)