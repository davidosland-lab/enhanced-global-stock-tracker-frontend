# World Event Risk Integration + HTML Reports Fix - v193

**Date:** 2026-03-01  
**Base:** v192 (AI-Enhanced Macro Sentiment)  
**Status:** ⏳ IN PROGRESS

---

## 🎯 What This Patch Does

### **Problem 1: HTML Reports Missing**
UK and US pipelines are NOT generating HTML morning reports (only JSON), making it hard to review overnight results.

### **Problem 2: World Events Not Integrated**
The AI macro sentiment analyzer (v192) detects crises but:
- ❌ Not integrated into overnight pipeline flow
- ❌ Not displayed in morning reports
- ❌ Not affecting trading gates/position sizing
- ❌ World risk score exists but isn't used

---

## 🔧 Solution Architecture

You identified the PERFECT integration points:

```
Overnight Pipeline Flow:
  ├─ Phase 1.1: Market Data Collection
  ├─ Phase 1.2: SPI Sentiment Analysis
  ├─ Phase 1.3: Macro News Monitoring ← ALREADY EXISTS
  │   ├─ RBA/BoE/Fed releases
  │   ├─ Global news scraping
  │   └─ 🆕 ADD: World Event Risk Assessment
  ├─ Phase 2: Stock Screening
  ├─ Phase 3: Event Risk Guard
  └─ Phase 4: Report Generation
      ├─ JSON report (working ✓)
      └─ HTML report (MISSING for UK/US ❌)
```

---

## 📋 Implementation Plan

### **Task 1: World Event Monitor Module**
**File:** `pipelines/models/screening/world_event_monitor.py`

**Output Format:**
```python
{
    "world_risk_score": 0-100,        # Composite risk (50 = neutral)
    "risk_level": "LOW|MODERATE|ELEVATED|HIGH|EXTREME",
    "fear": 0.0-1.0,                  # Fear emotion intensity
    "anger": 0.0-1.0,                 # Anger emotion intensity
    "neg_sent": 0.0-1.0,              # Negative sentiment (FinBERT)
    "top_topics": ["war", "oil", ...],
    "top_headlines": ["...", "..."],
    "timestamp": "2026-03-01T09:42:00Z",
    "article_count": 15,
    "sources": ["Reuters", "BBC", ...]
}
```

**Calculation:**
```python
world_risk_score = (
    neg_sent * 30 +      # FinBERT negative sentiment
    fear * 35 +          # Fear emotion (from transformer)
    anger * 20 +         # Anger emotion
    topic_severity * 15  # War/crisis keywords
)
```

---

### **Task 2: Integration into Overnight Pipeline**
**File:** `pipelines/models/screening/overnight_pipeline.py`

**Location:** `_fetch_market_sentiment()` method (line ~520)

**Current Code:**
```python
def _fetch_market_sentiment(self, market_data: Optional[Dict] = None) -> Dict:
    sentiment = self.spi_monitor.get_overnight_summary(market_data)
    
    # Phase 1.3: Macro News Monitoring (RBA/Global)
    if self.macro_monitor is not None:
        macro_news = self.macro_monitor.get_macro_sentiment()
        sentiment['macro_news'] = macro_news
    
    return sentiment
```

**New Code:**
```python
def _fetch_market_sentiment(self, market_data: Optional[Dict] = None) -> Dict:
    sentiment = self.spi_monitor.get_overnight_summary(market_data)
    
    # Phase 1.3: Macro News Monitoring (RBA/Global)
    if self.macro_monitor is not None:
        macro_news = self.macro_monitor.get_macro_sentiment()
        sentiment['macro_news'] = macro_news
    
    # 🆕 Phase 1.4: World Event Risk Assessment
    if self.world_event_monitor is not None:
        world_risk = self.world_event_monitor.get_world_event_risk()
        sentiment['world_event_risk'] = world_risk
        
        # Adjust market sentiment based on world risk
        raw_score = sentiment.get('sentiment_score', 50)
        world_score = world_risk.get('world_risk_score', 50)
        
        # Apply penalty (centered at 50 = neutral)
        penalty = 0.35 * (world_score - 50)  # Tune: 0.25-0.50
        
        sentiment['sentiment_score_raw'] = raw_score
        sentiment['sentiment_score'] = max(0, min(100, raw_score - penalty))
        
        # Recompute recommendation with adjusted score
        sentiment['recommendation'] = self.spi_monitor._get_recommendation(
            sentiment['sentiment_score'],
            sentiment.get('gap_prediction', 0)
        )
        
        logger.info(f"  World Risk: {world_score}/100 ({world_risk['risk_level']})")
        logger.info(f"  Sentiment: {raw_score:.1f} → {sentiment['sentiment_score']:.1f} (penalty: {penalty:.1f})")
    
    return sentiment
```

