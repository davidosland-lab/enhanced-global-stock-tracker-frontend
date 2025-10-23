# Where FinBERT Sentiment Data Comes From

## 📊 Current Data Sources for Sentiment Analysis

### 1. **Document Analyzer Module** (Currently Implemented)
**Location:** When users upload documents through the Document Analyzer module
- **How it works:** Users manually upload financial documents (PDFs, reports, articles)
- **Analysis:** FinBERT analyzes the uploaded text
- **Storage:** Sentiment scores stored in Integration Bridge database
- **Limitation:** Requires manual uploads - not automated

### 2. **Yahoo Finance News** (Ready to Use)
**API:** Built into yfinance library
```python
ticker = yf.Ticker("AAPL")
news = ticker.news  # Returns last 10-20 news items
```
- **Availability:** FREE, no API key needed
- **Content:** Headlines, summaries, links
- **Frequency:** Real-time updates
- **Coverage:** Major financial news about the stock

### 3. **RSS Feeds** (Ready to Use)
**Sources:** Multiple financial news RSS feeds
- Yahoo Finance: `https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}`
- Bloomberg: `https://feeds.bloomberg.com/markets/news.rss`
- Reuters: `https://feeds.reuters.com/reuters/businessNews`
- Wall Street Journal: `https://feeds.a.dj.com/rss/RSSMarketsMain.xml`
- **Availability:** FREE, no authentication
- **Updates:** Every 15-30 minutes

### 4. **Integration Bridge Database** (Currently Active)
**Location:** `ml_integration_bridge.db`
- Stores sentiment from all modules
- Historical sentiment patterns
- Cross-module sentiment sharing
- Pattern discovery from multiple sources

## 🚀 Additional Sources (Can Be Added)

### 5. **Reddit API** (Requires Registration)
```python
# Using PRAW library
import praw
reddit = praw.Reddit(client_id='YOUR_ID', client_secret='SECRET')
subreddit = reddit.subreddit('wallstreetbets')
```
- **Subreddits:** r/wallstreetbets, r/stocks, r/investing
- **Cost:** FREE with rate limits
- **Setup:** Register app at reddit.com/prefs/apps

### 6. **Twitter/X API** (Paid)
- **Cost:** $100/month for Basic tier
- **Volume:** 10,000 tweets/month
- **Real-time:** Streaming available
- **Cashtags:** Track $AAPL, $TSLA mentions

### 7. **News APIs** (Various Pricing)

#### NewsAPI.org (Recommended for Testing)
```python
# pip install newsapi-python
from newsapi import NewsApiClient
api = NewsApiClient(api_key='YOUR_KEY')
articles = api.get_everything(q='Apple stock')
```
- **Free Tier:** 100 requests/day
- **Cost:** $449/month for production
- **Sources:** 80,000+ news sources

#### Alpha Vantage News
```python
# Free with API key
url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={key}"
```
- **Free Tier:** 25 requests/day
- **Paid:** $49.99/month for 300 requests/day
- **Includes:** Sentiment scores pre-calculated

#### Benzinga News
- **Cost:** $177/month
- **Features:** Real-time news, pre-analyzed sentiment
- **Coverage:** Comprehensive financial news

### 8. **SEC EDGAR Filings** (FREE)
```python
# Using sec-edgar-downloader
from sec_edgar_downloader import Downloader
dl = Downloader("MyCompany", "email@example.com")
dl.get("10-K", "AAPL", limit=1)
```
- **Filings:** 10-K, 10-Q, 8-K reports
- **Cost:** FREE, public data
- **Analysis:** Extract MD&A sections for sentiment

### 9. **Earnings Call Transcripts**

#### Seeking Alpha API
- **Cost:** ~$20-50/month
- **Content:** Full earnings transcripts
- **History:** Years of historical calls

#### Financial Modeling Prep
```python
url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?quarter={q}&year={y}&apikey={key}"
```
- **Free Tier:** 250 requests/day
- **Paid:** From $14.99/month

## 📈 How Data Flows to ML Training

