# Factor View and Macro Betas - Technical Guide

## 🎯 Overview

**Version**: 1.1 with Factor View and Macro Betas  
**New Features**: Factor decomposition analysis and macro factor sensitivity  
**Date Added**: 2025-11-17

This version adds two powerful new analytical modules:
1. **Factor View Builder** - Decomposes opportunity scores into constituent factors
2. **Macro Beta Calculator** - Measures stock sensitivity to market factors

---

## 📊 What's New

### New Modules Added

```
models/screening/
├── factor_view.py          NEW - Factor decomposition and export
└── macro_beta.py           NEW - Macro factor beta calculation
```

### New Output Files Created

```
reports/factor_view/
├── YYYY-MM-DD_factor_view_stocks.csv           Per-stock factor breakdown
├── YYYY-MM-DD_factor_view_sector_summary.csv   Sector-level aggregates
└── YYYY-MM-DD_factor_view_summary.json         Overall statistics
```

---

## 🔬 Factor View Builder

### What It Does

**Purpose**: Breaks down each stock's opportunity score into individual contributing factors.

**Key Features**:
- Per-stock factor contributions
- Sector-level summaries
- Adjustment tracking (bonuses/penalties)
- Macro beta integration
- CSV + JSON exports

### Factors Tracked

#### Core Scoring Factors
1. **Prediction Confidence** (0-100)
   - How confident the model is in its prediction
   - Source: LSTM or baseline prediction

2. **Technical Strength** (0-100)
   - RSI, MACD, moving averages
   - Momentum indicators
   - Volume analysis

3. **SPI Alignment** (0-100)
   - Alignment with ASX200 SPI sentiment
   - Market direction concordance
   - Overnight gap prediction alignment

4. **Liquidity** (0-100)
   - Average daily volume
   - Bid-ask spread
   - Market depth

5. **Volatility** (0-100)
   - Price volatility (normalized)
   - Risk assessment
   - Stability metrics

6. **Sector Momentum** (0-100)
   - Sector performance
   - Relative sector strength
   - Peer comparison

#### Adjustments
1. **Total Adjustment** (-100 to +100)
   - Sum of all bonuses and penalties
   - Event risk adjustments
   - Special situation modifiers

2. **Penalty Count**
   - Number of negative adjustments applied
   - Examples: Basel III concerns, earnings misses

3. **Bonus Count**
   - Number of positive adjustments applied
   - Examples: Strong earnings, dividend increases

#### Macro Betas (NEW)
1. **Beta XJO** (ASX 200)
   - Sensitivity to overall Australian market
   - Calculated via OLS regression
   - 90-day lookback period

2. **Beta Lithium**
   - Sensitivity to lithium sector (LIT.AX proxy)
   - Materials/mining sector exposure
   - Commodity sensitivity

---

## 📈 Macro Beta Calculator

### What It Does

**Purpose**: Computes each stock's beta (sensitivity) to macro factors using OLS regression on daily returns.

**Method**: 
```
Beta = Covariance(Stock Returns, Factor Returns) / Variance(Factor Returns)
```

### Configuration

```python
MacroBetaCalculator(
    lookback_days=90,     # Data window (default: 90 days)
    min_obs=40,           # Minimum observations required
    factors=[             # Macro factors to calculate
        FactorDefinition(name="xjo", symbol="^AXJO"),       # ASX 200
        FactorDefinition(name="lithium", symbol="LIT.AX")   # Lithium proxy
    ]
)
```

### Interpretation

#### Beta XJO (ASX 200)
- **Beta > 1.0**: More volatile than market (amplifies moves)
- **Beta = 1.0**: Moves with market
- **Beta < 1.0**: Less volatile than market (defensive)
- **Beta < 0**: Inverse relationship (rare)

**Examples**:
- **CBA.AX** (Beta XJO = 0.85): Defensive bank stock
- **FMG.AX** (Beta XJO = 1.25): Cyclical mining stock
- **TLS.AX** (Beta XJO = 0.65): Defensive telecom

