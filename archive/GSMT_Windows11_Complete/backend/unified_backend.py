#!/usr/bin/env python3
"""
GSMT Unified Backend Server
Handles all data requests for GSMT modules
"""

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="GSMT Unified Backend", version="8.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for data
cache = {}
CACHE_DURATION = 120  # 2 minutes

def get_cached_data(key):
    """Get cached data if valid"""
    if key in cache:
        data, timestamp = cache[key]
        if (datetime.now() - timestamp).seconds < CACHE_DURATION:
            return data
    return None

def set_cache_data(key, data):
    """Store data in cache"""
    cache[key] = (data, datetime.now())

# Market indices configuration
MARKET_INDICES = {
    "^AXJO": {"name": "ASX 200", "region": "Asia"},
    "^N225": {"name": "Nikkei 225", "region": "Asia"},
    "^HSI": {"name": "Hang Seng", "region": "Asia"},
    "^FTSE": {"name": "FTSE 100", "region": "Europe"},
    "^GDAXI": {"name": "DAX", "region": "Europe"},
    "^FCHI": {"name": "CAC 40", "region": "Europe"},
    "^GSPC": {"name": "S&P 500", "region": "Americas"},
    "^DJI": {"name": "Dow Jones", "region": "Americas"},
    "^IXIC": {"name": "NASDAQ", "region": "Americas"},
}

