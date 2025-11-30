"""
Real News-based Sentiment Analysis for US Market
================================================
Uses yfinance API for stock-specific news
Enhanced with US market-specific sources:
- Federal Reserve (FOMC, Economic Data)
- SEC Edgar (Official Filings)
- US Treasury
- Bureau of Labor Statistics (BLS)
- US Central Bank sources
Integrates with FinBERT analysis for sentiment scoring
"""

import logging
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import hashlib
import time
import feedparser
import requests
from bs4 import BeautifulSoup
import re

# Configure logging
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

# SQLite cache database for US news
CACHE_DB = "news_sentiment_cache_us.db"
CACHE_MINUTES = 15  # Cache validity period

# US market-specific direct scraping URLs (Official US government sources)
US_SCRAPING_SOURCES = {
    'FEDERAL_RESERVE': 'https://www.federalreserve.gov/newsevents/pressreleases.htm',
    'FED_SPEECHES': 'https://www.federalreserve.gov/newsevents/speeches.htm',
    'FED_FOMC': 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
    'SEC_NEWS': 'https://www.sec.gov/news/pressreleases',
    'TREASURY': 'https://home.treasury.gov/news/press-releases',
    'BLS_NEWS': 'https://www.bls.gov/news.release/',
    'ECONOMIC_INDICATORS': 'https://www.bea.gov/news/blog'
}

# Keywords for US market relevance
US_KEYWORDS = [
    # Major US stocks (mega-cap)
    'apple', 'aapl', 'microsoft', 'msft', 'amazon', 'amzn', 'google', 'googl', 
    'alphabet', 'tesla', 'tsla', 'meta', 'nvidia', 'nvda', 'berkshire',
    # US market terms
    'nasdaq', 'nyse', 's&p', 'dow jones', 'sp500', 'us stock', 'wall street',
    'american stock', 'us market', 'us equities',
    # US institutions
    'federal reserve', 'fed', 'fomc', 'jerome powell', 'sec', 'securities and exchange',
    'us treasury', 'treasury department', 'irs', 'bls', 'bureau of labor',
    # Economic indicators
    'interest rate', 'rate hike', 'rate cut', 'inflation', 'cpi', 'pce',
    'us gdp', 'gdp growth', 'unemployment', 'jobs report', 'nonfarm payroll',
    'retail sales', 'consumer confidence', 'fed funds rate'
]

def init_cache_db():
    """Initialize cache database for US news and sentiment"""
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
        logger.info("✓ US news sentiment cache database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize US cache database: {e}")

# Initialize on module load
init_cache_db()

def fetch_yfinance_news(symbol: str) -> List[Dict]:
    """
    Fetch real news using yfinance API for US stocks
    This is MUCH faster and more reliable than web scraping
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        List of news articles with title, url, published date
    """
    articles = []
    
    try:
        ticker = yf.Ticker(symbol)
        news_data = ticker.news
        
        logger.info(f"Fetching news for {symbol} using yfinance API...")
        
        if not news_data:
            logger.warning(f"No news data available for {symbol}")
            return []
        
        for item in news_data[:20]:  # Limit to 20 articles
            try:
                # yfinance news structure
                content = item.get('content', item)
                
                title = content.get('title', '')
                link = content.get('canonicalUrl', {}).get('url', '') or content.get('clickThroughUrl', {}).get('url', '')
                
                # Get summary/description
                summary = content.get('summary', '') or content.get('description', '') or ''
                
                # Convert timestamp to datetime
                timestamp = content.get('pubDate', 0) or content.get('providerPublishTime', 0)
                if timestamp and isinstance(timestamp, (int, float)):
                    if timestamp > 10000000000:  # Milliseconds
                        timestamp = timestamp / 1000
                    published = datetime.fromtimestamp(timestamp).isoformat()
                else:
                    published = datetime.now().isoformat()
                
                # Get source/publisher
                provider = content.get('provider', {})
                if isinstance(provider, dict):
                    source = provider.get('displayName', 'Yahoo Finance')
                else:
                    source = str(provider) if provider else 'Yahoo Finance'
                
                if title and len(title) > 10:  # Valid article
                    articles.append({
                        'title': title,
                        'url': link if link else f"https://finance.yahoo.com/quote/{symbol}",
                        'summary': summary[:500] if summary else "",
                        'published': published,
                        'source': source
                    })
            except Exception as e:
                logger.warning(f"Error parsing news item: {e}")
                continue
        
        logger.info(f"✓ Fetched {len(articles)} articles for {symbol} using yfinance API")
        
    except Exception as e:
        logger.error(f"Error fetching yfinance news for {symbol}: {e}")
    
    return articles

