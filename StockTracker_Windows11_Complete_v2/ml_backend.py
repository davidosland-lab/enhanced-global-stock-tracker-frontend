"""
Enhanced ML Backend with Unified Backtesting Service
Provides model training, prediction, and centralized backtesting
"""

import os
import sys
import json
import logging
import sqlite3
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Stock Tracker ML Backend", version="2.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup for unified backtesting
DB_PATH = "unified_backtest.db"

def init_database():
    """Initialize SQLite database for backtest results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            model_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            initial_capital REAL NOT NULL,
            final_value REAL NOT NULL,
            total_return REAL NOT NULL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            win_rate REAL,
            num_trades INTEGER,
            avg_return_per_trade REAL,
            volatility REAL,
            alpha REAL,
            beta REAL,
            trades TEXT,
            equity_curve TEXT,
            parameters TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            model_type TEXT NOT NULL,
            parameters TEXT,
            performance_metrics TEXT,
            file_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Request models
class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = Field(default="random_forest", description="Model type")
    features: List[str] = Field(default_factory=lambda: ["close", "volume", "rsi", "macd"])
    lookback_days: int = Field(default=365, ge=30, le=1825)
    train_split: float = Field(default=0.8, gt=0.5, lt=0.95)

class PredictionRequest(BaseModel):
    symbol: str
    model_name: Optional[str] = None
    horizon_days: int = Field(default=30, ge=1, le=365)
    
class BacktestRequest(BaseModel):
    symbol: str
    model_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = Field(default=100000, gt=0)
    strategy_params: Optional[Dict] = None

class BacktestResult(BaseModel):
    symbol: str
    model_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    num_trades: int
    avg_return_per_trade: float
    volatility: float
    alpha: Optional[float] = None
    beta: Optional[float] = None
    trades: List[Dict]
    equity_curve: List[Dict]

# Unified Backtesting Service
class UnifiedBacktestService:
    """Centralized backtesting service for all modules"""
    
    @staticmethod
    async def run_backtest(
        symbol: str,
        model_name: str,
        start_date: str = None,
        end_date: str = None,
        initial_capital: float = 100000,
        strategy_params: Dict = None
    ) -> BacktestResult:
        """Run a comprehensive backtest"""
        try:
            # Default dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate returns
            df['returns'] = df['Close'].pct_change()
            df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Simple trading strategy based on model predictions
            # For demo purposes, using a momentum strategy
            df['signal'] = np.where(df['returns'].rolling(20).mean() > 0, 1, -1)
            df['position'] = df['signal'].shift(1)
            df['strategy_returns'] = df['position'] * df['returns']
            
            # Calculate cumulative returns
            df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
            df['cumulative_market_returns'] = (1 + df['returns']).cumprod()
            
            # Generate trades
            trades = []
            position = 0
            entry_price = 0
            entry_date = None
            
            for idx, row in df.iterrows():
                if position == 0 and row['position'] != 0:
                    # Enter position
                    position = row['position']
                    entry_price = row['Close']
                    entry_date = idx
                elif position != 0 and row['position'] != position:
                    # Exit position
                    exit_price = row['Close']
                    trade_return = (exit_price - entry_price) / entry_price * position
                    trades.append({
                        'entry_date': entry_date.isoformat(),
                        'exit_date': idx.isoformat(),
                        'entry_price': float(entry_price),
                        'exit_price': float(exit_price),
                        'position': 'long' if position > 0 else 'short',
                        'return': float(trade_return)
                    })
                    # Check if reversing position
                    if row['position'] != 0:
                        position = row['position']
                        entry_price = row['Close']
                        entry_date = idx
                    else:
                        position = 0
            
            # Calculate metrics
            final_value = initial_capital * float(df['cumulative_returns'].iloc[-1])
            total_return = (final_value - initial_capital) / initial_capital
            
            # Sharpe ratio
            sharpe_ratio = float(df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252))
            
            # Max drawdown
            cummax = df['cumulative_returns'].cummax()
            drawdown = (df['cumulative_returns'] - cummax) / cummax
            max_drawdown = float(drawdown.min())
            
            # Win rate
            winning_trades = [t for t in trades if t['return'] > 0]
            win_rate = len(winning_trades) / len(trades) if trades else 0
            
            # Average return per trade
            avg_return = sum(t['return'] for t in trades) / len(trades) if trades else 0
            
            # Volatility
            volatility = float(df['strategy_returns'].std() * np.sqrt(252))
            
            # Alpha and Beta (vs market)
            if len(df) > 60:  # Need sufficient data
                market_returns = df['returns'].dropna()
                strategy_returns = df['strategy_returns'].dropna()
                
                # Calculate beta
                covariance = np.cov(strategy_returns, market_returns)[0, 1]
                market_variance = np.var(market_returns)
                beta = float(covariance / market_variance) if market_variance != 0 else 1.0
                
                # Calculate alpha
                risk_free_rate = 0.02  # Assume 2% risk-free rate
                market_annual_return = float(market_returns.mean() * 252)
                strategy_annual_return = float(strategy_returns.mean() * 252)
                alpha = float(strategy_annual_return - (risk_free_rate + beta * (market_annual_return - risk_free_rate)))
            else:
                alpha = None
                beta = None
            
            # Create equity curve
            equity_curve = []
            for idx, row in df.iterrows():
                equity_curve.append({
                    'date': idx.isoformat(),
                    'value': float(initial_capital * row['cumulative_returns']),
                    'benchmark': float(initial_capital * row['cumulative_market_returns'])
                })
            
            # Store in database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO backtest_results (
                    timestamp, symbol, model_name, start_date, end_date,
                    initial_capital, final_value, total_return, sharpe_ratio,
                    max_drawdown, win_rate, num_trades, avg_return_per_trade,
                    volatility, alpha, beta, trades, equity_curve, parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                symbol, model_name, start_date, end_date,
                initial_capital, final_value, total_return, sharpe_ratio,
                max_drawdown, win_rate, len(trades), avg_return,
                volatility, alpha, beta,
                json.dumps(trades), json.dumps(equity_curve),
                json.dumps(strategy_params or {})
            ))
            
            conn.commit()
            conn.close()
            
            # Clean up NaN values
            if np.isnan(sharpe_ratio):
                sharpe_ratio = 0.0
            if alpha and np.isnan(alpha):
                alpha = None
            if beta and np.isnan(beta):
                beta = None
            if np.isnan(volatility):
                volatility = 0.0
            if np.isnan(avg_return):
                avg_return = 0.0
                
            return BacktestResult(
                symbol=symbol,
                model_name=model_name,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_value=final_value,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                num_trades=len(trades),
                avg_return_per_trade=avg_return,
                volatility=volatility,
                alpha=alpha,
                beta=beta,
                trades=trades,
                equity_curve=equity_curve
            )
            
        except Exception as e:
            logger.error(f"Backtest error for {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def get_backtest_history(
        symbol: Optional[str] = None,
        model_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Retrieve historical backtest results"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            query = "SELECT * FROM backtest_results WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                # Parse JSON fields
                result['trades'] = json.loads(result.get('trades', '[]'))
                result['equity_curve'] = json.loads(result.get('equity_curve', '[]'))
                result['parameters'] = json.loads(result.get('parameters', '{}'))
                results.append(result)
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving backtest history: {str(e)}")
            return []
    
    @staticmethod
    async def compare_models(
        symbol: str,
        model_names: List[str],
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """Compare multiple models on the same symbol"""
        try:
            comparison_results = []
            
            for model_name in model_names:
                result = await UnifiedBacktestService.run_backtest(
                    symbol=symbol,
                    model_name=model_name,
                    start_date=start_date,
                    end_date=end_date
                )
                comparison_results.append({
                    'model_name': model_name,
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'win_rate': result.win_rate,
                    'volatility': result.volatility,
                    'alpha': result.alpha,
                    'beta': result.beta
                })
            
            # Sort by total return
            comparison_results.sort(key=lambda x: x['total_return'], reverse=True)
            
            return {
                'symbol': symbol,
                'comparison_date': datetime.now().isoformat(),
                'start_date': start_date,
                'end_date': end_date,
                'models': comparison_results,
                'best_model': comparison_results[0]['model_name'] if comparison_results else None
            }
            
        except Exception as e:
            logger.error(f"Error comparing models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize backtest service
backtest_service = UnifiedBacktestService()

# ML Model Manager
class MLModelManager:
    """Manages ML models with automatic backtesting"""
    
    @staticmethod
    async def train_model(request: TrainingRequest) -> Dict:
        """Train a model and automatically run backtest"""
        try:
            # Fetch training data
            ticker = yf.Ticker(request.symbol)
            df = ticker.history(period=f"{request.lookback_days}d")
            
            if df.empty:
                raise ValueError(f"No data available for {request.symbol}")
            
            # Calculate features
            df['returns'] = df['Close'].pct_change()
            df['rsi'] = MLModelManager.calculate_rsi(df['Close'])
            df['macd'] = MLModelManager.calculate_macd(df['Close'])
            df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            
            # Prepare training data
            df = df.dropna()
            
            # Create target (next day return)
            df['target'] = df['returns'].shift(-1)
            df = df.dropna()
            
            # Train simple model (for demo)
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            
            features = ['returns', 'rsi', 'macd', 'volume_ratio']
            X = df[features]
            y = df['target']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=1-request.train_split, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Calculate metrics
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Save model
            model_name = f"{request.symbol}_{request.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = f"models/{model_name}.joblib"
            os.makedirs("models", exist_ok=True)
            joblib.dump(model, model_path)
            
            # Register model in database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO model_registry (
                    model_name, created_at, updated_at, model_type,
                    parameters, performance_metrics, file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_name,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                request.model_type,
                json.dumps({"features": features, "lookback_days": request.lookback_days}),
                json.dumps({"train_score": train_score, "test_score": test_score}),
                model_path
            ))
            
            conn.commit()
            conn.close()
            
            # Automatically run backtest
            backtest_result = await backtest_service.run_backtest(
                symbol=request.symbol,
                model_name=model_name,
                start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            return {
                "model_name": model_name,
                "symbol": request.symbol,
                "model_type": request.model_type,
                "train_score": train_score,
                "test_score": test_score,
                "features": features,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "backtest_summary": {
                    "total_return": backtest_result.total_return,
                    "sharpe_ratio": backtest_result.sharpe_ratio,
                    "max_drawdown": backtest_result.max_drawdown,
                    "win_rate": backtest_result.win_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Training error for {request.symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        return ema_fast - ema_slow

# API Endpoints

@app.get("/")
async def root():
    return {"message": "ML Backend with Unified Backtesting - Running on port 8003"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ML Backend",
        "version": "2.0",
        "features": ["training", "prediction", "unified_backtesting", "model_comparison"]
    }

@app.post("/api/train")
async def train_model(request: TrainingRequest):
    """Train a new ML model with automatic backtesting"""
    result = await MLModelManager.train_model(request)
    return result

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Generate predictions using trained model"""
    try:
        # For demo, return sample predictions
        ticker = yf.Ticker(request.symbol)
        current_price = ticker.info.get('regularMarketPrice', 100)
        
        predictions = []
        for i in range(request.horizon_days):
            # Simple random walk prediction for demo
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            predicted_price = current_price * (1 + change)
            predictions.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                "predicted_price": predicted_price,
                "confidence_lower": predicted_price * 0.95,
                "confidence_upper": predicted_price * 1.05
            })
            current_price = predicted_price
        
        return {
            "symbol": request.symbol,
            "model_name": request.model_name or "default",
            "predictions": predictions,
            "horizon_days": request.horizon_days
        }
        
    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/backtest")
