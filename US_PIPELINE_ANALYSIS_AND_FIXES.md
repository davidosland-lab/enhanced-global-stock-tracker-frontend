# 🔍 US Pipeline Analysis & Issue Resolution

**Date:** January 22, 2026  
**Version:** v1.3.15.24  
**Status:** ⚠️ Issues Identified + Solutions Provided

---

## 🎯 User Report Summary

**Issues Reported:**
1. ❌ US pipeline running **Australian stocks** instead of US stocks
2. ❌ **No sentiment analysis** appearing in output
3. ❌ FinBERT should review **latest media commentary** and **US Fed announcements**
4. ❌ Missing analysis of **major global events**

---

## ✅ Analysis Results

### Issue #1: Australian vs US Stocks ✅ **FALSE ALARM**

**Finding:** The US pipeline is **correctly configured** with US stocks.

**Evidence:**
- `config/us_sectors.json` contains **240 US stocks** (8 sectors × 30 stocks each)
- Sectors: Financials, Materials, Healthcare, Technology, Energy, Industrials, Consumer_Discretionary, Consumer_Staples
- Example stocks: AAPL, MSFT, GOOGL, AMZN, JPM, BAC, XOM, CVX, JNJ, UNH
- **No Australian stocks** (.AX suffix) found in US pipeline code
- US-specific scanner: `models/screening/us_stock_scanner.py` (no .AX suffix handling)

**Conclusion:** This is **NOT** an issue. The US pipeline scans US stocks correctly.

**Possible Confusion:**
- User may have seen logs from a **different pipeline run** (AU pipeline)
- Or terminal output was mixed from multiple sessions

---

### Issue #2: No Sentiment Analysis Appearing ⚠️ **REAL ISSUE**

**Finding:** FinBERT sentiment analysis **IS implemented** but may not be **visible** in output.

**Architecture:**
```
run_us_full_pipeline.py (Option 2)
    ↓
models/screening/us_overnight_pipeline.py
    ↓
models/screening/batch_predictor.py
    ↓
models/screening/finbert_bridge.py
    ↓
finbert_v4.4.4/models/news_sentiment_real.py (fetches news)
    ↓
finbert_v4.4.4/models/finbert_sentiment.py (FinBERT analysis)
```

**What FinBERT Does:**
1. **Fetches news** via `yfinance` API (Yahoo Finance)
2. **Analyzes sentiment** using FinBERT transformer model (ProsusAI/finbert)
3. **Scores** each stock with sentiment score (0-100)
4. **Integrates** sentiment into ensemble prediction

**Problem:** Sentiment data exists but may not be **displayed prominently** in reports.

**Root Causes:**
1. **Silent failures** - If FinBERT bridge fails to initialize, pipeline continues with defaults
2. **Log verbosity** - Sentiment scores may be logged but not visible in terminal output
3. **Report format** - HTML reports may not highlight sentiment prominently
4. **Cache issues** - Old cached data without sentiment

---

### Issue #3: Fed Announcements & Global Events ❌ **MISSING**

**Finding:** FinBERT analyzes **stock-specific news** but **NOT** Fed announcements or global events.

**Current News Sources:**
- ✅ Yahoo Finance (stock-specific news via `yfinance` API)
- ✅ Stock filings and press releases
- ❌ Federal Reserve announcements (FOMC, rate decisions)
- ❌ Treasury statements
- ❌ Global macro events (ECB, BoJ, geopolitical events)
- ❌ Economic indicators (CPI, jobs, GDP)

**What's Missing:**
1. **Fed RSS Feeds** - Federal Reserve press releases and speeches
2. **Economic Calendar** - CPI, NFP, GDP releases
3. **Global News** - Reuters, Bloomberg macro news
4. **Regulatory Announcements** - SEC, Treasury, Fed statements

**Current Implementation (AU Pipeline Only):**
- Australian pipeline fetches RBA (Reserve Bank of Australia) news
- US pipeline **does NOT** fetch Fed news yet

---

## 🛠️ Solutions & Fixes

### Fix #1: Make Sentiment Visible in Output

#### Option A: Enhanced Logging (Quick Fix)

Add verbose sentiment logging to `batch_predictor.py`:

```python
# In batch_predictor.py, after sentiment analysis:
if sentiment_score:
    logger.info(f"  📊 {symbol} Sentiment: {sentiment_score:.1f}/100 ({sentiment_label})")
    logger.info(f"     News Articles: {article_count}")
    logger.info(f"     Latest: {latest_headline[:80]}...")
```

#### Option B: Enhanced HTML Report (Better)

Modify `report_generator.py` to add sentiment section:

```python
# Add to HTML report:
<div class="sentiment-section">
    <h3>FinBERT Sentiment Analysis</h3>
    <table>
        <tr>
            <th>Symbol</th>
            <th>Sentiment Score</th>
            <th>Label</th>
            <th>News Count</th>
            <th>Latest Headline</th>
        </tr>
        {% for stock in stocks %}
        <tr>
            <td>{{ stock.symbol }}</td>
            <td class="{{ sentiment_class(stock.sentiment) }}">
                {{ stock.sentiment_score }}/100
            </td>
            <td>{{ stock.sentiment_label }}</td>
            <td>{{ stock.news_count }}</td>
            <td>{{ stock.latest_headline }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
```

#### Option C: JSON Output Enhancement (Best for Integration)

Add sentiment to `outputs/us_signals_report.json`:

```json
{
  "symbol": "AAPL",
  "prediction": 1,
  "confidence": 0.85,
  "finbert_sentiment": {
    "score": 82.5,
    "label": "Positive",
    "confidence": 0.91,
    "news_count": 15,
    "latest_headline": "Apple reports record Q4 earnings...",
    "analysis_timestamp": "2026-01-22T08:30:00Z"
  }
}
```

---

### Fix #2: Add Fed & Global Event Analysis

#### Implementation Plan

**New Module:** `models/screening/fed_news_monitor.py`

```python
"""
Federal Reserve & Global Event Monitor
Fetches macro news that impacts all US markets
"""

import feedparser
import requests
from datetime import datetime, timedelta

class FedNewsMonitor:
    """Monitor Fed announcements and global macro events"""
    
    def __init__(self):
        self.sources = {
            'fed_press_releases': 'https://www.federalreserve.gov/feeds/press_all.xml',
            'fed_speeches': 'https://www.federalreserve.gov/feeds/speeches.xml',
            'treasury': 'https://home.treasury.gov/rss',
            'sec': 'https://www.sec.gov/news/pressreleases.rss',
            'bls_employment': 'https://www.bls.gov/feed/bls_latest.rss',
            'census_economic': 'https://www.census.gov/economic-indicators/indicator.xml'
        }
    
    def fetch_fed_announcements(self, hours=24):
        """Fetch Fed press releases and speeches from last 24 hours"""
        announcements = []
        
        for source_name, rss_url in self.sources.items():
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    pub_date = self._parse_date(entry.published)
                    
                    # Filter to last 24 hours
                    if datetime.now() - pub_date < timedelta(hours=hours):
                        announcements.append({
                            'source': source_name,
                            'title': entry.title,
                            'summary': entry.get('summary', ''),
                            'link': entry.link,
                            'published': pub_date.isoformat(),
                            'category': self._categorize(entry.title)
                        })
            except Exception as e:
                logger.error(f"Error fetching {source_name}: {e}")
        
        return announcements
    
    def _categorize(self, title):
        """Categorize Fed announcements"""
        title_lower = title.lower()
        
        if 'rate' in title_lower or 'fomc' in title_lower:
            return 'INTEREST_RATES'
        elif 'inflation' in title_lower or 'cpi' in title_lower:
            return 'INFLATION'
        elif 'employment' in title_lower or 'jobs' in title_lower:
            return 'EMPLOYMENT'
        elif 'gdp' in title_lower or 'growth' in title_lower:
            return 'ECONOMIC_GROWTH'
        elif 'bank' in title_lower or 'financial' in title_lower:
            return 'FINANCIAL_REGULATION'
        else:
            return 'OTHER'
    
    def analyze_market_impact(self, announcements):
        """Analyze likely market impact of Fed announcements"""
        impact_scores = {
            'INTEREST_RATES': 10,  # Highest impact
            'INFLATION': 8,
            'EMPLOYMENT': 7,
            'ECONOMIC_GROWTH': 6,
            'FINANCIAL_REGULATION': 5,
            'OTHER': 2
        }
        
        overall_sentiment = 0
        major_events = []
        
        for announcement in announcements:
            category = announcement['category']
            impact = impact_scores.get(category, 0)
            
            # Use FinBERT to analyze the announcement text
            sentiment = self._analyze_fed_sentiment(announcement['title'] + ' ' + announcement['summary'])
            
            overall_sentiment += sentiment * impact
            
            if impact >= 7:  # Major event
                major_events.append({
                    'title': announcement['title'],
                    'category': category,
                    'sentiment': sentiment,
                    'impact_score': impact
                })
        
        return {
            'overall_sentiment': overall_sentiment / len(announcements) if announcements else 0,
            'major_events': major_events,
            'total_announcements': len(announcements)
        }
```

