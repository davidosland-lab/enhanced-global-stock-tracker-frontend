#!/usr/bin/env python3
"""
Fixed Backend V2 - With proper intraday support
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pytz
from cachetools import TTLCache
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fixed Market Data API V2", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

INDICES = {
    "^AORD": {"name": "ASX All Ordinaries", "region": "Australia"},
    "^FTSE": {"name": "FTSE 100", "region": "UK"},
    "^GSPC": {"name": "S&P 500", "region": "US"},
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Fixed Market Data API V2 with intraday support",
        "endpoints": [
            "/api/indices",
            "/api/stock/{symbol}",
            "/api/historical/{symbol}?period=1d&interval=5m"
        ],
        "version": "2.0.0"
    }

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get individual stock/index quote data"""
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
            "price": current_price,  # Alias for compatibility
            "previousClose": previous_close,
            "regularMarketPreviousClose": info.get('regularMarketPreviousClose', previous_close),
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
            "quoteType": info.get('quoteType'),
            "region": info.get('region')
        }
        
        # Cache the result
        cache[cache_key] = stock_data
        return stock_data
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found or error occurred: {str(e)}")

@app.get("/api/historical/{symbol}")
async def get_historical_data(
    symbol: str, 
    period: str = "5d", 
    interval: Optional[str] = None
):
    """Get historical data for charting with optional intraday intervals"""
    
    # Create cache key
    cache_key = f"hist_{symbol}_{period}_{interval}"
    if cache_key in cache:
        logger.info(f"Returning cached data for {cache_key}")
        return cache[cache_key]
    
    try:
        # Clean symbol
        symbol = symbol.upper().strip()
        logger.info(f"Fetching historical data for {symbol}, period={period}, interval={interval}")
        
        # Validate period
        valid_periods = ["1d", "2d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
        if period not in valid_periods:
            period = "5d"
        
        # Validate interval if provided
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        if interval and interval not in valid_intervals:
            logger.warning(f"Invalid interval {interval}, ignoring")
            interval = None
        
        # Fetch data
        if interval:
            # For intraday data, use download method
            logger.info(f"Using yf.download for intraday data")
            end_date = datetime.now()
            
            # Calculate start date based on period
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "2d":
                start_date = end_date - timedelta(days=2)
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=5)
            
            # Download with specific interval
            hist = yf.download(
                symbol, 
                start=start_date, 
                end=end_date, 
                interval=interval, 
                progress=False,
                auto_adjust=True,
                prepost=True
            )
            
            logger.info(f"Downloaded {len(hist)} data points")
            
        else:
            # Use ticker.history for daily data
            logger.info(f"Using ticker.history for daily data")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            logger.info(f"Got {len(hist)} data points from history")
        
        # Check if we have data
        if hist is None or len(hist) == 0:
            logger.warning(f"No data returned for {symbol}")
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")
        
        # Format data for charting
        data = []
        
        # Check if it's a multi-level column DataFrame (happens with yf.download)
        if isinstance(hist.columns, pd.MultiIndex):
            # Flatten the multi-level columns
            hist.columns = hist.columns.get_level_values(0)
        
        for date, row in hist.iterrows():
            try:
                # Get values, handling both uppercase and lowercase column names
                open_val = row.get('Open', row.get('open', 0))
                high_val = row.get('High', row.get('high', 0))
                low_val = row.get('Low', row.get('low', 0))
                close_val = row.get('Close', row.get('close', 0))
                volume_val = row.get('Volume', row.get('volume', 0))
                
                # Convert to float/int, handling NaN values
                open_price = float(open_val) if not pd.isna(open_val) else 0
                high_price = float(high_val) if not pd.isna(high_val) else 0
                low_price = float(low_val) if not pd.isna(low_val) else 0
                close_price = float(close_val) if not pd.isna(close_val) else 0
                volume = int(volume_val) if not pd.isna(volume_val) else 0
                
                data.append({
                    "date": date.isoformat(),
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume
                })
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue
        
        result = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": data,
            "dataPoints": len(data)
        }
        
        # Cache for 5 minutes
        cache[cache_key] = result
        logger.info(f"Returning {len(data)} data points for {symbol}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices")
async def get_all_indices():
    """Get all major indices data"""
    cache_key = "all_indices"
    if cache_key in cache:
        return cache[cache_key]
    
    indices_data = {}
    for symbol, info in INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                if len(hist) > 1:
                    previous_close = float(hist['Close'].iloc[-2])
                else:
                    previous_close = current_price
                
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "price": current_price,
                    "previousClose": previous_close,
                    "change": change,
                    "changePercent": change_percent,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                indices_data[symbol] = {
                    "name": info["name"],
                    "region": info["region"],
                    "error": "No data available"
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
    print("=" * 60)
    print("Starting FIXED Backend V2 with intraday support...")
    print("This version properly handles intraday data intervals")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8002)