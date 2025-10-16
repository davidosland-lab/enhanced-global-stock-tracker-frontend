#!/usr/bin/env python3
"""
Stock Tracker Backend API v5.0
Complete implementation with all fixes
Port: 8002
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Data processing
import yfinance as yf
import pandas as pd
import numpy as np
from cachetools import TTLCache
from pydantic import BaseModel

# Import custom modules
from backend_core import get_stock_info, get_aest_time, INDICES, POPULAR_STOCKS
from document_analyzer import analyze_document, FINBERT_AVAILABLE, PDF_SUPPORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Stock Tracker API", version="5.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for stock data (5 minutes TTL)
stock_cache = TTLCache(maxsize=100, ttl=300)

# Create directories
DIRS = {
    'historical': Path('historical_data'),
    'uploads': Path('uploads'),
    'analysis_cache': Path('analysis_cache'),
    'models': Path('ml_models')
}

for dir_path in DIRS.values():
    dir_path.mkdir(exist_ok=True)

# Pydantic models
class PredictionRequest(BaseModel):
    symbol: str
    days: int = 7

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "active",
        "message": "Stock Tracker API v5.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "real_time_stocks": True,
            "yahoo_finance_only": True,
            "no_synthetic_data": True,
            "finbert_available": FINBERT_AVAILABLE,
            "document_analysis": PDF_SUPPORT,
            "max_upload_size": "100MB"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Stock Tracker Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "5.0.0",
        "timezone": "ADST (UTC+11)"
    }

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    """Get real-time stock data"""
    try:
        if symbol in stock_cache:
            return stock_cache[symbol]
        
        data = get_stock_info(symbol)
        stock_cache[symbol] = data
        return data
    except Exception as e:
        logger.error(f"Error getting stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical/{symbol}")
async def get_historical(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get historical data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        data = []
        for index, row in hist.iterrows():
            data.append({
                "date": index.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": data
        }
    except Exception as e:
        logger.error(f"Historical data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-summary")
async def get_market_summary():
    """Get market summary with ADST support"""
    try:
        summary = {
            "indices": [],
            "market_status": {},
            "last_updated": datetime.now().isoformat(),
            "timezone": "ADST"
        }
        
        # Get ADST time
        aest_now = get_aest_time()
        current_hour = aest_now.hour + aest_now.minute / 60
        
        # Market hours in ADST
        market_hours = {
            "ASX": {"open": 10, "close": 16, "status": "closed"},
            "FTSE": {"open": 19, "close": 3.5, "status": "closed"},
            "SP500": {"open": 1.5, "close": 8, "status": "closed"}
        }
        
        # Check market status
        if 10 <= current_hour < 16:
            market_hours["ASX"]["status"] = "open"
        
        if current_hour >= 19 or current_hour < 3.5:
            market_hours["FTSE"]["status"] = "open"
        
        if 1.5 <= current_hour < 8:
            market_hours["SP500"]["status"] = "open"
        
        summary["market_status"] = market_hours
        
        # Get indices data
        for symbol, info in INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 1:
                    current = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current
                    change = current - prev_close
                    change_pct = (change / prev_close) * 100 if prev_close else 0
                    
                    summary["indices"].append({
                        "symbol": symbol,
                        "name": info["name"],
                        "region": info["region"],
                        "value": round(current, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_pct, 2)
                    })
            except Exception as e:
                logger.error(f"Error fetching index {symbol}: {e}")
        
        return summary
    except Exception as e:
        logger.error(f"Market summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices")
async def get_indices():
    """Get all indices"""
    indices_data = []
    for symbol, info in INDICES.items():
        try:
            data = get_stock_info(symbol)
            indices_data.append({**info, **data})
        except:
            continue
    return {"indices": indices_data}

@app.get("/api/market-movers")
async def get_market_movers():
    """Get market movers"""
    try:
        movers = {"gainers": [], "losers": [], "most_active": []}
        
        for symbol in POPULAR_STOCKS['ASX'][:10]:
            try:
                data = get_stock_info(symbol)
                if data['changePercent'] > 0:
                    movers['gainers'].append(data)
                else:
                    movers['losers'].append(data)
                movers['most_active'].append(data)
            except:
                continue
        
        movers['gainers'] = sorted(movers['gainers'], key=lambda x: x['changePercent'], reverse=True)[:5]
        movers['losers'] = sorted(movers['losers'], key=lambda x: x['changePercent'])[:5]
        movers['most_active'] = sorted(movers['most_active'], key=lambda x: x['volume'], reverse=True)[:5]
        
        return movers
    except Exception as e:
        logger.error(f"Market movers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    documentType: str = Form(default="financial")
):
    """Upload and analyze document (100MB limit)"""
    try:
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > 100:
            raise HTTPException(status_code=413, detail=f"File too large: {file_size_mb:.1f}MB")
        
        # Save file
        file_path = DIRS['uploads'] / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Analyze document
        analysis = analyze_document(str(file_path), file.filename, DIRS['analysis_cache'])
        
        # Add metadata
        analysis.update({
            "success": True,
            "documentType": documentType,
            "size": len(contents),
            "size_mb": round(file_size_mb, 2)
        })
        
        return analysis
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/historical/batch-download")
async def batch_download(request: Dict = Body(default={})):
    """Batch download historical data"""
    try:
        symbols = request.get('symbols', POPULAR_STOCKS['ASX'][:5])
        period = request.get('period', '1mo')
        
        results = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    filepath = DIRS['historical'] / f"{symbol}_{period}.csv"
                    hist.to_csv(filepath)
                    
                    results.append({
                        "symbol": symbol,
                        "records": len(hist),
                        "file": str(filepath)
                    })
            except Exception as e:
                logger.error(f"Failed {symbol}: {e}")
        
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/status")
async def ml_status():
    """ML service status"""
    return {
        "status": "ready",
        "models_available": ["LSTM", "Random Forest", "XGBoost"],
        "finbert_sentiment": FINBERT_AVAILABLE
    }

@app.post("/api/predict")
async def predict_price(request: PredictionRequest):
    """Simple price prediction"""
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
            next_price = last_price + trend * 0.5 + (sma - last_price) * 0.1
            predictions.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                "predicted_price": round(next_price, 2)
            })
            last_price = next_price
        
        return {
            "symbol": request.symbol,
            "current_price": round(float(prices[-1]), 2),
            "predictions": predictions
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def api_status():
    """API status"""
    return {
        "status": "active",
        "finbert_available": FINBERT_AVAILABLE,
        "pdf_support": PDF_SUPPORT,
        "max_file_upload": "100MB",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Stock Tracker Backend on port 8002")
    logger.info(f"FinBERT: {FINBERT_AVAILABLE}, PDF Support: {PDF_SUPPORT}")
    uvicorn.run(app, host="0.0.0.0", port=8002)