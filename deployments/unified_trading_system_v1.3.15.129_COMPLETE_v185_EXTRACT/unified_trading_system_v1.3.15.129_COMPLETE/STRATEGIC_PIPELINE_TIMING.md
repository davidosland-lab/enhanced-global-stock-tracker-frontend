# Strategic Pipeline Timing Guide

**Version**: v1.3.15.102  
**Date**: 2026-02-08  
**Purpose**: Maximize trading opportunities by running pipelines at optimal times

---

## Executive Summary

**Problem**: Running all pipelines at once wastes processing time and doesn't align with global market opening times.

**Solution**: Run each pipeline strategically before its market opens to get fresh signals.

**Benefit**: 
- ✅ Maximum relevance of trading signals
- ✅ Better timing for entry decisions
- ✅ Reduced processing load (run one at a time)
- ✅ Aligned with actual trading opportunities

---

## Global Market Trading Hours

### 🇦🇺 Australia (ASX)
- **Market**: Australian Stock Exchange
- **Timezone**: Australia/Sydney (AEDT/AEST)
- **Trading Hours**: 10:00 AM - 4:00 PM AEDT
- **UTC Equivalent**: ~00:00 - 06:00 UTC (varies by season)
- **Stocks**: 240 ASX stocks (.AX suffix)

### 🇺🇸 United States (NYSE/NASDAQ)
- **Market**: New York Stock Exchange / NASDAQ
- **Timezone**: America/New_York (EST/EDT)
- **Trading Hours**: 9:30 AM - 4:00 PM EST
- **UTC Equivalent**: 14:30 - 21:00 UTC
- **Stocks**: 480 US stocks (no suffix)

### 🇬🇧 United Kingdom (LSE)
- **Market**: London Stock Exchange
- **Timezone**: Europe/London (GMT/BST)
- **Trading Hours**: 8:00 AM - 4:30 PM GMT
- **UTC Equivalent**: 08:00 - 16:30 UTC
- **Stocks**: 240 UK stocks (.L suffix)

---

## Optimal Pipeline Timing Strategy

### 🎯 Rule: Run Pipeline 30-60 Minutes BEFORE Market Opens

**Why?**
1. **Fresh Signals**: Analysis is most relevant just before market opens
2. **Overnight Information**: Captures overnight news and market movements
3. **Execution Time**: Allows time to review signals and prepare trades
4. **Market Relevance**: Signals decay quickly after market opens

---

## Recommended Schedule (UTC Time)

### Scenario 1: Trading All Three Markets

If you're trading across all three markets, use this sequence:

#### 23:00 UTC (Previous Day) - Run AU Pipeline
```
Time: 23:00 UTC / 10:00 AM AEDT (next day) / 6:00 PM EST / 11:00 PM GMT
Target: ASX opens at 00:00 UTC (10:00 AM AEDT)
Command: Option 5 (Run AU Pipeline Only)
Duration: ~20 minutes
Report: reports/au_morning_report.json
```

**What This Captures**:
- US market close impact on ASX overnight
- Commodity price movements (Gold, Iron Ore)
- Asian futures (Nikkei, Hang Seng)
- SPI 200 futures
- Overnight news from US/UK

#### 07:30 UTC - Run UK Pipeline
```
Time: 07:30 UTC / 6:30 PM AEDT / 2:30 AM EST / 7:30 AM GMT
Target: LSE opens at 08:00 UTC (8:00 AM GMT)
Command: Option 7 (Run UK Pipeline Only)
Duration: ~20 minutes
Report: reports/uk_morning_report.json
```

**What This Captures**:
- Asian session results
- European futures (DAX, CAC)
- FTSE futures
- Overnight news from Asia
- Pre-market UK sentiment

#### 14:00 UTC - Run US Pipeline
```
Time: 14:00 UTC / 1:00 AM AEDT (next day) / 9:00 AM EST / 2:00 PM GMT
Target: NYSE opens at 14:30 UTC (9:30 AM EST)
Command: Option 6 (Run US Pipeline Only)
Duration: ~20 minutes
Report: reports/us_morning_report.json
```

