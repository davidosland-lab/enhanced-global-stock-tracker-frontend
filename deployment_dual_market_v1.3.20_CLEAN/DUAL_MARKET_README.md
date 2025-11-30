# Event Risk Guard v1.3.20 + US Market Extension

## What This Is

This package contains:

1. **✅ EXACT WORKING Event Risk Guard v1.3.20 REGIME FINAL** (ASX market)
   - All original files unchanged
   - Proven working regime engine
   - Complete market sentiment analysis
   - Working web UI

2. **🆕 US Market Extension** (parallel system)
   - Based on same architecture as ASX
   - Separate US modules (us_*.py)
   - Independent operation
   - Separate reports

## Structure

```
deployment_dual_market_v1.3.20_CLEAN/
├── models/
│   ├── screening/
│   │   ├── overnight_pipeline.py          # ASX pipeline (working v1.3.20)
│   │   ├── stock_scanner.py               # ASX scanner (working v1.3.20)
│   │   ├── spi_monitor.py                 # ASX sentiment (working v1.3.20)
│   │   ├── market_regime_engine.py        # ASX regime (working v1.3.20)
│   │   ├── report_generator.py            # ASX reports (working v1.3.20)
│   │   ├── us_overnight_pipeline.py       # US pipeline (new, ASX-based)
│   │   ├── us_stock_scanner.py            # US scanner (new, ASX-based)
│   │   ├── us_market_monitor.py           # US sentiment (new, ASX-based)
│   │   └── us_market_regime_engine.py     # US regime (new, ASX-based)
│   └── config/
│       ├── asx_sectors.json               # ASX sectors (original)
│       └── us_sectors.json                # US sectors (new)
├── web_ui.py                              # Dashboard (original)
├── templates/                             # UI templates (original)
├── static/                                # UI assets (original)
├── RUN_PIPELINE.bat                       # Run ASX pipeline
├── RUN_US_PIPELINE.bat                    # Run US pipeline (new)
└── START_WEB_UI.bat                       # Start dashboard
```

## Installation

### 1. Install Dependencies

```bash
INSTALL.bat
```

This installs all required Python packages.

### 2. Clear Python Cache (Important!)

```bash
# First time and after any updates
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

## Usage

### Run ASX Market Screening (Original, Proven Working)

```bash
RUN_PIPELINE.bat
```

**Output:**
- Report: `reports/morning_reports/2025-11-24_market_report.html`
- Data: `data/asx/`
- Includes regime engine data, market sentiment, top opportunities

### Run US Market Screening (New, ASX-Based)

```bash
RUN_US_PIPELINE.bat
```

**Output:**
- Report: `reports/us/2025-11-24_us_market_report.html`
- Data: `data/us/`
- Same structure as ASX reports

### Run Both Markets

```bash
REM Run ASX
RUN_PIPELINE.bat

REM Then run US
RUN_US_PIPELINE.bat
```

### Start Web Dashboard

```bash
START_WEB_UI.bat
```

Access at: `http://localhost:5000`

## Key Differences: ASX vs US

| Feature | ASX Pipeline | US Pipeline |
|---------|--------------|-------------|
| **Index** | ASX 200 (^AXJO) | S&P 500 (^GSPC) |
| **Sentiment** | SPI futures | S&P 500 + VIX |
| **Sectors** | 8 ASX sectors | 8 US sectors |
| **Stocks** | ASX tickers (.AX) | US tickers |
| **Reports** | reports/morning_reports/ | reports/us/ |
| **Data** | data/asx/ | data/us/ |

## Architecture

**US modules are CLONES of ASX modules:**

- ✅ Same logic
- ✅ Same structure
- ✅ Same parameters
- ✅ Different data sources only

This ensures:
- ✅ US inherits proven ASX stability
- ✅ No complex merging logic
- ✅ Easy to maintain
- ✅ Independent operation

## Testing

### Test ASX Only (Verify Original Works)

