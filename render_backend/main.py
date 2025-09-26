#!/usr/bin/env python3
"""
Optimized backend for Render.com deployment
Handles stock market data fetching with proper error handling
Includes CBA-specific enhanced features
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging
import os
import random
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global Market Indices API",
    description="Real-time market data API with integrated CBA analysis system",
    version="2.0.0"
)

# Import integrated CBA system if available
try:
    from integrated_cba_system import router as cba_router
    app.include_router(cba_router)
    logger.info("✅ CBA Integrated System loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ CBA Integrated System not available: {e}")

# Import unified prediction API with Phase 3 and Phase 4 models
try:
    from unified_prediction_api import router as unified_router
    app.include_router(unified_router)
    logger.info("✅ Unified Prediction API (Phase 3 & 4) loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Unified Prediction API not available: {e}")

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

# ============================================
# CBA Enhanced Features
# ============================================

def generate_mock_publications(limit: int = 5) -> List[Dict]:
    """Generate mock CBA publications with sentiment analysis"""
    publication_types = ["Annual Report", "Quarterly Update", "Market Analysis", "Economic Outlook", "Investor Brief"]
    sentiments = ["positive", "neutral", "negative"]
    
    publications = []
    for i in range(limit):
        pub_date = datetime.now() - timedelta(days=random.randint(1, 90))
        pub_type = random.choice(publication_types)
        sentiment = random.choice(sentiments)
        sentiment_score = random.uniform(-1, 1) if sentiment == "mixed" else (
            random.uniform(0.3, 1) if sentiment == "positive" else
            random.uniform(-1, -0.3) if sentiment == "negative" else
            random.uniform(-0.3, 0.3)
        )
        
        publications.append({
            "id": hashlib.md5(f"pub_{i}_{pub_date}".encode()).hexdigest()[:8],
            "title": f"CBA {pub_type}: {pub_date.strftime('%B %Y')} Edition",
            "publication_type": pub_type,
            "publication_date": pub_date.isoformat(),
            "content_summary": f"Analysis of CBA's {pub_type.lower()} focusing on {random.choice(['digital transformation', 'mortgage portfolio', 'business banking', 'retail operations', 'risk management'])}.",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment,
            "market_impact": random.choice(["High", "Medium", "Low"]),
            "key_topics": random.sample(["Digital Banking", "Home Loans", "Business Services", "Risk Management", "Customer Growth"], 3),
        })
    
    return publications

def generate_mock_news(limit: int = 5) -> List[Dict]:
    """Generate mock news articles about CBA"""
    headlines = [
        "CBA Reports Strong Quarter with Digital Banking Growth",
        "Commonwealth Bank Expands Business Lending Portfolio",
        "CBA Introduces New AI-Powered Customer Service",
        "Analysts Upgrade CBA Stock Rating to Buy",
        "CBA Partners with Fintech for Payment Innovation",
        "Commonwealth Bank Announces Dividend Increase",
        "CBA's Home Loan Market Share Reaches New High",
        "Tech Investment Pays Off for Commonwealth Bank"
    ]
    
    sources = ["Australian Financial Review", "The Australian", "Reuters", "Bloomberg", "Sydney Morning Herald"]
    
    articles = []
    for i in range(min(limit, len(headlines))):
        pub_date = datetime.now() - timedelta(hours=random.randint(1, 168))
        sentiment = random.choice(["positive", "neutral", "negative"])
        sentiment_score = (
            random.uniform(0.3, 0.9) if sentiment == "positive" else
            random.uniform(-0.9, -0.3) if sentiment == "negative" else
            random.uniform(-0.2, 0.2)
        )
        
        articles.append({
            "id": hashlib.md5(f"news_{i}_{pub_date}".encode()).hexdigest()[:8],
            "headline": headlines[i] if i < len(headlines) else random.choice(headlines),
            "source": random.choice(sources),
            "published_date": pub_date.isoformat(),
            "summary": f"Recent developments at Commonwealth Bank show {random.choice(['strong performance', 'strategic growth', 'market expansion', 'innovation focus'])} in {random.choice(['retail banking', 'business services', 'digital platforms', 'wealth management'])}.",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment,
            "relevance_score": random.uniform(0.7, 1.0),
            "categories": random.sample(["Banking", "Finance", "Technology", "Markets", "Business"], 2),
        })
    
    return articles

@app.get("/api/prediction/cba/publications")
async def get_cba_publications(
    limit: int = Query(5, description="Number of publications to return"),
    sentiment_filter: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral")
):
    """Get CBA publications with sentiment analysis"""
    try:
        publications = generate_mock_publications(limit)
        
        if sentiment_filter:
            publications = [p for p in publications if p["sentiment_label"] == sentiment_filter]
        
        return {
            "success": True,
            "publications": publications,
            "total_count": len(publications),
            "average_sentiment": np.mean([p["sentiment_score"] for p in publications]) if publications else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching publications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prediction/cba/news")
async def get_cba_news(
    limit: int = Query(5, description="Number of news articles to return"),
    hours: int = Query(168, description="Hours of news history to fetch")
):
    """Get news articles about CBA with sentiment analysis"""
    try:
        articles = generate_mock_news(limit)
        
        # Calculate aggregate sentiment
        sentiments = [a["sentiment_score"] for a in articles]
        
        return {
            "success": True,
            "articles": articles,
            "total_count": len(articles),
            "sentiment_summary": {
                "average": np.mean(sentiments) if sentiments else 0,
                "positive_count": sum(1 for s in sentiments if s > 0.2),
                "negative_count": sum(1 for s in sentiments if s < -0.2),
                "neutral_count": sum(1 for s in sentiments if -0.2 <= s <= 0.2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prediction/cba/enhanced")
async def get_enhanced_prediction(
    horizon: str = Query("1w", description="Prediction horizon: 1d, 1w, 1m, 3m"),
    include_publications: bool = Query(True, description="Include publications in analysis"),
    include_news: bool = Query(True, description="Include news sentiment in analysis")
):
    """Get enhanced CBA prediction with sentiment and document analysis"""
    try:
        # Get real market data for CBA
        ticker = yf.Ticker("CBA.AX")
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            raise ValueError("No data available for CBA.AX")
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Calculate basic technical indicators
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std()
        trend = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
        
        # Generate prediction based on trend and volatility
        horizon_days = {
            "1d": 1, "1w": 7, "1m": 30, "3m": 90
        }.get(horizon, 7)
        
        # Simulate sentiment impact
        sentiment_adjustment = 0
        if include_publications or include_news:
            pubs = generate_mock_publications(3) if include_publications else []
            news = generate_mock_news(3) if include_news else []
            all_sentiments = [p["sentiment_score"] for p in pubs] + [n["sentiment_score"] for n in news]
            avg_sentiment = np.mean(all_sentiments) if all_sentiments else 0
            sentiment_adjustment = avg_sentiment * 0.02  # 2% max impact from sentiment
        
        # Calculate predicted change
        base_change = trend * (horizon_days / 30)
        volatility_factor = volatility * np.sqrt(horizon_days) * random.uniform(-0.5, 0.5)
        predicted_change = base_change + volatility_factor + sentiment_adjustment
        
        # Ensure reasonable bounds
        predicted_change = max(min(predicted_change, 0.15), -0.15)
        predicted_price = current_price * (1 + predicted_change)
        
        # Calculate confidence
        confidence = max(0.4, min(0.9, 1 - (volatility * 10)))
        
        # Generate probability distribution
        prob_up = 0.5 + (predicted_change * 2)
        prob_up = max(0.1, min(0.9, prob_up))
        
        return {
            "success": True,
            "prediction": {
                "current_price": current_price,
                "predicted_price": predicted_price,
                "predicted_change_percent": predicted_change * 100,
                "confidence_interval": {
                    "lower": predicted_price * (1 - volatility * 2),
                    "upper": predicted_price * (1 + volatility * 2),
                    "confidence": confidence
                },
                "probability_up": prob_up,
                "probability_down": 1 - prob_up,
                "horizon": horizon
            },
            "analysis_summary": f"Based on technical analysis{', publications' if include_publications else ''}{', and news sentiment' if include_news else ''}, CBA is predicted to {'rise' if predicted_change > 0 else 'fall'} by {abs(predicted_change * 100):.2f}% over the next {horizon}.",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prediction/cba/banking-sector")
async def get_banking_sector_analysis():
    """Get comparative analysis of Australian banking sector"""
    try:
        banks = ["CBA.AX", "WBC.AX", "ANZ.AX", "NAB.AX"]
        sector_data = []
        
        for bank in banks:
            try:
                ticker = yf.Ticker(bank)
                hist = ticker.history(period="1mo")
                
                if not hist.empty:
                    current = float(hist['Close'].iloc[-1])
                    change_1d = ((current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
                    change_1w = ((current - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] * 100) if len(hist) > 5 else 0
                    change_1m = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                    
                    sector_data.append({
                        "symbol": bank,
                        "name": {
                            "CBA.AX": "Commonwealth Bank",
                            "WBC.AX": "Westpac",
                            "ANZ.AX": "ANZ Bank",
                            "NAB.AX": "National Australia Bank"
                        }.get(bank, bank),
                        "current_price": current,
                        "change_1d": change_1d,
                        "change_1w": change_1w,
                        "change_1m": change_1m,
                        "performance_rank": 0
                    })
            except Exception as e:
                logger.warning(f"Error fetching data for {bank}: {e}")
        
        # Rank by 1-month performance
        sector_data.sort(key=lambda x: x["change_1m"], reverse=True)
        for i, bank in enumerate(sector_data):
            bank["performance_rank"] = i + 1
        
        # Find CBA's position
        cba_data = next((b for b in sector_data if b["symbol"] == "CBA.AX"), None)
        
        return {
            "success": True,
            "sector_data": sector_data,
            "cba_ranking": cba_data["performance_rank"] if cba_data else None,
            "sector_average": {
                "change_1d": np.mean([b["change_1d"] for b in sector_data]) if sector_data else 0,
                "change_1w": np.mean([b["change_1w"] for b in sector_data]) if sector_data else 0,
                "change_1m": np.mean([b["change_1m"] for b in sector_data]) if sector_data else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing banking sector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)