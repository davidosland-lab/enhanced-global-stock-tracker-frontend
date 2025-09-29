#!/usr/bin/env python3
"""
Real Market Data Server - Actual Yahoo Finance Market Data
Uses yfinance API for real-time market information
GSMT Ver 8.1.3
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import yfinance as yf
import json
from typing import Dict, List, Any, Optional
import asyncio
import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GSMT Real Market Data Server", version="8.1.3")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real market indices symbols
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

# Cache for market data (5 minute expiry)
data_cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

def get_cached_data(key: str) -> Optional[Any]:
    """Get data from cache if still valid"""
    if key in data_cache:
        cached = data_cache[key]
        if datetime.now() - cached['timestamp'] < timedelta(seconds=CACHE_DURATION):
            return cached['data']
    return None

def set_cached_data(key: str, data: Any):
    """Store data in cache with timestamp"""
    data_cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

def get_market_hours(region: str) -> Dict[str, Any]:
    """Get actual market hours status for a region"""
    now = datetime.now()
    
    # These are simplified market hours - in production, use proper timezone handling
    market_hours = {
        "Asia": {
            "open": 9,
            "close": 16,
            "timezone": "AEST"
        },
        "Europe": {
            "open": 8,
            "close": 16.5,
            "timezone": "CET"
        },
        "Americas": {
            "open": 9.5,
            "close": 16,
            "timezone": "EST"
        }
    }
    
    if region in market_hours:
        hours = market_hours[region]
        # This is simplified - in production, convert to proper timezone
        current_hour = now.hour + (now.minute / 60)
        is_open = hours["open"] <= current_hour < hours["close"]
        
        return {
            "is_open": is_open,
            "open_time": f"{hours['open']:.1f}",
            "close_time": f"{hours['close']:.1f}",
            "timezone": hours["timezone"],
            "status": "OPEN" if is_open else "CLOSED"
        }
    
    return {"is_open": False, "status": "UNKNOWN"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GSMT Real Market Data Server",
        "version": "8.1.3",
        "status": "operational",
        "data_source": "yfinance (Yahoo Finance)",
        "endpoints": {
            "/api/stock/{symbol}": "Get real stock/index data",
            "/api/indices": "Get all indices with real data",
            "/api/market-status": "Get market status",
            "/api/technical/{symbol}": "Technical analysis with real data",
            "/api/predict/{symbol}": "Real data-based predictions",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, period: str = "1d", interval: str = "5m"):
    """Get real stock data from Yahoo Finance"""
    try:
        # Check cache first
        cache_key = f"stock_{symbol}_{period}_{interval}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        # Fetch real data from yfinance
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Get current info
        info = ticker.info
        
        # Prepare response
        data = {
            "symbol": symbol,
            "name": info.get("longName", info.get("shortName", symbol)),
            "price": float(hist['Close'].iloc[-1]) if not hist.empty else 0,
            "previousClose": info.get("previousClose", float(hist['Close'].iloc[0]) if not hist.empty else 0),
            "change": 0,
            "changePercent": 0,
            "dayHigh": float(hist['High'].max()) if not hist.empty else 0,
            "dayLow": float(hist['Low'].min()) if not hist.empty else 0,
            "volume": int(hist['Volume'].sum()) if not hist.empty else 0,
            "marketCap": info.get("marketCap", 0),
            "history": hist.reset_index().to_dict('records') if not hist.empty else []
        }
        
        # Calculate change
        if data["previousClose"] > 0:
            data["change"] = data["price"] - data["previousClose"]
            data["changePercent"] = (data["change"] / data["previousClose"]) * 100
        
        # Cache and return
        set_cached_data(cache_key, data)
        return data
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/indices")
async def get_all_indices():
    """Get real data for all tracked indices"""
    try:
        # Check cache
        cache_key = "all_indices"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        indices_data = {}
        errors = []
        
        # Fetch data for each index
        for symbol, info in MARKET_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="5m")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    open_price = float(hist['Open'].iloc[0])
                    
                    indices_data[symbol] = {
                        "name": info["name"],
                        "region": info["region"],
                        "price": current_price,
                        "previousClose": open_price,
                        "change": current_price - open_price,
                        "changePercent": ((current_price - open_price) / open_price * 100) if open_price > 0 else 0,
                        "dayHigh": float(hist['High'].max()),
                        "dayLow": float(hist['Low'].min()),
                        "volume": int(hist['Volume'].sum()),
                        "lastUpdate": datetime.now().isoformat()
                    }
            except Exception as e:
                errors.append({"symbol": symbol, "error": str(e)})
                logger.warning(f"Failed to fetch {symbol}: {str(e)}")
        
        result = {
            "indices": indices_data,
            "timestamp": datetime.now().isoformat(),
            "errors": errors if errors else None
        }
        
        # Cache and return
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-status")
async def get_market_status():
    """Get real market status for all regions"""
    try:
        regions = ["Asia", "Europe", "Americas"]
        status = {}
        
        for region in regions:
            status[region] = get_market_hours(region)
            
            # Add real-time market sentiment if available
            # This could be enhanced with real sentiment APIs
            status[region]["indices"] = []
            for symbol, info in MARKET_INDICES.items():
                if info["region"] == region:
                    status[region]["indices"].append(symbol)
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str, period: str = "1mo"):
    """Get real technical analysis for a symbol"""
    try:
        # Check cache
        cache_key = f"technical_{symbol}_{period}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        # Fetch real data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate real technical indicators
        close_prices = hist['Close'].values
        high_prices = hist['High'].values
        low_prices = hist['Low'].values
        volumes = hist['Volume'].values
        
        # RSI calculation
        def calculate_rsi(prices, period=14):
            deltas = pd.Series(prices).diff()
            gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
            loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.values
        
        # Moving averages
        sma_20 = pd.Series(close_prices).rolling(window=20).mean().values
        sma_50 = pd.Series(close_prices).rolling(window=50).mean().values
        ema_12 = pd.Series(close_prices).ewm(span=12).mean().values
        ema_26 = pd.Series(close_prices).ewm(span=26).mean().values
        
        # MACD
        macd_line = ema_12 - ema_26
        signal_line = pd.Series(macd_line).ewm(span=9).mean().values
        
        # Bollinger Bands
        sma_20_series = pd.Series(close_prices).rolling(window=20).mean()
        std_20 = pd.Series(close_prices).rolling(window=20).std()
        upper_band = (sma_20_series + (std_20 * 2)).values
        lower_band = (sma_20_series - (std_20 * 2)).values
        
        result = {
            "symbol": symbol,
            "period": period,
            "indicators": {
                "rsi": {
                    "value": float(calculate_rsi(close_prices)[-1]) if len(close_prices) > 14 else 50,
                    "interpretation": "neutral"
                },
                "macd": {
                    "macd": float(macd_line[-1]) if len(macd_line) > 0 else 0,
                    "signal": float(signal_line[-1]) if len(signal_line) > 0 else 0,
                    "histogram": float(macd_line[-1] - signal_line[-1]) if len(macd_line) > 0 else 0
                },
                "moving_averages": {
                    "sma_20": float(sma_20[-1]) if not pd.isna(sma_20[-1]) else None,
                    "sma_50": float(sma_50[-1]) if not pd.isna(sma_50[-1]) else None,
                    "ema_12": float(ema_12[-1]) if not pd.isna(ema_12[-1]) else None,
                    "ema_26": float(ema_26[-1]) if not pd.isna(ema_26[-1]) else None
                },
                "bollinger_bands": {
                    "upper": float(upper_band[-1]) if not pd.isna(upper_band[-1]) else None,
                    "middle": float(sma_20[-1]) if not pd.isna(sma_20[-1]) else None,
                    "lower": float(lower_band[-1]) if not pd.isna(lower_band[-1]) else None
                },
                "volume": {
                    "current": int(volumes[-1]),
                    "average": int(volumes.mean())
                }
            },
            "price_data": {
                "current": float(close_prices[-1]),
                "high": float(high_prices.max()),
                "low": float(low_prices.min()),
                "change": float(close_prices[-1] - close_prices[0]),
                "changePercent": float((close_prices[-1] - close_prices[0]) / close_prices[0] * 100)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add interpretations
        rsi_value = result["indicators"]["rsi"]["value"]
        if rsi_value > 70:
            result["indicators"]["rsi"]["interpretation"] = "overbought"
        elif rsi_value < 30:
            result["indicators"]["rsi"]["interpretation"] = "oversold"
        
        # Cache and return
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predict/{symbol}")
async def get_prediction(symbol: str):
    """Get predictions based on real technical analysis"""
    try:
        # Get real technical data
        tech_data = await get_technical_analysis(symbol)
        
        # Simple prediction based on real indicators
        # In production, this would use trained ML models
        current_price = tech_data["price_data"]["current"]
        rsi = tech_data["indicators"]["rsi"]["value"]
        macd_histogram = tech_data["indicators"]["macd"]["histogram"]
        
        # Simple rule-based prediction (replace with ML model)
        bias = 0
        if rsi < 30:
            bias += 0.02  # Oversold, expect bounce
        elif rsi > 70:
            bias -= 0.02  # Overbought, expect pullback
        
        if macd_histogram > 0:
            bias += 0.01  # Bullish momentum
        else:
            bias -= 0.01  # Bearish momentum
        
        predictions = {
            "1_day": {
                "value": current_price * (1 + bias),
                "confidence": 0.65,  # Lower confidence for simple model
                "direction": "up" if bias > 0 else "down"
            },
            "1_week": {
                "value": current_price * (1 + bias * 3),
                "confidence": 0.55,
                "direction": "up" if bias > 0 else "down"
            },
            "1_month": {
                "value": current_price * (1 + bias * 5),
                "confidence": 0.45,
                "direction": "up" if bias > 0 else "down"
            }
        }
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predictions": predictions,
            "based_on": "real_technical_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in prediction for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/technical/candlestick-data/{symbol}")
async def get_candlestick_data(symbol: str, period: str = "5d", interval: str = "15m"):
    """Get real candlestick data for charting"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Format for candlestick charts
        candles = []
        for index, row in hist.iterrows():
            candles.append({
                "timestamp": index.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": candles
        }
        
    except Exception as e:
        logger.error(f"Error fetching candlestick data for {symbol}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)