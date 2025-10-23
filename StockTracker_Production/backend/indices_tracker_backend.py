"""
Indices Tracker Backend - Real-time global indices monitoring
Tracks AORD (Australian), FTSE 100, S&P 500, and other major indices
Port: 8007
"""

import os
import sys
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Data processing
import pandas as pd
import numpy as np
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Indices Tracker Backend", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for caching
INDICES_DB = "indices_cache.db"

# Global indices configuration with correct Yahoo Finance symbols
GLOBAL_INDICES = {
    # US Indices
    "S&P 500": {"symbol": "^GSPC", "name": "S&P 500", "region": "US"},
    "NASDAQ": {"symbol": "^IXIC", "name": "NASDAQ Composite", "region": "US"},
    "DOW": {"symbol": "^DJI", "name": "Dow Jones Industrial", "region": "US"},
    "RUSSELL": {"symbol": "^RUT", "name": "Russell 2000", "region": "US"},
    "VIX": {"symbol": "^VIX", "name": "CBOE Volatility Index", "region": "US"},
    
    # European Indices
    "FTSE": {"symbol": "^FTSE", "name": "FTSE 100", "region": "UK"},
    "DAX": {"symbol": "^GDAXI", "name": "DAX", "region": "Germany"},
    "CAC": {"symbol": "^FCHI", "name": "CAC 40", "region": "France"},
    "STOXX": {"symbol": "^STOXX50E", "name": "Euro Stoxx 50", "region": "Europe"},
    
    # Asian Indices
    "NIKKEI": {"symbol": "^N225", "name": "Nikkei 225", "region": "Japan"},
    "HSI": {"symbol": "^HSI", "name": "Hang Seng", "region": "Hong Kong"},
    "SHANGHAI": {"symbol": "000001.SS", "name": "Shanghai Composite", "region": "China"},
    "KOSPI": {"symbol": "^KS11", "name": "KOSPI", "region": "South Korea"},
    
    # Australian Indices
    "AORD": {"symbol": "^AORD", "name": "All Ordinaries", "region": "Australia"},
    "ASX200": {"symbol": "^AXJO", "name": "ASX 200", "region": "Australia"},
    
    # Commodities/Futures
    "GOLD": {"symbol": "GC=F", "name": "Gold Futures", "region": "Commodity"},
    "OIL": {"symbol": "CL=F", "name": "Crude Oil Futures", "region": "Commodity"},
    "SILVER": {"symbol": "SI=F", "name": "Silver Futures", "region": "Commodity"},
    
    # Crypto
    "BTC": {"symbol": "BTC-USD", "name": "Bitcoin", "region": "Crypto"},
    "ETH": {"symbol": "ETH-USD", "name": "Ethereum", "region": "Crypto"},
}

# Sector indices
SECTOR_INDICES = {
    "TECH": {"symbol": "XLK", "name": "Technology Select Sector", "region": "US"},
    "FINANCE": {"symbol": "XLF", "name": "Financial Select Sector", "region": "US"},
    "HEALTH": {"symbol": "XLV", "name": "Health Care Select Sector", "region": "US"},
    "ENERGY": {"symbol": "XLE", "name": "Energy Select Sector", "region": "US"},
    "CONSUMER": {"symbol": "XLY", "name": "Consumer Discretionary", "region": "US"},
    "INDUSTRIAL": {"symbol": "XLI", "name": "Industrial Select Sector", "region": "US"},
    "MATERIALS": {"symbol": "XLB", "name": "Materials Select Sector", "region": "US"},
    "UTILITIES": {"symbol": "XLU", "name": "Utilities Select Sector", "region": "US"},
    "REALESTATE": {"symbol": "XLRE", "name": "Real Estate Select Sector", "region": "US"},
}