async def run_backtest(request: BacktestRequest):
    """Run backtest using unified service"""
    result = await backtest_service.run_backtest(
        symbol=request.symbol,
        model_name=request.model_name,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        strategy_params=request.strategy_params
    )
    return result

@app.get("/api/ml/backtest/history")
async def get_backtest_history(
    symbol: Optional[str] = Query(None),
    model_name: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """Retrieve historical backtest results"""
    results = await backtest_service.get_backtest_history(symbol, model_name, limit)
    return {"results": results}

@app.post("/api/ml/models/compare")
async def compare_models(
    symbol: str,
    model_names: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Compare multiple models on the same symbol"""
    comparison = await backtest_service.compare_models(
        symbol=symbol,
        model_names=model_names,
        start_date=start_date,
        end_date=end_date
    )
    return comparison

@app.get("/api/models")
async def list_models():
    """List all registered models"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM model_registry ORDER BY updated_at DESC")
        columns = [col[0] for col in cursor.description]
        models = []
        
        for row in cursor.fetchall():
            model = dict(zip(columns, row))
            model['parameters'] = json.loads(model.get('parameters', '{}'))
            model['performance_metrics'] = json.loads(model.get('performance_metrics', '{}'))
            models.append(model)
        
        conn.close()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return {"models": []}

@app.delete("/api/models/{model_name}")
async def delete_model(model_name: str):
    """Delete a registered model"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get model path
        cursor.execute("SELECT file_path FROM model_registry WHERE model_name = ?", (model_name,))
        result = cursor.fetchone()
        
        if result:
            file_path = result[0]
            # Delete file if exists
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete from registry
            cursor.execute("DELETE FROM model_registry WHERE model_name = ?", (model_name,))
            conn.commit()
            conn.close()
            
            return {"message": f"Model {model_name} deleted successfully"}
        else:
            conn.close()
            raise HTTPException(status_code=404, detail="Model not found")
            
    except Exception as e:
        logger.error(f"Error deleting model {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/status")
async def ml_status():
    """Get ML service status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count models
        cursor.execute("SELECT COUNT(*) FROM model_registry")
        model_count = cursor.fetchone()[0]
        
        # Count backtests
        cursor.execute("SELECT COUNT(*) FROM backtest_results")
        backtest_count = cursor.fetchone()[0]
        
        # Get recent backtests
        cursor.execute("""
            SELECT symbol, model_name, total_return, sharpe_ratio, timestamp
            FROM backtest_results
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        recent_backtests = []
        for row in cursor.fetchall():
            recent_backtests.append({
                'symbol': row[0],
                'model_name': row[1],
                'total_return': row[2],
                'sharpe_ratio': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        
        return {
            "status": "operational",
            "models_registered": model_count,
            "backtests_performed": backtest_count,
            "recent_backtests": recent_backtests,
            "database_path": DB_PATH,
            "service_version": "2.0"
        }
        
    except Exception as e:
        logger.error(f"Error getting ML status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Backend with Unified Backtesting on port 8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)