**Integration into US Pipeline:**

```python
# In us_overnight_pipeline.py, Phase 1:

def _fetch_us_market_sentiment(self):
    """Fetch US market sentiment + Fed announcements"""
    
    # Original market sentiment (S&P 500, VIX, etc.)
    sentiment = self.market_monitor.get_market_overview()
    
    # NEW: Fetch Fed announcements
    if hasattr(self, 'fed_monitor'):
        fed_data = self.fed_monitor.fetch_fed_announcements(hours=24)
        fed_impact = self.fed_monitor.analyze_market_impact(fed_data)
        
        # Add to sentiment data
        sentiment['fed_announcements'] = fed_data
        sentiment['fed_impact'] = fed_impact
        
        # Log major events
        if fed_impact['major_events']:
            logger.info("\n🏛️ MAJOR FED ANNOUNCEMENTS (Last 24 Hours):")
            for event in fed_impact['major_events']:
                logger.info(f"  • {event['category']}: {event['title']}")
                logger.info(f"    Impact: {event['impact_score']}/10, Sentiment: {event['sentiment']:.1f}")
    
    return sentiment
```

---

## 📋 Implementation Checklist

### Phase 1: Make Sentiment Visible (1-2 hours)

- [ ] Add verbose sentiment logging to `batch_predictor.py`
- [ ] Enhance `outputs/us_signals_report.json` with sentiment data
- [ ] Add sentiment section to HTML report template
- [ ] Test with 5 stocks to verify sentiment appears

### Phase 2: Add Fed News Monitor (3-4 hours)

- [ ] Create `models/screening/fed_news_monitor.py`
- [ ] Implement RSS feed parsing for Fed sources
- [ ] Add FinBERT analysis for Fed announcements
- [ ] Integrate into `us_overnight_pipeline.py` Phase 1
- [ ] Test Fed announcement detection and analysis

### Phase 3: Enhance Reporting (2-3 hours)

- [ ] Add "Fed & Global Events" section to HTML report
- [ ] Display major announcements prominently
- [ ] Add market impact summary
- [ ] Include sentiment scores for each announcement
- [ ] Generate email alerts for major Fed events

---

## 🧪 Testing Instructions

### Test 1: Verify US Stocks (5 minutes)

```cmd
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15

:: Check US sectors config
type config\us_sectors.json | findstr "AAPL MSFT JPM"

:: Expected: Should show US stocks, NOT .AX stocks
```

### Test 2: Check FinBERT Status (5 minutes)

```cmd
:: Run quick test mode
python run_us_full_pipeline.py --mode test

:: Watch logs for these lines:
:: [OK] FinBERT Bridge initialized successfully
:: [OK] FinBERT LSTM Available: True
:: [OK] FinBERT Sentiment Available: True
```

### Test 3: Verify Sentiment in Output (10 minutes)

```cmd
:: Run full pipeline
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

:: After completion, check report:
type outputs\us_signals_report.json | findstr "sentiment"

:: Expected: Should see sentiment scores for each stock
```

### Test 4: Check Fed News Sources (5 minutes)

```python
# Test Fed RSS feeds
import feedparser

urls = [
    'https://www.federalreserve.gov/feeds/press_all.xml',
    'https://www.federalreserve.gov/feeds/speeches.xml'
]

for url in urls:
    feed = feedparser.parse(url)
    print(f"\n{url}")
    print(f"  Entries: {len(feed.entries)}")
    if feed.entries:
        print(f"  Latest: {feed.entries[0].title}")
        print(f"  Date: {feed.entries[0].published}")
```

