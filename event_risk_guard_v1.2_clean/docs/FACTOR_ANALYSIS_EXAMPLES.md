# Factor Analysis Examples - Event Risk Guard v1.1

## 📊 Practical Usage Guide

This document provides **real-world examples** of how to analyze factor view outputs using Excel and Python.

---

## 📁 File Locations

After running `RUN_OVERNIGHT_PIPELINE.bat`, find factor analysis files in:

```
reports/factor_view/
├── 2025-11-17_factor_view_stocks.csv           ← Per-stock factor breakdown
├── 2025-11-17_factor_view_sector_summary.csv   ← Sector aggregations
└── 2025-11-17_factor_view_summary.json         ← Portfolio statistics
```

---

## 🔷 Excel Examples

### Example 1: Build Defensive Portfolio

**Goal**: Find stocks with low market sensitivity and high stability

**Steps**:
1. Open `factor_view_stocks.csv` in Excel
2. **Data → Filter** (enable filtering on all columns)
3. Apply filters:
   - `beta_xjo` < 0.8 (defensive stocks)
   - `volatility` > 70 (stable prices)
   - `liquidity` > 80 (easy to trade)
   - `opportunity_score` > 75 (still attractive)
4. Sort by `opportunity_score` (descending)
5. Select top 10 stocks

**Expected Result**:
```
Symbol    Name              Beta XJO  Volatility  Opp Score
CSL.AX    CSL Limited       0.68      82.5        85.3
WOW.AX    Woolworths        0.72      78.3        81.2
TLS.AX    Telstra           0.65      75.8        79.5
...
```

**Interpretation**: Low-beta stocks that won't amplify market downturns

---

### Example 2: Identify Lithium Plays

**Goal**: Find stocks with high commodity exposure

**Steps**:
1. Open `factor_view_stocks.csv` in Excel
2. Enable filters
3. Apply filters:
   - `beta_lithium` > 0.5 (high commodity exposure)
   - `sector` = "Materials" (filter to materials)
   - `opportunity_score` > 75 (good opportunities)
4. Sort by `beta_lithium` (descending)

**Expected Result**:
```
Symbol    Name          Beta Lithium  Opp Score  Sector
PLS.AX    Pilbara Mins  0.92         82.5       Materials
MIN.AX    Mineral Res   0.78         79.3       Materials
LTR.AX    Liontown      0.85         81.7       Materials
...
```

**Interpretation**: Pure plays on lithium price movements

---

### Example 3: Pivot Table - Sector Analysis

**Goal**: Compare sectors by average scores and betas

**Steps**:
1. Open `factor_view_stocks.csv` in Excel
2. **Insert → PivotTable**
3. **Rows**: `sector`
4. **Values**:
   - Average of `opportunity_score`
   - Average of `beta_xjo`
   - Average of `beta_lithium`
   - Count of `symbol` (renamed to "Stock Count")
5. Sort by `Average of opportunity_score` (descending)

**Expected Result**:
```
Sector          Avg Opp Score  Avg Beta XJO  Avg Beta Lithium  Stock Count
Financials      82.3          0.92          0.08              15
Healthcare      80.1          0.68          0.02              8
Materials       78.5          1.15          0.85              12
...
```

**Interpretation**: 
- Financials have best opportunities with moderate beta
- Healthcare is defensive (low XJO beta)
- Materials are aggressive with high lithium exposure

---

### Example 4: Conditional Formatting - Factor Heatmap

**Goal**: Visualize factor strengths across stocks

**Steps**:
1. Open `factor_view_stocks.csv` in Excel
2. Select columns: `prediction_confidence` through `sector_momentum`
3. **Home → Conditional Formatting → Color Scales**
4. Choose: **Green-Yellow-Red** (reversed)
   - Green = High (good)
   - Red = Low (needs attention)
5. Scroll through to identify patterns

**What to look for**:
- **All green row**: Stock excels across all factors
- **Red volatility**: Stock may be risky
- **Red liquidity**: Stock may be hard to trade
- **Green technical_strength**: Strong momentum

