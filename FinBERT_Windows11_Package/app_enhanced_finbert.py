#!/usr/bin/env python3
"""
Enhanced FinBERT Trading System with Automatic Data Feeds
Includes: Government announcements, economic indicators, geopolitical events, 
interest rates, bond yields, and customizable historical periods
"""

import os
import sys
import json
import time
import logging
import warnings
import datetime as dt
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_finbert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import standard libraries
import numpy as np
import pandas as pd
import yfinance as yf
import requests
import feedparser
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from tqdm import tqdm
from datetime import datetime, timedelta

# Import ML libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif

# Try to import FinBERT dependencies
FINBERT_AVAILABLE = False
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"PyTorch device: {device}")
    
    try:
        model_name = "ProsusAI/finbert"
        cache_dir = "./models"
        
        logger.info("Loading FinBERT model...")
        FINBERT_TOKENIZER = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        FINBERT_MODEL = AutoModelForSequenceClassification.from_pretrained(
            model_name, cache_dir=cache_dir
        ).to(device)
        FINBERT_MODEL.eval()
        FINBERT_AVAILABLE = True
        logger.info("✓ FinBERT model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load FinBERT model: {e}")
        
except ImportError as e:
    logger.warning(f"FinBERT dependencies not available: {e}")

# Flask app
app = Flask(__name__)
CORS(app)

# Configuration
CACHE_DIR = Path("./cache")
CACHE_DIR.mkdir(exist_ok=True)

@dataclass
class DataConfig:
    """Configuration for data fetching"""
    historical_periods = {
        '1mo': '1 Month',
        '3mo': '3 Months',
        '6mo': '6 Months',
        '1y': '1 Year',
        '2y': '2 Years',
        '5y': '5 Years',
        'max': 'Maximum Available'
    }
    
    # API endpoints (free tier)
    news_apis = {
        'newsapi': 'https://newsapi.org/v2/everything',  # Requires free API key
        'alphavantage_news': 'https://www.alphavantage.co/query',  # Free tier available
        'finnhub': 'https://finnhub.io/api/v1/news',  # Free tier available
    }
    
    # Economic data sources (no API key required)
    economic_feeds = {
        'fed_rates': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates',
        'treasury_yields': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates',
        'fred_api': 'https://api.stlouisfed.org/fred/series/observations',  # Fed economic data
    }
    
    # RSS Feeds for real-time updates (no API needed)
    rss_feeds = {
        'central_banks': [
            'https://www.federalreserve.gov/feeds/press_all.xml',  # Fed announcements
            'https://www.ecb.europa.eu/rss/press.xml',  # ECB announcements
            'https://www.rba.gov.au/rss/rss.xml',  # RBA announcements
            'https://www.bankofengland.co.uk/rss/news',  # BoE announcements
        ],
        'economic_news': [
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://www.investing.com/rss/news.rss',
        ],
        'geopolitical': [
            'https://www.cfr.org/rss.xml',  # Council on Foreign Relations
            'https://www.reuters.com/rssFeed/worldNews',
            'https://feeds.bbci.co.uk/news/world/rss.xml',
        ]
    }

