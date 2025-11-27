# Intraday AUS Pipeline Enhancement Plan

## Problem Statement
Currently, the AUS overnight pipeline is designed to run **after market close** (overnight) to predict next-day opportunities. When run during **market hours (10 AM - 4 PM AEST)**, the system doesn't account for:
- Market already being open (live prices)
- Partial trading day data
- Intraday volatility and momentum
- Real-time price movements

## Proposed Enhancements

### Phase 1: Market Hours Detection Module ⚡ HIGH PRIORITY

**New Module: `models/screening/market_hours_detector.py`**

```python
class MarketHoursDetector:
    """Detects if ASX/US markets are currently open"""
    
    def is_market_open(self, market='ASX') -> Dict:
        """
        Returns:
            {
                'is_open': bool,
                'market_phase': 'pre_market' | 'open' | 'closed' | 'after_hours',
                'time_until_open': timedelta (if closed),
                'time_until_close': timedelta (if open),
                'trading_hours_elapsed_pct': float (0-100)
            }
        """
```

**Trading Hours:**
- **ASX**: 10:00 AM - 4:00 PM AEST (6 hours)
- **US (EST)**: 9:30 AM - 4:00 PM EST (6.5 hours)

---

### Phase 2: Intraday Data Fetcher Enhancement

**Update: `stock_scanner.py`**

Add intraday-aware fetching:

```python
def fetch_stock_history(self, symbol, period='1mo', include_intraday=False):
    """
    Enhanced to detect and use intraday data
    
    Args:
        include_intraday: If True and market is open, fetch 1-minute bars
    """
    market_status = self.market_detector.is_market_open('ASX')
    
    if market_status['is_open'] and include_intraday:
        # Use interval='1m', period='1d' for live intraday data
        return ticker.history(interval='1m', period='1d')
    else:
        # Standard daily data
        return ticker.history(period=period)
```

**Benefits:**
- ✅ Live price tracking during market hours
- ✅ Capture intraday momentum
- ✅ Better entry/exit timing

---

### Phase 3: Adaptive Pipeline Logic

**Update: `overnight_pipeline.py`**

Add market-hours-aware execution:

```python
class OvernightPipeline:
    def run(self):
        """Enhanced with intraday awareness"""
        
        # Detect market status
        market_status = self.market_detector.is_market_open('ASX')
        
        if market_status['is_open']:
            logger.warning("⚠️  ASX MARKET IS CURRENTLY OPEN - Running INTRADAY mode")
            return self._run_intraday_pipeline(market_status)
        else:
            logger.info("✓ ASX market closed - Running OVERNIGHT mode")
            return self._run_overnight_pipeline()
    
    def _run_intraday_pipeline(self, market_status):
        """
        Intraday-specific adjustments:
        1. Use real-time prices (1-min bars)
        2. Emphasize momentum indicators (RSI, MACD)
        3. De-emphasize overnight gap predictions
        4. Focus on same-day opportunities
        5. Shorter prediction horizon (hours vs. next day)
        """
        
        # Adjust opportunity scorer weights
        intraday_weights = {
            'prediction_confidence': 0.25,  # ↓ Less reliable intraday
            'technical_strength': 0.30,     # ↑ More important (momentum)
            'spi_alignment': 0.05,          # ↓ Less relevant (market open)
            'liquidity': 0.20,              # ↑ Critical for intraday
            'volatility': 0.15,             # ↑ Opportunity for intraday
            'sector_momentum': 0.05
        }
        
        # Use intraday data
        opportunities = self._scan_with_intraday_data()
        
        # Generate intraday-specific report
        report_path = self._generate_intraday_report(opportunities)
        
        return opportunities, report_path
```

---

### Phase 4: Enhanced Opportunity Scorer

**Update: `opportunity_scorer.py`**

Add intraday momentum scoring:

```python
def score_intraday_opportunity(self, stock_data, market_status):
    """
    Intraday-specific scoring:
    - Volume spike detection (vs. daily avg)
    - Price momentum (last 15/30/60 minutes)
    - Breakout detection (support/resistance levels)
    - Bid-ask spread (liquidity)
    """
    
    scores = {}
    
    # Volume surge (vs. typical hourly volume)
    if market_status['trading_hours_elapsed_pct'] > 20:  # After first hour
        current_volume_rate = stock_data['current_volume'] / market_status['hours_elapsed']
        typical_hourly = stock_data['avg_daily_volume'] / 6  # ASX trades 6 hours
        scores['volume_surge'] = min((current_volume_rate / typical_hourly) * 50, 100)
    
    # Intraday momentum
    if 'intraday_prices' in stock_data:
        prices = stock_data['intraday_prices']
        mom_15m = (prices[-1] - prices[-15]) / prices[-15] * 100
        mom_60m = (prices[-1] - prices[-60]) / prices[-60] * 100
        scores['momentum'] = (abs(mom_15m) * 0.4 + abs(mom_60m) * 0.6) * 10
    
    return scores
```

---

### Phase 5: Report Generator Updates

**Update: `report_generator.py`**

Add intraday report template:

```html
<!-- Intraday Report Header -->
<div class="alert alert-warning">
    <h4>⚡ INTRADAY ANALYSIS - Market Currently OPEN</h4>
    <p>Generated: {current_time} AEST</p>
    <p>Trading Hours Elapsed: {elapsed_pct}%</p>
    <p>Time Until Close: {time_to_close}</p>
    <p><strong>Note:</strong> Prices and opportunities are based on real-time data and may change rapidly.</p>
</div>

<!-- Add intraday-specific metrics -->
<table>
    <tr>
        <th>Symbol</th>
        <th>Current Price</th>
        <th>15m Momentum</th>
        <th>Volume vs. Avg</th>
        <th>Intraday High/Low</th>
    </tr>
</table>
```