**What This Captures**:
- European morning session results
- UK market trends
- S&P 500 futures
- VIX (volatility)
- Pre-market US sentiment
- Economic data releases (typically 8:30 AM EST)

---

## Recommended Schedule (Local Time Examples)

### If You're In Australia (AEDT)
```
09:30 AM AEDT - Run AU Pipeline (before ASX opens at 10:00 AM)
06:30 PM AEDT - Run UK Pipeline (before LSE opens at 7:00 PM AEDT)
01:00 AM AEDT - Run US Pipeline (before NYSE opens at 1:30 AM AEDT)
```

### If You're In United States (EST)
```
06:00 PM EST  - Run AU Pipeline (before ASX opens at 7:00 PM EST)
02:30 AM EST  - Run UK Pipeline (before LSE opens at 3:00 AM EST)
09:00 AM EST  - Run US Pipeline (before NYSE opens at 9:30 AM EST)
```

### If You're In United Kingdom (GMT)
```
11:00 PM GMT  - Run AU Pipeline (before ASX opens at midnight GMT)
07:30 AM GMT  - Run UK Pipeline (before LSE opens at 8:00 AM GMT)
02:00 PM GMT  - Run US Pipeline (before NYSE opens at 2:30 PM GMT)
```

---

## Menu Options Explained

### START.bat Menu Structure

```
1. Start Complete System - FinBERT + Dashboard + Pipelines
2. Start FinBERT Only - Sentiment analysis server
3. Start Dashboard Only - Paper trading interface

--- Overnight Pipeline Options ---
4. Run All Pipelines (AU + US + UK) - ~60 minutes     ← All at once (not ideal)
5. Run AU Pipeline Only (ASX) - ~20 minutes           ← RECOMMENDED
6. Run US Pipeline Only (NYSE/NASDAQ) - ~20 minutes   ← RECOMMENDED
7. Run UK Pipeline Only (LSE) - ~20 minutes           ← RECOMMENDED

8. Exit
```

### When to Use Each Option

**Option 4 (All Pipelines)**:
- ❌ **NOT RECOMMENDED** for live trading
- ✅ Good for: Backtesting, testing, full system verification
- ⏱️ Takes 60 minutes
- 💡 Use only when timing doesn't matter

**Options 5, 6, 7 (Individual Pipelines)**:
- ✅ **RECOMMENDED** for live trading
- ✅ Strategic timing aligned with market opens
- ⏱️ Takes 20 minutes each
- 💡 Run just before each market opens

---

## Automation with Task Scheduler (Windows)

### Setup Automated Pipeline Runs

**1. Create Task for AU Pipeline**
```batch
Task Name: AU Pipeline Morning Run
Program: C:\path\to\unified_trading_dashboard\RUN_AU_PIPELINE_ONLY.bat
Trigger: Daily at 11:30 PM (for midnight UTC ASX open)
Settings: 
  - Run whether user is logged on or not
  - Wake computer to run
  - Stop task if runs longer than 1 hour
```

**2. Create Task for UK Pipeline**
```batch
Task Name: UK Pipeline Morning Run
Program: C:\path\to\unified_trading_dashboard\RUN_UK_PIPELINE_ONLY.bat
Trigger: Daily at 7:30 AM GMT
Settings:
  - Run whether user is logged on or not
  - Wake computer to run
  - Stop task if runs longer than 1 hour
```

**3. Create Task for US Pipeline**
```batch
Task Name: US Pipeline Morning Run
Program: C:\path\to\unified_trading_dashboard\RUN_US_PIPELINE_ONLY.bat
Trigger: Daily at 9:00 AM EST
Settings:
  - Run whether user is logged on or not
  - Wake computer to run
  - Stop task if runs longer than 1 hour
```

---

## Market-Hours Filter Integration

### How It Works Together

**Market-Hours Filter (v1.3.15.92)**:
- Monitors 720 stocks continuously (every 5 minutes)
- Only scans stocks when their market is OPEN
- Saves 30-70% processing time
- Purpose: Real-time opportunity detection

**Strategic Pipeline Timing (v1.3.15.102)**:
- Runs ONCE before each market opens
- Deep analysis with ML/FinBERT/LSTM
- Generates morning report with top opportunities
- Purpose: Pre-market preparation

