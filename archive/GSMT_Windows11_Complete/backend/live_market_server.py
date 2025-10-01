#!/usr/bin/env python3
"""
GSMT Live Market Data Server
NO DEMO DATA - REAL MARKET DATA ONLY
Uses Yahoo Finance for all market data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import pytz
from cachetools import TTLCache
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GSMT Live Market Data API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Market indices configuration
MARKET_INDICES = {
    # Asia Pacific
    "^AXJO": {"name": "ASX 200", "region": "Asia"},
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

def get_sydney_time():
    """Get current Sydney time"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    return datetime.now(sydney_tz)

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
        "^AXJO": (600, 960),     # 10:00 - 16:00
        "^N225": (600, 930),     # 10:00 - 15:30
        "^HSI": (690, 1080),     # 11:30 - 18:00
        "000001.SS": (690, 1020), # 11:30 - 17:00
        "^KS11": (600, 990),     # 10:00 - 16:30
        "^STI": (660, 1140),     # 11:00 - 19:00
        "^FTSE": (1020, 90),     # 17:00 - 01:30 (next day)
        "^GDAXI": (1020, 90),    # 17:00 - 01:30
        "^FCHI": (1020, 90),     # 17:00 - 01:30
        "^STOXX50E": (1020, 90), # 17:00 - 01:30
        "^IBEX": (1020, 90),     # 17:00 - 01:30
        "^AEX": (1020, 90),      # 17:00 - 01:30
        "^DJI": (1410, 360),     # 23:30 - 06:00 (next day)
        "^GSPC": (1410, 360),    # 23:30 - 06:00
        "^IXIC": (1410, 360),    # 23:30 - 06:00
        "^RUT": (1410, 360),     # 23:30 - 06:00
        "^GSPTSE": (1410, 360),  # 23:30 - 06:00
        "^BVSP": (1320, 300)     # 22:00 - 05:00
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
        "service": "GSMT Live Market Data API",
        "status": "active",
        "endpoints": {
            "/api/indices": "Get all indices with real-time data",
            "/api/indices/{symbol}": "Get specific index data",
            "/api/indices/{symbol}/intraday": "Get intraday 5-minute data",
            "/api/market-status": "Get market trading status"
        },
        "data_source": "Yahoo Finance - REAL DATA ONLY",
        "no_demo_data": True
    }

@app.get("/api/indices")
async def get_all_indices():
    """Get real-time data for all indices - NO DEMO DATA"""
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
                
                # Get current quote
                quote = ticker.info
                hist = ticker.history(period="1d", interval="5m")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    open_price = float(hist['Open'].iloc[0])
                    
                    # Get previous close from daily data
                    daily_hist = ticker.history(period="5d")
                    if len(daily_hist) >= 2:
                        previous_close = float(daily_hist['Close'].iloc[-2])
                    else:
                        previous_close = open_price
                    
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                    
                    indices_data[symbol] = {
                        "name": info["name"],
                        "region": info["region"],
                        "price": current_price,
                        "previousClose": previous_close,
                        "open": open_price,
                        "change": change,
                        "changePercent": change_percent,
                        "dayHigh": float(hist['High'].max()),
                        "dayLow": float(hist['Low'].min()),
                        "volume": int(hist['Volume'].sum()),
                        "isOpen": is_market_open(symbol),
                        "lastUpdate": datetime.now().isoformat(),
                        "dataSource": "Yahoo Finance"
                    }
                    logger.info(f"Fetched real data for {symbol}: {change_percent:.2f}%")
                else:
                    logger.warning(f"No data available for {symbol}")
                    errors.append({"symbol": symbol, "error": "No data available"})
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {str(e)}")
                errors.append({"symbol": symbol, "error": str(e)})
        
        result = {
            "indices": indices_data,
            "timestamp": datetime.now().isoformat(),
            "sydney_time": get_sydney_time().isoformat(),
            "errors": errors if errors else None,
            "data_source": "Yahoo Finance - Real Data",
            "cache_ttl": 120
        }
        
        # Cache the result
        cache[cache_key] = result
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_all_indices: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/indices/{symbol}")
async def get_index_data(symbol: str):
    """Get real-time data for a specific index"""
    try:
        if symbol not in MARKET_INDICES:
            raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        current_price = float(hist['Close'].iloc[-1])
        open_price = float(hist['Open'].iloc[0])
        
        # Get previous close
        daily_hist = ticker.history(period="5d")
        if len(daily_hist) >= 2:
            previous_close = float(daily_hist['Close'].iloc[-2])
        else:
            previous_close = open_price
        
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close > 0 else 0
        
        return {
            "symbol": symbol,
            "name": MARKET_INDICES[symbol]["name"],
            "region": MARKET_INDICES[symbol]["region"],
            "price": current_price,
            "previousClose": previous_close,
            "open": open_price,
            "change": change,
            "changePercent": change_percent,
            "dayHigh": float(hist['High'].max()),
            "dayLow": float(hist['Low'].min()),
            "volume": int(hist['Volume'].sum()),
            "isOpen": is_market_open(symbol),
            "lastUpdate": datetime.now().isoformat(),
            "dataSource": "Yahoo Finance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices/{symbol}/intraday")
async def get_intraday_data(symbol: str):
    """Get intraday 5-minute data for an index"""
    try:
        if symbol not in MARKET_INDICES:
            raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
        
        # Check cache
        cache_key = f"intraday_{symbol}"
        if cache_key in cache:
            return cache[cache_key]
        
        ticker = yf.Ticker(symbol)
        
        # Get intraday data (5-minute intervals)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No intraday data available for {symbol}")
        
        # Get previous close
        daily_hist = ticker.history(period="5d")
        if len(daily_hist) >= 2:
            previous_close = float(daily_hist['Close'].iloc[-2])
        else:
            previous_close = float(hist['Open'].iloc[0])
        
        # Format data for frontend
        data_points = []
        for index, row in hist.iterrows():
            timestamp = index.strftime('%H:%M')
            price = float(row['Close'])
            change_percent = ((price - previous_close) / previous_close * 100) if previous_close > 0 else 0
            
            data_points.append({
                "time": timestamp,
                "price": price,
                "changePercent": change_percent,
                "volume": int(row['Volume']),
                "high": float(row['High']),
                "low": float(row['Low'])
            })
        
        result = {
            "symbol": symbol,
            "name": MARKET_INDICES[symbol]["name"],
            "previousClose": previous_close,
            "dataPoints": data_points,
            "timestamp": datetime.now().isoformat(),
            "interval": "5m",
            "dataSource": "Yahoo Finance"
        }
        
        # Cache for 2 minutes
        cache[cache_key] = result
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-status")
async def get_market_status():
    """Get current market trading status"""
    sydney_time = get_sydney_time()
    
    status = {}
    for symbol, info in MARKET_INDICES.items():
        is_open = is_market_open(symbol)
        status[symbol] = {
            "name": info["name"],
            "region": info["region"],
            "isOpen": is_open,
            "status": "Trading" if is_open else "Closed"
        }
    
    return {
        "marketStatus": status,
        "sydneyTime": sydney_time.isoformat(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting GSMT Live Market Data Server - REAL DATA ONLY")
    logger.info("No demo/synthetic data will be served")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")