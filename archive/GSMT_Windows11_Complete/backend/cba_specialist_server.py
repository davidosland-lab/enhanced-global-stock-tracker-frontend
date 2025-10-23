#!/usr/bin/env python3
"""
Real CBA Specialist Server - Commonwealth Bank of Australia Analysis
Uses actual market data from Yahoo Finance API
GSMT Ver 8.1.3
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import yfinance as yf
import json
from typing import Dict, List, Any, Optional
import asyncio
import logging
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CBA Specialist Server - Real Data", version="8.1.3")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Australian banking sector peers - real symbols
BANKING_PEERS = {
    "CBA.AX": "Commonwealth Bank of Australia",
    "WBC.AX": "Westpac Banking Corporation", 
    "ANZ.AX": "ANZ Group Holdings",
    "NAB.AX": "National Australia Bank",
    "MQG.AX": "Macquarie Group",
    "BEN.AX": "Bendigo and Adelaide Bank"
}

# Data cache with 5-minute expiry
data_cache = {}
CACHE_DURATION = 300  # 5 minutes

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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CBA Specialist Server - Real Data",
        "bank": "Commonwealth Bank of Australia",
        "symbol": "CBA.AX",
        "version": "8.1.3",
        "data_source": "Yahoo Finance (Real Market Data)",
        "endpoints": {
            "/api/cba/price": "Real-time CBA stock price",
            "/api/cba/history": "Historical price data",
            "/api/cba/prediction": "Data-driven predictions",
            "/api/cba/sentiment": "Market sentiment (if available)",
            "/api/cba/banking-sector": "Real banking sector comparison",
            "/api/cba/technical": "Technical analysis"
        }
    }

@app.get("/api/cba/price")
async def get_cba_price():
    """Get real CBA stock price and metrics"""
    try:
        # Check cache
        cached = get_cached_data("cba_price")
        if cached:
            return cached
        
        # Fetch real data from Yahoo Finance
        cba = yf.Ticker("CBA.AX")
        info = cba.info
        
        # Get latest price data
        hist = cba.history(period="1d", interval="5m")
        if hist.empty:
            hist = cba.history(period="5d")  # Fallback to daily data
        
        current_price = float(hist['Close'].iloc[-1]) if not hist.empty else info.get('currentPrice', 0)
        prev_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
        
        result = {
            "symbol": "CBA.AX",
            "name": info.get('longName', 'Commonwealth Bank of Australia'),
            "price": current_price,
            "previousClose": prev_close,
            "change": current_price - prev_close if prev_close else 0,
            "changePercent": ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
            "dayHigh": info.get('dayHigh', float(hist['High'].max()) if not hist.empty else 0),
            "dayLow": info.get('dayLow', float(hist['Low'].min()) if not hist.empty else 0),
            "volume": info.get('volume', int(hist['Volume'].sum()) if not hist.empty else 0),
            "marketCap": info.get('marketCap', 0),
            "marketCapFormatted": f"${info.get('marketCap', 0) / 1e9:.1f}B" if info.get('marketCap') else "N/A",
            "peRatio": info.get('trailingPE', info.get('forwardPE', 0)),
            "dividendYield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            "beta": info.get('beta', 0),
            "52WeekHigh": info.get('fiftyTwoWeekHigh', 0),
            "52WeekLow": info.get('fiftyTwoWeekLow', 0),
            "sector": info.get('sector', 'Financial Services'),
            "industry": info.get('industry', 'Banks'),
            "exchange": "ASX",
            "currency": info.get('currency', 'AUD'),
            "lastUpdate": datetime.now().isoformat()
        }
        
        # Cache and return
        set_cached_data("cba_price", result)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching CBA price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cba/history")
async def get_cba_history(period: str = "1mo", interval: str = "1d"):
    """Get real historical CBA data"""
    try:
        # Check cache
        cache_key = f"cba_history_{period}_{interval}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        # Fetch real historical data
        cba = yf.Ticker("CBA.AX")
        hist = cba.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Format data
        prices = []
        volumes = []
        timestamps = []
        
        for index, row in hist.iterrows():
            timestamps.append(index.isoformat())
            prices.append(float(row['Close']))
            volumes.append(int(row['Volume']))
        
        result = {
            "symbol": "CBA.AX",
            "period": period,
            "interval": interval,
            "prices": prices,
            "volumes": volumes,
            "timestamps": timestamps,
            "high": float(hist['High'].max()),
            "low": float(hist['Low'].min()),
            "average": float(hist['Close'].mean()),
            "volatility": float(hist['Close'].std()),
            "totalVolume": int(hist['Volume'].sum()),
            "dataPoints": len(prices)
        }
        
        # Cache and return
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching CBA history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cba/banking-sector")
async def get_banking_sector():
    """Get real banking sector comparison"""
    try:
        # Check cache
        cached = get_cached_data("banking_sector")
        if cached:
            return cached
        
        peers = []
        
        for symbol, name in BANKING_PEERS.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_close = info.get('previousClose', float(hist['Open'].iloc[0]))
                    
                    peers.append({
                        "symbol": symbol,
                        "name": name,
                        "price": current_price,
                        "change": current_price - prev_close,
                        "changePercent": ((current_price - prev_close) / prev_close * 100) if prev_close else 0,
                        "marketCap": info.get('marketCap', 0),
                        "peRatio": info.get('trailingPE', 0),
                        "dividendYield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                        "volume": info.get('volume', 0)
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {str(e)}")
        
        # Sort by market cap
        peers.sort(key=lambda x: x['marketCap'], reverse=True)
        
        result = {
            "peers": peers,
            "sectorAverage": {
                "peRatio": np.mean([p['peRatio'] for p in peers if p['peRatio'] > 0]),
                "dividendYield": np.mean([p['dividendYield'] for p in peers if p['dividendYield'] > 0]),
                "changePercent": np.mean([p['changePercent'] for p in peers])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache and return
        set_cached_data("banking_sector", result)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching banking sector data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cba/technical")
async def get_cba_technical(period: str = "3mo"):
    """Get real technical analysis for CBA"""
    try:
        # Check cache
        cache_key = f"cba_technical_{period}"
        cached = get_cached_data(cache_key)
        if cached:
            return cached
        
        # Fetch data
        cba = yf.Ticker("CBA.AX")
        hist = cba.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No data available for technical analysis")
        
        # Calculate technical indicators
        close_prices = hist['Close'].values
        high_prices = hist['High'].values
        low_prices = hist['Low'].values
        volumes = hist['Volume'].values
        
        # RSI
        def calculate_rsi(prices, period=14):
            deltas = pd.Series(prices).diff()
            gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
            loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not rsi.empty else 50
        
        # Moving averages
        sma_20 = pd.Series(close_prices).rolling(window=20).mean()
        sma_50 = pd.Series(close_prices).rolling(window=50).mean()
        ema_12 = pd.Series(close_prices).ewm(span=12).mean()
        ema_26 = pd.Series(close_prices).ewm(span=26).mean()
        
        # MACD
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        macd_histogram = macd_line - signal_line
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        sma_bb = pd.Series(close_prices).rolling(window=bb_period).mean()
        std_bb = pd.Series(close_prices).rolling(window=bb_period).std()
        upper_band = sma_bb + (std_bb * bb_std)
        lower_band = sma_bb - (std_bb * bb_std)
        
        # Support and Resistance
        support = float(low_prices.min())
        resistance = float(high_prices.max())
        pivot = (float(hist['High'].iloc[-1]) + float(hist['Low'].iloc[-1]) + float(hist['Close'].iloc[-1])) / 3
        
        result = {
            "symbol": "CBA.AX",
            "indicators": {
                "rsi": {
                    "value": calculate_rsi(close_prices),
                    "signal": "overbought" if calculate_rsi(close_prices) > 70 else "oversold" if calculate_rsi(close_prices) < 30 else "neutral"
                },
                "macd": {
                    "macd": float(macd_line.iloc[-1]) if not macd_line.empty else 0,
                    "signal": float(signal_line.iloc[-1]) if not signal_line.empty else 0,
                    "histogram": float(macd_histogram.iloc[-1]) if not macd_histogram.empty else 0,
                    "crossover": "bullish" if float(macd_histogram.iloc[-1]) > 0 else "bearish"
                },
                "moving_averages": {
                    "sma_20": float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None,
                    "sma_50": float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
                    "ema_12": float(ema_12.iloc[-1]) if not pd.isna(ema_12.iloc[-1]) else None,
                    "ema_26": float(ema_26.iloc[-1]) if not pd.isna(ema_26.iloc[-1]) else None,
                    "signal": "bullish" if not pd.isna(sma_20.iloc[-1]) and close_prices[-1] > sma_20.iloc[-1] else "bearish"
                },
                "bollinger_bands": {
                    "upper": float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None,
                    "middle": float(sma_bb.iloc[-1]) if not pd.isna(sma_bb.iloc[-1]) else None,
                    "lower": float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None,
                    "position": "upper" if close_prices[-1] > upper_band.iloc[-1] else "lower" if close_prices[-1] < lower_band.iloc[-1] else "middle"
                },
                "support_resistance": {
                    "support": support,
                    "resistance": resistance,
                    "pivot": pivot,
                    "r1": (2 * pivot) - float(hist['Low'].iloc[-1]),
                    "s1": (2 * pivot) - float(hist['High'].iloc[-1])
                },
                "volume": {
                    "current": int(volumes[-1]),
                    "average": int(volumes.mean()),
                    "trend": "increasing" if volumes[-1] > volumes.mean() else "decreasing"
                }
            },
            "summary": {
                "trend": "bullish" if close_prices[-1] > sma_20.iloc[-1] and macd_histogram.iloc[-1] > 0 else "bearish",
                "strength": "strong" if abs(macd_histogram.iloc[-1]) > std_bb.iloc[-1] else "weak",
                "recommendation": "buy" if calculate_rsi(close_prices) < 40 and macd_histogram.iloc[-1] > 0 else "sell" if calculate_rsi(close_prices) > 60 and macd_histogram.iloc[-1] < 0 else "hold"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache and return
        set_cached_data(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error in CBA technical analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cba/prediction")
async def get_cba_prediction():
    """Get CBA predictions based on real technical analysis"""
    try:
        # Get real technical analysis
        technical = await get_cba_technical()
        price_data = await get_cba_price()
        
        current_price = price_data["price"]
        rsi = technical["indicators"]["rsi"]["value"]
        macd_signal = technical["indicators"]["macd"]["crossover"]
        trend = technical["summary"]["trend"]
        
        # Calculate prediction bias based on real indicators
        # This is a simplified model - in production use proper ML
        bias = 0
        confidence_modifier = 0.7  # Lower confidence for simple model
        
        # RSI-based bias
        if rsi < 30:
            bias += 0.015  # Oversold
        elif rsi > 70:
            bias -= 0.015  # Overbought
        else:
            bias += (50 - rsi) * 0.0002  # Neutral zone
        
        # MACD-based bias
        if macd_signal == "bullish":
            bias += 0.01
        else:
            bias -= 0.01
        
        # Trend-based bias
        if trend == "bullish":
            bias += 0.005
        else:
            bias -= 0.005
        
        # Create predictions
        predictions = {
            "1_day": {
                "predicted": current_price * (1 + bias),
                "confidence": 0.65 * confidence_modifier,
                "range": {
                    "low": current_price * (1 + bias - 0.01),
                    "high": current_price * (1 + bias + 0.01)
                }
            },
            "7_day": {
                "predicted": current_price * (1 + bias * 3.5),
                "confidence": 0.55 * confidence_modifier,
                "range": {
                    "low": current_price * (1 + bias * 3.5 - 0.03),
                    "high": current_price * (1 + bias * 3.5 + 0.03)
                }
            },
            "30_day": {
                "predicted": current_price * (1 + bias * 8),
                "confidence": 0.45 * confidence_modifier,
                "range": {
                    "low": current_price * (1 + bias * 8 - 0.05),
                    "high": current_price * (1 + bias * 8 + 0.05)
                }
            }
        }
        
        return {
            "symbol": "CBA.AX",
            "current_price": current_price,
            "predictions": predictions,
            "models": {
                "primary": "Technical Analysis Based",
                "confidence": "Real Data",
                "last_updated": datetime.now().isoformat()
            },
            "factors": {
                "rsi": rsi,
                "macd_signal": macd_signal,
                "trend": trend,
                "bias": bias
            }
        }
        
    except Exception as e:
        logger.error(f"Error in CBA prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cba/sentiment")
async def get_cba_sentiment():
    """Get market sentiment for CBA"""
    try:
        # In a real implementation, this would fetch from news APIs
        # For now, we'll derive sentiment from technical indicators
        technical = await get_cba_technical()
        
        # Derive sentiment from technical indicators
        rsi = technical["indicators"]["rsi"]["value"]
        macd_crossover = technical["indicators"]["macd"]["crossover"]
        trend = technical["summary"]["trend"]
        volume_trend = technical["indicators"]["volume"]["trend"]
        
        # Calculate sentiment score
        sentiment_score = 0
        
        if rsi < 30:
            sentiment_score += 0.3  # Oversold = potential bullish
        elif rsi > 70:
            sentiment_score -= 0.3  # Overbought = potential bearish
        
        if macd_crossover == "bullish":
            sentiment_score += 0.2
        else:
            sentiment_score -= 0.2
        
        if trend == "bullish":
            sentiment_score += 0.2
        else:
            sentiment_score -= 0.2
        
        if volume_trend == "increasing":
            sentiment_score += 0.1
        
        # Determine overall sentiment
        if sentiment_score > 0.3:
            overall_sentiment = "bullish"
        elif sentiment_score < -0.3:
            overall_sentiment = "bearish"
        else:
            overall_sentiment = "neutral"
        
        return {
            "sentiment": {
                "overall": sentiment_score,
                "trend": overall_sentiment,
                "confidence": abs(sentiment_score),
                "sources": "Technical indicators analysis"
            },
            "technical_signals": {
                "rsi_signal": technical["indicators"]["rsi"]["signal"],
                "macd_signal": macd_crossover,
                "trend": trend,
                "volume": volume_trend
            },
            "news": {
                "note": "Real-time news sentiment requires news API integration",
                "available": False
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in CBA sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)