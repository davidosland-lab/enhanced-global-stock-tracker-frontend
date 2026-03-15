# 🔄 PIPELINE REVERSION TO SECTOR-BASED MODEL

**Date**: January 3, 2026  
**Issue**: Current pipelines use reduced stock presets (8-20 stocks)  
**Required**: Revert to original sector-based model (8 sectors × 30 stocks = 240 total)  
**Status**: 🔴 IN PROGRESS

---

## 📊 ORIGINAL MODEL (To Restore)

### Design Pattern
```
1. Configure 8 sectors per market
2. Each sector has ~30 stocks (240 total)
3. Scan all 240 stocks with ML/FinBERT analysis
4. Take top 10 from each sector (80 stocks total)
5. Process top 80 through trading pipeline
```

### Example Flow (AU/ASX)
```
Financials:        30 stocks → scan → top 10
Materials:         30 stocks → scan → top 10
Healthcare:        30 stocks → scan → top 10
Technology:        30 stocks → scan → top 10
Energy:            30 stocks → scan → top 10
Industrials:       30 stocks → scan → top 10
Consumer_Staples:  30 stocks → scan → top 10
Real_Estate:       30 stocks → scan → top 10
─────────────────────────────────────────────
TOTAL:            240 stocks → 80 top stocks
```

---

## 🚨 CURRENT STATE (Incorrect)

### AU Pipeline (`run_au_pipeline.py`)
```python
ASX_PRESETS = {
    'ASX Blue Chips': [8 stocks],    # ❌ Too few
    'ASX Banks': [6 stocks],         # ❌ Too few
    'ASX Mining': [7 stocks],        # ❌ Too few
    ...
}
```

### US Pipeline (`run_us_pipeline.py`)
```python
US_PRESETS = {
    'US Tech Giants': [8 stocks],    # ❌ Too few
    'US Blue Chips': [8 stocks],     # ❌ Too few
    ...
}
```

### UK Pipeline (`run_uk_pipeline.py`)
```python
UK_PRESETS = {
    'FTSE 100 Top 10': [10 stocks],  # ❌ Too few
    'UK Blue Chips': [8 stocks],     # ❌ Too few
    ...
}
```

---

## ✅ REQUIRED CHANGES

### 1. Update Sector Configuration Files

#### `phase3_intraday_deployment/config/asx_sectors.json`
```json
{
  "sectors": {
    "Financials": {"weight": 1.2, "stocks": [30 stocks]},
    "Materials": {"weight": 1.3, "stocks": [30 stocks]},
    "Healthcare": {"weight": 1.1, "stocks": [30 stocks]},
    "Technology": {"weight": 1.4, "stocks": [30 stocks]},
    "Energy": {"weight": 1.2, "stocks": [30 stocks]},
    "Industrials": {"weight": 1.0, "stocks": [30 stocks]},
    "Consumer_Staples": {"weight": 1.0, "stocks": [30 stocks]},
    "Real_Estate": {"weight": 0.9, "stocks": [30 stocks]}
  },
  "metadata": {
    "total_stocks": 240,
    "sectors_count": 8,
    "stocks_per_sector": 30
  }
}
```

#### `phase3_intraday_deployment/config/us_sectors.json`
```json
{
  "sectors": {
    "Financials": {"weight": 1.2, "stocks": [30 stocks]},
    "Materials": {"weight": 1.3, "stocks": [30 stocks]},
    "Healthcare": {"weight": 1.1, "stocks": [30 stocks]},
    "Technology": {"weight": 1.4, "stocks": [30 stocks]},
    "Energy": {"weight": 1.2, "stocks": [30 stocks]},
    "Industrials": {"weight": 1.0, "stocks": [30 stocks]},
    "Consumer_Discretionary": {"weight": 1.0, "stocks": [30 stocks]},
    "Consumer_Staples": {"weight": 1.0, "stocks": [30 stocks]}
  },
  "metadata": {
    "total_stocks": 240,
    "sectors_count": 8,
    "stocks_per_sector": 30
  }
}
```

#### `phase3_intraday_deployment/config/uk_sectors.json` (NEW)
```json
{
  "sectors": {
    "Financials": {"weight": 1.2, "stocks": [30 stocks]},
    "Materials": {"weight": 1.3, "stocks": [30 stocks]},
    "Healthcare": {"weight": 1.1, "stocks": [30 stocks]},
    "Technology": {"weight": 1.0, "stocks": [30 stocks]},
    "Energy": {"weight": 1.2, "stocks": [30 stocks]},
    "Industrials": {"weight": 1.0, "stocks": [30 stocks]},
    "Consumer_Discretionary": {"weight": 1.0, "stocks": [30 stocks]},
    "Consumer_Staples": {"weight": 1.0, "stocks": [30 stocks]}
  },
  "metadata": {
    "total_stocks": 240,
    "sectors_count": 8,
    "stocks_per_sector": 30
  }
}
```

---

### 2. Create Stock Scanner Module

**File**: `phase3_intraday_deployment/stock_scanner.py`

```python
class SectorStockScanner:
    """
    Scans stocks by sector and ranks them
    
    Process:
    1. Load sector configuration
    2. Scan all stocks in sector (with validation)
    3. Score stocks using ML + FinBERT
    4. Return top N stocks per sector
    """
    
    def __init__(self, config_file):
        self.sectors = load_sectors(config_file)
    
    def scan_sector(self, sector_name, top_n=10):
        """Scan sector and return top N stocks"""
        stocks = self.sectors[sector_name]['stocks']
        scored_stocks = []
        
        for symbol in stocks:
            score = self.calculate_score(symbol)
            scored_stocks.append({'symbol': symbol, 'score': score})
        
        # Sort by score and return top N
        scored_stocks.sort(key=lambda x: x['score'], reverse=True)
        return scored_stocks[:top_n]
    
    def scan_all_sectors(self, top_n_per_sector=10):
        """Scan all sectors and return top stocks per sector"""
        results = {}
        for sector_name in self.sectors:
            results[sector_name] = self.scan_sector(sector_name, top_n)
        return results
```

