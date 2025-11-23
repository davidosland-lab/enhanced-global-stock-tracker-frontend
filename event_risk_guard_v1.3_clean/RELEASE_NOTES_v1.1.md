# Release Notes - Event Risk Guard v1.1

## 📅 Release Information

**Version**: 1.1 Factor Analysis  
**Release Date**: 2025-11-17  
**Upgrade From**: v1.0 Final  
**Compatibility**: 100% Backwards Compatible

---

## 🎯 What's New in v1.1

### Major Features Added

#### 1. Factor Attribution Analysis
Break down opportunity scores to understand what drives each stock's ranking.

**What it does:**
- Decomposes scores into 6 constituent factors
- Tracks adjustment impacts (bonuses/penalties)
- Generates per-stock and sector-level breakdowns
- Exports to CSV and JSON for analysis

**Factors analyzed:**
1. Prediction Confidence (0-100)
2. Technical Strength (0-100)
3. SPI Alignment (0-100)
4. Liquidity (0-100)
5. Volatility (0-100)
6. Sector Momentum (0-100)

**New files generated:**
```
reports/factor_view/
├── 2025-11-17_factor_view_stocks.csv           (~25 KB)
├── 2025-11-17_factor_view_sector_summary.csv   (~2 KB)
└── 2025-11-17_factor_view_summary.json         (~5 KB)
```

---

#### 2. Macro Beta Calculator
Quantify stock sensitivity to market factors using statistical regression.

**What it does:**
- Calculates betas using OLS regression
- Uses 90-day daily return data
- Provides market sensitivity metrics
- Identifies defensive vs aggressive stocks

**Default factors:**
- **XJO (^AXJO)**: ASX 200 Index - measures market sensitivity
- **Lithium (LIT.AX)**: Lithium ETF - measures commodity exposure

**Beta interpretation:**
- Beta > 1.0 = Aggressive (amplifies market moves)
- Beta = 1.0 = Moves with market
- Beta < 1.0 = Defensive (cushions market moves)
- Beta ≈ 0 = Independent of market

---

### Enhanced Pipeline Integration

**New pipeline steps:**
1. Calculate macro betas (after stock fetching)
2. Add betas to stock records
3. Run existing prediction and scoring
4. Build factor view (after scoring)
5. Save factor analysis outputs
6. Include factor view in results

**Performance impact:**
- Beta calculation: +8-12 seconds
- Factor view generation: +1-2 seconds
- Total overhead: ~10-15 seconds (~9% increase)
- **Conclusion**: Minimal impact for significant value added

---

## 📊 Use Cases

### Use Case 1: Build Defensive Portfolio
```python
import pandas as pd
df = pd.read_csv("reports/factor_view/2025-11-17_factor_view_stocks.csv")

# Filter for defensive stocks
defensive = df[
    (df['beta_xjo'] < 0.8) &          # Low market sensitivity
    (df['volatility'] > 70) &         # Stable prices
    (df['liquidity'] > 80) &          # Easy to trade
    (df['opportunity_score'] > 75)    # Still attractive
].sort_values('opportunity_score', ascending=False)

print(defensive[['symbol', 'name', 'beta_xjo', 'opportunity_score']].head(10))
```

### Use Case 2: Find Commodity Plays
```python
# Filter for lithium exposure
lithium_plays = df[
    (df['beta_lithium'] > 0.5) &      # High commodity exposure
    (df['sector'] == 'Materials') &   # Materials sector
    (df['opportunity_score'] > 75)    # Good opportunity
].sort_values('beta_lithium', ascending=False)

print(lithium_plays[['symbol', 'beta_lithium', 'opportunity_score']].head(10))
```

### Use Case 3: Sector Rotation Analysis
```python
sectors = pd.read_csv("reports/factor_view/2025-11-17_factor_view_sector_summary.csv")

# Identify strongest sectors
print(sectors.sort_values('avg_opportunity_score', ascending=False))

# Compare risk profiles
print(sectors[['sector', 'avg_beta_xjo', 'avg_opportunity_score']])
```