---

## Implementation Priority

### 🚀 Phase 1 (Immediate - 2 hours)
1. ✅ Create `MarketHoursDetector` module
2. ✅ Add market status check to pipeline entry point
3. ✅ Add warning/info messages for intraday runs

### 📊 Phase 2 (High Priority - 4 hours)
1. ✅ Update `stock_scanner.py` for intraday data fetching
2. ✅ Adjust opportunity scorer weights for intraday
3. ✅ Create intraday report template

### 🎯 Phase 3 (Medium Priority - 6 hours)
1. ✅ Add intraday momentum indicators
2. ✅ Volume surge detection
3. ✅ Real-time price alerts

### 🔮 Phase 4 (Future Enhancement)
1. ✅ WebSocket integration for live price streaming
2. ✅ Automated intraday re-scans (every 15/30 minutes)
3. ✅ Push notifications for breakout alerts

---

## Configuration Changes

**Add to `screening_config.json`:**

```json
{
  "market_hours": {
    "asx": {
      "timezone": "Australia/Sydney",
      "open_time": "10:00",
      "close_time": "16:00",
      "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    "us": {
      "timezone": "America/New_York",
      "open_time": "09:30",
      "close_time": "16:00",
      "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }
  },
  "intraday_mode": {
    "enabled": true,
    "auto_detect": true,
    "fetch_interval": "1m",
    "rescan_frequency_minutes": 30,
    "opportunity_weights": {
      "prediction_confidence": 0.25,
      "technical_strength": 0.30,
      "spi_alignment": 0.05,
      "liquidity": 0.20,
      "volatility": 0.15,
      "sector_momentum": 0.05
    }
  }
}
```

---

## Testing Plan

### Test Scenario 1: Overnight Run (Current Behavior)
```bash
# Run at 11:00 PM AEST (market closed)
python RUN_PIPELINE.bat
# Expected: Overnight mode, SPI predictions used
```

### Test Scenario 2: Intraday Run
```bash
# Run at 2:00 PM AEST (market open, 67% elapsed)
python RUN_PIPELINE.bat
# Expected: Intraday mode, live prices, momentum focus
```

### Test Scenario 3: Pre-Market Run
```bash
# Run at 9:00 AM AEST (before market open)
python RUN_PIPELINE.bat
# Expected: Overnight mode with pre-market warnings
```

---

## Cost Impact

### Data Fetching
- **Overnight mode**: ~240 stocks × 1 request = 240 requests
- **Intraday mode**: ~240 stocks × 1 request (still daily data, just more recent)
- **Additional cost**: $0 (yfinance is free, no extra API calls)

### AI Scoring
- Same as overnight mode (~$0.033 per run)
- If re-scanning every 30 minutes: ~$0.33 for 10 intraday rescans

### Recommendation
- Default: Single intraday scan ($0.033)
- Optional: Auto-rescan every 30 mins (add ~$0.33/day)

---

## Questions for User

1. **Do you want automatic intraday detection?**
   - ✅ Yes (recommended): Pipeline auto-detects and adjusts
   - ❌ No: Manual mode selection via config/CLI arg

2. **Should we use real-time 1-minute bars during market hours?**
   - ✅ Yes: Better momentum detection, more data
   - ❌ No: Stick to daily data (less accurate intraday)

3. **Auto-rescan feature?**
   - ✅ Yes: Rescan every X minutes during market hours
   - ❌ No: Single run only

4. **Report naming convention?**
   - Overnight: `asx_report_20250112_080000.html`
   - Intraday: `asx_intraday_report_20250112_140000.html`

---

## Next Steps

**Immediate Action (Option 1 - Quick Implementation)**
```bash
# Create basic market hours detector
python CREATE_MARKET_HOURS_DETECTOR.py

# Add intraday check to pipeline
python PATCH_PIPELINE_INTRADAY.py

# Test run during market hours
python RUN_PIPELINE.bat
```

**Immediate Action (Option 2 - Full Implementation)**
```bash
# Full enhancement package (estimated 6-8 hours development)
# Includes all Phase 1-3 features
```

---

## Benefits Summary

### Overnight Mode (Current)
- ✅ Predicts next-day opportunities
- ✅ Uses SPI futures and US market data
- ✅ No cost (except AI: ~$0.033)

### Intraday Mode (Enhanced)
- ✅ Live/recent prices
- ✅ Momentum-based opportunities
- ✅ Same-day actionable insights
- ✅ Better entry/exit timing
- ⚠️  Less predictive (more reactive)
- ⚠️  Requires faster decision-making

---

## Conclusion

The current system **can** run during market hours but doesn't optimize for it. The proposed enhancements will:
1. ✅ Detect market status automatically
2. ✅ Adjust scoring weights for intraday context
3. ✅ Use more recent/live data when available
4. ✅ Provide intraday-specific insights
5. ✅ Maintain backward compatibility with overnight runs

**Recommendation:** Implement **Phase 1** immediately (2 hours) for basic awareness, then **Phase 2** (4 hours) for full intraday optimization.

---

**Ready to implement?** Let me know which phases you'd like to prioritize! 🚀
