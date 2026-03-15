# GLOBAL MARKET VIEW - FTSE 100 DATA SOURCE & MULTI-MARKET ARCHITECTURE

**Date**: 2026-01-29  
**Version**: v1.3.15.45 FINAL  
**Question**: "Where is the FTSE 100 figure coming from? Why only UK market? I thought we were trying to get a global view?"

---

## Quick Answer

**FTSE 100 Data Source**: Yahoo Finance API (^FTSE ticker), real-time during UK market hours  
**Why UK-Only**: You're viewing the **UK Morning Report** - the system actually supports **ALL THREE** major markets (AU/US/UK)  
**Global View**: Run **Option 4: Run All Markets Pipelines** to get complete global coverage

---

## 1. FTSE 100 Data Source Details

### Data Provider
- **Source**: Yahoo Finance API (via YahooQuery library)
- **Ticker Symbol**: `^FTSE` (FTSE 100 Index)
- **Additional UK Data**:
  - `^VFTSE` - UK VIX (volatility/fear index)
  - `GBPUSD=X` - GBP/USD exchange rate

### Code Location
```python
# File: models/screening/uk_overnight_pipeline.py
# Function: _fetch_uk_market_sentiment() (line ~290)

from yahooquery import Ticker

# Fetch UK market data
uk_tickers = Ticker(['^FTSE', '^VFTSE', 'GBPUSD=X'])
ftse_data = uk_tickers.price['^FTSE']

ftse_price = ftse_data.get('regularMarketPrice', 7500.0)
previous_close = ftse_data.get('regularMarketPreviousClose', ftse_price)
ftse_change = ((ftse_price - previous_close) / previous_close) * 100
```

### Data Freshness
- **Update Frequency**: Real-time during UK market hours (08:00-16:30 GMT)
- **Pipeline Run**: Overnight/morning snapshot (typically 06:00-08:00 GMT)
- **Your 0.17% Figure**: Captured at pipeline run time from live API

### Calculation
```
FTSE Change % = ((Current Price - Previous Close) / Previous Close) × 100

Example:
- Previous Close: 8,500.00
- Current Price: 8,514.45
- Change: ((8,514.45 - 8,500.00) / 8,500.00) × 100 = +0.17%
```

---

## 2. Multi-Market Architecture

### The System IS Multi-Market (You're Just Viewing One Report)

The system has **THREE separate overnight pipelines**, each with dedicated market analysis:

| Pipeline | Market | Primary Index | Secondary Indicators | Report File |
|----------|--------|---------------|---------------------|-------------|
| **AU** | ASX (Australia) | ^AORD (All Ordinaries) | SPI 200 futures, Gap prediction | `au_morning_report.json` |
| **US** | NYSE/NASDAQ | ^GSPC (S&P 500), ^DJI, ^IXIC | US futures, Pre-market | `us_morning_report.json` |
| **UK** | LSE (London) | ^FTSE (FTSE 100) | ^VFTSE (UK VIX), GBP/USD | `uk_morning_report.json` |

### Current Status: Why You See UK-Only

You're viewing the **UK Morning Report** (`uk_morning_report.json`), which is **intentionally UK-focused**. This is by design - each report focuses on its specific market for detailed regional analysis.

---

## 3. How to Get Global View

### Option A: Run All Markets Pipelines (Recommended)

```batch
1. Run: LAUNCH_COMPLETE_SYSTEM.bat
2. Choose: [4] Run All Markets Pipelines
3. Wait: 15-45 minutes (depending on market complexity)
4. Result: Three complete reports
   - reports/screening/au_morning_report.json (AU market)
   - reports/screening/us_morning_report.json (US market)
   - reports/screening/uk_morning_report.json (UK market)
```

### Option B: Run Individual Pipelines

```batch
# Australian Market
LAUNCH_COMPLETE_SYSTEM.bat → [1] Run AU Overnight Pipeline

# US Market  
LAUNCH_COMPLETE_SYSTEM.bat → [2] Run US Overnight Pipeline

# UK Market
LAUNCH_COMPLETE_SYSTEM.bat → [3] Run UK Overnight Pipeline
```

### Option C: View Unified Dashboard (Live Global View)

```batch
1. Run: LAUNCH_COMPLETE_SYSTEM.bat
2. Choose: [5] Launch Unified Trading Dashboard
3. Browser: Opens http://localhost:8050
4. Dashboard shows:
   - Market Performance (All 3 markets with intraday charts)
   - Global sentiment aggregation
   - Trading opportunities across all markets
   - Component signals (FinBERT, LSTM, Technical) for all symbols
```

---

## 4. Market Sentiment Calculation by Region

### UK Sentiment (What You're Seeing)

