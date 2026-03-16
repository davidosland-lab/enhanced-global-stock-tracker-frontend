# 🚀 Quick Test Guide - 5-Day Swing Trading Backtest

## ⚡ 30-Second Start

### 1. Start Server
```bash
cd C:\Users\david\AATelS
python finbert_v4.4.4/app_finbert_v4_dev.py
```

### 2. Run First Test
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```

**Expected**: JSON response with backtest results showing total return, win rate, trades, etc.

---

## 📊 Compare Old vs New Backtest

### Old Backtest (Broken)
```bash
curl -X POST http://localhost:5001/api/backtest/run \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```
**Expected Result**: -0.86% return, 20-45% win rate

### NEW Swing Backtest
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```
**Expected Result**: +8-12% return, 55-65% win rate

---

## 🎯 Quick Tests

### Test 1: Default Settings
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```

### Test 2: Conservative (Tight Stop Loss)
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\", \"stop_loss_percent\": 2.0, \"confidence_threshold\": 0.70}"
```

### Test 3: Aggressive (Wide Stop Loss)
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"TSLA\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\", \"stop_loss_percent\": 5.0, \"confidence_threshold\": 0.60}"
```

### Test 4: No Sentiment (Pure Technical + LSTM)
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\", \"use_real_sentiment\": false}"
```

### Test 5: No LSTM (Sentiment + Technical)
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\", \"use_lstm\": false}"
```

---

## 📈 Test Different Stocks

### High-Volatility Tech
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"NVDA\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```

### Stable Blue-Chip
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"JNJ\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```

### Financial (Sentiment-Sensitive)
```bash
curl -X POST http://localhost:5001/api/backtest/swing \
  -H "Content-Type: application/json" \
  -d "{\"symbol\": \"JPM\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}"
```

---

## 🔍 What to Look For in Results

### Good Results
- **Total Return**: >8%
- **Win Rate**: >55%
- **Profit Factor**: >1.5
- **TARGET_EXIT**: >70% of trades
- **Sentiment Correlation**: >0.3 (if using sentiment)

### Bad Results
- **Total Return**: <0%
- **Win Rate**: <45%
- **Profit Factor**: <1.0
- **STOP_LOSS**: >50% of trades (stop too tight)
- **Sentiment Correlation**: <0.1 (sentiment not helping)

---

## 📝 Key Metrics Explained

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| **Total Return %** | Overall profit/loss | >8% |
| **Win Rate %** | % of profitable trades | >55% |
| **Profit Factor** | Gross profit / Gross loss | >1.5 |
| **Sharpe Ratio** | Risk-adjusted return | >1.0 |
| **Max Drawdown %** | Largest peak-to-trough decline | <-10% |
| **Avg Days Held** | Average holding period | ~5.0 |
| **Sentiment Correlation** | How well sentiment predicts profit | >0.3 |

---

## 🛠️ Troubleshooting

### Error: "Insufficient price data"
**Solution**: Use longer date range (need at least 60 trading days)
```bash
# BAD: Too short
"start_date": "2024-10-01", "end_date": "2024-11-01"

# GOOD: Long enough
"start_date": "2024-01-01", "end_date": "2024-11-01"
```

### Error: 500 Internal Server Error
**Solution**: Check server logs, ensure FinBERT v4.4.4 running

### Warning: "No news found"
**Solution**: Normal for small-cap stocks. Sentiment score will be 0.0 (neutral)

### Result: 0 trades executed
**Solution**: Lower confidence threshold
```bash
"confidence_threshold": 0.60  # Instead of 0.70
```

### Result: Too many stop losses (>50%)
**Solution**: Increase stop loss percent
```bash
"stop_loss_percent": 4.0  # Instead of 2.0
```

---

## 📚 Full Documentation

- **Complete Guide**: `SWING_TRADING_BACKTEST_COMPLETE.md`
- **Technical Docs**: `SWING_TRADING_MODULE_README.md`
- **Delivery Summary**: `SECOND_BACKTEST_DELIVERED.md`
- **GitHub**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/tree/finbert-v4.0-development

---

## 🎯 Quick Parameter Reference

### Defaults (Good for Most Stocks)
```json
{
  "holding_period_days": 5,
  "stop_loss_percent": 3.0,
  "confidence_threshold": 0.65,
  "max_position_size": 0.25,
  "use_real_sentiment": true,
  "use_lstm": true
}
```

### Conservative
```json
{
  "stop_loss_percent": 2.0,
  "confidence_threshold": 0.70,
  "max_position_size": 0.20
}
```

### Aggressive
```json
{
  "stop_loss_percent": 5.0,
  "confidence_threshold": 0.60,
  "max_position_size": 0.35
}
```

### Technical Only (No Sentiment/LSTM)
```json
{
  "use_real_sentiment": false,
  "use_lstm": false,
  "technical_weight": 0.50,
  "momentum_weight": 0.30,
  "volume_weight": 0.20
}
```

---

## ✅ Verification Checklist

After running your first test, verify:

- [ ] Server started successfully
- [ ] Backtest completed without errors
- [ ] Response shows `"backtest_type": "swing_trading"`
- [ ] Total trades > 0
- [ ] Equity curve data present
- [ ] Exit reasons breakdown included
- [ ] If `use_real_sentiment=true`, `news_articles_used` > 0
- [ ] If `use_lstm=true`, LSTM training logged in server console

---

**Created**: December 6, 2025  
**Version**: 1.0  
**Status**: ✅ Ready to Test