@app.get("/")
async def root():
    return {
        "service": "GSMT Unified Backend",
        "version": "8.0",
        "status": "operational",
        "endpoints": [
            "/api/indices",
            "/api/indices/{symbol}/intraday",
            "/api/stock/{symbol}",
            "/api/cba/data",
            "/api/technical/{symbol}"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/indices")
async def get_all_indices():
    """Get all market indices data"""
    logger.info("Fetching all indices data")
    
    cached = get_cached_data('all_indices')
    if cached:
        return cached
    
    indices_data = {}
    errors = []
    
    for symbol, info in MARKET_INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="5m")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                open_price = float(hist['Open'].iloc[0])
                high = float(hist['High'].max())
                low = float(hist['Low'].min())
                volume = int(hist['Volume'].sum())
                
                prev_hist = ticker.history(period="2d", interval="1d")
                if len(prev_hist) >= 2:
                    previous_close = float(prev_hist['Close'].iloc[-2])
                else:
                    previous_close = open_price
                
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": current_price,
                    "previousClose": previous_close,
                    "open": open_price,
                    "change": change,
                    "changePercent": change_percent,
                    "dayHigh": high,
                    "dayLow": low,
                    "volume": volume,
                    "lastUpdate": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            errors.append(f"Error fetching {symbol}")
    
    response = {
        "indices": indices_data,
        "errors": errors if errors else None,
        "timestamp": datetime.now().isoformat()
    }
    
    set_cache_data('all_indices', response)
    return response

@app.get("/api/indices/{symbol}/intraday")
async def get_index_intraday(symbol: str):
    """Get intraday data for specific index with 5-minute intervals"""
    logger.info(f"Fetching intraday data for {symbol}")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get 5-minute interval data for today
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            # Try to get hourly data as fallback
            hist = ticker.history(period="5d", interval="1h")
            if hist.empty:
                raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Get previous close
        prev_hist = ticker.history(period="2d", interval="1d")
        if len(prev_hist) >= 2:
            previous_close = float(prev_hist['Close'].iloc[-2])
        else:
            previous_close = float(hist['Open'].iloc[0])
        
        # Format data points
        data_points = []
        for idx, row in hist.iterrows():
            time_str = idx.strftime("%H:%M")
            price = float(row['Close'])
            change_percent = ((price - previous_close) / previous_close * 100) if previous_close != 0 else 0
            
            data_points.append({
                "time": time_str,
                "price": price,
                "changePercent": change_percent,
                "volume": int(row['Volume']),
                "high": float(row['High']),
                "low": float(row['Low'])
            })
        
        return {
            "symbol": symbol,
            "name": MARKET_INDICES.get(symbol, {}).get("name", symbol),
            "previousClose": previous_close,
            "dataPoints": data_points,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get stock data for single stock tracker"""
    logger.info(f"Fetching stock data for {symbol}")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get stock info
        info = ticker.info
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Format history
        history_data = []
        for idx, row in hist.iterrows():
            history_data.append({
                "date": idx.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol.upper(),
            "info": {
                "longName": info.get('longName', symbol),
                "currentPrice": info.get('currentPrice', float(hist['Close'].iloc[-1])),
                "previousClose": info.get('previousClose', float(hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[0])),
                "marketCap": info.get('marketCap', 0),
                "volume": info.get('volume', int(hist['Volume'].iloc[-1])),
                "dayHigh": info.get('dayHigh', float(hist['High'].iloc[-1])),
                "dayLow": info.get('dayLow', float(hist['Low'].iloc[-1]))
            },
            "history": history_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching stock {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data for {symbol}: {str(e)}")

@app.get("/api/cba/data")
async def get_cba_data():
    """Get Commonwealth Bank of Australia data"""
    logger.info("Fetching CBA data")
    
    try:
        ticker = yf.Ticker("CBA.AX")
        
        # Get current data
        info = ticker.info
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            hist = ticker.history(period="5d", interval="1h")
        
        current_price = float(hist['Close'].iloc[-1]) if not hist.empty else info.get('currentPrice', 0)
        
        # Get previous close
        prev_hist = ticker.history(period="2d", interval="1d")
        if len(prev_hist) >= 2:
            previous_close = float(prev_hist['Close'].iloc[-2])
        else:
            previous_close = info.get('previousClose', current_price)
        
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
        
        # Get historical data for chart
        hist_30d = ticker.history(period="1mo", interval="1d")
        historical_data = []
        for idx, row in hist_30d.iterrows():
            historical_data.append({
                "date": idx.isoformat(),
                "price": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "currentPrice": current_price,
            "previousClose": previous_close,
            "change": change,
            "changePercent": change_percent,
            "marketCap": info.get('marketCap', 0),
            "volume": info.get('volume', 0),
            "peRatio": info.get('trailingPE', 0),
            "dividendYield": info.get('dividendYield', 0),
            "historical": historical_data,
            "lastUpdate": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching CBA data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/technical/{symbol}")
async def get_technical_data(symbol: str):
    """Get technical analysis data"""
    logger.info(f"Fetching technical data for {symbol}")
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo", interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate technical indicators
        closes = hist['Close'].values
        highs = hist['High'].values
        lows = hist['Low'].values
        volumes = hist['Volume'].values
        
        # RSI
        def calculate_rsi(prices, period=14):
            deltas = np.diff(prices)
            gains = deltas.copy()
            gains[gains < 0] = 0
            losses = -deltas.copy()
            losses[losses < 0] = 0
            
            avg_gain = np.mean(gains[-period:]) if len(gains) >= period else 0
            avg_loss = np.mean(losses[-period:]) if len(losses) >= period else 0
            
            if avg_loss == 0:
                return 100
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        # Moving averages
        sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
        sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else closes[-1]
        
        # MACD
        ema_12 = pd.Series(closes).ewm(span=12).mean().iloc[-1]
        ema_26 = pd.Series(closes).ewm(span=26).mean().iloc[-1]
        macd = ema_12 - ema_26
        
        # Bollinger Bands
        sma = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
        std = np.std(closes[-20:]) if len(closes) >= 20 else 0
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        # Format candle data
        candle_data = []
        for idx, row in hist.iterrows():
            candle_data.append({
                "time": idx.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "indicators": {
                "rsi": calculate_rsi(closes),
                "sma20": sma_20,
                "sma50": sma_50,
                "macd": macd,
                "upperBand": upper_band,
                "lowerBand": lower_band,
                "volume": int(volumes[-1])
            },
            "candleData": candle_data,
            "lastUpdate": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting GSMT Unified Backend on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)