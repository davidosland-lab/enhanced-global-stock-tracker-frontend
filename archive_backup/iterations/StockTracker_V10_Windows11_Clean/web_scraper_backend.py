"""
Web Scraper Backend - Retrieves sentiment data, news, and documents for stocks
Integrates with FinBERT for sentiment analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import logging
import json
import sqlite3
import hashlib
import re
import uvicorn
import feedparser
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Scraper for Stock Sentiment")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for caching scraped data
CACHE_DB = "scraped_data_cache.db"

def init_database():
    """Initialize SQLite database for caching scraped data"""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_cache (
            cache_key TEXT PRIMARY KEY,
            symbol TEXT,
            source TEXT,
            data TEXT,
            sentiment_score REAL,
            analyzed BOOLEAN DEFAULT 0,
            timestamp REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_symbol_source 
        ON scraped_cache(symbol, source)
    """)
    
    conn.commit()
    conn.close()
    logger.info("Scraper cache database initialized")

# Initialize database on startup
init_database()

class ScrapeRequest(BaseModel):
    symbol: str
    sources: Optional[List[str]] = ["all"]  # news, reddit, twitter, sec, yahoo
    max_items: Optional[int] = 10
    analyze_sentiment: Optional[bool] = True

class ScrapedItem(BaseModel):
    title: str
    content: str
    source: str
    url: Optional[str]
    date: Optional[str]
    sentiment: Optional[Dict] = None

