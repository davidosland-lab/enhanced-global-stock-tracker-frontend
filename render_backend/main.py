#!/usr/bin/env python3
"""
Optimized backend for Render.com deployment
Handles stock market data fetching with proper error handling
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global Market Indices API",
    description="Real-time market data API for indices tracking",
    version="1.0.0"
)

# Configure CORS - allow all origins for public API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Global Market Indices API",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "stock_data": "/api/stock/{symbol}",
            "indices_list": "/api/indices"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Global Market Indices API",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/stock/{symbol}")
async def get_stock_data(
    symbol: str,
    period: str = Query("5d", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("5m", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """
    Fetch historical stock/index data
    """
    try:
        logger.info(f"Fetching data for {symbol} (period={period}, interval={interval})")
        
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            logger.warning(f"No data found for {symbol}")
            raise HTTPException(status_code=404, detail=f"No data available for symbol: {symbol}")
        
        # Get ticker info (may fail for indices, so we handle gracefully)
        info = {}
        try:
            info = ticker.info
        except Exception as e:
            logger.debug(f"Could not fetch info for {symbol}: {e}")
            # Provide defaults for indices
            info = {
                "shortName": symbol,
                "currency": "USD",
                "exchangeTimezoneName": "America/New_York"
            }
        
        # Prepare data for response
        data_points = []
        for timestamp, row in hist.iterrows():
            data_points.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row["Open"]) if row["Open"] else None,
                "high": float(row["High"]) if row["High"] else None,
                "low": float(row["Low"]) if row["Low"] else None,
                "close": float(row["Close"]) if row["Close"] else None,
                "volume": int(row["Volume"]) if row["Volume"] else 0
            })
        
        # Get previous close for percentage calculations
        previous_close = None
        if len(hist) > 0:
            # Try to get the actual previous close
            try:
                # Get one more day of data to find previous close
                extended_hist = ticker.history(period="10d", interval="1d")
                if len(extended_hist) > 1:
                    previous_close = float(extended_hist["Close"].iloc[-2])
                else:
                    previous_close = float(hist["Close"].iloc[0])
            except:
                previous_close = float(hist["Close"].iloc[0])
        
        return {
            "symbol": symbol,
            "shortName": info.get("shortName", symbol),
            "currency": info.get("currency", "USD"),
            "exchangeTimezoneName": info.get("exchangeTimezoneName", "America/New_York"),
            "data": data_points,
            "previousClose": previous_close,
            "dataPoints": len(data_points),
            "period": period,
            "interval": interval
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/indices")
async def get_indices_list():
    """
    Get list of supported market indices
    """
    return {
        "asia": [
            {"symbol": "^N225", "name": "Nikkei 225", "country": "Japan"},
            {"symbol": "^HSI", "name": "Hang Seng", "country": "Hong Kong"},
            {"symbol": "000001.SS", "name": "Shanghai Composite", "country": "China"},
            {"symbol": "^AXJO", "name": "ASX 200", "country": "Australia"},
            {"symbol": "^AORD", "name": "All Ordinaries", "country": "Australia"},
            {"symbol": "^KS11", "name": "KOSPI", "country": "South Korea"},
            {"symbol": "^STI", "name": "Straits Times", "country": "Singapore"}
        ],
        "europe": [
            {"symbol": "^FTSE", "name": "FTSE 100", "country": "UK"},
            {"symbol": "^GDAXI", "name": "DAX", "country": "Germany"},
            {"symbol": "^FCHI", "name": "CAC 40", "country": "France"},
            {"symbol": "^STOXX50E", "name": "Euro Stoxx 50", "country": "EU"},
            {"symbol": "^IBEX", "name": "IBEX 35", "country": "Spain"},
            {"symbol": "^SSMI", "name": "SMI", "country": "Switzerland"}
        ],
        "americas": [
            {"symbol": "^GSPC", "name": "S&P 500", "country": "USA"},
            {"symbol": "^DJI", "name": "Dow Jones", "country": "USA"},
            {"symbol": "^IXIC", "name": "NASDAQ", "country": "USA"},
            {"symbol": "^RUT", "name": "Russell 2000", "country": "USA"},
            {"symbol": "^GSPTSE", "name": "TSX Composite", "country": "Canada"},
            {"symbol": "^BVSP", "name": "Bovespa", "country": "Brazil"},
            {"symbol": "^MXX", "name": "IPC Mexico", "country": "Mexico"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)