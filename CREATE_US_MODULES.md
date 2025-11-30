# Plan: Create US Market Modules Based on Working ASX

## Strategy

**Clone the working ASX modules and adapt them for US market data sources.**

## Modules to Create

### 1. US Stock Scanner
**Source:** `stock_scanner.py` (ASX)  
**Target:** `us_stock_scanner.py`  
**Changes:**
- Config: `asx_sectors.json` → `us_sectors.json`
- Symbols: Add US format (no `.AX` suffix)
- Keep ALL logic identical

### 2. US Market Monitor  
**Source:** `spi_monitor.py` (ASX SPI futures)  
**Target:** `us_market_monitor.py`  
**Changes:**
- Index: `^AXJO` → `^GSPC` (S&P 500)
- Index: `^VIX` (add VIX monitoring)
- Keep sentiment calculation logic

### 3. US Market Regime Engine
**Source:** `market_regime_engine.py` (ASX)  
**Target:** `us_market_regime_engine.py`  
**Changes:**
- Index: ASX 200 → S&P 500
- Keep HMM logic identical

### 4. US Overnight Pipeline
**Source:** `overnight_pipeline.py` (ASX)  
**Target:** `us_overnight_pipeline.py`  
**Changes:**
- Use US modules instead of ASX
- Report path: `reports/us/`
- Keep orchestration logic identical

### 5. US Sectors Config
**Create:** `models/config/us_sectors.json`  
**Content:** US sector definitions with stocks

## Key Principle

**CLONE, DON'T REDESIGN**

- ✅ Copy working ASX code exactly
- ✅ Change only data sources (symbols, indices)
- ✅ Keep all logic, structure, parameters identical
- ❌ Don't try to "improve" or "optimize"
- ❌ Don't merge ASX and US into one system

## Execution Order

1. Create `us_sectors.json` config
2. Clone `stock_scanner.py` → `us_stock_scanner.py`
3. Clone `spi_monitor.py` → `us_market_monitor.py`
4. Clone `market_regime_engine.py` → `us_market_regime_engine.py`
5. Clone `overnight_pipeline.py` → `us_overnight_pipeline.py`
6. Test US pipeline independently
7. Add UI integration (separate US section)

## Testing

Test US pipeline completely independently:
```bash
python models/screening/us_overnight_pipeline.py
```

Should generate:
- `reports/us/2025-11-24_us_market_report.html`
- With regime data
- With market sentiment
- With top opportunities

## No Breaking Changes to ASX

- ✅ ASX modules remain unchanged
- ✅ ASX still works exactly as before
- ✅ US is completely separate parallel system