class WebScraper:
    """Multi-source web scraper for stock information"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_yahoo_finance_news(self, symbol: str, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape news from Yahoo Finance"""
        items = []
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:max_items] if hasattr(ticker, 'news') else []
            
            for article in news:
                item = ScrapedItem(
                    title=article.get('title', ''),
                    content=article.get('summary', article.get('title', '')),
                    source='Yahoo Finance',
                    url=article.get('link', ''),
                    date=datetime.fromtimestamp(article.get('providerPublishTime', 0)).isoformat() if article.get('providerPublishTime') else None
                )
                items.append(item)
                
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance: {e}")
        
        return items
    
    async def scrape_finviz_news(self, symbol: str, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape news from Finviz"""
        items = []
        try:
            url = f"https://finviz.com/quote.ashx?t={symbol}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    news_table = soup.find('table', class_='fullview-news-outer')
                    if news_table:
                        rows = news_table.find_all('tr')[:max_items]
                        
                        for row in rows:
                            link = row.find('a', class_='tab-link-news')
                            if link:
                                date_td = row.find('td', align='right')
                                item = ScrapedItem(
                                    title=link.text.strip(),
                                    content=link.text.strip(),  # Finviz only shows titles
                                    source='Finviz',
                                    url=link.get('href', ''),
                                    date=date_td.text.strip() if date_td else None
                                )
                                items.append(item)
                                
        except Exception as e:
            logger.error(f"Error scraping Finviz: {e}")
        
        return items
    
    async def scrape_reddit_sentiment(self, symbol: str, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape Reddit posts mentioning the stock"""
        items = []
        try:
            # Using Reddit's JSON endpoint (no API key required for public data)
            subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
            
            for subreddit in subreddits[:2]:  # Limit to avoid rate limiting
                url = f"https://www.reddit.com/r/{subreddit}/search.json?q={symbol}&limit={max_items//2}&sort=new&restrict_sr=1"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            item = ScrapedItem(
                                title=post_data.get('title', ''),
                                content=post_data.get('selftext', post_data.get('title', '')),
                                source=f'Reddit r/{subreddit}',
                                url=f"https://reddit.com{post_data.get('permalink', '')}",
                                date=datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat()
                            )
                            items.append(item)
                            
                await asyncio.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
        
        return items
    
    async def scrape_seeking_alpha_news(self, symbol: str, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape news headlines from Seeking Alpha RSS"""
        items = []
        try:
            url = f"https://seekingalpha.com/symbol/{symbol}/news"
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for article elements
                    articles = soup.find_all('article', limit=max_items)
                    
                    for article in articles:
                        title_elem = article.find('h3') or article.find('a')
                        if title_elem:
                            item = ScrapedItem(
                                title=title_elem.text.strip(),
                                content=title_elem.text.strip(),
                                source='Seeking Alpha',
                                url='https://seekingalpha.com',
                                date=datetime.now().isoformat()
                            )
                            items.append(item)
                            
        except Exception as e:
            logger.error(f"Error scraping Seeking Alpha: {e}")
        
        return items
    
    async def scrape_google_news(self, symbol: str, company_name: str = None, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape Google News RSS feed"""
        items = []
        try:
            # Get company name if not provided
            if not company_name:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                company_name = info.get('longName', info.get('shortName', symbol))
            
            # Google News RSS URL
            query = quote(f"{symbol} {company_name} stock")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_items]:
                item = ScrapedItem(
                    title=entry.title,
                    content=BeautifulSoup(entry.summary, 'html.parser').text if hasattr(entry, 'summary') else entry.title,
                    source='Google News',
                    url=entry.link,
                    date=entry.published if hasattr(entry, 'published') else datetime.now().isoformat()
                )
                items.append(item)
                
        except Exception as e:
            logger.error(f"Error scraping Google News: {e}")
        
        return items
    
    async def scrape_marketwatch_news(self, symbol: str, max_items: int = 10) -> List[ScrapedItem]:
        """Scrape MarketWatch news"""
        items = []
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find news articles
                    articles = soup.find_all('div', class_='article__content', limit=max_items)
                    
                    for article in articles:
                        headline = article.find('h3', class_='article__headline')
                        if headline:
                            link = headline.find('a')
                            if link:
                                item = ScrapedItem(
                                    title=link.text.strip(),
                                    content=link.text.strip(),
                                    source='MarketWatch',
                                    url=f"https://www.marketwatch.com{link.get('href', '')}" if link.get('href', '').startswith('/') else link.get('href', ''),
                                    date=datetime.now().isoformat()
                                )
                                items.append(item)
                                
        except Exception as e:
            logger.error(f"Error scraping MarketWatch: {e}")
        
        return items

async def analyze_with_finbert(items: List[ScrapedItem]) -> List[ScrapedItem]:
    """Send scraped items to FinBERT for sentiment analysis"""
    analyzed_items = []
    
    try:
        # Connect to FinBERT backend
        async with aiohttp.ClientSession() as session:
            for item in items:
                try:
                    # Combine title and content for analysis
                    text_to_analyze = f"{item.title}. {item.content}"
                    
                    # Send to FinBERT
                    async with session.post(
                        'http://localhost:8003/api/sentiment/analyze',
                        json={'text': text_to_analyze[:2000]}  # Limit text length
                    ) as response:
                        if response.status == 200:
                            sentiment_data = await response.json()
                            item.sentiment = sentiment_data
                        else:
                            # Fallback to basic sentiment
                            item.sentiment = {
                                'sentiment': 'neutral',
                                'confidence': 0.5,
                                'method': 'fallback'
                            }
                    
                except Exception as e:
                    logger.error(f"Error analyzing item with FinBERT: {e}")
                    item.sentiment = {
                        'sentiment': 'neutral',
                        'confidence': 0.5,
                        'method': 'error'
                    }
                
                analyzed_items.append(item)
                
    except Exception as e:
        logger.error(f"Error connecting to FinBERT: {e}")
        return items  # Return unanalyzed items if FinBERT is unavailable
    
    return analyzed_items

def cache_scraped_data(symbol: str, source: str, items: List[ScrapedItem]):
    """Cache scraped data in SQLite"""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    for item in items:
        cache_key = hashlib.md5(f"{symbol}_{source}_{item.title}".encode()).hexdigest()
        sentiment_score = item.sentiment.get('confidence', 0) if item.sentiment else 0
        
        cursor.execute("""
            INSERT OR REPLACE INTO scraped_cache 
            (cache_key, symbol, source, data, sentiment_score, analyzed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cache_key, 
            symbol, 
            source,
            json.dumps(item.dict()),
            sentiment_score,
            1 if item.sentiment else 0,
            datetime.now().timestamp()
        ))
    
    conn.commit()
    conn.close()

def get_cached_data(symbol: str, max_age_hours: int = 24) -> List[ScrapedItem]:
    """Retrieve cached data if available and fresh"""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    min_timestamp = (datetime.now() - timedelta(hours=max_age_hours)).timestamp()
    
    cursor.execute("""
        SELECT data FROM scraped_cache 
        WHERE symbol = ? AND timestamp > ?
        ORDER BY timestamp DESC
    """, (symbol, min_timestamp))
    
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for row in rows:
        try:
            item_data = json.loads(row[0])
            items.append(ScrapedItem(**item_data))
        except:
            continue
    
    return items

@app.get("/")
async def root():
    return {
        "service": "Web Scraper for Stock Sentiment",
        "version": "1.0",
        "status": "operational",
        "endpoints": {
            "/scrape": "Scrape data for a stock symbol",
            "/cached/{symbol}": "Get cached data for a symbol",
            "/sources": "List available data sources"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "web_scraper", "port": 8006}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": "web_scraper", "port": 8006}

@app.post("/scrape")
async def scrape_stock_data(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape sentiment data and news for a stock symbol
    """
    try:
        all_items = []
        
        async with WebScraper() as scraper:
            # Determine which sources to scrape
            sources_to_scrape = request.sources
            if "all" in sources_to_scrape:
                sources_to_scrape = ["yahoo", "finviz", "reddit", "google", "marketwatch", "seeking_alpha"]
            
            # Scrape each source
            tasks = []
            
            if "yahoo" in sources_to_scrape:
                tasks.append(scraper.scrape_yahoo_finance_news(request.symbol, request.max_items))
            
            if "finviz" in sources_to_scrape:
                tasks.append(scraper.scrape_finviz_news(request.symbol, request.max_items))
            
            if "reddit" in sources_to_scrape:
                tasks.append(scraper.scrape_reddit_sentiment(request.symbol, request.max_items))
            
            if "google" in sources_to_scrape:
                tasks.append(scraper.scrape_google_news(request.symbol, None, request.max_items))
            
            if "marketwatch" in sources_to_scrape:
                tasks.append(scraper.scrape_marketwatch_news(request.symbol, request.max_items))
            
            if "seeking_alpha" in sources_to_scrape:
                tasks.append(scraper.scrape_seeking_alpha_news(request.symbol, request.max_items))
            
            # Execute all scraping tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Scraping error: {result}")
        
        # Analyze sentiment if requested
        if request.analyze_sentiment and all_items:
            all_items = await analyze_with_finbert(all_items)
        
        # Cache the results
        if all_items:
            background_tasks.add_task(cache_scraped_data, request.symbol, "mixed", all_items)
        
        # Calculate aggregate sentiment
        sentiment_scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for item in all_items:
            if item.sentiment:
                sentiment = item.sentiment.get('sentiment', 'neutral').lower()
                sentiment_scores[sentiment] = sentiment_scores.get(sentiment, 0) + 1
        
        total_items = len(all_items)
        if total_items > 0:
            sentiment_percentages = {
                k: (v / total_items) * 100 
                for k, v in sentiment_scores.items()
            }
        else:
            sentiment_percentages = sentiment_scores
        
        return {
            "success": True,
            "symbol": request.symbol,
            "total_items": len(all_items),
            "items": [item.dict() for item in all_items],
            "aggregate_sentiment": sentiment_percentages,
            "sources_scraped": sources_to_scrape
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_stock_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cached/{symbol}")
async def get_cached_scrape(symbol: str, max_age_hours: int = 24):
    """Get cached scraped data for a symbol"""
    try:
        items = get_cached_data(symbol, max_age_hours)
        
        return {
            "success": True,
            "symbol": symbol,
            "total_items": len(items),
            "items": [item.dict() for item in items],
            "from_cache": True
        }
        
    except Exception as e:
        logger.error(f"Error getting cached data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def list_sources():
    """List available data sources"""
    return {
        "sources": {
            "yahoo": "Yahoo Finance news and data",
            "finviz": "Finviz financial news",
            "reddit": "Reddit posts from stock-related subreddits",
            "google": "Google News aggregated articles",
            "marketwatch": "MarketWatch financial news",
            "seeking_alpha": "Seeking Alpha analysis and news"
        },
        "usage": "Use 'all' to scrape all sources or specify individual sources in array"
    }

if __name__ == "__main__":
    logger.info("Starting Web Scraper Backend on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)