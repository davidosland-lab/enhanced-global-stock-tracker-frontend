# v1.3.15.183 Quick Reference Guide

## 🎯 What Changed?

**Problem**: System was selling NVDA at +2.76% profit due to 5-day holding period expiry.

**Solution**: 
- ✅ Extended holding period: 5 days → **15 days**
- ✅ Widened trailing stop: 3% → **5%**
- ✅ **NEW**: Profit protection - won't exit positions above +5% profit on time/trailing stop

---

## 🚀 Key Features

### 1. Smart Exit Logic
```
IF profit >= 5% AND (trailing stop OR holding period):
    → HOLD position (extend time)
ELSE:
    → EXIT normally
```

### 2. Exit Rules Matrix

| Your Position | Old v181 | New v183 |
|--------------|----------|----------|
| +2% profit, Day 5 | EXIT | EXIT (below 5%) |
| +6% profit, Day 5 | EXIT | **HOLD → Day 20** |
| +8% profit, trailing stop hit | EXIT | **HOLD (extend)** |
| -3% loss | EXIT | Still EXIT |

### 3. Configuration Defaults
```json
{
  "holding_period_days": 15,      // Was: 5
  "stop_loss_percent": 5.0,       // Was: 3.0
  "min_profit_to_hold": 5.0,      // NEW
  "disable_time_exit_for_winners": true  // NEW
}
```

---

## 📊 Expected Results

| Metric | Before (v181) | After (v183) | Target |
|--------|---------------|--------------|--------|
| Win Rate | 28.6% | 60-70% | 75-85% |
| Avg Hold Time | 5 days | 10-15 days | 10-20 days |
| Winners Sold Early | High | Low | Minimal |
| Realized P/L | -$600 | Positive | +$5-10k |

---

## 🔧 Tuning Options

### Conservative
```json
"holding_period_days": 10,
"stop_loss_percent": 4.0,
"min_profit_to_hold": 3.0
```

### Balanced (Default)
```json
"holding_period_days": 15,
"stop_loss_percent": 5.0,
"min_profit_to_hold": 5.0
```

### Aggressive
```json
"holding_period_days": 20,
"stop_loss_percent": 7.0,
"min_profit_to_hold": 3.0
```

---

## 📝 Example: NVDA Trade

### Old Logic (v181)
```
Day 1: Buy @ $187.84
Day 2: $190 (+1.2%) → Trailing stop @ $184.30
Day 3: $195 (+3.8%) → Trailing stop @ $189.15
Day 4: $193 (+2.76%) → Trailing stop @ $187.21
Day 5: HOLDING PERIOD EXPIRED → SELL @ $193 ❌

Profit: +$5.16/share (+2.76%)
Issue: Sold during uptrend, missed $200+ move
```

### New Logic (v183)
```
Day 1: Buy @ $187.84
Day 2: $190 (+1.2%) → Trailing stop @ $180.50
Day 3: $195 (+3.8%) → Trailing stop @ $185.25
Day 4: $193 (+2.76%) → Check: Profit < 5% → Normal exit
Day 5: HOLDING PERIOD → Profit < 5% → SELL @ $193

BUT if price hit $197 (+4.9%):
Day 5: HOLDING PERIOD → Profit still < 5% → SELL

BUT if price hit $198 (+5.4%):
Day 5: HOLDING PERIOD → Profit ≥ 5% → EXTEND TO DAY 20 ✅
Day 10: $205 (+9.1%) → Still held
Day 15: $210 (+11.8%) → Still held  
Day 20: Evaluate again

Potential Profit: +$22/share (+11.8%) vs +$5.16 (+2.76%)
```

---

## ⚠️ Important Notes

### Stop Loss Still Active
```
Loss >= 5% → ALWAYS EXIT (no profit protection)
```

### Profit Threshold
```
Only positions with profit ≥ 5% get protection
Positions with 2-4% profit will still exit normally
```

### Auto-Extension
```
When holding period expires and profit ≥ 5%:
→ System automatically extends by another 15 days
→ No manual intervention needed
```

---

## 🎯 When to Use This Version

### ✅ Use v183 If:
- You're frustrated by selling winners early
- Your win rate is below 50%
- You want to "let winners run"
- You pick good stocks but exits hurt performance

### ❌ Don't Use v183 If:
- You need strict 5-day flips
- You prefer tight 3% stops
- Capital rotation speed is critical
- Your strategy is high-frequency

---

## 🔍 Monitoring Success

### Watch These Logs
```
✅ GOOD: "Holding period expired but profit 8.2% >= 5.0%, extending hold"
✅ GOOD: "Trailing stop hit but profit 6.5% >= 5.0%, holding"
❌ BAD: Still seeing frequent "TARGET_EXIT_5d" with profits < 5%
```

### Track These Metrics
```python
# After 30 trades with v183:
win_rate >= 60%          # Up from 28.6%
avg_profit_per_winner >= 8%   # Up from 2-3%
holding_period_avg >= 10 days  # Up from 5 days
```

---

## 🆘 Troubleshooting

### Problem: Still Exiting Winners Early
**Solution**: Lower `min_profit_to_hold` to 3.0%

### Problem: Holding Losers Too Long
**Solution**: Check if stop loss is working (should exit at -5%)

### Problem: Too Many Extended Positions
**Solution**: Increase `min_profit_to_hold` to 7.0%

---

## 📚 Further Reading

- Full changelog: `CHANGELOG_v183.md`
- Configuration guide: `docs/configuration.md`
- Exit logic details: `docs/exit_strategies.md`

---

**Quick Start**: Extract → Copy state → Run dashboard → Monitor for "extending hold" messages

**Questions?** Check logs for exit reasons and compare with this guide.
