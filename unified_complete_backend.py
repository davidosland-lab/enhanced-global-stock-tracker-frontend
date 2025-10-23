#!/usr/bin/env python3
"""
Unified Complete Backend - Serves ALL existing modules
Integrates with existing enhanced backends while providing missing endpoints
Preserves all working functionality
Port: 8000
"""

import os
import sys
import logging
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Data processing
import pandas as pd
import numpy as np
import yfinance as yf

# HTTP client for forwarding requests
import httpx
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Unified Complete Backend", version="3.0")

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry for forwarding
BACKEND_SERVICES = {
    "ml": "http://localhost:8002",
    "finbert": "http://localhost:8003", 
    "historical": "http://localhost:8004",
    "backtesting": "http://localhost:8005",
    "scraper": "http://localhost:8006",
    "indices": "http://localhost:8007",
    "performance": "http://localhost:8010"
}

# HTML Module mappings
HTML_MODULES = {
    "/": "system_index.html",
    "/index": "system_index.html",
    "/prediction": "prediction_center_fixed.html",
    "/prediction_center": "prediction_center_fixed.html",
    "/global_markets": "global_market_tracker.html",
    "/indices": "indices_tracker_fixed_times.html",
    "/cba": "cba_enhanced.html",
    "/technical": "technical_analysis_enhanced.html",
    "/sentiment": "sentiment_scraper_universal.html",
    "/historical": "historical_data_analysis.html",
    "/document": "document_analyzer.html",
    "/performance": "performance_tracker.html",
    "/backtesting": "backtesting.html"
}

# Client for making requests
client = httpx.AsyncClient(timeout=60.0)

async def forward_to_service(service: str, endpoint: str, method: str = "GET", 
                            data: Optional[Dict] = None, params: Optional[Dict] = None):
    """Forward request to appropriate backend service"""
    if service not in BACKEND_SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")
    
    url = f"{BACKEND_SERVICES[service]}{endpoint}"
    
    try:
        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Service returned {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Error forwarding to {service}: {str(e)}")
        # Return mock data if service is down
        return {"error": f"Service unavailable: {str(e)}", "mock_data": True}

# Root endpoint
@app.get("/")
async def root():
    """Serve main index"""
    if os.path.exists("system_index.html"):
        return FileResponse("system_index.html")
    return {"message": "Unified Complete Backend", "version": "3.0"}

# Serve HTML modules
@app.get("/{module_name}.html")
async def serve_html(module_name: str):
    """Serve HTML files"""
    file_path = f"{module_name}.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail=f"Module {module_name} not found")

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API endpoints for ML service
@app.post("/train")
async def train(request: Request):
    """Forward training request to ML backend"""
    data = await request.json()
    return await forward_to_service("ml", "/train", "POST", data)

@app.post("/predict")
async def predict(request: Request):
    """Forward prediction request to ML backend"""
    data = await request.json()
    return await forward_to_service("ml", "/predict", "POST", data)

@app.get("/models/{symbol}")
async def get_models(symbol: str):
    """Get available models for a symbol"""
    return await forward_to_service("ml", f"/models/{symbol}", "GET")

# API endpoints for stock data (used by multiple modules)
@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get stock data - primary endpoint for many modules"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        # Get current info
        info = ticker.info
        
        # Format response
        return {
            "symbol": symbol,
            "data": {
                "dates": hist.index.strftime('%Y-%m-%d %H:%M').tolist(),
                "open": hist['Open'].tolist(),
                "high": hist['High'].tolist(), 
                "low": hist['Low'].tolist(),
                "close": hist['Close'].tolist(),
                "volume": hist['Volume'].tolist()
            },
            "info": {
                "currentPrice": info.get('currentPrice', hist['Close'].iloc[-1]),
                "previousClose": info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1]),
                "dayHigh": info.get('dayHigh', hist['High'].iloc[-1]),
                "dayLow": info.get('dayLow', hist['Low'].iloc[-1]),
                "volume": info.get('volume', hist['Volume'].iloc[-1]),
                "marketCap": info.get('marketCap', 0),
                "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', hist['High'].max()),
                "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', hist['Low'].min())
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/symbols")
async def get_symbols():
    """Get list of available symbols"""
    # Common symbols - extend as needed
    symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM", 
        "V", "JNJ", "WMT", "PG", "UNH", "DIS", "MA", "HD", "BAC", "PFE",
        "CBA.AX", "BHP.AX", "CSL.AX", "WBC.AX", "ANZ.AX", "NAB.AX", "WES.AX",
        "^GSPC", "^DJI", "^IXIC", "^FTSE", "^GDAXI", "^N225", "^HSI", "^AORD"
    ]
    return {"symbols": symbols}

# Historical data endpoints
@app.get("/api/historical/{symbol}")
async def get_historical(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Forward to historical backend or fetch directly"""
    result = await forward_to_service("historical", f"/api/historical/{symbol}", "GET", 
                                     params={"period": period, "interval": interval})
    if "error" in result:
        # Fallback to direct fetch
        return await get_stock_data(symbol, period, interval)
    return result

# Sentiment endpoints
@app.get("/api/sentiment/scrape")
async def get_sentiment():
    """Get global sentiment"""
    return await forward_to_service("scraper", "/api/scrape", "GET")

@app.get("/api/sources")
async def get_sources():
    """Get sentiment sources"""
    return await forward_to_service("scraper", "/api/sources", "GET")

@app.get("/api/market_risk")
async def get_market_risk():
    """Get market risk assessment"""
    return await forward_to_service("scraper", "/api/market_risk", "GET")

# Indices endpoints
@app.get("/api/indices")
async def get_indices():
    """Get all indices - forward or provide fallback"""
    result = await forward_to_service("indices", "/api/indices", "GET")
    if "error" in result:
        # Provide fallback data
        indices = ["^GSPC", "^DJI", "^IXIC", "^FTSE", "^AORD"]
        data = {}
        for idx in indices:
            try:
                ticker = yf.Ticker(idx)
                hist = ticker.history(period="1d", interval="5m")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    open_price = hist['Open'].iloc[0]
                    change = current - open_price
                    change_pct = (change / open_price) * 100 if open_price != 0 else 0
                    
                    data[idx] = {
                        "symbol": idx,
                        "current": round(current, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_pct, 2),
                        "volume": int(hist['Volume'].sum())
                    }
            except:
                continue
        return {"data": data, "timestamp": datetime.now().isoformat()}
    return result

@app.get("/api/sectors")
async def get_sectors():
    """Get sector performance"""
    return await forward_to_service("indices", "/api/sectors", "GET")

# Performance tracking endpoints
@app.post("/api/record_prediction")
async def record_prediction(request: Request):
    """Record a prediction"""
    data = await request.json()
    return await forward_to_service("performance", "/api/record_prediction", "POST", data)

@app.get("/api/performance/accuracy")
async def get_accuracy(symbol: Optional[str] = None, days: int = 30):
    """Get prediction accuracy"""
    return await forward_to_service("performance", "/api/prediction_accuracy", "GET",
                                   params={"symbol": symbol, "days": days})

@app.get("/api/performance/summary") 
async def get_performance_summary(days: int = 30):
    """Get performance summary"""
    return await forward_to_service("performance", "/api/performance_summary", "GET",
                                   params={"days": days})

# Backtesting endpoints
@app.post("/api/backtest")
async def run_backtest(request: Request):
    """Run backtesting"""
    data = await request.json()
    return await forward_to_service("backtesting", "/api/backtest", "POST", data)

# Document analysis endpoints
@app.post("/api/analyze_document")
async def analyze_document(request: Request):
    """Analyze document with FinBERT"""
    data = await request.json()
    return await forward_to_service("finbert", "/api/analyze_document", "POST", data)

# CBA specific endpoints (for CBA enhanced module)
@app.get("/api/cba/analysis")
async def get_cba_analysis():
    """Get CBA specific analysis"""
    try:
        # Fetch CBA.AX data
        ticker = yf.Ticker("CBA.AX")
        hist = ticker.history(period="1mo", interval="1d")
        info = ticker.info
        
        # Get related bank stocks
        banks = ["WBC.AX", "ANZ.AX", "NAB.AX"]
        comparisons = {}
        
        for bank in banks:
            try:
                bank_ticker = yf.Ticker(bank)
                bank_hist = bank_ticker.history(period="1mo", interval="1d")
                if not bank_hist.empty:
                    comparisons[bank] = {
                        "current": round(bank_hist['Close'].iloc[-1], 2),
                        "change_pct": round(((bank_hist['Close'].iloc[-1] / bank_hist['Close'].iloc[0]) - 1) * 100, 2)
                    }
            except:
                continue
        
        return {
            "cba": {
                "symbol": "CBA.AX",
                "current": round(hist['Close'].iloc[-1], 2) if not hist.empty else 0,
                "change": round(hist['Close'].iloc[-1] - hist['Close'].iloc[0], 2) if not hist.empty else 0,
                "volume": int(hist['Volume'].sum()) if not hist.empty else 0,
                "marketCap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "dividend_yield": info.get('dividendYield', 0)
            },
            "comparisons": comparisons,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting CBA analysis: {str(e)}")
        return {"error": str(e)}

# ASX specific endpoints
@app.get("/api/asx/top_movers")
async def get_asx_movers():
    """Get ASX top movers"""
    asx_stocks = ["CBA.AX", "BHP.AX", "CSL.AX", "WBC.AX", "ANZ.AX", "NAB.AX", 
                  "WES.AX", "WOW.AX", "TLS.AX", "RIO.AX"]
    
    movers = []
    for symbol in asx_stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1d")
            if not hist.empty:
                change_pct = ((hist['Close'].iloc[-1] / hist['Open'].iloc[-1]) - 1) * 100
                movers.append({
                    "symbol": symbol,
                    "price": round(hist['Close'].iloc[-1], 2),
                    "change_percent": round(change_pct, 2)
                })
        except:
            continue
    
    # Sort by absolute change
    movers.sort(key=lambda x: abs(x['change_percent']), reverse=True)
    
    return {
        "top_gainers": [m for m in movers if m['change_percent'] > 0][:5],
        "top_losers": [m for m in movers if m['change_percent'] < 0][:5]
    }

# Technical analysis endpoints
@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str, period: str = "3mo"):
    """Get technical indicators"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        # Calculate technical indicators
        close_prices = hist['Close']
        
        # Moving averages
        ma_20 = close_prices.rolling(window=20).mean()
        ma_50 = close_prices.rolling(window=50).mean()
        ma_200 = close_prices.rolling(window=200).mean()
        
        # RSI
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = close_prices.ewm(span=12).mean()
        ema_26 = close_prices.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        
        # Bollinger Bands
        sma_20 = close_prices.rolling(window=20).mean()
        std_20 = close_prices.rolling(window=20).std()
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        
        return {
            "symbol": symbol,
            "indicators": {
                "ma_20": ma_20.iloc[-1] if not pd.isna(ma_20.iloc[-1]) else None,
                "ma_50": ma_50.iloc[-1] if not pd.isna(ma_50.iloc[-1]) else None,
                "ma_200": ma_200.iloc[-1] if not pd.isna(ma_200.iloc[-1]) else None,
                "rsi": rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None,
                "macd": macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else None,
                "signal": signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else None,
                "upper_band": upper_band.iloc[-1] if not pd.isna(upper_band.iloc[-1]) else None,
                "lower_band": lower_band.iloc[-1] if not pd.isna(lower_band.iloc[-1]) else None
            },
            "signals": {
                "rsi_signal": "Oversold" if rsi.iloc[-1] < 30 else "Overbought" if rsi.iloc[-1] > 70 else "Neutral",
                "macd_signal": "Bullish" if macd.iloc[-1] > signal.iloc[-1] else "Bearish",
                "ma_signal": "Bullish" if close_prices.iloc[-1] > ma_50.iloc[-1] else "Bearish"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve all routes
@app.get("/api/health/all")
async def check_all_services():
    """Check health of all backend services"""
    health_status = {}
    for service, url in BACKEND_SERVICES.items():
        try:
            response = await client.get(f"{url}/health", timeout=2)
            health_status[service] = "online" if response.status_code == 200 else "error"
        except:
            health_status[service] = "offline"
    
    return {
        "services": health_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = 8000
    logger.info(f"Starting Unified Complete Backend on port {port}...")
    logger.info("This backend integrates all modules and services")
    logger.info("Access the system at http://localhost:8000/")
    
    uvicorn.run(app, host="0.0.0.0", port=port)