**Formula**:
```
Score = 50 (baseline)
      + (FTSE_change% × 10)        [FTSE 100 impact: ±30 max]
      + VFTSE_adjustment            [Fear/volatility: -15 to +5]
      - (GBPUSD_change% × 5)        [Currency impact: ±10]
      
Clamped to [0, 100]
```

**Your 0.17% Example**:
```
Score = 50
      + (0.17% × 10) = +1.7
      + VFTSE adjustment (assume -0)
      - (0.14% × 5) = -0.7
      = 51.0 (NEUTRAL to SLIGHTLY BULLISH)
```

### AU Sentiment (Different Approach)

**Formula**:
```
Score = Based on SPI 200 futures gap prediction
      + Technical analysis of ^AORD
      + Overnight US market influence
      + Currency (AUD/USD) impact
```

**Key Difference**: AU pipeline emphasizes **gap prediction** (how ASX will open relative to previous close), incorporating overnight US market movements.

### US Sentiment (Different Again)

**Formula**:
```
Score = Aggregate of S&P 500, Dow Jones, NASDAQ
      + Pre-market futures
      + Global market influence (EU/Asia overnight)
      + Sector rotation analysis
```

**Key Difference**: US pipeline provides **pre-market analysis** and is the most influential for global markets (AU/UK pipelines both reference US overnight moves).

---

## 5. Global Market Integration

### How Markets Influence Each Other

```
Timeline (GMT):
00:00 ├─ AU Market Opens (ASX 00:00 GMT = 11:00 AEDT)
      │  → Influenced by: US previous day + Asian markets
06:00 ├─ AU Market Closes
      │
08:00 ├─ UK Market Opens (LSE)
      │  → Influenced by: AU session + European markets
      │
14:30 ├─ US Market Opens (NYSE/NASDAQ)
      │  → Influenced by: UK session + global sentiment
      │
16:30 ├─ UK Market Closes
      │
21:00 ├─ US Market Closes
      └─ → Sets tone for next AU session
```

### Cross-Market Data Flow

**UK Pipeline** (`uk_morning_report.json`) includes:
- **Overnight US Markets**: S&P 500, Nasdaq, Dow Jones performance
- **Global Sentiment**: Aggregated macro news from US/EU/UK
- **Currency Influence**: GBP/USD, EUR/GBP

**AU Pipeline** (`au_morning_report.json`) includes:
- **Overnight US Markets**: Critical for gap prediction
- **SPI Futures**: Pre-market indicator for ASX
- **Currency Influence**: AUD/USD

**US Pipeline** (`us_morning_report.json`) includes:
- **Overnight Asian Markets**: AU, Japan, Hong Kong
- **European Pre-Market**: FTSE, DAX, CAC
- **Futures**: S&P, Nasdaq, Dow futures

---

## 6. Accessing Global Data

### Current Files Available

After running **Option 4: Run All Markets Pipelines**, you'll have:

```
reports/
├── screening/
│   ├── au_morning_report.json    ← AU market (ASX)
│   ├── us_morning_report.json    ← US market (NYSE/NASDAQ)
│   └── uk_morning_report.json    ← UK market (LSE)
└── morning_reports/
    ├── au_morning_report.html    ← AU HTML report
    ├── us_morning_report.html    ← US HTML report
    └── uk_morning_report.html    ← UK HTML report
```

### What Each Report Contains

**Common Structure** (all three reports):
```json
{
  "market_overview": {
    "market_code": "AU" / "US" / "UK",
    "primary_index": {
      "symbol": "^AORD" / "^GSPC" / "^FTSE",
      "price": 8514.45,
      "change_percent": 0.17
    },
    "sentiment": {
      "overall_sentiment": "Bullish",
      "sentiment_score": 69.3,
      "confidence": "High",
      "recommendation": {
        "stance": "BUY",
        "message": "Strong market conditions",
        "risk_level": "Moderate"
      }
    },
    "overnight_us_markets": {
      "sp500": { "price": 5100.50, "change": 0.45 },
      "nasdaq": { "price": 16200.30, "change": 0.67 },
      "dow": { "price": 38500.20, "change": 0.32 }
    }
  },
  "top_opportunities": [
    {
      "symbol": "SAGA.L",
      "signal": "BUY",
      "confidence": 59.5,
      "score": 42.3,
      "technical": { "rsi": 47.8, "macd": "bullish" }
    }
  ],
  "sector_summary": { ... },
  "system_stats": { ... }
}
```

---

## 7. Why Three Separate Reports?

### Design Philosophy

**Reason 1: Market-Specific Analysis**
- Each market has unique characteristics (regulations, trading hours, liquidity)
- Different technical indicators work better in different markets
- Regional news/events impact regional stocks

