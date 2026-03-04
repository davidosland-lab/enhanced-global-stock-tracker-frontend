# Backtest vs Paper Trading - Decision Making Comparison

**Date**: February 28, 2026  
**System**: Unified Trading System v1.3.15.191.1

---

## ❌ CRITICAL ISSUE IDENTIFIED

**The backtest module and paper trading module use DIFFERENT decision-making methods.**

---

## Decision Making Comparison

### Paper Trading / Dashboard Module

**Uses 5-Component ML System** (FinBERT + LSTM + Technical + Momentum + Volume):

1. **FinBERT Sentiment** (40% weight overnight, 25% intraday)
   - Real sentiment analysis from news
   - Integrated from FinBERT v4.4.4
   - Analyzes actual market sentiment

2. **LSTM Predictions** (25% weight)
   - Trained neural network model
   - Price pattern recognition
   - Trend forecasting

3. **Technical Indicators** (weight varies)
   - RSI, MACD, Bollinger Bands
   - Moving averages
   - Volume analysis

4. **Momentum Signals** (weight varies)
   - Rate of change
   - Trend strength
   - Acceleration

5. **Volume Analysis**
   - Volume patterns
   - Institutional activity

**Configuration**:
```python
sentiment_weight=0.25,  # FinBERT
lstm_weight=0.25,       # LSTM
# Plus technical, momentum, volume
```

**Target**: 70-75% win rate  
**Confidence Threshold**: 48% (v190 fix) or 52% default

---

### Backtest Module (Current)

**Uses 3-Component Technical System** (LSTM-like + Technical + Momentum):

1. **LSTM-like Logic** (40% weight)
   - NOT a trained LSTM model
   - Pattern matching using moving averages
   - Trend continuation heuristics
   - **No actual neural network**

2. **Technical Indicators** (35% weight)
   - RSI, MACD, Bollinger Bands
   - Moving averages (same as paper trading)

3. **Momentum Signals** (25% weight)
   - Rate of change
   - Trend strength (same as paper trading)

**Configuration**:
```python
lstm_weight = 0.40      # But NOT real LSTM
technical_weight = 0.35
momentum_weight = 0.25
```

**Missing Components**:
- ❌ **No FinBERT sentiment** (most important in paper trading)
- ❌ **No trained LSTM** (uses approximation)
- ❌ **No volume analysis**

**Confidence Threshold**: 0.60 (60%) default, can be set to 0.48

---

## Key Differences

| Component | Paper Trading | Backtest Module |
|-----------|--------------|-----------------|
| **FinBERT Sentiment** | ✅ Yes (25-40% weight) | ❌ No |
| **LSTM Model** | ✅ Trained neural network | ❌ Pattern matching approximation |
| **Technical Indicators** | ✅ Yes | ✅ Yes (same) |
| **Momentum Signals** | ✅ Yes | ✅ Yes (same) |
| **Volume Analysis** | ✅ Yes | ❌ No |
| **Target Win Rate** | 70-75% | Unknown (different system) |
| **Default Confidence** | 48-52% | 60% |

---

## Impact on Results

### Problem
The backtest module will produce **different signals** than paper trading because:

1. **Missing FinBERT sentiment** (25-40% of decision weight in live system)
2. **LSTM approximation** instead of trained model
3. **No volume analysis**

### Consequence
**Backtest results will NOT accurately predict paper trading performance.**

If backtest shows:
- 55% win rate → Paper trading might show 70% (with FinBERT)
- 45% win rate → Paper trading might show 60%
- Different trades selected entirely

---

## Visualization Capabilities

### Paper Trading / Dashboard

**Has Real-Time Visualizations**:
- ✅ Live dashboard with Plotly/Dash
- ✅ Portfolio performance charts
- ✅ Equity curve
- ✅ P&L tracking
- ✅ Position monitoring
- ✅ Real-time updates

### Backtest Module (Current)

**No Built-In Visualizations**:
- ❌ No charts generated
- ❌ No graphs
- ❌ No visual performance tracking
- ✅ Outputs CSV and JSON only

**What It Provides**:
- CSV files with predictions
- JSON files with metrics
- Text log output
- No visual charts

---

## What Needs to Be Done

### Option 1: Accept Different Decisions ⚠️

**Use backtest as-is** but understand:
- Results are **indicative only**
- Not exact replica of paper trading
- Different signals = different trades
- Can't directly compare

**Good for**: General strategy validation, rough performance estimate

---

### Option 2: Align Backtest with Paper Trading ⭐ (Recommended)

**Modify backtest module to match paper trading**:

1. **Add FinBERT Sentiment**
   - Integrate `core/sentiment_integration.py`
   - Apply 25-40% weight
   - Analyze historical news (if available)

2. **Use Real LSTM Model**
   - Load trained LSTM from `ml_pipeline/`
   - Replace LSTM-like approximation
   - Apply 25% weight

3. **Add Volume Analysis**
   - Import volume analysis logic
   - Integrate into ensemble

4. **Match Confidence Threshold**
   - Default to 0.48 (matches v190 fix)
   - Align with paper trading config

5. **Add Visualizations**
   - Generate equity curve charts
   - Create P&L graphs
   - Show entry/exit points
   - Monthly performance heatmap

**Result**: Backtest accurately replicates paper trading decisions

**Time**: 2-3 hours integration work

---

### Option 3: Quick Visualization Add-On

**Add charts to existing backtest** (without changing decision logic):

Create `core/backtest_visualizer.py`:
- Equity curve chart
- P&L timeline
- Trade distribution
- Win/loss analysis
- Monthly returns heatmap
- Drawdown chart

**Result**: Visual analysis of backtest results (but still different decisions)

**Time**: 30-60 minutes

---

## Recommendation

### Immediate Action (Option 3)
Add visualization to see backtest results graphically:
- Create `backtest_visualizer.py`
- Generate charts from CSV/JSON outputs
- Understand current backtest performance

### Follow-Up Action (Option 2)
Align backtest with paper trading:
- Integrate FinBERT sentiment
- Use real LSTM model
- Add volume analysis
- Match exact configuration

### Final Validation
Once aligned:
- Run 1-year backtest
- Compare to paper trading results
- Validate win rate matches (70-75%)
- Deploy with confidence

---

## Conclusion

**Current State**: 
- ❌ Backtest and paper trading use **different decision methods**
- ❌ No visualizations in backtest module
- ❌ Results will not match paper trading

**Needs**:
1. Visualization tools (30-60 min)
2. Decision-making alignment (2-3 hours)

**Once fixed**:
- ✅ Backtest accurately predicts paper trading
- ✅ Visual performance analysis
- ✅ Confident deployment decisions

---

## Next Steps

Choose one:

1. **Add visualizations now** (quick, see results graphically)
2. **Align decision-making** (accurate, matches paper trading)
3. **Do both** (comprehensive solution)

Let me know which path you prefer and I'll implement it immediately.

