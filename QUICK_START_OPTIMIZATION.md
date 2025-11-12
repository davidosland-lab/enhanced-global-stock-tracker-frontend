# Parameter Optimization - Quick Start Guide

## 🚀 5-Minute Test

### 1. Start Server
```bash
cd /home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED
python app_finbert_v4_dev.py
```

### 2. Open Browser
Navigate to: **http://localhost:5001**

### 3. Run Optimization
1. Click **"Optimize Parameters"** (amber button, top right)
2. Symbol: **AAPL**
3. Method: **Random Search** (default)
4. Dates: Leave defaults (last 2 years)
5. Click **"Start Optimization"**
6. Wait 2-3 minutes ☕
7. Review results
8. Click **"Apply Optimal Parameters"**
9. Run backtest with optimal settings

---

## 📊 What You'll See

### Progress
```
Optimization Progress
Testing configurations...
████████████████░░░░░░░░░░ 50%
This may take 2-5 minutes
```

### Results
```
🏆 Optimization Complete!

Best Parameters Found:
  Confidence Threshold:  0.65
  Lookback Days:         75
  Position Size:         15%
  Expected Return:       +12.45%

Summary Stats:
  Configurations Tested: 50
  Avg Train Return: 8.67%
  Avg Test Return: 6.89%
  Low Overfit Configs: 12
```

---

## 🎯 Expected Results (AAPL, 2-year period)

| Parameter | Typical Range | Optimal (example) |
|-----------|---------------|-------------------|
| Confidence | 0.50-0.80 | 0.65 |
| Lookback | 30-120 days | 75 days |
| Position Size | 5%-25% | 15% |
| Test Return | 8-15% | 12.45% |
| Overfit Score | <30% | 18.4% |

---

## ⚙️ Methods Comparison

| Method | Time | Iterations | Best For |
|--------|------|------------|----------|
| Random Search | 2-3 min | 50 | Quick exploration |
| Grid Search | 3-5 min | 60 | Thorough testing |

---

## 🛡️ Overfitting Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 🟢 0-20% | Excellent | Use confidently |
| 🟡 20-40% | Acceptable | Monitor performance |
| 🔴 40%+ | Warning | Consider different params |

**Formula**: `(train_return - test_return) / train_return × 100`

---

## 🔗 Quick Links

- **PR #7**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/7
- **Documentation**: `PARAMETER_OPTIMIZATION_COMPLETE.md`
- **UI Flow**: `OPTIMIZATION_UI_FLOW.md`
- **Implementation**: `PARAMETER_OPTIMIZATION_IMPLEMENTATION.md`

---

## 🐛 Troubleshooting

### Modal doesn't open
- Check browser console (F12)
- Verify JavaScript loaded
- Check for conflicting modals

### Optimization takes too long (>10 minutes)
- Check server logs for errors
- Verify Yahoo Finance API accessible
- Try shorter date range

### Results seem wrong
- Verify dates are correct
- Check symbol is valid
- Review server logs for warnings
- Compare with manual backtest

### "Apply Parameters" doesn't work
- Check backtest modal has parameter inputs
- Verify input IDs match JavaScript
- Check browser console for errors

---

## 💡 Pro Tips

1. **First Run**: Use Random Search on AAPL (2 years)
2. **Fine-Tuning**: Use Grid Search around promising params
3. **Multiple Stocks**: Run separately for each symbol
4. **Overfitting**: Prefer configs with <25% degradation
5. **Date Range**: Use at least 1 year for reliable results
6. **Validation**: Always run a full backtest with optimal params

---

## 📝 API Example

```python
import requests

response = requests.post('http://localhost:5001/api/backtest/optimize', json={
    'symbol': 'AAPL',
    'start_date': '2023-01-01',
    'end_date': '2024-11-01',
    'model_type': 'ensemble',
    'optimization_method': 'random',
    'max_iterations': 50
})

results = response.json()
print(f"Best confidence: {results['best_parameters']['confidence_threshold']}")
print(f"Test return: {results['summary']['best_test_return']:.2f}%")
```

---

## ✅ Testing Checklist

- [ ] Server starts without errors
- [ ] Button appears in header
- [ ] Modal opens on click
- [ ] Form validation works
- [ ] Progress indicator shows
- [ ] API call completes (2-5 min)
- [ ] Results display correctly
- [ ] Top 10 table populates
- [ ] Apply button works
- [ ] Parameters transfer to backtest
- [ ] Close modal works
- [ ] Click outside closes modal

---

## 🎓 Understanding the Results

### Train Return vs Test Return
- **Train**: Performance on 75% of historical data
- **Test**: Performance on remaining 25% (unseen)
- **Good**: Test return close to train return
- **Bad**: Test return much worse than train (overfitting)

### Why This Matters
Parameters optimized only on training data might memorize patterns specific to that period. Testing on unseen data ensures they generalize to new market conditions.

### Example Interpretation
```
Config #1:
  Train: 20%, Test: 5%, Overfit: 75%
  ❌ Too specific to training period

Config #2:
  Train: 12%, Test: 10%, Overfit: 16.7%
  ✅ Good generalization
```

---

## 🚀 Next Steps After Testing

1. **Validate**: Run full backtest with optimal parameters
2. **Compare**: Test on different stocks
3. **Document**: Record optimal parameters for each symbol
4. **Monitor**: Track performance on live data
5. **Iterate**: Re-optimize periodically as market conditions change

---

**Implementation Status**: ✅ Complete  
**Version**: 1.0  
**Date**: November 1, 2025  
**Testing**: Ready
