#!/usr/bin/env python3
"""Simple backend server for testing indices tracker"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="Simple Stock API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Simple Stock API"
    }

@app.get("/api/stock/{symbol}")
async def get_stock_data(
    symbol: str,
    period: str = Query("5d"),
    interval: str = Query("5m")
):
    """Get stock data from Yahoo Finance"""
    try:
        print(f"Fetching data for {symbol} (period={period}, interval={interval})")
        
        # Get data from yfinance
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return {"error": f"No data available for {symbol}"}
        
        # Get basic info
        info = {}
        try:
            info = ticker.info
        except:
            pass
        
        # Prepare response
        data = []
        for timestamp, row in hist.iterrows():
            data.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })
        
        return {
            "symbol": symbol,
            "shortName": info.get("shortName", symbol),
            "currency": info.get("currency", "USD"),
            "exchangeTimezoneName": info.get("exchangeTimezoneName", "America/New_York"),
            "data": data,
            "previousClose": float(hist["Close"].iloc[0]) if len(hist) > 0 else None
        }
        
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}

if __name__ == "__main__":
    print("Starting Simple Stock API on port 8000...")
    print("Access at: http://localhost:8000")
    print("Test endpoint: http://localhost:8000/api/stock/^N225?period=5d&interval=5m")
    uvicorn.run(app, host="0.0.0.0", port=8000)