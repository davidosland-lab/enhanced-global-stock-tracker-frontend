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
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup FinBERT path - prioritize local installation
FINBERT_PATH_RELATIVE = Path(__file__).resolve().parent.parent.parent / 'finbert_v4.4.4'
FINBERT_PATH_AATELS = Path(r'C:\Users\david\AATelS\finbert_v4.4.4')

# Use local installation FIRST, fallback to AATelS
if FINBERT_PATH_RELATIVE.exists():
    FINBERT_PATH = FINBERT_PATH_RELATIVE
    logger.info(f"[OK] Using FinBERT from local installation: {FINBERT_PATH}")
elif FINBERT_PATH_AATELS.exists():
    FINBERT_PATH = FINBERT_PATH_AATELS
    logger.info(f"[OK] Using FinBERT from AATelS (fallback): {FINBERT_PATH}")
else:
    FINBERT_PATH = None
    logger.warning(f"[!] FinBERT path not found. Tried:")
    logger.warning(f"    1. {FINBERT_PATH_RELATIVE} (local)")
    logger.warning(f"    2. {FINBERT_PATH_AATELS} (AATelS)")

# Add FinBERT to Python path and import
finbert_analyzer = None
if FINBERT_PATH and FINBERT_PATH.exists():
    FINBERT_MODELS_PATH = FINBERT_PATH / 'models'
    sys.path.insert(0, str(FINBERT_PATH))
    sys.path.insert(0, str(FINBERT_MODELS_PATH))
    logger.info(f"[OK] Added FinBERT to sys.path")
    
    try:
        from finbert_sentiment import FinBERTSentimentAnalyzer
        finbert_analyzer = FinBERTSentimentAnalyzer(model_name="ProsusAI/finbert")
        logger.info("[OK] FinBERT sentiment analyzer loaded successfully")
    except ImportError as e:
        finbert_analyzer = None
        logger.warning(f"[!] Failed to import FinBERT: {e}")