---

### Example 5: Multi-Criteria Filtering

**Goal**: Find stocks meeting multiple specific criteria

**Criteria**:
- High AI confidence (prediction_confidence > 85)
- Strong technical setup (technical_strength > 85)
- Market-aligned (spi_alignment > 70)
- Liquid (liquidity > 80)

**Steps**:
1. Open `factor_view_stocks.csv` in Excel
2. Enable filters on all columns
3. Apply all four filters above
4. Sort by `opportunity_score` (descending)

**Expected Result**: 5-15 stocks meeting all criteria

**Use case**: High-conviction trades with strong signals across multiple dimensions

---

## 🐍 Python Examples

### Example 1: Load and Explore Data

```python
import pandas as pd
import numpy as np

# Load factor view
df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Basic info
print(f"Total stocks: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nSummary statistics:")
print(df[['opportunity_score', 'beta_xjo', 'beta_lithium']].describe())

# Top 10 opportunities
print("\nTop 10 Opportunities:")
print(df.nlargest(10, 'opportunity_score')[['symbol', 'name', 'opportunity_score', 'prediction']])
```

---

### Example 2: Defensive Portfolio Builder

```python
import pandas as pd

df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Define defensive criteria
defensive = df[
    (df['beta_xjo'] < 0.8) &          # Low market sensitivity
    (df['volatility'] > 70) &         # Stable prices
    (df['liquidity'] > 80) &          # Easy to trade
    (df['opportunity_score'] > 75)    # Still attractive
].copy()

# Sort by opportunity score
defensive = defensive.sort_values('opportunity_score', ascending=False)

# Display results
print(f"Found {len(defensive)} defensive stocks\n")
print(defensive[['symbol', 'name', 'beta_xjo', 'volatility', 'opportunity_score']].head(10))

# Export to new CSV
defensive.to_csv("reports/factor_view/defensive_portfolio.csv", index=False)
print("\nExported to: reports/factor_view/defensive_portfolio.csv")
```

---

### Example 3: Factor Correlation Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Select factor columns
factors = [
    'prediction_confidence', 'technical_strength', 'spi_alignment',
    'liquidity', 'volatility', 'sector_momentum',
    'beta_xjo', 'beta_lithium', 'opportunity_score'
]

# Calculate correlation matrix
corr_matrix = df[factors].corr()

# Create heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Factor Correlation Matrix', fontsize=16)
plt.tight_layout()
plt.savefig('reports/factor_view/factor_correlation.png', dpi=300)
print("Correlation heatmap saved to: reports/factor_view/factor_correlation.png")

# Find strongest correlations with opportunity_score
opp_score_corr = corr_matrix['opportunity_score'].sort_values(ascending=False)
print("\nFactors most correlated with opportunity_score:")
print(opp_score_corr)
```

---

### Example 4: Sector Comparison

```python
import pandas as pd

stocks_df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")
sector_df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_sector_summary.csv")

# Display sector rankings
print("=" * 80)
print("SECTOR RANKINGS")
print("=" * 80)

sector_df_sorted = sector_df.sort_values('avg_opportunity_score', ascending=False)
for idx, row in sector_df_sorted.iterrows():
    print(f"\n{row['sector']:20s}")
    print(f"  Avg Opportunity: {row['avg_opportunity_score']:.1f}")
    print(f"  Beta XJO:        {row['avg_beta_xjo']:.2f} {'(Defensive)' if row['avg_beta_xjo'] < 0.8 else '(Aggressive)' if row['avg_beta_xjo'] > 1.2 else '(Moderate)'}")
    print(f"  Beta Lithium:    {row['avg_beta_lithium']:.2f}")
    print(f"  Stock Count:     {row['stock_count']}")
    print(f"  Buy Signals:     {row['buy_count']}")
```

---

### Example 5: Time Series Analysis (Multiple Runs)

```python
import pandas as pd
import glob
from datetime import datetime

# Load all factor view files
files = sorted(glob.glob("reports/factor_view/*_factor_view_stocks.csv"))

