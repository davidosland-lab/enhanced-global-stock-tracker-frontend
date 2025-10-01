#!/usr/bin/env python3
"""
Fixed Backend - Uses correct previous close from history data
"""

import logging
from datetime import datetime
from typing import Dict, Any
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pytz
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fixed Market Data API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Market indices
MARKET_INDICES = {
    "^AORD": {"name": "All Ordinaries", "region": "Asia"},
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

# Cache for 2 minutes
cache = TTLCache(maxsize=100, ttl=120)

def is_market_open(symbol: str) -> bool:
    """Check if market is currently open in AEST"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    sydney_time = datetime.now(sydney_tz)
    hour = sydney_time.hour
    weekday = sydney_time.weekday()
    
    if weekday >= 5:  # Weekend
        return False
    
    # Simplified market hours in AEST
    if symbol in ["^AORD", "^AXJO"]:
        return 10 <= hour < 16
    elif symbol in ["^FTSE", "^GDAXI", "^FCHI"]:
        return hour >= 18 or hour < 3
    elif symbol in ["^GSPC", "^DJI", "^IXIC"]:
        return hour < 7 or hour >= 23.5
    
    return False

@app.get("/")
async def root():
    return {
        "service": "Fixed Market Data API",
        "status": "active",
        "message": "Using correct previous close from history data"
    }

@app.get("/api/indices")
async def get_all_indices():
    """Get all indices with CORRECT percentage calculations"""
    cache_key = "all_indices"
    if cache_key in cache:
        return cache[cache_key]
    
    indices_data = {}
    
    for symbol, info in MARKET_INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            
            # Get 2-day history to ensure we have previous close
            hist = ticker.history(period="2d")
            
            if not hist.empty:
                # Current price is the latest close
                current_price = float(hist['Close'].iloc[-1])
                
                # Get correct previous close from history
                if len(hist) > 1:
                    # Use the second-to-last close as previous close
                    previous_close = float(hist['Close'].iloc[-2])
                else:
                    # Fallback to ticker info if only 1 day of data
                    ticker_info = ticker.info
                    previous_close = ticker_info.get('regularMarketPreviousClose', current_price)
                
                # Calculate change based on history data
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                # Get additional info
                ticker_info = ticker.info
                
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": current_price,
                    "previousClose": previous_close,
                    "change": change,
                    "changePercent": change_percent,
                    "dayHigh": ticker_info.get('dayHigh', 0),
                    "dayLow": ticker_info.get('dayLow', 0),
                    "volume": ticker_info.get('regularMarketVolume', 0),
                    "isOpen": is_market_open(symbol),
                    "lastUpdate": datetime.now().isoformat(),
                    "dataSource": "Yahoo Finance (History-based)"
                }
                
                logger.info(f"{symbol}: Price={current_price:.2f}, PrevClose={previous_close:.2f}, Change={change_percent:.2f}%")
                
            else:
                # No history available, use ticker info
                ticker_info = ticker.info
                current_price = ticker_info.get('regularMarketPrice', 0)
                previous_close = ticker_info.get('regularMarketPreviousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": current_price,
                    "previousClose": previous_close,
                    "change": change,
                    "changePercent": change_percent,
                    "dayHigh": ticker_info.get('dayHigh', 0),
                    "dayLow": ticker_info.get('dayLow', 0),
                    "volume": ticker_info.get('regularMarketVolume', 0),
                    "isOpen": is_market_open(symbol),
                    "lastUpdate": datetime.now().isoformat(),
                    "dataSource": "Yahoo Finance (Info-based)"
                }
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            indices_data[symbol] = {
                "name": info["name"],
                "region": info["region"],
                "error": str(e)
            }
    
    result = {
        "indices": indices_data,
        "timestamp": datetime.now().isoformat()
    }
    
    cache[cache_key] = result
    return result

if __name__ == "__main__":
    print("Starting FIXED Backend with correct percentage calculations...")
    print("This version uses history data for accurate previous close values")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")