#### Beta Lithium
- **High (> 1.0)**: Strong lithium/commodity exposure
- **Moderate (0.5-1.0)**: Some commodity sensitivity
- **Low (< 0.5)**: Little lithium exposure
- **Negative**: Inverse relationship (hedging)

**Examples**:
- **PLS.AX** (Beta Lithium = 1.8): Direct lithium producer
- **BHP.AX** (Beta Lithium = 0.6): Diversified miner
- **WES.AX** (Beta Lithium = 0.1): Retail (no exposure)

---

## 📂 Output Files Explained

### 1. Stock-Level Factor View CSV

**File**: `reports/factor_view/YYYY-MM-DD_factor_view_stocks.csv`

**Columns**:
```csv
symbol,name,sector,price,opportunity_score,
prediction_confidence,technical_strength,spi_alignment,
liquidity,volatility,sector_momentum,base_total,
total_adjustment,penalty_count,bonus_count,
beta_xjo,beta_lithium,prediction,confidence_pct
```

**Example Row**:
```csv
CBA.AX,Commonwealth Bank,Financials,105.23,87.3,
89.2,85.4,72.5,
95.0,68.3,78.9,82.1,
+5.2,0,2,
0.85,0.12,BUY,89.2
```

**Use Cases**:
- Detailed per-stock analysis
- Factor contribution comparison
- Excel pivot tables
- Data science notebooks
- Custom visualizations

---

### 2. Sector Summary CSV

**File**: `reports/factor_view/YYYY-MM-DD_factor_view_sector_summary.csv`

**Columns**:
```csv
sector,avg_opportunity_score,avg_beta_xjo,avg_beta_lithium
```

**Example**:
```csv
sector,avg_opportunity_score,avg_beta_xjo,avg_beta_lithium
Materials,82.5,1.15,0.85
Financials,78.3,0.82,0.08
Healthcare,75.1,0.68,0.02
Consumer Discretionary,71.8,0.95,0.15
```

**Use Cases**:
- Sector rotation analysis
- Macro exposure assessment
- Portfolio diversification
- Risk management

---

### 3. Summary JSON

**File**: `reports/factor_view/YYYY-MM-DD_factor_view_summary.json`

**Structure**:
```json
{
  "sector_avg_opportunity": {
    "Materials": 82.5,
    "Financials": 78.3,
    "Healthcare": 75.1
  },
  "beta_xjo_by_sector": {
    "Materials": 1.15,
    "Financials": 0.82,
    "Healthcare": 0.68
  },
  "beta_lithium_by_sector": {
    "Materials": 0.85,
    "Financials": 0.08,
    "Healthcare": 0.02
  },
  "overall": {
    "count": 81,
    "avg_opportunity_score": 75.2,
    "avg_beta_xjo": 0.92,
    "avg_beta_lithium": 0.35
  }
}
```

**Use Cases**:
- Dashboard integration
- Web API consumption
- Automated reporting
- Data pipelines

---

## 🔄 Integration with Pipeline

### How It Works

The overnight pipeline now includes these steps:

```python
# 1. Scan stocks (existing)
stocks = scanner.scan_stocks()

# 2. Calculate macro betas (NEW)
beta_map = macro_beta_calc.compute_betas(symbols)

# 3. Add betas to stock data (NEW)
for stock in stocks:
    stock['macro_betas'] = beta_map.get(stock['symbol'], {})

# 4. Generate predictions (existing)
predictions = predictor.predict(stocks)

# 5. Calculate opportunity scores (existing)
scored_stocks = scorer.score_opportunities(predictions)

# 6. Build factor view (NEW)
factor_view = factor_builder.build_factor_view(scored_stocks)

# 7. Save factor view outputs (NEW)
factor_paths = factor_builder.save_factor_view(factor_view)

# 8. Generate standard reports (existing)
report = reporter.generate_report(scored_stocks)
```

---

## 📊 Use Cases

### 1. Factor Attribution Analysis

**Question**: "Why did Stock X get a high/low score?"

