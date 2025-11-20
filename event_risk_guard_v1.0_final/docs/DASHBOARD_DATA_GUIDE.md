# Dashboard Data Guide

## What Data Shows on the Dashboard

The dashboard displays **real data** from the overnight pipeline execution. Here's exactly what you'll see:

---

## 📊 Real-Time Data Sources

### Data Flow
```
Overnight Pipeline Runs
    ↓
Saves: reports/pipeline_state/{date}_pipeline_state.json
    ↓
Web UI Reads: /api/status
    ↓
Dashboard Displays: Live Data
```

---

## 1. System Status Cards (4 Cards)

### 🟢 System Status
**Data Source**: Configuration + Pipeline state
**Shows**:
- **Active**: Pipeline has run and data exists
- **Inactive**: No recent pipeline execution

**Real Example**:
```
System Status
Active
```

### 📧 Email Notifications
**Data Source**: `screening_config.json` → `email_notifications.enabled`
**Shows**:
- **Enabled**: Emails will be sent after pipeline runs
- **Disabled**: No emails (silent mode)

**Real Example**:
```
Email Notifications
Enabled
```

### 🤖 LSTM Training
**Data Source**: `screening_config.json` → `lstm_training.enabled`
**Shows**:
- **Enabled**: System trains LSTM models automatically
- **Disabled**: No automatic training

**Real Example**:
```
LSTM Training
Enabled
```

### 📈 SPI Monitoring
**Data Source**: `screening_config.json` → `spi_monitoring.enabled`
**Shows**:
- **Enabled**: Monitors SPI200/ASX overnight gaps
- **Disabled**: No SPI tracking

**Real Example**:
```
SPI Monitoring
Enabled
```

---

## 2. Pipeline Summary (4 Metrics)

**Data Source**: `{date}_pipeline_state.json` → `summary` object

### Real Data Structure:
```json
{
  "summary": {
    "report_date": "2025-11-15",
    "total_stocks_scanned": 81,
    "opportunities_found": 15,
    "spi_sentiment_score": 72.5,
    "market_bias": "BULLISH"
  }
}
```

### What You See:
```
Stocks Scanned: 81
Opportunities Found: 15
SPI Sentiment: 72.5/100
Market Bias: BULLISH
```

**Values Explained**:
- **Stocks Scanned**: Total ASX stocks analyzed (typically 80-100)
- **Opportunities Found**: Stocks with opportunity_score ≥ 65
- **SPI Sentiment**: Market sentiment (0-100, higher = more bullish)
- **Market Bias**: BULLISH / BEARISH / NEUTRAL

---

## 3. Top 10 Opportunities Table

**Data Source**: `{date}_pipeline_state.json` → `top_opportunities[]`

### Real Data Structure:
```json
{
  "top_opportunities": [
    {
      "symbol": "BHP.AX",
      "company_name": "BHP Group Limited",
      "opportunity_score": 87.3,
      "signal": "BUY",
      "confidence": 89.2,
      "sector": "Materials",
      "current_price": 45.67
    },
    {
      "symbol": "CBA.AX",
      "company_name": "Commonwealth Bank",
      "opportunity_score": 84.1,
      "signal": "BUY",
      "confidence": 85.7,
      "sector": "Financials",
      "current_price": 112.34
    }
  ]
}
```

### What You See:
| Symbol | Score | Signal | Confidence | Sector |
|--------|-------|--------|-----------|--------|
| BHP.AX | 87.3 🟢 | BUY | 89.2% | Materials |
| CBA.AX | 84.1 🟢 | BUY | 85.7% | Financials |
| CSL.AX | 76.5 🟡 | HOLD | 72.3% | Healthcare |
| WES.AX | 71.2 🟡 | BUY | 68.9% | Consumer |
| FMG.AX | 58.3 🔴 | SELL | 61.2% | Materials |

**Color Coding**:
- 🟢 **Green (80-100)**: High confidence - Strong opportunity
- 🟡 **Yellow (60-79)**: Medium confidence - Moderate opportunity
- 🔴 **Red (0-59)**: Low confidence - Weak/negative signal

