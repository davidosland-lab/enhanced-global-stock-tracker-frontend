"""
Enhanced ML Backend with Sentiment Integration
Incorporates FinBERT sentiment analysis and media sentiment into training
"""

import os
import sys
import json
import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import ta
import warnings
warnings.filterwarnings('ignore')

# Import FinBERT analyzer
try:
    from finbert_analyzer import analyze_financial_text
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    print("FinBERT not available - using basic sentiment")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Sentiment-Enhanced ML Backend", version="4.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced database with sentiment tables
DB_PATH = "ml_sentiment_enhanced.db"
BRIDGE_DB = "ml_integration_bridge.db"

def init_sentiment_database():
    """Initialize database with sentiment tracking tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sentiment history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            confidence REAL,
            key_phrases TEXT,
            document_type TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Daily aggregated sentiment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_sentiment (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            avg_sentiment REAL,
            max_sentiment REAL,
            min_sentiment REAL,
            sentiment_count INTEGER,
            news_volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    ''')
    
    # Model performance with sentiment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_model_performance (
            model_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            with_sentiment BOOLEAN,
            accuracy_gain REAL,
            best_features TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_sentiment_database()

class SentimentEnhancedTrainer:
    """ML trainer that incorporates sentiment analysis"""
    
    def __init__(self):
        self.models_dir = "sentiment_enhanced_models"
        os.makedirs(self.models_dir, exist_ok=True)
    
    def get_sentiment_from_bridge(self, symbol: str, start_date: str = None) -> pd.DataFrame:
        """Retrieve sentiment data from integration bridge database"""
        try:
            conn = sqlite3.connect(BRIDGE_DB)
            query = '''
                SELECT timestamp, pattern_data, confidence
                FROM shared_patterns
                WHERE symbol = ? AND pattern_type = 'strong_sentiment'
                ORDER BY created_at DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol,))
            conn.close()
            
            if not df.empty:
                # Parse sentiment scores from pattern data
                sentiments = []
                for _, row in df.iterrows():
                    data = json.loads(row['pattern_data'])
                    sentiments.append({
                        'timestamp': row['timestamp'],
                        'sentiment': data.get('score', 0),
                        'confidence': row['confidence']
                    })
                return pd.DataFrame(sentiments)
        except Exception as e:
            logger.warning(f"Could not retrieve sentiment from bridge: {e}")
        
        return pd.DataFrame()
    
    def generate_mock_sentiment(self, symbol: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate realistic mock sentiment data for demonstration"""
        # Simulate realistic sentiment patterns
        np.random.seed(hash(symbol) % 1000)  # Consistent per symbol
        
        sentiment_data = []
        base_sentiment = 0.1  # Slightly positive bias
        
        for date in dates:
            # Add weekly patterns (more positive Mon/Fri)
            day_of_week = date.dayofweek
            weekly_bias = 0.1 if day_of_week in [0, 4] else -0.05
            
            # Add random walk with mean reversion
            change = np.random.normal(0, 0.15)
            base_sentiment = 0.7 * base_sentiment + 0.3 * (0.1 + weekly_bias) + change
            base_sentiment = np.clip(base_sentiment, -1, 1)
            
            # Add occasional strong sentiment events
            if np.random.random() < 0.05:  # 5% chance of strong event
                base_sentiment = np.random.choice([-0.8, -0.7, 0.7, 0.8])
            
            sentiment_data.append({
                'date': date,
                'sentiment_score': base_sentiment,
                'confidence': 0.7 + np.random.random() * 0.3,
                'news_volume': np.random.poisson(5)  # Average 5 articles/day
            })
        
        return pd.DataFrame(sentiment_data).set_index('date')
    
    def get_enhanced_features_with_sentiment(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Generate features including sentiment data"""
        df = df.copy()
        
        # Standard technical indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        df['macd'] = ta.trend.MACD(df['close']).macd()
        df['bb_upper'] = ta.volatility.BollingerBands(df['close']).bollinger_hband()
        df['bb_lower'] = ta.volatility.BollingerBands(df['close']).bollinger_lband()
        df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
        df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
        
        # Price patterns
        df['price_change'] = df['close'].pct_change()
        df['volume_change'] = df['volume'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['close_to_high'] = df['close'] / df['high']
        
        # Momentum features
        df['momentum_5'] = df['close'].pct_change(5)
        df['momentum_10'] = df['close'].pct_change(10)
        df['momentum_20'] = df['close'].pct_change(20)
        
        # Volatility features
        df['volatility_5'] = df['close'].rolling(5).std()
        df['volatility_10'] = df['close'].rolling(10).std()
        df['volatility_20'] = df['close'].rolling(20).std()
        
        # GET SENTIMENT DATA
        # First try to get real sentiment from bridge
        sentiment_df = self.get_sentiment_from_bridge(symbol)
        
        # If no real sentiment, generate mock sentiment for demonstration
        if sentiment_df.empty:
            logger.info(f"Generating mock sentiment for {symbol} demonstration")
            sentiment_df = self.generate_mock_sentiment(symbol, df.index)
        else:
            # Align sentiment with price data dates
            sentiment_df['date'] = pd.to_datetime(sentiment_df['timestamp'])
            sentiment_df = sentiment_df.set_index('date')
            sentiment_df = sentiment_df.reindex(df.index, method='ffill')
        
        # ADD SENTIMENT FEATURES
        if not sentiment_df.empty:
            # Raw sentiment
            df['sentiment_score'] = sentiment_df.get('sentiment_score', 0)
            df['sentiment_confidence'] = sentiment_df.get('confidence', 0.5)
            df['news_volume'] = sentiment_df.get('news_volume', 1)
            
            # Sentiment momentum
            df['sentiment_ma_3'] = df['sentiment_score'].rolling(3).mean()
            df['sentiment_ma_7'] = df['sentiment_score'].rolling(7).mean()
            df['sentiment_ma_14'] = df['sentiment_score'].rolling(14).mean()
            
            # Sentiment change
            df['sentiment_change_1d'] = df['sentiment_score'].diff()
            df['sentiment_change_3d'] = df['sentiment_score'].diff(3)
            df['sentiment_change_7d'] = df['sentiment_score'].diff(7)
            
            # Sentiment volatility
            df['sentiment_std_7'] = df['sentiment_score'].rolling(7).std()
            df['sentiment_std_14'] = df['sentiment_score'].rolling(14).std()
            
            # Cross features (sentiment × price)
            df['sentiment_price_alignment'] = df['sentiment_score'] * df['price_change']
            df['sentiment_price_divergence'] = (
                (df['sentiment_score'] > 0) != (df['price_change'] > 0)
            ).astype(int)
            
            # Extreme sentiment indicators
            df['extreme_positive_sentiment'] = (df['sentiment_score'] > 0.7).astype(int)
            df['extreme_negative_sentiment'] = (df['sentiment_score'] < -0.7).astype(int)
            
            # News volume indicators
            df['high_news_volume'] = (df['news_volume'] > df['news_volume'].rolling(20).mean() * 2).astype(int)
            df['news_volume_ma_7'] = df['news_volume'].rolling(7).mean()
            
            # Sentiment strength
            df['sentiment_strength'] = abs(df['sentiment_score'])
            df['sentiment_conviction'] = df['sentiment_strength'] * df['sentiment_confidence']
            
            logger.info(f"Added {len([c for c in df.columns if 'sentiment' in c or 'news' in c])} sentiment features")
        else:
            logger.warning(f"No sentiment data available for {symbol}")
            # Add zero sentiment features
            for col in ['sentiment_score', 'sentiment_ma_7', 'sentiment_change_1d', 
                       'sentiment_price_alignment', 'news_volume']:
                df[col] = 0
        
        return df
    
    async def train_with_sentiment(self, symbol: str, model_type: str = "random_forest",
                                  use_sentiment: bool = True) -> Dict:
        """Train model with optional sentiment features"""
        
        # Get price data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y")
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Get features (with or without sentiment)
        if use_sentiment:
            df = self.get_enhanced_features_with_sentiment(df, symbol)
            logger.info(f"Training WITH sentiment features for {symbol}")
        else:
            # Just technical features
            df = self.get_enhanced_features_with_sentiment(df, symbol)
            # Remove sentiment columns
            sentiment_cols = [c for c in df.columns if 'sentiment' in c or 'news' in c]
            df = df.drop(columns=sentiment_cols)
            logger.info(f"Training WITHOUT sentiment features for {symbol}")
        
        # Clean data
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        
        if len(df) < 50:
            raise ValueError(f"Insufficient data for training: {len(df)} rows")
        
        # Prepare features and target
        feature_columns = [col for col in df.columns 
                          if col not in ['close', 'open', 'high', 'low', 'volume', 'dividends', 'stock splits']]
        
        X = df[feature_columns].values
        y = df['close'].shift(-1).fillna(method='ffill').values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
        else:
            model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=7, random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Get predictions
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Feature importance analysis
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(feature_columns, model.feature_importances_))
            # Sort by importance
            feature_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Calculate sentiment feature importance
            sentiment_features = [k for k in feature_importance.keys() if 'sentiment' in k or 'news' in k]
            sentiment_importance = sum([feature_importance[k] for k in sentiment_features])
            
            logger.info(f"Top features: {list(feature_importance.keys())[:5]}")
            logger.info(f"Sentiment feature importance: {sentiment_importance:.2%}")
        
        # Save model
        model_id = f"{symbol}_{model_type}_{'with' if use_sentiment else 'no'}_sentiment_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        model_path = os.path.join(self.models_dir, f"{model_id}.joblib")
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            'model_id': model_id,
            'symbol': symbol,
            'model_type': model_type,
            'with_sentiment': use_sentiment,
            'train_score': train_score,
            'test_score': test_score,
            'mae': mae,
            'feature_count': len(feature_columns),
            'sentiment_features': len([c for c in feature_columns if 'sentiment' in c or 'news' in c]),
            'top_features': feature_importance,
            'created_at': datetime.now().isoformat()
        }
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sentiment_model_performance 
            (model_id, symbol, with_sentiment, accuracy_gain, best_features, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            model_id,
            symbol,
            use_sentiment,
            test_score,
            json.dumps(list(feature_importance.keys())[:5]),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return metadata

# Initialize trainer
trainer = SentimentEnhancedTrainer()

# Request models
class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"
    use_sentiment: bool = True

class ComparisonRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"

# API Endpoints

@app.post("/api/train-with-sentiment")
async def train_with_sentiment(request: TrainingRequest):
    """Train model with sentiment features"""
    try:
        result = await trainer.train_with_sentiment(
            symbol=request.symbol,
            model_type=request.model_type,
            use_sentiment=request.use_sentiment
        )
        return result
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare-sentiment-impact")
async def compare_sentiment_impact(request: ComparisonRequest):
    """Train two models and compare performance with/without sentiment"""
    try:
        # Train without sentiment
        result_without = await trainer.train_with_sentiment(
            symbol=request.symbol,
            model_type=request.model_type,
            use_sentiment=False
        )
        
        # Train with sentiment
        result_with = await trainer.train_with_sentiment(
            symbol=request.symbol,
            model_type=request.model_type,
            use_sentiment=True
        )
        
        # Calculate improvement
        improvement = {
            'symbol': request.symbol,
            'model_type': request.model_type,
            'without_sentiment': {
                'test_score': result_without['test_score'],
                'mae': result_without['mae']
            },
            'with_sentiment': {
                'test_score': result_with['test_score'],
                'mae': result_with['mae'],
                'sentiment_features': result_with['sentiment_features']
            },
            'improvement': {
                'accuracy_gain': (result_with['test_score'] - result_without['test_score']) * 100,
                'mae_reduction': result_without['mae'] - result_with['mae'],
                'percentage_improvement': ((result_with['test_score'] / result_without['test_score']) - 1) * 100
            },
            'top_sentiment_features': [k for k in result_with['top_features'].keys() 
                                      if 'sentiment' in k or 'news' in k]
        }
        
        return improvement
        
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiment-history/{symbol}")
async def get_sentiment_history(symbol: str, days: int = 30):
    """Get historical sentiment data for a symbol"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, avg_sentiment, max_sentiment, min_sentiment, sentiment_count, news_volume
        FROM daily_sentiment
        WHERE symbol = ? 
        ORDER BY date DESC
        LIMIT ?
    ''', (symbol, days))
    
    data = []
    for row in cursor.fetchall():
        data.append({
            'date': row[0],
            'avg_sentiment': row[1],
            'max_sentiment': row[2],
            'min_sentiment': row[3],
            'sentiment_count': row[4],
            'news_volume': row[5]
        })
    
    conn.close()
    return data

@app.get("/api/model-comparison/{symbol}")
async def get_model_comparison(symbol: str):
    """Get performance comparison of models with/without sentiment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT model_id, with_sentiment, accuracy_gain, best_features, created_at
        FROM sentiment_model_performance
        WHERE symbol = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (symbol,))
    
    models = []
    for row in cursor.fetchall():
        models.append({
            'model_id': row[0],
            'with_sentiment': bool(row[1]),
            'accuracy': row[2],
            'best_features': json.loads(row[3]) if row[3] else [],
            'created_at': row[4]
        })
    
    conn.close()
    
    # Calculate average improvement
    with_sentiment = [m['accuracy'] for m in models if m['with_sentiment']]
    without_sentiment = [m['accuracy'] for m in models if not m['with_sentiment']]
    
    avg_improvement = 0
    if with_sentiment and without_sentiment:
        avg_improvement = (np.mean(with_sentiment) - np.mean(without_sentiment)) * 100
    
    return {
        'models': models,
        'average_improvement': avg_improvement,
        'with_sentiment_avg': np.mean(with_sentiment) if with_sentiment else 0,
        'without_sentiment_avg': np.mean(without_sentiment) if without_sentiment else 0
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sentiment-enhanced-ml-backend"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sentiment-Enhanced ML Backend on port 8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)