### Use Case 4: Factor-Driven Screening
```python
# Find stocks with strong technical setups + AI confirmation
technical_plays = df[
    (df['technical_strength'] > 85) &
    (df['prediction_confidence'] > 80) &
    (df['liquidity'] > 75)
].sort_values('technical_strength', ascending=False)

print(technical_plays[['symbol', 'technical_strength', 'prediction']].head(10))
```

---

## 🔄 Upgrading from v1.0

### Do I Need to Upgrade?

**Upgrade if:**
- ✅ You want deeper insight into what drives opportunity scores
- ✅ You need to assess market sensitivity (beta analysis)
- ✅ You want to build factor-based investment strategies
- ✅ You need sector-level portfolio analytics
- ✅ You want to filter stocks by specific factors

**Stay on v1.0 if:**
- ❌ You only need top-level opportunity scores
- ❌ You don't use CSV exports for analysis
- ❌ You're satisfied with existing functionality

---

### Upgrade Instructions

#### Option A: Clean Install (Recommended)

1. **Extract new package:**
   ```
   event_risk_guard_v1.1_factor_analysis.zip
   ```

2. **Copy your configuration:**
   ```
   From v1.0: models/config/screening_config.json
   To v1.1: models/config/screening_config.json
   ```

3. **Copy trained LSTM models (if you have them):**
   ```
   From v1.0: models/lstm_models/*.keras
   To v1.1: models/lstm_models/*.keras
   ```

4. **Run as normal:**
   ```
   RUN_OVERNIGHT_PIPELINE.bat
   ```

**Total time**: 5 minutes

---

#### Option B: In-Place Upgrade (Advanced Users)

1. **Backup v1.0 folder:**
   ```
   Copy entire event_risk_guard_v1.0_final folder
   ```

2. **Copy new files from v1.1:**
   ```
   models/screening/factor_view.py
   models/screening/macro_beta.py
   docs/FACTOR_VIEW_AND_BETAS.md
   docs/FACTOR_ANALYSIS_EXAMPLES.md
   RELEASE_NOTES_v1.1.md
   ```

3. **Update existing files:**
   ```
   models/screening/overnight_pipeline.py
   README.md
   QUICK_START.md
   WINDOWS_11_INSTALL.md
   CHANGELOG.md
   PACKAGE_CONTENTS.txt
   ```

4. **Create output directory:**
   ```
   mkdir reports\factor_view
   ```

5. **Run pipeline:**
   ```
   RUN_OVERNIGHT_PIPELINE.bat
   ```

**Note**: In-place upgrade is more complex. Clean install recommended.

---

### What Stays the Same

✅ **No configuration changes required** - system works out of the box  
✅ **No new dependencies** - uses existing packages  
✅ **All batch files unchanged** - same workflow  
✅ **Web UI unchanged** - same dashboard  
✅ **All v1.0 features preserved** - 100% backwards compatible

---

## 📁 New File Structure

```
event_risk_guard_v1.1_factor_analysis/
│
├── 🆕 RELEASE_NOTES_v1.1.md          ← You are here
│
├── models/screening/
│   ├── 🆕 factor_view.py              ← Factor attribution builder
│   ├── 🆕 macro_beta.py               ← Beta calculator
│   └── overnight_pipeline.py          (ENHANCED - factor integration)
│
├── docs/
│   ├── 🆕 FACTOR_VIEW_AND_BETAS.md    ← Technical guide
│   └── 🆕 FACTOR_ANALYSIS_EXAMPLES.md ← Usage examples
│
└── reports/
    └── 🆕 factor_view/                ← New output directory
        ├── *_factor_view_stocks.csv
        ├── *_factor_view_sector_summary.csv
        └── *_factor_view_summary.json
```

---

## 🔧 Configuration Options

### Customize Beta Factors

Want to add custom factors beyond XJO and Lithium?

**Edit**: `models/screening/overnight_pipeline.py` (line 144)

