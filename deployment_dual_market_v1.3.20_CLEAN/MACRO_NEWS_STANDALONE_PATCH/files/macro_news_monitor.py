"""
Macro News Monitor
==================
Monitors and analyzes government/central bank announcements that impact market sentiment:
- Federal Reserve (US): FOMC, interest rate decisions, Fed speeches
- Reserve Bank of Australia: Cash rate decisions, RBA speeches, board minutes
- Economic indicators: CPI, GDP, unemployment
- Integrates with FinBERT for sentiment analysis

This module enhances market sentiment scoring with macro economic context.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FinBERT analyzer
try:
    from ..finbert_sentiment import finbert_analyzer
except ImportError:
    try:
        from models.finbert_sentiment import finbert_analyzer
    except ImportError:
        finbert_analyzer = None
        logger.warning("FinBERT analyzer not available for macro news sentiment")


class MacroNewsMonitor:
    """
    Monitor and analyze macro economic news that impacts market sentiment
    """
    
    def __init__(self, market: str = 'US'):
        """
        Initialize macro news monitor
        
        Args:
            market: 'US' or 'ASX'
        """
        self.market = market.upper()
        self.polite_delay = 3.0  # Respectful scraping delay (increased to 3 seconds)
        self.timeout = 15  # Increased timeout to 15 seconds
        self.max_retries = 2  # Retry failed requests
        self.headers = {
            'User-Agent': 'FinBERT-Educational-Scraper/1.0 (Non-commercial; Educational purposes)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        # US sources
        self.us_sources = {
            'FED_RELEASES': 'https://www.federalreserve.gov/newsevents/pressreleases.htm',
            'FED_SPEECHES': 'https://www.federalreserve.gov/newsevents/speeches.htm',
            'FED_FOMC': 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
        }
        
        # Australian sources
        self.aus_sources = {
            'RBA_MEDIA': 'https://www.rba.gov.au/media-releases/',
            'RBA_SPEECHES': 'https://www.rba.gov.au/speeches/',
        }
        
        # Macro keywords for sentiment analysis
        self.macro_keywords = {
            'US': [
                'interest rate', 'rate hike', 'rate cut', 'fomc', 'federal reserve',
                'jerome powell', 'inflation', 'cpi', 'pce', 'gdp', 'unemployment',
                'jobs report', 'nonfarm payroll', 'fed funds rate', 'monetary policy',
                'quantitative easing', 'tapering', 'recession', 'economic outlook'
            ],
            'ASX': [
                'cash rate', 'interest rate', 'rba', 'reserve bank', 'philip lowe',
                'michele bullock', 'inflation', 'cpi', 'gdp', 'unemployment',
                'board minutes', 'monetary policy', 'economic outlook', 'australian economy'
            ]
        }
        
        logger.info(f"Macro News Monitor initialized for {market} market")
    
    def _safe_request(self, url: str, description: str = "page") -> Optional[requests.Response]:
        """
        Make a safe HTTP request with retries and delays
        
        Args:
            url: URL to fetch
            description: Description for logging
            
        Returns:
            Response object or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    wait_time = self.polite_delay * (attempt + 1)
                    logger.info(f"    Retry {attempt + 1}/{self.max_retries} after {wait_time}s delay...")
                    time.sleep(wait_time)
                else:
                    time.sleep(self.polite_delay)
                
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"    Rate limited (429), waiting longer...")
                    time.sleep(self.polite_delay * 2)
                    continue
                elif response.status_code >= 500:  # Server error
                    logger.warning(f"    Server error ({response.status_code}), retrying...")
                    continue
                else:
                    logger.warning(f"    HTTP {response.status_code} for {description}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"    Timeout fetching {description}")
                if attempt < self.max_retries - 1:
                    continue
            except requests.exceptions.ConnectionError:
                logger.warning(f"    Connection error fetching {description}")
                if attempt < self.max_retries - 1:
                    continue
            except Exception as e:
                logger.warning(f"    Error fetching {description}: {e}")
                return None
        
        logger.warning(f"  Failed to fetch {description} after {self.max_retries} attempts")
        return None
    
    def get_macro_sentiment(self) -> Dict:
        """
        Fetch and analyze macro economic news sentiment
        
        Returns:
            Dictionary with macro news and sentiment scores
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"MACRO NEWS ANALYSIS - {self.market} MARKET")
        logger.info(f"{'='*80}")
        
        if self.market == 'US':
            return self._get_us_macro_sentiment()
        elif self.market == 'ASX':
            return self._get_aus_macro_sentiment()
        else:
            logger.warning(f"Unknown market: {self.market}")
            return self._get_default_sentiment()
    
    def _get_us_macro_sentiment(self) -> Dict:
        """Fetch and analyze US Federal Reserve news"""
        articles = []
        
        # Scrape Fed Press Releases
        fed_releases = self._scrape_fed_releases()
        articles.extend(fed_releases)
        
        # Scrape Fed Speeches
        fed_speeches = self._scrape_fed_speeches()
        articles.extend(fed_speeches)
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(articles)
        
        # Determine sentiment label
        if sentiment_score > 0.15:
            sentiment_label = "BULLISH"
        elif sentiment_score < -0.15:
            sentiment_label = "BEARISH"
        else:
            sentiment_label = "NEUTRAL"
        
        result = {
            'market': 'US',
            'article_count': len(articles),
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': sentiment_label,
            'articles': articles[:5],  # Top 5 for reports
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(articles, sentiment_score, 'US')
        }
        
        logger.info(f"✓ US Macro News: {len(articles)} articles, Sentiment: {sentiment_label} ({sentiment_score:+.3f})")
        
        return result
    
    def _get_aus_macro_sentiment(self) -> Dict:
        """Fetch and analyze RBA news"""
        articles = []
        
        # Scrape RBA Media Releases
        rba_releases = self._scrape_rba_releases()
        articles.extend(rba_releases)
        
        # Scrape RBA Speeches
        rba_speeches = self._scrape_rba_speeches()
        articles.extend(rba_speeches)
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(articles)
        
        # Determine sentiment label
        if sentiment_score > 0.15:
            sentiment_label = "BULLISH"
        elif sentiment_score < -0.15:
            sentiment_label = "BEARISH"
        else:
            sentiment_label = "NEUTRAL"
        
        result = {
            'market': 'ASX',
            'article_count': len(articles),
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': sentiment_label,
            'articles': articles[:5],  # Top 5 for reports
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(articles, sentiment_score, 'ASX')
        }
        
        logger.info(f"✓ ASX Macro News: {len(articles)} articles, Sentiment: {sentiment_label} ({sentiment_score:+.3f})")
        
        return result
    
    def _scrape_fed_releases(self) -> List[Dict]:
        """Scrape Federal Reserve press releases"""
        articles = []
        
        try:
            logger.info("  Fetching Federal Reserve press releases...")
            
            response = self._safe_request(self.us_sources['FED_RELEASES'], "Fed releases")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find recent press releases
                release_links = soup.find_all('a', href=re.compile(r'/newsevents/pressreleases/'))
                
                for link in release_links[:5]:  # Top 5 recent
                    try:
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.federalreserve.gov{url}"
                        
                        # Check if relevant to monetary policy
                        if any(kw in title.lower() for kw in ['monetary', 'fomc', 'interest', 'rate', 'policy']):
                            articles.append({
                                'title': f"Fed: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'Federal Reserve (Official)',
                                'type': 'press_release'
                            })
                            logger.info(f"    ✓ Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Fed release: {e}")
                        continue
                
                logger.info(f"  ✓ Federal Reserve Releases: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape Fed releases: {e}")
        
        return articles
    
    def _scrape_fed_speeches(self) -> List[Dict]:
        """Scrape Federal Reserve speeches"""
        articles = []
        
        try:
            logger.info("  Fetching Federal Reserve speeches...")
            
            response = self._safe_request(self.us_sources['FED_SPEECHES'], "Fed speeches")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find recent speeches
                speech_links = soup.find_all('a', href=re.compile(r'/newsevents/speech/'))
                
                for link in speech_links[:3]:  # Top 3 recent
                    try:
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.federalreserve.gov{url}"
                        
                        articles.append({
                            'title': f"Fed Speech: {title}",
                            'url': url,
                            'published': datetime.now().isoformat(),
                            'source': 'Federal Reserve (Official)',
                            'type': 'speech'
                        })
                        logger.info(f"    ✓ Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Fed speech: {e}")
                        continue
                
                logger.info(f"  ✓ Federal Reserve Speeches: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape Fed speeches: {e}")
        
        return articles
    
    def _scrape_rba_releases(self) -> List[Dict]:
        """Scrape RBA media releases"""
        articles = []
        
        try:
            logger.info("  Fetching RBA media releases...")
            
            response = self._safe_request(self.aus_sources['RBA_MEDIA'], "RBA releases")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find media release links
                release_links = soup.find_all('a', href=re.compile(r'/media-releases/\d{4}/'))
                
                seen_urls = set()
                for link in release_links[:5]:  # Top 5 recent
                    try:
                        url = link.get('href', '')
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        title = link.get_text(strip=True)
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.rba.gov.au{url}"
                        
                        # Extract date from text if present
                        date_pattern = r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})'
                        date_match = re.search(date_pattern, title)
                        
                        if date_match:
                            date_str = date_match.group(1)
                            try:
                                parsed_date = datetime.strptime(date_str, '%d %B %Y')
                                published = parsed_date.isoformat()
                            except:
                                published = datetime.now().isoformat()
                            
                            # Clean title
                            title = title.replace(date_str, '').strip()
                        else:
                            published = datetime.now().isoformat()
                        
                        if title and len(title) > 10:
                            articles.append({
                                'title': f"RBA: {title}",
                                'url': url,
                                'published': published,
                                'source': 'Reserve Bank of Australia (Official)',
                                'type': 'media_release'
                            })
                            logger.info(f"    ✓ Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing RBA release: {e}")
                        continue
                
                logger.info(f"  ✓ RBA Media Releases: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape RBA releases: {e}")
        
        return articles
    
    def _scrape_rba_speeches(self) -> List[Dict]:
        """Scrape RBA speeches"""
        articles = []
        
        try:
            logger.info("  Fetching RBA speeches...")
            
            response = self._safe_request(self.aus_sources['RBA_SPEECHES'], "RBA speeches")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find speech links
                speech_links = soup.find_all('a', href=re.compile(r'/speeches/\d{4}/'))
                
                seen_urls = set()
                for link in speech_links[:3]:  # Top 3 recent
                    try:
                        url = link.get('href', '')
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        title = link.get_text(strip=True)
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.rba.gov.au{url}"
                        
                        articles.append({
                            'title': f"RBA Speech: {title}",
                            'url': url,
                            'published': datetime.now().isoformat(),
                            'source': 'Reserve Bank of Australia (Official)',
                            'type': 'speech'
                        })
                        logger.info(f"    ✓ Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing RBA speech: {e}")
                        continue
                
                logger.info(f"  ✓ RBA Speeches: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape RBA speeches: {e}")
        
        return articles
    
    def _analyze_sentiment(self, articles: List[Dict]) -> float:
        """
        Analyze sentiment of macro news articles
        
        Returns:
            Sentiment score between -1 (bearish) and +1 (bullish)
        """
        if not articles:
            return 0.0
        
        if finbert_analyzer is None:
            logger.warning("FinBERT not available, using keyword-based sentiment")
            return self._keyword_sentiment(articles)
        
        try:
            # Analyze each article title with FinBERT
            scores = []
            
            for article in articles:
                title = article.get('title', '')
                if not title:
                    continue
                
                try:
                    result = finbert_analyzer.analyze(title)
                    
                    if isinstance(result, dict) and 'sentiment' in result:
                        # Normalize sentiment to -1 to +1 range
                        sentiment = float(result['sentiment'])
                        scores.append(sentiment)
                    
                except Exception as e:
                    logger.debug(f"FinBERT analysis failed for article: {e}")
                    continue
            
            if scores:
                avg_sentiment = sum(scores) / len(scores)
                logger.info(f"  FinBERT sentiment: {avg_sentiment:+.3f} (from {len(scores)} articles)")
                return avg_sentiment
            else:
                return 0.0
        
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}, using fallback")
            return self._keyword_sentiment(articles)
    
    def _keyword_sentiment(self, articles: List[Dict]) -> float:
        """Fallback keyword-based sentiment analysis"""
        positive_words = ['rise', 'growth', 'strong', 'improve', 'positive', 'up', 'gain', 'optimistic']
        negative_words = ['fall', 'decline', 'weak', 'concern', 'negative', 'down', 'risk', 'pessimistic']
        
        score = 0.0
        count = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            
            pos_count = sum(1 for w in positive_words if w in title)
            neg_count = sum(1 for w in negative_words if w in title)
            
            if pos_count + neg_count > 0:
                article_score = (pos_count - neg_count) / (pos_count + neg_count)
                score += article_score
                count += 1
        
        return score / count if count > 0 else 0.0
    
    def _generate_summary(self, articles: List[Dict], sentiment_score: float, market: str) -> str:
        """Generate human-readable summary of macro news"""
        if not articles:
            return f"No recent {market} macro news available."
        
        sentiment_label = "bullish" if sentiment_score > 0.15 else "bearish" if sentiment_score < -0.15 else "neutral"
        
        summary = f"Analyzed {len(articles)} recent {market} central bank articles. "
        summary += f"Overall sentiment: {sentiment_label} ({sentiment_score:+.2f}). "
        
        # Highlight key topics
        all_titles = ' '.join([a.get('title', '') for a in articles]).lower()
        
        key_topics = []
        if market == 'US':
            if 'interest rate' in all_titles or 'rate' in all_titles:
                key_topics.append("interest rates")
            if 'fomc' in all_titles:
                key_topics.append("FOMC")
            if 'inflation' in all_titles:
                key_topics.append("inflation")
        else:  # ASX
            if 'cash rate' in all_titles or 'rate' in all_titles:
                key_topics.append("cash rate")
            if 'inflation' in all_titles:
                key_topics.append("inflation")
            if 'board' in all_titles:
                key_topics.append("RBA board")
        
        if key_topics:
            summary += f"Key topics: {', '.join(key_topics)}."
        
        return summary
    
    def _get_default_sentiment(self) -> Dict:
        """Return default sentiment when no data available"""
        return {
            'market': self.market,
            'article_count': 0,
            'sentiment_score': 0.0,
            'sentiment_label': 'NEUTRAL',
            'articles': [],
            'timestamp': datetime.now().isoformat(),
            'summary': f"No recent {self.market} macro news available."
        }


def test_macro_monitor():
    """Test function for macro news monitor"""
    print("="*80)
    print("TESTING MACRO NEWS MONITOR")
    print("="*80)
    
    # Test US
    print("\n1. Testing US Federal Reserve news...")
    us_monitor = MacroNewsMonitor(market='US')
    us_result = us_monitor.get_macro_sentiment()
    print(f"\nUS Result:")
    print(f"  Articles: {us_result['article_count']}")
    print(f"  Sentiment: {us_result['sentiment_label']} ({us_result['sentiment_score']:+.3f})")
    print(f"  Summary: {us_result['summary']}")
    
    # Test ASX
    print("\n2. Testing RBA news...")
    aus_monitor = MacroNewsMonitor(market='ASX')
    aus_result = aus_monitor.get_macro_sentiment()
    print(f"\nASX Result:")
    print(f"  Articles: {aus_result['article_count']}")
    print(f"  Sentiment: {aus_result['sentiment_label']} ({aus_result['sentiment_score']:+.3f})")
    print(f"  Summary: {aus_result['summary']}")
    
    print("\n✓ Test complete!")


if __name__ == '__main__':
    test_macro_monitor()
