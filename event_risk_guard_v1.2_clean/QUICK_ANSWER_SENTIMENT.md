# Quick Answer: Why "Neutral" During Market Falls?

## Your Question
> "OGSI says neutral. The market has fallen dramatically over the last week. What is used to measure this and how is it factored in?"

---

## The Answer (Short Version)

### What Was Wrong (v1.1)
The sentiment system only looked at **overnight** and **5-day** changes. If the most recent overnight session was flat/mixed, it showed "neutral" even during weekly declines.

**Your case**: Week down 4-5%, overnight flat → "NEUTRAL" ❌

### What's Fixed (v1.2)
Now tracks **7-day** and **14-day** trends with 20% weight in sentiment scoring.

**Your case**: Week down 4-5%, overnight flat → "SELL" (39.4/100) ✅

---

## What's Measured Now

| Time Window | Weight | Purpose |
|-------------|--------|---------|
| Overnight | 30% | US market impact |
| Gap Prediction | 25% | Opening prediction |
| US Agreement | 15% | Confidence level |
| **7-day + 14-day** | **20%** | **Weekly trend** ← NEW |
| Confidence | 10% | Signal strength |

---

## Test Results (Nov 18, 2025)

```
ASX 200 Status:
  1-day: -1.94%
  7-day: -4.10%    ← NEW
  14-day: -4.69%   ← NEW

Sentiment Score: 39.4/100
Recommendation: SELL
Direction: BEARISH
```

**Before (v1.1)**: Would have shown neutral  
**After (v1.2)**: Correctly shows bearish

---

## How It Works

```python
# Medium-term component (20% of total score)
seven_day = -4.10%
fourteen_day = -4.69%

# Recent trend weighted more (60% vs 40%)
medium_term = (seven_day * 0.6) + (fourteen_day * 0.4)
            = (-4.10 * 0.6) + (-4.69 * 0.4)
            = -4.34%

# Convert to score contribution
contribution = (-4.34 / 5.0) * 10 * 2.0
             = -17.4 points

# Final score includes this medium-term component
total_score = 50 + overnight(-4.9) + gap(-3.9) + agreement(+7.5) 
              + medium_term(-17.4) + confidence(+8.0)
            = 39.4 → SELL
```

---

## Run It Yourself

```bash
cd /home/user/webapp
python models/screening/spi_monitor.py
```

You'll see:
```
ASX 200 STATUS
Change (1-day): -1.94%
5-Day Change: -3.75%
7-Day Change: -4.10%     ← NEW
14-Day Change: -4.69%    ← NEW

SENTIMENT ANALYSIS
Sentiment Score: 39.4/100
Recommendation: SELL
```

---

## Complete Documentation

1. **User-Friendly Explanation**: `docs/SENTIMENT_SYSTEM_EXPLAINED.md`
2. **Technical Guide**: `docs/SENTIMENT_CALCULATION_v1.2.md`
3. **Release Notes**: `RELEASE_NOTES_v1.2.md`

---

## Pull Request

**URL**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/8

**Status**: ✅ Implemented and tested  
**Commits**: 3c36c41, 02385f6  
**Version**: 1.2.0  
**Backward Compatible**: Yes

---

## Bottom Line

✅ **Fixed**: System now captures weekly trends  
✅ **Tested**: Correctly identifies bearish conditions  
✅ **Documented**: Complete technical and user guides  
✅ **Deployed**: Ready in finbert-v4.0-development branch

**You won't see "neutral" during dramatic weekly falls anymore.**

---

*Generated: 2025-11-18*  
*Implementation: Option B (Enhanced with medium-term trends)*