### Combined Workflow

```
Before Market Opens:
  ↓
Run Pipeline (20 min)
  ├─ 240 stocks analyzed
  ├─ ML predictions generated
  ├─ Morning report created
  └─ Top opportunities identified
  ↓
Market Opens:
  ↓
Market-Hours Filter (continuous)
  ├─ Monitors opportunities every 5 min
  ├─ Only scans when market is open
  ├─ Real-time breakout detection
  └─ Updates continuously
  ↓
Market Closes:
  ↓
Filter pauses scanning
(Market-hours filter skips closed market)
```

---

## Quick Reference Card

### AU Pipeline (ASX)
- **When**: 30 min before 10:00 AM AEDT
- **Menu**: Option 5
- **Time**: ~20 minutes
- **Report**: reports/au_morning_report.json

### US Pipeline (NYSE/NASDAQ)
- **When**: 30 min before 9:30 AM EST
- **Menu**: Option 6
- **Time**: ~20 minutes
- **Report**: reports/us_morning_report.json

### UK Pipeline (LSE)
- **When**: 30 min before 8:00 AM GMT
- **Menu**: Option 7
- **Time**: ~20 minutes
- **Report**: reports/uk_morning_report.json

---

## Example: One Day Trading Workflow

**Scenario**: Trader in New York (EST) trading all three markets

```
6:00 PM EST (Previous Day)
  → Run AU Pipeline (Option 5)
  → Review reports/au_morning_report.json
  → Prepare orders for ASX open at 7:00 PM EST

2:30 AM EST
  → Run UK Pipeline (Option 7)
  → Review reports/uk_morning_report.json
  → Prepare orders for LSE open at 3:00 AM EST

9:00 AM EST
  → Run US Pipeline (Option 6)
  → Review reports/us_morning_report.json
  → Prepare orders for NYSE open at 9:30 AM EST

Throughout the day:
  → Market-hours filter monitors continuously
  → Only active stocks are scanned (automatic)
  → Real-time opportunities detected
```

---

## Benefits Summary

### Before (Option 4 - All Pipelines at Once)
```
❌ Run all pipelines at midnight (60 minutes)
❌ AU signals: 10 hours old by ASX open
❌ US signals: 14 hours old by NYSE open
❌ UK signals: 8 hours old by LSE open
❌ Stale information
❌ Poor timing
```

### After (Options 5, 6, 7 - Strategic Timing)
```
✅ Run each pipeline just before market opens (20 min each)
✅ AU signals: Fresh (30 min old)
✅ US signals: Fresh (30 min old)
✅ UK signals: Fresh (30 min old)
✅ Current information
✅ Optimal timing
✅ Better entry decisions
```

---

## FAQ

**Q: Can I still run all pipelines at once?**  
A: Yes, Option 4 still exists. Useful for testing or when timing doesn't matter.

**Q: What if I only trade one market?**  
A: Use the specific option (5, 6, or 7) for your market. Ignore the others.

**Q: Do I need to run pipelines every day?**  
A: Recommended for active trading. For less active trading, run as needed.

**Q: What about weekends?**  
A: Pipelines work with `--ignore-market-hours` flag, so they run anytime. But signals are less useful when markets are closed.

**Q: Can I run a pipeline while a market is open?**  
A: Yes, but signals are most valuable before market opens. During market hours, rely on the continuous market-hours filter.

**Q: How do I automate this?**  
A: Use Windows Task Scheduler (see Automation section above).

---

## Summary

**Strategic Timing = Better Trading**

- 🎯 Run pipelines BEFORE markets open (not after, not during)
- ⏰ Use Options 5, 6, 7 for individual markets
- 🌍 Align with global market timing
- 📊 Market-hours filter handles real-time monitoring
- ✅ Fresh signals = Better decisions

**Menu Structure**:
- Options 1-3: System components
- **Options 5-7: Strategic pipeline timing** ← USE THESE
- Option 4: All at once (testing only)

---

**Version**: v1.3.15.102  
**Status**: ✅ **PRODUCTION READY**  
**Recommendation**: Use individual pipeline options (5, 6, 7) for optimal trading
