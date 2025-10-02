#!/usr/bin/env python3
"""
Fixed Backend - Uses correct previous close from history data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pytz
from cachetools import TTLCache
import pandas as pd

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

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get individual stock data"""
    try:
        # Clean the symbol
        symbol = symbol.upper().strip()
        
        # Check cache first
        cache_key = f"stock_{symbol}"
        if cache_key in cache:
            return cache[cache_key]
        
        # Fetch stock data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get history for more accurate data
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            if len(hist) > 1:
                previous_close = float(hist['Close'].iloc[-2])
            else:
                previous_close = info.get('regularMarketPreviousClose', current_price)
        else:
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('regularMarketPreviousClose', current_price)
        
        # Prepare response
        stock_data = {
            "symbol": symbol,
            "longName": info.get('longName'),
            "shortName": info.get('shortName'),
            "regularMarketPrice": current_price,
            "previousClose": previous_close,
            "regularMarketPreviousClose": info.get('regularMarketPreviousClose'),
            "regularMarketOpen": info.get('regularMarketOpen'),
            "dayHigh": info.get('dayHigh'),
            "dayLow": info.get('dayLow'),
            "regularMarketVolume": info.get('regularMarketVolume'),
            "averageVolume": info.get('averageVolume'),
            "marketCap": info.get('marketCap'),
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow'),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh'),
            "trailingPE": info.get('trailingPE'),
            "dividendYield": info.get('dividendYield'),
            "beta": info.get('beta'),
            "exchange": info.get('exchange'),
            "currency": info.get('currency'),
            "dataSource": "Yahoo Finance (Real-time)",
            "lastUpdate": datetime.now().isoformat()
        }
        
        # Cache for 2 minutes
        cache[cache_key] = stock_data
        return stock_data
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found or error occurred: {str(e)}")

@app.get("/api/historical/{symbol}")
async def get_historical_data(symbol: str, period: str = "5d", interval: str = None):
    """Get historical data for charting"""
    cache_key = f"hist_{symbol}_{period}_{interval}"
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Validate period
        valid_periods = ["1d", "2d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
        if period not in valid_periods:
            period = "5d"
        
        # Validate interval
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        if interval and interval not in valid_intervals:
            interval = None
        
        # Get historical data with interval if specified
        if interval:
            # For intraday data, use download method which supports intervals
            end_date = datetime.now()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "2d":
                start_date = end_date - timedelta(days=2)
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=5)
            
            hist = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
        else:
            # Default behavior without interval
            hist = ticker.history(period=period)
        
        if hist is None or (hasattr(hist, 'empty') and hist.empty) or len(hist) == 0:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")
        
        # Format data for charting
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.isoformat(),
                "open": float(row['Open']) if 'Open' in row else float(row.get('open', 0)),
                "high": float(row['High']) if 'High' in row else float(row.get('high', 0)),
                "low": float(row['Low']) if 'Low' in row else float(row.get('low', 0)),
                "close": float(row['Close']) if 'Close' in row else float(row.get('close', 0)),
                "volume": int(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else 0
            })
        
        result = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": data,
            "dataPoints": len(data)
        }
        
        # Cache for 5 minutes
        cache[cache_key] = result
        return result
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting FIXED Backend with correct percentage calculations...")
    print("This version uses history data for accurate previous close values")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")