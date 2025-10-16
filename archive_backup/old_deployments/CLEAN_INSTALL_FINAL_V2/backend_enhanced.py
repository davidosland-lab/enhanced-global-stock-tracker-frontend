#!/usr/bin/env python3
"""
Enhanced Backend with Document Analysis Integration
Version: 5.1.0
Adds document-stock linking and sentiment retrieval endpoints
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

import yfinance as yf
import pandas as pd
import numpy as np
from cachetools import TTLCache
from pydantic import BaseModel

from backend_core import get_stock_info, get_aest_time, INDICES, POPULAR_STOCKS
from document_analyzer import analyze_document, FINBERT_AVAILABLE, PDF_SUPPORT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Tracker API Enhanced", version="5.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache
stock_cache = TTLCache(maxsize=100, ttl=300)

# Directories
DIRS = {
    'historical': Path('historical_data'),
    'uploads': Path('uploads'),
    'analysis_cache': Path('analysis_cache'),
    'models': Path('ml_models'),
    'db': Path('database')
}

for dir_path in DIRS.values():
    dir_path.mkdir(exist_ok=True)

# Database setup for document-stock linking
DB_PATH = DIRS['db'] / 'document_analysis.db'

def init_database():
    """Initialize SQLite database for document analysis storage"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE,
            filename TEXT,
            stock_symbol TEXT,
            sentiment TEXT,
            confidence REAL,
            sentiment_positive REAL,
            sentiment_negative REAL,
            sentiment_neutral REAL,
            summary TEXT,
            word_count INTEGER,
            document_type TEXT,
            analyzed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_stock_symbol 
        ON document_analysis(stock_symbol)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sentiment 
        ON document_analysis(sentiment)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

# Initialize database on startup
init_database()

# Pydantic models
class PredictionRequest(BaseModel):
    symbol: str
    days: int = 7
    use_sentiment: bool = True

class DocumentAnalysisResponse(BaseModel):
    filename: str
    stock_symbol: str
    sentiment: str
    confidence: float
    summary: str
    analyzed_at: str

# ============= DOCUMENT INTEGRATION FUNCTIONS =============

