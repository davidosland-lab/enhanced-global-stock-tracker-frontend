"""
Real News-based Sentiment Analysis - NO MOCK DATA
Integrates Yahoo Finance news scraping with FinBERT analysis
Based on V10 working implementation
"""

import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import hashlib
import time
import re

# Configure logging before anything else
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import finbert_analyzer - handle import errors gracefully
try:
    from .finbert_sentiment import finbert_analyzer
    logger.info("✓ FinBERT analyzer imported successfully")
except (ImportError, ValueError) as e:
    # Try absolute import as fallback
    try:
        from models.finbert_sentiment import finbert_analyzer
        logger.info("✓ FinBERT analyzer imported (absolute path)")
    except (ImportError, ValueError) as e2:
        logger.error(f"Failed to import finbert_analyzer: {e2}")
        finbert_analyzer = None

# SQLite cache database
CACHE_DB = "news_sentiment_cache.db"
CACHE_MINUTES = 15  # Cache validity period

def init_cache_db():
    """Initialize cache database for news and sentiment"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_cache (
                symbol TEXT PRIMARY KEY,
                news_data TEXT,
                sentiment_data TEXT,
                timestamp INTEGER,
                article_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✓ News sentiment cache database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize cache database: {e}")

# Initialize on module load
init_cache_db()

async def fetch_yahoo_news(symbol: str) -> List[Dict]:
    """
    Fetch real news from Yahoo Finance for a stock symbol
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        List of news articles with title, url, published date
    """
    articles = []
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find news items (Yahoo Finance uses various CSS classes)
                    news_items = soup.find_all(['li', 'div'], {'class': re.compile('stream-item|news-item|StreamDataList')})
                    
                    for item in news_items[:20]:  # Limit to 20 articles
                        # Try to find title and link
                        title_elem = item.find('a', {'class': re.compile('title|headline|Fw\\(b\\)')})
                        if not title_elem:
                            title_elem = item.find('h3') or item.find('a')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                            
                            # Fix relative URLs
                            if link and not link.startswith('http'):
                                link = f"https://finance.yahoo.com{link}"
                            
                            # Try to find summary/description
                            summary_elem = item.find('p')
                            summary = summary_elem.get_text(strip=True) if summary_elem else ""
                            
                            # Try to find publish time
                            time_elem = item.find('time') or item.find('span', {'class': re.compile('time|date')})
                            published = time_elem.get('datetime', '') if time_elem else datetime.now().isoformat()
                            
                            if title and len(title) > 10:  # Valid article
                                articles.append({
                                    'title': title,
                                    'url': link,
                                    'summary': summary[:500] if summary else "",
                                    'published': published,
                                    'source': 'Yahoo Finance'
                                })
                    
                    logger.info(f"Fetched {len(articles)} articles for {symbol} from Yahoo Finance")
                else:
                    logger.warning(f"Yahoo Finance returned status {response.status} for {symbol}")
                    
    except Exception as e:
        logger.error(f"Error fetching Yahoo Finance news for {symbol}: {e}")
    
    return articles

async def fetch_finviz_news(symbol: str) -> List[Dict]:
    """
    Fetch news from Finviz as backup source
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        List of news articles
    """
    articles = []
    url = f"https://finviz.com/quote.ashx?t={symbol}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find news table
                    news_table = soup.find('table', {'class': 'fullview-news-outer'})
                    if news_table:
                        rows = news_table.find_all('tr')
                        
                        for row in rows[:15]:  # Limit to 15 articles
                            link_cell = row.find('a', {'class': 'tab-link-news'})
                            if link_cell:
                                title = link_cell.get_text(strip=True)
                                link = link_cell.get('href', '')
                                
                                # Get timestamp
                                time_cell = row.find('td', {'align': 'right'})
                                published = time_cell.get_text(strip=True) if time_cell else ""
                                
                                articles.append({
                                    'title': title,
                                    'url': link,
                                    'summary': '',
                                    'published': published,
                                    'source': 'Finviz'
                                })
                        
                        logger.info(f"Fetched {len(articles)} articles for {symbol} from Finviz")
                        
    except Exception as e:
        logger.error(f"Error fetching Finviz news for {symbol}: {e}")
    
    return articles

def get_cache_key(symbol: str) -> str:
    """Generate cache key for symbol"""
    return hashlib.md5(symbol.upper().encode()).hexdigest()

def get_cached_sentiment(symbol: str) -> Optional[Dict]:
    """
    Get cached sentiment data if still valid
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Cached sentiment data or None if expired/missing
    """
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sentiment_data, timestamp, article_count 
            FROM news_cache 
            WHERE symbol = ?
        ''', (symbol.upper(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            sentiment_json, timestamp, article_count = result
            age_minutes = (time.time() - timestamp) / 60
            
            if age_minutes < CACHE_MINUTES:
                logger.info(f"Cache hit for {symbol} (age: {age_minutes:.1f} min, {article_count} articles)")
                import json
                sentiment_data = json.loads(sentiment_json)
                sentiment_data['cached'] = True
                sentiment_data['cache_age_minutes'] = round(age_minutes, 1)
                return sentiment_data
            else:
                logger.info(f"Cache expired for {symbol} (age: {age_minutes:.1f} min)")
        
    except Exception as e:
        logger.error(f"Cache retrieval error: {e}")
    
    return None

def save_to_cache(symbol: str, sentiment_data: Dict, article_count: int):
    """
    Save sentiment data to cache
    
    Args:
        symbol: Stock ticker symbol
        sentiment_data: Sentiment analysis results
        article_count: Number of articles analyzed
    """
    try:
        import json
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO news_cache 
            (symbol, news_data, sentiment_data, timestamp, article_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            symbol.upper(),
            json.dumps({}),  # We can store news data here if needed
            json.dumps(sentiment_data),
            int(time.time()),
            article_count
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Cached sentiment for {symbol} ({article_count} articles)")
        
    except Exception as e:
        logger.error(f"Cache save error: {e}")

async def get_real_sentiment_for_symbol(symbol: str, use_cache: bool = True) -> Dict:
    """
    Get REAL sentiment analysis for a stock symbol using news scraping and FinBERT
    NO MOCK DATA - Returns error if news unavailable
    
    Args:
        symbol: Stock ticker symbol
        use_cache: Whether to use cached results
    
    Returns:
        Sentiment analysis results with news articles
    """
    symbol = symbol.upper()
    
    # Check cache first
    if use_cache:
        cached = get_cached_sentiment(symbol)
        if cached:
            return cached
    
    logger.info(f"Fetching REAL news for {symbol} from web sources...")
    
    # Fetch news from multiple sources concurrently
    try:
        yahoo_task = fetch_yahoo_news(symbol)
        finviz_task = fetch_finviz_news(symbol)
        
        yahoo_articles, finviz_articles = await asyncio.gather(
            yahoo_task, 
            finviz_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(yahoo_articles, Exception):
            logger.error(f"Yahoo news fetch failed: {yahoo_articles}")
            yahoo_articles = []
        if isinstance(finviz_articles, Exception):
            logger.error(f"Finviz news fetch failed: {finviz_articles}")
            finviz_articles = []
        
        # Combine articles
        all_articles = yahoo_articles + finviz_articles
        
        if len(all_articles) == 0:
            logger.warning(f"NO REAL NEWS FOUND for {symbol} - Cannot provide sentiment")
            return {
                'symbol': symbol,
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {
                    'negative': 0.33,
                    'neutral': 0.34,
                    'positive': 0.33
                },
                'compound': 0.0,
                'method': 'No News Available',
                'article_count': 0,
                'articles': [],
                'timestamp': datetime.now().isoformat(),
                'error': 'No news articles found for this symbol',
                'cached': False
            }
        
        # Analyze sentiment of each article using FinBERT
        logger.info(f"Analyzing {len(all_articles)} articles with FinBERT for {symbol}")
        
        analyzed_articles = []
        for article in all_articles[:25]:  # Limit to 25 most recent
            # Combine title and summary for analysis
            text = f"{article['title']}. {article['summary']}"
            if not finbert_analyzer:
                logger.error("FinBERT analyzer not available")
                return {"error": "FinBERT not available"}
            sentiment_result = finbert_analyzer.analyze_text(text)
            
            article['sentiment'] = sentiment_result['sentiment']
            article['sentiment_score'] = sentiment_result['compound']
            article['confidence'] = sentiment_result['confidence']
            analyzed_articles.append(article)
        
        # Aggregate sentiment from all articles
        if len(analyzed_articles) > 0:
            news_texts = [f"{a['title']}. {a['summary']}" for a in analyzed_articles]
            aggregate_sentiment = finbert_analyzer.analyze_news_batch(news_texts)
            
            # Add metadata
            aggregate_sentiment['symbol'] = symbol
            aggregate_sentiment['article_count'] = len(analyzed_articles)
            aggregate_sentiment['articles'] = analyzed_articles[:10]  # Return top 10 articles
            aggregate_sentiment['sources'] = list(set(a['source'] for a in analyzed_articles))
            aggregate_sentiment['cached'] = False
            
            # Calculate distribution
            positive_count = sum(1 for a in analyzed_articles if a['sentiment'] == 'positive')
            negative_count = sum(1 for a in analyzed_articles if a['sentiment'] == 'negative')
            neutral_count = sum(1 for a in analyzed_articles if a['sentiment'] == 'neutral')
            
            aggregate_sentiment['distribution'] = {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count,
                'positive_pct': round((positive_count / len(analyzed_articles)) * 100, 1),
                'negative_pct': round((negative_count / len(analyzed_articles)) * 100, 1),
                'neutral_pct': round((neutral_count / len(analyzed_articles)) * 100, 1)
            }
            
            # Save to cache
            save_to_cache(symbol, aggregate_sentiment, len(analyzed_articles))
            
            logger.info(f"✓ REAL sentiment analysis complete for {symbol}: {aggregate_sentiment['sentiment'].upper()} ({aggregate_sentiment['confidence']:.1f}%)")
            return aggregate_sentiment
        else:
            return {
                'symbol': symbol,
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
                'compound': 0.0,
                'method': 'No Valid Articles',
                'article_count': 0,
                'articles': [],
                'timestamp': datetime.now().isoformat(),
                'error': 'Could not analyze any articles',
                'cached': False
            }
            
    except Exception as e:
        logger.error(f"Error in real sentiment analysis for {symbol}: {e}")
        return {
            'symbol': symbol,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
            'compound': 0.0,
            'method': 'Error',
            'article_count': 0,
            'articles': [],
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'cached': False
        }

def get_sentiment_sync(symbol: str, use_cache: bool = True) -> Dict:
    """
    Synchronous wrapper for real sentiment analysis
    
    Args:
        symbol: Stock ticker symbol
        use_cache: Whether to use cached results
    
    Returns:
        Sentiment analysis results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_real_sentiment_for_symbol(symbol, use_cache))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Sync sentiment error for {symbol}: {e}")
        return {
            'symbol': symbol,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
            'compound': 0.0,
            'method': 'Error',
            'article_count': 0,
            'articles': [],
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'cached': False
        }
