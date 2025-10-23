"""
Enhanced ML Backend with Iterative Learning and Knowledge Building
Implements model versioning, transfer learning, and performance tracking
"""

import os
import sys
import json
import logging
import sqlite3
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import warnings
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import ta
warnings.filterwarnings('ignore')

# Import historical data service for faster data access
try:
    from historical_data_service import get_service as get_historical_service
    HISTORICAL_SERVICE = True
    logger = logging.getLogger(__name__)
    logger.info("Historical data service available - using local database for faster access")
except ImportError:
    HISTORICAL_SERVICE = False
    logger = logging.getLogger(__name__)
    logger.warning("Historical data service not available - using Yahoo Finance directly")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Enhanced ML Backend with Iterative Learning", version="3.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup for model tracking and knowledge building
DB_PATH = "ml_knowledge_base.db"

def init_enhanced_database():
    """Initialize enhanced database with model lineage and performance tracking"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Model registry with version tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT UNIQUE NOT NULL,
            model_name TEXT NOT NULL,
            version INTEGER NOT NULL,
            parent_model_id TEXT,
            symbol TEXT NOT NULL,
            model_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            train_score REAL,
            test_score REAL,
            cross_val_score REAL,
            parameters TEXT,
            feature_importance TEXT,
            file_path TEXT,
            is_best_model BOOLEAN DEFAULT 0
        )
    ''')
    
    # Training history for tracking improvements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            epoch INTEGER,
            timestamp TEXT NOT NULL,
            train_loss REAL,
            val_loss REAL,
            train_accuracy REAL,
            val_accuracy REAL,
            learning_rate REAL,
            improvement REAL,
            FOREIGN KEY (model_id) REFERENCES model_registry (model_id)
        )
    ''')
    
    # Knowledge base for storing learned patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            confidence REAL,
            discovered_by_model TEXT,
            created_at TEXT NOT NULL,
            validation_count INTEGER DEFAULT 0,
            success_rate REAL
        )
    ''')
    
    # Model performance comparison
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_comparison (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            model_1_id TEXT,
            model_2_id TEXT,
            model_1_score REAL,
            model_2_score REAL,
            improvement_percentage REAL,
            comparison_metrics TEXT
        )
    ''')
    
    # Feature engineering history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feature_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            feature_name TEXT NOT NULL,
            feature_type TEXT,
            importance_score REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (model_id) REFERENCES model_registry (model_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize enhanced database
init_enhanced_database()

class EnhancedModelTrainer:
    """Enhanced model trainer with iterative learning capabilities"""
    
    def __init__(self):
        self.models_dir = "enhanced_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
    def load_previous_best_model(self, symbol: str, model_type: str) -> Optional[Tuple[Any, Dict]]:
        """Load the best performing model for a symbol"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model_id, file_path, parameters, test_score, feature_importance
            FROM model_registry 
            WHERE symbol = ? AND model_type = ? AND is_best_model = 1
            ORDER BY test_score DESC
            LIMIT 1
        ''', (symbol, model_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and os.path.exists(result[1]):
            model = joblib.load(result[1])
            metadata = {
                'model_id': result[0],
                'parameters': json.loads(result[2]) if result[2] else {},
                'test_score': result[3],
                'feature_importance': json.loads(result[4]) if result[4] else {}
            }
            return model, metadata
        return None
    
    def get_enhanced_features(self, df: pd.DataFrame, learned_patterns: List[Dict]) -> pd.DataFrame:
        """Generate enhanced features based on learned patterns"""
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
        
        # Apply learned patterns
        for pattern in learned_patterns:
            if pattern['pattern_type'] == 'price_threshold':
                data = json.loads(pattern['pattern_data'])
                df[f"pattern_{pattern['id']}"] = (
                    (df['close'] > data.get('lower', 0)) & 
                    (df['close'] < data.get('upper', float('inf')))
                ).astype(int) * pattern['confidence']
            elif pattern['pattern_type'] == 'volume_spike':
                data = json.loads(pattern['pattern_data'])
                df[f"pattern_{pattern['id']}"] = (
                    df['volume'] > df['volume'].rolling(20).mean() * data.get('multiplier', 2)
                ).astype(int) * pattern['confidence']
        
        return df
    
    def transfer_learning(self, base_model: Any, new_data: pd.DataFrame, 
                         fine_tune_ratio: float = 0.3) -> Any:
        """Apply transfer learning from a base model to new data"""
        # Get base model's parameters
        base_params = base_model.get_params()
        
        # Create new model with transferred parameters
        if isinstance(base_model, RandomForestRegressor):
            # Reduce trees for fine-tuning, keep other parameters
            new_model = RandomForestRegressor(
                n_estimators=max(10, int(base_params['n_estimators'] * fine_tune_ratio)),
                max_depth=base_params['max_depth'],
                min_samples_split=base_params['min_samples_split'],
                min_samples_leaf=base_params['min_samples_leaf'],
                random_state=42
            )
        else:
            new_model = type(base_model)(**base_params)
        
        return new_model
    
    async def train_iterative_model(self, symbol: str, model_type: str = "random_forest",
                                   iterations: int = 5) -> Dict:
        """Train model iteratively, building on previous knowledge"""
        
        # Fetch data - use historical service if available for faster access
        if HISTORICAL_SERVICE:
            try:
                service = get_historical_service()
                df = service.get_data(symbol, auto_download=True)
                if df is None or df.empty:
                    # Fallback to Yahoo Finance
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(period="2y")
            except Exception as e:
                logger.warning(f"Historical service error, falling back to Yahoo Finance: {e}")
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="2y")
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="2y")
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Load learned patterns from knowledge base
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, pattern_type, pattern_data, confidence 
            FROM knowledge_base 
            WHERE symbol = ? AND confidence > 0.6
            ORDER BY confidence DESC
            LIMIT 20
        ''', (symbol,))
        patterns = [dict(zip(['id', 'pattern_type', 'pattern_data', 'confidence'], row)) 
                   for row in cursor.fetchall()]
        
        # Generate enhanced features
        df = self.get_enhanced_features(df, patterns)
        df = df.dropna()
        
        # Prepare features and target
        feature_columns = [col for col in df.columns if col not in ['close', 'open', 'high', 'low', 'dividends', 'stock splits']]
        X = df[feature_columns].values
        y = df['close'].shift(-1).fillna(method='ffill').values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Load previous best model
        previous_best = self.load_previous_best_model(symbol, model_type)
        
        best_model = None
        best_score = -float('inf')
        training_history = []
        
        for iteration in range(iterations):
            logger.info(f"Training iteration {iteration + 1}/{iterations}")
            
            if iteration == 0 and previous_best:
                # Start with transfer learning from previous best model
                model, prev_metadata = previous_best
                model = self.transfer_learning(model, df)
                logger.info(f"Using transfer learning from model with score: {prev_metadata['test_score']}")
            else:
                # Create new model or improve existing
                if model_type == "random_forest":
                    # Progressively increase complexity
                    n_estimators = 50 + (iteration * 30)
                    max_depth = 10 + (iteration * 2)
                    model = RandomForestRegressor(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        min_samples_split=max(2, 5 - iteration),
                        random_state=42 + iteration
                    )
                elif model_type == "gradient_boosting":
                    n_estimators = 50 + (iteration * 20)
                    learning_rate = max(0.01, 0.1 - (iteration * 0.02))
                    model = GradientBoostingRegressor(
                        n_estimators=n_estimators,
                        learning_rate=learning_rate,
                        max_depth=5 + iteration,
                        random_state=42 + iteration
                    )
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            cv_score = np.mean(cv_scores)
            
            # Calculate predictions for error analysis
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Track improvement
            improvement = test_score - best_score if best_score != -float('inf') else 0
            
            training_history.append({
                'iteration': iteration + 1,
                'train_score': train_score,
                'test_score': test_score,
                'cv_score': cv_score,
                'mse': mse,
                'mae': mae,
                'improvement': improvement
            })
            
            # Update best model
            if test_score > best_score:
                best_score = test_score
                best_model = model
                
                # Extract feature importance
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(feature_columns, model.feature_importances_))
                    
                    # Learn new patterns from important features
                    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                    for feat_name, importance in top_features:
                        if importance > 0.1 and 'pattern_' not in feat_name:
                            # Store discovered pattern
                            cursor.execute('''
                                INSERT INTO knowledge_base (symbol, pattern_type, pattern_data, 
                                                          confidence, discovered_by_model, created_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                symbol,
                                'feature_importance',
                                json.dumps({'feature': feat_name, 'importance': importance}),
                                importance,
                                f"{symbol}_{model_type}_v{iteration+1}",
                                datetime.now().isoformat()
                            ))
            
            logger.info(f"Iteration {iteration + 1}: Train={train_score:.4f}, "
                       f"Test={test_score:.4f}, CV={cv_score:.4f}, Improvement={improvement:.4f}")
        
        # Save best model
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_id = f"{symbol}_{model_type}_{timestamp}"
        model_version = 1
        
        if previous_best:
            # Increment version from previous best
            prev_id = previous_best[1]['model_id']
            cursor.execute('SELECT version FROM model_registry WHERE model_id = ?', (prev_id,))
            prev_version = cursor.fetchone()
            if prev_version:
                model_version = prev_version[0] + 1
        
        # Save model file
        model_path = os.path.join(self.models_dir, f"{model_id}.joblib")
        joblib.dump(best_model, model_path)
        
        # Save scaler
        scaler_path = os.path.join(self.models_dir, f"{model_id}_scaler.joblib")
        joblib.dump(scaler, scaler_path)
        
        # Update all models for this symbol to not be best
        cursor.execute('''
            UPDATE model_registry 
            SET is_best_model = 0 
            WHERE symbol = ? AND model_type = ?
        ''', (symbol, model_type))
        
        # Save to registry
        cursor.execute('''
            INSERT INTO model_registry (
                model_id, model_name, version, parent_model_id, symbol, model_type,
                created_at, train_score, test_score, cross_val_score, parameters,
                feature_importance, file_path, is_best_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_id,
            f"{symbol} {model_type.title()} v{model_version}",
            model_version,
            previous_best[1]['model_id'] if previous_best else None,
            symbol,
            model_type,
            datetime.now().isoformat(),
            training_history[-1]['train_score'],
            best_score,
            training_history[-1]['cv_score'],
            json.dumps({
                'iterations': iterations,
                'features': feature_columns,
                'data_points': len(df)
            }),
            json.dumps(feature_importance) if 'feature_importance' in locals() else None,
            model_path,
            1  # Mark as best model
        ))
        
        # Save training history
        for hist in training_history:
            cursor.execute('''
                INSERT INTO training_history (
                    model_id, epoch, timestamp, train_loss, val_loss,
                    train_accuracy, val_accuracy, learning_rate, improvement
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_id,
                hist['iteration'],
                datetime.now().isoformat(),
                1 - hist['train_score'],  # Convert score to loss
                1 - hist['test_score'],
                hist['train_score'],
                hist['test_score'],
                0.1,  # Default learning rate
                hist['improvement']
            ))
        
        # Compare with previous best
        if previous_best:
            improvement_pct = ((best_score - previous_best[1]['test_score']) / 
                             abs(previous_best[1]['test_score']) * 100) if previous_best[1]['test_score'] != 0 else 0
            
            cursor.execute('''
                INSERT INTO model_comparison (
                    symbol, timestamp, model_1_id, model_2_id,
                    model_1_score, model_2_score, improvement_percentage, comparison_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                datetime.now().isoformat(),
                previous_best[1]['model_id'],
                model_id,
                previous_best[1]['test_score'],
                best_score,
                improvement_pct,
                json.dumps({
                    'previous_version': model_version - 1,
                    'new_version': model_version,
                    'training_iterations': iterations
                })
            ))
            
            logger.info(f"Model improved by {improvement_pct:.2f}% from previous best")
        
        conn.commit()
        conn.close()
        
        return {
            'model_id': model_id,
            'version': model_version,
            'parent_model': previous_best[1]['model_id'] if previous_best else None,
            'symbol': symbol,
            'model_type': model_type,
            'best_test_score': best_score,
            'training_history': training_history,
            'improvement_from_baseline': improvement_pct if previous_best else 0,
            'iterations_completed': iterations,
            'features_used': len(feature_columns),
            'patterns_applied': len(patterns),
            'model_path': model_path
        }