---

### 3. Update Pipeline Runners

#### `run_au_pipeline.py` Changes

**Before**:
```python
ASX_PRESETS = {
    'ASX Blue Chips': ['CBA.AX', 'BHP.AX', ...]  # 8 stocks
}

# Direct usage
symbols = ASX_PRESETS['ASX Blue Chips']
```

**After**:
```python
from stock_scanner import SectorStockScanner

scanner = SectorStockScanner('config/asx_sectors.json')
results = scanner.scan_all_sectors(top_n_per_sector=10)

# Extract top stocks from all sectors
symbols = []
for sector, stocks in results.items():
    symbols.extend([s['symbol'] for s in stocks])

# Result: ~80 top stocks from 240 scanned
```

Similar changes for `run_us_pipeline.py` and `run_uk_pipeline.py`.

---

## 📁 FILES TO MODIFY

### Configuration Files
1. ✅ `phase3_intraday_deployment/config/asx_sectors.json` - UPDATE
2. ✅ `phase3_intraday_deployment/config/us_sectors.json` - UPDATE
3. ✅ `phase3_intraday_deployment/config/uk_sectors.json` - CREATE

### Scanner Module
4. ✅ `phase3_intraday_deployment/stock_scanner.py` - CREATE

### Pipeline Runners
5. ✅ `phase3_intraday_deployment/run_au_pipeline.py` - UPDATE
6. ✅ `phase3_intraday_deployment/run_us_pipeline.py` - UPDATE
7. ✅ `phase3_intraday_deployment/run_uk_pipeline.py` - UPDATE

---

## 🎯 IMPLEMENTATION STEPS

### Step 1: Restore Original Sector Configs
- Copy sector JSON from git history (commit 0ccb412)
- Place in `phase3_intraday_deployment/config/`
- Verify 8 sectors × 30 stocks = 240 total

### Step 2: Create Stock Scanner Module
- Implement `SectorStockScanner` class
- Add validation (price, volume, market cap)
- Add scoring (ML + FinBERT integration)
- Add sector weighting

### Step 3: Update Pipeline Runners
- Replace preset-based selection
- Use `SectorStockScanner` instead
- Scan 240 stocks → select top 80
- Keep existing trading logic

### Step 4: Test All Pipelines
- Test AU pipeline with 240 stocks
- Test US pipeline with 240 stocks
- Test UK pipeline with 240 stocks
- Verify top 10 per sector selection

---

## 🔢 EXPECTED RESULTS

### Before (Current)
```
AU: 8-20 stocks depending on preset
US: 8-20 stocks depending on preset
UK: 8-20 stocks depending on preset
Total: ~24-60 stocks across all markets
```

### After (Target)
```
AU: Scan 240 → Trade top 80 (10 per sector)
US: Scan 240 → Trade top 80 (10 per sector)
UK: Scan 240 → Trade top 80 (10 per sector)
Total: Scan 720 → Trade top 240 stocks
```

---

## ⚠️ IMPORTANT NOTES

### Processing Model
1. **Scan Phase**: All 240 stocks analyzed (ML + FinBERT)
2. **Selection Phase**: Top 10 from each sector chosen (80 stocks)
3. **Trading Phase**: Monitor and trade top 80 stocks
4. **Refresh**: Re-scan periodically (daily/weekly)

### Performance Considerations
- Scanning 240 stocks takes ~10-15 minutes per market
- Use caching to avoid re-scanning same stocks
- Run scans during off-market hours (overnight)
- Use rate limiting to avoid API throttling

### Configuration Flexibility
- Can adjust `top_n_per_sector` (default: 10)
- Can adjust sector weights (high-weight sectors matter more)
- Can filter by selection criteria (min price, volume, etc.)

---

## 📊 COMPARISON

| Metric | Current (Preset) | Target (Sector-Based) |
|--------|------------------|----------------------|
| **Stocks Scanned** | 8-20 | 240 |
| **Stocks Traded** | 8-20 | 80 (top 10/sector) |
| **Sectors Covered** | Mixed | 8 balanced |
| **Diversification** | Low | High |
| **ML Analysis** | Minimal | Comprehensive |
| **Selection Method** | Manual presets | Automated scoring |
| **Update Frequency** | Static | Dynamic (daily) |

---

## 🚀 NEXT STEPS

1. **[IN PROGRESS]** Copy original sector configs from git history
2. **[PENDING]** Create `stock_scanner.py` module
3. **[PENDING]** Update all three pipeline runners
4. **[PENDING]** Test AU/US/UK pipelines
5. **[PENDING]** Document changes and commit

---

## 📝 NOTES

### Why This Model Is Better
- **Diversification**: Balanced across 8 sectors
- **Coverage**: Scans 3x more stocks (240 vs 80)
- **Selection**: Data-driven (ML scores) vs manual presets
- **Flexibility**: Easy to add/remove stocks per sector
- **Scalability**: Can expand to more sectors/stocks

### Migration Path
- Keep existing presets for backwards compatibility
- Add new `--use-sectors` flag for sector-based mode
- Default to sector-based for new installations
- Deprecate presets in future version

---

**Status**: 🔴 Implementation in progress  
**Priority**: 🔴 HIGH - Core functionality restoration  
**Est. Time**: 2-3 hours for full implementation  
**Testing**: 1 hour per market (3 hours total)

