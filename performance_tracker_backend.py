"""
Performance Tracker Backend - Model and Prediction Performance Monitoring
Tracks ML model accuracy, prediction success rates, and backtesting results over time
Port: 8010
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Data processing
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Performance Tracker Backend", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for tracking
PERFORMANCE_DB = "performance_tracker.db"

# Request models
class PredictionRecord(BaseModel):
    symbol: str
    predicted_price: float
    actual_price: Optional[float] = None
    prediction_date: str
    target_date: str
    model_type: str = "RandomForest"
    confidence: float = 0.0
    sentiment_score: Optional[float] = None
    features_used: Optional[Dict] = None

class BacktestRecord(BaseModel):
    strategy: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int

class ModelTrainingRecord(BaseModel):
    model_type: str
    symbol: str
    training_date: str
    training_samples: int
    features_count: int
    mse: float
    rmse: float
    mae: float
    r2: float
    training_time: float

def init_database():
    """Initialize SQLite database for performance tracking"""
    conn = sqlite3.connect(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    # Predictions tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            actual_price REAL,
            prediction_date TEXT NOT NULL,
            target_date TEXT NOT NULL,
            model_type TEXT NOT NULL,
            confidence REAL,
            sentiment_score REAL,
            error_percent REAL,
            features TEXT,
            timestamp INTEGER NOT NULL
        )
    """)
    
    # Model training history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            training_date TEXT NOT NULL,
            training_samples INTEGER,
            features_count INTEGER,
            mse REAL,
            rmse REAL,
            mae REAL,
            r2 REAL,
            training_time REAL,
            timestamp INTEGER NOT NULL
        )
    """)
    
    # Backtesting results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            initial_capital REAL,
            final_value REAL,
            total_return REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            win_rate REAL,
            total_trades INTEGER,
            timestamp INTEGER NOT NULL
        )
    """)
    
    # Performance metrics aggregation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            metric_value REAL NOT NULL,
            details TEXT,
            timestamp INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

@app.get("/")
async def root():
    return {"message": "Performance Tracker Backend", "version": "1.0", "port": 8010}

@app.post("/api/record_prediction")
async def record_prediction(prediction: PredictionRecord):
    """Record a new prediction for tracking"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Calculate error if actual price is provided
        error_percent = None
        if prediction.actual_price is not None and prediction.predicted_price != 0:
            error_percent = ((prediction.actual_price - prediction.predicted_price) / prediction.predicted_price) * 100
        
        cursor.execute("""
            INSERT INTO predictions (
                symbol, predicted_price, actual_price, prediction_date, 
                target_date, model_type, confidence, sentiment_score, 
                error_percent, features, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction.symbol,
            prediction.predicted_price,
            prediction.actual_price,
            prediction.prediction_date,
            prediction.target_date,
            prediction.model_type,
            prediction.confidence,
            prediction.sentiment_score,
            error_percent,
            json.dumps(prediction.features_used) if prediction.features_used else None,
            int(datetime.now().timestamp())
        ))
        
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "error_percent": error_percent,
            "message": "Prediction recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error recording prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update_prediction")
async def update_prediction(prediction_id: int, actual_price: float):
    """Update a prediction with actual price once available"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Get the prediction
        cursor.execute("SELECT predicted_price FROM predictions WHERE id = ?", (prediction_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        predicted_price = result[0]
        error_percent = ((actual_price - predicted_price) / predicted_price) * 100 if predicted_price != 0 else 0
        
        # Update with actual price
        cursor.execute("""
            UPDATE predictions 
            SET actual_price = ?, error_percent = ?
            WHERE id = ?
        """, (actual_price, error_percent, prediction_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "predicted": predicted_price,
            "actual": actual_price,
            "error_percent": round(error_percent, 2)
        }
        
    except Exception as e:
        logger.error(f"Error updating prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/record_training")
async def record_training(training: ModelTrainingRecord):
    """Record model training performance"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO model_training (
                model_type, symbol, training_date, training_samples,
                features_count, mse, rmse, mae, r2, training_time, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            training.model_type,
            training.symbol,
            training.training_date,
            training.training_samples,
            training.features_count,
            training.mse,
            training.rmse,
            training.mae,
            training.r2,
            training.training_time,
            int(datetime.now().timestamp())
        ))
        
        conn.commit()
        training_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success",
            "training_id": training_id,
            "message": "Training metrics recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error recording training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/record_backtest")
