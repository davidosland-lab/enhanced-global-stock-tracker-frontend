#!/usr/bin/env python3
"""
GSMT Unified Backend Server v9 - Fixed Version
Handles all data requests for GSMT modules with proper error handling
"""

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
import json
import traceback
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="GSMT Unified Backend v9", version="9.0")

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
CACHE_DURATION = 60  # 1 minute cache for frequent requests

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
    "^AXJO": {"name": "ASX 200", "region": "Asia", "symbol": "^AXJO"},
    "^N225": {"name": "Nikkei 225", "region": "Asia", "symbol": "^N225"},
    "^HSI": {"name": "Hang Seng", "region": "Asia", "symbol": "^HSI"},
    "^FTSE": {"name": "FTSE 100", "region": "Europe", "symbol": "^FTSE"},
    "^GDAXI": {"name": "DAX", "region": "Europe", "symbol": "^GDAXI"},
    "^FCHI": {"name": "CAC 40", "region": "Europe", "symbol": "^FCHI"},
    "^GSPC": {"name": "S&P 500", "region": "Americas", "symbol": "^GSPC"},
    "^DJI": {"name": "Dow Jones", "region": "Americas", "symbol": "^DJI"},
    "^IXIC": {"name": "NASDAQ", "region": "Americas", "symbol": "^IXIC"},
}

# Common stocks for quick access
COMMON_STOCKS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "META": "Meta Platforms Inc.",
    "NVDA": "NVIDIA Corporation",
    "CBA.AX": "Commonwealth Bank of Australia",
    "BHP.AX": "BHP Group",
    "CSL.AX": "CSL Limited"
}

@app.get("/")
async def root():
    return {
        "service": "GSMT Unified Backend v9",
        "version": "9.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/indices - Get all market indices",
            "/api/indices/{symbol}/intraday - Get intraday data for index",
            "/api/stock/{symbol} - Get stock data",
            "/api/cba/data - Get CBA specific data",
            "/api/technical/{symbol} - Get technical analysis data",
            "/api/prediction/{symbol} - Get ML predictions"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(cache)
    }

