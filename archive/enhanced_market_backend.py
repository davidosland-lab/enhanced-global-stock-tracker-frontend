#!/usr/bin/env python3
"""
Enhanced Market Data Backend with Proper AEST Time Handling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import pytz
from cachetools import TTLCache
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Market Data API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Market indices configuration - INCLUDING ALL ORDINARIES
MARKET_INDICES = {
    # Asia Pacific
    "^AXJO": {"name": "ASX 200", "region": "Asia"},
    "^AORD": {"name": "All Ordinaries", "region": "Asia"},  # Added All Ordinaries
    "^N225": {"name": "Nikkei 225", "region": "Asia"},
    "^HSI": {"name": "Hang Seng", "region": "Asia"},
    "000001.SS": {"name": "Shanghai", "region": "Asia"},
    "^KS11": {"name": "KOSPI", "region": "Asia"},
    "^STI": {"name": "STI", "region": "Asia"},
    
    # Europe
    "^FTSE": {"name": "FTSE 100", "region": "Europe"},
    "^GDAXI": {"name": "DAX", "region": "Europe"},
    "^FCHI": {"name": "CAC 40", "region": "Europe"},
    "^STOXX50E": {"name": "Euro Stoxx 50", "region": "Europe"},
    "^IBEX": {"name": "IBEX 35", "region": "Europe"},
    "^AEX": {"name": "AEX", "region": "Europe"},
    
    # Americas
    "^DJI": {"name": "Dow Jones", "region": "Americas"},
    "^GSPC": {"name": "S&P 500", "region": "Americas"},
    "^IXIC": {"name": "NASDAQ", "region": "Americas"},
    "^RUT": {"name": "Russell 2000", "region": "Americas"},
    "^GSPTSE": {"name": "TSX", "region": "Americas"},
    "^BVSP": {"name": "Bovespa", "region": "Americas"}
}

# Cache for market data (2 minute TTL)
cache = TTLCache(maxsize=100, ttl=120)

# AEST timezone
AEST_TZ = pytz.timezone('Australia/Sydney')

def get_sydney_time():
    """Get current Sydney time"""
    return datetime.now(AEST_TZ)

def is_market_open(symbol: str) -> bool:
    """Check if market is currently open"""
    sydney_time = get_sydney_time()
    hour = sydney_time.hour
    minute = sydney_time.minute
    weekday = sydney_time.weekday()
    
    # Skip weekends
    if weekday >= 5:
        return False
    
    current_minutes = hour * 60 + minute
    
    # Market hours in Sydney time (AEST/AEDT)
    market_hours = {
        # Australian markets
        "^AXJO": (600, 960),     # 10:00 - 16:00
        "^AORD": (600, 960),     # 10:00 - 16:00
        
        # Asian markets
        "^N225": (600, 900),     # 10:00 - 15:00
        "^HSI": (690, 1020),     # 11:30 - 17:00
        "000001.SS": (690, 960), # 11:30 - 16:00
        "^KS11": (540, 930),     # 09:00 - 15:30
        "^STI": (600, 1080),     # 10:00 - 18:00
        
        # European markets (evening in AEST)
        "^FTSE": (1080, 150),    # 18:00 - 02:30 (next day)
        "^GDAXI": (1080, 150),   # 18:00 - 02:30
        "^FCHI": (1080, 150),    # 18:00 - 02:30
        "^STOXX50E": (1080, 150),# 18:00 - 02:30
        "^IBEX": (1080, 150),    # 18:00 - 02:30
        "^AEX": (1080, 150),     # 18:00 - 02:30
        
        # US markets (overnight in AEST)
        "^DJI": (30, 420),       # 00:30 - 07:00
        "^GSPC": (30, 420),      # 00:30 - 07:00
        "^IXIC": (30, 420),      # 00:30 - 07:00
        "^RUT": (30, 420),       # 00:30 - 07:00
        "^GSPTSE": (30, 420),    # 00:30 - 07:00
        "^BVSP": (1320, 240)     # 22:00 - 04:00 (next day)
    }
    
    if symbol in market_hours:
        open_time, close_time = market_hours[symbol]
        if close_time < open_time:  # Market spans midnight
            return current_minutes >= open_time or current_minutes < close_time
        else:
            return open_time <= current_minutes < close_time
    
    return False

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enhanced Market Data API",
        "status": "active",
        "endpoints": {
            "/api/indices": "Get all indices with real-time data",
            "/api/indices/{symbol}": "Get specific index data",
            "/api/indices/{symbol}/history": "Get historical data with AEST timestamps",
            "/api/market-status": "Get market trading status"
        },
        "data_source": "Yahoo Finance - REAL DATA ONLY",
        "timezone": "AEST/AEDT"
    }

@app.get("/api/indices")
async def get_all_indices():
    """Get real-time data for all indices"""
    try:
        # Check cache
        cache_key = "all_indices"
        if cache_key in cache:
            logger.info("Returning cached indices data")
            return cache[cache_key]
        
        indices_data = {}
        errors = []
        
        for symbol, info in MARKET_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                ticker_info = ticker.info
                
                # Get the most recent price data
                hist = ticker.history(period="1d", interval="1m")
                
                if hist.empty:
                    # Fallback to info if no recent history
                    current_price = ticker_info.get('regularMarketPrice', 0)
                    previous_close = ticker_info.get('regularMarketPreviousClose', 0)
                else:
                    # Use the most recent data point
                    current_price = float(hist['Close'].iloc[-1])
                    previous_close = float(hist['Close'].iloc[0])
                
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": current_price,
                    "previousClose": previous_close,
                    "open": ticker_info.get('regularMarketOpen', 0),
                    "change": change,
                    "changePercent": change_percent,
                    "dayHigh": ticker_info.get('dayHigh', 0),
                    "dayLow": ticker_info.get('dayLow', 0),
                    "volume": ticker_info.get('regularMarketVolume', 0),
                    "isOpen": is_market_open(symbol),
                    "lastUpdate": datetime.now().isoformat(),
                    "dataSource": "Yahoo Finance"
                }
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {str(e)}")
                errors.append({"symbol": symbol, "error": str(e)})
                # Return placeholder data on error
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": 0,
                    "previousClose": 0,
                    "open": 0,
                    "change": 0,
                    "changePercent": 0,
                    "dayHigh": 0,
                    "dayLow": 0,
                    "volume": 0,
                    "isOpen": is_market_open(symbol),
                    "lastUpdate": datetime.now().isoformat(),
                    "dataSource": "Error",
                    "error": str(e)
                }
        
        result = {
            "indices": indices_data,
            "timestamp": datetime.now().isoformat(),
            "errors": errors if errors else None,
            "total": len(indices_data)
        }
        
        # Cache the result
        cache[cache_key] = result
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_all_indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices/{symbol}/history")
async def get_index_history(
    symbol: str,
    period: str = Query(default="1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y")
):
    """Get historical data for an index with proper AEST timestamps"""
    try:
        if symbol not in MARKET_INDICES:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        # Cache key includes period
        cache_key = f"history_{symbol}_{period}"
        if cache_key in cache:
            logger.info(f"Returning cached history for {symbol}")
            return cache[cache_key]
        
        ticker = yf.Ticker(symbol)
        
        # Map period to interval
        interval_map = {
            "1d": "5m",
            "5d": "30m",
            "1mo": "1d",
            "3mo": "1d",
            "6mo": "1d",
            "1y": "1wk"
        }
        
        interval = interval_map.get(period, "1d")
        
        # Fetch historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Convert to AEST and prepare data
        history_data = []
        for idx, row in hist.iterrows():
            # Convert timestamp to AEST
            # Handle both timezone-aware and naive timestamps
            if hasattr(idx, 'tz') and idx.tz is not None:
                timestamp = idx.tz_convert(AEST_TZ)
            else:
                timestamp = pd.Timestamp(idx).tz_localize('UTC').tz_convert(AEST_TZ)
            
            history_data.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                "changePercent": float((row['Close'] - row['Open']) / row['Open'] * 100) if row['Open'] > 0 else 0
            })
        
        result = {
            "symbol": symbol,
            "name": MARKET_INDICES[symbol]["name"],
            "region": MARKET_INDICES[symbol]["region"],
            "period": period,
            "interval": interval,
            "history": history_data,
            "dataPoints": len(history_data),
            "timezone": "AEST",
            "lastUpdate": datetime.now(AEST_TZ).isoformat()
        }
        
        # Cache the result
        cache[cache_key] = result
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices/{symbol}")
async def get_index_data(symbol: str):
    """Get real-time data for a specific index"""
    try:
        if symbol not in MARKET_INDICES:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        ticker = yf.Ticker(symbol)
        ticker_info = ticker.info
        
        # Get recent price data
        hist = ticker.history(period="1d", interval="1m")
        
        if hist.empty:
            current_price = ticker_info.get('regularMarketPrice', 0)
            previous_close = ticker_info.get('regularMarketPreviousClose', 0)
        else:
            current_price = float(hist['Close'].iloc[-1])
            previous_close = float(hist['Close'].iloc[0])
        
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        return {
            "symbol": symbol,
            "name": MARKET_INDICES[symbol]["name"],
            "region": MARKET_INDICES[symbol]["region"],
            "price": current_price,
            "previousClose": previous_close,
            "open": ticker_info.get('regularMarketOpen', 0),
            "change": change,
            "changePercent": change_percent,
            "dayHigh": ticker_info.get('dayHigh', 0),
            "dayLow": ticker_info.get('dayLow', 0),
            "volume": ticker_info.get('regularMarketVolume', 0),
            "isOpen": is_market_open(symbol),
            "lastUpdate": datetime.now().isoformat(),
            "timezone": "AEST"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-status")
async def get_market_status():
    """Get current market trading status"""
    sydney_time = get_sydney_time()
    
    status = {}
    for symbol, info in MARKET_INDICES.items():
        status[symbol] = {
            "name": info["name"],
            "region": info["region"],
            "isOpen": is_market_open(symbol)
        }
    
    return {
        "currentTime": sydney_time.isoformat(),
        "timezone": "Australia/Sydney",
        "markets": status
    }

if __name__ == "__main__":
    print("Starting Enhanced Market Data Server on port 8000...")
    print("Access the API at: http://localhost:8000")
    print("All Ordinaries (^AORD) is included in the indices")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")