---

### **Task 3: Report Generator Enhancement**
**File:** `pipelines/models/screening/report_generator.py`

**Location:** `_build_market_overview()` method

**Add World Risk Card:**
```python
def _build_market_overview(self, spi_sentiment: Dict) -> str:
    # ... existing market overview HTML ...
    
    # 🆕 Add World Event Risk Card
    world_risk = spi_sentiment.get('world_event_risk', {})
    if world_risk:
        world_score = world_risk.get('world_risk_score', 50)
        risk_level = world_risk.get('risk_level', 'UNKNOWN')
        
        # Color coding
        if world_score >= 80:
            color = '#dc3545'  # Red (danger)
        elif world_score >= 65:
            color = '#ffc107'  # Yellow (warning)
        else:
            color = '#28a745'  # Green (safe)
        
        world_html = f'''
        <div class="metric-card">
            <div class="metric-label">World Event Risk</div>
            <div class="metric-value" style="color: {color}">
                {world_score}/100
            </div>
            <div class="metric-sublabel">{risk_level}</div>
            <div class="metric-detail">
                Fear: {world_risk.get('fear', 0):.2f} | 
                Anger: {world_risk.get('anger', 0):.2f}
            </div>
            <div class="metric-detail">
                Top: {', '.join(world_risk.get('top_topics', [])[:3])}
            </div>
        </div>
        '''
        
        market_overview_html += world_html
    
    return market_overview_html
```

---

### **Task 4: Trading Gates Integration**
**File:** `core/sentiment_integration.py`

**Location:** `_determine_trading_decision()` method

**Add World Risk Gates:**
```python
def _determine_trading_decision(self, ...):
    # ... existing gate logic ...
    
    # 🆕 World Risk Gate (market-wide overlay)
    world_risk = morning_data.get('world_event_risk', {})
    world_score = world_risk.get('world_risk_score', 50)
    
    if world_score >= 85 and market_sentiment < 60:
        # Extreme world risk + weak market = BLOCK
        decision = "BLOCK"
        size_multiplier = 0.0
        reasons.append(
            f"World risk EXTREME ({world_score}/100): "
            f"{world_risk.get('risk_level', '')} - "
            f"Top: {', '.join(world_risk.get('top_topics', [])[:2])}"
        )
    elif world_score >= 75:
        # Elevated world risk = REDUCE
        if decision == "ALLOW":
            decision = "REDUCE"
        size_multiplier = min(size_multiplier, 0.6)  # Max 60% size
        reasons.append(
            f"World risk elevated ({world_score}/100): "
            f"{world_risk.get('risk_level', '')}"
        )
    elif world_score >= 65:
        # Moderate world risk = slight reduction
        size_multiplier = min(size_multiplier, 0.85)  # Max 85% size
        reasons.append(f"World risk moderate ({world_score}/100)")
    
    return decision, size_multiplier, reasons
```

---

### **Task 5: HTML Report Generation Fix**
**Files:** `scripts/run_uk_full_pipeline.py`, `scripts/run_us_full_pipeline.py`

**Problem:** These pipelines only save JSON, not HTML.

**Current Code (UK/US):**
```python
# Save report (JSON only)
report_path = f"reports/uk_pipeline_report_{today_str}.json"
with open(report_path, 'w') as f:
    json.dump(report_data, f, indent=2)
```

