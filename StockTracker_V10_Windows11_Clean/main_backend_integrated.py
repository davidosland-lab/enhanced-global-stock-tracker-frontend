"""
Integrated Main Backend Service
Coordinates all modules with proper port configuration
NO fake data - all real market data and sentiment
"""

import os
import logging
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiohttp
import asyncio
import json
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Tracker Integrated Backend", version="3.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service configuration - CORRECT PORTS
SERVICES = {
    "ml": "http://localhost:8002",           # ML Backend with FinBERT
    "finbert": "http://localhost:8003",       # Document analyzer
    "historical": "http://localhost:8004",    # Historical data with SQLite
    "backtesting": "http://localhost:8005",   # Backtesting service
    "scraper": "http://localhost:8006"        # Enhanced global scraper
}

# Request models
class StockRequest(BaseModel):
    symbol: str
    
class PriceRequest(BaseModel):
    symbol: str
    period: str = "1mo"
    interval: str = "1d"

class AnalysisRequest(BaseModel):
    symbol: str
    include_ml: bool = True
    include_sentiment: bool = True
    include_technical: bool = True

class PredictionRequest(BaseModel):
    symbol: str
    days: int = 7
    model_type: str = "random_forest"
    use_sentiment: bool = True

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str = "ml_sentiment"
    initial_capital: float = 100000.0

class MarketOverviewRequest(BaseModel):
    symbols: List[str] = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "SPY", "QQQ"]
    include_sentiment: bool = True

# Helper functions
async def make_request(session: aiohttp.ClientSession, url: str, method: str = "GET", 
                       json_data: dict = None, timeout: int = 30) -> Optional[dict]:
    """Make async HTTP request with error handling"""
    try:
        kwargs = {"timeout": aiohttp.ClientTimeout(total=timeout)}
        if json_data:
            kwargs["json"] = json_data
            
        async with session.request(method, url, **kwargs) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"Request to {url} returned status {response.status}")
                return None
    except asyncio.TimeoutError:
        logger.error(f"Timeout requesting {url}")
        return None
    except Exception as e:
        logger.error(f"Error requesting {url}: {e}")
        return None