**Columns Explained**:
- **Symbol**: ASX stock code (e.g., BHP.AX, CBA.AX)
- **Score**: Opportunity score (0-100, composite of LSTM/sentiment/technical)
- **Signal**: Trading recommendation (BUY/SELL/HOLD)
- **Confidence**: Model confidence in prediction (%)
- **Sector**: ASX sector classification

---

## 4. Latest Report

**Data Source**: Latest file in `reports/html/*.html`

### Real Example:
```
📄 Latest Report
Date: 2025-11-15
File: 2025-11-15_market_report.html
Size: 124 KB
Modified: Nov 15, 2025 7:30 AM

[📄 View Report]
```

**What You See**:
- Report date (when pipeline ran)
- Filename of HTML report
- File size in KB/MB
- Last modified timestamp
- Button to open full report in new tab

**Full Report Contains**:
- Complete stock analysis (80-100 stocks)
- Event risk calendar (Basel III, earnings, dividends)
- Detailed opportunity analysis
- Charts and visualizations
- Event Risk Guard flags

---

## 5. Statistics Panel

**Data Source**: `{date}_pipeline_state.json` → `statistics` object

### Real Data Structure:
```json
{
  "statistics": {
    "total_stocks_scanned": 81,
    "top_opportunities_count": 15,
    "high_confidence_count": 23,
    "buy_signals": 18,
    "sell_signals": 12,
    "hold_signals": 51,
    "event_risk_stocks": 7,
    "skip_trading_count": 5
  }
}
```

### What You See:
```
📊 Statistics
Total Scanned: 81
Top Opportunities: 15
High Confidence: 23
BUY Signals: 18
SELL Signals: 12
HOLD Signals: 51
Event Risk Stocks: 7
Skip Trading: 5
```

**Metrics Explained**:
- **Total Scanned**: All stocks analyzed
- **Top Opportunities**: Stocks with score ≥ 65
- **High Confidence**: Predictions with confidence ≥ 70%
- **BUY Signals**: Positive predictions
- **SELL Signals**: Negative predictions  
- **HOLD Signals**: Neutral/wait predictions
- **Event Risk Stocks**: Stocks with upcoming events detected
- **Skip Trading**: Stocks flagged DO NOT TRADE (imminent events)

---

## 6. Market Sentiment

**Data Source**: `{date}_pipeline_state.json` → `market_sentiment` object

### Real Data Structure:
```json
{
  "market_sentiment": {
    "score": 72.5,
    "gap_prediction": 0.35,
    "direction": "UP",
    "recommendation": "BULLISH"
  }
}
```

### What You See:
```
📈 Market Sentiment
Score: 72.5/100
Gap Prediction: +0.35%
Direction: UP
Stance: BULLISH
```

**Values Explained**:
- **Score**: Overall market sentiment (0-100)
  - 0-30: Very Bearish
  - 30-45: Bearish
  - 45-55: Neutral
  - 55-70: Bullish
  - 70-100: Very Bullish
- **Gap Prediction**: Expected ASX200 overnight gap (%)
- **Direction**: UP / DOWN / FLAT
- **Stance**: BULLISH / BEARISH / NEUTRAL / CAUTIOUS

---

## 7. Trained LSTM Models

**Data Source**: Files in `models/lstm_models/*.keras`

### Real Example:
```
🧠 Trained Models (25 models)

[BHP.AX] [CBA.AX] [CSL.AX] [WES.AX] [FMG.AX]
[NAB.AX] [ANZ.AX] [WBC.AX] [RIO.AX] [MQG.AX]
[WOW.AX] [TLS.AX] [QAN.AX] [STO.AX] [ORG.AX]
[GMG.AX] [SCG.AX] [TCL.AX] [AMC.AX] [QBE.AX]
[COH.AX] [RMD.AX] [SHL.AX] [JBH.AX] [COL.AX]

[Refresh]
```

**What It Shows**:
- Grid of stock symbols with trained LSTM models
- Each badge = one trained model exists
- Click refresh to update after training
- Shows model coverage across portfolio

