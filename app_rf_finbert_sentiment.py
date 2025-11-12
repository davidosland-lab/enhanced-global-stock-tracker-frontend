#!/usr/bin/env python3
"""
Enhanced Random Forest with FinBERT Sentiment Analysis
Properly integrates sentiment as pre-calculated features (no API calls during training)
Includes Australian market-specific feeds and multi-asset support
"""

import os
import re
import json
import time
import datetime as dt
import warnings
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import yfinance as yf
import requests
import feedparser
from tqdm import tqdm

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Try to import transformer models for FinBERT
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    FINBERT_AVAILABLE = True
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError as e:
    FINBERT_AVAILABLE = False
    print(f"WARNING: transformers/torch not available. FinBERT disabled. Error: {e}")

print("=" * 80)
print("RANDOM FOREST WITH FINBERT SENTIMENT ANALYSIS")
print("=" * 80)
print(f"✓ FinBERT Available: {FINBERT_AVAILABLE}")
print("✓ Pre-calculated sentiment (no API calls during training)")
print("✓ Australian market feeds (RBA, ABS, Treasury)")
print("✓ Multi-asset support")
print("=" * 80)

app = Flask(__name__)
CORS(app)

# Configuration
CACHE_DIR = "./cache_sentiment"
YAHOO_REQUEST_DELAY = 3
COST_BPS = 2  # Trading cost in basis points

# Australian stocks
ASX20 = [
    "CBA.AX", "NAB.AX", "ANZ.AX", "WBC.AX",  # Banks
    "BHP.AX", "RIO.AX", "FMG.AX",  # Mining
    "CSL.AX", "WES.AX", "WOW.AX",  # Healthcare/Retail
    "TLS.AX", "MQG.AX", "WDS.AX",  # Telco/Finance
    "GMG.AX", "TCL.AX", "BXB.AX",  # Property
    "SCG.AX", "QAN.AX", "ALL.AX", "COL.AX"  # Mixed
]

# News query for Australian market
NEWS_QUERY = (
    "Australia finance OR ASX OR Australian economy OR RBA OR CPI OR inflation OR unemployment "
    "OR budget OR Commonwealth Bank OR CBA OR BHP OR Rio Tinto OR CSL OR Qantas OR Reserve Bank"
)

# Australian RSS feeds
RSS_FEEDS = [
    "https://www.rba.gov.au/rss/rss.xml",  # RBA news/speeches
    "https://www.abs.gov.au/rss.xml",  # ABS statistics
    "https://treasury.gov.au/media-release/rss",  # Treasury
    "https://asic.gov.au/about-asic/news-centre/find-a-media-release/?output=rss",  # ASIC
    "https://www.asx.com.au/asx/rss/announcement/20",  # ASX announcements
]

# Keywords for event detection
WAR_KEYWORDS = [
    "war", "conflict", "missile", "invasion", "strike", "hostilities", "drone", "airstrike",
    "sanctions", "geopolitical", "border clash", "troop", "shelling", "military"
]

MACRO_KEYWORDS = [
    "CPI", "inflation", "unemployment", "GDP", "PMI", "retail sales", "trade balance", 
    "interest rate", "cash rate", "RBA", "rate decision", "jobs data", "labor market", 
    "budget", "federal budget", "Reserve Bank", "monetary policy"
]

def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    os.makedirs(CACHE_DIR, exist_ok=True)

def clean_text(s: str) -> str:
    """Clean and normalize text"""
    return re.sub(r"\s+", " ", (s or "")).strip()

def safe_dtparse(s: str) -> Optional[pd.Timestamp]:
    """Safely parse datetime string"""
    try:
        return pd.to_datetime(s, utc=True)
    except:
        return None