```bash
python models\screening\overnight_pipeline.py
```

Should complete with:
- ✅ Regime data displayed
- ✅ Market sentiment calculated
- ✅ Report generated
- ✅ No errors

### Test US Only

```bash
python models\screening\us_overnight_pipeline.py
```

Should complete with:
- ✅ S&P 500 sentiment
- ✅ HMM regime analysis
- ✅ US sectors scanned
- ✅ Report generated

## Troubleshooting

### ASX Pipeline Issues

The ASX pipeline is the EXACT working v1.3.20. If it doesn't work:

1. Clear Python cache
2. Verify you're in correct directory
3. Check `TROUBLESHOOTING_CRASHES.txt`
4. Run `DIAGNOSE_CRASH.py`

### US Pipeline Issues

The US pipeline is a CLONE of ASX. If it doesn't work:

1. Verify ASX works first
2. Check US sectors config exists: `models/config/us_sectors.json`
3. Check reports/us/ directory exists
4. Check logs in `logs/screening/us/`

### "No regime data in reports"

This was the original issue. With the v1.3.20 REGIME FINAL baseline:

**ASX:** Should always show regime data (proven working)
**US:** Should show regime data (uses same logic as ASX)

If missing:
1. Clear Python cache
2. Verify using THIS package (not an old one)
3. Check that `report_generator.py` is from v1.3.20

## What's Different From Previous Attempts

### Previous Approach (Failed):
- ❌ Tried to merge ASX and US into one system
- ❌ Changed report_generator parameters
- ❌ Modified working code
- ❌ Complex integration

### Current Approach (Working):
- ✅ Kept ASX exactly as v1.3.20
- ✅ Cloned ASX architecture for US
- ✅ Separate, parallel systems
- ✅ No changes to working code

## Files From Original v1.3.20

These files are UNCHANGED from working v1.3.20:

- ✅ `models/screening/overnight_pipeline.py`
- ✅ `models/screening/report_generator.py`
- ✅ `models/screening/market_regime_engine.py`
- ✅ `models/screening/spi_monitor.py`
- ✅ `models/screening/stock_scanner.py`
- ✅ `web_ui.py`
- ✅ `templates/dashboard.html`
- ✅ All other ASX modules

## New Files for US Market

These files are NEW but based on ASX:

- 🆕 `models/screening/us_overnight_pipeline.py`
- 🆕 `models/screening/us_market_monitor.py`
- 🆕 `models/screening/us_market_regime_engine.py`
- 🆕 `models/screening/us_stock_scanner.py`
- 🆕 `models/config/us_sectors.json`
- 🆕 `RUN_US_PIPELINE.bat`

## Version Information

- **Base:** Event Risk Guard v1.3.20 REGIME FINAL (2025-11-21)
- **Extension:** US Market (2025-11-24)
- **Status:** ASX proven working, US based on same architecture

## Support

For issues:

1. **ASX not working:** Something wrong with extraction/installation (v1.3.20 is proven)
2. **US not working:** Check if ASX works first, then debug US-specific issues
3. **Both not working:** Installation or environment problem

## Expected Behavior

**After installation:**

### ASX Pipeline:
- ✅ Market sentiment analysis
- ✅ Regime engine classification
- ✅ Stock scanning across 8 sectors
- ✅ Report with regime data
- ✅ Web UI shows status

### US Pipeline:
- ✅ S&P 500 sentiment analysis
- ✅ HMM regime classification
- ✅ Stock scanning across 8 US sectors
- ✅ Report with regime data (same format as ASX)
- ✅ Independent operation

## Summary

This package provides:

1. **Proven working ASX pipeline** (v1.3.20 REGIME FINAL)
2. **US market extension** (clone of ASX architecture)
3. **Separate, parallel operation** (no merging complexity)
4. **Same proven logic** (US inherits ASX stability)

**Test ASX first. If it works, US should work too (it's the same code with different data sources).**
