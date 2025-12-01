# News, Events & Macro Data Monitoring - Current Status

## Overview

Your FinBERT system has **PARTIAL** news and event monitoring capabilities. Some features are implemented but not fully integrated into the overnight pipelines.

---

## ✅ What's Currently Working

### 1. **Event Risk Guard** (Partially Integrated)

**Location:** `models/screening/event_risk_guard.py`

**What it does:**
- ✅ Detects upcoming earnings announcements (7-day lookahead)
- ✅ Detects dividend ex-dates
- ✅ Fetches 72-hour news headlines from yfinance
- ✅ Analyzes news sentiment using FinBERT
- ✅ Detects Basel III and regulatory reports (for banks)
- ✅ Flags high-risk periods (earnings ±3 days, dividend ±1 day)
- ✅ Suggests position size haircuts (20-70% reduction)
- ✅ Calculates hedge ratios vs market index

**Data Sources:**
- yfinance calendar (earnings dates)
- yfinance dividends schedule
- yfinance news API (company-specific news)
- Optional CSV file: `config/event_calendar.csv` (manual events)

**Integration Status:**
- ✅ Integrated in US overnight pipeline (Phase 2.5)
- ✅ Integrated in ASX overnight pipeline
- ✅ Used for risk assessment before predictions
- ✅ Visible in reports

**Example Events Detected:**
```
✓ Event Risk Assessment Complete:
  Upcoming Events: 12
  Sit-Out Recommendations: 3

Stocks with upcoming events:
- AAPL: Earnings in 2 days → 40% weight haircut
- CBA.AX: Dividend in 1 day → 20% weight haircut
- WBC.AX: Basel III report → Negative sentiment warning
```

---

### 2. **News Sentiment Modules** (NOT Integrated Yet)

**Location:** 
- `models/news_sentiment_us.py` (US market)
- `models/news_sentiment_asx.py` (ASX market)

**What they can do:**
- ✅ Fetch stock-specific news from yfinance
- ✅ Scrape Federal Reserve official pages (US)
  - FOMC announcements
  - Fed speeches (Jerome Powell, etc.)
  - Monetary policy updates
  - Interest rate decisions
- ✅ Scrape RBA official pages (Australia)
  - Cash rate decisions
  - Board minutes
  - Economic statements
- ✅ Scrape SEC filings (US)
- ✅ Scrape US Treasury announcements
- ✅ Scrape Bureau of Labor Statistics (employment data)
- ✅ Analyze sentiment using FinBERT
- ✅ Cache results for 15 minutes

**Macro Keywords Monitored (US):**
```python
- Interest rates, rate hikes, rate cuts
- Inflation, CPI, PCE
- GDP growth, recession
- Unemployment, jobs report, nonfarm payroll
- Federal Reserve, FOMC, Jerome Powell
- Retail sales, consumer confidence
- Fed funds rate
```

**Macro Keywords Monitored (ASX):**
```python
- Interest rates, cash rate
- RBA (Reserve Bank of Australia)
- Inflation, GDP
- ASX announcements
- Major bank news (CBA, WBC, NAB, ANZ)
- Mining sector news
```

**Integration Status:**
- ❌ **NOT integrated** into overnight pipelines
- ⚠️ Code exists but not called
- ⚠️ Would need to be added to market sentiment analysis

---

### 3. **Market Regime Engine** (Integrated)

**Location:** `models/screening/us_market_regime_engine.py`

**What it does:**
- ✅ Analyzes market conditions (Bull/Bear/Crisis/Recovery)
- ✅ Calculates crash risk score (0-100%)
- ✅ Tracks VIX levels (fear gauge)
- ✅ Monitors S&P 500 trends
- ✅ Detects volatility spikes

**Integration Status:**
- ✅ Fully integrated in US pipeline
- ✅ Crash risk affects sentiment score
- ✅ Regime affects opportunity scoring

---

## ⚠️ Current Limitations

### What's **NOT** Currently Monitored:

1. **Federal Reserve Interest Rate Decisions:**
   - Code exists to scrape Fed announcements
   - **NOT actively integrated** into sentiment calculation
   - Would need manual CSV updates or full integration

2. **FOMC Meeting Announcements:**
   - Can be scraped from Federal Reserve website
   - **NOT automatically monitored**
   - Would impact sentiment if integrated

3. **Government Economic Data Releases:**
   - CPI (inflation), GDP, unemployment
   - Code exists to monitor
   - **NOT integrated** into pipelines

4. **RBA Cash Rate Decisions (Australia):**
   - Can be scraped from RBA website
   - **NOT automatically monitored**
   - Manual CSV updates only

5. **Major Geopolitical Events:**
   - Not monitored (requires external API)
   - Would need integration with news APIs

---

## 🔧 How It Currently Works

### Example: Interest Rate Announcement Impact

**Current Behavior:**
1. Event Risk Guard checks for earnings/dividends only
2. Market Regime Engine tracks VIX and market trends
3. **Fed rate decisions are NOT automatically detected**
4. Sentiment score based on:
   - S&P 500 / ASX 200 price movement
   - VIX levels
   - Company-specific news (72-hour window)
   - Market regime (bull/bear)

**What's Missing:**
- Real-time detection of Fed/RBA announcements
- Integration of macro economic data into sentiment
- Forward-looking event calendar (FOMC meetings)

---

## 📊 Example Workflow (Current vs Ideal)

### **Current Workflow:**

```
1. Pipeline runs → Fetch S&P 500 / ASX 200 data
2. Calculate sentiment (market index movement)
3. Check event risks (earnings, dividends)
4. Scan 72-hour news for each stock
5. Generate predictions
6. Telegram report sent
```