class EnhancedDataFetcher:
    """Fetches all types of market data automatically"""
    
    def __init__(self):
        self.config = DataConfig()
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Fetch historical stock data with custom period"""
        try:
            logger.info(f"Fetching {period} of data for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Add additional data
            info = ticker.info
            df['MarketCap'] = info.get('marketCap', 0)
            df['PE_Ratio'] = info.get('trailingPE', 0)
            df['Beta'] = info.get('beta', 1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def get_treasury_yields(self) -> Dict[str, float]:
        """Fetch current US Treasury yields"""
        try:
            # Using FRED API (Federal Reserve Economic Data) - no key required for basic use
            yields = {}
            
            # Key treasury maturities
            series_ids = {
                'DGS2': '2_year',   # 2-Year Treasury
                'DGS10': '10_year',  # 10-Year Treasury
                'DGS30': '30_year',  # 30-Year Treasury
                'DFEDTARU': 'fed_funds'  # Federal Funds Rate
            }
            
            for series_id, name in series_ids.items():
                url = f"https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': series_id,
                    'api_key': 'demo',  # Demo key for basic access
                    'file_type': 'json',
                    'limit': 1,
                    'sort_order': 'desc'
                }
                
                try:
                    response = self.session.get(url, params=params, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if 'observations' in data and data['observations']:
                            yields[name] = float(data['observations'][0].get('value', 0))
                except:
                    yields[name] = 0
            
            # Calculate yield curve slope (10Y - 2Y)
            if '10_year' in yields and '2_year' in yields:
                yields['yield_curve_slope'] = yields['10_year'] - yields['2_year']
            
            logger.info(f"Treasury yields fetched: {yields}")
            return yields
            
        except Exception as e:
            logger.error(f"Error fetching treasury yields: {e}")
            return {}
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """Fetch key economic indicators"""
        indicators = {}
        
        try:
            # VIX (Fear Index)
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="1d")
            if not vix_hist.empty:
                indicators['vix'] = float(vix_hist['Close'].iloc[-1])
                indicators['vix_change'] = float(vix_hist['Close'].pct_change().iloc[-1])
            
            # Dollar Index
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_hist = dxy.history(period="1d")
            if not dxy_hist.empty:
                indicators['dollar_index'] = float(dxy_hist['Close'].iloc[-1])
            
            # Gold (Safe Haven)
            gold = yf.Ticker("GC=F")
            gold_hist = gold.history(period="1d")
            if not gold_hist.empty:
                indicators['gold_price'] = float(gold_hist['Close'].iloc[-1])
            
            # Oil (Economic indicator)
            oil = yf.Ticker("CL=F")
            oil_hist = oil.history(period="1d")
            if not oil_hist.empty:
                indicators['oil_price'] = float(oil_hist['Close'].iloc[-1])
            
            # Major indices for context
            indices = {
                '^GSPC': 'sp500',
                '^DJI': 'dow_jones',
                '^IXIC': 'nasdaq',
                '^FTSE': 'ftse100',
                '^N225': 'nikkei'
            }
            
            for ticker_symbol, name in indices.items():
                try:
                    index = yf.Ticker(ticker_symbol)
                    hist = index.history(period="1d")
                    if not hist.empty:
                        indicators[f'{name}_close'] = float(hist['Close'].iloc[-1])
                        indicators[f'{name}_change'] = float(hist['Close'].pct_change().iloc[-1])
                except:
                    pass
            
            logger.info(f"Economic indicators fetched: {len(indicators)} indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {e}")
            return indicators
    
    def get_central_bank_news(self) -> List[Dict]:
        """Fetch central bank announcements"""
        all_news = []
        
        for feed_url in self.config.rss_feeds['central_banks']:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Last 5 entries
                    news_item = {
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'link': entry.get('link', ''),
                        'source': 'Central Bank',
                        'category': 'monetary_policy'
                    }
                    all_news.append(news_item)
            except Exception as e:
                logger.error(f"Error fetching central bank news: {e}")
        
        return all_news
    
    def get_geopolitical_events(self) -> List[Dict]:
        """Fetch geopolitical news and events"""
        events = []
        
        # Keywords for geopolitical events
        keywords = [
            'war', 'conflict', 'sanctions', 'trade war', 'tariff',
            'election', 'coup', 'crisis', 'nuclear', 'missile',
            'invasion', 'military', 'nato', 'china', 'russia'
        ]
        
        for feed_url in self.config.rss_feeds['geopolitical']:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    
                    # Check if it's relevant geopolitical news
                    if any(keyword in title or keyword in summary for keyword in keywords):
                        events.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'link': entry.get('link', ''),
                            'source': 'Geopolitical',
                            'category': 'geopolitical_risk'
                        })
            except Exception as e:
                logger.error(f"Error fetching geopolitical events: {e}")
        
        return events
    
    def get_market_news(self, symbol: str) -> List[Dict]:
        """Fetch news for specific stock"""
        news = []
        
        try:
            # Yahoo Finance news for the symbol
            ticker = yf.Ticker(symbol)
            yahoo_news = ticker.news if hasattr(ticker, 'news') else []
            
            for item in yahoo_news[:10]:
                news.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat(),
                    'link': item.get('link', ''),
                    'source': 'Yahoo Finance',
                    'category': 'company_news'
                })
            
            # Add RSS feed news
            feed = feedparser.parse(f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}')
            for entry in feed.entries[:5]:
                news.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'link': entry.get('link', ''),
                    'source': 'Yahoo RSS',
                    'category': 'company_news'
                })
                
        except Exception as e:
            logger.error(f"Error fetching market news for {symbol}: {e}")
        
        return news

class EnhancedSentimentAnalyzer:
    """Advanced sentiment analysis with FinBERT and fallback"""
    
    def __init__(self):
        self.use_finbert = FINBERT_AVAILABLE
        if self.use_finbert:
            self.model = FINBERT_MODEL
            self.tokenizer = FINBERT_TOKENIZER
            self.device = device
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        if not text:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "score": 0.0}
        
        if self.use_finbert:
            try:
                # FinBERT analysis
                inputs = self.tokenizer(
                    text, 
                    return_tensors="pt", 
                    truncation=True, 
                    max_length=512,
                    padding=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    predictions = predictions.cpu().numpy()[0]
                
                return {
                    "positive": float(predictions[0]),
                    "negative": float(predictions[1]),
                    "neutral": float(predictions[2]),
                    "score": float(predictions[0] - predictions[1])
                }
            except Exception as e:
                logger.error(f"FinBERT analysis failed: {e}")
        
        # Fallback to keyword analysis
        return self._keyword_sentiment(text)
    
    def _keyword_sentiment(self, text: str) -> Dict[str, float]:
        """Fallback keyword-based sentiment"""
        text_lower = text.lower()
        
        positive_words = {
            'gain', 'rise', 'surge', 'profit', 'beat', 'strong', 'buy',
            'upgrade', 'positive', 'growth', 'bullish', 'rally', 'record'
        }
        
        negative_words = {
            'loss', 'fall', 'drop', 'decline', 'miss', 'weak', 'sell',
            'downgrade', 'negative', 'bearish', 'crash', 'crisis', 'risk'
        }
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "score": 0.0}
        
        pos_ratio = pos_count / total
        neg_ratio = neg_count / total
        
        return {
            "positive": pos_ratio * 0.7 + 0.15,
            "negative": neg_ratio * 0.7 + 0.15,
            "neutral": 1 - (pos_ratio + neg_ratio) * 0.7,
            "score": pos_ratio - neg_ratio
        }
    
    def analyze_news_batch(self, news_items: List[Dict]) -> Dict[str, float]:
        """Analyze batch of news items"""
        if not news_items:
            return {
                'overall_sentiment': 0.0,
                'positive_ratio': 0.33,
                'negative_ratio': 0.33,
                'volatility': 0.0
            }
        
        sentiments = []
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            sentiment = self.analyze_text(text)
            sentiments.append(sentiment['score'])
        
        return {
            'overall_sentiment': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'positive_ratio': sum(1 for s in sentiments if s > 0.1) / len(sentiments),
            'negative_ratio': sum(1 for s in sentiments if s < -0.1) / len(sentiments),
            'volatility': np.std(sentiments) if len(sentiments) > 1 else 0
        }

class EnhancedMLModel:
    """Advanced ML model with multiple data sources"""
    
    def __init__(self):
        self.data_fetcher = EnhancedDataFetcher()
        self.sentiment_analyzer = EnhancedSentimentAnalyzer()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
    
    def prepare_enhanced_features(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Prepare comprehensive feature set"""
        logger.info(f"Preparing enhanced features for {symbol} over {period}")
        
        # Get stock data
        df = self.data_fetcher.get_stock_data(symbol, period)
        if df.empty:
            return pd.DataFrame()
        
        # Basic price features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Technical indicators
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'] = self._calculate_macd(df['Close'])
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            if len(df) >= period:
                df[f'SMA_{period}'] = df['Close'].rolling(period).mean()
                df[f'Price_to_SMA_{period}'] = df['Close'] / df[f'SMA_{period}']
        
        # Volatility measures
        df['Volatility_20'] = df['Returns'].rolling(20).std()
        df['Volatility_60'] = df['Returns'].rolling(60).std()
        df['ATR'] = self._calculate_atr(df)
        
        # Bollinger Bands
        df['BB_upper'], df['BB_lower'] = self._calculate_bollinger_bands(df['Close'])
        df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # Get economic indicators
        econ_data = self.data_fetcher.get_economic_indicators()
        for key, value in econ_data.items():
            df[f'econ_{key}'] = value
        
        # Get treasury yields
        yields = self.data_fetcher.get_treasury_yields()
        for key, value in yields.items():
            df[f'yield_{key}'] = value
        
        # Get news and sentiment
        all_news = []
        all_news.extend(self.data_fetcher.get_market_news(symbol))
        all_news.extend(self.data_fetcher.get_central_bank_news())
        all_news.extend(self.data_fetcher.get_geopolitical_events())
        
        # Analyze sentiment
        sentiment_data = self.sentiment_analyzer.analyze_news_batch(all_news)
        for key, value in sentiment_data.items():
            df[f'sentiment_{key}'] = value
        
        # Market regime features
        df['Market_Regime'] = self._identify_market_regime(df)
        
        # Target variable (next day return direction)
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info(f"Prepared {len(df)} samples with {len(df.columns)} features")
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        return exp1 - exp2
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        return upper, lower
    
    def _identify_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """Identify market regime (trending/ranging/volatile)"""
        returns = df['Returns'].rolling(20)
        
        # Calculate regime metrics
        trend_strength = abs(returns.mean() / returns.std())
        
        regime = pd.Series(index=df.index, dtype=int)
        regime[trend_strength > 0.5] = 1  # Trending
        regime[trend_strength <= 0.5] = 0  # Ranging
        regime[returns.std() > returns.std().quantile(0.8)] = 2  # High volatility
        
        return regime
    
    def train_enhanced_model(self, symbol: str, period: str = "6mo") -> Dict:
        """Train model with enhanced features"""
        logger.info(f"Training enhanced model for {symbol} with {period} of data")
        
        # Prepare features
        df = self.prepare_enhanced_features(symbol, period)
        if df.empty or len(df) < 100:
            return {"error": "Insufficient data for training"}
        
        # Select features (exclude target and non-numeric)
        feature_cols = [col for col in df.columns if col not in ['Target', 'Date'] 
                       and df[col].dtype in ['float64', 'int64']]
        
        X = df[feature_cols]
        y = df['Target']
        
        # Feature selection (keep top features)
        selector = SelectKBest(f_classif, k=min(30, len(feature_cols)))
        X_selected = selector.fit_transform(X, y)
        selected_features = [feature_cols[i] for i in selector.get_support(indices=True)]
        
        # Split data
        split_idx = int(len(X_selected) * 0.8)
        X_train, X_test = X_selected[:split_idx], X_selected[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train ensemble model
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            ),
            'gradient_boost': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        results = {}
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            results[name] = {
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score)
            }
            
            if test_score > best_score:
                best_score = test_score
                best_model = model
        
        # Store best model
        self.models[symbol] = best_model
        self.scalers[symbol] = scaler
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            importance = pd.DataFrame({
                'feature': selected_features,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            self.feature_importance[symbol] = importance.head(15).to_dict('records')
        
        return {
            "symbol": symbol,
            "period": period,
            "samples": len(df),
            "features": len(selected_features),
            "models": results,
            "best_model": max(results, key=lambda x: results[x]['test_accuracy']),
            "best_accuracy": float(best_score),
            "feature_importance": self.feature_importance.get(symbol, []),
            "data_sources": {
                "stock_data": True,
                "economic_indicators": len(econ_data) > 0,
                "treasury_yields": len(yields) > 0,
                "news_sentiment": len(all_news) > 0,
                "finbert_enabled": FINBERT_AVAILABLE
            }
        }
    
    def predict_enhanced(self, symbol: str, period: str = "1mo") -> Dict:
        """Make enhanced prediction"""
        if symbol not in self.models:
            # Train if not exists
            result = self.train_enhanced_model(symbol, period)
            if "error" in result:
                return result
        
        # Get latest features
        df = self.prepare_enhanced_features(symbol, "1mo")
        if df.empty:
            return {"error": "No data available for prediction"}
        
        # Prepare features
        feature_cols = [col for col in df.columns if col not in ['Target', 'Date'] 
                       and df[col].dtype in ['float64', 'int64']]
        
        X = df[feature_cols].iloc[-1:].values
        
        # Scale and predict
        X_scaled = self.scalers[symbol].transform(X)
        prediction = self.models[symbol].predict(X_scaled)[0]
        probability = self.models[symbol].predict_proba(X_scaled)[0]
        
        # Get current market data
        latest = df.iloc[-1]
        
        return {
            "symbol": symbol,
            "prediction": "BUY" if prediction == 1 else "SELL",
            "confidence": float(max(probability)),
            "probability_up": float(probability[1]),
            "probability_down": float(probability[0]),
            "current_price": float(latest.get('Close', 0)),
            "technical_indicators": {
                "rsi": float(latest.get('RSI', 50)),
                "macd": float(latest.get('MACD', 0)),
                "volatility": float(latest.get('Volatility_20', 0)),
                "volume_ratio": float(latest.get('Volume_Ratio', 1))
            },
            "market_data": {
                "vix": float(latest.get('econ_vix', 0)),
                "dollar_index": float(latest.get('econ_dollar_index', 0)),
                "sp500_change": float(latest.get('econ_sp500_change', 0))
            },
            "yields": {
                "2_year": float(latest.get('yield_2_year', 0)),
                "10_year": float(latest.get('yield_10_year', 0)),
                "yield_curve": float(latest.get('yield_yield_curve_slope', 0))
            },
            "sentiment": {
                "overall": float(latest.get('sentiment_overall_sentiment', 0)),
                "volatility": float(latest.get('sentiment_volatility', 0))
            },
            "timestamp": datetime.now().isoformat()
        }

# Initialize components
ml_model = EnhancedMLModel()

# HTML Template with period selector
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced FinBERT Trading System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .status-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .status-item .label {
            color: #6c757d;
            font-size: 12px;
            margin-bottom: 5px;
        }
        
        .status-item .value {
            font-size: 18px;
            font-weight: 600;
        }
        
        .status-active {
            color: #10b981;
        }
        
        .status-inactive {
            color: #ef4444;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #1e3c72;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #495057;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 35px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .results {
            margin-top: 25px;
        }
        
        .result-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .result-label {
            color: #6c757d;
            font-size: 14px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .result-value {
            color: #212529;
            font-size: 20px;
            font-weight: 600;
        }
        
        .prediction-buy {
            color: #10b981;
        }
        
        .prediction-sell {
            color: #ef4444;
        }
        
        .data-sources {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        
        .data-source {
            background: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        
        .data-source.active {
            border-color: #10b981;
            background: #f0fdf4;
        }
        
        .data-source.inactive {
            border-color: #ef4444;
            background: #fef2f2;
        }
        
        .indicator-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .indicator {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .indicator-label {
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .indicator-value {
            font-size: 18px;
            font-weight: 600;
            color: #212529;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
            transition: width 0.5s ease;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .spinner {
            border: 3px solid #e9ecef;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        
        .feature-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .feature-name {
            color: #6c757d;
            font-size: 12px;
        }
        
        .feature-importance {
            color: #667eea;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced FinBERT Trading System</h1>
            <p style="color: #6c757d; margin-bottom: 20px;">
                Automatic data feeds: Government announcements, Economic indicators, Geopolitical events, Interest rates, Bond yields
            </p>
            <div class="status-grid" id="statusGrid">
                <div class="status-item">
                    <div class="label">FinBERT Status</div>
                    <div class="value" id="finbertStatus">Checking...</div>
                </div>
                <div class="status-item">
                    <div class="label">Data Sources</div>
                    <div class="value" id="dataSourcesCount">0</div>
                </div>
                <div class="status-item">
                    <div class="label">Last Update</div>
                    <div class="value" id="lastUpdate">--:--</div>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Train Enhanced Model</h2>
                <div class="form-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="trainSymbol" placeholder="e.g., AAPL, TSLA, CBA.AX" value="AAPL">
                </div>
                <div class="form-group">
                    <label>Historical Period</label>
                    <select id="trainPeriod">
                        <option value="1mo">1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo" selected>6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="2y">2 Years</option>
                        <option value="5y">5 Years</option>
                        <option value="max">Maximum Available</option>
                    </select>
                </div>
                <button class="btn" onclick="trainModel()">
                    🧠 Train Model with All Data Sources
                </button>
                <div id="trainResults" class="results"></div>
            </div>
            
            <div class="card">
                <h2>🔮 Make Prediction</h2>
                <div class="form-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="predictSymbol" placeholder="e.g., AAPL, TSLA, CBA.AX" value="AAPL">
                </div>
                <div class="form-group">
                    <label>Analysis Period</label>
                    <select id="predictPeriod">
                        <option value="1mo" selected>1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                    </select>
                </div>
                <button class="btn" onclick="makePrediction()">
                    📈 Get Prediction
                </button>
                <div id="predictResults" class="results"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>📰 Live Data Feeds</h2>
            <div class="data-sources" id="dataSourcesStatus">
                <div class="data-source">Stock Data</div>
                <div class="data-source">Treasury Yields</div>
                <div class="data-source">Economic Indicators</div>
                <div class="data-source">Central Banks</div>
                <div class="data-source">Geopolitical</div>
                <div class="data-source">Market News</div>
            </div>
            <button class="btn" onclick="checkDataFeeds()" style="margin-top: 20px;">
                🔄 Refresh Data Feeds
            </button>
            <div id="feedResults" class="results"></div>
        </div>
    </div>
    
    <script>
        // Check system status on load
        window.addEventListener('load', () => {
            checkStatus();
            updateTime();
            setInterval(updateTime, 60000);
        });
        
        function updateTime() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = 
                now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                const finbertStatus = document.getElementById('finbertStatus');
                if (data.finbert_enabled) {
                    finbertStatus.textContent = '✓ Active';
                    finbertStatus.className = 'value status-active';
                } else {
                    finbertStatus.textContent = '⚠ Fallback';
                    finbertStatus.className = 'value status-inactive';
                }
                
                document.getElementById('dataSourcesCount').textContent = data.data_sources || '6';
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }
        
        async function trainModel() {
            const symbol = document.getElementById('trainSymbol').value;
            const period = document.getElementById('trainPeriod').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            const resultsDiv = document.getElementById('trainResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Training enhanced model with all data sources...</div>';
            
            try {
                const response = await fetch('/api/train_enhanced', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, period })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="result-item">
                        <div class="result-label">Error</div>
                        <div class="result-value">${data.error}</div>
                    </div>`;
                    return;
                }
                
                let html = `
                    <div class="result-item">
                        <div class="result-label">Training Results</div>
                        <div class="result-value">${symbol} - ${period}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Best Model</div>
                        <div class="result-value">${data.best_model || 'Random Forest'}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Accuracy</div>
                        <div class="result-value">${((data.best_accuracy || 0) * 100).toFixed(2)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Training Samples</div>
                        <div class="result-value">${data.samples || 0}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Features Used</div>
                        <div class="result-value">${data.features || 0}</div>
                    </div>
                `;
                
                // Show data sources
                if (data.data_sources) {
                    html += '<div class="result-item"><div class="result-label">Data Sources Active</div><div class="data-sources">';
                    for (const [source, active] of Object.entries(data.data_sources)) {
                        html += `<div class="data-source ${active ? 'active' : 'inactive'}">${source.replace(/_/g, ' ')}</div>`;
                    }
                    html += '</div></div>';
                }
                
                // Show top features
                if (data.feature_importance && data.feature_importance.length > 0) {
                    html += '<div class="result-item"><div class="result-label">Top Features</div><div class="feature-grid">';
                    data.feature_importance.slice(0, 6).forEach(feature => {
                        html += `<div class="feature-item">
                            <div class="feature-name">${feature.feature}</div>
                            <div class="feature-importance">${(feature.importance * 100).toFixed(1)}%</div>
                        </div>`;
                    });
                    html += '</div></div>';
                }
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
        
        async function makePrediction() {
            const symbol = document.getElementById('predictSymbol').value;
            const period = document.getElementById('predictPeriod').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            const resultsDiv = document.getElementById('predictResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Analyzing with all data sources...</div>';
            
            try {
                const response = await fetch('/api/predict_enhanced', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, period })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="result-item">
                        <div class="result-label">Error</div>
                        <div class="result-value">${data.error}</div>
                    </div>`;
                    return;
                }
                
                const predictionClass = data.prediction === 'BUY' ? 'prediction-buy' : 'prediction-sell';
                const upProb = (data.probability_up || 0) * 100;
                
                let html = `
                    <div class="result-item">
                        <div class="result-label">Prediction</div>
                        <div class="result-value ${predictionClass}">${data.prediction}</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Confidence</div>
                        <div class="result-value">${((data.confidence || 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Probability</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${upProb}%"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Down: ${(100 - upProb).toFixed(1)}%</span>
                            <span>Up: ${upProb.toFixed(1)}%</span>
                        </div>
                    </div>
                `;
                
                // Market indicators
                if (data.market_data) {
                    html += '<div class="result-item"><div class="result-label">Market Indicators</div><div class="indicator-grid">';
                    html += `<div class="indicator">
                        <div class="indicator-label">VIX (Fear Index)</div>
                        <div class="indicator-value">${data.market_data.vix?.toFixed(2) || '--'}</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">Dollar Index</div>
                        <div class="indicator-value">${data.market_data.dollar_index?.toFixed(2) || '--'}</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">S&P 500 Change</div>
                        <div class="indicator-value">${((data.market_data.sp500_change || 0) * 100).toFixed(2)}%</div>
                    </div>`;
                    html += '</div></div>';
                }
                
                // Treasury yields
                if (data.yields) {
                    html += '<div class="result-item"><div class="result-label">Treasury Yields</div><div class="indicator-grid">';
                    html += `<div class="indicator">
                        <div class="indicator-label">2-Year</div>
                        <div class="indicator-value">${data.yields['2_year']?.toFixed(2) || '--'}%</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">10-Year</div>
                        <div class="indicator-value">${data.yields['10_year']?.toFixed(2) || '--'}%</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">Yield Curve</div>
                        <div class="indicator-value">${data.yields.yield_curve?.toFixed(2) || '--'}</div>
                    </div>`;
                    html += '</div></div>';
                }
                
                // Technical indicators
                if (data.technical_indicators) {
                    html += '<div class="result-item"><div class="result-label">Technical Analysis</div><div class="indicator-grid">';
                    html += `<div class="indicator">
                        <div class="indicator-label">RSI</div>
                        <div class="indicator-value">${data.technical_indicators.rsi?.toFixed(2) || '--'}</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">MACD</div>
                        <div class="indicator-value">${data.technical_indicators.macd?.toFixed(3) || '--'}</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">Volatility</div>
                        <div class="indicator-value">${((data.technical_indicators.volatility || 0) * 100).toFixed(2)}%</div>
                    </div>`;
                    html += `<div class="indicator">
                        <div class="indicator-label">Volume Ratio</div>
                        <div class="indicator-value">${data.technical_indicators.volume_ratio?.toFixed(2) || '--'}</div>
                    </div>`;
                    html += '</div></div>';
                }
                
                // Sentiment
                if (data.sentiment) {
                    html += `<div class="result-item">
                        <div class="result-label">News Sentiment</div>
                        <div class="result-value">${data.sentiment.overall?.toFixed(3) || '0.000'}</div>
                    </div>`;
                }
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
        
        async function checkDataFeeds() {
            const resultsDiv = document.getElementById('feedResults');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Checking all data feeds...</div>';
            
            try {
                const response = await fetch('/api/check_feeds');
                const data = await response.json();
                
                let html = '<div class="result-item"><div class="result-label">Data Feed Status</div>';
                html += '<div style="margin-top: 15px;">';
                
                for (const [feed, status] of Object.entries(data)) {
                    const statusClass = status.active ? 'status-active' : 'status-inactive';
                    const statusIcon = status.active ? '✓' : '✗';
                    html += `<div style="margin-bottom: 10px;">
                        <span class="${statusClass}">${statusIcon}</span> 
                        <strong>${feed}:</strong> ${status.message || (status.active ? 'Active' : 'Inactive')}
                        ${status.count ? ` (${status.count} items)` : ''}
                    </div>`;
                }
                
                html += '</div></div>';
                resultsDiv.innerHTML = html;
                
                // Update visual indicators
                const sources = document.querySelectorAll('#dataSourcesStatus .data-source');
                const feedNames = ['Stock Data', 'Treasury Yields', 'Economic Indicators', 'Central Banks', 'Geopolitical', 'Market News'];
                sources.forEach((source, index) => {
                    const feedKey = feedNames[index].toLowerCase().replace(' ', '_');
                    const status = data[feedKey];
                    if (status && status.active) {
                        source.classList.add('active');
                        source.classList.remove('inactive');
                    } else {
                        source.classList.add('inactive');
                        source.classList.remove('active');
                    }
                });
            } catch (error) {
                resultsDiv.innerHTML = `<div class="result-item">
                    <div class="result-label">Error</div>
                    <div class="result-value">${error.message}</div>
                </div>`;
            }
        }
    </script>
</body>
</html>
'''

# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    return jsonify({
        "finbert_enabled": FINBERT_AVAILABLE,
        "data_sources": 6,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/train_enhanced', methods=['POST'])
def train_enhanced():
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    period = data.get('period', '6mo')
    
    result = ml_model.train_enhanced_model(symbol, period)
    return jsonify(result)

@app.route('/api/predict_enhanced', methods=['POST'])
def predict_enhanced():
    data = request.json
    symbol = data.get('symbol', 'AAPL')
    period = data.get('period', '1mo')
    
    result = ml_model.predict_enhanced(symbol, period)
    return jsonify(result)

@app.route('/api/check_feeds')
def check_feeds():
    """Check status of all data feeds"""
    fetcher = EnhancedDataFetcher()
    
    status = {}
    
    # Check stock data
    try:
        df = fetcher.get_stock_data('AAPL', '1mo')
        status['stock_data'] = {'active': not df.empty, 'message': f'{len(df)} days of data'}
    except:
        status['stock_data'] = {'active': False, 'message': 'Failed to fetch'}
    
    # Check treasury yields
    try:
        yields = fetcher.get_treasury_yields()
        status['treasury_yields'] = {'active': len(yields) > 0, 'count': len(yields)}
    except:
        status['treasury_yields'] = {'active': False, 'message': 'Failed to fetch'}
    
    # Check economic indicators
    try:
        indicators = fetcher.get_economic_indicators()
        status['economic_indicators'] = {'active': len(indicators) > 0, 'count': len(indicators)}
    except:
        status['economic_indicators'] = {'active': False, 'message': 'Failed to fetch'}
    
    # Check central bank news
    try:
        cb_news = fetcher.get_central_bank_news()
        status['central_banks'] = {'active': len(cb_news) > 0, 'count': len(cb_news)}
    except:
        status['central_banks'] = {'active': False, 'message': 'Failed to fetch'}
    
    # Check geopolitical events
    try:
        geo_events = fetcher.get_geopolitical_events()
        status['geopolitical'] = {'active': len(geo_events) > 0, 'count': len(geo_events)}
    except:
        status['geopolitical'] = {'active': False, 'message': 'Failed to fetch'}
    
    # Check market news
    try:
        news = fetcher.get_market_news('AAPL')
        status['market_news'] = {'active': len(news) > 0, 'count': len(news)}
    except:
        status['market_news'] = {'active': False, 'message': 'Failed to fetch'}
    
    return jsonify(status)

if __name__ == '__main__':
    # Create directories
    Path("logs").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("cache").mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("ENHANCED FINBERT TRADING SYSTEM")
    print("="*70)
    print("✓ Automatic Data Feeds:")
    print("  • Stock prices and technical indicators")
    print("  • Government announcements (Fed, ECB, RBA, BoE)")
    print("  • Economic indicators (VIX, Dollar, Gold, Oil)")
    print("  • Interest rates and bond yields")
    print("  • Geopolitical events monitoring")
    print("  • Market news and sentiment")
    print("="*70)
    print(f"FinBERT Status: {'✓ ENABLED' if FINBERT_AVAILABLE else '⚠ FALLBACK MODE'}")
    print("="*70)
    print("Server starting at http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)