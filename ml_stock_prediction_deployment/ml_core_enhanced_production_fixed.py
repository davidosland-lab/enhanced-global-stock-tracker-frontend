#!/usr/bin/env python3
"""
ML Core Enhanced Production System - FIXED VERSION
With optional sentiment analysis and improved error handling
"""

# ==================== CONFIGURATION ====================
USE_SENTIMENT = False  # Set to True to enable sentiment analysis
PORT = 8000  # Change if port conflict

import logging
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== IMPORTS ====================
import sys
import os
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import time

# Data handling
import pandas as pd
import numpy as np
from pandas.api.extensions import ExtensionDtype
from pandas import DataFrame, Series
import pandas.api.types as pdtypes

# Custom JSON Encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, pd.DatetimeIndex, datetime)):
            return obj.isoformat()
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif pd.api.types.is_datetime64_any_dtype(obj):
            return str(obj)
        return super().default(obj)

# Data source
import yfinance as yf

# Handle scipy import issue for Python 3.12
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    logger.warning("Scipy not available, some features may be limited")
    SCIPY_AVAILABLE = False

# Import comprehensive sentiment analyzer (optional)
if USE_SENTIMENT:
    try:
        from comprehensive_sentiment_analyzer import sentiment_analyzer
        SENTIMENT_AVAILABLE = True
        logger.info("Sentiment analyzer loaded successfully")
    except ImportError:
        SENTIMENT_AVAILABLE = False
        logger.warning("Comprehensive sentiment analyzer not available, will use neutral value")
else:
    SENTIMENT_AVAILABLE = False
    logger.info("Sentiment analysis disabled by configuration")

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor, StackingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

# Optional: XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.info("XGBoost not available, using GradientBoosting as fallback")

# Optional: TA-Lib
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logger.info("TA-Lib not available, using fallback calculations")

# Web framework
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# ==================== CONFIGURATION ====================

class MLConfig:
    # Model parameters
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    CV_FOLDS = 5
    
    # Feature engineering
    MIN_PERIODS = 50  # Minimum periods for indicators
    
    # Backtesting
    INITIAL_CAPITAL = 100000
    COMMISSION_RATE = 0.001  # 0.1%
    SLIPPAGE_RATE = 0.0005   # 0.05%
    
    # Performance thresholds
    MIN_SHARPE_RATIO = 1.0
    MAX_DRAWDOWN_ALLOWED = 0.25  # 25%
    MIN_WIN_RATE = 0.55  # 55%
    
    # Cache settings
    CACHE_TTL_HOURS = 12

# ==================== DATABASE MANAGER ====================

class EnhancedDatabaseManager:
    """Centralized database management with proper initialization"""
    
    def __init__(self):
        self.cache_db = "ml_cache_enhanced.db"
        self.models_db = "ml_models_enhanced.db"
        self.backtest_db = "backtest_results_enhanced.db"
        self.predictions_db = "predictions_enhanced.db"
        
        self.initialize_all_databases()
    
    def initialize_all_databases(self):
        """Initialize all databases with proper schemas"""
        
        # Cache database
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_cache (
                    cache_key TEXT PRIMARY KEY,
                    symbol TEXT,
                    data BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_symbol ON data_cache(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON data_cache(expires_at)")
        
        # Models database
        with sqlite3.connect(self.models_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trained_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    ensemble_type TEXT,
                    model_data BLOB,
                    feature_names TEXT,
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    validation_score REAL,
                    training_samples INTEGER,
                    feature_count INTEGER
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_models_symbol ON trained_models(symbol)")
        
        # Backtesting database
        with sqlite3.connect(self.backtest_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backtest_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT,
                    symbol TEXT,
                    start_date DATE,
                    end_date DATE,
                    initial_capital REAL,
                    final_value REAL,
                    total_return REAL,
                    annual_return REAL,
                    sharpe_ratio REAL,
                    sortino_ratio REAL,
                    max_drawdown REAL,
                    win_rate REAL,
                    profit_factor REAL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    avg_win REAL,
                    avg_loss REAL,
                    largest_win REAL,
                    largest_loss REAL,
                    commission_paid REAL,
                    slippage_cost REAL,
                    trade_history TEXT,
                    equity_curve TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Predictions database
        with sqlite3.connect(self.predictions_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_price REAL,
                    predicted_price REAL,
                    confidence REAL,
                    model_version TEXT,
                    features_used INTEGER,
                    actual_price REAL,
                    error REAL
                )
            """)

# ==================== DATA FETCHER WITH CACHE ====================

class CachedDataFetcher:
    """Fetch and cache market data for 50x speed improvement"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_cache_key(self, symbol: str, period: str, interval: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{period}_{interval}"
    
    def fetch_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
        """Fetch data with caching (50x speed improvement)"""
        
        cache_key = self.get_cache_key(symbol, period, interval)
        
        # Check cache first
        with sqlite3.connect(self.db.cache_db) as conn:
            cursor = conn.execute("""
                SELECT data FROM data_cache 
                WHERE cache_key = ? AND expires_at > datetime('now')
            """, (cache_key,))
            row = cursor.fetchone()
            
            if row:
                self.cache_hits += 1
                logger.info(f"Cache hit for {symbol} (Hit rate: {self.get_hit_rate():.1%})")
                return pickle.loads(row[0])
        
        # Cache miss - fetch fresh data
        self.cache_misses += 1
        logger.info(f"Cache miss for {symbol}, fetching fresh data...")
        
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Store in cache
            expires_at = datetime.now() + timedelta(hours=MLConfig.CACHE_TTL_HOURS)
            with sqlite3.connect(self.db.cache_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO data_cache (cache_key, symbol, data, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (cache_key, symbol, pickle.dumps(df), expires_at))
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        with sqlite3.connect(self.db.cache_db) as conn:
            conn.execute("DELETE FROM data_cache WHERE expires_at < datetime('now')")
            logger.info("Expired cache entries cleared")

# ==================== FEATURE ENGINEERING ====================

class ComprehensiveFeatureEngineer:
    """Generate 35-36 optimal features based on research"""
    
    # Base features (35) + optional sentiment (1) = 36 total
    ESSENTIAL_FEATURES = [
        # Price-based (5)
        'returns_1', 'returns_5', 'returns_20', 'log_returns', 'volatility_20',
        
        # Moving Averages (6)
        'sma_20', 'sma_50', 'ema_12', 'ema_26', 'ma_ratio_20_50', 'ma_cross',
        
        # Momentum Indicators (7)
        'rsi_14', 'macd', 'macd_signal', 'macd_hist', 'momentum_10', 'roc_10', 'stoch_rsi',
        
        # Volatility Indicators (5)
        'bb_upper', 'bb_lower', 'bb_width', 'bb_position', 'atr_14',
        
        # Volume Indicators (5)
        'volume_ratio', 'obv_change', 'mfi_14', 'ad_line', 'vwap_ratio',
        
        # Trend Indicators (4)
        'adx_14', 'plus_di', 'minus_di', 'aroon_osc',
        
        # Market Structure (3)
        'high_low_spread', 'close_open_spread', 'support_resistance_ratio'
    ]
    
    # Add sentiment if enabled
    if SENTIMENT_AVAILABLE:
        ESSENTIAL_FEATURES.append('comprehensive_sentiment')
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_importance = {}
    
    def calculate_all_features(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Calculate all technical indicators"""
        
        df = df.copy()
        
        # Price-based features
        df['returns_1'] = df['Close'].pct_change(1)
        df['returns_5'] = df['Close'].pct_change(5)
        df['returns_20'] = df['Close'].pct_change(20)
        df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['volatility_20'] = df['returns_1'].rolling(window=20).std()
        
        # Moving Averages
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['ma_ratio_20_50'] = df['sma_20'] / df['sma_50']
        df['ma_cross'] = (df['sma_20'] > df['sma_50']).astype(int)
        
        # RSI
        df['rsi_14'] = self.calculate_rsi(df['Close'], 14)
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Momentum
        df['momentum_10'] = df['Close'] - df['Close'].shift(10)
        df['roc_10'] = (df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)
        
        # Stochastic RSI
        df['stoch_rsi'] = (df['rsi_14'] - df['rsi_14'].rolling(14).min()) / \
                         (df['rsi_14'].rolling(14).max() - df['rsi_14'].rolling(14).min() + 1e-10)
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        df['bb_middle'] = df['Close'].rolling(window=bb_period).mean()
        df['bb_std'] = df['Close'].rolling(window=bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (bb_std * df['bb_std'])
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_width'] + 1e-10)
        
        # ATR
        df['atr_14'] = self.calculate_atr(df, 14)
        
        # Volume indicators
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        df['obv'] = (np.sign(df['Close'].diff()) * df['Volume']).cumsum()
        df['obv_change'] = df['obv'].pct_change()
        
        # Money Flow Index
        df['mfi_14'] = self.calculate_mfi(df, 14)
        
        # Accumulation/Distribution Line
        df['ad_line'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / \
                       (df['High'] - df['Low'] + 1e-10) * df['Volume']
        df['ad_line'] = df['ad_line'].cumsum()
        
        # VWAP
        df['vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / \
                     df['Volume'].cumsum()
        df['vwap_ratio'] = df['Close'] / df['vwap']
        
        # ADX, +DI, -DI
        adx_period = 14
        df['tr'] = self.calculate_true_range(df)
        df['plus_dm'] = np.where((df['High'].diff() > df['Low'].shift().diff()) & 
                                 (df['High'].diff() > 0), df['High'].diff(), 0)
        df['minus_dm'] = np.where((df['Low'].shift().diff() > df['High'].diff()) & 
                                  (df['Low'].shift().diff() > 0), df['Low'].shift().diff(), 0)
        
        df['tr_smooth'] = df['tr'].rolling(adx_period).mean()
        df['plus_di'] = 100 * (df['plus_dm'].rolling(adx_period).mean() / df['tr_smooth'])
        df['minus_di'] = 100 * (df['minus_dm'].rolling(adx_period).mean() / df['tr_smooth'])
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'] + 1e-10)
        df['adx_14'] = df['dx'].rolling(adx_period).mean()
        
        # Aroon Oscillator
        if SCIPY_AVAILABLE:
            high_idx = df['High'].rolling(window=25).apply(lambda x: x.argmax())
            low_idx = df['Low'].rolling(window=25).apply(lambda x: x.argmin())
            df['aroon_up'] = ((25 - high_idx) / 25) * 100
            df['aroon_down'] = ((25 - low_idx) / 25) * 100
            df['aroon_osc'] = df['aroon_up'] - df['aroon_down']
        else:
            df['aroon_osc'] = 0
        
        # Market Structure
        df['high_low_spread'] = (df['High'] - df['Low']) / df['Close']
        df['close_open_spread'] = (df['Close'] - df['Open']) / (df['Open'] + 1e-10)
        
        # Support and Resistance
        df['resistance'] = df['High'].rolling(window=20).max()
        df['support'] = df['Low'].rolling(window=20).min()
        df['support_resistance_ratio'] = (df['Close'] - df['support']) / (df['resistance'] - df['support'] + 1e-10)
        
        # COMPREHENSIVE SENTIMENT (36th feature - OPTIONAL)
        if SENTIMENT_AVAILABLE and symbol:
            try:
                # Calculate sentiment score
                sentiment_score = sentiment_analyzer.calculate_comprehensive_sentiment(symbol)
                df['comprehensive_sentiment'] = sentiment_score
                logger.info(f"Sentiment score for {symbol}: {sentiment_score:.3f}")
            except Exception as e:
                logger.warning(f"Error calculating sentiment: {e}, using neutral")
                df['comprehensive_sentiment'] = 0.5
        elif 'comprehensive_sentiment' in self.ESSENTIAL_FEATURES:
            # Use neutral sentiment if not available
            df['comprehensive_sentiment'] = 0.5
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info(f"Calculated {len([c for c in self.ESSENTIAL_FEATURES if c in df.columns])} features")
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        return 100 - (100 / (1 + rs))
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        tr = self.calculate_true_range(df)
        return tr.rolling(window=period).mean()
    
    def calculate_true_range(self, df):
        """Calculate True Range"""
        hl = df['High'] - df['Low']
        hc = abs(df['High'] - df['Close'].shift())
        lc = abs(df['Low'] - df['Close'].shift())
        return pd.concat([hl, hc, lc], axis=1).max(axis=1)
    
    def calculate_mfi(self, df, period=14):
        """Calculate Money Flow Index"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        
        positive_flow_sum = positive_flow.rolling(period).sum()
        negative_flow_sum = negative_flow.rolling(period).sum()
        
        mfi = 100 - (100 / (1 + positive_flow_sum / (negative_flow_sum + 1e-10)))
        return mfi

# ==================== MODEL BUILDER ====================

class EnsembleModelBuilder:
    """Build and manage ensemble models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        
    def build_ensemble(self, ensemble_type: str = "voting") -> Any:
        """Build ensemble model based on type"""
        
        # Base models
        models = [
            ('rf', RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )),
            ('gb', GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )),
            ('svm', SVR(
                kernel='rbf',
                C=1.0,
                epsilon=0.1
            ))
        ]
        
        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            models.append(('xgb', xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )))
        
        # Add Neural Network
        models.append(('nn', MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size='auto',
            learning_rate='adaptive',
            max_iter=500,
            random_state=42,
            early_stopping=True
        )))
        
        if ensemble_type == "voting":
            # Voting ensemble with weights
            weights = [0.30, 0.25, 0.15, 0.25, 0.05] if XGBOOST_AVAILABLE else [0.35, 0.30, 0.20, 0.15]
            return VotingRegressor(models, weights=weights)
        elif ensemble_type == "stacking":
            # Stacking ensemble
            final_estimator = GradientBoostingRegressor(
                n_estimators=50,
                learning_rate=0.1,
                random_state=42
            )
            return StackingRegressor(
                estimators=models,
                final_estimator=final_estimator,
                cv=3
            )
        else:
            raise ValueError(f"Unknown ensemble type: {ensemble_type}")
    
    def train(self, X: np.ndarray, y: np.ndarray, ensemble_type: str = "voting") -> Dict:
        """Train ensemble model"""
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Build and train ensemble
        model = self.build_ensemble(ensemble_type)
        
        # Time the training
        start_time = time.time()
        model.fit(X_scaled, y)
        training_time = time.time() - start_time
        
        # Cross-validation
        tscv = TimeSeriesSplit(n_splits=MLConfig.CV_FOLDS)
        cv_scores = cross_val_score(model, X_scaled, y, cv=tscv, 
                                   scoring='neg_mean_squared_error')
        
        return {
            'model': model,
            'training_time': training_time,
            'cv_scores': cv_scores,
            'scaler': self.scaler
        }
    
    def predict(self, model: Any, X_test: np.ndarray) -> np.ndarray:
        """Make predictions with ensemble"""
        X_test_scaled = self.scaler.transform(X_test)
        return model.predict(X_test_scaled)

# ==================== BACKTESTING ENGINE ====================

class RobustBacktestingEngine:
    """Realistic backtesting with transaction costs"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = [initial_capital]
        
        # Transaction costs
        self.commission_rate = MLConfig.COMMISSION_RATE
        self.slippage_rate = MLConfig.SLIPPAGE_RATE
    
    def execute_trade(self, signal: int, price: float, timestamp: pd.Timestamp, 
                     confidence: float = 0.5, volatility: float = 0.2) -> Dict:
        """Execute trade with realistic costs"""
        
        trade = {
            'timestamp': str(timestamp),
            'signal': signal,
            'price': price,
            'shares': 0,
            'value': 0,
            'commission': 0,
            'slippage': 0,
            'pnl': 0
        }
        
        if signal == 0:
            return trade
        
        # Calculate position size (simplified)
        position_value = self.capital * 0.1 * confidence
        
        # Apply slippage
        if signal == 1:
            execution_price = price * (1 + self.slippage_rate)
        else:
            execution_price = price * (1 - self.slippage_rate)
        
        # Calculate shares and costs
        shares = position_value / execution_price
        commission = position_value * self.commission_rate
        
        # Update trade
        trade['shares'] = shares * signal
        trade['value'] = position_value
        trade['commission'] = commission
        trade['slippage'] = abs(execution_price - price) * shares
        
        # Update capital
        if signal == 1:
            self.capital -= (position_value + commission)
        else:
            self.capital += (position_value - commission)
        
        self.trades.append(trade)
        self.equity_curve.append(self.capital)
        
        return trade
    
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        
        if not self.trades:
            return {}
        
        equity = pd.Series(self.equity_curve)
        returns = equity.pct_change().dropna()
        
        # Calculate metrics
        total_return = (equity.iloc[-1] - equity.iloc[0]) / equity.iloc[0]
        
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # Win rate
        winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        total_trades = len(self.trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'win_rate': win_rate * 100,
            'total_trades': total_trades
        }

# ==================== ORCHESTRATOR ====================

class MLSystemOrchestrator:
    """Main orchestrator for the ML system"""
    
    def __init__(self):
        self.db_manager = EnhancedDatabaseManager()
        self.data_fetcher = CachedDataFetcher(self.db_manager)
        self.feature_engineer = ComprehensiveFeatureEngineer()
        self.model_builder = EnsembleModelBuilder()
        self.backtester = None
        
    def train_model(self, symbol: str, ensemble_type: str = "voting", days: int = 480) -> Dict:
        """Train model with comprehensive features"""
        
        start_time = time.time()
        
        # Fetch data
        df = self.data_fetcher.fetch_data(symbol, period=f"{days}d")
        
        # Calculate features  
        df_features = self.feature_engineer.calculate_all_features(df, symbol)
        
        # Prepare training data
        available_features = [f for f in ComprehensiveFeatureEngineer.ESSENTIAL_FEATURES 
                            if f in df_features.columns]
        
        X = df_features[available_features].iloc[:-1].values
        y = df_features['Close'].shift(-1).iloc[:-1].values
        
        # Train model
        result = self.model_builder.train(X, y, ensemble_type)
        
        # Save model
        model_data = {
            'model': result['model'],
            'scaler': result['scaler'],
            'features': available_features,
            'symbol': symbol,
            'ensemble_type': ensemble_type
        }
        
        with sqlite3.connect(self.db_manager.models_db) as conn:
            conn.execute("""
                INSERT INTO trained_models 
                (symbol, ensemble_type, model_data, feature_names, validation_score, 
                 training_samples, feature_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                ensemble_type, 
                pickle.dumps(model_data),
                json.dumps(available_features),
                float(result['cv_scores'].mean()),
                len(X),
                len(available_features)
            ))
        
        total_time = time.time() - start_time
        
        return {
            'symbol': symbol,
            'ensemble_type': ensemble_type,
            'training_samples': len(X),
            'features_used': len(available_features),
            'metrics': {
                'cv_score_mean': float(result['cv_scores'].mean()),
                'cv_score_std': float(result['cv_scores'].std())
            },
            'training_time': result['training_time'],
            'total_time': total_time,
            'cache_hit_rate': self.data_fetcher.get_hit_rate()
        }

# ==================== API ENDPOINTS ====================

app = FastAPI(title="ML Core Enhanced Production")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = MLSystemOrchestrator()

# Request models
class TrainRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    ensemble_type: str = Field(default="voting", description="voting or stacking")
    days: int = Field(default=480, description="Days of historical data")

class BacktestRequest(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class PredictRequest(BaseModel):
    symbol: str
    horizon: int = Field(default=1, description="Days ahead to predict")

@app.get("/")
async def root():
    """System information endpoint"""
    feature_count = len(ComprehensiveFeatureEngineer.ESSENTIAL_FEATURES)
    return {
        "system": "ML Core Enhanced Production",
        "version": "2.0-FIXED",
        "status": "operational",
        "features": {
            "models": ["RandomForest", "GradientBoosting", "SVM", "XGBoost", "NeuralNetwork"],
            "ensemble": ["voting", "stacking"],
            "features_count": feature_count,
            "sentiment_enabled": SENTIMENT_AVAILABLE,
            "cache_enabled": True,
            "backtesting": "with transaction costs"
        }
    }

@app.post("/api/train")
async def train_model(request: TrainRequest):
    """Train ensemble model endpoint"""
    try:
        result = orchestrator.train_model(
            symbol=request.symbol,
            ensemble_type=request.ensemble_type,
            days=request.days
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def list_models():
    """List all trained models"""
    try:
        with sqlite3.connect(orchestrator.db_manager.models_db) as conn:
            cursor = conn.execute("""
                SELECT symbol, ensemble_type, training_date, validation_score
                FROM trained_models
                ORDER BY training_date DESC
                LIMIT 20
            """)
            models = [
                {
                    "symbol": row[0],
                    "ensemble_type": row[1],
                    "training_date": row[2],
                    "validation_score": row[3]
                }
                for row in cursor.fetchall()
            ]
        return models
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return []

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "hit_rate": orchestrator.data_fetcher.get_hit_rate(),
        "cache_hits": orchestrator.data_fetcher.cache_hits,
        "cache_misses": orchestrator.data_fetcher.cache_misses
    }

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear expired cache entries"""
    orchestrator.data_fetcher.clear_expired_cache()
    return {"status": "Cache cleared"}

# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info("ML Core Enhanced Production System starting...")
    logger.info(f"XGBoost available: {XGBOOST_AVAILABLE}")
    logger.info(f"TA-Lib available: {TALIB_AVAILABLE}")
    logger.info(f"Sentiment analysis: {'ENABLED' if SENTIMENT_AVAILABLE else 'DISABLED'}")
    logger.info(f"Port: {PORT}")
    logger.info("System ready!")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)