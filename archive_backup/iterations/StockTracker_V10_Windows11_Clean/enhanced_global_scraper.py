"""
Enhanced Global Sentiment Web Scraper
Captures broader sentiment from:
- Global political events
- Wars and conflicts
- Economic indicators
- Government reports
- Market news
- Central bank announcements
- Commodity markets
- Cryptocurrency sentiment
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import aiohttp
import asyncio
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import quote
import logging
import sqlite3
from contextlib import contextmanager
import hashlib
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Global Sentiment Scraper", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite cache setup
DB_PATH = "sentiment_cache.db"

def init_db():
    """Initialize SQLite database for caching"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_cache (
            cache_key TEXT PRIMARY KEY,
            data TEXT,
            timestamp INTEGER,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

class ScrapeRequest(BaseModel):
    symbol: Optional[str] = None
    sources: List[str] = []
    include_global: bool = True
    cache_minutes: int = 15

class Article(BaseModel):
    title: str
    url: str
    source: str
    published: Optional[str]
    summary: Optional[str]
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    category: str = "market"  # market, politics, economic, war, government, commodity, crypto
    relevance_score: float = 1.0
    impact: str = "medium"  # low, medium, high, critical

class ScrapeResponse(BaseModel):
    symbol: Optional[str]
    articles: List[Article]
    sources_checked: List[str]
    global_sentiment: Dict[str, Any]
    timestamp: str
    cache_hit: bool = False

# Enhanced sentiment keywords for different categories
SENTIMENT_KEYWORDS = {
    "positive": {
        "market": ["bull", "rally", "gains", "surge", "profit", "growth", "recover", "breakthrough", "record high"],
        "politics": ["agreement", "peace", "cooperation", "stability", "reform", "progress", "unity", "diplomatic success"],
        "economic": ["expansion", "job growth", "inflation cooling", "GDP growth", "consumer confidence", "stimulus"],
        "government": ["approval", "stimulus", "support", "investment", "infrastructure", "tax cut", "deregulation"]
    },
    "negative": {
        "market": ["bear", "crash", "plunge", "loss", "decline", "recession", "default", "bankruptcy", "bubble"],
        "politics": ["conflict", "sanction", "tension", "crisis", "instability", "coup", "protest", "corruption"],
        "economic": ["recession", "unemployment", "inflation", "stagflation", "deficit", "debt crisis", "downturn"],
        "war": ["attack", "invasion", "escalation", "casualties", "bombing", "military", "warfare", "nuclear"],
        "government": ["shutdown", "deficit", "debt ceiling", "impeachment", "scandal", "investigation", "regulation"]
    }
}

# Global news sources configuration
GLOBAL_SOURCES = {
    "reuters_global": {
        "url": "https://www.reuters.com/world/",
        "type": "scrape",
        "category": "politics"
    },
    "bbc_world": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "type": "rss",
        "category": "politics"
    },
    "economist_feed": {
        "url": "https://www.economist.com/international/rss.xml",
        "type": "rss",
        "category": "economic"
    },
    "federal_reserve": {
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "type": "rss",
        "category": "government"
    },
    "ecb_news": {
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "type": "scrape",
        "category": "government"
    },
    "imf_news": {
        "url": "https://www.imf.org/en/News/RSS",
        "type": "rss",
        "category": "economic"
    },
    "world_bank": {
        "url": "https://www.worldbank.org/en/news/rss.xml",
        "type": "rss",
        "category": "economic"
    },
    "bloomberg_markets": {
        "url": "https://www.bloomberg.com/markets",
        "type": "scrape",
        "category": "market"
    },
    "ft_world": {
        "url": "https://www.ft.com/world?format=rss",
        "type": "rss",
        "category": "economic"
    },
    "un_news": {
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "type": "rss",
        "category": "politics"
    },
    "commodity_news": {
        "url": "https://www.investing.com/commodities/",
        "type": "scrape",
        "category": "commodity"
    },
    "crypto_panic": {
        "url": "https://cryptopanic.com/api/v1/posts/?auth_token=fake&public=true",
        "type": "api",
        "category": "crypto"
    }
}