**Sentiment inputs:**
- ✅ Market index (S&P 500, ASX 200)
- ✅ VIX (volatility)
- ✅ Stock-specific news (yfinance)
- ✅ Earnings calendar
- ❌ Fed/RBA announcements
- ❌ Macro economic data

### **Ideal Workflow (If Fully Integrated):**

```
1. Pipeline runs
2. Check for upcoming Fed/RBA meetings (7-day lookahead)
3. Scrape Fed/RBA for recent announcements
4. Analyze sentiment of Fed/RBA statements
5. Adjust market sentiment score based on macro news
6. Fetch S&P 500 / ASX 200 data
7. Check event risks (earnings, dividends, regulatory)
8. Scan 72-hour news for each stock
9. Generate predictions (with macro context)
10. Telegram report with macro summary
```

**Sentiment inputs (enhanced):**
- ✅ Market index
- ✅ VIX
- ✅ Stock-specific news
- ✅ Earnings calendar
- ✅ Fed/RBA announcements (NEW)
- ✅ Interest rate decisions (NEW)
- ✅ Economic data releases (NEW)

---

## 🚀 Integration Options

### **Option 1: Manual Event Calendar (Quick)**

Create `config/event_calendar.csv`:

```csv
ticker,event_type,date,title,url
SPY,fed_meeting,2025-12-18,"FOMC Meeting","https://www.federalreserve.gov/..."
SPY,cpi_release,2025-12-10,"CPI Report","https://www.bls.gov/..."
XJO.AX,rba_meeting,2025-12-03,"RBA Cash Rate Decision","https://www.rba.gov.au/..."
```

**Pros:**
- ✅ Works immediately
- ✅ Already supported by Event Risk Guard
- ✅ Full control over events

**Cons:**
- ❌ Requires manual updates
- ❌ Can miss unexpected announcements

---

### **Option 2: Full News Sentiment Integration (Comprehensive)**

Integrate existing news sentiment modules into pipelines:

**Changes needed:**
1. Add news sentiment fetching to US/ASX market monitors
2. Scrape Fed/RBA pages before each pipeline run
3. Analyze macro news sentiment with FinBERT
4. Adjust market sentiment score based on macro news
5. Include macro summary in Telegram reports

**Benefits:**
- ✅ Automatic detection of Fed/RBA announcements
- ✅ Real-time sentiment from government sources
- ✅ Comprehensive macro context
- ✅ No manual updates needed

**Implementation Time:** 2-3 hours

---

### **Option 3: Hybrid Approach (Recommended)**

**Phase 1 (Quick):**
- Use manual CSV for known events (FOMC schedule, RBA meetings)
- Keep current Event Risk Guard integration

**Phase 2 (Enhanced):**
- Integrate Federal Reserve scraping for US pipeline
- Integrate RBA scraping for ASX pipeline
- Add macro news section to morning reports

**Benefits:**
- ✅ Immediate coverage of scheduled events
- ✅ Gradual enhancement with automation
- ✅ Lower maintenance once automated

---

## 📋 Current Event Types Supported

| Event Type | Detection | Integration | Source |
|------------|-----------|-------------|--------|
| **Earnings** | ✅ Auto | ✅ Yes | yfinance |
| **Dividends** | ✅ Auto | ✅ Yes | yfinance |
| **Basel III Reports** | ✅ Auto | ✅ Yes | CSV/yfinance |
| **Stock News** | ✅ Auto | ✅ Yes (72h) | yfinance |
| **Fed Meetings** | ⚠️ Manual | ❌ No | CSV only |
| **RBA Meetings** | ⚠️ Manual | ❌ No | CSV only |
| **Interest Rates** | ⚠️ Manual | ❌ No | CSV only |
| **CPI/GDP Data** | ❌ No | ❌ No | Not monitored |
| **Geopolitical** | ❌ No | ❌ No | Not monitored |

---

## 🎯 Recommendation

**To answer your question:** 

> "Is there a review media comment and government news that would impact the sentiment score?"

**Short answer:** 
- **Stock-specific news:** ✅ Yes (72-hour window, yfinance)
- **Earnings/dividends:** ✅ Yes (automatic detection)
- **Government announcements (Fed/RBA):** ⚠️ **Partially** (code exists, not integrated)
- **Interest rate decisions:** ⚠️ **Manual CSV only**
- **Major economic data:** ❌ **Not monitored**

**For best results, I recommend Option 3 (Hybrid):**
1. Create manual CSV with known Fed/RBA meetings
2. Integrate news sentiment modules (2-3 hours work)
3. Get automatic monitoring of macro announcements

---

## 📁 Relevant Files

**Event monitoring:**
- `models/screening/event_risk_guard.py` - Event detection (integrated)
- `config/event_calendar.csv` - Manual events (create this)

**News sentiment (not integrated yet):**
- `models/news_sentiment_us.py` - US macro news scraping
- `models/news_sentiment_asx.py` - ASX macro news scraping

**Market monitoring (integrated):**
- `models/screening/us_market_monitor.py` - S&P 500, VIX
- `models/screening/spi_monitor.py` - ASX 200
- `models/screening/us_market_regime_engine.py` - Market regime analysis

---

**Would you like me to:**
1. ✅ Create the manual event calendar CSV for upcoming Fed/RBA meetings?
2. ✅ Integrate the news sentiment modules into the pipelines?
3. ✅ Add macro news summary to morning reports?

Let me know which approach you prefer!