# Extract dates and load data
dfs = []
for file in files:
    date_str = file.split('/')[-1].split('_')[0]
    df = pd.read_csv(file)
    df['date'] = pd.to_datetime(date_str)
    dfs.append(df)

# Combine all data
all_data = pd.concat(dfs, ignore_index=True)

# Analyze specific stock over time
symbol = "CBA.AX"
stock_history = all_data[all_data['symbol'] == symbol].sort_values('date')

print(f"Historical Analysis for {symbol}")
print("=" * 80)
print(stock_history[['date', 'opportunity_score', 'beta_xjo', 'prediction_confidence', 'technical_strength']])

# Calculate changes
if len(stock_history) > 1:
    latest = stock_history.iloc[-1]
    previous = stock_history.iloc[-2]
    
    print(f"\n📊 Recent Changes:")
    print(f"Opportunity Score: {previous['opportunity_score']:.1f} → {latest['opportunity_score']:.1f} ({latest['opportunity_score'] - previous['opportunity_score']:+.1f})")
    print(f"Beta XJO:          {previous['beta_xjo']:.2f} → {latest['beta_xjo']:.2f} ({latest['beta_xjo'] - previous['beta_xjo']:+.2f})")
```

---

### Example 6: Custom Factor Weighting

```python
import pandas as pd

df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Define custom weights (must sum to 1.0)
weights = {
    'prediction_confidence': 0.25,  # 25% - AI confidence
    'technical_strength': 0.20,     # 20% - Technical setup
    'liquidity': 0.20,              # 20% - Tradability
    'volatility': 0.15,             # 15% - Stability
    'sector_momentum': 0.10,        # 10% - Sector strength
    'spi_alignment': 0.10          # 10% - Market alignment
}

# Calculate custom score
df['custom_score'] = (
    df['prediction_confidence'] * weights['prediction_confidence'] +
    df['technical_strength'] * weights['technical_strength'] +
    df['liquidity'] * weights['liquidity'] +
    df['volatility'] * weights['volatility'] +
    df['sector_momentum'] * weights['sector_momentum'] +
    df['spi_alignment'] * weights['spi_alignment']
)

# Compare to original opportunity_score
comparison = df[['symbol', 'name', 'opportunity_score', 'custom_score']].copy()
comparison['score_diff'] = comparison['custom_score'] - comparison['opportunity_score']
comparison = comparison.sort_values('custom_score', ascending=False)

print("Top 10 by Custom Score:")
print(comparison.head(10))