class FinBERTSentimentAnalyzer:
    """FinBERT sentiment analyzer for financial text"""
    
    def __init__(self):
        if not FINBERT_AVAILABLE:
            self.model = None
            self.tokenizer = None
            return
        
        print("Loading FinBERT model...")
        self.model_name = "yiyanghkust/finbert-tone"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(device)
        self.model.eval()
        print("FinBERT loaded successfully")
    
    def analyze_batch(self, texts: List[str]) -> List[float]:
        """Analyze sentiment for a batch of texts"""
        if not FINBERT_AVAILABLE or not texts:
            return [0.0] * len(texts)
        
        scores = []
        batch_size = 16
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                chunk = texts[i:i+batch_size]
                encoding = self.tokenizer(
                    chunk, 
                    padding=True, 
                    truncation=True, 
                    max_length=96, 
                    return_tensors="pt"
                ).to(device)
                
                logits = self.model(**encoding).logits
                probs = torch.softmax(logits, dim=1).cpu().numpy()
                
                # FinBERT-tone labels: [neutral=0, positive=1, negative=2]
                # Score = P(positive) - P(negative)
                for p in probs:
                    score = float(p[1] - p[2])  # Range: [-1, 1]
                    scores.append(score)
        
        return scores

class NewsFetcher:
    """Fetch news from multiple sources"""
    
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.cache_file_raw = os.path.join(CACHE_DIR, "raw_news.json")
        self.cache_file_daily = os.path.join(CACHE_DIR, "daily_sentiment.csv")
        ensure_cache_dir()
    
    def fetch_newsapi(self, query: str, from_date: str, to_date: str) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if not self.newsapi_key:
            return []
        
        results = []
        headers = {"User-Agent": "rf-sentiment/1.0"}
        
        d0 = pd.to_datetime(from_date).date()
        d1 = pd.to_datetime(to_date).date()
        
        for day in tqdm(pd.date_range(d0, d1, freq="D"), desc="NewsAPI"):
            f = day.strftime("%Y-%m-%d")
            t = (day + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            
            url = (f"https://newsapi.org/v2/everything?"
                   f"q={requests.utils.quote(query)}&from={f}&to={t}"
                   f"&language=en&sortBy=publishedAt&pageSize=100")
            
            try:
                r = requests.get(url, headers=headers, timeout=20, 
                               params={"apiKey": self.newsapi_key})
                
                if r.status_code == 200:
                    data = r.json()
                    for art in data.get("articles", []):
                        results.append({
                            "title": clean_text(art.get("title")),
                            "publishedAt": art.get("publishedAt"),
                            "source": (art.get("source") or {}).get("name"),
                            "url": art.get("url")
                        })
                
                time.sleep(0.3)  # Rate limiting
            except Exception as e:
                print(f"NewsAPI error: {e}")
                continue
        
        return results
    
    def fetch_rss(self, feeds: List[str], start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> List[Dict]:
        """Fetch news from RSS feeds"""
        items = []
        
        for url in tqdm(feeds, desc="RSS feeds"):
            try:
                fp = feedparser.parse(url)
                for entry in fp.get("entries", []):
                    published = entry.get("published") or entry.get("updated")
                    ts = safe_dtparse(published)
                    
                    if ts is None:
                        continue
                    
                    if not (start_ts <= ts <= end_ts):
                        continue
                    
                    items.append({
                        "title": clean_text(entry.get("title", "")),
                        "publishedAt": ts.isoformat(),
                        "source": url.split("/")[2],  # Domain as source
                        "url": entry.get("link", url)
                    })
            except Exception as e:
                print(f"RSS error for {url}: {e}")
                continue
        
        return items
    
    def aggregate_sentiment(self, news_items: List[Dict], analyzer: FinBERTSentimentAnalyzer) -> pd.DataFrame:
        """Aggregate sentiment by day"""
        if not news_items:
            return pd.DataFrame()
        
        df = pd.DataFrame(news_items)
        df["ts"] = pd.to_datetime(df["publishedAt"], utc=True)
        df["date"] = df["ts"].dt.tz_convert("Australia/Sydney").dt.date
        df["title"] = df["title"].fillna("")
        
        # Keyword detection
        df["war_hit"] = df["title"].apply(
            lambda s: int(any(k.lower() in s.lower() for k in WAR_KEYWORDS))
        )
        df["macro_hit"] = df["title"].apply(
            lambda s: int(any(k.lower() in s.lower() for k in MACRO_KEYWORDS))
        )
        
        # Sentiment analysis
        if FINBERT_AVAILABLE and len(df) > 0:
            print("Analyzing sentiment with FinBERT...")
            df["sentiment"] = analyzer.analyze_batch(df["title"].tolist())
        else:
            df["sentiment"] = 0.0
        
        # Daily aggregation
        daily = df.groupby("date").agg(
            sent_mean=("sentiment", "mean"),
            sent_std=("sentiment", "std"),
            war_hits=("war_hit", "sum"),
            macro_hits=("macro_hit", "sum"),
            n_items=("title", "count")
        ).reset_index()
        
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.set_index("date").sort_index()
        
        # Fill missing values
        daily["sent_std"] = daily["sent_std"].fillna(0)
        
        return daily

class TechnicalFeatures:
    """Calculate technical indicators"""
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
        down = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
        rs = up / (down.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    @staticmethod
    def calculate_features(df: pd.DataFrame, sentiment_daily: pd.DataFrame = None) -> pd.DataFrame:
        """Calculate all features including sentiment"""
        features = df.copy()
        
        # Price-based features
        features["ret_1d"] = df["close"].pct_change()
        features["ret_5d"] = df["close"].pct_change(5)
        features["ret_20d"] = df["close"].pct_change(20)
        
        # Volatility
        features["vol_10"] = features["ret_1d"].rolling(10).std()
        features["vol_20"] = features["ret_1d"].rolling(20).std()
        features["vol_ratio"] = features["vol_10"] / features["vol_20"]
        
        # Moving averages
        features["sma_10"] = df["close"].rolling(10).mean()
        features["sma_20"] = df["close"].rolling(20).mean()
        features["sma_50"] = df["close"].rolling(50).mean()
        
        # Price relative to MAs
        features["px_sma10"] = df["close"] / features["sma_10"] - 1
        features["px_sma20"] = df["close"] / features["sma_20"] - 1
        features["px_sma50"] = df["close"] / features["sma_50"] - 1
        
        # Momentum
        features["mom_10"] = df["close"].pct_change(10)
        features["mom_20"] = df["close"].pct_change(20)
        
        # RSI
        features["rsi_14"] = TechnicalFeatures.rsi(df["close"], 14)
        
        # MACD
        ema_12 = df["close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["close"].ewm(span=26, adjust=False).mean()
        features["macd"] = ema_12 - ema_26
        features["macd_signal"] = features["macd"].ewm(span=9, adjust=False).mean()
        features["macd_hist"] = features["macd"] - features["macd_signal"]
        
        # Volume features
        if "volume" in df.columns:
            features["volume_ratio"] = df["volume"] / df["volume"].rolling(20).mean()
            features["volume_change"] = df["volume"].pct_change()
        
        # Add sentiment if available
        if sentiment_daily is not None and not sentiment_daily.empty:
            # Align sentiment by date (Australian timezone)
            idx_au = df.index.tz_localize("UTC").tz_convert("Australia/Sydney").normalize()
            temp = pd.DataFrame({"index": df.index, "date_au": idx_au})
            
            daily = sentiment_daily.rename_axis("date").reset_index()
            merged = temp.merge(daily, left_on="date_au", right_on="date", how="left").set_index("index")
            
            # Add sentiment features
            for col in ["sent_mean", "sent_std", "war_hits", "macro_hits", "n_items"]:
                if col in merged.columns:
                    features[col] = merged[col].fillna(0)
            
            # Smoothed sentiment
            if "sent_mean" in features.columns:
                features["sent_3d"] = features["sent_mean"].rolling(3).mean()
                features["sent_10d"] = features["sent_mean"].rolling(10).mean()
                features["sent_momentum"] = features["sent_mean"] - features["sent_10d"]
        
        # Target: next day up/down
        features["target"] = (df["close"].pct_change().shift(-1) > 0).astype(int)
        
        return features.dropna()

class RandomForestPredictor:
    """Random Forest with walk-forward validation"""
    
    def __init__(self, n_estimators=600, max_depth=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.scaler = StandardScaler()
        self.model = None
        self.feature_cols = None
        self.feature_importance = None
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get feature columns (exclude target and metadata)"""
        exclude = ["target", "close", "open", "high", "low", "volume"]
        return [col for col in df.columns if col not in exclude]
    
    def walk_forward_validate(self, df: pd.DataFrame, n_splits: int = 5) -> pd.Series:
        """Walk-forward validation with OOF predictions"""
        self.feature_cols = self.get_feature_columns(df)
        
        X = df[self.feature_cols].values
        y = df["target"].values
        dates = df.index
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=n_splits)
        oof_proba = np.full(len(df), np.nan)
        
        feature_importances = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X_scaled)):
            # Train model
            model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                max_features="sqrt",
                min_samples_split=10,
                min_samples_leaf=5,
                n_jobs=-1,
                random_state=42
            )
            
            model.fit(X_scaled[train_idx], y[train_idx])
            
            # Predict probabilities
            oof_proba[test_idx] = model.predict_proba(X_scaled[test_idx])[:, 1]
            
            # Store feature importance
            feature_importances.append(model.feature_importances_)
        
        # Average feature importances
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': np.mean(feature_importances, axis=0)
        }).sort_values('importance', ascending=False)
        
        # Calculate metrics
        valid_mask = ~np.isnan(oof_proba)
        y_pred = (oof_proba[valid_mask] >= 0.5).astype(int)
        accuracy = accuracy_score(y[valid_mask], y_pred)
        
        print(f"Walk-forward CV Accuracy: {accuracy:.3f}")
        
        # Train final model on all data
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            max_features="sqrt",
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Return OOF probabilities
        return pd.Series(oof_proba, index=dates, name="probability")
    
    def predict(self, features: pd.DataFrame) -> float:
        """Make prediction for new data"""
        if self.model is None or self.feature_cols is None:
            return 0.5
        
        X = features[self.feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        proba = self.model.predict_proba(X_scaled)[0, 1]
        return proba

class Backtester:
    """Backtest trading strategies"""
    
    @staticmethod
    def backtest_long_flat(df: pd.DataFrame, probabilities: pd.Series, cost_bps: int = 2) -> Dict:
        """Backtest long/flat strategy"""
        # Generate positions (1 = long, 0 = flat)
        positions = (probabilities >= 0.5).astype(int)
        
        # Calculate next-day returns (aligned with predictions)
        returns_next = df.loc[probabilities.index, "close"].pct_change().shift(-1)
        
        # Calculate turnover and costs
        turnover = positions.diff().abs().fillna(0)
        costs = turnover * (cost_bps / 10000)
        
        # Strategy returns
        strategy_returns = (positions * returns_next).fillna(0) - costs
        
        # Calculate equity curve
        equity = (1 + strategy_returns).cumprod()
        
        # Buy & hold benchmark
        bh_returns = df.loc[equity.index, "close"].pct_change().fillna(0)
        bh_equity = (1 + bh_returns).cumprod()
        
        # Calculate metrics
        def sharpe(returns, periods=252):
            mu = returns.mean() * periods
            sd = returns.std(ddof=1) * np.sqrt(periods)
            return mu / sd if sd > 0 else 0
        
        hit_rate = (
            ((positions == 1) & (returns_next > 0)) | 
            ((positions == 0) & (returns_next <= 0))
        ).mean()
        
        max_dd = ((equity / equity.cummax()) - 1).min()
        cagr = (equity.iloc[-1] ** (252 / len(strategy_returns))) - 1
        
        return {
            "sharpe": sharpe(strategy_returns),
            "hit_rate": hit_rate,
            "max_drawdown": max_dd,
            "cagr": cagr,
            "total_return": equity.iloc[-1] - 1,
            "bh_return": bh_equity.iloc[-1] - 1,
            "equity_curve": equity,
            "bh_equity": bh_equity
        }

# Global instances
sentiment_analyzer = FinBERTSentimentAnalyzer()
news_fetcher = NewsFetcher()

@app.route('/api/rf/analyze/<symbol>')
def analyze_with_rf_sentiment(symbol):
    """Analyze stock with Random Forest and FinBERT sentiment"""
    try:
        period = request.args.get('period', '2y')
        
        print(f"\nAnalyzing {symbol} with Random Forest + FinBERT")
        
        # Fetch price data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return jsonify({'error': f'No data for {symbol}'}), 404
        
        df = df.rename(columns=str.lower)
        
        # Fetch/load sentiment data
        start = df.index.min()
        end = df.index.max()
        
        # Check cache first
        cache_file = os.path.join(CACHE_DIR, f"sentiment_{symbol}_{period}.csv")
        
        if os.path.exists(cache_file):
            # Load cached sentiment
            sentiment_daily = pd.read_csv(cache_file, parse_dates=["date"]).set_index("date")
            print("Loaded cached sentiment data")
        else:
            # Fetch news
            print("Fetching news...")
            news_items = []
            
            # NewsAPI (if key available)
            if news_fetcher.newsapi_key:
                query = f"{symbol} OR {symbol.replace('.AX', '')} OR Australia finance"
                news_items.extend(
                    news_fetcher.fetch_newsapi(
                        query, 
                        start.strftime("%Y-%m-%d"),
                        end.strftime("%Y-%m-%d")
                    )
                )
            
            # RSS feeds
            news_items.extend(
                news_fetcher.fetch_rss(
                    RSS_FEEDS,
                    pd.Timestamp(start).tz_localize("UTC"),
                    pd.Timestamp(end).tz_localize("UTC")
                )
            )
            
            # Aggregate sentiment
            sentiment_daily = news_fetcher.aggregate_sentiment(news_items, sentiment_analyzer)
            
            # Cache for future use
            if not sentiment_daily.empty:
                sentiment_daily.to_csv(cache_file)
                print(f"Cached sentiment data to {cache_file}")
        
        # Calculate features
        print("Calculating features...")
        features_df = TechnicalFeatures.calculate_features(df, sentiment_daily)
        
        if len(features_df) < 100:
            return jsonify({'error': 'Insufficient data for analysis'}), 400
        
        # Train Random Forest with walk-forward validation
        print("Training Random Forest...")
        rf_model = RandomForestPredictor()
        probabilities = rf_model.walk_forward_validate(features_df)
        
        # Backtest
        print("Backtesting...")
        backtest_results = Backtester.backtest_long_flat(features_df, probabilities)
        
        # Get latest prediction
        latest_features = features_df.iloc[-1:].drop(columns=["target"])
        latest_prediction = rf_model.predict(latest_features)
        
        # Prepare response
        current_price = float(df['close'].iloc[-1])
        prev_close = float(df['close'].iloc[-2]) if len(df) > 1 else current_price
        
        # Determine signal
        signal = "BUY" if latest_prediction > 0.55 else "SELL" if latest_prediction < 0.45 else "HOLD"
        
        # Get top feature importances
        top_features = rf_model.feature_importance.head(10).to_dict('records')
        
        # Check if sentiment features are important
        sentiment_features = rf_model.feature_importance[
            rf_model.feature_importance['feature'].str.contains('sent|war|macro|n_items')
        ]
        sentiment_importance = sentiment_features['importance'].sum()
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'price_change': current_price - prev_close,
            'price_change_pct': ((current_price - prev_close) / prev_close) * 100,
            'prediction': float(latest_prediction),
            'signal': signal,
            'confidence': abs(latest_prediction - 0.5) * 200,
            'backtest': {
                'sharpe_ratio': float(backtest_results['sharpe']),
                'hit_rate': float(backtest_results['hit_rate']) * 100,
                'max_drawdown': float(backtest_results['max_drawdown']) * 100,
                'cagr': float(backtest_results['cagr']) * 100,
                'total_return': float(backtest_results['total_return']) * 100,
                'bh_return': float(backtest_results['bh_return']) * 100,
                'outperformance': float((backtest_results['total_return'] - backtest_results['bh_return']) * 100)
            },
            'feature_importance': top_features,
            'sentiment_importance': float(sentiment_importance * 100),
            'model_info': {
                'type': 'Random Forest with FinBERT',
                'n_estimators': rf_model.n_estimators,
                'n_features': len(rf_model.feature_cols),
                'cv_folds': 5
            }
        })
        
    except Exception as e:
        print(f"Error in RF analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/rf/multi-asset', methods=['POST'])
def analyze_multi_asset():
    """Analyze multiple assets with Random Forest + sentiment"""
    try:
        data = request.json
        symbols = data.get('symbols', ASX20[:5])  # Default to first 5 ASX20
        
        results = {}
        
        for symbol in tqdm(symbols, desc="Analyzing assets"):
            try:
                # Make request to single-asset endpoint
                response = analyze_with_rf_sentiment(symbol)
                
                if response.status_code == 200:
                    results[symbol] = response.json
                else:
                    results[symbol] = {'error': 'Analysis failed'}
                    
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        # Create summary
        summary = {
            'total_assets': len(symbols),
            'successful': sum(1 for r in results.values() if 'signal' in r),
            'buy_signals': sum(1 for r in results.values() if r.get('signal') == 'BUY'),
            'sell_signals': sum(1 for r in results.values() if r.get('signal') == 'SELL'),
            'hold_signals': sum(1 for r in results.values() if r.get('signal') == 'HOLD'),
            'avg_sharpe': np.mean([r['backtest']['sharpe_ratio'] for r in results.values() 
                                  if 'backtest' in r]),
            'avg_hit_rate': np.mean([r['backtest']['hit_rate'] for r in results.values() 
                                    if 'backtest' in r])
        }
        
        return jsonify({
            'summary': summary,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'finbert_available': FINBERT_AVAILABLE,
        'version': '1.0-rf-finbert'
    })

@app.route('/')
def index():
    """Web interface for Random Forest + FinBERT sentiment system"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Forest + FinBERT Sentiment Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .header h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            color: #7f8c8d;
            font-size: 16px;
        }
        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .control-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #ecf0f1;
            font-size: 15px;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #3498db;
        }
        button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52,152,219,0.4);
        }
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        .signal {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .signal-buy {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
        }
        .signal-sell {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }
        .signal-hold {
            background: linear-gradient(135deg, #f39c12, #f1c40f);
            color: white;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .metric-label {
            color: #7f8c8d;
            font-weight: 500;
        }
        .metric-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .feature-bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .feature-name {
            width: 150px;
            font-size: 14px;
            color: #34495e;
        }
        .feature-bar-fill {
            flex: 1;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            margin: 0 10px;
            position: relative;
            overflow: hidden;
        }
        .feature-bar-value {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            transition: width 0.5s ease;
        }
        .feature-importance-value {
            font-size: 14px;
            color: #2c3e50;
            font-weight: bold;
        }
        .sentiment-badge {
            display: inline-block;
            padding: 5px 15px;
            background: linear-gradient(135deg, #9b59b6, #8e44ad);
            color: white;
            border-radius: 20px;
            font-size: 14px;
            margin: 5px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌲 Random Forest + FinBERT Sentiment Analysis</h1>
            <p>Advanced ML with financial sentiment analysis • Australian market feeds • No API calls during training</p>
            <div style="margin-top: 15px;">
                <span class="sentiment-badge">✓ Pre-calculated sentiment</span>
                <span class="sentiment-badge">✓ RBA/ABS/Treasury feeds</span>
                <span class="sentiment-badge">✓ Walk-forward validation</span>
                <span class="sentiment-badge">✓ FinBERT sentiment model</span>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-row">
                <input type="text" id="symbol" placeholder="Symbol (e.g., CBA.AX)" value="CBA.AX">
                <select id="period">
                    <option value="1y">1 Year</option>
                    <option value="2y" selected>2 Years</option>
                    <option value="5y">5 Years</option>
                </select>
                <button onclick="analyzeStock()">🚀 Analyze with RF + Sentiment</button>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="card">
                <h2>Analysis Results</h2>
                <div class="loading">Enter a symbol and click Analyze to begin</div>
            </div>
        </div>
    </div>
    
    <script>
        async function analyzeStock() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                alert('Please enter a symbol');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="card">
                    <h2>Analysis Results</h2>
                    <div class="loading">
                        🔄 Analyzing ${symbol} with Random Forest + FinBERT...<br>
                        <small>This may take a minute as we analyze sentiment from news feeds</small>
                    </div>
                </div>
            `;
            
            try {
                const response = await fetch(`/api/rf/analyze/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    resultsDiv.innerHTML = `
                        <div class="card">
                            <h2>Error</h2>
                            <div class="error">${data.error}</div>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="card">
                        <h2>Error</h2>
                        <div class="error">${error.message}</div>
                    </div>
                `;
            }
        }
        
        function displayResults(data) {
            const signalClass = data.signal === 'BUY' ? 'signal-buy' : 
                               data.signal === 'SELL' ? 'signal-sell' : 'signal-hold';
            
            let html = `
                <div class="card">
                    <h2>📊 ${data.symbol} Analysis</h2>
                    <div class="signal ${signalClass}">
                        ${data.signal}
                        <div style="font-size: 16px; margin-top: 10px;">
                            Confidence: ${data.confidence.toFixed(1)}%
                        </div>
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Current Price</span>
                        <span class="metric-value">$${data.current_price.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Prediction</span>
                        <span class="metric-value">${(data.prediction * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Price Change</span>
                        <span class="metric-value ${data.price_change >= 0 ? 'positive' : 'negative'}">
                            ${data.price_change >= 0 ? '+' : ''}${data.price_change.toFixed(2)} 
                            (${data.price_change_pct.toFixed(2)}%)
                        </span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>📈 Backtest Performance</h2>
                    <div class="metric">
                        <span class="metric-label">Sharpe Ratio</span>
                        <span class="metric-value">${data.backtest.sharpe_ratio.toFixed(2)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Hit Rate</span>
                        <span class="metric-value">${data.backtest.hit_rate.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Max Drawdown</span>
                        <span class="metric-value negative">${data.backtest.max_drawdown.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CAGR</span>
                        <span class="metric-value ${data.backtest.cagr >= 0 ? 'positive' : 'negative'}">
                            ${data.backtest.cagr.toFixed(1)}%
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Strategy Return</span>
                        <span class="metric-value ${data.backtest.total_return >= 0 ? 'positive' : 'negative'}">
                            ${data.backtest.total_return.toFixed(1)}%
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Buy & Hold Return</span>
                        <span class="metric-value">${data.backtest.bh_return.toFixed(1)}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Outperformance</span>
                        <span class="metric-value ${data.backtest.outperformance >= 0 ? 'positive' : 'negative'}">
                            ${data.backtest.outperformance >= 0 ? '+' : ''}${data.backtest.outperformance.toFixed(1)}%
                        </span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🎯 Feature Importance</h2>
                    <div style="margin-bottom: 15px;">
                        <strong>Sentiment Importance:</strong> 
                        <span class="sentiment-badge">${data.sentiment_importance.toFixed(1)}%</span>
                    </div>
                    ${data.feature_importance.map(f => `
                        <div class="feature-bar">
                            <span class="feature-name">${f.feature}</span>
                            <div class="feature-bar-fill">
                                <div class="feature-bar-value" style="width: ${f.importance * 500}%"></div>
                            </div>
                            <span class="feature-importance-value">${(f.importance * 100).toFixed(1)}%</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="card">
                    <h2>ℹ️ Model Information</h2>
                    <div class="metric">
                        <span class="metric-label">Model Type</span>
                        <span class="metric-value">${data.model_info.type}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Trees</span>
                        <span class="metric-value">${data.model_info.n_estimators}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Features</span>
                        <span class="metric-value">${data.model_info.n_features}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CV Folds</span>
                        <span class="metric-value">${data.model_info.cv_folds}</span>
                    </div>
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Random Forest + FinBERT Sentiment Server...")
    print("="*60)
    print("Features:")
    print("  • Random Forest with walk-forward validation")
    print("  • FinBERT financial sentiment analysis")
    print("  • Australian market feeds (RBA, ABS, Treasury)")
    print("  • Pre-calculated sentiment (no API calls during training)")
    print("  • Proper feature importance analysis")
    print("="*60)
    print(f"Server running on: http://localhost:5003")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5003, host='0.0.0.0')