else:
    logger.warning("[!] FinBERT not available - using keyword-based sentiment")


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
        
        # UK sources
        self.uk_sources = {
            'BOE_NEWS': 'https://www.bankofengland.co.uk/news',
            'BOE_SPEECHES': 'https://www.bankofengland.co.uk/news/speeches',
            'GOV_UK_TREASURY': 'https://www.gov.uk/government/organisations/hm-treasury/news',
            'FCA_NEWS': 'https://www.fca.org.uk/news',
        }
        
        # Global news sources (Comprehensive Coverage)
        self.global_sources = {
            # Major International News Agencies
            'REUTERS_MARKETS': 'https://www.reuters.com/markets/',
            'REUTERS_US': 'https://www.reuters.com/world/us/',
            'REUTERS_WORLD': 'https://www.reuters.com/world/',
            'BBC_BUSINESS': 'https://www.bbc.com/news/business',
            'BBC_US': 'https://www.bbc.com/news/world-us-canada',
            'BBC_WORLD': 'https://www.bbc.com/news/world',
            'BLOOMBERG_MARKETS': 'https://www.bloomberg.com/markets',
            'AP_NEWS': 'https://apnews.com/business',
            'AFP_NEWS': 'https://www.afp.com/en/news-hub',
            'AL_JAZEERA': 'https://www.aljazeera.com/economy/',
            
            # Government & Policy
            'WHITE_HOUSE': 'https://www.whitehouse.gov/briefing-room/statements-releases/',
            'US_TREASURY': 'https://home.treasury.gov/news/press-releases',
            'US_STATE_DEPT': 'https://www.state.gov/press-releases/',
            
            # European Sources
            'EU_COMMISSION': 'https://ec.europa.eu/commission/presscorner/home/en',
            'ECB_NEWS': 'https://www.ecb.europa.eu/press/pr/date/html/index.en.html',
            'EUROPEAN_PARLIAMENT': 'https://www.europarl.europa.eu/news/en/press-room',
            
            # Asian Sources
            'PBOC_NEWS': 'http://www.pbc.gov.cn/en/3688006/index.html',
            'BOJ_NEWS': 'https://www.boj.or.jp/en/announcements/index.htm',
            'CHINA_DAILY': 'https://www.chinadaily.com.cn/business',
            'JAPAN_TIMES': 'https://www.japantimes.co.jp/business/',
            
            # Financial Institutions
            'IMF_NEWS': 'https://www.imf.org/en/News',
            'WORLD_BANK': 'https://www.worldbank.org/en/news',
            'BIS_NEWS': 'https://www.bis.org/press/index.htm',
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
            ],
            'UK': [
                'interest rate', 'rate hike', 'rate cut', 'bank of england', 'boe',
                'andrew bailey', 'mpc', 'monetary policy committee', 'inflation', 'cpi',
                'gdp', 'unemployment', 'gilt', 'sterling', 'brexit', 'treasury',
                'budget', 'fiscal policy', 'quantitative easing', 'recession', 'ftse'
            ],
            'GLOBAL': [
                # Geopolitical & Military Conflicts (Expanded)
                'war', 'warfare', 'conflict', 'military', 'invasion', 'occupation',
                'strike', 'airstrike', 'attack', 'bombing', 'missile', 'drone',
                'ceasefire', 'peace talks', 'negotiation', 'treaty',
                'ukraine', 'russia', 'putin', 'zelensky', 'crimea', 'donbas',
                'middle east', 'gaza', 'israel', 'palestine', 'hamas', 'hezbollah',
                'iran', 'tehran', 'nuclear', 'enrichment',
                'china', 'beijing', 'xi jinping', 'taiwan', 'strait', 'south china sea',
                'north korea', 'kim jong', 'pyongyang',
                'afghanistan', 'taliban', 'isis', 'terrorism', 'extremism',
                'syria', 'yemen', 'libya', 'sudan',
                'nato', 'alliance', 'military aid', 'weapons',
                
                # US Political Events & Policy (Expanded)
                'trump', 'biden', 'president', 'presidential', 'vice president',
                'white house', 'oval office', 'administration', 'cabinet',
                'executive order', 'presidential decree', 'veto',
                'congress', 'senate', 'house', 'speaker', 'majority leader',
                'election', 'campaign', 'primary', 'midterm',
                'supreme court', 'justice', 'ruling', 'decision',
                'impeachment', 'investigation', 'probe', 'scandal',
                'policy change', 'policy shift', 'regulatory', 'deregulation',
                'tariff', 'duty', 'trade policy', 'trade deal', 'trade agreement',
                'immigration', 'border', 'deportation', 'asylum', 'refugee',
                'sanctions', 'embargo', 'restrictions', 'penalties',
                'shutdown', 'government shutdown', 'debt ceiling', 'default',
                
                # International Trade & Economics (Expanded)
                'trade war', 'trade dispute', 'trade tensions',
                'protectionism', 'isolationism', 'nationalism',
                'wto', 'world trade organization',
                'free trade', 'trade agreement', 'bilateral', 'multilateral',
                'supply chain', 'logistics', 'shipping', 'freight',
                'disruption', 'bottleneck', 'shortage', 'scarcity',
                'inflation', 'deflation', 'stagflation', 'inflation shock',
                'recession', 'depression', 'slowdown', 'downturn', 'contraction',
                'recovery', 'rebound', 'expansion', 'boom',
                'correction', 'bear market', 'bull market',
                'gdp', 'growth', 'output', 'productivity',
                'unemployment', 'jobs', 'employment', 'labor market',
                'wages', 'salary', 'income', 'earnings',
                
                # Market Volatility & Risk (Expanded)
                'uncertainty', 'volatility', 'turbulence', 'instability',
                'risk', 'risk-off', 'risk-on', 'risk appetite',
                'concern', 'worry', 'anxiety', 'fear', 'panic',
                'selloff', 'sell-off', 'dumping', 'liquidation',
                'crash', 'collapse', 'plunge', 'tumble', 'slump',
                'turmoil', 'chaos', 'mayhem', 'disruption',
                'safe haven', 'flight to quality', 'defensive',
                'vix', 'volatility index', 'fear gauge',
                
                # Energy & Commodities (Expanded)
                'oil', 'crude', 'brent', 'wti', 'petroleum',
                'oil price', 'oil shock', 'energy crisis', 'energy security',
                'opec', 'opec+', 'cartel', 'production cut', 'output',
                'gas', 'natural gas', 'lng', 'pipeline',
                'coal', 'fossil fuel', 'renewable', 'solar', 'wind',
                'electricity', 'power', 'grid', 'blackout',
                'commodity', 'commodities', 'raw materials',
                'metals', 'gold', 'silver', 'copper', 'iron ore',
                'wheat', 'corn', 'soy', 'agriculture', 'food prices',
                
                # Financial Crises & Banking (Expanded)
                'banking crisis', 'bank failure', 'bank run',
                'financial crisis', 'credit crisis', 'liquidity crisis',
                'sovereign debt', 'debt crisis', 'default', 'restructuring',
                'contagion', 'spillover', 'systemic risk',
                'bailout', 'rescue', 'intervention', 'support package',
                'central bank', 'fed', 'ecb', 'boe', 'boj', 'pboc',
                'interest rate', 'rate hike', 'rate cut', 'monetary policy',
                'quantitative easing', 'qe', 'tightening', 'tapering',
                'reserve', 'liquidity', 'capital', 'leverage',
                
                # Currency & Exchange Rates (Expanded)
                'dollar', 'euro', 'pound', 'yen', 'yuan', 'renminbi',
                'currency', 'forex', 'fx', 'exchange rate',
                'devaluation', 'depreciation', 'appreciation',
                'peg', 'float', 'intervention',
                'reserve currency', 'safe haven currency',
                
                # European Issues (Expanded)
                'european union', 'eu', 'brussels', 'european commission',
                'brexit', 'uk exit', 'northern ireland',
                'eurozone', 'euro area', 'single currency',
                'greece', 'italy', 'spain', 'portugal',
                'germany', 'france', 'merkel', 'macron',
                'migration', 'refugee crisis', 'schengen',
                
                # Asian Economic Issues (Expanded)
                'china economy', 'chinese growth', 'china slowdown',
                'evergrande', 'property crisis', 'real estate',
                'japan deflation', 'abenomics', 'nikkei',
                'india', 'modi', 'rupee',
                'southeast asia', 'asean',
                'hong kong', 'singapore', 'financial hub',
                
                # Technology & Cyber (Expanded)
                'tech war', 'chip war', 'semiconductor',
                'huawei', 'tiktok', 'tech ban',
                'cyber attack', 'hack', 'ransomware',
                'data breach', 'privacy', 'surveillance',
                'ai', 'artificial intelligence', 'automation',
                
                # Climate & Environment (Expanded)
                'climate', 'climate change', 'global warming',
                'carbon', 'emissions', 'net zero',
                'cop', 'paris agreement', 'climate summit',
                'esg', 'green', 'sustainable',
                'natural disaster', 'extreme weather',
                'hurricane', 'typhoon', 'cyclone',
                'earthquake', 'tsunami', 'volcano',
                'flood', 'drought', 'wildfire',
                'famine', 'water crisis',
                
                # Health & Pandemic (Expanded)
                'pandemic', 'epidemic', 'outbreak',
                'covid', 'coronavirus', 'virus', 'disease',
                'lockdown', 'quarantine', 'restriction',
                'vaccine', 'vaccination', 'immunity',
                'who', 'world health organization',
                
                # Social & Political Unrest (Expanded)
                'protest', 'demonstration', 'riot',
                'civil unrest', 'uprising', 'revolution',
                'coup', 'military takeover', 'junta',
                'dictatorship', 'authoritarian', 'democracy',
                'election fraud', 'disputed election',
                'corruption', 'scandal', 'investigation',
                
                # International Organizations (Expanded)
                'united nations', 'un', 'security council',
                'imf', 'world bank', 'wto',
                'g7', 'g20', 'summit',
                'davos', 'world economic forum',
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
        elif self.market == 'UK':
            return self._get_uk_macro_sentiment()
        else:
            logger.warning(f"Unknown market: {self.market}")
            return self._get_default_sentiment()
    
    def _get_us_macro_sentiment(self) -> Dict:
        """Fetch and analyze US Federal Reserve news and global events"""
        articles = []
        
        # Scrape Fed Press Releases
        fed_releases = self._scrape_fed_releases()
        articles.extend(fed_releases)
        
        # Scrape Fed Speeches
        fed_speeches = self._scrape_fed_speeches()
        articles.extend(fed_speeches)
        
        # Scrape global news (geopolitical events, trade wars, crises)
        # US markets are affected by global events even though US is a major driver
        global_news = self._scrape_global_news()
        articles.extend(global_news)
        
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
            'top_articles': articles[:5],  # Alias for compatibility
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(articles, sentiment_score, 'US')
        }
        
        logger.info(f"[OK] US Macro News: {len(articles)} articles (Fed + Global), Sentiment: {sentiment_label} ({sentiment_score:+.3f})")
        
        return result
    
    def _get_aus_macro_sentiment(self) -> Dict:
        """Fetch and analyze RBA news and global events affecting ASX"""
        articles = []
        
        # Scrape RBA Media Releases
        rba_releases = self._scrape_rba_releases()
        articles.extend(rba_releases)
        
        # Scrape RBA Speeches
        rba_speeches = self._scrape_rba_speeches()
        articles.extend(rba_speeches)
        
        # Scrape global news (China trade, US policies, commodities, geopolitical events)
        # Australia is heavily impacted by global events affecting commodities and trade
        global_news = self._scrape_global_news()
        articles.extend(global_news)
        
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
            'top_articles': articles[:5],  # Alias for compatibility
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(articles, sentiment_score, 'ASX')
        }
        
        logger.info(f"[OK] ASX Macro News: {len(articles)} articles (RBA + Global), Sentiment: {sentiment_label} ({sentiment_score:+.3f})")
        
        return result
    
    def _get_uk_macro_sentiment(self) -> Dict:
        """Fetch and analyze UK (BoE/Treasury) and global news"""
        articles = []
        
        # Scrape UK Bank of England news
        boe_news = self._scrape_boe_news_rss()  # Use RSS for reliability
        articles.extend(boe_news)
        
        # Scrape UK Government Treasury news
        uk_gov_news = self._scrape_uk_gov_news()
        articles.extend(uk_gov_news)
        
        # Scrape global news (wars, crises, major events)
        global_news = self._scrape_global_news()
        articles.extend(global_news)
        
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
            'market': 'UK',
            'article_count': len(articles),
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': sentiment_label,
            'articles': articles[:5],  # Top 5 for reports
            'top_articles': articles[:5],  # Alias for compatibility
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(articles, sentiment_score, 'UK')
        }
        
        logger.info(f"[OK] UK Macro News: {len(articles)} articles, Sentiment: {sentiment_label} ({sentiment_score:+.3f})")
        
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
                            logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Fed release: {e}")
                        continue
                
                logger.info(f"  [OK] Federal Reserve Releases: {len(articles)} articles")
        
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
                        logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Fed speech: {e}")
                        continue
                
                logger.info(f"  [OK] Federal Reserve Speeches: {len(articles)} articles")
        
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
                            logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing RBA release: {e}")
                        continue
                
                logger.info(f"  [OK] RBA Media Releases: {len(articles)} articles")
        
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
                        logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing RBA speech: {e}")
                        continue
                
                logger.info(f"  [OK] RBA Speeches: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape RBA speeches: {e}")
        
        return articles
    
    def _scrape_uk_boe_news(self) -> List[Dict]:
        """Scrape Bank of England news and speeches"""
        articles = []
        
        try:
            logger.info("  Fetching Bank of England news...")
            
            response = self._safe_request(self.uk_sources['BOE_NEWS'], "BoE news")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find news articles
                news_items = soup.find_all('article', limit=5) or soup.find_all('div', class_=re.compile(r'news|article'), limit=5)
                
                for item in news_items[:3]:  # Top 3 recent
                    try:
                        title_elem = item.find(['h2', 'h3', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link_elem = item.find('a', href=True)
                            url = link_elem['href'] if link_elem else ''
                            
                            if url and not url.startswith('http'):
                                url = f"https://www.bankofengland.co.uk{url}"
                            
                            # Check if relevant to macro keywords
                            if any(kw in title.lower() for kw in self.macro_keywords['UK']):
                                articles.append({
                                    'title': f"BoE: {title}",
                                    'url': url,
                                    'published': datetime.now().isoformat(),
                                    'source': 'Bank of England (Official)',
                                    'type': 'central_bank'
                                })
                                logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing BoE news: {e}")
                        continue
                
                logger.info(f"  [OK] Bank of England News: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape BoE news: {e}")
        
        return articles
    
    def _scrape_boe_news_rss(self) -> List[Dict]:
        """
        Scrape Bank of England news via RSS feed (more reliable than HTML scraping)
        
        BoE RSS feeds are stable and provide structured data without HTML parsing issues.
        """
        articles = []
        
        try:
            # Try to import feedparser
            try:
                import feedparser
            except ImportError:
                logger.warning("  feedparser not installed, falling back to HTML scraping")
                return self._scrape_uk_boe_news()
            
            logger.info("  Fetching Bank of England news (RSS)...")
            
            # Parse BoE news RSS feed
            feed_url = 'https://www.bankofengland.co.uk/news.rss'
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logger.warning(f"    No entries in BoE RSS feed")
                return self._scrape_uk_boe_news()
            
            for entry in feed.entries[:10]:  # Top 10 recent articles
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')
                    published = entry.get('published', datetime.now().isoformat())
                    summary = entry.get('summary', '')
                    
                    if not title or not url:
                        continue
                    
                    # Filter for relevance
                    text = f"{title} {summary}".lower()
                    relevant_keywords = [
                        'interest rate', 'bank rate', 'monetary policy', 
                        'inflation', 'mpc', 'committee', 'andrew bailey',
                        'governor', 'financial stability', 'economic outlook',
                        'quantitative', 'gilt', 'forecast', 'decision'
                    ]
                    
                    is_relevant = any(kw in text for kw in relevant_keywords)
                    
                    # Include if relevant or if we have few articles
                    if is_relevant or len(articles) < 5:
                        articles.append({
                            'title': f"BoE: {title}",
                            'url': url,
                            'published': published,
                            'source': 'Bank of England (Official)',
                            'type': 'central_bank',
                            'summary': summary[:200] if summary else ''
                        })
                        logger.debug(f"    Added: {title[:60]}...")
                
                except Exception as e:
                    logger.debug(f"    Error parsing RSS entry: {e}")
                    continue
            
            logger.info(f"  [OK] Bank of England News (RSS): {len(articles)} articles")
        
        except Exception as e:
            logger.error(f"  [ERROR] BoE RSS scraping failed: {e}")
            return self._scrape_uk_boe_news()
        
        return articles
    
    def _scrape_uk_gov_news(self) -> List[Dict]:
        """Scrape UK Government Treasury news"""
        articles = []
        
        try:
            logger.info("  Fetching UK Treasury news...")
            
            response = self._safe_request(self.uk_sources['GOV_UK_TREASURY'], "UK Treasury")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find government announcements
                announcements = soup.find_all('a', class_=re.compile(r'gem-c-document-list__item-title'), limit=5)
                
                if not announcements:
                    announcements = soup.find_all('h3', limit=5)
                
                for item in announcements[:3]:  # Top 3 recent
                    try:
                        if item.name == 'a':
                            title = item.get_text(strip=True)
                            url = item.get('href', '')
                        else:
                            link = item.find('a', href=True)
                            title = item.get_text(strip=True)
                            url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.gov.uk{url}"
                        
                        # Check if relevant to fiscal/economic policy
                        if any(kw in title.lower() for kw in ['budget', 'tax', 'spending', 'fiscal', 'economy', 'inflation', 'growth']):
                            articles.append({
                                'title': f"UK Treasury: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'HM Treasury (Official)',
                                'type': 'government'
                            })
                            logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Treasury news: {e}")
                        continue
                
                logger.info(f"  [OK] UK Treasury News: {len(articles)} articles")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape UK Treasury news: {e}")
        
        return articles
    
    def _scrape_global_news(self) -> List[Dict]:
        """
        Scrape comprehensive global news from major international sources
        
        Coverage:
        - Geopolitical events (wars, conflicts, military actions)
        - US political events (admin policy, tariffs, executive orders)
        - International trade disputes and agreements
        - European economic/political issues (EU, Brexit, ECB)
        - Asian economic developments (China, Japan, India)
        - Energy crises and commodity shocks
        - Climate events and natural disasters
        - Financial crises and banking issues
        - Currency crises and debt defaults
        - Technology wars and cyber attacks
        - Health pandemics and epidemics
        - Social unrest and political upheaval
        """
        articles = []
        
        try:
            logger.info("  Fetching comprehensive global news (all major global issues)...")
            
            # Source 1: Reuters Markets
            response = self._safe_request(self.global_sources['REUTERS_MARKETS'], "Reuters markets")
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find top headlines
                headlines = soup.find_all(['h3', 'h2'], class_=re.compile(r'headline|title'), limit=10)
                
                for headline in headlines[:5]:  # Top 5
                    try:
                        title = headline.get_text(strip=True)
                        link = headline.find_parent('a', href=True) or headline.find('a', href=True)
                        url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.reuters.com{url}"
                        
                        # Check if relevant to global macro keywords
                        title_lower = title.lower()
                        if any(kw in title_lower for kw in self.macro_keywords['GLOBAL']):
                            articles.append({
                                'title': f"Global: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'Reuters (Global)',
                                'type': 'global_event'
                            })
                            logger.info(f"    [OK] Found: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Reuters headline: {e}")
                        continue
            
            # Source 2: Reuters US (for US political news)
            response_us = self._safe_request(self.global_sources.get('REUTERS_US', ''), "Reuters US")
            
            if response_us:
                soup = BeautifulSoup(response_us.text, 'html.parser')
                
                # Find US political headlines
                headlines = soup.find_all(['h3', 'h2'], class_=re.compile(r'headline|title'), limit=10)
                
                for headline in headlines[:3]:  # Top 3 US political
                    try:
                        title = headline.get_text(strip=True)
                        link = headline.find_parent('a', href=True) or headline.find('a', href=True)
                        url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.reuters.com{url}"
                        
                        # Check if relevant to US political/economic events
                        title_lower = title.lower()
                        us_keywords = ['trump', 'president', 'white house', 'tariff', 'trade', 'policy', 
                                      'administration', 'executive order', 'sanctions', 'immigration']
                        if any(kw in title_lower for kw in us_keywords):
                            articles.append({
                                'title': f"US Political: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'Reuters (US Political)',
                                'type': 'us_political'
                            })
                            logger.info(f"    [OK] Found US: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Reuters US headline: {e}")
                        continue
            
            # Source 3: BBC Business
            response_bbc = self._safe_request(self.global_sources['BBC_BUSINESS'], "BBC Business")
            
            if response_bbc:
                soup = BeautifulSoup(response_bbc.text, 'html.parser')
                
                # Find BBC headlines
                headlines = soup.find_all(['h2', 'h3'], limit=8)
                
                for headline in headlines[:3]:  # Top 3 BBC
                    try:
                        title = headline.get_text(strip=True)
                        link = headline.find_parent('a', href=True) or headline.find('a', href=True)
                        url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.bbc.com{url}"
                        
                        # Check if relevant to global macro keywords
                        title_lower = title.lower()
                        if any(kw in title_lower for kw in self.macro_keywords['GLOBAL']):
                            articles.append({
                                'title': f"Global: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'BBC News (Business)',
                                'type': 'global_event'
                            })
                            logger.info(f"    [OK] Found BBC: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing BBC headline: {e}")
                        continue
            
            # Source 4: BBC World (for geopolitical events)
            response_world = self._safe_request(self.global_sources.get('BBC_WORLD', ''), "BBC World")
            
            if response_world:
                soup = BeautifulSoup(response_world.text, 'html.parser')
                headlines = soup.find_all(['h2', 'h3'], limit=10)
                
                for headline in headlines[:3]:
                    try:
                        title = headline.get_text(strip=True)
                        link = headline.find_parent('a', href=True) or headline.find('a', href=True)
                        url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.bbc.com{url}"
                        
                        title_lower = title.lower()
                        # Focus on geopolitical keywords
                        geopolitical_keywords = ['war', 'conflict', 'military', 'attack', 'crisis', 
                                               'china', 'russia', 'ukraine', 'iran', 'nuclear',
                                               'election', 'coup', 'protest', 'unrest']
                        if any(kw in title_lower for kw in geopolitical_keywords):
                            articles.append({
                                'title': f"Geopolitical: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'BBC World News',
                                'type': 'geopolitical'
                            })
                            logger.info(f"    [OK] Found Geopolitical: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing BBC World: {e}")
                        continue
            
            # Source 5: Al Jazeera Economics (Middle East perspective)
            response_aj = self._safe_request(self.global_sources.get('AL_JAZEERA', ''), "Al Jazeera")
            
            if response_aj:
                soup = BeautifulSoup(response_aj.text, 'html.parser')
                headlines = soup.find_all(['h2', 'h3', 'h4'], limit=8)
                
                for headline in headlines[:2]:  # Top 2 from Al Jazeera
                    try:
                        title = headline.get_text(strip=True)
                        link = headline.find_parent('a', href=True) or headline.find('a', href=True)
                        url = link['href'] if link else ''
                        
                        if url and not url.startswith('http'):
                            url = f"https://www.aljazeera.com{url}"
                        
                        title_lower = title.lower()
                        # Focus on energy, Middle East, Asia
                        regional_keywords = ['oil', 'opec', 'energy', 'middle east', 'iran', 
                                           'china', 'india', 'asia', 'commodity']
                        if any(kw in title_lower for kw in regional_keywords):
                            articles.append({
                                'title': f"Regional: {title}",
                                'url': url,
                                'published': datetime.now().isoformat(),
                                'source': 'Al Jazeera (Regional)',
                                'type': 'regional_event'
                            })
                            logger.info(f"    [OK] Found Regional: {title[:60]}...")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing Al Jazeera: {e}")
                        continue
            
            logger.info(f"  [OK] Global News: {len(articles)} articles (Reuters + BBC + Al Jazeera + Geopolitical)")
        
        except Exception as e:
            logger.warning(f"  Failed to scrape global news: {e}")
        
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
                    # Use analyze_text method from FinBERTSentimentAnalyzer
                    result = finbert_analyzer.analyze_text(title)
                    
                    if isinstance(result, dict):
                        # FinBERT returns 'label' (positive/negative/neutral) and 'score'
                        # Convert to -1 to +1 range
                        label = result.get('label', 'neutral').lower()
                        confidence = result.get('score', 0.5)
                        
                        if label == 'positive':
                            sentiment = confidence
                        elif label == 'negative':
                            sentiment = -confidence
                        else:  # neutral
                            sentiment = 0.0
                        
                        scores.append(sentiment)
                        article['sentiment'] = sentiment  # Store in article for later display
                    
                except Exception as e:
                    logger.debug(f"FinBERT analysis failed for article: {e}")
                    continue
            
            if scores:
                avg_sentiment = sum(scores) / len(scores)
                logger.info(f"  FinBERT sentiment: {avg_sentiment:+.3f} (from {len(scores)} articles)")
                return avg_sentiment
            else:
                logger.warning("No scores generated, using fallback")
                return self._keyword_sentiment(articles)
        
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
    
    print("\n[OK] Test complete!")


if __name__ == '__main__':
    test_macro_monitor()