**Answer**: Look at factor_view_stocks.csv:
```csv
CBA.AX: opportunity_score=87.3
├─ prediction_confidence: 89.2 ✅ (very high)
├─ technical_strength: 85.4 ✅ (strong)
├─ spi_alignment: 72.5 ✓ (good)
├─ liquidity: 95.0 ✅ (excellent)
├─ volatility: 68.3 ✓ (moderate)
├─ sector_momentum: 78.9 ✓ (good)
└─ total_adjustment: +5.2 (2 bonuses, 0 penalties)
```

---

### 2. Sector Rotation Strategy

**Question**: "Which sectors have best risk/reward?"

**Answer**: Look at factor_view_sector_summary.csv:
```csv
Materials: score=82.5, beta_xjo=1.15 → High return, high risk
Financials: score=78.3, beta_xjo=0.82 → Good return, lower risk ✅
Healthcare: score=75.1, beta_xjo=0.68 → Moderate return, defensive
```

**Action**: Overweight Financials (good scores, moderate beta)

---

### 3. Portfolio Beta Management

**Question**: "What's my portfolio's market exposure?"

**Answer**: Calculate weighted average beta:
```python
portfolio_beta_xjo = sum(weight[i] * beta_xjo[i] for i in stocks)

Example:
50% CBA.AX (beta 0.85) + 50% BHP.AX (beta 1.20)
= 0.50 * 0.85 + 0.50 * 1.20
= 1.025 (slightly above market)
```

---

### 4. Commodity Exposure Analysis

**Question**: "Which stocks are exposed to lithium prices?"

**Answer**: Sort by beta_lithium in factor_view_stocks.csv:
```csv
PLS.AX: beta_lithium=1.8 ✅ (direct exposure)
LTR.AX: beta_lithium=1.6 ✅ (direct exposure)
MIN.AX: beta_lithium=1.2 ✅ (significant exposure)
BHP.AX: beta_lithium=0.6 ✓ (some exposure)
CBA.AX: beta_lithium=0.1 ❌ (minimal exposure)
```

---

### 5. Risk-Adjusted Returns

**Question**: "Which stocks offer best reward per unit risk?"

**Answer**: Calculate Sharpe-like ratio:
```python
risk_adjusted_score = opportunity_score / (beta_xjo * volatility)

Example:
Stock A: score=85, beta=1.2, vol=75 → 85/(1.2*75) = 0.94
Stock B: score=80, beta=0.8, vol=60 → 80/(0.8*60) = 1.67 ✅ Better!
```

---

## 🔧 Configuration Options

### Customize Macro Factors

Edit `models/screening/overnight_pipeline.py`:

```python
# Add more factors
self.macro_beta_calc = MacroBetaCalculator(
    lookback_days=90,
    min_obs=40,
    factors=[
        FactorDefinition(name="xjo", symbol="^AXJO"),      # ASX 200
        FactorDefinition(name="lithium", symbol="LIT.AX"), # Lithium
        FactorDefinition(name="gold", symbol="GLD"),       # Gold ← NEW
        FactorDefinition(name="oil", symbol="CL=F"),       # Crude Oil ← NEW
        FactorDefinition(name="usd_aud", symbol="AUDUSD=X") # FX ← NEW
    ]
)
```

### Adjust Lookback Period

```python
# Shorter window (more responsive, less stable)
self.macro_beta_calc = MacroBetaCalculator(lookback_days=30, min_obs=20)

# Longer window (more stable, less responsive)
self.macro_beta_calc = MacroBetaCalculator(lookback_days=180, min_obs=80)
```

---

## 📈 Performance Impact

### Execution Time

**Macro Beta Calculation**:
- ~5-10 seconds for 80-100 stocks
- Downloads 90 days of price data
- Computes OLS regressions

**Factor View Building**:
- ~1-2 seconds
- In-memory processing
- Fast CSV/JSON writes

**Total Pipeline Impact**: +10-15 seconds (negligible)

### Data Storage

**Additional Files Created**:
- 3 files per day (stocks CSV, sector CSV, summary JSON)
- ~100-200 KB per day
- ~3-6 MB per month