# Market-specific sources (existing ones enhanced)
MARKET_SOURCES = {
    "yahoo": {
        "base_url": "https://finance.yahoo.com/quote/{}/news",
        "category": "market"
    },
    "finviz": {
        "base_url": "https://finviz.com/quote.ashx?t={}",
        "category": "market"
    },
    "marketwatch": {
        "base_url": "https://www.marketwatch.com/investing/stock/{}",
        "category": "market"
    },
    "seeking_alpha": {
        "base_url": "https://seekingalpha.com/symbol/{}/news",
        "category": "market"
    },
    "benzinga": {
        "base_url": "https://www.benzinga.com/quote/{}",
        "category": "market"
    },
    "reddit_wsb": {
        "base_url": "https://www.reddit.com/r/wallstreetbets/search.json?q={}&sort=new&limit=25",
        "category": "market"
    },
    "reddit_stocks": {
        "base_url": "https://www.reddit.com/r/stocks/search.json?q={}&sort=new&limit=25",
        "category": "market"
    }
}

def calculate_sentiment(text: str, category: str = "market") -> tuple[str, float]:
    """Enhanced sentiment calculation with category-specific keywords"""
    if not text:
        return "neutral", 0.0
    
    text_lower = text.lower()
    positive_score = 0
    negative_score = 0
    
    # Check category-specific keywords
    for cat, keywords in SENTIMENT_KEYWORDS["positive"].items():
        if cat == category or category == "market":
            for keyword in keywords:
                if keyword in text_lower:
                    positive_score += 1.5 if cat == category else 1.0
    
    for cat, keywords in SENTIMENT_KEYWORDS["negative"].items():
        if cat == category or category == "market":
            for keyword in keywords:
                if keyword in text_lower:
                    negative_score += 1.5 if cat == category else 1.0
    
    # Additional pattern matching for critical events
    critical_patterns = [
        r"\bwar\s+(declared|breaks\s+out)\b",
        r"\bmarket\s+crash",
        r"\bemergency\s+rate\s+cut",
        r"\bdefault\s+on\s+debt",
        r"\bnuclear\s+threat"
    ]
    
    for pattern in critical_patterns:
        if re.search(pattern, text_lower):
            negative_score += 3
    
    # Calculate final sentiment
    if positive_score > negative_score:
        sentiment = "positive"
        score = min(1.0, positive_score / 10)
    elif negative_score > positive_score:
        sentiment = "negative"
        score = max(-1.0, -negative_score / 10)
    else:
        sentiment = "neutral"
        score = 0.0
    
    return sentiment, score

def calculate_impact(text: str, category: str) -> str:
    """Calculate the potential market impact of news"""
    impact_keywords = {
        "critical": ["war", "crash", "collapse", "default", "nuclear", "invasion", "pandemic"],
        "high": ["fed", "ecb", "interest rate", "gdp", "inflation", "unemployment", "earnings"],
        "medium": ["trade", "tariff", "regulation", "merger", "acquisition", "ipo"],
        "low": ["forecast", "analyst", "upgrade", "downgrade", "target"]
    }
    
    text_lower = text.lower()
    
    for level, keywords in impact_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return level
    
    return "medium"

def get_cache_key(source: str, params: dict) -> str:
    """Generate cache key"""
    param_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(f"{source}:{param_str}".encode()).hexdigest()

