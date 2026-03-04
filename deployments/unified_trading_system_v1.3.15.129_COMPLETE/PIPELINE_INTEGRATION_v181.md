# Pipeline Integration Feature - v1.3.15.181

**Date**: 2026-02-24  
**Version**: v1.3.15.181  
**Status**: Ready for deployment

---

## Overview

The system now automatically monitors for updated pipeline reports and acts on the top 5 recommendations from each market without requiring manual intervention or dashboard restart.

---

## What's New

### Automatic Pipeline Report Detection
- Checks for updated reports every 30 minutes
- Compares file modification times vs cached timestamps
- Automatically reloads when new pipeline runs are detected
- Works for AU, UK, and US markets

### Top Recommendations Processing
- Extracts top 5 stocks from each market report
- Evaluates them against trading signal parameters
- Executes trades automatically for qualified recommendations
- Prevents duplicate trades using timestamp-based tracking

### Integration with Existing System
- Works alongside live ML signal generation
- Respects max position limits
- Uses same risk management rules
- Logs all pipeline-driven actions clearly

---

## How It Works

### 1. Detection Phase (Every 30 Minutes)
```
[PIPELINE] Checking for updated reports...
[PIPELINE] Detected updated AU morning report
[PIPELINE] Reloading morning reports...
[OK] Loaded AU morning report - 12 opportunities, sentiment 65.3, age 0.2h
```

### 2. Extraction Phase
```
[PIPELINE] Processing fresh pipeline recommendations...
[PIPELINE] Found 15 recommendations across all markets
```

### 3. Evaluation Phase
Each recommendation is checked against:

**For BUY signals:**
- Opportunity score >= 60.0 (composite ranking)
- Sentiment >= 45.0 (not too bearish)
- Report age < 12 hours (fresh data)
- Confidence = (score × 70%) + (sentiment × 30%)

**For SELL signals:**
- Must have open position
- Score <= 40.0 (lower score = stronger sell)
- Confidence = ((100-score) × 70%) + ((100-sentiment) × 30%)

### 4. Execution Phase
```
[PIPELINE] Actionable: BHP.AX (AU) - BUY @ score=78.5, confidence=72.3%
[PIPELINE]   Reason: Pipeline BUY: score=78.5, sentiment=68.0
[PIPELINE] Executing BUY for BHP.AX at $45.23
[TRADE] ENTRY - BHP.AX: 100 shares @ $45.23, conf=72.3%
```

---

## Benefits

### For Your Workflow
1. **No Manual Steps**: Run pipelines 2 hours before market open, dashboard picks them up automatically
2. **Fresh Data**: Always uses the latest pipeline analysis
3. **Flexible Timing**: System adapts to any pipeline schedule
4. **No Restart Required**: Dashboard keeps running, picks up new reports seamlessly

### For Trading Performance
1. **Faster Execution**: Trades within 30 minutes of pipeline completion
2. **Quality Filtering**: Only acts on high-confidence recommendations
3. **Dual Signal Source**: Combines pipeline + live ML signals
4. **Risk Control**: Respects position limits and trading criteria

---

## Configuration

### Timing (Adjustable in Code)
```python
self._reports_check_interval = timedelta(minutes=30)  # Check every 30 minutes
```

### Recommendation Limits
```python
max_recommendations: int = 5  # Top 5 per market
```

### Trading Criteria (in _evaluate_pipeline_recommendation)
```python
# BUY thresholds
min_score = 60.0
min_sentiment = 45.0
max_report_age_hours = 12

# SELL thresholds
max_score = 40.0  # For sell signals
```

---

## Example Scenarios

### Scenario 1: Normal Pipeline Run
```
06:00 - Start dashboard
06:30 - First check (no new reports)
07:00 - Second check (no new reports)
07:30 - Run AU pipeline (creates fresh report)
08:00 - Third check (detects new AU report!)
        - Reloads reports
        - Finds 12 opportunities
        - Evaluates top 5
        - Executes 2 BUY trades (score 78.5, 72.3)
08:30 - Fourth check (no changes)
```

### Scenario 2: Multiple Markets
```
06:00 - Run AU pipeline
07:00 - Run UK pipeline
08:00 - Dashboard checks
        - Detects both new reports
        - Processes top 5 from AU (15 total)
        - Processes top 5 from UK (15 total)
        - Evaluates all 30 recommendations
        - Executes 4 trades (respects max 3 positions, fills remaining slot)
```