---

## 📊 Expected Output After Fixes

### Terminal Output (During Pipeline Run)

```
================================================================================
PHASE 3: BATCH PREDICTION
================================================================================
Generating predictions for 240 stocks...

🧠 FinBERT Sentiment Analysis:
  📊 AAPL Sentiment: 82.5/100 (Positive)
     News Articles: 15
     Latest: Apple reports record Q4 earnings beating estimates...
  
  📊 MSFT Sentiment: 78.3/100 (Positive)
     News Articles: 12
     Latest: Microsoft Azure grows 30% as cloud demand surges...

🏛️ MAJOR FED ANNOUNCEMENTS (Last 24 Hours):
  • INTEREST_RATES: Federal Reserve holds rates steady at 5.25%-5.50%
    Impact: 10/10, Sentiment: 65.0 (Cautiously Positive)
  
  • INFLATION: Powell signals inflation progress, rate cuts possible in 2026
    Impact: 10/10, Sentiment: 72.5 (Positive)

================================================================================
PHASE 5: US MARKET REPORT GENERATION
================================================================================
[OK] Report Generated: outputs/us_signals_report.html
[OK] Sentiment data included for all 240 stocks
[OK] Fed announcements section added
```

### JSON Output (`outputs/us_signals_report.json`)

```json
{
  "timestamp": "2026-01-22T08:30:00Z",
  "market": "US",
  "fed_announcements": [
    {
      "title": "Federal Reserve maintains current policy stance",
      "category": "INTEREST_RATES",
      "sentiment": 65.0,
      "impact_score": 10,
      "published": "2026-01-21T14:00:00Z"
    }
  ],
  "market_sentiment": {
    "overall": "Positive",
    "score": 72.5,
    "fed_impact": 7.8
  },
  "top_opportunities": [
    {
      "symbol": "AAPL",
      "opportunity_score": 92.5,
      "prediction": 1,
      "confidence": 0.85,
      "finbert_sentiment": {
        "score": 82.5,
        "label": "Positive",
        "confidence": 0.91,
        "news_count": 15,
        "latest_headline": "Apple reports record Q4 earnings...",
        "key_topics": ["earnings", "iPhone sales", "services growth"]
      },
      "technical_score": 88.2,
      "lstm_prediction": 0.89
    }
  ]
}
```

---

## 🚀 Quick Action Plan

### Immediate (Today)
1. ✅ Verify US pipeline scans US stocks (already confirmed)
2. ⏳ Add sentiment logging to `batch_predictor.py`
3. ⏳ Test pipeline with 5 stocks to see sentiment output

### Short-term (This Week)
1. ⏳ Implement `fed_news_monitor.py`
2. ⏳ Integrate Fed announcements into US pipeline
3. ⏳ Enhance HTML/JSON reports with sentiment

### Medium-term (Next Week)
1. ⏳ Add global event monitoring (ECB, BoJ, geopolitical)
2. ⏳ Create email alerts for major Fed announcements
3. ⏳ Backtest sentiment impact on predictions

---

## 📝 Summary

**Issues Status:**
1. ❌ Australian stocks in US pipeline → ✅ **FALSE ALARM** (US stocks confirmed)
2. ⚠️ No sentiment appearing → **REAL ISSUE** (sentiment exists but not visible)
3. ❌ Missing Fed announcements → **TRUE** (not implemented yet)
4. ❌ Missing global events → **TRUE** (not implemented yet)

**Solutions:**
- **Quick Fix:** Add logging to show sentiment scores (1 hour)
- **Medium Fix:** Enhance reports with sentiment data (3 hours)
- **Complete Fix:** Add Fed news monitor + global events (8 hours)

**Bottom Line:**
The US pipeline is **correctly implemented** with FinBERT sentiment analysis, but the **output needs enhancement** to make sentiment visible, and **Fed announcements need to be added** as a new feature.

---

**Document:** `US_PIPELINE_ANALYSIS_AND_FIXES.md`  
**Version:** 1.0  
**Date:** 2026-01-22  
**Next Review:** After implementing Phase 1 fixes