```
1. Data Collection
   ├── Manual: Document uploads
   ├── Automatic: Yahoo Finance (every hour)
   ├── Automatic: RSS feeds (every 30 min)
   └── On-demand: Reddit, SEC filings

2. FinBERT Analysis
   ├── Each text item → sentiment score (-1 to +1)
   ├── Confidence score (0 to 1)
   └── Key phrases extracted

3. Storage
   ├── sentiment_data.db (raw sentiment)
   ├── daily_sentiment table (aggregated)
   └── ml_integration_bridge.db (patterns)

4. ML Training Integration
   ├── Load historical prices
   ├── Merge with daily sentiment
   ├── Create sentiment features
   └── Train model with enhanced features
```

## 🔧 Quick Setup for Automated Sentiment

### Option 1: Yahoo Finance Only (Easiest, FREE)
```python
# Already works with existing code!
import yfinance as yf

ticker = yf.Ticker("AAPL")
news = ticker.news  # Automatic news fetching

# FinBERT analyzes each article
for article in news:
    sentiment = analyze_financial_text(article['title'] + article['summary'])
```

### Option 2: Yahoo + RSS Feeds (FREE, More Coverage)
```python
# In sentiment_data_collector.py
collector = SentimentDataCollector()
data = await collector.collect_all_sentiment("AAPL")
# Automatically fetches from Yahoo + RSS feeds
```

### Option 3: Comprehensive (Requires API Keys)
```python
# Add API keys to environment variables
os.environ['NEWS_API_KEY'] = 'your_newsapi_key'
os.environ['REDDIT_CLIENT_ID'] = 'your_reddit_id'
os.environ['ALPHAVANTAGE_KEY'] = 'your_av_key'

# Collector automatically uses available APIs
collector = SentimentDataCollector()
data = await collector.collect_all_sentiment("AAPL")
```

## 💰 Cost Comparison

| Source | Cost | Volume | Update Frequency | Setup Difficulty |
|--------|------|---------|-----------------|------------------|
| Document Uploads | FREE | Manual | When uploaded | Easy |
| Yahoo Finance | FREE | 20 articles | Real-time | Very Easy |
| RSS Feeds | FREE | Unlimited | 15-30 min | Easy |
| Reddit API | FREE | 60 req/min | Real-time | Medium |
| NewsAPI | FREE/$449 | 100/day free | Real-time | Easy |
| Alpha Vantage | FREE/$50 | 25/day free | Real-time | Easy |
| Twitter/X | $100+ | 10k/month | Real-time | Medium |
| SEC EDGAR | FREE | Unlimited | When filed | Easy |

## 🎯 Recommended Setup for Best Results

### Minimum (FREE):
1. **Yahoo Finance News** - Automatic with yfinance
2. **RSS Feeds** - Multiple sources
3. **Document Uploads** - For important reports

### Optimal (Low Cost ~$50/month):
1. Everything above PLUS:
2. **Alpha Vantage** - Pre-scored sentiment
3. **Reddit API** - Social sentiment
4. **SEC Filings** - Quarterly reports

### Professional ($200+/month):
1. Everything above PLUS:
2. **NewsAPI or Benzinga** - Comprehensive news
3. **Twitter/X API** - Real-time social
4. **Seeking Alpha** - Earnings transcripts

## 📝 Current Implementation Status

✅ **Working Now:**
- Document Analyzer uploads
- Yahoo Finance integration
- RSS feed parsing
- Integration Bridge storage
- FinBERT analysis

🔧 **Ready to Activate:**
- Reddit API (just add credentials)
- Alpha Vantage (just add API key)
- SEC EDGAR (no credentials needed)

⏳ **Requires Additional Setup:**
- Twitter/X API (paid subscription)
- NewsAPI (API key + paid plan)
- Seeking Alpha (subscription)

## 🚀 How to Start Getting Sentiment Data NOW

1. **The system already fetches Yahoo Finance news automatically** when you train a model
2. **RSS feeds are parsed automatically** - no setup needed
3. **Document uploads work** through the Document Analyzer module

To see it in action:
```python
# Run the sentiment collector
python backend/sentiment_data_collector.py

# It will automatically fetch from:
# - Yahoo Finance (FREE)
# - RSS Feeds (FREE)
# - Any uploaded documents
# - Mock data for demonstration
```

The ML training will automatically use whatever sentiment data is available, with more sources providing better accuracy!