@app.get("/api/indices")
async def get_all_indices():
    """Get all market indices data"""
    logger.info("Fetching all indices data")
    
    try:
        cached = get_cached_data('all_indices')
        if cached:
            logger.info("Returning cached indices data")
            return cached
        
        indices_data = {}
        errors = []
        
        # Fetch data for each index
        for symbol, info in MARKET_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                
                # Try to get 5-minute data first
                hist = ticker.history(period="1d", interval="5m")
                
                if hist.empty:
                    # Fallback to daily data
                    hist = ticker.history(period="5d", interval="1d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    open_price = float(hist['Open'].iloc[0])
                    high = float(hist['High'].max())
                    low = float(hist['Low'].min())
                    volume = int(hist['Volume'].sum())
                    
                    # Get previous close for change calculation
                    prev_hist = ticker.history(period="2d", interval="1d")
                    if len(prev_hist) >= 2:
                        previous_close = float(prev_hist['Close'].iloc[-2])
                    else:
                        previous_close = open_price
                    
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                    
                    indices_data[symbol] = {
                        "symbol": symbol,
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
                    logger.info(f"Successfully fetched {symbol}: {info['name']}")
                else:
                    errors.append(f"No data available for {symbol}")
                    logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                error_msg = f"Error fetching {symbol}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        response = {
            "success": True,
            "indices": indices_data,
            "errors": errors if errors else None,
            "timestamp": datetime.now().isoformat(),
            "count": len(indices_data)
        }
        
        if indices_data:
            set_cache_data('all_indices', response)
        
        return response
        
    except Exception as e:
        logger.error(f"Critical error in get_all_indices: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/indices/{symbol}/intraday")
async def get_index_intraday(symbol: str):
    """Get intraday data for specific index with 5-minute intervals"""
    logger.info(f"Fetching intraday data for {symbol}")
    
    try:
        # Validate symbol
        if symbol not in MARKET_INDICES and not symbol.startswith("^"):
            symbol = f"^{symbol}"
        
        ticker = yf.Ticker(symbol)
        
        # Get 5-minute interval data for today
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            # Try hourly data as fallback
            hist = ticker.history(period="5d", interval="1h")
            if hist.empty:
                logger.warning(f"No intraday data available for {symbol}")
                return {
                    "success": False,
                    "symbol": symbol,
                    "error": "No data available",
                    "timestamp": datetime.now().isoformat()
                }
        
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
                "timestamp": idx.isoformat(),
                "price": price,
                "changePercent": change_percent,
                "volume": int(row['Volume']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "open": float(row['Open'])
            })
        
        return {
            "success": True,
            "symbol": symbol,
            "name": MARKET_INDICES.get(symbol, {}).get("name", symbol),
            "previousClose": previous_close,
            "dataPoints": data_points,
            "count": len(data_points),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stock/{symbol}")
async def get_stock_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """Get stock data for single stock tracker"""
    logger.info(f"Fetching stock data for {symbol}, period={period}, interval={interval}")
    
    try:
        # Ensure symbol is uppercase
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"stock_{symbol}_{period}_{interval}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        ticker = yf.Ticker(symbol)
        
        # Get stock info
        info = ticker.info
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            logger.warning(f"No data found for {symbol}")
            return {
                "success": False,
                "symbol": symbol,
                "error": "No data available",
                "timestamp": datetime.now().isoformat()
            }
        
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
        
        # Calculate technical indicators
        closes = hist['Close'].values
        volumes = hist['Volume'].values
        
        # Simple Moving Averages
        sma_20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else float(closes[-1])
        sma_50 = float(np.mean(closes[-50:])) if len(closes) >= 50 else float(closes[-1])
        
        # RSI
        def calculate_rsi(prices, period=14):
            deltas = np.diff(prices)
            gains = deltas.copy()
            gains[gains < 0] = 0
            losses = -deltas.copy()
            losses[losses < 0] = 0
            
            if len(gains) >= period:
                avg_gain = np.mean(gains[-period:])
                avg_loss = np.mean(losses[-period:])
            else:
                avg_gain = np.mean(gains) if len(gains) > 0 else 0
                avg_loss = np.mean(losses) if len(losses) > 0 else 0
            
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            return float(100 - (100 / (1 + rs)))
        
        rsi = calculate_rsi(closes)
        
        response = {
            "success": True,
            "symbol": symbol.upper(),
            "info": {
                "longName": info.get('longName', COMMON_STOCKS.get(symbol, symbol)),
                "currentPrice": info.get('currentPrice', float(hist['Close'].iloc[-1])),
                "previousClose": info.get('previousClose', float(hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[0])),
                "marketCap": info.get('marketCap', 0),
                "volume": info.get('volume', int(hist['Volume'].iloc[-1])),
                "dayHigh": info.get('dayHigh', float(hist['High'].iloc[-1])),
                "dayLow": info.get('dayLow', float(hist['Low'].iloc[-1])),
                "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 0),
                "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 0),
                "beta": info.get('beta', 0),
                "trailingPE": info.get('trailingPE', 0),
                "forwardPE": info.get('forwardPE', 0),
                "dividendYield": info.get('dividendYield', 0)
            },
            "technical_indicators": {
                "rsi": rsi,
                "sma20": sma_20,
                "sma50": sma_50,
                "volume": int(volumes[-1]) if len(volumes) > 0 else 0,
                "avgVolume": int(np.mean(volumes)) if len(volumes) > 0 else 0
            },
            "history": history_data,
            "timestamp": datetime.now().isoformat()
        }
        
        set_cache_data(cache_key, response)
        return response
        
    except Exception as e:
        logger.error(f"Error fetching stock {symbol}: {str(e)}\n{traceback.format_exc()}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/cba/data")
async def get_cba_data():
    """Get Commonwealth Bank of Australia data"""
    logger.info("Fetching CBA data")
    
    try:
        # Check cache
        cached = get_cached_data('cba_data')
        if cached:
            return cached
        
        ticker = yf.Ticker("CBA.AX")
        
        # Get current data
        info = ticker.info
        
        # Get intraday data
        hist = ticker.history(period="1d", interval="5m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="1h")
        
        # Get 30-day history
        hist_30d = ticker.history(period="1mo", interval="1d")
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
        else:
            current_price = info.get('currentPrice', 0)
        
        # Get previous close
        if len(hist_30d) >= 2:
            previous_close = float(hist_30d['Close'].iloc[-2])
        else:
            previous_close = info.get('previousClose', current_price)
        
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0
        
        # Format historical data
        historical_data = []
        for idx, row in hist_30d.iterrows():
            historical_data.append({
                "date": idx.isoformat(),
                "price": float(row['Close']),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "volume": int(row['Volume'])
            })
        
        response = {
            "success": True,
            "symbol": "CBA.AX",
            "name": "Commonwealth Bank of Australia",
            "currentPrice": current_price,
            "previousClose": previous_close,
            "change": change,
            "changePercent": change_percent,
            "marketCap": info.get('marketCap', 0),
            "volume": info.get('volume', int(hist['Volume'].iloc[-1]) if not hist.empty else 0),
            "avgVolume": info.get('averageVolume', 0),
            "dayHigh": info.get('dayHigh', float(hist['High'].max()) if not hist.empty else 0),
            "dayLow": info.get('dayLow', float(hist['Low'].min()) if not hist.empty else 0),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 0),
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 0),
            "peRatio": info.get('trailingPE', 0),
            "forwardPE": info.get('forwardPE', 0),
            "dividendYield": info.get('dividendYield', 0),
            "beta": info.get('beta', 0),
            "eps": info.get('trailingEps', 0),
            "pegRatio": info.get('pegRatio', 0),
            "historical": historical_data,
            "lastUpdate": datetime.now().isoformat()
        }
        
        set_cache_data('cba_data', response)
        return response
        
    except Exception as e:
        logger.error(f"Error fetching CBA data: {str(e)}\n{traceback.format_exc()}")
        return {
            "success": False,
            "symbol": "CBA.AX",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/technical/{symbol}")
async def get_technical_data(symbol: str):
    """Get technical analysis data"""
    logger.info(f"Fetching technical data for {symbol}")
    
    try:
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"technical_{symbol}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo", interval="1d")
        
        if hist.empty:
            return {
                "success": False,
                "symbol": symbol,
                "error": "No data available",
                "timestamp": datetime.now().isoformat()
            }
        
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
            
            if len(gains) >= period:
                avg_gain = np.mean(gains[-period:])
                avg_loss = np.mean(losses[-period:])
            else:
                avg_gain = np.mean(gains) if len(gains) > 0 else 0
                avg_loss = np.mean(losses) if len(losses) > 0 else 0
            
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            return float(100 - (100 / (1 + rs)))
        
        # Moving averages
        sma_20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else float(closes[-1])
        sma_50 = float(np.mean(closes[-50:])) if len(closes) >= 50 else float(closes[-1])
        sma_200 = float(np.mean(closes[-200:])) if len(closes) >= 200 else float(closes[-1])
        
        # MACD
        ema_12 = pd.Series(closes).ewm(span=12, adjust=False).mean()
        ema_26 = pd.Series(closes).ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd = float(macd_line.iloc[-1])
        signal = float(signal_line.iloc[-1])
        histogram = macd - signal
        
        # Bollinger Bands
        sma = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
        std = np.std(closes[-20:]) if len(closes) >= 20 else 0
        upper_band = float(sma + (2 * std))
        lower_band = float(sma - (2 * std))
        
        # Stochastic Oscillator
        low_14 = min(lows[-14:]) if len(lows) >= 14 else lows[-1]
        high_14 = max(highs[-14:]) if len(highs) >= 14 else highs[-1]
        k = float(((closes[-1] - low_14) / (high_14 - low_14) * 100)) if (high_14 - low_14) != 0 else 50
        
        # Format candle data for chart
        candle_data = []
        for idx, row in hist.tail(60).iterrows():  # Last 60 days
            candle_data.append({
                "time": idx.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        response = {
            "success": True,
            "symbol": symbol,
            "indicators": {
                "rsi": calculate_rsi(closes),
                "sma20": sma_20,
                "sma50": sma_50,
                "sma200": sma_200,
                "macd": macd,
                "signal": signal,
                "histogram": histogram,
                "upperBand": upper_band,
                "lowerBand": lower_band,
                "stochastic_k": k,
                "volume": int(volumes[-1]),
                "avgVolume": int(np.mean(volumes))
            },
            "candleData": candle_data,
            "lastUpdate": datetime.now().isoformat()
        }
        
        set_cache_data(cache_key, response)
        return response
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/prediction/{symbol}")
async def get_prediction_data(symbol: str):
    """Get ML prediction data for a symbol"""
    logger.info(f"Fetching prediction data for {symbol}")
    
    try:
        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period="6mo", interval="1d")
        
        if hist.empty:
            return {
                "success": False,
                "symbol": symbol,
                "error": "No data available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate simple predictions based on trends
        closes = hist['Close'].values
        
        # Calculate trend
        if len(closes) >= 30:
            recent_trend = np.polyfit(range(30), closes[-30:], 1)[0]
            short_term_prediction = closes[-1] + (recent_trend * 5)  # 5 day prediction
            medium_term_prediction = closes[-1] + (recent_trend * 20)  # 20 day prediction
        else:
            short_term_prediction = closes[-1]
            medium_term_prediction = closes[-1]
        
        # Calculate volatility
        returns = np.diff(closes) / closes[:-1]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Simple confidence based on volatility
        confidence = max(0.3, min(0.9, 1 - volatility))
        
        response = {
            "success": True,
            "symbol": symbol,
            "currentPrice": float(closes[-1]),
            "predictions": {
                "shortTerm": {
                    "days": 5,
                    "price": float(short_term_prediction),
                    "change": float(short_term_prediction - closes[-1]),
                    "changePercent": float((short_term_prediction - closes[-1]) / closes[-1] * 100)
                },
                "mediumTerm": {
                    "days": 20,
                    "price": float(medium_term_prediction),
                    "change": float(medium_term_prediction - closes[-1]),
                    "changePercent": float((medium_term_prediction - closes[-1]) / closes[-1] * 100)
                }
            },
            "metrics": {
                "volatility": float(volatility),
                "confidence": float(confidence),
                "trend": "bullish" if recent_trend > 0 else "bearish" if recent_trend < 0 else "neutral"
            },
            "historicalAccuracy": {
                "shortTerm": 0.65,  # Placeholder
                "mediumTerm": 0.58   # Placeholder
            },
            "lastUpdate": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating predictions for {symbol}: {str(e)}")
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting GSMT Unified Backend v9 on port 8000")
    logger.info("Access the API at http://localhost:8000")
    logger.info("API documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )