# News Sources Separation Plan: ASX vs US Markets

## Current Problem

**Issue:** Both ASX and US pipelines share the same news sentiment module (`news_sentiment_real.py`) which is hardcoded for **Australian sources only**:

### Current Australian Sources
```python
AUSTRALIAN_SCRAPING_SOURCES = {
    'RBA_CHART_PACK': 'https://www.rba.gov.au/chart-pack/',
    'RBA_MEDIA_RELEASES': 'https://www.rba.gov.au/media-releases/',
    'RBA_SPEECHES': 'https://www.rba.gov.au/speeches/',
    'RBA_PUBLICATIONS': 'https://www.rba.gov.au/publications/',
    'RBA_STATISTICS': 'https://www.rba.gov.au/statistics/'
}

AUSTRALIAN_KEYWORDS = [
    'cba', 'bhp', 'asx', 'australian stock', 'rba', 
    'cash rate', 'australian economy', etc.
]
```

**Problem:** US pipeline gets Australian news/analysis, not US-specific information.

---

## Proposed Solution: Market-Specific News Modules

### Architecture
```
Current (BROKEN):
┌─────────────┐
│ ASX Pipeline│─┐
└─────────────┘ │
                ├──► news_sentiment_real.py (Australian only)
┌─────────────┐ │
│ US Pipeline │─┘
└─────────────┘

Proposed (CORRECT):
┌─────────────┐
│ ASX Pipeline│──► news_sentiment_asx.py (Australian sources)
└─────────────┘

┌─────────────┐
│ US Pipeline │──► news_sentiment_us.py (US sources)
└─────────────┘
```

---

## Implementation Plan

### Step 1: Create US News Sentiment Module

**File:** `models/news_sentiment_us.py`

**US-Specific Sources:**

#### 1. US Federal Reserve (Central Bank)
```python
US_FED_SOURCES = {
    'FED_PRESS_RELEASES': 'https://www.federalreserve.gov/newsevents/pressreleases.htm',
    'FED_SPEECHES': 'https://www.federalreserve.gov/newsevents/speeches.htm',
    'FED_TESTIMONY': 'https://www.federalreserve.gov/newsevents/testimony.htm',
    'FED_BEIGE_BOOK': 'https://www.federalreserve.gov/monetarypolicy/beigebook/',
    'FED_FOMC_CALENDAR': 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
    'FED_FOMC_MINUTES': 'https://www.federalreserve.gov/monetarypolicy/fomcminutes.htm',
    'FED_DATA': 'https://www.federalreserve.gov/data.htm'
}
```

#### 2. US Treasury & Economic Data
```python
US_TREASURY_SOURCES = {
    'TREASURY_PRESS': 'https://home.treasury.gov/news/press-releases',
    'TREASURY_DATA': 'https://home.treasury.gov/policy-issues/economic-policy/economic-data',
    'BLS_EMPLOYMENT': 'https://www.bls.gov/news.release/empsit.toc.htm',  # Bureau of Labor Statistics
    'BLS_CPI': 'https://www.bls.gov/news.release/cpi.toc.htm',  # Inflation data
    'CENSUS_RETAIL': 'https://www.census.gov/retail/index.html'  # Retail sales
}
```

#### 3. SEC (Securities & Exchange Commission)
```python
US_SEC_SOURCES = {
    'SEC_NEWS': 'https://www.sec.gov/news/pressreleases',
    'SEC_SPEECHES': 'https://www.sec.gov/news/speeches',
    'SEC_STATEMENTS': 'https://www.sec.gov/news/statements'
}
```

#### 4. US Financial Media (RSS Feeds)
```python
US_MEDIA_RSS_FEEDS = {
    'CNBC_MARKETS': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
    'CNBC_ECONOMY': 'https://www.cnbc.com/id/20910258/device/rss/rss.html',
    'MARKETWATCH': 'https://www.marketwatch.com/rss/',
    'BARRONS': 'https://www.barrons.com/rss',
    'WSJ_MARKETS': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    'WSJ_ECONOMY': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
    'BLOOMBERG_MARKETS': 'https://www.bloomberg.com/markets',
    'REUTERS_BUSINESS': 'https://www.reuters.com/business/'
}
```

#### 5. Social Media & Commentary (Twitter/X)
```python
US_COMMENTARY_SOURCES = {
    # Federal Reserve officials (via RSS/aggregators)
    'FED_TWITTER_AGGREGATOR': 'https://nitter.net/federalreserve',  # Fed official account
    'JEROME_POWELL_SPEECHES': 'https://www.federalreserve.gov/aboutthefed/bios/board/powell.htm',
    
    # Financial influencers/analysts
    'SEEKING_ALPHA_FEEDS': 'https://seekingalpha.com/market-news',
    'FINVIZ_NEWS': 'https://finviz.com/news.ashx',
    
    # Economic commentators
    'ZEROHEDGE': 'https://www.zerohedge.com/fullrss2.xml',
    'CALCULATED_RISK': 'http://www.calculatedriskblog.com/feeds/posts/default'
}
```

#### 6. US Stock-Specific Keywords
```python
US_KEYWORDS = [
    # Major US stocks
    'apple', 'microsoft', 'google', 'alphabet', 'amazon', 'tesla', 'nvidia', 'meta',
    'berkshire', 'jpmorgan', 'goldman sachs', 'bank of america', 'wells fargo',
    'exxon', 'chevron', 'walmart', 'coca-cola', 'pepsi', 'boeing', 'intel',
    
    # US market terms
    'dow jones', 'dow', 'djia', 's&p 500', 's&p', 'nasdaq', 'nyse', 'russell 2000',
    'us stock', 'american stock', 'us market', 'wall street',
    
    # US institutions
    'federal reserve', 'fed', 'fomc', 'jerome powell', 'sec', 'treasury',
    'janet yellen', 'us treasury', 'us government',
    
    # US economic indicators
    'fed funds rate', 'interest rate', 'us cpi', 'us gdp', 'us unemployment',
    'us jobs report', 'nonfarm payrolls', 'pce', 'fomc meeting', 'fed decision',
    'us inflation', 'us economy', 'us consumer', 'us retail sales'
]
```

---

### Step 2: Rename/Refactor Australian Module

**Action:** Rename `news_sentiment_real.py` → `news_sentiment_asx.py`

**Purpose:** Make it explicitly Australian-focused

**Changes:**
```python
# Keep existing Australian sources
# Add more ASX-specific sources:

AUSTRALIAN_MEDIA_RSS_FEEDS = {
    'ASX_ANNOUNCEMENTS': 'https://www.asx.com.au/asx/statistics/announcements.do',
    'AFR_MARKETS': 'https://www.afr.com/markets',  # Australian Financial Review
    'SMH_BUSINESS': 'https://www.smh.com.au/business',  # Sydney Morning Herald
    'THE_AUSTRALIAN_BUSINESS': 'https://www.theaustralian.com.au/business',
    'ABC_BUSINESS': 'https://www.abc.net.au/news/business/',
    'BUSINESS_INSIDER_AU': 'https://www.businessinsider.com.au/'
}

AUSTRALIAN_GOVERNMENT_SOURCES = {
    'TREASURY_PRESS': 'https://treasury.gov.au/news',
    'ABS_RELEASES': 'https://www.abs.gov.au/media-centre',  # Australian Bureau of Statistics
    'APRA_NEWS': 'https://www.apra.gov.au/news-and-publications',
    'ASIC_RELEASES': 'https://asic.gov.au/about-asic/news-centre/find-a-media-release/'
}
```

---

### Step 3: Update Batch Predictor to Use Market-Specific Module

**File:** `models/screening/batch_predictor.py`

**Current (Shared):**
```python
from news_sentiment_real import get_sentiment_sync
```

**Proposed (Market-Aware):**
```python
def _get_news_sentiment_module(self, market='ASX'):
    """Get market-specific news sentiment module"""
    if market == 'US':
        from news_sentiment_us import get_sentiment_sync
    else:  # ASX or default
        from news_sentiment_asx import get_sentiment_sync
    return get_sentiment_sync
```

---

### Step 4: Update FinBERT Bridge

**File:** `models/screening/finbert_bridge.py`

**Add Market Parameter:**
```python
class FinBERTBridge:
    def __init__(self, market='ASX'):
        self.market = market
        # ... existing code ...
    
    def get_sentiment_analysis(self, symbol: str, **kwargs):
        """Get sentiment analysis using market-specific news sources"""
        if self.market == 'US':
            from news_sentiment_us import get_sentiment_sync
        else:
            from news_sentiment_asx import get_sentiment_sync
        
        return get_sentiment_sync(symbol, **kwargs)
```

---

### Step 5: Update Pipelines to Specify Market

#### ASX Pipeline (overnight_pipeline.py)
```python
def __init__(self):
    # ...
    self.predictor = BatchPredictor(market='ASX')
    # ...
```

#### US Pipeline (us_overnight_pipeline.py)
```python
def __init__(self):
    # ...
    self.predictor = BatchPredictor(market='US')
    # ...
```

---

## Data Flow Comparison

### ASX Pipeline News Flow
```
ASX Stock (e.g., CBA.AX)
    ↓
batch_predictor (market='ASX')
    ↓
finbert_bridge (market='ASX')
    ↓
news_sentiment_asx.py
    ↓
Sources:
  - RBA (Reserve Bank of Australia)
  - ASX Announcements
  - Australian Financial Review
  - ABC Business
  - ABS (Bureau of Statistics)
  - Australian Treasury
    ↓
Keywords: 'cba', 'asx', 'rba', 'cash rate', 'australian economy'
    ↓
FinBERT Analysis (Australian context)
    ↓
Sentiment Score for ASX stocks
```

### US Pipeline News Flow
```
US Stock (e.g., AAPL)
    ↓
batch_predictor (market='US')
    ↓
finbert_bridge (market='US')
    ↓
news_sentiment_us.py
    ↓
Sources:
  - Federal Reserve (Fed)
  - US Treasury
  - SEC
  - CNBC, Bloomberg, WSJ
  - BLS (Labor Statistics)
  - Census Bureau
    ↓
Keywords: 'apple', 'fed', 'fomc', 's&p 500', 'us economy', 'fed funds rate'
    ↓
FinBERT Analysis (US context)
    ↓
Sentiment Score for US stocks
```

---

## Configuration Updates

### New Config Section: `screening_config.json`

```json
{
  "news_sentiment": {
    "asx": {
      "enabled": true,
      "sources": ["rba", "asx", "afr", "abc", "treasury", "abs"],
      "cache_duration_minutes": 15,
      "max_articles_per_symbol": 20,
      "scraping_delay_seconds": 2.0,
      "keywords_weight": 1.0
    },
    "us": {
      "enabled": true,
      "sources": ["fed", "sec", "treasury", "cnbc", "wsj", "bloomberg"],
      "cache_duration_minutes": 15,
      "max_articles_per_symbol": 20,
      "scraping_delay_seconds": 2.0,
      "keywords_weight": 1.0
    }
  }
}
```

---

## Implementation Priorities

### Phase 1: Core Separation (High Priority)
1. ✅ Create `news_sentiment_us.py` with US sources
2. ✅ Rename `news_sentiment_real.py` → `news_sentiment_asx.py`
3. ✅ Add market parameter to `BatchPredictor`
4. ✅ Add market parameter to `FinBERTBridge`
5. ✅ Update both pipelines to specify market

**Expected Time:** 4-6 hours  
**Impact:** Critical - ensures correct news for each market

### Phase 2: Source Enhancement (Medium Priority)
1. ✅ Add US Federal Reserve sources (speeches, minutes, data)
2. ✅ Add US Treasury and BLS sources
3. ✅ Add US financial media RSS feeds
4. ✅ Add Australian media RSS feeds
5. ✅ Implement keyword-based relevance scoring

**Expected Time:** 4-6 hours  
**Impact:** High - improves news quality and relevance

### Phase 3: Configuration & Testing (Medium Priority)
1. ✅ Add news_sentiment config section
2. ✅ Test ASX pipeline with Australian sources
3. ✅ Test US pipeline with US sources
4. ✅ Verify sentiment scores differ appropriately
5. ✅ Document news source attribution

**Expected Time:** 2-3 hours  
**Impact:** Medium - ensures compliance and testing

