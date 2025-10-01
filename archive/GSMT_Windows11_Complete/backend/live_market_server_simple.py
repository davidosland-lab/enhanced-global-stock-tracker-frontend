#!/usr/bin/env python3
"""
GSMT Live Market Data Server - SIMPLE VERSION (No cachetools dependency)
NO DEMO DATA - ONLY REAL YAHOO FINANCE DATA
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import json

import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GSMT Live Market Data API",
    description="Real market data from Yahoo Finance - NO DEMO DATA",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Market indices configuration
MARKET_INDICES = {
    # Asia-Pacific
    "^AXJO": {"name": "ASX 200", "region": "Asia", "timezone": "Australia/Sydney"},
    "^N225": {"name": "Nikkei 225", "region": "Asia", "timezone": "Asia/Tokyo"},
    "^HSI": {"name": "Hang Seng", "region": "Asia", "timezone": "Asia/Hong_Kong"},
    "^SSEC": {"name": "Shanghai Composite", "region": "Asia", "timezone": "Asia/Shanghai"},
    "^KS11": {"name": "KOSPI", "region": "Asia", "timezone": "Asia/Seoul"},
    "^NSEI": {"name": "Nifty 50", "region": "Asia", "timezone": "Asia/Kolkata"},
    "^STI": {"name": "Straits Times", "region": "Asia", "timezone": "Asia/Singapore"},
    
    # Europe
    "^FTSE": {"name": "FTSE 100", "region": "Europe", "timezone": "Europe/London"},
    "^GDAXI": {"name": "DAX", "region": "Europe", "timezone": "Europe/Berlin"},
    "^FCHI": {"name": "CAC 40", "region": "Europe", "timezone": "Europe/Paris"},
    "^STOXX50E": {"name": "Euro Stoxx 50", "region": "Europe", "timezone": "Europe/Brussels"},
    "^IBEX": {"name": "IBEX 35", "region": "Europe", "timezone": "Europe/Madrid"},
    "^AEX": {"name": "AEX", "region": "Europe", "timezone": "Europe/Amsterdam"},
    "^SSMI": {"name": "SMI", "region": "Europe", "timezone": "Europe/Zurich"},
    
    # Americas
    "^GSPC": {"name": "S&P 500", "region": "Americas", "timezone": "America/New_York"},
    "^DJI": {"name": "Dow Jones", "region": "Americas", "timezone": "America/New_York"},
    "^IXIC": {"name": "NASDAQ", "region": "Americas", "timezone": "America/New_York"},
    "^RUT": {"name": "Russell 2000", "region": "Americas", "timezone": "America/New_York"},
    "^GSPTSE": {"name": "TSX", "region": "Americas", "timezone": "America/Toronto"},
    "^BVSP": {"name": "Bovespa", "region": "Americas", "timezone": "America/Sao_Paulo"},
    "^MXX": {"name": "IPC Mexico", "region": "Americas", "timezone": "America/Mexico_City"},
}

# Simple in-memory cache with timestamp
cache = {}
CACHE_DURATION = 120  # 2 minutes in seconds

def is_cache_valid(timestamp):
    """Check if cache entry is still valid"""
    if not timestamp:
        return False
    return (datetime.now() - timestamp).total_seconds() < CACHE_DURATION

def get_cached_data(key):
    """Get data from cache if valid"""
    if key in cache:
        data, timestamp = cache[key]
        if is_cache_valid(timestamp):
            logger.info(f"Cache hit for {key}")
            return data
    return None

def set_cache_data(key, data):
    """Store data in cache with timestamp"""
    cache[key] = (data, datetime.now())
    logger.info(f"Cache set for {key}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GSMT Live Market Data API",
        "status": "operational",
        "data_source": "Yahoo Finance",
        "demo_data": False,
        "message": "NO DEMO DATA - Real market data only"
    }

@app.get("/api/indices")
async def get_all_indices():
    """Get real-time data for all indices - NO DEMO DATA"""
    logger.info("Fetching all indices data from Yahoo Finance")
    
    # Check cache first
    cached_data = get_cached_data('all_indices')
    if cached_data:
        return cached_data
    
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
                
                # Get previous close
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
                    "isOpen": False,  # Market status would need real-time checking
                    "lastUpdate": datetime.now().isoformat(),
                    "dataSource": "Yahoo Finance"
                }
                logger.info(f"Successfully fetched data for {symbol}")
            else:
                logger.warning(f"No data available for {symbol}")
                errors.append(f"No data for {symbol}")
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            errors.append(f"Error fetching {symbol}: {str(e)}")
    
    response = {
        "indices": indices_data,
        "errors": errors if errors else None,
        "timestamp": datetime.now().isoformat(),
        "dataSource": "Yahoo Finance",
        "demoData": False
    }
    
    # Cache the response
    set_cache_data('all_indices', response)
    
    return response

@app.get("/api/indices/{symbol}")
async def get_index_data(symbol: str):
    """Get real-time data for a specific index - NO DEMO DATA"""
    logger.info(f"Fetching data for {symbol} from Yahoo Finance")
    
    # Check cache first
    cache_key = f'index_{symbol}'
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    if symbol not in MARKET_INDICES:
        raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        current_price = float(hist['Close'].iloc[-1])
        open_price = float(hist['Open'].iloc[0])
        high = float(hist['High'].max())
        low = float(hist['Low'].min())
        volume = int(hist['Volume'].sum())
        
        # Get previous close
        prev_hist = ticker.history(period="2d", interval="1d")
        if len(prev_hist) >= 2:
            previous_close = float(prev_hist['Close'].iloc[-2])
        else:
            previous_close = open_price
        
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
        
        response = {
            "symbol": symbol,
            "name": MARKET_INDICES[symbol]["name"],
            "region": MARKET_INDICES[symbol]["region"],
            "price": current_price,
            "previousClose": previous_close,
            "open": open_price,
            "change": change,
            "changePercent": change_percent,
            "dayHigh": high,
            "dayLow": low,
            "volume": volume,
            "lastUpdate": datetime.now().isoformat(),
            "dataSource": "Yahoo Finance",
            "demoData": False
        }
        
        # Cache the response
        set_cache_data(cache_key, response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/indices/{symbol}/intraday")
async def get_intraday_data(
    symbol: str,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """Get intraday 5-minute data for a specific index - NO DEMO DATA"""
    logger.info(f"Fetching intraday data for {symbol} from Yahoo Finance")
    
    if symbol not in MARKET_INDICES:
        raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Determine period based on date
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.now().date()
            days_diff = (today - target_date.date()).days
            
            if days_diff < 0:
                raise HTTPException(status_code=400, detail="Cannot fetch future data")
            elif days_diff == 0:
                period = "1d"
            elif days_diff <= 5:
                period = "5d"
            else:
                period = "1mo"
        else:
            period = "1d"
        
        # Fetch 5-minute interval data
        hist = ticker.history(period=period, interval="5m")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No intraday data available for {symbol}")
        
        # Get previous close for percentage calculations
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
            "name": MARKET_INDICES[symbol]["name"],
            "previousClose": previous_close,
            "dataPoints": data_points,
            "timestamp": datetime.now().isoformat(),
            "dataSource": "Yahoo Finance",
            "demoData": False
        }
        
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "GSMT Live Market Data Server",
        "demoData": False
    }

if __name__ == "__main__":
    logger.info("Starting GSMT Live Market Data Server - REAL DATA ONLY")
    logger.info("No demo/synthetic data will be served")
    uvicorn.run(app, host="0.0.0.0", port=8000)