**Fixed Code:**
```python
# Generate HTML report
from pipelines.models.screening.report_generator import ReportGenerator

report_gen = ReportGenerator()
html_path = report_gen.generate_morning_report(
    opportunities=opportunities,
    spi_sentiment=spi_sentiment,
    sector_summary=sector_summary,
    system_stats=system_stats,
    event_risk_data=event_risk_data,
    market_data=market_data
)

logger.info(f"[OK] HTML report: {html_path}")

# Also save JSON
json_path = f"reports/uk_pipeline_report_{today_str}.json"
with open(json_path, 'w') as f:
    json.dump(report_data, f, indent=2)

logger.info(f"[OK] JSON report: {json_path}")
```

---

## 📊 Expected Behavior After Patch

### **Tonight's Pipeline Run:**

```
[09:40] Phase 1.1: Collecting market data...
[09:41] Phase 1.2: SPI sentiment analysis... Score: 55/100
[09:42] Phase 1.3: Macro news monitoring...
[09:42]   - RBA: 3 articles, sentiment: NEUTRAL
[09:42]   - Global: 8 articles, sentiment: BEARISH (-0.54)
[09:43] Phase 1.4: World event risk assessment...
[09:43]   - Analyzed 15 headlines
[09:43]   - Detected: war (3), conflict (2), oil shock (1)
[09:43]   - Fear: 0.72, Anger: 0.58
[09:43]   - World Risk: 78/100 (ELEVATED)
[09:43]   - Sentiment adjustment: 55 → 45 (penalty: -10)
[09:43]   - Recommendation: NEUTRAL → CAUTION
[09:44] Phase 2: Stock screening (200 stocks)...
[09:50] Phase 3: Event risk guard...
[09:51] Phase 4: Report generation...
[09:51]   - HTML: reports/uk_morning_report_20260301.html ✓
[09:51]   - JSON: reports/uk_pipeline_report_20260301.json ✓
```

### **Tomorrow's Paper Trading:**

```
[08:00] Loading pipeline report...
[08:00] Market sentiment: 45/100 (CAUTION)
[08:00] World risk: 78/100 (ELEVATED)
[08:00] ⚠️ World risk elevated - reducing position sizes
[08:01] Position multiplier: 0.60 (was 1.00)
[08:05] Opening position AAPL: $3,000 (was $5,000)
[08:06] Opening position MSFT: $3,000 (was $5,000)
```

---

## 🎯 Key Metrics

| Metric | Before v193 | After v193 |
|--------|-------------|------------|
| **HTML Reports** | AU only | AU + UK + US ✓ |
| **World Risk Integration** | ❌ Not used | ✓ Full integration |
| **Trading Gates** | Market sentiment only | + World risk overlay |
| **Position Sizing** | Fixed | Dynamic (world risk aware) |
| **Report Display** | 4 metrics | 5 metrics (+ world risk) |

---

## 📥 Implementation Status

- [ ] Create world_event_monitor.py
- [ ] Integrate into overnight_pipeline.py
- [ ] Update report_generator.py (HTML display)
- [ ] Update sentiment_integration.py (trading gates)
- [ ] Fix UK/US pipeline scripts (HTML generation)
- [ ] Create installation BAT file
- [ ] Test end-to-end integration

---

## ⏱️ Timeline

**Estimated Time:** 2-3 hours to implement + test

**Should I proceed with creating the full patch files?**

This is a more substantial change than v192 (which just added analysis), because v193:
1. Adds new module (world_event_monitor.py)
2. Modifies overnight pipeline logic (sentiment adjustment)
3. Updates report generator (new display section)
4. Modifies trading gates (new blocking/reduction rules)
5. Fixes UK/US pipeline scripts (HTML generation)

**Do you want me to:**
A) Create the complete patch now (all files)?
B) Start with just the HTML report fix (simpler, immediate value)?
C) Review the integration plan first and adjust before coding?

---

**Note:** This builds on v192 (AI sentiment), so you should have v192 installed first, or I can create v193 as a standalone that includes both v192 + v193 changes.