### Scenario 3: Stale Reports
```
Morning: Run pipelines
Evening: Dashboard still running
Next day 08:00: Check detects no new reports
                Existing positions managed normally
                No new pipeline trades (reports > 12h old)
```

---

## Logging

### Success Logs
```
[PIPELINE] Detected updated US morning report
[PIPELINE] Reloading morning reports...
[OK] Loaded US morning report - 8 opportunities, sentiment 58.2, age 0.5h
[PIPELINE] Processing fresh pipeline recommendations...
[PIPELINE] Found 8 recommendations across all markets
[PIPELINE] Actionable: AAPL (US) - BUY @ score=68.5, confidence=65.2%
[PIPELINE] Executing BUY for AAPL at $175.50
[PIPELINE] Processed 1 actionable recommendations
```

### Filtering Logs
```
[PIPELINE] Not actionable: TSLA - Score too low: 55.0 < 60.0
[PIPELINE] Not actionable: GOOGL - Sentiment too bearish: 38.5 < 45.0
[PIPELINE] Not actionable: META - Report too old: 14.2h > 12h
[PIPELINE] Skipping MSFT - already have position
```

---

## Impact on Existing Features

### What Doesn't Change
- Live ML signal generation continues as normal
- Manual symbol scanning still works
- Entry timing logic unchanged
- Risk management rules unchanged
- Position management unchanged

### What's Enhanced
- More entry opportunities (pipeline + ML)
- Faster response to pipeline analysis
- Better utilization of overnight research
- Reduced manual monitoring required

---

## Testing Checklist

After installing v1.3.15.181:

- [ ] Start dashboard
- [ ] Wait 30 minutes, check logs for first pipeline check
- [ ] Run a pipeline (AU/UK/US)
- [ ] Wait up to 30 minutes for detection
- [ ] Verify logs show: "Detected updated X morning report"
- [ ] Verify logs show: "Processing fresh pipeline recommendations"
- [ ] Check if any recommendations were actionable
- [ ] Verify trades executed if criteria met
- [ ] Confirm processed recommendations not repeated

---

## Troubleshooting

### "No new recommendations to process"
- Normal if reports haven't changed
- Check report timestamps in logs
- Verify pipeline actually ran and created new reports

### "Not actionable" for all recommendations
- Check score/sentiment thresholds
- Verify report age < 12 hours
- May need to adjust criteria in code

### Reports not detected
- Check file paths: `reports/screening/{market}_morning_report.json`
- Verify file modification times updated
- Check 30-minute interval hasn't passed yet

### Duplicate trades
- Should not happen (uses recommendation_key tracking)
- If occurs, check _processed_recommendations set
- Report as bug

---

## Version History

| Version | Feature | Status |
|---------|---------|--------|
| v1.3.15.181 | Pipeline integration & top 5 processing | This version |
| v1.3.15.180 | Fixed sentiment dict structure bug | Deployed |
| v1.3.15.179 | Fixed numeric prediction handling | Deployed |
| v1.3.15.178 | String to numeric signal conversion | Deployed |
| v1.3.15.177 | Trading logic threshold fixes | Deployed |

---

## Files Modified

- `core/paper_trading_coordinator.py` (main changes)
  - Added: `_check_for_updated_reports()`
  - Added: `_get_pipeline_recommendations()`
  - Added: `_evaluate_pipeline_recommendation()`
  - Added: `_process_pipeline_recommendations()`
  - Modified: `__init__()` to track check times
  - Modified: `run_trading_cycle()` to integrate pipeline processing

---

## Next Steps

1. Download v1.3.15.181 package
2. Stop dashboard (Ctrl+C)
3. Replace old folder with v181
4. Restart dashboard
5. Run pipelines as normal (2 hours before market open)
6. Monitor logs for pipeline detection and processing
7. Review executed trades in portfolio

---

## Support

- GitHub PR: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/11
- Commit: `70adec1`
- Issues: Comment on PR or create new issue

---

**Bottom Line**: Run your pipelines whenever convenient (morning, evening, etc.). The dashboard will automatically detect them, reload the reports, evaluate the top recommendations, and execute qualifying trades - all without any manual intervention.