**Reason 2: Timing Optimization**
- Run AU pipeline after US market close (optimal timing for gap prediction)
- Run UK pipeline before LSE open (pre-market analysis)
- Run US pipeline before NYSE open (overnight integration)

**Reason 3: Modularity**
- Can run individual markets without processing all three
- Faster execution per market
- Easier debugging and maintenance

**Reason 4: Regulatory/Data**
- Different data providers per region
- Different market holidays
- Different reporting requirements

---

## 8. Creating a Unified Global View

### Future Enhancement: Global Aggregator

The system **currently** has three separate reports. To create a **single global view**, you would need to:

```python
# Proposed: models/screening/global_aggregator.py

def aggregate_global_markets():
    """Combine AU/US/UK reports into unified global view."""
    
    # Load all three reports
    au_report = load_json('reports/screening/au_morning_report.json')
    us_report = load_json('reports/screening/us_morning_report.json')
    uk_report = load_json('reports/screening/uk_morning_report.json')
    
    # Aggregate sentiment
    global_sentiment = {
        'au': au_report['market_overview']['sentiment'],
        'us': us_report['market_overview']['sentiment'],
        'uk': uk_report['market_overview']['sentiment'],
        'weighted_score': (
            au_report['sentiment_score'] * 0.25 +  # AU 25%
            us_report['sentiment_score'] * 0.50 +  # US 50% (dominant)
            uk_report['sentiment_score'] * 0.25    # UK 25%
        )
    }
    
    # Aggregate top opportunities
    all_opportunities = (
        au_report['top_opportunities'] +
        us_report['top_opportunities'] +
        uk_report['top_opportunities']
    )
    all_opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'global_sentiment': global_sentiment,
        'top_global_opportunities': all_opportunities[:20],
        'market_breakdown': {
            'au': au_report['market_overview'],
            'us': us_report['market_overview'],
            'uk': uk_report['market_overview']
        }
    }
```

---

## 9. Immediate Action Plan

### To Answer Your Question Directly

**Step 1**: Run all three market pipelines
```batch
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
LAUNCH_COMPLETE_SYSTEM.bat
[Choose Option 4: Run All Markets Pipelines]
```

**Step 2**: View all three reports
```batch
# JSON reports (data)
type reports\screening\au_morning_report.json
type reports\screening\us_morning_report.json  
type reports\screening\uk_morning_report.json

# HTML reports (visual)
start reports\morning_reports\au_morning_report.html
start reports\morning_reports\us_morning_report.html
start reports\morning_reports\uk_morning_report.html
```

**Step 3**: Launch unified dashboard (live global view)
```batch
LAUNCH_COMPLETE_SYSTEM.bat
[Choose Option 5: Launch Unified Trading Dashboard]
Browser opens: http://localhost:8050
```

**Step 4**: Review Market Performance panel in dashboard
- Shows **all three markets** with intraday charts
- Live sentiment for AU, US, UK
- Trading opportunities across all markets

---

## 10. Summary

### Your Question Answered

| Question | Answer |
|----------|---------|
| **Where is FTSE 100 coming from?** | Yahoo Finance API (`^FTSE`) via YahooQuery library |
| **Why 0.17% specifically?** | Real-time snapshot from UK market at pipeline run time |
| **Why UK-only?** | You're viewing UK Morning Report - system supports all 3 markets |
| **How to get global view?** | Run Option 4 (All Markets) or launch Unified Dashboard |

### The System IS Multi-Market

```
✅ AU Market Support: FULL (overnight_pipeline.py)
✅ US Market Support: FULL (us_overnight_pipeline.py)  
✅ UK Market Support: FULL (uk_overnight_pipeline.py)
✅ Multi-Market Dashboard: FULL (unified_trading_dashboard.py)
✅ Cross-Market Influence: FULL (overnight US data in AU/UK reports)
```

### Bottom Line

The FTSE 100 figure (0.17%) comes from **Yahoo Finance API** and represents **UK market-specific** analysis. The system **already provides global coverage** through three parallel pipelines - you just need to:

1. Run all three market pipelines (Option 4)
2. View unified dashboard for live global monitoring
3. Each report includes overnight data from other markets

**The global view exists - you were just looking at one piece of it!**

---

## Files Referenced

- `models/screening/uk_overnight_pipeline.py` (UK sentiment, line ~290-400)
- `models/screening/overnight_pipeline.py` (AU sentiment)
- `models/screening/us_overnight_pipeline.py` (US sentiment)
- `unified_trading_dashboard.py` (Multi-market dashboard, line ~1040-1100)
- `LAUNCH_COMPLETE_SYSTEM.bat` (Options 1-5 for pipelines)

---

**Status**: Question answered - System provides full global coverage  
**Action**: Run Option 4 to see complete AU/US/UK analysis  
**Priority**: Information complete - no code changes needed