```python
from models/screening/macro_beta import FactorDefinition

self.macro_beta_calc = MacroBetaCalculator(
    lookback_days=180,  # Change lookback period (default 90)
    min_obs=80,         # Require more observations (default 40)
    factors=[
        FactorDefinition(name="xjo", symbol="^AXJO"),        # ASX 200
        FactorDefinition(name="lithium", symbol="LIT.AX"),   # Lithium
        # Add custom factors:
        FactorDefinition(name="usd_aud", symbol="AUDUSD=X"), # Currency
        FactorDefinition(name="iron_ore", symbol="TIOA.AX"), # Iron ore
        FactorDefinition(name="gold", symbol="GLD"),         # Gold
    ]
)
```

**Result**: Additional columns in factor view CSV files

---

### Change Output Directory

**Edit**: `models/screening/overnight_pipeline.py` (after line 144)

```python
from pathlib import Path
self.factor_builder = FactorViewBuilder(timezone=self.timezone)
self.factor_builder.output_dir = Path("reports/custom_analysis")
```

---

## 📊 Output File Reference

### File 1: factor_view_stocks.csv

**Columns** (20 fields):
```
symbol, name, sector, opportunity_score,
prediction_confidence, technical_strength, spi_alignment,
liquidity, volatility, sector_momentum,
base_total, total_adjustment, penalty_count, bonus_count,
beta_xjo, beta_lithium, prediction, confidence_pct
```

**Use for**: Per-stock analysis, filtering, custom screens

---

### File 2: factor_view_sector_summary.csv

**Columns** (17 fields):
```
sector, stock_count,
avg_opportunity_score, avg_prediction_confidence, avg_technical_strength,
avg_spi_alignment, avg_liquidity, avg_volatility, avg_sector_momentum,
avg_beta_xjo, avg_beta_lithium,
buy_count, hold_count, sell_count,
avg_adjustment, total_penalties, total_bonuses
```

**Use for**: Sector rotation, risk assessment by sector

---

### File 3: factor_view_summary.json

**Structure**:
```json
{
  "timestamp": "2025-11-17T23:45:00+11:00",
  "total_stocks": 85,
  "sectors": { /* per-sector breakdowns */ },
  "overall": { /* portfolio-level stats */ },
  "top_factors": { /* highest/lowest by factor */ }
}
```

**Use for**: Automated reporting, API integration, dashboards

---

## ⚡ Performance Characteristics

### Execution Time

**v1.0 Pipeline**: ~18-20 minutes (85 stocks)  
**v1.1 Pipeline**: ~19-22 minutes (85 stocks)  
**Overhead**: ~1-2 minutes (~9% increase)

**Breakdown:**
- Stock scanning: Same (~10 min)
- FinBERT analysis: Same (~4 min)
- LSTM prediction: Same (~2 min)
- Technical analysis: Same (~1 min)
- **🆕 Beta calculation**: +8-12 seconds
- Scoring: Same (~30 sec)
- **🆕 Factor view**: +1-2 seconds
- Report generation: Same (~1 min)

---

### Storage Impact

**Per Run:**
- v1.0: ~150 KB (HTML + CSV + JSON)
- v1.1: ~182 KB (v1.0 files + 3 new factor files)
- **Additional**: ~32 KB per run

**Monthly** (30 runs):
- Additional storage: ~960 KB (~1 MB)

**Annual** (365 runs):
- Additional storage: ~11.4 MB

**Conclusion**: Negligible storage impact

---

### Network Impact

**Additional yfinance API calls:**
- Factor data download: 2 additional symbols (XJO, Lithium)
- Data per symbol: ~90 days × 150 bytes = ~13.5 KB
- Total additional: ~27 KB per run

**Rate limiting**: Handled automatically by yfinance

---

## 🐛 Troubleshooting

### Issue: Beta values are NaN

**Cause**: Insufficient price data (< 40 observations)

**Solution**: Stock recently listed or trading suspended
- Check stock history on Yahoo Finance
- Reduce `min_obs` in macro_beta.py (not recommended)
- Accept NaN for new listings (system handles gracefully)

---

### Issue: Factor view files not generated

**Cause**: Directory permissions or disk space

**Solution**:
```batch
# Check directory exists
dir reports\factor_view

# Create if missing
mkdir reports\factor_view

# Check disk space
dir reports /s
```

---

### Issue: Pipeline slower than expected