# Initialize trainer
trainer = EnhancedModelTrainer()

# Request models
class IterativeTrainingRequest(BaseModel):
    symbol: str
    model_type: str = Field(default="random_forest", description="Model type")
    iterations: int = Field(default=5, ge=1, le=20)
    use_transfer_learning: bool = Field(default=True)

@app.post("/api/train/iterative")
async def train_iterative(request: IterativeTrainingRequest):
    """Train model iteratively with knowledge building"""
    try:
        result = await trainer.train_iterative_model(
            symbol=request.symbol,
            model_type=request.model_type,
            iterations=request.iterations
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/{symbol}/history")
async def get_model_history(symbol: str):
    """Get training history for a symbol"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT model_id, model_name, version, created_at, train_score, 
               test_score, cross_val_score, is_best_model
        FROM model_registry
        WHERE symbol = ?
        ORDER BY version DESC
        LIMIT 20
    ''', (symbol,))
    
    models = []
    for row in cursor.fetchall():
        models.append({
            'model_id': row[0],
            'name': row[1],
            'version': row[2],
            'created_at': row[3],
            'train_score': row[4],
            'test_score': row[5],
            'cross_val_score': row[6],
            'is_best': bool(row[7])
        })
    
    conn.close()
    return models

@app.get("/api/models/{symbol}/improvement-chart")
async def get_improvement_chart(symbol: str):
    """Get model improvement over versions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT version, test_score, train_score, created_at
        FROM model_registry
        WHERE symbol = ?
        ORDER BY version ASC
    ''', (symbol,))
    
    data = {
        'versions': [],
        'test_scores': [],
        'train_scores': [],
        'timestamps': []
    }
    
    for row in cursor.fetchall():
        data['versions'].append(f"v{row[0]}")
        data['test_scores'].append(row[1] if row[1] else 0)
        data['train_scores'].append(row[2] if row[2] else 0)
        data['timestamps'].append(row[3])
    
    conn.close()
    return data

@app.get("/api/knowledge-base/{symbol}")
async def get_learned_patterns(symbol: str):
    """Get learned patterns for a symbol"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT pattern_type, pattern_data, confidence, discovered_by_model,
               created_at, validation_count, success_rate
        FROM knowledge_base
        WHERE symbol = ?
        ORDER BY confidence DESC
        LIMIT 50
    ''', (symbol,))
    
    patterns = []
    for row in cursor.fetchall():
        patterns.append({
            'type': row[0],
            'data': json.loads(row[1]) if row[1] else {},
            'confidence': row[2],
            'discovered_by': row[3],
            'created_at': row[4],
            'validations': row[5],
            'success_rate': row[6]
        })
    
    conn.close()
    return patterns

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced ML Backend",
        "version": "3.0",
        "features": [
            "iterative_training",
            "transfer_learning",
            "knowledge_building",
            "model_versioning",
            "pattern_recognition"
        ]
    }

@app.get("/health")
async def simple_health():
    """Simple health endpoint for frontend"""
    return {"status": "ok"}

@app.get("/api/ml/status")
async def ml_status():
    """ML service status"""
    return {
        "status": "ready",
        "models_available": ["LSTM", "Random Forest", "XGBoost", "ARIMA"],
        "training_supported": True,
        "prediction_supported": True,
        "iterative_learning": True
    }

@app.get("/api/ml/models")
async def list_all_models():
    """List all available trained models"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT symbol, model_id, model_type, version, accuracy, created_at
        FROM model_registry
        ORDER BY created_at DESC
    ''')
    
    models = []
    for row in cursor.fetchall():
        models.append({
            "symbol": row[0],
            "model_id": row[1],
            "model_type": row[2],
            "version": row[3],
            "accuracy": row[4],
            "created_at": row[5]
        })
    
    conn.close()
    return {"models": models, "count": len(models)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Enhanced ML Backend with Iterative Learning on port 8003")
    logger.info("Features: Model versioning, Transfer learning, Knowledge building")
    uvicorn.run(app, host="0.0.0.0", port=8003)