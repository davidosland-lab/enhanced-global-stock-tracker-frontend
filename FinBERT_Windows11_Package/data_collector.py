#!/usr/bin/env python3
"""
Automated Data Collector for FinBERT Trading System
Collects news, economic data, and market information automatically
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

import requests
import feedparser
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    """Collects comprehensive market and economic data"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API configurations (free tiers)
        self.news_api_key = None  # Optional: Add your NewsAPI key
        self.fred_api_key = None  # Optional: Add your FRED API key
        
    def collect_all_data(self, symbol: str) -> Dict[str, Any]:
        """Collect all available data for a symbol"""
        logger.info(f"Collecting comprehensive data for {symbol}")
        
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'stock_news': self.get_stock_news(symbol),
            'company_info': self.get_company_info(symbol),
            'economic_indicators': self.get_economic_indicators(),
            'interest_rates': self.get_interest_rates(),
            'geopolitical_news': self.get_geopolitical_news(),
            'government_announcements': self.get_government_announcements(),
            'market_sentiment': self.get_market_sentiment(),
            'sector_performance': self.get_sector_performance(symbol),
            'technical_indicators': self.get_technical_indicators(symbol)
        }
        
        # Cache the data
        self._save_to_cache(symbol, data)
        return data
    
    def get_stock_news(self, symbol: str, max_items: int = 20) -> List[Dict]:
        """Get latest news for a specific stock"""
        news_items = []
        
        try:
            # Yahoo Finance news
            ticker = yf.Ticker(symbol)
            if hasattr(ticker, 'news'):
                for item in ticker.news[:max_items]:
                    news_items.append({
                        'source': 'Yahoo Finance',
                        'title': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'link': item.get('link', ''),
                        'published': item.get('providerPublishTime', 0),
                        'type': 'company_news'
                    })
        except Exception as e:
            logger.error(f"Error fetching Yahoo news: {e}")
        
        # RSS Feeds for financial news
        rss_feeds = [
            ('Reuters Business', 'https://feeds.reuters.com/reuters/businessNews'),
            ('Bloomberg', 'https://feeds.bloomberg.com/markets/news.rss'),
            ('MarketWatch', 'http://feeds.marketwatch.com/marketwatch/topstories'),
            ('CNBC', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'),
            ('WSJ Markets', 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml')
        ]
        
        for source_name, feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Get top 5 from each source
                    # Check if stock symbol is mentioned
                    content = f"{entry.get('title', '')} {entry.get('summary', '')}".upper()
                    if symbol.split('.')[0] in content:
                        news_items.append({
                            'source': source_name,
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', '')[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'type': 'market_news'
                        })
            except Exception as e:
                logger.debug(f"Error fetching {source_name}: {e}")
        
        return news_items
    
    def get_company_info(self, symbol: str) -> Dict:
        """Get comprehensive company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'analyst_recommendation': info.get('recommendationKey', ''),
                'target_mean_price': info.get('targetMeanPrice', 0)
            }
        except Exception as e:
            logger.error(f"Error fetching company info: {e}")
            return {}
    
    def get_economic_indicators(self) -> Dict:
        """Get key economic indicators"""
        indicators = {}
        
        # Get major indices
        indices = {
            'SP500': '^GSPC',
            'DOW': '^DJI',
            'NASDAQ': '^IXIC',
            'VIX': '^VIX',
            'DXY': 'DX-Y.NYB',  # Dollar Index
            'GOLD': 'GC=F',
            'OIL': 'CL=F'
        }
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    indicators[name] = {
                        'price': float(hist['Close'].iloc[-1]),
                        'change': float(hist['Close'].iloc[-1] - hist['Open'].iloc[0]),
                        'change_pct': float((hist['Close'].iloc[-1] / hist['Open'].iloc[0] - 1) * 100)
                    }
            except Exception as e:
                logger.debug(f"Error fetching {name}: {e}")
        
        return indicators
    
    def get_interest_rates(self) -> Dict:
        """Get current interest rates and bond yields"""
        rates = {}
        
        # Treasury yields
        treasuries = {
            '2Y': '^IRX',  # 13 week
            '5Y': '^FVX',  # 5 year
            '10Y': '^TNX', # 10 year
            '30Y': '^TYX'  # 30 year
        }
        
        for name, symbol in treasuries.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    rates[f'US_{name}_yield'] = float(hist['Close'].iloc[-1])
            except Exception as e:
                logger.debug(f"Error fetching {name} yield: {e}")
        
        # Try to get Fed Funds Rate from FRED (if API key available)
        if self.fred_api_key:
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': 'DFF',
                    'api_key': self.fred_api_key,
                    'file_type': 'json',
                    'limit': 1,
                    'sort_order': 'desc'
                }
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'observations' in data and data['observations']:
                        rates['fed_funds_rate'] = float(data['observations'][0]['value'])
            except Exception as e:
                logger.debug(f"Error fetching Fed rate: {e}")
        
        return rates
    
    def get_geopolitical_news(self) -> List[Dict]:
        """Get geopolitical news that might affect markets"""
        news = []
        
        # Keywords that indicate geopolitical events
        keywords = [
            'war', 'conflict', 'sanctions', 'trade war', 'tariff',
            'election', 'coup', 'protest', 'strike', 'embargo',
            'military', 'missile', 'nuclear', 'brexit', 'referendum'
        ]
        
        # Geopolitical RSS feeds
        feeds = [
            ('Reuters World', 'https://feeds.reuters.com/Reuters/worldNews'),
            ('BBC World', 'http://feeds.bbci.co.uk/news/world/rss.xml'),
            ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
        ]
        
        for source, feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    content = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
                    if any(keyword in content for keyword in keywords):
                        news.append({
                            'source': source,
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', '')[:500],
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'type': 'geopolitical'
                        })
            except Exception as e:
                logger.debug(f"Error fetching {source}: {e}")
        
        return news
    
    def get_government_announcements(self) -> List[Dict]:
        """Get government and central bank announcements"""
        announcements = []
        
        # Central bank RSS feeds
        cb_feeds = [
            ('Federal Reserve', 'https://www.federalreserve.gov/feeds/press_all.xml'),
            ('ECB', 'https://www.ecb.europa.eu/rss/press.html'),
            ('Bank of England', 'https://www.bankofengland.co.uk/rss/news'),
            ('RBA', 'https://www.rba.gov.au/rss/rss.xml'),
        ]
        
        for source, feed_url in cb_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    announcements.append({
                        'source': source,
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', '')[:500],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'type': 'central_bank'
                    })
            except Exception as e:
                logger.debug(f"Error fetching {source}: {e}")
        
        # Try to get treasury announcements
        try:
            treasury_feed = feedparser.parse('https://www.treasury.gov/rss/PRESS_RELEASES.xml')
            for entry in treasury_feed.entries[:5]:
                announcements.append({
                    'source': 'US Treasury',
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', '')[:500],
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'type': 'treasury'
                })
        except Exception as e:
            logger.debug(f"Error fetching treasury: {e}")
        
        return announcements
    
    def get_market_sentiment(self) -> Dict:
        """Calculate overall market sentiment indicators"""
        sentiment = {}
        
        try:
            # Fear & Greed indicators
            vix = yf.Ticker('^VIX')
            vix_hist = vix.history(period='1mo')
            if not vix_hist.empty:
                current_vix = float(vix_hist['Close'].iloc[-1])
                vix_avg = float(vix_hist['Close'].mean())
                
                # VIX levels: <12 low fear, 12-20 normal, 20-30 high fear, >30 extreme fear
                if current_vix < 12:
                    vix_sentiment = 'extreme_greed'
                elif current_vix < 20:
                    vix_sentiment = 'greed'
                elif current_vix < 30:
                    vix_sentiment = 'fear'
                else:
                    vix_sentiment = 'extreme_fear'
                
                sentiment['vix'] = {
                    'value': current_vix,
                    'average': vix_avg,
                    'sentiment': vix_sentiment
                }
            
            # Put/Call Ratio (if available)
            # This would require options data which is limited in free APIs
            
            # Market breadth - advancing vs declining
            # This would require more comprehensive market data
            
        except Exception as e:
            logger.debug(f"Error calculating sentiment: {e}")
        
        return sentiment
    
    def get_sector_performance(self, symbol: str) -> Dict:
        """Get sector performance data"""
        sectors = {}
        
        # Sector ETFs for comparison
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU'
        }
        
        for sector, etf in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period='1mo')
                if not hist.empty:
                    sectors[sector] = {
                        'etf': etf,
                        'price': float(hist['Close'].iloc[-1]),
                        'change_1d': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100),
                        'change_1w': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100),
                        'change_1m': float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100)
                    }
            except Exception as e:
                logger.debug(f"Error fetching {sector}: {e}")
        
        return sectors
    
    def get_technical_indicators(self, symbol: str) -> Dict:
        """Calculate comprehensive technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if hist.empty:
                return {}
            
            indicators = {}
            
            # Price levels
            indicators['current_price'] = float(hist['Close'].iloc[-1])
            indicators['volume'] = int(hist['Volume'].iloc[-1])
            
            # Moving averages
            indicators['sma_20'] = float(hist['Close'].rolling(20).mean().iloc[-1])
            indicators['sma_50'] = float(hist['Close'].rolling(50).mean().iloc[-1])
            indicators['ema_12'] = float(hist['Close'].ewm(span=12).mean().iloc[-1])
            indicators['ema_26'] = float(hist['Close'].ewm(span=26).mean().iloc[-1])
            
            # MACD
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            indicators['macd_signal'] = float(hist['Close'].ewm(span=9).mean().iloc[-1])
            
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = float(100 - (100 / (1 + rs)).iloc[-1])
            
            # Bollinger Bands
            bb_period = 20
            bb_std = hist['Close'].rolling(bb_period).std()
            bb_mean = hist['Close'].rolling(bb_period).mean()
            indicators['bb_upper'] = float((bb_mean + 2 * bb_std).iloc[-1])
            indicators['bb_lower'] = float((bb_mean - 2 * bb_std).iloc[-1])
            indicators['bb_middle'] = float(bb_mean.iloc[-1])
            
            # Support and Resistance
            indicators['resistance_1'] = float(hist['High'].rolling(20).max().iloc[-1])
            indicators['support_1'] = float(hist['Low'].rolling(20).min().iloc[-1])
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
    
    def _save_to_cache(self, symbol: str, data: Dict):
        """Save collected data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{datetime.now().strftime('%Y%m%d')}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Data cached to {cache_file}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def load_from_cache(self, symbol: str, max_age_hours: int = 4) -> Optional[Dict]:
        """Load data from cache if available and recent"""
        cache_pattern = os.path.join(self.cache_dir, f"{symbol}_*.json")
        import glob
        cache_files = glob.glob(cache_pattern)
        
        if cache_files:
            latest_cache = max(cache_files, key=os.path.getctime)
            cache_age = time.time() - os.path.getctime(latest_cache)
            
            if cache_age < max_age_hours * 3600:
                try:
                    with open(latest_cache, 'r') as f:
                        logger.info(f"Loading from cache: {latest_cache}")
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading cache: {e}")
        
        return None

class DataProcessor:
    """Process collected data for ML model input"""
    
    @staticmethod
    def extract_sentiment_features(data: Dict) -> Dict[str, float]:
        """Extract sentiment features from collected data"""
        features = {
            'news_count': 0,
            'positive_news_ratio': 0,
            'negative_news_ratio': 0,
            'geopolitical_risk': 0,
            'government_activity': 0,
            'market_fear': 0
        }
        
        # Count and analyze news sentiment
        if 'stock_news' in data:
            features['news_count'] = len(data['stock_news'])
            
            # Simple keyword-based sentiment (would be better with FinBERT)
            positive_keywords = ['beat', 'exceed', 'profit', 'gain', 'rise', 'upgrade', 'buy', 'strong']
            negative_keywords = ['miss', 'loss', 'fall', 'drop', 'downgrade', 'sell', 'weak', 'concern']
            
            positive_count = 0
            negative_count = 0
            
            for news_item in data['stock_news']:
                text = f"{news_item.get('title', '')} {news_item.get('summary', '')}".lower()
                if any(word in text for word in positive_keywords):
                    positive_count += 1
                if any(word in text for word in negative_keywords):
                    negative_count += 1
            
            if features['news_count'] > 0:
                features['positive_news_ratio'] = positive_count / features['news_count']
                features['negative_news_ratio'] = negative_count / features['news_count']
        
        # Geopolitical risk score
        if 'geopolitical_news' in data:
            features['geopolitical_risk'] = min(len(data['geopolitical_news']) / 10, 1.0)
        
        # Government activity score
        if 'government_announcements' in data:
            features['government_activity'] = min(len(data['government_announcements']) / 5, 1.0)
        
        # Market fear from VIX
        if 'market_sentiment' in data and 'vix' in data['market_sentiment']:
            vix_value = data['market_sentiment']['vix']['value']
            features['market_fear'] = min(vix_value / 40, 1.0)  # Normalize VIX to 0-1
        
        return features
    
    @staticmethod
    def extract_macro_features(data: Dict) -> Dict[str, float]:
        """Extract macroeconomic features"""
        features = {}
        
        # Economic indicators
        if 'economic_indicators' in data:
            for indicator, values in data['economic_indicators'].items():
                if isinstance(values, dict):
                    features[f'{indicator}_change'] = values.get('change_pct', 0)
        
        # Interest rates
        if 'interest_rates' in data:
            for rate_name, rate_value in data['interest_rates'].items():
                features[rate_name] = rate_value
        
        # Sector performance
        if 'sector_performance' in data:
            # Get average sector performance
            sector_changes = []
            for sector, performance in data['sector_performance'].items():
                if isinstance(performance, dict):
                    sector_changes.append(performance.get('change_1w', 0))
            
            if sector_changes:
                features['avg_sector_performance'] = sum(sector_changes) / len(sector_changes)
        
        return features
    
    @staticmethod
    def prepare_ml_features(data: Dict) -> pd.DataFrame:
        """Prepare all features for ML model input"""
        all_features = {}
        
        # Get sentiment features
        sentiment_features = DataProcessor.extract_sentiment_features(data)
        all_features.update(sentiment_features)
        
        # Get macro features
        macro_features = DataProcessor.extract_macro_features(data)
        all_features.update(macro_features)
        
        # Get technical indicators
        if 'technical_indicators' in data:
            all_features.update(data['technical_indicators'])
        
        # Get company fundamentals
        if 'company_info' in data:
            fundamental_features = {
                'pe_ratio': data['company_info'].get('pe_ratio', 0),
                'dividend_yield': data['company_info'].get('dividend_yield', 0),
                'beta': data['company_info'].get('beta', 1)
            }
            all_features.update(fundamental_features)
        
        # Convert to DataFrame
        return pd.DataFrame([all_features])

if __name__ == "__main__":
    # Example usage
    collector = MarketDataCollector()
    
    # Collect data for a stock
    symbol = "AAPL"
    print(f"Collecting data for {symbol}...")
    
    # Try to load from cache first
    data = collector.load_from_cache(symbol, max_age_hours=4)
    
    if data is None:
        # Collect fresh data
        data = collector.collect_all_data(symbol)
    
    # Process the data for ML
    processor = DataProcessor()
    features = processor.prepare_ml_features(data)
    
    print("\nCollected Data Summary:")
    print(f"Stock News Items: {len(data.get('stock_news', []))}")
    print(f"Geopolitical News Items: {len(data.get('geopolitical_news', []))}")
    print(f"Government Announcements: {len(data.get('government_announcements', []))}")
    print(f"Economic Indicators: {len(data.get('economic_indicators', {}))}")
    print(f"Interest Rates: {len(data.get('interest_rates', {}))}")
    print(f"Sector Performance: {len(data.get('sector_performance', {}))}")
    print(f"Technical Indicators: {len(data.get('technical_indicators', {}))}")
    
    print("\nML Features Shape:", features.shape)
    print("\nSample Features:")
    print(features.iloc[0].to_dict())