**Cause**: Network latency (yfinance downloads)

**Solution**:
- Check internet connection speed
- Run during off-peak hours
- Expected overhead is ~1-2 minutes (acceptable)

---

### Issue: Can't find factor view documentation

**Location**:
```
docs/FACTOR_VIEW_AND_BETAS.md           (Technical guide)
docs/FACTOR_ANALYSIS_EXAMPLES.md        (Usage examples)
```

---

## ✅ Verification Checklist

After upgrading to v1.1, verify:

- [ ] Pipeline completes successfully
- [ ] Factor view files generated in `reports/factor_view/`
- [ ] CSV files open in Excel without errors
- [ ] Beta values present (not all NaN)
- [ ] Sector summary has correct stock counts
- [ ] JSON summary valid structure
- [ ] Execution time acceptable (~19-22 min)
- [ ] All v1.0 outputs still generated (HTML, CSV, dashboard JSON)

---

## 📚 Learning Resources

### Documentation

**Technical Guide:**
```
docs/FACTOR_VIEW_AND_BETAS.md
```
- Detailed explanation of factors
- Beta calculation methodology
- OLS regression background
- Configuration options

**Usage Examples:**
```
docs/FACTOR_ANALYSIS_EXAMPLES.md
```
- Excel pivot table examples
- Python analysis snippets
- Common filtering queries
- Portfolio construction templates

**Updated Guides:**
```
README.md                    (Factor analysis section added)
QUICK_START.md               (New outputs documented)
WINDOWS_11_INSTALL.md        (v1.1 updates)
```

---

### Example Analyses

**Defensive Portfolio:**
```python
# See: docs/FACTOR_ANALYSIS_EXAMPLES.md - Example 1
```

**Lithium Play Identification:**
```python
# See: docs/FACTOR_ANALYSIS_EXAMPLES.md - Example 2
```

**Sector Rotation:**
```python
# See: docs/FACTOR_ANALYSIS_EXAMPLES.md - Example 3
```

**Factor Performance Analysis:**
```python
# See: docs/FACTOR_ANALYSIS_EXAMPLES.md - Example 4
```

---

## 🔮 What's Next (Future v1.2+)

### Potential Future Enhancements

**Additional Factors:**
- Gold prices (GLD or GOLD.AX)
- Oil prices (CL=F or WPL.AX)
- Interest rates (^TNX for US 10-year)
- More currency pairs (AUDJPY=X, etc.)

**Advanced Analytics:**
- Multi-factor regression models
- Rolling beta calculations (time-varying)
- Factor momentum tracking
- Beta stability metrics

**Machine Learning:**
- Use factors as LSTM inputs
- Factor-based model training
- Dynamic factor weighting
- Regime-based factor selection

**Dashboard Integration:**
- Factor view section in web UI
- Interactive factor charts
- Sector comparison widgets
- Beta distribution visualizations

---

## 💬 Feedback

We'd love to hear how you're using v1.1 factor analysis:
- Which factors are most useful?
- What additional factors would you like?
- How are you using the CSV outputs?
- What analysis workflows have you created?

---

## 📜 Version History

**v1.1 Factor Analysis** (2025-11-17)
- Added factor attribution analysis
- Added macro beta calculator
- Enhanced pipeline integration
- 100% backwards compatible

**v1.0 Final** (2025-11-16)
- All 10 fixes applied
- Complete system ready
- Production tested

---

## ✅ Summary

**v1.1 adds powerful factor analysis capabilities** to help you:
- Understand what drives opportunity scores
- Assess market sensitivity (beta analysis)
- Build factor-based strategies
- Analyze sector-level trends

**Upgrade is seamless** with:
- No configuration changes required
- 100% backwards compatibility
- Minimal performance impact
- Negligible storage overhead

**Ready to upgrade?** Extract v1.1 package and run:
```batch
RUN_OVERNIGHT_PIPELINE.bat
```

**New outputs will be in**: `reports/factor_view/`

---

**Happy analyzing!** 📊

For questions, see `docs/TROUBLESHOOTING.md` or `docs/FACTOR_VIEW_AND_BETAS.md`
