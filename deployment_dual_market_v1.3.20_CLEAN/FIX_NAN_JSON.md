# Fix NaN JSON Error

## 🔴 Error

```
Swing backtest error: SyntaxError: Unexpected token 'N', 
..."returns": NaN... is not valid JSON
```

## ✅ Solution

The backend is returning `NaN` (Not a Number) in JSON responses, which is invalid. JavaScript can't parse it.

### Quick Fix (Download Latest Code)

**File to Update**: `C:\Users\david\AATelS\finbert_v4.4.4\models\backtesting\swing_trader_engine.py`

**Download Fixed Version**:
```
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/finbert_v4.4.4/models/backtesting/swing_trader_engine.py
```

**Steps**:
1. Download the file above
2. Replace your local file with it
3. Restart server
4. Test again

### OR Apply Patch Manually

Add this method to the `SwingTraderEngine` class (around line 854):

```python
def _clean_dict_for_json(self, data):
    """Replace NaN/Inf values with None for JSON serialization"""
    import math
    
    if isinstance(data, list):
        return [self._clean_dict_for_json(item) for item in data]
    elif isinstance(data, dict):
        return {k: self._clean_dict_for_json(v) for k, v in data.items()}
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
        return data
    else:
        return data
```

Then find line ~851 and change:
```python
# OLD
'trades': trades_df.to_dict('records'),
'equity_curve': equity_df.to_dict('records')

# NEW
'trades': self._clean_dict_for_json(trades_df.to_dict('records')),
'equity_curve': self._clean_dict_for_json(equity_df.to_dict('records'))
```

Also update lines 815-826 to handle NaN:

```python
# Line ~815 - Sharpe ratio
if len(equity_df) > 1 and equity_df['returns'].std() > 0:
    sharpe_ratio = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252)
    if np.isnan(sharpe_ratio) or np.isinf(sharpe_ratio):
        sharpe_ratio = 0.0
else:
    sharpe_ratio = 0.0

# Line ~820 - Max drawdown
max_drawdown = equity_df['drawdown'].min()
if np.isnan(max_drawdown):
    max_drawdown = 0.0

# Line ~826 - Sentiment correlation
if 'sentiment_score' in trades_df.columns and 'pnl_percent' in trades_df.columns:
    sentiment_corr = trades_df[['sentiment_score', 'pnl_percent']].corr().iloc[0, 1]
    if np.isnan(sentiment_corr):
        sentiment_corr = 0.0
else:
    sentiment_corr = 0.0

# Line ~850 - Avg days held
avg_days_held = trades_df['days_held'].mean()
if np.isnan(avg_days_held):
    avg_days_held = 0.0
```

## ✅ After Fix

Restart server and test. The error will be gone!

---

**Commit**: `3140865`  
**Status**: Fixed in latest code