async def record_backtest(backtest: BacktestRecord):
    """Record backtesting results"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO backtest_results (
                strategy, symbol, start_date, end_date, initial_capital,
                final_value, total_return, sharpe_ratio, max_drawdown,
                win_rate, total_trades, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            backtest.strategy,
            backtest.symbol,
            backtest.start_date,
            backtest.end_date,
            backtest.initial_capital,
            backtest.final_value,
            backtest.total_return,
            backtest.sharpe_ratio,
            backtest.max_drawdown,
            backtest.win_rate,
            backtest.total_trades,
            int(datetime.now().timestamp())
        ))
        
        conn.commit()
        backtest_id = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success",
            "backtest_id": backtest_id,
            "message": "Backtest results recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error recording backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prediction_accuracy")
async def get_prediction_accuracy(symbol: Optional[str] = None, days: int = 30):
    """Get prediction accuracy statistics"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Build query
        query = """
            SELECT symbol, model_type, 
                   AVG(ABS(error_percent)) as avg_error,
                   COUNT(*) as total_predictions,
                   SUM(CASE WHEN ABS(error_percent) < 5 THEN 1 ELSE 0 END) as accurate_predictions,
                   MIN(error_percent) as best_error,
                   MAX(error_percent) as worst_error,
                   AVG(confidence) as avg_confidence
            FROM predictions
            WHERE actual_price IS NOT NULL 
            AND prediction_date >= ?
        """
        
        params = [start_date]
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
            
        query += " GROUP BY symbol, model_type"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format results
        accuracy_data = []
        for row in results:
            total_preds = row[3]
            accurate_preds = row[4]
            accuracy_rate = (accurate_preds / total_preds * 100) if total_preds > 0 else 0
            
            accuracy_data.append({
                "symbol": row[0],
                "model_type": row[1],
                "avg_error_percent": round(row[2], 2) if row[2] else 0,
                "total_predictions": total_preds,
                "accurate_predictions": accurate_preds,
                "accuracy_rate": round(accuracy_rate, 2),
                "best_error": round(row[5], 2) if row[5] else 0,
                "worst_error": round(row[6], 2) if row[6] else 0,
                "avg_confidence": round(row[7], 2) if row[7] else 0
            })
        
        # Get recent predictions for chart
        chart_query = """
            SELECT prediction_date, predicted_price, actual_price, error_percent
            FROM predictions
            WHERE actual_price IS NOT NULL 
            AND prediction_date >= ?
        """
        
        if symbol:
            chart_query += " AND symbol = ?"
        chart_query += " ORDER BY prediction_date DESC LIMIT 100"
        
        cursor.execute(chart_query, params)
        chart_data = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "success",
            "period_days": days,
            "accuracy_statistics": accuracy_data,
            "chart_data": [
                {
                    "date": row[0],
                    "predicted": row[1],
                    "actual": row[2],
                    "error": round(row[3], 2) if row[3] else 0
                }
                for row in chart_data
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting accuracy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model_performance")
async def get_model_performance(model_type: Optional[str] = None, days: int = 30):
    """Get model training performance over time"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Build query
        query = """
            SELECT model_type, 
                   AVG(r2) as avg_r2,
                   AVG(rmse) as avg_rmse,
                   AVG(mae) as avg_mae,
                   AVG(training_time) as avg_training_time,
                   COUNT(*) as total_trainings,
                   MAX(r2) as best_r2,
                   MIN(rmse) as best_rmse
            FROM model_training
            WHERE training_date >= ?
        """
        
        params = [start_date]
        if model_type:
            query += " AND model_type = ?"
            params.append(model_type)
            
        query += " GROUP BY model_type"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format results
        performance_data = []
        for row in results:
            performance_data.append({
                "model_type": row[0],
                "avg_r2_score": round(row[1], 4) if row[1] else 0,
                "avg_rmse": round(row[2], 4) if row[2] else 0,
                "avg_mae": round(row[3], 4) if row[3] else 0,
                "avg_training_time": round(row[4], 2) if row[4] else 0,
                "total_trainings": row[5],
                "best_r2": round(row[6], 4) if row[6] else 0,
                "best_rmse": round(row[7], 4) if row[7] else 0
            })
        
        # Get training history
        history_query = """
            SELECT training_date, model_type, r2, rmse, mae, training_time
            FROM model_training
            WHERE training_date >= ?
        """
        
        if model_type:
            history_query += " AND model_type = ?"
        history_query += " ORDER BY training_date DESC LIMIT 100"
        
        cursor.execute(history_query, params)
        history_data = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "success",
            "period_days": days,
            "model_performance": performance_data,
            "training_history": [
                {
                    "date": row[0],
                    "model": row[1],
                    "r2": round(row[2], 4) if row[2] else 0,
                    "rmse": round(row[3], 4) if row[3] else 0,
                    "mae": round(row[4], 4) if row[4] else 0,
                    "time": round(row[5], 2) if row[5] else 0
                }
                for row in history_data
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest_performance")
async def get_backtest_performance(strategy: Optional[str] = None, days: int = 90):
    """Get backtesting performance statistics"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Calculate date range
        start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Build query
        query = """
            SELECT strategy,
                   AVG(total_return) as avg_return,
                   AVG(sharpe_ratio) as avg_sharpe,
                   AVG(max_drawdown) as avg_drawdown,
                   AVG(win_rate) as avg_win_rate,
                   COUNT(*) as total_backtests,
                   MAX(total_return) as best_return,
                   MIN(max_drawdown) as best_drawdown
            FROM backtest_results
            WHERE timestamp >= ?
        """
        
        params = [start_timestamp]
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
            
        query += " GROUP BY strategy"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format results
        backtest_data = []
        for row in results:
            backtest_data.append({
                "strategy": row[0],
                "avg_return": round(row[1], 2) if row[1] else 0,
                "avg_sharpe_ratio": round(row[2], 2) if row[2] else 0,
                "avg_max_drawdown": round(row[3], 2) if row[3] else 0,
                "avg_win_rate": round(row[4], 2) if row[4] else 0,
                "total_backtests": row[5],
                "best_return": round(row[6], 2) if row[6] else 0,
                "best_drawdown": round(row[7], 2) if row[7] else 0
            })
        
        # Get backtest history
        history_query = """
            SELECT start_date, end_date, strategy, symbol, 
                   total_return, sharpe_ratio, max_drawdown, win_rate
            FROM backtest_results
            WHERE timestamp >= ?
        """
        
        if strategy:
            history_query += " AND strategy = ?"
        history_query += " ORDER BY timestamp DESC LIMIT 100"
        
        cursor.execute(history_query, params)
        history_data = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "success",
            "period_days": days,
            "strategy_performance": backtest_data,
            "backtest_history": [
                {
                    "start": row[0],
                    "end": row[1],
                    "strategy": row[2],
                    "symbol": row[3],
                    "return": round(row[4], 2) if row[4] else 0,
                    "sharpe": round(row[5], 2) if row[5] else 0,
                    "drawdown": round(row[6], 2) if row[6] else 0,
                    "win_rate": round(row[7], 2) if row[7] else 0
                }
                for row in history_data
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting backtest performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance_summary")
async def get_performance_summary(days: int = 30):
    """Get overall performance summary"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Date ranges
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Get prediction accuracy
        cursor.execute("""
            SELECT COUNT(*) as total,
                   AVG(ABS(error_percent)) as avg_error,
                   SUM(CASE WHEN ABS(error_percent) < 5 THEN 1 ELSE 0 END) as accurate
            FROM predictions
            WHERE actual_price IS NOT NULL AND prediction_date >= ?
        """, (start_date,))
        pred_result = cursor.fetchone()
        
        # Get model performance
        cursor.execute("""
            SELECT AVG(r2) as avg_r2, AVG(rmse) as avg_rmse
            FROM model_training
            WHERE training_date >= ?
        """, (start_date,))
        model_result = cursor.fetchone()
        
        # Get backtest performance
        cursor.execute("""
            SELECT AVG(total_return) as avg_return, AVG(sharpe_ratio) as avg_sharpe
            FROM backtest_results
            WHERE timestamp >= ?
        """, (start_timestamp,))
        backtest_result = cursor.fetchone()
        
        # Get best performing symbols
        cursor.execute("""
            SELECT symbol, COUNT(*) as count, AVG(ABS(error_percent)) as avg_error
            FROM predictions
            WHERE actual_price IS NOT NULL AND prediction_date >= ?
            GROUP BY symbol
            ORDER BY avg_error ASC
            LIMIT 5
        """, (start_date,))
        best_symbols = cursor.fetchall()
        
        conn.close()
        
        # Calculate summary metrics
        total_predictions = pred_result[0] if pred_result[0] else 0
        accurate_predictions = pred_result[2] if pred_result[2] else 0
        accuracy_rate = (accurate_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        return {
            "status": "success",
            "period_days": days,
            "summary": {
                "predictions": {
                    "total": total_predictions,
                    "accuracy_rate": round(accuracy_rate, 2),
                    "avg_error_percent": round(pred_result[1], 2) if pred_result[1] else 0
                },
                "models": {
                    "avg_r2_score": round(model_result[0], 4) if model_result and model_result[0] else 0,
                    "avg_rmse": round(model_result[1], 4) if model_result and model_result[1] else 0
                },
                "backtesting": {
                    "avg_return": round(backtest_result[0], 2) if backtest_result and backtest_result[0] else 0,
                    "avg_sharpe_ratio": round(backtest_result[1], 2) if backtest_result and backtest_result[1] else 0
                },
                "best_performing_symbols": [
                    {
                        "symbol": row[0],
                        "predictions": row[1],
                        "avg_error": round(row[2], 2) if row[2] else 0
                    }
                    for row in best_symbols
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/clear_old_data")
async def clear_old_data(days_to_keep: int = 90):
    """Clear old performance data"""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        cursor = conn.cursor()
        
        # Calculate cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        cutoff_timestamp = int((datetime.now() - timedelta(days=days_to_keep)).timestamp())
        
        # Clear old predictions
        cursor.execute("DELETE FROM predictions WHERE prediction_date < ?", (cutoff_date,))
        predictions_deleted = cursor.rowcount
        
        # Clear old training records
        cursor.execute("DELETE FROM model_training WHERE training_date < ?", (cutoff_date,))
        trainings_deleted = cursor.rowcount
        
        # Clear old backtest results
        cursor.execute("DELETE FROM backtest_results WHERE timestamp < ?", (cutoff_timestamp,))
        backtests_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "deleted": {
                "predictions": predictions_deleted,
                "training_records": trainings_deleted,
                "backtest_results": backtests_deleted
            },
            "message": f"Cleared data older than {days_to_keep} days"
        }
        
    except Exception as e:
        logger.error(f"Error clearing old data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize database on startup
init_database()

if __name__ == "__main__":
    port = 8010
    logger.info(f"Starting Performance Tracker Backend on port {port}...")
    
    # Initialize database
    init_database()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)