---

## 🔍 Troubleshooting

### Issue: Beta calculations return empty

**Cause**: Insufficient price data for some stocks

**Solution**:
1. Check min_obs setting (lower if needed)
2. Verify symbols are valid (Yahoo Finance)
3. Check internet connection
4. Review logs for yfinance errors

```python
# Lower minimum observations threshold
self.macro_beta_calc = MacroBetaCalculator(min_obs=20)  # Default: 40
```

---

### Issue: Factor view files not created

**Cause**: reports/factor_view/ directory missing

**Solution**: Directory is auto-created, but verify:
```python
from pathlib import Path
Path("reports/factor_view").mkdir(parents=True, exist_ok=True)
```

---

### Issue: Some stocks missing betas

**Normal**: Not all stocks have sufficient data

**Check**:
- Stock must have 40+ days of data (default)
- Factor (^AXJO) must have data for same period
- Sufficient overlap between stock and factor returns

---

## 📊 Example Analysis Workflow

### 1. Run Pipeline
```batch
RUN_OVERNIGHT_PIPELINE.bat
```

### 2. Load Factor View in Excel/Python

**Excel**:
```
1. Open: reports\factor_view\2025-11-17_factor_view_stocks.csv
2. Create pivot table
3. Analyze by sector, beta ranges, score ranges
```

**Python**:
```python
import pandas as pd

# Load data
stocks = pd.read_csv('reports/factor_view/2025-11-17_factor_view_stocks.csv')
sectors = pd.read_csv('reports/factor_view/2025-11-17_factor_view_sector_summary.csv')

# Find high beta materials stocks
high_beta_materials = stocks[
    (stocks['sector'] == 'Materials') & 
    (stocks['beta_xjo'] > 1.2) &
    (stocks['opportunity_score'] > 80)
]

# Calculate portfolio metrics
portfolio_beta = stocks['beta_xjo'].mean()
portfolio_lithium_exposure = stocks['beta_lithium'].mean()
```

---

## 🎯 Best Practices

### 1. Monitor Beta Stability
- Track betas over time (compare daily files)
- Watch for sudden changes (might indicate data issues)
- Use longer lookback for more stable estimates

### 2. Combine with Other Factors
- Don't use betas in isolation
- Consider opportunity score, sector, fundamentals
- Use betas for portfolio construction, not stock picking

### 3. Understand Limitations
- Betas are historical (past ≠ future)
- Based on correlations (not causation)
- Can change during market regime shifts

### 4. Regular Review
- Check factor contributions weekly
- Monitor sector rotations
- Adjust portfolio based on changing betas

---

## 📚 Further Reading

### Academic References
- **Beta Calculation**: Sharpe, W. (1964). "Capital Asset Prices"
- **Factor Models**: Fama & French (1992). "The Cross-Section of Expected Stock Returns"
- **OLS Regression**: Standard econometric textbooks

### Related Documentation
- `docs/DASHBOARD_DATA_GUIDE.md` - Dashboard data structure
- `README.md` - System overview
- `models/screening/opportunity_scorer.py` - Scoring methodology

---

## ✅ Summary

**New Features**:
- ✅ Factor-level score decomposition
- ✅ Macro beta calculations (XJO, Lithium)
- ✅ Sector-level aggregations
- ✅ Enhanced CSV/JSON exports
- ✅ Portfolio analysis capabilities

**Benefits**:
- 🎯 Understand why stocks scored high/low
- 📊 Better portfolio construction
- 🔍 Risk management insights
- 📈 Factor attribution analysis
- 💡 Sector rotation strategies

**Impact**:
- ⚡ Minimal performance overhead (~10-15 seconds)
- 💾 Small storage footprint (~3-6 MB/month)
- 🔧 Fully integrated with existing pipeline
- 📱 Ready for dashboard/notebook consumption

---

**Version**: 1.1 with Factor View and Macro Betas  
**Date**: 2025-11-17  
**Status**: Production Ready ✅
