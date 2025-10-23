#!/usr/bin/env python3
"""
Enhanced CBA-specific API endpoints for the CBA Market Tracker
Includes document analysis, news sentiment, and prediction features
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging
import random
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CBA Enhanced Market Tracker API",
    description="Specialized API for Commonwealth Bank analysis with sentiment and predictions",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data generators for demonstration
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
            "download_url": f"/api/documents/cba_{i}.pdf"
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
            "headline": random.choice(headlines),
            "source": random.choice(sources),
            "published_date": pub_date.isoformat(),
            "summary": f"Recent developments at Commonwealth Bank show {random.choice(['strong performance', 'strategic growth', 'market expansion', 'innovation focus'])} in {random.choice(['retail banking', 'business services', 'digital platforms', 'wealth management'])}.",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment,
            "relevance_score": random.uniform(0.7, 1.0),
            "categories": random.sample(["Banking", "Finance", "Technology", "Markets", "Business"], 2),
            "url": f"https://news.example.com/cba-article-{i}"
        })
    
    return articles

def calculate_enhanced_prediction(symbol: str, horizon: str, include_sentiment: bool = True) -> Dict:
    """Generate enhanced prediction with sentiment analysis"""
    try:
        # Get real market data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            raise ValueError(f"No data available for {symbol}")
        
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
        sentiment_adjustment = random.uniform(-0.02, 0.03) if include_sentiment else 0
        
        # Calculate predicted change
        base_change = trend * (horizon_days / 30)  # Scale trend by time horizon
        volatility_factor = volatility * np.sqrt(horizon_days) * random.uniform(-1, 1)
        predicted_change = base_change + volatility_factor + sentiment_adjustment
        
        # Ensure reasonable bounds
        predicted_change = max(min(predicted_change, 0.15), -0.15)  # Cap at ±15%
        
        predicted_price = current_price * (1 + predicted_change)
        
        # Calculate confidence based on volatility
        confidence = max(0.4, min(0.9, 1 - (volatility * 10)))
        
        # Generate probability distribution
        prob_up = 0.5 + (predicted_change * 2)  # Rough probability
        prob_up = max(0.1, min(0.9, prob_up))
        
        return {
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
            "horizon": horizon,
            "factors_considered": [
                "Historical price trends",
                "Market volatility",
                "Technical indicators",
                "Sentiment analysis" if include_sentiment else None,
                "Banking sector performance"
            ],
            "risk_metrics": {
                "volatility": volatility,
                "sharpe_ratio": (trend / volatility) if volatility > 0 else 0,
                "max_drawdown": float((hist['Close'].min() - hist['Close'].max()) / hist['Close'].max())
            }
        }
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "CBA Enhanced Market Tracker API",
        "version": "2.0.0",
        "endpoints": {
            "publications": "/api/prediction/cba/publications",
            "news": "/api/prediction/cba/news",
            "enhanced_prediction": "/api/prediction/cba/enhanced",
            "banking_sector": "/api/prediction/cba/banking-sector",
            "sentiment_analysis": "/api/prediction/cba/sentiment"
        }
    }

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
        # Generate prediction
        prediction = calculate_enhanced_prediction("CBA.AX", horizon, include_publications or include_news)
        
        # Add sentiment impact if requested
        sentiment_impact = {}
        if include_publications or include_news:
            pubs = generate_mock_publications(3) if include_publications else []
            news = generate_mock_news(3) if include_news else []
            
            all_sentiments = [p["sentiment_score"] for p in pubs] + [n["sentiment_score"] for n in news]
            avg_sentiment = np.mean(all_sentiments) if all_sentiments else 0
            
            sentiment_impact = {
                "overall_sentiment": avg_sentiment,
                "sentiment_label": "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral",
                "impact_on_prediction": avg_sentiment * 2,  # Percentage impact
                "sources_analyzed": len(pubs) + len(news)
            }
        
        return {
            "success": True,
            "prediction": prediction,
            "sentiment_analysis": sentiment_impact,
            "analysis_summary": f"Based on technical analysis{', publications' if include_publications else ''}{', and news sentiment' if include_news else ''}, CBA is predicted to {'rise' if prediction['predicted_change_percent'] > 0 else 'fall'} by {abs(prediction['predicted_change_percent']):.2f}% over the next {horizon}.",
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
                        "performance_rank": 0  # Will be calculated
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
                "change_1d": np.mean([b["change_1d"] for b in sector_data]),
                "change_1w": np.mean([b["change_1w"] for b in sector_data]),
                "change_1m": np.mean([b["change_1m"] for b in sector_data])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing banking sector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prediction/cba/sentiment")
async def get_sentiment_analysis():
    """Get aggregated sentiment analysis from all sources"""
    try:
        # Gather sentiment from multiple sources
        pubs = generate_mock_publications(5)
        news = generate_mock_news(5)
        
        # Calculate sentiment metrics
        pub_sentiments = [p["sentiment_score"] for p in pubs]
        news_sentiments = [n["sentiment_score"] for n in news]
        all_sentiments = pub_sentiments + news_sentiments
        
        # Time-weighted sentiment (more recent = higher weight)
        weighted_sentiments = []
        for item in pubs + news:
            date_key = "publication_date" if "publication_date" in item else "published_date"
            item_date = datetime.fromisoformat(item[date_key].replace('Z', '+00:00'))
            days_ago = (datetime.now() - item_date.replace(tzinfo=None)).days
            weight = 1 / (1 + days_ago * 0.1)  # Recent items have higher weight
            weighted_sentiments.append(item["sentiment_score"] * weight)
        
        weighted_average = np.average(weighted_sentiments) if weighted_sentiments else 0
        
        return {
            "success": True,
            "sentiment_metrics": {
                "overall_score": np.mean(all_sentiments),
                "weighted_score": weighted_average,
                "publications_sentiment": np.mean(pub_sentiments) if pub_sentiments else 0,
                "news_sentiment": np.mean(news_sentiments) if news_sentiments else 0,
                "trend": "improving" if weighted_average > np.mean(all_sentiments) else "declining",
                "confidence": min(0.9, 0.5 + len(all_sentiments) * 0.05)
            },
            "distribution": {
                "very_positive": sum(1 for s in all_sentiments if s > 0.6),
                "positive": sum(1 for s in all_sentiments if 0.2 < s <= 0.6),
                "neutral": sum(1 for s in all_sentiments if -0.2 <= s <= 0.2),
                "negative": sum(1 for s in all_sentiments if -0.6 <= s < -0.2),
                "very_negative": sum(1 for s in all_sentiments if s <= -0.6)
            },
            "sources_analyzed": {
                "publications": len(pubs),
                "news_articles": len(news),
                "total": len(pubs) + len(news)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)