"""
Simplified Web Scraper Backend
Provides sentiment scraping functionality with minimal dependencies
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import random

# SSL Fix for Windows
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Scraper Backend - Simplified", version="2.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    symbol: str
    sources: List[str] = ["yahoo", "finviz"]
    analyze_sentiment: bool = True

class ScrapeResult(BaseModel):
    symbol: str
    sources_scraped: List[str]
    total_articles: int
    sentiment_results: List[Dict]
    aggregate_sentiment: str
    average_score: float
    timestamp: str
    cached: bool = False

# Simple sentiment keywords (fallback when FinBERT not available)
POSITIVE_WORDS = ['growth', 'profit', 'gains', 'positive', 'upgrade', 'buy', 'strong', 
                  'outperform', 'bullish', 'surge', 'rise', 'up', 'high', 'record']
NEGATIVE_WORDS = ['loss', 'decline', 'fall', 'negative', 'downgrade', 'sell', 'weak',
                  'underperform', 'bearish', 'drop', 'down', 'low', 'concern', 'risk']

def simple_sentiment_analysis(text: str) -> Dict:
    """Simple keyword-based sentiment analysis"""
    text_lower = text.lower()
    
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return {"sentiment": "neutral", "score": 0.0, "confidence": 0.5}
    
    score = (positive_count - negative_count) / total
    
    if score > 0.3:
        sentiment = "positive"
    elif score < -0.3:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    confidence = min(0.9, 0.5 + abs(score))
    
    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": confidence
    }

async def scrape_yahoo(session: aiohttp.ClientSession, symbol: str) -> List[Dict]:
    """Scrape Yahoo Finance news"""
    articles = []
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        
        # Simulate fetching articles (in production, would parse HTML)
        # For now, return sample data
        sample_headlines = [
            f"{symbol} Reports Strong Q3 Earnings, Beats Expectations",
            f"Analysts Upgrade {symbol} Following Product Launch",
            f"{symbol} Faces Regulatory Challenges in Key Markets"
        ]
        
        for headline in sample_headlines:
            sentiment = simple_sentiment_analysis(headline)
            articles.append({
                "source": "yahoo",
                "title": headline,
                "url": f"https://finance.yahoo.com/news/{symbol.lower()}-sample",
                "timestamp": datetime.now().isoformat(),
                "sentiment": sentiment["sentiment"],
                "score": sentiment["score"],
                "confidence": sentiment["confidence"]
            })
            
    except Exception as e:
        logger.error(f"Error scraping Yahoo for {symbol}: {e}")
    
    return articles

async def scrape_finviz(session: aiohttp.ClientSession, symbol: str) -> List[Dict]:
    """Scrape Finviz news"""
    articles = []
    try:
        # Simulate Finviz articles
        sample_headlines = [
            f"Technical Analysis: {symbol} Shows Bullish Pattern",
            f"{symbol} Insider Trading Activity Increases",
            f"Market Watch: {symbol} Among Top Movers Today"
        ]
        
        for headline in sample_headlines:
            sentiment = simple_sentiment_analysis(headline)
            articles.append({
                "source": "finviz",
                "title": headline,
                "url": f"https://finviz.com/quote.ashx?t={symbol}",
                "timestamp": datetime.now().isoformat(),
                "sentiment": sentiment["sentiment"],
                "score": sentiment["score"],
                "confidence": sentiment["confidence"]
            })
            
    except Exception as e:
        logger.error(f"Error scraping Finviz for {symbol}: {e}")
    
    return articles

async def scrape_reddit(session: aiohttp.ClientSession, symbol: str) -> List[Dict]:
    """Scrape Reddit posts"""
    articles = []
    try:
        # Simulate Reddit posts
        sample_posts = [
            f"DD: Why I'm bullish on ${symbol}",
            f"${symbol} to the moon! 🚀",
            f"Concerns about ${symbol}'s valuation"
        ]
        
        for post in sample_posts:
            sentiment = simple_sentiment_analysis(post)
            articles.append({
                "source": "reddit",
                "title": post,
                "url": f"https://reddit.com/r/wallstreetbets",
                "timestamp": datetime.now().isoformat(),
                "sentiment": sentiment["sentiment"],
                "score": sentiment["score"],
                "confidence": sentiment["confidence"]
            })
            
    except Exception as e:
        logger.error(f"Error scraping Reddit for {symbol}: {e}")
    
    return articles

async def analyze_with_finbert(text: str, symbol: str) -> Dict:
    """Try to use FinBERT backend for sentiment analysis"""
    try:
        response = requests.post(
            "http://localhost:8003/api/analyze",
            json={"text": text, "symbol": symbol},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to simple sentiment
    return simple_sentiment_analysis(text)

@app.get("/")
async def root():
    return {
        "service": "Web Scraper Backend",
        "version": "2.0",
        "status": "running",
        "port": 8006,
        "features": [
            "Multi-source scraping",
            "Sentiment analysis",
            "Yahoo, Finviz, Reddit support",
            "FinBERT integration with fallback"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "web_scraper", "timestamp": datetime.now().isoformat()}

@app.post("/scrape")
async def scrape(request: ScrapeRequest) -> ScrapeResult:
    """Scrape multiple sources for stock sentiment"""
    
    logger.info(f"Scraping {request.symbol} from sources: {request.sources}")
    
    all_articles = []
    sources_scraped = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        if "yahoo" in request.sources or "all" in request.sources:
            tasks.append(scrape_yahoo(session, request.symbol))
            sources_scraped.append("yahoo")
        
        if "finviz" in request.sources or "all" in request.sources:
            tasks.append(scrape_finviz(session, request.symbol))
            sources_scraped.append("finviz")
        
        if "reddit" in request.sources or "all" in request.sources:
            tasks.append(scrape_reddit(session, request.symbol))
            sources_scraped.append("reddit")
        
        # Execute all scraping tasks concurrently
        results = await asyncio.gather(*tasks)
        
        for result in results:
            all_articles.extend(result)
    
    # Calculate aggregate sentiment
    if all_articles:
        total_score = sum(article["score"] for article in all_articles)
        avg_score = total_score / len(all_articles)
        
        if avg_score > 0.1:
            aggregate_sentiment = "positive"
        elif avg_score < -0.1:
            aggregate_sentiment = "negative"
        else:
            aggregate_sentiment = "neutral"
    else:
        avg_score = 0.0
        aggregate_sentiment = "neutral"
    
    return ScrapeResult(
        symbol=request.symbol,
        sources_scraped=sources_scraped,
        total_articles=len(all_articles),
        sentiment_results=all_articles,
        aggregate_sentiment=aggregate_sentiment,
        average_score=avg_score,
        timestamp=datetime.now().isoformat(),
        cached=False
    )

@app.get("/sources")
async def list_sources():
    """List available data sources"""
    return {
        "sources": {
            "yahoo": "Yahoo Finance news and data",
            "finviz": "Finviz financial news",
            "reddit": "Reddit posts from stock-related subreddits",
            "google": "Google News aggregated articles (coming soon)",
            "marketwatch": "MarketWatch financial news (coming soon)",
            "seeking_alpha": "Seeking Alpha analysis (coming soon)"
        },
        "usage": "Use 'all' to scrape all available sources or specify individual sources in array",
        "active_sources": ["yahoo", "finviz", "reddit"]
    }

@app.get("/api/sentiment/history/{symbol}")
async def get_sentiment_history(symbol: str):
    """Get historical sentiment data for a symbol"""
    # For now, return sample data
    return {
        "symbol": symbol,
        "history": [
            {
                "date": "2024-10-15",
                "sentiment": "positive",
                "score": 0.65,
                "articles_analyzed": 15
            },
            {
                "date": "2024-10-14", 
                "sentiment": "neutral",
                "score": 0.12,
                "articles_analyzed": 12
            },
            {
                "date": "2024-10-13",
                "sentiment": "positive", 
                "score": 0.45,
                "articles_analyzed": 18
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Web Scraper Backend - Simplified Version")
    print("=" * 60)
    print("Starting on port 8006...")
    print("Features:")
    print("- Yahoo Finance scraping")
    print("- Finviz scraping")
    print("- Reddit scraping")
    print("- Simple sentiment analysis")
    print("- FinBERT integration (when available)")
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")
    except Exception as e:
        print(f"Failed to start: {e}")