### Phase 4: Advanced Features (Low Priority - Future)
1. ⏳ Social media integration (Twitter/X API)
2. ⏳ Reddit sentiment (r/wallstreetbets, r/ASX_Bets)
3. ⏳ YouTube financial commentary transcripts
4. ⏳ Podcast analysis (Odd Lots, Planet Money, etc.)
5. ⏳ Real-time news alerts

**Expected Time:** 2-3 weeks  
**Impact:** Low - nice to have, not critical

---

## Benefits of Separation

### Accuracy
- ✅ ASX stocks analyzed with Australian economic context
- ✅ US stocks analyzed with US economic context
- ✅ Fed rate decisions impact US stocks appropriately
- ✅ RBA decisions impact ASX stocks appropriately

### Relevance
- ✅ No more RBA news for US stocks
- ✅ No more Fed news for ASX stocks
- ✅ Market-specific indicators (cash rate vs fed funds)
- ✅ Local market sentiment (Wall Street vs ASX)

### Performance
- ✅ Faster news fetching (fewer irrelevant sources)
- ✅ Better keyword matching (market-specific terms)
- ✅ Reduced noise in sentiment analysis
- ✅ More accurate prediction confidence

### Compliance
- ✅ Clear attribution to news sources
- ✅ Respectful scraping (2s delays, User-Agent headers)
- ✅ Separate cache databases (no cross-contamination)
- ✅ Market-appropriate disclaimers

---

## Testing Checklist

### ASX Pipeline
- [ ] Run ASX pipeline with new `news_sentiment_asx.py`
- [ ] Verify RBA sources are fetched
- [ ] Check for Australian keywords in sentiment
- [ ] Confirm no US sources appear
- [ ] Validate sentiment scores reasonable for ASX context

### US Pipeline
- [ ] Run US pipeline with new `news_sentiment_us.py`
- [ ] Verify Fed sources are fetched
- [ ] Check for US keywords in sentiment
- [ ] Confirm no Australian sources appear
- [ ] Validate sentiment scores reasonable for US context

### Cross-Validation
- [ ] Compare sentiment for same company in different markets
  - Example: BHP (Australian mining) vs BHP ADR (US listing)
  - Should have different news sources
  - Should reflect different market contexts
- [ ] Verify cache separation (separate DB or keys)
- [ ] Check logs for correct source attribution

---

## Example Output Comparison

### Before (Broken - Shared Module)

**US Stock (AAPL) gets Australian news:**
```
Fetching news for AAPL...
Sources:
  - RBA: "Cash Rate Decision - November 2025" ❌ (Wrong country!)
  - ASX Announcements: "Mining Sector Update" ❌ (Wrong market!)
  - AFR: "Australian Banks Under Pressure" ❌ (Irrelevant!)

Sentiment: Neutral (50/100) - Based on Australian economy
```

### After (Fixed - Separate Modules)

**US Stock (AAPL) gets US news:**
```
Fetching news for AAPL...
Sources:
  - Fed: "FOMC Meeting Minutes - Rate Hike Signaled" ✅
  - CNBC: "Apple Unveils New iPhone, Stock Surges" ✅
  - Bloomberg: "Tech Sector Rally on Fed Comments" ✅
  - WSJ: "Apple Supply Chain Concerns Ease" ✅

Sentiment: Bullish (78/100) - Based on US market and Apple-specific news
```

**ASX Stock (CBA.AX) gets Australian news:**
```
Fetching news for CBA.AX...
Sources:
  - RBA: "Cash Rate Held at 4.35%, Cautious Outlook" ✅
  - ASX: "CBA Reports Strong Quarterly Earnings" ✅
  - AFR: "Banks Face Mortgage Market Pressure" ✅
  - ABC: "Australian Economy Shows Resilience" ✅

Sentiment: Moderately Bullish (65/100) - Based on Australian banking context
```

---

## Next Steps

1. **Review this plan** - Confirm approach is correct
2. **Implement Phase 1** - Create US module, separate sources
3. **Test thoroughly** - Verify both pipelines work correctly
4. **Deploy & Monitor** - Track sentiment accuracy improvements
5. **Iterate** - Add more sources based on performance

**Ready to implement?** This will significantly improve the relevance and accuracy of news-based sentiment analysis for both markets.
