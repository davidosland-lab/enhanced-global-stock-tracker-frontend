"""
Sentiment Data Collector - Multiple Sources for FinBERT Analysis
Collects financial text from various sources for sentiment analysis
"""

import os
import json
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
import yfinance as yf
from bs4 import BeautifulSoup
import feedparser
import pandas as pd

# Import FinBERT analyzer
try:
    from finbert_analyzer import FinBERTAnalyzer, analyze_financial_text
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentDataCollector:
    """Collects and analyzes sentiment from multiple sources"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.analyzer = FinBERTAnalyzer() if FINBERT_AVAILABLE else None
        self.init_database()
        
        # Data source configurations
        self.sources = {
            'document_uploads': True,      # From Document Analyzer module
            'yahoo_news': True,            # Yahoo Finance news
            'rss_feeds': True,             # Financial RSS feeds
            'sec_filings': True,           # SEC EDGAR filings
            'reddit': True,                # Reddit financial subreddits
            'seeking_alpha': True,         # Seeking Alpha articles
            'press_releases': True,        # Company press releases
            'earnings_calls': True         # Earnings call transcripts
        }
    
    def init_database(self):
        """Initialize database for sentiment storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                title TEXT,
                content TEXT,
                url TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                confidence REAL,
                key_phrases TEXT,
                analyzed_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_sentiment_aggregate (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                avg_sentiment REAL,
                max_sentiment REAL,
                min_sentiment REAL,
                total_articles INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============ SOURCE 1: Document Uploads ============
    def get_uploaded_documents(self, symbol: str) -> List[Dict]:
        """Get documents uploaded through Document Analyzer module"""
        documents = []
        
        # Check integration bridge database for document sentiment
        try:
            bridge_db = "ml_integration_bridge.db"
            if os.path.exists(bridge_db):
                conn = sqlite3.connect(bridge_db)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, data 
                    FROM integration_events 
                    WHERE source_module = 'document_analyzer' 
                    AND data LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''', (f'%"{symbol}"%',))
                
                for row in cursor.fetchall():
                    try:
                        data = json.loads(row[1])
                        documents.append({
                            'source': 'document_upload',
                            'timestamp': row[0],
                            'content': data.get('analysis_text', ''),
                            'sentiment': data.get('sentiment_score', 0),
                            'confidence': data.get('confidence', 0.5)
                        })
                    except:
                        pass
                
                conn.close()
                logger.info(f"Found {len(documents)} uploaded documents for {symbol}")
        except Exception as e:
            logger.warning(f"Could not access uploaded documents: {e}")
        
        return documents
    
    # ============ SOURCE 2: Yahoo Finance News ============
    async def get_yahoo_news(self, symbol: str) -> List[Dict]:
        """Fetch news from Yahoo Finance"""
        news_items = []
        
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            for item in news[:20]:  # Last 20 news items
                news_items.append({
                    'source': 'yahoo_finance',
                    'timestamp': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat(),
                    'title': item.get('title', ''),
                    'content': item.get('summary', ''),
                    'url': item.get('link', ''),
                    'publisher': item.get('publisher', '')
                })
            
            logger.info(f"Fetched {len(news_items)} news items from Yahoo Finance for {symbol}")
        except Exception as e:
            logger.warning(f"Could not fetch Yahoo news: {e}")
        
        return news_items
    
    # ============ SOURCE 3: RSS Feeds ============
    def get_rss_feeds(self, symbol: str) -> List[Dict]:
        """Fetch financial RSS feeds"""
        feeds = []
        
        # Financial RSS feed URLs
        rss_urls = [
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            "https://feeds.reuters.com/reuters/businessNews"
        ]
        
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    # Check if entry mentions the symbol
                    if symbol.upper() in (entry.get('title', '') + entry.get('summary', '')).upper():
                        feeds.append({
                            'source': 'rss_feed',
                            'timestamp': datetime.now().isoformat(),
                            'title': entry.get('title', ''),
                            'content': entry.get('summary', ''),
                            'url': entry.get('link', '')
                        })
            except Exception as e:
                logger.warning(f"Could not parse RSS feed {url}: {e}")
        
        logger.info(f"Found {len(feeds)} RSS items for {symbol}")
        return feeds
    
    # ============ SOURCE 4: Reddit ============
    async def get_reddit_sentiment(self, symbol: str) -> List[Dict]:
        """Fetch Reddit posts and comments (mock implementation)"""
        reddit_items = []
        
        # In production, use Reddit API or PRAW library
        # This is a mock implementation showing the structure
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
        
        # Mock data for demonstration
        reddit_items.append({
            'source': 'reddit',
            'timestamp': datetime.now().isoformat(),
            'title': f"Discussion about ${symbol}",
            'content': f"Sample Reddit discussion about {symbol} stock performance and prospects.",
            'url': f"https://reddit.com/r/stocks/comments/sample_{symbol}",
            'subreddit': 'stocks',
            'score': 150,
            'comments': 45
        })
        
        return reddit_items
    
    # ============ SOURCE 5: SEC Filings ============
    async def get_sec_filings(self, symbol: str) -> List[Dict]:
        """Fetch recent SEC filings (10-K, 10-Q, 8-K)"""
        filings = []
        
        # In production, use SEC EDGAR API
        # This shows the structure for SEC filing sentiment
        filing_types = ['10-K', '10-Q', '8-K']
        
        # Mock data showing structure
        filings.append({
            'source': 'sec_filing',
            'timestamp': datetime.now().isoformat(),
            'title': f"{symbol} Quarterly Report (10-Q)",
            'content': "Risk factors and management discussion section...",
            'url': f"https://www.sec.gov/edgar/sample/{symbol}",
            'filing_type': '10-Q'
        })
        
        return filings
    
    # ============ SOURCE 6: Earnings Call Transcripts ============
    def get_earnings_transcripts(self, symbol: str) -> List[Dict]:
        """Fetch earnings call transcripts"""
        transcripts = []
        
        # In production, use services like AlphaVantage or Seeking Alpha API
        # Mock structure for earnings calls
        transcripts.append({
            'source': 'earnings_call',
            'timestamp': datetime.now().isoformat(),
            'title': f"{symbol} Q3 2024 Earnings Call",
            'content': "CEO remarks about strong growth and positive guidance...",
            'url': f"https://seekingalpha.com/earnings/{symbol}",
            'quarter': 'Q3 2024'
        })
        
        return transcripts
    
    # ============ SENTIMENT ANALYSIS ============
    def analyze_sentiment(self, text: str, title: str = "") -> Dict:
        """Analyze sentiment using FinBERT"""
        if FINBERT_AVAILABLE and self.analyzer:
            # Combine title and content for analysis
            full_text = f"{title} {text}"[:512]  # FinBERT max length
            result = analyze_financial_text(full_text)
            return result
        else:
            # Fallback to keyword-based sentiment
            return self.keyword_sentiment(text)
    
    def keyword_sentiment(self, text: str) -> Dict:
        """Simple keyword-based sentiment as fallback"""
        positive_words = ['growth', 'profit', 'beat', 'exceed', 'strong', 'bullish', 'upgrade']
        negative_words = ['loss', 'decline', 'miss', 'weak', 'bearish', 'downgrade', 'risk']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return {'sentiment': 'positive', 'score': 0.5, 'confidence': 0.6}
        elif neg_count > pos_count:
            return {'sentiment': 'negative', 'score': -0.5, 'confidence': 0.6}
        else:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.5}
    
    # ============ MAIN COLLECTION METHOD ============
    async def collect_all_sentiment(self, symbol: str, days_back: int = 7) -> Dict:
        """Collect sentiment from all available sources"""
        all_sentiment_data = []
        
        # 1. Get uploaded documents
        documents = self.get_uploaded_documents(symbol)
        all_sentiment_data.extend(documents)
        
        # 2. Get Yahoo news
        yahoo_news = await self.get_yahoo_news(symbol)
        for item in yahoo_news:
            sentiment = self.analyze_sentiment(item.get('content', ''), item.get('title', ''))
            item.update(sentiment)
            all_sentiment_data.append(item)
        
        # 3. Get RSS feeds
        rss_items = self.get_rss_feeds(symbol)
        for item in rss_items:
            sentiment = self.analyze_sentiment(item.get('content', ''), item.get('title', ''))
            item.update(sentiment)
            all_sentiment_data.append(item)
        
        # 4. Get Reddit sentiment
        reddit_items = await self.get_reddit_sentiment(symbol)
        for item in reddit_items:
            sentiment = self.analyze_sentiment(item.get('content', ''), item.get('title', ''))
            item.update(sentiment)
            all_sentiment_data.append(item)
        
        # 5. Get SEC filings
        sec_items = await self.get_sec_filings(symbol)
        for item in sec_items:
            sentiment = self.analyze_sentiment(item.get('content', ''), item.get('title', ''))
            item.update(sentiment)
            all_sentiment_data.append(item)
        
        # 6. Get earnings transcripts
        earnings_items = self.get_earnings_transcripts(symbol)
        for item in earnings_items:
            sentiment = self.analyze_sentiment(item.get('content', ''), item.get('title', ''))
            item.update(sentiment)
            all_sentiment_data.append(item)
        
        # Store in database
        self.store_sentiment_data(symbol, all_sentiment_data)
        
        # Calculate aggregate metrics
        aggregate = self.calculate_aggregate_sentiment(all_sentiment_data)
        
        return {
            'symbol': symbol,
            'total_items': len(all_sentiment_data),
            'sources': {
                'document_uploads': len([d for d in all_sentiment_data if d['source'] == 'document_upload']),
                'yahoo_finance': len([d for d in all_sentiment_data if d['source'] == 'yahoo_finance']),
                'rss_feeds': len([d for d in all_sentiment_data if d['source'] == 'rss_feed']),
                'reddit': len([d for d in all_sentiment_data if d['source'] == 'reddit']),
                'sec_filings': len([d for d in all_sentiment_data if d['source'] == 'sec_filing']),
                'earnings_calls': len([d for d in all_sentiment_data if d['source'] == 'earnings_call'])
            },
            'aggregate': aggregate,
            'recent_items': all_sentiment_data[:10]  # Last 10 items
        }
    
    def store_sentiment_data(self, symbol: str, data_items: List[Dict]):
        """Store sentiment data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in data_items:
            cursor.execute('''
                INSERT INTO sentiment_data 
                (symbol, source, timestamp, title, content, url, sentiment_score, 
                 sentiment_label, confidence, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                item.get('source', ''),
                item.get('timestamp', datetime.now().isoformat()),
                item.get('title', ''),
                item.get('content', '')[:1000],  # Truncate long content
                item.get('url', ''),
                item.get('score', 0),
                item.get('sentiment', 'neutral'),
                item.get('confidence', 0.5),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def calculate_aggregate_sentiment(self, data_items: List[Dict]) -> Dict:
        """Calculate aggregate sentiment metrics"""
        if not data_items:
            return {'avg_sentiment': 0, 'sentiment_label': 'neutral'}
        
        scores = [item.get('score', 0) for item in data_items if 'score' in item]
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            # Determine overall sentiment
            if avg_score > 0.2:
                label = 'positive'
            elif avg_score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'avg_sentiment': avg_score,
                'max_sentiment': max(scores),
                'min_sentiment': min(scores),
                'sentiment_label': label,
                'positive_ratio': len([s for s in scores if s > 0.2]) / len(scores),
                'negative_ratio': len([s for s in scores if s < -0.2]) / len(scores)
            }
        
        return {'avg_sentiment': 0, 'sentiment_label': 'neutral'}
    
    async def get_training_ready_sentiment(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get sentiment data formatted for ML training"""
        conn = sqlite3.connect(self.db_path)
        
        # Get daily aggregated sentiment
        query = '''
            SELECT 
                date(timestamp) as date,
                AVG(sentiment_score) as daily_sentiment,
                COUNT(*) as news_count,
                MAX(sentiment_score) as max_sentiment,
                MIN(sentiment_score) as min_sentiment,
                AVG(confidence) as avg_confidence
            FROM sentiment_data
            WHERE symbol = ?
            AND timestamp > date('now', '-' || ? || ' days')
            GROUP BY date(timestamp)
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, days))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Add rolling averages
            df['sentiment_ma_3'] = df['daily_sentiment'].rolling(3).mean()
            df['sentiment_ma_7'] = df['daily_sentiment'].rolling(7).mean()
            
            # Add sentiment momentum
            df['sentiment_change'] = df['daily_sentiment'].diff()
            
            logger.info(f"Prepared {len(df)} days of sentiment data for {symbol}")
        
        return df

# Example usage
async def main():
    collector = SentimentDataCollector()
    
    # Collect sentiment for a symbol
    result = await collector.collect_all_sentiment("AAPL", days_back=7)
    
    print(f"Collected {result['total_items']} sentiment items")
    print(f"Sources: {result['sources']}")
    print(f"Aggregate sentiment: {result['aggregate']}")
    
    # Get training-ready data
    training_data = await collector.get_training_ready_sentiment("AAPL", days=30)
    print(f"Training data shape: {training_data.shape}")

if __name__ == "__main__":
    asyncio.run(main())