**Model Details** (from file metadata):
- File size (typically 500-800 KB per model)
- Last trained date
- Model performance metrics (in logs)

---

## 8. Recent Logs

**Data Source**: Last 100 lines of `logs/screening/overnight_pipeline.log`

### Real Example:
```
📋 Recent Logs

2025-11-15 07:30:15 - INFO - ============================================
2025-11-15 07:30:15 - INFO - OVERNIGHT STOCK SCREENING - STARTING
2025-11-15 07:30:15 - INFO - ============================================
2025-11-15 07:30:16 - INFO - Configuration loaded
2025-11-15 07:30:17 - INFO - PHASE 1: MARKET SENTIMENT
2025-11-15 07:30:22 - INFO - ✓ Market Sentiment Retrieved
2025-11-15 07:30:22 - INFO -   Sentiment Score: 72.5/100
2025-11-15 07:30:22 - INFO -   Gap Prediction: +0.35%
2025-11-15 07:30:23 - INFO - PHASE 2: STOCK SCANNING
2025-11-15 07:30:24 - INFO - Scanning 81 stocks across 10 sectors
2025-11-15 07:35:42 - INFO - ✓ Scanning complete: 81 stocks
2025-11-15 07:35:43 - INFO - PHASE 3: PREDICTIONS
2025-11-15 07:40:15 - INFO - ✓ Predictions complete
2025-11-15 07:40:16 - INFO - PHASE 4: SCORING
2025-11-15 07:42:35 - INFO - ✓ Scoring complete
2025-11-15 07:42:36 - INFO - PHASE 5: REPORT GENERATION
2025-11-15 07:43:12 - INFO - ✓ HTML report generated
2025-11-15 07:43:13 - INFO - PHASE 6: FINALIZATION
2025-11-15 07:43:15 - INFO - ✓ Pipeline finalized
2025-11-15 07:43:15 - INFO - PIPELINE COMPLETE
2025-11-15 07:43:15 - INFO - Total Time: 13.0 minutes

[Refresh]
```

**What It Shows**:
- Real-time pipeline execution logs
- Phase progress tracking
- Timestamps for each step
- Errors and warnings
- Performance metrics
- Success/failure indicators

---

## 9. Event Risk Flags (In Opportunities Table)

**Data Source**: Event Risk Guard detection in pipeline

### Real Example with Events:
| Symbol | Score | Signal | Confidence | Sector | Event Flag |
|--------|-------|--------|-----------|--------|------------|
| CBA.AX | 84.1 | ⚠️ SKIP | 85.7% | Financials | 📅 Basel III (2 days) |
| BHP.AX | 87.3 | BUY | 89.2% | Materials | - |
| NAB.AX | 76.5 | ⚠️ SKIP | 72.3% | Financials | 📊 Earnings (1 day) |
| CSL.AX | 71.2 | BUY | 68.9% | Healthcare | - |

**Event Types Detected**:
- 📅 **Basel III Reports**: Bank regulatory reports (high volatility)
- 📊 **Earnings Announcements**: Company earnings (price sensitive)
- 💰 **Dividend Payments**: Ex-dividend dates (price adjustments)
- 📢 **AGM/SGM**: Annual/special meetings (corporate actions)

**Event Windows**:
- **72 hours before event**: ⚠️ WARNING - Increased risk
- **24 hours before event**: 🚫 SKIP TRADING - Do not trade
- **Event day**: 🚫 SKIP TRADING - Do not trade
- **24 hours after event**: ⚠️ CAUTION - Wait for stabilization

---

## 10. CSV Export Files

**Data Source**: `reports/csv/*.csv` (generated by pipeline)

### Files Created:
```
reports/csv/
├── 2025-11-15_screening_results.csv      (Full analysis)
└── 2025-11-15_event_risk_summary.csv     (Event flags only)
```

### Full Results CSV Contains:
- Symbol, Name, Price, Sector
- Opportunity Score, Signal, Confidence
- LSTM Prediction, Sentiment Score
- Technical Indicators (RSI, MACD, etc.)
- Event Risk Flags
- Skip Trading boolean