print("\nBiggest score differences:")
print(comparison.nlargest(5, 'score_diff')[['symbol', 'opportunity_score', 'custom_score', 'score_diff']])
```

---

### Example 7: Beta-Adjusted Returns Analysis

```python
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Download recent performance (last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

symbols = df['symbol'].tolist()[:10]  # First 10 for speed
returns_data = []

for symbol in symbols:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        if len(hist) > 0:
            returns = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
            beta_xjo = df[df['symbol'] == symbol]['beta_xjo'].values[0]
            returns_data.append({
                'symbol': symbol,
                'return_30d': returns,
                'beta_xjo': beta_xjo,
                'risk_adjusted_return': returns / max(beta_xjo, 0.5)  # Avoid div by zero
            })
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

# Create results dataframe
results = pd.DataFrame(returns_data)
results = results.sort_values('risk_adjusted_return', ascending=False)

print("Beta-Adjusted Returns (30 days):")
print("=" * 80)
print(results.to_string(index=False))
```

---

## 📈 Advanced Workflows

### Workflow 1: Monthly Rebalancing Strategy

```python
import pandas as pd

# Load factor view
df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Define portfolio constraints
MAX_STOCKS = 10
MIN_LIQUIDITY = 80
MIN_OPP_SCORE = 75
TARGET_AVG_BETA = 1.0  # Neutral market exposure

# Filter candidates
candidates = df[
    (df['liquidity'] >= MIN_LIQUIDITY) &
    (df['opportunity_score'] >= MIN_OPP_SCORE)
].copy()

# Sort by opportunity score
candidates = candidates.sort_values('opportunity_score', ascending=False)

# Build portfolio with beta constraint
portfolio = []
current_beta_sum = 0

for idx, row in candidates.iterrows():
    if len(portfolio) >= MAX_STOCKS:
        break
    
    # Check if adding this stock keeps avg beta near target
    new_beta_avg = (current_beta_sum + row['beta_xjo']) / (len(portfolio) + 1)
    
    if abs(new_beta_avg - TARGET_AVG_BETA) < 0.3:  # Within 0.3 of target
        portfolio.append(row)
        current_beta_sum += row['beta_xjo']

# Convert to dataframe
portfolio_df = pd.DataFrame(portfolio)

print(f"Portfolio Summary:")
print(f"Stocks: {len(portfolio_df)}")
print(f"Average Beta XJO: {portfolio_df['beta_xjo'].mean():.2f}")
print(f"Average Opportunity Score: {portfolio_df['opportunity_score'].mean():.1f}")
print(f"\nHoldings:")
print(portfolio_df[['symbol', 'name', 'opportunity_score', 'beta_xjo', 'sector']])

# Export
portfolio_df.to_csv("reports/factor_view/monthly_portfolio.csv", index=False)
```

---

### Workflow 2: Risk Parity Allocation

```python
import pandas as pd
import numpy as np

df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Select top stocks
top_stocks = df.nlargest(10, 'opportunity_score').copy()

# Calculate inverse volatility weights (risk parity)
# Higher volatility = lower weight
top_stocks['volatility_inverse'] = 100 / top_stocks['volatility']
total_inv_vol = top_stocks['volatility_inverse'].sum()
top_stocks['weight'] = (top_stocks['volatility_inverse'] / total_inv_vol) * 100

# Display allocation
print("Risk Parity Portfolio Allocation:")
print("=" * 80)
print(top_stocks[['symbol', 'name', 'volatility', 'weight', 'opportunity_score']].to_string(index=False))
print(f"\nTotal Weight: {top_stocks['weight'].sum():.1f}%")
print(f"Average Volatility: {top_stocks['volatility'].mean():.1f}")
```

---

## 🎓 Tips and Best Practices

### Excel Tips

1. **Save Custom Views**: After applying filters, save as custom view (View → Custom Views)
2. **Use Tables**: Convert to Table (Ctrl+T) for easier filtering and formulas
3. **Freeze Panes**: Freeze first row (View → Freeze Panes) for easier scrolling
4. **Named Ranges**: Create named ranges for factor columns for easier formulas

### Python Tips

1. **Virtual Environment**: Use venv for package management
2. **Jupyter Notebooks**: Great for interactive analysis
3. **Save Scripts**: Save working analysis scripts for reuse
4. **Version Control**: Git track your analysis code

### Analysis Tips

1. **Multiple Factors**: Don't rely on single factor—combine multiple factors
2. **Beta Context**: Consider market conditions when using beta
3. **Sector Diversification**: Don't concentrate too heavily in one sector
4. **Time Series**: Analyze trends over multiple pipeline runs
5. **Backtesting**: Compare factor signals to actual stock performance

---

## 📋 Common Filters Reference

**Defensive Stocks:**
```
beta_xjo < 0.8
volatility > 70
```

**Aggressive Growth:**
```
beta_xjo > 1.2
prediction_confidence > 85
technical_strength > 80
```

**High Confidence Trades:**
```
prediction_confidence > 85
technical_strength > 85
liquidity > 80
```

**Commodity Plays:**
```
beta_lithium > 0.5
sector = "Materials"
```

**Liquid Stocks Only:**
```
liquidity > 85
```

**Stable Stocks:**
```
volatility > 75
penalty_count = 0
```

---

## 🔗 Related Documentation

- **Technical Guide**: `docs/FACTOR_VIEW_AND_BETAS.md`
- **Release Notes**: `RELEASE_NOTES_v1.1.md`
- **Main README**: `README.md`

---

**Happy analyzing!** 📊

For questions or issues, see `docs/TROUBLESHOOTING.md`