def get_cached_data(cache_key: str, max_age_minutes: int = 15) -> Optional[dict]:
    """Get cached data if still valid"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT data, timestamp FROM sentiment_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        
        if row:
            data, timestamp = row
            if time.time() - timestamp < (max_age_minutes * 60):
                return json.loads(data)
    return None

def save_to_cache(cache_key: str, data: dict, source: str):
    """Save data to cache"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO sentiment_cache 
               (cache_key, data, timestamp, source) VALUES (?, ?, ?, ?)""",
            (cache_key, json.dumps(data), int(time.time()), source)
        )
        conn.commit()

async def fetch_rss_feed(url: str, category: str) -> List[Article]:
    """Fetch and parse RSS feeds"""
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # Limit to 10 entries
            sentiment, score = calculate_sentiment(
                f"{entry.get('title', '')} {entry.get('summary', '')}", 
                category
            )
            impact = calculate_impact(
                f"{entry.get('title', '')} {entry.get('summary', '')}", 
                category
            )
            
            article = Article(
                title=entry.get('title', 'No title'),
                url=entry.get('link', ''),
                source=feed.feed.get('title', url),
                published=entry.get('published', ''),
                summary=entry.get('summary', '')[:500] if entry.get('summary') else None,
                sentiment=sentiment,
                sentiment_score=score,
                category=category,
                impact=impact
            )
            articles.append(article)
    except Exception as e:
        logger.error(f"Error fetching RSS feed {url}: {e}")
    
    return articles

async def scrape_yahoo_finance(session: aiohttp.ClientSession, symbol: str) -> List[Article]:
    """Scrape Yahoo Finance for stock-specific news"""
    articles = []
    url = MARKET_SOURCES["yahoo"]["base_url"].format(symbol)
    
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find news items
                news_items = soup.find_all('div', {'class': re.compile('news-item|StreamDataList')})
                
                for item in news_items[:10]:
                    title_elem = item.find('a', {'class': re.compile('title|headline')})
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"https://finance.yahoo.com{link}"
                        
                        summary = item.find('p')
                        summary_text = summary.get_text(strip=True) if summary else ""
                        
                        sentiment, score = calculate_sentiment(f"{title} {summary_text}", "market")
                        impact = calculate_impact(f"{title} {summary_text}", "market")
                        
                        article = Article(
                            title=title,
                            url=link,
                            source="Yahoo Finance",
                            published=datetime.now().isoformat(),
                            summary=summary_text[:500],
                            sentiment=sentiment,
                            sentiment_score=score,
                            category="market",
                            impact=impact
                        )
                        articles.append(article)
                        
    except Exception as e:
        logger.error(f"Error scraping Yahoo Finance: {e}")
    
    return articles

async def scrape_finviz(session: aiohttp.ClientSession, symbol: str) -> List[Article]:
    """Scrape Finviz for technical and news data"""
    articles = []
    url = MARKET_SOURCES["finviz"]["base_url"].format(symbol)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_table = soup.find('table', {'class': 'fullview-news-outer'})
                if news_table:
                    rows = news_table.find_all('tr')
                    
                    for row in rows[:10]:
                        link_cell = row.find('a', {'class': 'tab-link-news'})
                        if link_cell:
                            title = link_cell.get_text(strip=True)
                            link = link_cell.get('href', '')
                            
                            sentiment, score = calculate_sentiment(title, "market")
                            impact = calculate_impact(title, "market")
                            
                            article = Article(
                                title=title,
                                url=link,
                                source="Finviz",
                                published=datetime.now().isoformat(),
                                sentiment=sentiment,
                                sentiment_score=score,
                                category="market",
                                impact=impact
                            )
                            articles.append(article)
                            
    except Exception as e:
        logger.error(f"Error scraping Finviz: {e}")
    
    return articles

async def scrape_reddit(session: aiohttp.ClientSession, symbol: str, subreddit: str = "wallstreetbets") -> List[Article]:
    """Scrape Reddit for social sentiment"""
    articles = []
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": symbol,
        "sort": "new",
        "limit": 10,
        "t": "week"
    }
    
    try:
        headers = {'User-Agent': 'StockTracker/1.0'}
        async with session.get(url, params=params, headers=headers, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')[:500]
                    
                    sentiment, score = calculate_sentiment(f"{title} {selftext}", "market")
                    
                    article = Article(
                        title=title,
                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                        source=f"Reddit r/{subreddit}",
                        published=datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        summary=selftext,
                        sentiment=sentiment,
                        sentiment_score=score,
                        category="market",
                        impact="low"  # Reddit posts typically have lower market impact
                    )
                    articles.append(article)
                    
    except Exception as e:
        logger.error(f"Error scraping Reddit: {e}")
    
    return articles

async def fetch_global_sentiment(session: aiohttp.ClientSession, include_sources: List[str]) -> List[Article]:
    """Fetch global news and sentiment from various sources"""
    all_articles = []
    tasks = []
    
    for source_name, config in GLOBAL_SOURCES.items():
        if include_sources and source_name not in include_sources:
            continue
            
        if config["type"] == "rss":
            tasks.append(fetch_rss_feed(config["url"], config["category"]))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_articles.extend(result)
    
    return all_articles

async def scrape_all_sources(symbol: Optional[str], sources: List[str], include_global: bool) -> ScrapeResponse:
    """Main scraping function that coordinates all sources"""
    async with aiohttp.ClientSession() as session:
        all_articles = []
        sources_checked = []
        
        # Fetch stock-specific news if symbol provided
        if symbol:
            tasks = []
            
            if not sources or "yahoo" in sources:
                tasks.append(scrape_yahoo_finance(session, symbol))
                sources_checked.append("yahoo")
            
            if not sources or "finviz" in sources:
                tasks.append(scrape_finviz(session, symbol))
                sources_checked.append("finviz")
            
            if not sources or "reddit" in sources:
                tasks.append(scrape_reddit(session, symbol))
                sources_checked.append("reddit_wsb")
                tasks.append(scrape_reddit(session, symbol, "stocks"))
                sources_checked.append("reddit_stocks")
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
        
        # Fetch global sentiment if requested
        if include_global:
            global_articles = await fetch_global_sentiment(session, sources)
            all_articles.extend(global_articles)
            sources_checked.extend([s for s in GLOBAL_SOURCES.keys() if not sources or s in sources])
        
        # Calculate aggregate sentiment metrics
        total_articles = len(all_articles)
        if total_articles > 0:
            positive_count = sum(1 for a in all_articles if a.sentiment == "positive")
            negative_count = sum(1 for a in all_articles if a.sentiment == "negative")
            neutral_count = sum(1 for a in all_articles if a.sentiment == "neutral")
            
            avg_sentiment_score = sum(a.sentiment_score for a in all_articles) / total_articles
            
            # Group by category
            category_sentiment = {}
            for article in all_articles:
                if article.category not in category_sentiment:
                    category_sentiment[article.category] = {
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0,
                        "articles": []
                    }
                category_sentiment[article.category][article.sentiment] += 1
                category_sentiment[article.category]["articles"].append(article)
            
            # Calculate impact distribution
            impact_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for article in all_articles:
                impact_dist[article.impact] += 1
            
            global_sentiment = {
                "overall_sentiment": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral",
                "sentiment_score": avg_sentiment_score,
                "positive_ratio": positive_count / total_articles,
                "negative_ratio": negative_count / total_articles,
                "neutral_ratio": neutral_count / total_articles,
                "total_articles": total_articles,
                "category_breakdown": {
                    cat: {
                        "positive": data["positive"],
                        "negative": data["negative"],
                        "neutral": data["neutral"],
                        "total": sum([data["positive"], data["negative"], data["neutral"]])
                    }
                    for cat, data in category_sentiment.items()
                },
                "impact_distribution": impact_dist,
                "market_risk_level": "high" if impact_dist["critical"] > 0 or impact_dist["high"] > total_articles * 0.3 else "medium" if impact_dist["high"] > total_articles * 0.1 else "low"
            }
        else:
            global_sentiment = {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 1.0,
                "total_articles": 0,
                "category_breakdown": {},
                "impact_distribution": {},
                "market_risk_level": "unknown"
            }
        
        return ScrapeResponse(
            symbol=symbol,
            articles=all_articles[:50],  # Limit to 50 most recent articles
            sources_checked=sources_checked,
            global_sentiment=global_sentiment,
            timestamp=datetime.now().isoformat()
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enhanced Global Sentiment Scraper",
        "version": "2.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/sources",
            "/scrape",
            "/global-sentiment",
            "/market-risk",
            "/clear-cache"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced Global Sentiment Scraper",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sources")
async def list_sources():
    """List all available news sources"""
    return {
        "market_sources": {
            name: {
                "description": f"{name.title()} - Market news and analysis",
                "category": config["category"]
            }
            for name, config in MARKET_SOURCES.items()
        },
        "global_sources": {
            name: {
                "description": name.replace("_", " ").title(),
                "category": config["category"],
                "type": config["type"]
            }
            for name, config in GLOBAL_SOURCES.items()
        },
        "categories": [
            "market", "politics", "economic", "war", 
            "government", "commodity", "crypto"
        ]
    }

@app.post("/scrape")
async def scrape_sentiment(request: ScrapeRequest):
    """Main scraping endpoint with caching"""
    try:
        # Check cache first
        cache_key = get_cache_key("scrape", {
            "symbol": request.symbol,
            "sources": request.sources,
            "include_global": request.include_global
        })
        
        cached_data = get_cached_data(cache_key, request.cache_minutes)
        if cached_data:
            response = ScrapeResponse(**cached_data)
            response.cache_hit = True
            return response
        
        # Fetch fresh data
        response = await scrape_all_sources(
            request.symbol,
            request.sources,
            request.include_global
        )
        
        # Save to cache
        save_to_cache(cache_key, response.dict(), "scrape")
        
        return response
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/global-sentiment")
async def get_global_sentiment():
    """Get only global sentiment without stock-specific data"""
    request = ScrapeRequest(
        symbol=None,
        sources=[],
        include_global=True
    )
    return await scrape_sentiment(request)

@app.get("/market-risk")
async def get_market_risk():
    """Analyze current market risk based on global sentiment"""
    response = await get_global_sentiment()
    
    risk_factors = []
    risk_score = 0.0
    
    # Analyze sentiment distribution
    if response.global_sentiment["negative_ratio"] > 0.6:
        risk_factors.append("High negative sentiment (>60%)")
        risk_score += 0.3
    
    # Analyze impact distribution
    impact_dist = response.global_sentiment.get("impact_distribution", {})
    if impact_dist.get("critical", 0) > 0:
        risk_factors.append(f"Critical events detected: {impact_dist['critical']}")
        risk_score += 0.4
    
    if impact_dist.get("high", 0) > response.global_sentiment["total_articles"] * 0.3:
        risk_factors.append("High impact events exceed 30% of news")
        risk_score += 0.2
    
    # Analyze category-specific risks
    category_breakdown = response.global_sentiment.get("category_breakdown", {})
    
    if "war" in category_breakdown:
        war_sentiment = category_breakdown["war"]
        if war_sentiment.get("negative", 0) > war_sentiment.get("total", 1) * 0.5:
            risk_factors.append("Elevated geopolitical tensions")
            risk_score += 0.15
    
    if "economic" in category_breakdown:
        econ_sentiment = category_breakdown["economic"]
        if econ_sentiment.get("negative", 0) > econ_sentiment.get("total", 1) * 0.5:
            risk_factors.append("Negative economic indicators")
            risk_score += 0.15
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "CRITICAL"
        recommendation = "Consider defensive positions and risk hedging"
    elif risk_score >= 0.5:
        risk_level = "HIGH"
        recommendation = "Monitor closely and reduce exposure to volatile assets"
    elif risk_score >= 0.3:
        risk_level = "MODERATE"
        recommendation = "Maintain balanced portfolio with stop losses"
    else:
        risk_level = "LOW"
        recommendation = "Normal market conditions, follow standard strategy"
    
    return {
        "risk_level": risk_level,
        "risk_score": min(1.0, risk_score),
        "risk_factors": risk_factors,
        "recommendation": recommendation,
        "global_sentiment": response.global_sentiment,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/clear-cache")
async def clear_cache():
    """Clear sentiment cache"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sentiment_cache WHERE timestamp < ?", 
                         (int(time.time()) - 3600,))  # Clear entries older than 1 hour
            deleted = cursor.rowcount
            conn.commit()
        
        return {
            "status": "success",
            "deleted_entries": deleted,
            "message": f"Cleared {deleted} cached entries older than 1 hour"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/{symbol}")
async def test_scraping(symbol: str):
    """Test endpoint for debugging"""
    request = ScrapeRequest(
        symbol=symbol,
        sources=[],
        include_global=True,
        cache_minutes=0  # Bypass cache for testing
    )
    return await scrape_sentiment(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)