def save_analysis_to_db(analysis: Dict, stock_symbol: str, document_type: str):
    """Save document analysis to database linked to stock symbol"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO document_analysis 
            (file_hash, filename, stock_symbol, sentiment, confidence,
             sentiment_positive, sentiment_negative, sentiment_neutral,
             summary, word_count, document_type, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis.get('file_hash'),
            analysis.get('filename'),
            stock_symbol.upper(),
            analysis['analysis'].get('sentiment', 'neutral'),
            analysis['analysis'].get('confidence', 0.0),
            analysis['analysis'].get('sentiment_scores', {}).get('positive', 0.33),
            analysis['analysis'].get('sentiment_scores', {}).get('negative', 0.33),
            analysis['analysis'].get('sentiment_scores', {}).get('neutral', 0.34),
            analysis['analysis'].get('summary', ''),
            analysis['analysis'].get('word_count', 0),
            document_type,
            analysis['analysis'].get('analyzed_at', datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved analysis for {stock_symbol}: {analysis['filename']}")
        return True
    except Exception as e:
        logger.error(f"Error saving analysis to DB: {e}")
        return False

def get_sentiment_for_stock(symbol: str, days: int = 30) -> Dict:
    """Get aggregated sentiment analysis for a stock"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get recent analyses
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT sentiment, confidence, sentiment_positive, 
                   sentiment_negative, sentiment_neutral, analyzed_at
            FROM document_analysis
            WHERE stock_symbol = ? AND analyzed_at > ?
            ORDER BY analyzed_at DESC
        ''', (symbol.upper(), cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {
                "symbol": symbol,
                "sentiment": "neutral",
                "confidence": 0.0,
                "document_count": 0,
                "latest_analysis": None
            }
        
        # Aggregate sentiments
        total_positive = sum(r[2] for r in results) / len(results)
        total_negative = sum(r[3] for r in results) / len(results)
        total_neutral = sum(r[4] for r in results) / len(results)
        avg_confidence = sum(r[1] for r in results) / len(results)
        
        # Determine overall sentiment
        sentiments = {"positive": total_positive, "negative": total_negative, "neutral": total_neutral}
        overall_sentiment = max(sentiments, key=sentiments.get)
        
        return {
            "symbol": symbol,
            "sentiment": overall_sentiment,
            "confidence": round(avg_confidence, 3),
            "sentiment_scores": {
                "positive": round(total_positive, 3),
                "negative": round(total_negative, 3),
                "neutral": round(total_neutral, 3)
            },
            "document_count": len(results),
            "latest_analysis": results[0][5] if results else None,
            "trend": "improving" if results[0][2] > results[-1][2] else "declining"
        }
    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        return {
            "symbol": symbol,
            "sentiment": "neutral",
            "confidence": 0.0,
            "document_count": 0,
            "error": str(e)
        }

def get_all_document_analyses(limit: int = 50) -> List[Dict]:
    """Get all recent document analyses"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, stock_symbol, sentiment, confidence, 
                   summary, analyzed_at, document_type
            FROM document_analysis
            ORDER BY analyzed_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        analyses = []
        for r in results:
            analyses.append({
                "filename": r[0],
                "stock_symbol": r[1],
                "sentiment": r[2],
                "confidence": r[3],
                "summary": r[4][:100] + "..." if len(r[4]) > 100 else r[4],
                "analyzed_at": r[5],
                "document_type": r[6]
            })
        
        return analyses
    except Exception as e:
        logger.error(f"Error getting document analyses: {e}")
        return []

def calculate_sentiment_weighted_prediction(symbol: str, base_prediction: float, days_ahead: int) -> float:
    """Adjust price prediction based on document sentiment"""
    sentiment_data = get_sentiment_for_stock(symbol, days=30)
    
    # Sentiment multipliers
    sentiment_impact = {
        "positive": 1.02,  # 2% boost for positive sentiment
        "negative": 0.98,  # 2% reduction for negative sentiment
        "neutral": 1.0     # No change for neutral
    }
    
    # Apply sentiment weight based on confidence
    base_multiplier = sentiment_impact.get(sentiment_data['sentiment'], 1.0)
    confidence = sentiment_data['confidence']
    
    # Weighted multiplier (higher confidence = stronger impact)
    weighted_multiplier = 1 + (base_multiplier - 1) * confidence
    
    # Apply decay over time (sentiment impact reduces for further predictions)
    time_decay = 0.95 ** days_ahead
    final_multiplier = 1 + (weighted_multiplier - 1) * time_decay
    
    return base_prediction * final_multiplier

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    return {
        "status": "active",
        "message": "Stock Tracker API Enhanced v5.1.0",
        "features": {
            "document_integration": True,
            "sentiment_analysis": FINBERT_AVAILABLE,
            "sentiment_weighted_predictions": True,
            "document_stock_linking": True
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "5.1.0",
        "finbert": FINBERT_AVAILABLE,
        "database": DB_PATH.exists()
    }

@app.get("/api/stock/{symbol}")
async def get_stock_with_sentiment(symbol: str):
    """Get stock data with sentiment analysis"""
    try:
        # Get basic stock data
        if symbol in stock_cache:
            stock_data = stock_cache[symbol]
        else:
            stock_data = get_stock_info(symbol)
            stock_cache[symbol] = stock_data
        
        # Add sentiment data
        sentiment_data = get_sentiment_for_stock(symbol)
        stock_data['sentiment_analysis'] = sentiment_data
        
        return stock_data
    except Exception as e:
        logger.error(f"Error getting stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/upload")
async def upload_document_enhanced(
    file: UploadFile = File(...),
    stock_symbol: str = Form(...),
    document_type: str = Form(default="financial_report")
):
    """Upload document linked to specific stock"""
    try:
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > 100:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Save file
        file_path = DIRS['uploads'] / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Analyze document
        analysis = analyze_document(str(file_path), file.filename, DIRS['analysis_cache'])
        
        # Save to database linked to stock
        saved = save_analysis_to_db(analysis, stock_symbol, document_type)
        
        # Add metadata
        analysis.update({
            "success": True,
            "stock_symbol": stock_symbol.upper(),
            "document_type": document_type,
            "size_mb": round(file_size_mb, 2),
            "saved_to_db": saved
        })
        
        logger.info(f"Document analyzed for {stock_symbol}: {file.filename}")
        return analysis
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/sentiment/{symbol}")
async def get_stock_sentiment(symbol: str, days: int = Query(30, description="Days to look back")):
    """Get sentiment analysis for a specific stock"""
    sentiment_data = get_sentiment_for_stock(symbol, days)
    return sentiment_data

@app.get("/api/documents/analyses")
async def get_all_analyses(limit: int = Query(50, description="Maximum results")):
    """Get all document analyses"""
    analyses = get_all_document_analyses(limit)
    return {
        "count": len(analyses),
        "analyses": analyses
    }

@app.get("/api/documents/by-stock/{symbol}")
async def get_documents_for_stock(symbol: str):
    """Get all documents analyzed for a specific stock"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, sentiment, confidence, summary, 
                   analyzed_at, document_type
            FROM document_analysis
            WHERE stock_symbol = ?
            ORDER BY analyzed_at DESC
        ''', (symbol.upper(),))
        
        results = cursor.fetchall()
        conn.close()
        
        documents = []
        for r in results:
            documents.append({
                "filename": r[0],
                "sentiment": r[1],
                "confidence": r[2],
                "summary": r[3],
                "analyzed_at": r[4],
                "document_type": r[5]
            })
        
        return {
            "symbol": symbol,
            "document_count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error getting documents for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def predict_with_sentiment(request: PredictionRequest):
    """Predict stock price with sentiment weighting"""
    try:
        ticker = yf.Ticker(request.symbol)
        hist = ticker.history(period="3mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {request.symbol}")
        
        prices = hist['Close'].values
        sma = np.mean(prices[-20:])
        trend = (prices[-1] - prices[-5]) / 5
        
        predictions = []
        last_price = float(prices[-1])
        
        for i in range(request.days):
            # Base prediction
            base_prediction = last_price + trend * 0.5 + (sma - last_price) * 0.1
            
            # Apply sentiment weighting if enabled
            if request.use_sentiment:
                weighted_prediction = calculate_sentiment_weighted_prediction(
                    request.symbol, base_prediction, i
                )
            else:
                weighted_prediction = base_prediction
            
            predictions.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                "predicted_price": round(weighted_prediction, 2),
                "base_price": round(base_prediction, 2),
                "sentiment_adjusted": request.use_sentiment
            })
            last_price = weighted_prediction
        
        # Get sentiment summary
        sentiment_data = get_sentiment_for_stock(request.symbol) if request.use_sentiment else None
        
        return {
            "symbol": request.symbol,
            "current_price": round(float(prices[-1]), 2),
            "predictions": predictions,
            "method": "SMA_Trend_Sentiment" if request.use_sentiment else "SMA_Trend",
            "sentiment_analysis": sentiment_data
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-sentiment")
async def get_market_sentiment():
    """Get overall market sentiment from all analyzed documents"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get sentiment distribution
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM document_analysis
            WHERE analyzed_at > datetime('now', '-30 days')
            GROUP BY sentiment
        ''')
        
        results = cursor.fetchall()
        
        # Get top positive and negative stocks
        cursor.execute('''
            SELECT stock_symbol, 
                   AVG(sentiment_positive - sentiment_negative) as net_sentiment,
                   COUNT(*) as doc_count
            FROM document_analysis
            WHERE analyzed_at > datetime('now', '-30 days')
            GROUP BY stock_symbol
            ORDER BY net_sentiment DESC
            LIMIT 5
        ''')
        
        top_positive = cursor.fetchall()
        
        cursor.execute('''
            SELECT stock_symbol, 
                   AVG(sentiment_positive - sentiment_negative) as net_sentiment,
                   COUNT(*) as doc_count
            FROM document_analysis
            WHERE analyzed_at > datetime('now', '-30 days')
            GROUP BY stock_symbol
            ORDER BY net_sentiment ASC
            LIMIT 5
        ''')
        
        top_negative = cursor.fetchall()
        
        conn.close()
        
        # Process results
        sentiment_dist = {}
        for r in results:
            sentiment_dist[r[0]] = {
                "count": r[1],
                "avg_confidence": round(r[2], 3) if r[2] else 0
            }
        
        return {
            "sentiment_distribution": sentiment_dist,
            "top_positive_stocks": [
                {"symbol": r[0], "net_sentiment": round(r[1], 3), "documents": r[2]}
                for r in top_positive
            ],
            "top_negative_stocks": [
                {"symbol": r[0], "net_sentiment": round(r[1], 3), "documents": r[2]}
                for r in top_negative
            ],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Keep all other endpoints from original backend...
# (historical, market-summary, indices, etc. remain the same)

if __name__ == "__main__":
    logger.info("Starting Enhanced Backend with Document Integration on port 8002")
    logger.info(f"FinBERT: {FINBERT_AVAILABLE}, Database: {DB_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=8002)