def get_real_stock_data(symbol: str) -> Dict:
    """Get real-time stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current data
        current = ticker.history(period="1d")
        if current.empty:
            # Try with period="5d" as fallback
            current = ticker.history(period="5d")
            if current.empty:
                raise ValueError(f"No data available for {symbol}")
        
        current_price = float(current['Close'].iloc[-1])
        current_volume = int(current['Volume'].iloc[-1])
        
        # Calculate metrics
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close else 0
        
        # Get 52-week data
        year_data = ticker.history(period="1y")
        if not year_data.empty:
            year_high = float(year_data['High'].max())
            year_low = float(year_data['Low'].min())
        else:
            year_high = info.get('fiftyTwoWeekHigh', current_price)
            year_low = info.get('fiftyTwoWeekLow', current_price)
        
        return {
            "symbol": symbol.upper(),
            "name": info.get('longName', symbol),
            "price": current_price,
            "change": change,
            "changePercent": change_percent,
            "volume": current_volume,
            "avgVolume": info.get('averageVolume', current_volume),
            "marketCap": info.get('marketCap', 0),
            "dayHigh": float(current['High'].iloc[-1]),
            "dayLow": float(current['Low'].iloc[-1]),
            "open": float(current['Open'].iloc[-1]),
            "previousClose": prev_close,
            "yearHigh": year_high,
            "yearLow": year_low,
            "pe": info.get('trailingPE', 0),
            "forwardPE": info.get('forwardPE', 0),
            "eps": info.get('trailingEps', 0),
            "dividend": info.get('dividendYield', 0),
            "beta": info.get('beta', 1.0),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "website": info.get('website', ''),
            "description": info.get('longBusinessSummary', '')[:500],
            "employees": info.get('fullTimeEmployees', 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Failed to fetch data for {symbol}")

def calculate_technical_indicators(df: pd.DataFrame) -> Dict:
    """Calculate technical indicators"""
    try:
        # Simple Moving Averages
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
        sma_200 = df['Close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else None
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        # Bollinger Bands
        bb_middle = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        bb_upper = bb_middle + (2 * bb_std)
        bb_lower = bb_middle - (2 * bb_std)
        
        # Stochastic
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        k_percent = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        d_percent = k_percent.rolling(window=3).mean()
        
        return {
            "sma_20": float(sma_20) if not pd.isna(sma_20) else None,
            "sma_50": float(sma_50) if sma_50 and not pd.isna(sma_50) else None,
            "sma_200": float(sma_200) if sma_200 and not pd.isna(sma_200) else None,
            "rsi": float(current_rsi) if not pd.isna(current_rsi) else None,
            "macd": float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
            "macd_signal": float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
            "macd_histogram": float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None,
            "bb_upper": float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
            "bb_middle": float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
            "bb_lower": float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
            "stoch_k": float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else None,
            "stoch_d": float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else None,
            "current_price": float(df['Close'].iloc[-1])
        }
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return {}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with service status"""
    async with aiohttp.ClientSession() as session:
        status = {}
        for service, url in SERVICES.items():
            health_url = f"{url}/health"
            result = await make_request(session, health_url, timeout=5)
            status[service] = "healthy" if result else "unavailable"
    
    return {
        "service": "Stock Tracker Integrated Backend",
        "version": "3.0",
        "status": "running",
        "services": status,
        "features": [
            "Real market data from Yahoo Finance",
            "FinBERT sentiment analysis",
            "Global news sentiment (politics, wars, economics)",
            "ML predictions with RandomForest/GradientBoost/XGBoost",
            "SQLite caching for 50x faster performance",
            "Backtesting with $100,000 starting capital",
            "Technical analysis and indicators"
        ],
        "endpoints": [
            "/api/stock/{symbol}",
            "/api/prices/{symbol}",
            "/api/analysis/{symbol}",
            "/api/predict",
            "/api/sentiment/{symbol}",
            "/api/backtest",
            "/api/market-overview",
            "/api/indicators/{symbol}"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    """Get real-time stock data"""
    try:
        return get_real_stock_data(symbol.upper())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/prices/{symbol}")
async def get_prices(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get historical price data with caching"""
    async with aiohttp.ClientSession() as session:
        # Try SQLite cached data first
        url = f"{SERVICES['historical']}/historical"
        data = {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "use_cache": True
        }
        
        result = await make_request(session, url, "POST", data)
        
        if result:
            return result
        else:
            # Fallback to direct Yahoo Finance
            try:
                ticker = yf.Ticker(symbol.upper())
                df = ticker.history(period=period, interval=interval)
                
                return {
                    "symbol": symbol.upper(),
                    "data": {
                        "dates": df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                        "open": df['Open'].tolist(),
                        "high": df['High'].tolist(),
                        "low": df['Low'].tolist(),
                        "close": df['Close'].tolist(),
                        "volume": df['Volume'].tolist()
                    },
                    "period": period,
                    "interval": interval
                }
            except Exception as e:
                raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/analysis/{symbol}")
async def analyze_stock(symbol: str, request: AnalysisRequest = None):
    """Comprehensive stock analysis"""
    results = {
        "symbol": symbol.upper(),
        "timestamp": datetime.now().isoformat()
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Get basic stock data
        results["stock_data"] = get_real_stock_data(symbol)
        
        # Technical analysis
        if not request or request.include_technical:
            url = f"{SERVICES['historical']}/analysis"
            data = {
                "symbol": symbol.upper(),
                "analysis_types": ["trend", "volatility", "patterns", "support_resistance"],
                "period": "3mo",
                "use_cache": True
            }
            tasks.append(make_request(session, url, "POST", data))
        
        # ML predictions
        if not request or request.include_ml:
            url = f"{SERVICES['ml']}/predict"
            data = {
                "symbol": symbol.upper(),
                "days": 7,
                "model_type": "random_forest",
                "use_sentiment": True
            }
            tasks.append(make_request(session, url, "POST", data))
        
        # Sentiment analysis
        if not request or request.include_sentiment:
            url = f"{SERVICES['scraper']}/scrape"
            data = {
                "symbol": symbol.upper(),
                "sources": [],
                "include_global": True,
                "cache_minutes": 5
            }
            tasks.append(make_request(session, url, "POST", data))
        
        # Wait for all tasks
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        for i, response in enumerate(responses):
            if isinstance(response, dict):
                if i == 0 and (not request or request.include_technical):
                    results["technical_analysis"] = response
                elif i == 1 or (i == 0 and request and not request.include_technical):
                    results["ml_predictions"] = response
                elif i == 2 or (i == 1 and request and not request.include_technical):
                    results["sentiment_analysis"] = response
    
    return results

@app.post("/api/predict")
async def predict_prices(request: PredictionRequest):
    """Get ML predictions with sentiment"""
    async with aiohttp.ClientSession() as session:
        url = f"{SERVICES['ml']}/predict"
        data = request.dict()
        
        result = await make_request(session, url, "POST", data)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=503, detail="ML service unavailable")

@app.get("/api/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Get comprehensive sentiment analysis"""
    async with aiohttp.ClientSession() as session:
        url = f"{SERVICES['scraper']}/scrape"
        data = {
            "symbol": symbol.upper(),
            "sources": [],
            "include_global": True,
            "cache_minutes": 5
        }
        
        result = await make_request(session, url, "POST", data)
        
        if result:
            # Add market risk assessment
            risk_url = f"{SERVICES['scraper']}/market-risk"
            risk_data = await make_request(session, risk_url)
            
            if risk_data:
                result["market_risk"] = risk_data
            
            return result
        else:
            raise HTTPException(status_code=503, detail="Sentiment service unavailable")

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """Run backtesting simulation"""
    async with aiohttp.ClientSession() as session:
        url = f"{SERVICES['backtesting']}/backtest"
        data = request.dict()
        
        # Set timeout higher for backtesting
        result = await make_request(session, url, "POST", data, timeout=60)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=503, detail="Backtesting service unavailable")

@app.post("/api/market-overview")
async def get_market_overview(request: MarketOverviewRequest = MarketOverviewRequest()):
    """Get market overview for multiple symbols"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "stocks": [],
        "market_sentiment": None
    }
    
    async with aiohttp.ClientSession() as session:
        # Get data for each symbol
        for symbol in request.symbols:
            try:
                stock_data = get_real_stock_data(symbol)
                results["stocks"].append(stock_data)
            except:
                logger.warning(f"Failed to get data for {symbol}")
        
        # Get overall market sentiment if requested
        if request.include_sentiment:
            url = f"{SERVICES['scraper']}/global-sentiment"
            sentiment_data = await make_request(session, url)
            
            if sentiment_data:
                results["market_sentiment"] = sentiment_data
    
    return results

@app.get("/api/indicators/{symbol}")
async def get_indicators(symbol: str):
    """Get technical indicators for a symbol"""
    try:
        ticker = yf.Ticker(symbol.upper())
        df = ticker.history(period="3mo")
        
        if df.empty:
            raise ValueError(f"No data for {symbol}")
        
        indicators = calculate_technical_indicators(df)
        
        # Add interpretation
        interpretation = []
        
        if indicators.get("rsi"):
            rsi = indicators["rsi"]
            if rsi < 30:
                interpretation.append("RSI indicates oversold conditions")
            elif rsi > 70:
                interpretation.append("RSI indicates overbought conditions")
            else:
                interpretation.append("RSI in neutral range")
        
        if indicators.get("macd") and indicators.get("macd_signal"):
            if indicators["macd"] > indicators["macd_signal"]:
                interpretation.append("MACD shows bullish momentum")
            else:
                interpretation.append("MACD shows bearish momentum")
        
        current_price = indicators.get("current_price", 0)
        
        if indicators.get("bb_upper") and indicators.get("bb_lower"):
            if current_price > indicators["bb_upper"]:
                interpretation.append("Price above Bollinger Band - potential overbought")
            elif current_price < indicators["bb_lower"]:
                interpretation.append("Price below Bollinger Band - potential oversold")
        
        return {
            "symbol": symbol.upper(),
            "indicators": indicators,
            "interpretation": interpretation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/train/{symbol}")
async def train_model(symbol: str, model_type: str = "random_forest"):
    """Trigger ML model training"""
    async with aiohttp.ClientSession() as session:
        url = f"{SERVICES['ml']}/train"
        data = {
            "symbol": symbol.upper(),
            "model_type": model_type,
            "use_sentiment": True,
            "use_global_sentiment": True,
            "cache_data": True
        }
        
        result = await make_request(session, url, "POST", data, timeout=120)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=503, detail="ML training service unavailable")

@app.get("/api/services/status")
async def check_services():
    """Check status of all microservices"""
    async with aiohttp.ClientSession() as session:
        status = {}
        
        for service, base_url in SERVICES.items():
            try:
                health_url = f"{base_url}/health"
                result = await make_request(session, health_url, timeout=5)
                
                if result:
                    status[service] = {
                        "status": "online",
                        "url": base_url,
                        "details": result
                    }
                else:
                    status[service] = {
                        "status": "offline",
                        "url": base_url,
                        "details": None
                    }
            except:
                status[service] = {
                    "status": "error",
                    "url": base_url,
                    "details": None
                }
    
    return status

# Serve static files
@app.get("/{filename}")
async def serve_html(filename: str):
    """Serve HTML files"""
    file_path = f"./{filename}"
    if os.path.exists(file_path) and filename.endswith('.html'):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)