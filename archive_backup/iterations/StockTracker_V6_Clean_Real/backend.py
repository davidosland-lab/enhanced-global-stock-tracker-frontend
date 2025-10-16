"""
Main Backend API - Real Implementation
Handles stock data, historical data, and coordinates with ML backend
"""

import os
import json
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Stock Tracker Main API", version="6.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Stock Tracker Main API",
        "version": "6.0",
        "status": "operational",
        "endpoints": {
            "stock": "/api/stock/{symbol}",
            "historical": "/api/historical/{symbol}",
            "news": "/api/news/{symbol}",
            "status": "/api/status"
        }
    }

@app.get("/api/status")
async def get_status():
    """Get API status"""
    return {
        "status": "online",
        "backend": "connected",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "yahoo_finance": "active",
            "prediction": "active",
            "historical_data": "active",
            "technical_analysis": "active"
        }
    }

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get real-time stock data"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        return {
            "symbol": symbol.upper(),
            "price": current_price,
            "name": info.get('longName', symbol),
            "change": info.get('regularMarketChange', 0),
            "changePercent": info.get('regularMarketChangePercent', 0),
            "volume": info.get('volume', 0),
            "marketCap": info.get('marketCap', 0),
            "dayHigh": info.get('dayHigh', 0),
            "dayLow": info.get('dayLow', 0),
            "open": info.get('open', 0),
            "previousClose": info.get('previousClose', 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical/{symbol}")
async def get_historical_data(
    symbol: str, 
    period: str = "1mo", 
    interval: str = "1d"
):
    """Get historical stock data"""
    try:
        ticker = yf.Ticker(symbol.upper())
        
        # Fetch historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        # Convert to list of dictionaries
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data,
            "count": len(data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/{symbol}")
async def get_stock_news(symbol: str):
    """Get stock news"""
    try:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news[:10] if hasattr(ticker, 'news') else []
        
        return {
            "symbol": symbol.upper(),
            "news": news,
            "count": len(news)
        }
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {str(e)}")
        return {"symbol": symbol.upper(), "news": [], "count": 0}

@app.get("/api/technical/{symbol}")
async def get_technical_indicators(symbol: str):
    """Calculate technical indicators"""
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period="3mo", interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data for technical analysis")
        
        close_prices = hist['Close'].values
        
        # Calculate simple indicators
        sma_20 = pd.Series(close_prices).rolling(window=20).mean().iloc[-1]
        sma_50 = pd.Series(close_prices).rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else None
        
        # RSI calculation
        def calculate_rsi(prices, period=14):
            deltas = np.diff(prices)
            seed = deltas[:period+1]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down if down != 0 else 100
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        rsi = calculate_rsi(close_prices) if len(close_prices) > 14 else 50
        
        # Current price
        current_price = close_prices[-1]
        
        # Determine signals
        signal = "NEUTRAL"
        if sma_20 and current_price > sma_20 * 1.02:
            signal = "BUY"
        elif sma_20 and current_price < sma_20 * 0.98:
            signal = "SELL"
        
        return {
            "symbol": symbol.upper(),
            "current_price": float(current_price),
            "sma_20": float(sma_20) if sma_20 else None,
            "sma_50": float(sma_50) if sma_50 else None,
            "rsi": float(rsi),
            "signal": signal,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Main Backend API on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)