### Event Risk Summary CSV Contains:
- Only stocks with upcoming events
- Event type, date, days until
- Risk level, recommended action
- Historical volatility around events

---

## When Data Updates

### Auto-Refresh (Every 30 seconds)
- System status cards
- Latest report info
- Top opportunities
- Pipeline summary

### Manual Refresh
- Models list (click Refresh button)
- Logs (click Refresh button)
- Reports list (click View All)

### After Pipeline Runs
- All data refreshes automatically
- New report appears
- Opportunities update
- Statistics recalculate
- New CSV files generated

---

## Sample Full Dashboard View

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Event Risk Guard                                         │
│ ASX Stock Screening & Risk Management System                │
│                                      [🔄 Refresh] [⚙️ Settings]│
└─────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 🟢 System    │ 📧 Email     │ 🤖 LSTM      │ 📈 SPI       │
│ Status       │ Notifications│ Training     │ Monitoring   │
│ Active       │ Enabled      │ Enabled      │ Enabled      │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌────────────────────────────────────────────────────────────┐
│ 📄 Latest Report                         [View All Reports] │
├────────────────────────────────────────────────────────────┤
│ Date: 2025-11-15                                           │
│ File: 2025-11-15_market_report.html                        │
│ Size: 124 KB                                               │
│ Modified: Nov 15, 2025 7:30 AM                             │
│ [📄 View Report]                                           │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ 🔄 Pipeline Summary                                        │
├────────────────────────────────────────────────────────────┤
│ Stocks Scanned: 81    │ SPI Sentiment: 72.5/100           │
│ Opportunities: 15     │ Market Bias: BULLISH              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ 🎯 Top 10 Opportunities                                    │
├────────────────────────────────────────────────────────────┤
│ Symbol │ Score │ Signal │ Confidence │ Sector             │
│ BHP.AX │ 87.3🟢│ BUY    │ 89.2%      │ Materials          │
│ CBA.AX │ 84.1🟢│ BUY    │ 85.7%      │ Financials         │
│ CSL.AX │ 76.5🟡│ HOLD   │ 72.3%      │ Healthcare         │
│ WES.AX │ 71.2🟡│ BUY    │ 68.9%      │ Consumer           │
│ FMG.AX │ 67.8🟡│ BUY    │ 65.4%      │ Materials          │
│ NAB.AX │ 58.3🔴│ SKIP   │ 61.2%      │ Financials (Event) │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────┬─────────────────────────────┐
│ 🧠 Trained Models (25)       │ 📋 Recent Logs              │
├──────────────────────────────┼─────────────────────────────┤
│ [BHP.AX] [CBA.AX] [CSL.AX]   │ 2025-11-15 07:30:15 - INFO  │
│ [WES.AX] [FMG.AX] [NAB.AX]   │ PIPELINE STARTING           │
│ [ANZ.AX] [WBC.AX] [RIO.AX]   │ ...                         │
│ [MQG.AX] [WOW.AX] ...        │ 07:43:15 - INFO             │
│                              │ PIPELINE COMPLETE            │
│ [Refresh]                    │ [Refresh]                    │
└──────────────────────────────┴─────────────────────────────┘
```

---

## Data Availability

### First Time (No Pipeline Run Yet)
```
System Status: Inactive
Latest Report: No reports available yet
Top Opportunities: No data available
Models: No trained models yet
```

### After First Pipeline Run
```
System Status: Active ✅
Latest Report: Available ✅
Top Opportunities: 10-15 stocks ✅
Models: Growing (train 1-20 per night) ✅
```

### Ongoing (Daily Operation)
```
New report every night (automatic)
Opportunities update daily
Models accumulate (retrain stale ones)
Logs show continuous operation
```

---

## Summary

**The dashboard shows REAL data from**:
1. Pipeline execution results (JSON files)
2. Configuration settings (JSON config)
3. Trained model files (.keras files)
4. Log files (text logs)
5. Generated reports (HTML files)

**NOT fake/demo data** - Everything is live from the actual system!

**Data updates**: Automatically every 30 seconds + manual refresh buttons

**Access**: http://localhost:5000 after running START_WEB_UI.bat