def init_database():
    """Initialize SQLite database for caching"""
    conn = sqlite3.connect(INDICES_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indices_cache (
            cache_key TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correlations (
            pair TEXT PRIMARY KEY,
            correlation REAL,
            period TEXT,
            timestamp INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def get_cache(cache_key: str, max_age_minutes: int = 5):
    """Get cached data if fresh enough"""
    conn = sqlite3.connect(INDICES_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT data, timestamp FROM indices_cache 
        WHERE cache_key = ? AND timestamp > ?
    """, (cache_key, int(time.time()) - (max_age_minutes * 60)))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def set_cache(cache_key: str, symbol: str, data: Any):
    """Set cache data"""
    conn = sqlite3.connect(INDICES_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO indices_cache (cache_key, symbol, data, timestamp)
        VALUES (?, ?, ?, ?)
    """, (cache_key, symbol, json.dumps(data), int(time.time())))
    
    conn.commit()
    conn.close()

def fetch_index_data(symbol: str, period: str = "1d", interval: str = "5m"):
    """Fetch index data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None
            
        # Get current info
        info = ticker.info
        
        # Calculate statistics
        current_price = hist['Close'].iloc[-1] if not hist.empty else 0
        open_price = hist['Open'].iloc[0] if not hist.empty else current_price
        high = hist['High'].max() if not hist.empty else current_price
        low = hist['Low'].min() if not hist.empty else current_price
        volume = hist['Volume'].sum() if not hist.empty else 0
        
        # Calculate change
        change = current_price - open_price
        change_percent = (change / open_price * 100) if open_price != 0 else 0
        
        # Moving averages
        ma_5 = hist['Close'].tail(5).mean() if len(hist) >= 5 else current_price
        ma_20 = hist['Close'].tail(20).mean() if len(hist) >= 20 else current_price
        
        # Volatility
        volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100 if len(hist) > 1 else 0
        
        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss if loss.any() else 0
        rsi = 100 - (100 / (1 + rs)).iloc[-1] if not hist.empty else 50
        
        return {
            "symbol": symbol,
            "current": round(current_price, 2),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": int(volume),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "ma_5": round(ma_5, 2),
            "ma_20": round(ma_20, 2),
            "volatility": round(volatility, 2),
            "rsi": round(rsi, 2),
            "timestamp": datetime.now().isoformat(),
            "historical": hist['Close'].tail(100).tolist()
        }
        
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None

@app.get("/")
async def root():
    return {"message": "Indices Tracker Backend", "version": "1.0", "port": 8007}

@app.get("/api/indices")
async def get_all_indices():
    """Get current data for all major indices"""
    try:
        results = {}
        
        # Fetch data for all indices
        for key, config in GLOBAL_INDICES.items():
            cache_key = f"index_{config['symbol']}_current"
            cached_data = get_cache(cache_key, max_age_minutes=5)
            
            if cached_data:
                results[key] = cached_data
            else:
                data = fetch_index_data(config['symbol'], period="1d", interval="5m")
                if data:
                    data['name'] = config['name']
                    data['region'] = config['region']
                    results[key] = data
                    set_cache(cache_key, config['symbol'], data)
        
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/index/{symbol}")
async def get_index_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get detailed data for a specific index"""
    try:
        # Find the index config
        index_config = None
        for key, config in {**GLOBAL_INDICES, **SECTOR_INDICES}.items():
            if config['symbol'].upper() == symbol.upper() or key.upper() == symbol.upper():
                index_config = config
                break
        
        if not index_config:
            raise HTTPException(status_code=404, detail=f"Index {symbol} not found")
        
        cache_key = f"index_{index_config['symbol']}_{period}_{interval}"
        cached_data = get_cache(cache_key, max_age_minutes=15)
        
        if cached_data:
            return cached_data
        
        # Fetch detailed data
        ticker = yf.Ticker(index_config['symbol'])
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Prepare response
        data = {
            "symbol": index_config['symbol'],
            "name": index_config['name'],
            "region": index_config['region'],
            "period": period,
            "interval": interval,
            "data": {
                "dates": hist.index.strftime('%Y-%m-%d %H:%M').tolist(),
                "open": hist['Open'].tolist(),
                "high": hist['High'].tolist(),
                "low": hist['Low'].tolist(),
                "close": hist['Close'].tolist(),
                "volume": hist['Volume'].tolist()
            },
            "statistics": {
                "current": round(hist['Close'].iloc[-1], 2),
                "period_high": round(hist['High'].max(), 2),
                "period_low": round(hist['Low'].min(), 2),
                "period_return": round((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100, 2),
                "volatility": round(hist['Close'].pct_change().std() * np.sqrt(252) * 100, 2),
                "avg_volume": int(hist['Volume'].mean())
            },
            "timestamp": datetime.now().isoformat()
        }
        
        set_cache(cache_key, index_config['symbol'], data)
        return data
        
    except Exception as e:
        logger.error(f"Error getting index {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sectors")
async def get_sector_performance():
    """Get performance of all sectors"""
    try:
        results = {}
        
        for key, config in SECTOR_INDICES.items():
            cache_key = f"sector_{config['symbol']}_current"
            cached_data = get_cache(cache_key, max_age_minutes=10)
            
            if cached_data:
                results[key] = cached_data
            else:
                data = fetch_index_data(config['symbol'], period="1d", interval="15m")
                if data:
                    data['name'] = config['name']
                    results[key] = data
                    set_cache(cache_key, config['symbol'], data)
        
        # Sort by performance
        sorted_sectors = sorted(results.items(), 
                              key=lambda x: x[1].get('change_percent', 0), 
                              reverse=True)
        
        return {
            "status": "success",
            "data": dict(sorted_sectors),
            "best_performer": sorted_sectors[0][0] if sorted_sectors else None,
            "worst_performer": sorted_sectors[-1][0] if sorted_sectors else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/correlations")
async def get_index_correlations(indices: str = "SPX,FTSE,AORD", period: str = "1mo"):
    """Calculate correlation between specified indices"""
    try:
        index_list = indices.split(",")
        
        # Map to Yahoo symbols
        symbols = []
        for idx in index_list:
            idx_upper = idx.upper()
            if idx_upper in ["SPX", "SP500", "S&P"]:
                symbols.append("^GSPC")
            elif idx_upper == "FTSE":
                symbols.append("^FTSE")
            elif idx_upper == "AORD":
                symbols.append("^AORD")
            elif idx_upper == "NASDAQ":
                symbols.append("^IXIC")
            elif idx_upper == "DOW":
                symbols.append("^DJI")
            elif idx_upper == "ASX":
                symbols.append("^AXJO")
            else:
                # Try to find in our config
                for key, config in GLOBAL_INDICES.items():
                    if key.upper() == idx_upper:
                        symbols.append(config['symbol'])
                        break
        
        if not symbols:
            raise HTTPException(status_code=400, detail="No valid indices provided")
        
        # Fetch data for all indices
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval="1d")
            if not hist.empty:
                data[symbol] = hist['Close']
        
        if not data:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Create DataFrame and calculate correlations
        df = pd.DataFrame(data)
        correlation_matrix = df.corr()
        
        # Format results
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col1, col2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                correlations.append({
                    "pair": f"{col1}-{col2}",
                    "correlation": round(corr_value, 3),
                    "strength": "Strong" if abs(corr_value) > 0.7 else "Moderate" if abs(corr_value) > 0.4 else "Weak",
                    "direction": "Positive" if corr_value > 0 else "Negative"
                })
        
        return {
            "status": "success",
            "period": period,
            "correlations": correlations,
            "matrix": correlation_matrix.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating correlations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market_breadth")
async def get_market_breadth():
    """Calculate market breadth indicators"""
    try:
        # For US market breadth, we'll use S&P 500 constituents (simplified)
        # In production, you'd want to fetch actual constituent data
        
        # Fetch major indices for breadth approximation
        indices = ["^GSPC", "^IXIC", "^DJI", "^RUT"]
        
        breadth_data = {
            "advances": 0,
            "declines": 0,
            "unchanged": 0,
            "new_highs": 0,
            "new_lows": 0,
            "volume_advances": 0,
            "volume_declines": 0
        }
        
        for symbol in indices:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="1d")
                
                if not hist.empty:
                    change = hist['Close'].iloc[-1] - hist['Open'].iloc[-1]
                    if change > 0:
                        breadth_data["advances"] += 1
                        breadth_data["volume_advances"] += hist['Volume'].iloc[-1]
                    elif change < 0:
                        breadth_data["declines"] += 1
                        breadth_data["volume_declines"] += hist['Volume'].iloc[-1]
                    else:
                        breadth_data["unchanged"] += 1
                    
                    # Check for 52-week highs/lows
                    hist_year = ticker.history(period="1y", interval="1d")
                    if not hist_year.empty:
                        current = hist['Close'].iloc[-1]
                        year_high = hist_year['High'].max()
                        year_low = hist_year['Low'].min()
                        
                        if current >= year_high * 0.98:  # Within 2% of high
                            breadth_data["new_highs"] += 1
                        elif current <= year_low * 1.02:  # Within 2% of low
                            breadth_data["new_lows"] += 1
                            
            except Exception as e:
                logger.warning(f"Error processing {symbol}: {str(e)}")
                continue
        
        # Calculate breadth indicators
        total = breadth_data["advances"] + breadth_data["declines"]
        advance_decline_ratio = breadth_data["advances"] / breadth_data["declines"] if breadth_data["declines"] > 0 else float('inf')
        
        # McClellan Oscillator approximation (simplified)
        mcclellan = (breadth_data["advances"] - breadth_data["declines"]) / total * 100 if total > 0 else 0
        
        return {
            "status": "success",
            "breadth": breadth_data,
            "indicators": {
                "advance_decline_ratio": round(advance_decline_ratio, 2),
                "advance_decline_line": breadth_data["advances"] - breadth_data["declines"],
                "mcclellan_oscillator": round(mcclellan, 2),
                "new_high_low_ratio": breadth_data["new_highs"] / breadth_data["new_lows"] if breadth_data["new_lows"] > 0 else float('inf'),
                "volume_ratio": breadth_data["volume_advances"] / breadth_data["volume_declines"] if breadth_data["volume_declines"] > 0 else float('inf')
            },
            "market_sentiment": "Bullish" if advance_decline_ratio > 1.5 else "Bearish" if advance_decline_ratio < 0.67 else "Neutral",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating market breadth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compare")
async def compare_indices(symbols: str, period: str = "1mo"):
    """Compare performance of multiple indices"""
    try:
        symbol_list = symbols.split(",")
        comparison_data = {}
        
        for symbol in symbol_list:
            # Map common names to Yahoo symbols
            yahoo_symbol = symbol
            for key, config in {**GLOBAL_INDICES, **SECTOR_INDICES}.items():
                if key.upper() == symbol.upper():
                    yahoo_symbol = config['symbol']
                    break
            
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period=period, interval="1d")
            
            if not hist.empty:
                # Calculate relative performance (normalized to 100)
                normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                
                comparison_data[symbol] = {
                    "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                    "values": normalized.tolist(),
                    "absolute_return": round((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100, 2),
                    "volatility": round(hist['Close'].pct_change().std() * np.sqrt(252) * 100, 2),
                    "max_drawdown": round(((hist['Close'] / hist['Close'].cummax() - 1).min()) * 100, 2)
                }
        
        if not comparison_data:
            raise HTTPException(status_code=404, detail="No data available for comparison")
        
        return {
            "status": "success",
            "period": period,
            "comparison": comparison_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize database on startup
init_database()

if __name__ == "__main__":
    import time
    port = 8007
    logger.info(f"Starting Indices Tracker Backend on port {port}...")
    
    # Initialize cache database
    init_database()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)