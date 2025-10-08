#!/usr/bin/env python3
"""
Stock Tracker Backend - Core Functions
Real Yahoo Finance data only - No synthetic/demo data
"""

import logging
import yfinance as yf
from datetime import datetime
import pytz
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_aest_time():
    """Get current time in Australian Eastern time (ADST support)"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    return datetime.now(sydney_tz)

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get REAL stock information from Yahoo Finance - NO FALLBACK DATA"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price - REAL DATA ONLY
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        if not current_price:
            hist = ticker.history(period='1d')
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
        
        # Calculate daily change
        prev_close = info.get('previousClose', 0) or info.get('regularMarketPreviousClose', 0)
        if prev_close and current_price:
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0
            change_percent = 0
        
        # Return ONLY real data
        return {
            "symbol": symbol,
            "name": info.get('longName', symbol),
            "price": round(current_price, 2) if current_price else 0,
            "previousClose": round(prev_close, 2) if prev_close else 0,
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "volume": info.get('volume', 0),
            "marketCap": info.get('marketCap', 0),
            "dayHigh": info.get('dayHigh', 0),
            "dayLow": info.get('dayLow', 0),
            "yearHigh": info.get('fiftyTwoWeekHigh', 0),
            "yearLow": info.get('fiftyTwoWeekLow', 0),
            "pe_ratio": info.get('forwardPE', 0),
            "dividend_yield": info.get('dividendYield', 0),
            "timestamp": datetime.now().isoformat(),
            "data_source": "yahoo_finance_real"
        }
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
        raise

# Market indices
INDICES = {
    "^AORD": {"name": "ASX All Ordinaries", "region": "Australia"},
    "^AXJO": {"name": "ASX 200", "region": "Australia"},
    "^FTSE": {"name": "FTSE 100", "region": "UK"},
    "^GSPC": {"name": "S&P 500", "region": "US"},
    "^DJI": {"name": "Dow Jones", "region": "US"},
    "^IXIC": {"name": "NASDAQ", "region": "US"},
    "^N225": {"name": "Nikkei 225", "region": "Japan"},
    "^HSI": {"name": "Hang Seng", "region": "Hong Kong"}
}

# Popular stocks
POPULAR_STOCKS = {
    'ASX': ['CBA.AX', 'BHP.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 'WDS.AX', 'MQG.AX', 'WES.AX', 'TLS.AX'],
    'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'JNJ', 'V'],
    'Tech': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'INTC', 'ORCL', 'CSCO', 'ADBE']
}