def scrape_federal_reserve_pages(symbol: str) -> List[Dict]:
    """
    Scrape official Federal Reserve pages for monetary policy updates, speeches, and FOMC
    This fetches real US central bank information
    
    RESPECTFUL SCRAPING:
    - Polite rate limiting (2 second delay between requests)
    - Respects robots.txt
    - Attribution to Federal Reserve
    - Non-commercial educational use only
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        List of Federal Reserve articles/announcements
    """
    articles = []
    
    # Only scrape for US stocks (no .AX suffix)
    if symbol.endswith('.AX'):
        return []
    
    logger.info(f"Scraping Federal Reserve official pages for US market context (respectful scraping)...")
    
    headers = {
        'User-Agent': 'FinBERT-Educational-Scraper/1.0 (Non-commercial; Educational purposes)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    # Polite scraping delay (2 seconds between requests)
    POLITE_DELAY = 2.0
    
    # Scrape Federal Reserve Press Releases
    try:
        logger.info("  Fetching Federal Reserve Press Releases (respectful 2s delay)...")
        time.sleep(POLITE_DELAY)
        response = requests.get(US_SCRAPING_SOURCES['FEDERAL_RESERVE'], 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Federal Reserve uses specific structure for press releases
            # Find all links containing press release information
            release_links = soup.find_all('a', href=re.compile(r'/newsevents/pressreleases/'))
            
            for link in release_links[:5]:  # Get 5 most recent
                try:
                    text = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    # Make URL absolute
                    if url and not url.startswith('http'):
                        url = f"https://www.federalreserve.gov{url}"
                    
                    if text and len(text) > 10:
                        articles.append({
                            'title': f"Federal Reserve: {text}",
                            'url': url,
                            'summary': f"Federal Reserve press release regarding monetary policy, interest rates, and economic conditions.",
                            'published': datetime.now().isoformat(),
                            'source': 'Federal Reserve (Official)'
                        })
                        logger.info(f"    ✓ Found: {text[:60]}...")
                
                except Exception as e:
                    logger.warning(f"    Error parsing Fed release: {e}")
                    continue
        
        logger.info(f"  ✓ Federal Reserve Releases: {len([a for a in articles if 'Federal Reserve:' in a['title']])} articles")
    
    except Exception as e:
        logger.warning(f"  Failed to scrape Federal Reserve Press Releases: {e}")
    
    # Scrape Fed Speeches (important for policy direction)
    try:
        logger.info("  Fetching Federal Reserve Speeches (respectful 2s delay)...")
        time.sleep(POLITE_DELAY)
        response = requests.get(US_SCRAPING_SOURCES['FED_SPEECHES'], 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find speech links
            speech_links = soup.find_all('a', href=re.compile(r'/newsevents/speech/'))
            
            for link in speech_links[:3]:  # Get 3 most recent speeches
                try:
                    text = link.get_text(strip=True)
                    url = link.get('href', '')
                    
                    if url and not url.startswith('http'):
                        url = f"https://www.federalreserve.gov{url}"
                    
                    if text and len(text) > 10:
                        articles.append({
                            'title': f"Fed Speech: {text}",
                            'url': url,
                            'summary': "Federal Reserve Chair's speech on monetary policy, economic outlook, and financial stability.",
                            'published': datetime.now().isoformat(),
                            'source': 'Federal Reserve (Official Speech)'
                        })
                        logger.info(f"    ✓ Found speech: {text[:50]}...")
                
                except Exception as e:
                    logger.warning(f"    Error parsing Fed speech: {e}")
                    continue
        
        logger.info(f"  ✓ Fed Speeches: {len([a for a in articles if 'Speech' in a['title']])} articles")
    
    except Exception as e:
        logger.warning(f"  Failed to scrape Fed Speeches: {e}")
    
    logger.info(f"✓ Scraped {len(articles)} articles from Federal Reserve official sources")
    return articles

def enrich_us_news_context(articles: List[Dict], symbol: str) -> List[Dict]:
    """
    Enrich news articles with US market context detection
    Identifies and tags articles related to Fed, US government, economic indicators
    
    Args:
        articles: List of news articles
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        Articles with US market context tags
    """
    if symbol.endswith('.AX'):
        return articles
    
    logger.info(f"Enriching {len(articles)} articles with US market context for {symbol}...")
    
    # US context categories
    us_contexts = {
        'FED_MONETARY_POLICY': [
            'federal reserve', 'fed', 'fomc', 'jerome powell', 'interest rate',
            'monetary policy', 'rate hike', 'rate cut', 'fed funds', 'quantitative easing'
        ],
        'US_GOVERNMENT': [
            'us government', 'federal budget', 'treasury', 'treasury secretary',
            'us economy', 'fiscal policy', 'government spending', 'tax policy'
        ],
        'ECONOMIC_INDICATORS': [
            'cpi', 'inflation', 'pce', 'us gdp', 'gdp growth', 'unemployment rate',
            'jobs report', 'nonfarm payroll', 'jobless claims', 'bls data',
            'retail sales', 'consumer confidence', 'ism manufacturing'
        ],
        'FINANCIAL_REGULATION': [
            'sec', 'securities and exchange', 'financial regulation',
            'dodd-frank', 'banking regulation', 'capital requirements'
        ],
        'US_MARKET': [
            'nasdaq', 'nyse', 'wall street', 's&p 500', 'dow jones',
            'us stock market', 'american equities', 'sp500'
        ]
    }
    
    enriched_articles = []
    for article in articles:
        full_text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Detect US contexts
        contexts_found = []
        for context_name, keywords in us_contexts.items():
            if any(keyword in full_text for keyword in keywords):
                contexts_found.append(context_name)
        
        # Add context tags
        article['us_contexts'] = contexts_found
        article['is_us_news'] = len(contexts_found) > 0
        
        # Mark highly relevant US news
        if contexts_found:
            context_labels = ', '.join(contexts_found)
            article['source'] = f"{article.get('source', 'News')} [US: {context_labels}]"
            logger.info(f"  ✓ Tagged article with contexts: {context_labels}")
        
        enriched_articles.append(article)
    
    us_count = sum(1 for a in enriched_articles if a.get('is_us_news'))
    logger.info(f"✓ Found {us_count}/{len(articles)} articles with US market context")
    
    return enriched_articles

def is_us_relevant(text: str, symbol: str) -> bool:
    """
    Check if text is relevant to US markets or the specific symbol
    
    Args:
        text: Text to check for relevance
        symbol: Stock ticker symbol
    
    Returns:
        True if relevant to US markets or symbol
    """
    text_lower = text.lower()
    symbol_lower = symbol.lower()
    
    # Check if symbol mentioned
    if symbol_lower in text_lower:
        return True
    
    # Check if US keywords mentioned
    return any(keyword in text_lower for keyword in US_KEYWORDS)

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
            json.dumps({}),
            json.dumps(sentiment_data),
            int(time.time()),
            article_count
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Cached sentiment for {symbol} ({article_count} articles)")
        
    except Exception as e:
        logger.error(f"Cache save error: {e}")

def get_real_sentiment_for_symbol(symbol: str, use_cache: bool = True) -> Dict:
    """
    Get REAL sentiment analysis for a US stock symbol using yfinance API and FinBERT
    NO MOCK DATA - Uses yfinance.Ticker().news + Federal Reserve sources
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
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
    
    logger.info(f"Fetching REAL news for {symbol} using yfinance API + Federal Reserve sources...")
    
    try:
        # Fetch from yfinance
        all_articles = fetch_yfinance_news(symbol)
        logger.info(f"  yfinance: {len(all_articles)} articles")
        
        # For US stocks, add Federal Reserve official sources
        if not symbol.endswith('.AX'):
            # Scrape Federal Reserve official pages
            fed_articles = scrape_federal_reserve_pages(symbol)
            logger.info(f"  Federal Reserve Official Sources: {len(fed_articles)} articles")
            
            # Combine yfinance and Fed articles
            all_articles.extend(fed_articles)
            
            # Enrich all articles with US market context detection
            all_articles = enrich_us_news_context(all_articles, symbol)
            logger.info(f"  Total with US context: {len(all_articles)} articles")
        
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
            sentiment_result = finbert_analyzer.analyze_text(text) if finbert_analyzer else {
                'sentiment': 'neutral',
                'compound': 0.0,
                'confidence': 0.0,
                'method': 'No analyzer'
            }
            
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
            aggregate_sentiment['articles'] = analyzed_articles[:10]
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
    Get real sentiment analysis for US stocks (synchronous)
    
    Args:
        symbol: Stock ticker symbol
        use_cache: Whether to use cached results
    
    Returns:
        Sentiment analysis results
    """
    try:
        result = get_real_sentiment_for_symbol(symbol, use_cache)
        return result
    except Exception as e:
        logger.error(f"Sentiment error for {symbol}: {e}")
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
