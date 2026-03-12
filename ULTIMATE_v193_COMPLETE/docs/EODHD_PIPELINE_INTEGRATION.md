# ============================================================
# EODHD INTEGRATION - PIPELINE EXECUTION FLOW
# Unified Trading System v193.11.7.6
# ============================================================

## How EODHD Calls Are Integrated Into Pipeline Runs

The EODHD API calls are **NOT separate instances** - they are **fully integrated** into the existing pipeline runners as part of the market sentiment analysis phase.

---

## Pipeline Execution Flow

### Australian Market Pipeline (`run_au_pipeline.py`)

```
1. Pipeline Start
   └─> OvernightPipeline.run_full_pipeline()
       
2. Market Sentiment Phase
   └─> SPIMonitor.get_market_sentiment()
       │
       ├─> Priority 1: EODHD SPI 200 Futures ✓ NEW
       │   └─> EODHDClient.get_spi_200_overnight_gap()
       │       ├─> Check cache (4-hour TTL)
       │       ├─> Check rate limit (2/20 daily)
       │       └─> Fetch AP.INDX (SPI 200 futures)
       │
       ├─> Priority 2: Realtime Predictor (fallback)
       ├─> Priority 3: SPI Proxy Advanced (fallback)
       └─> Priority 4: US Market Correlation (fallback)

3. Stock Scanning Phase (uses sentiment result)
4. Event Risk Assessment
5. Batch Prediction (FinBERT + LSTM)
6. Opportunity Scoring (14-factor)
7. Report Generation
```

**Key Point**: When you run `run_au_pipeline.py`, it automatically:
1. Initializes SPIMonitor
2. SPIMonitor initializes EODHDClient (if .env configured)
3. EODHDClient makes API call during sentiment analysis
4. Result flows through rest of pipeline

**No separate EODHD script needed!**

---

### UK Market Pipeline (`run_uk_pipeline.py`)

```
1. Pipeline Start
   └─> UKOvernightPipeline.run_full_pipeline()
       
2. Market Sentiment Phase
   └─> RealtimeFTSEPredictor.compute_prediction()
       │
       ├─> Priority 1: EODHD FTSE 100 Futures ✓ NEW
       │   └─> EODHDClient.get_ftse_100_overnight_gap()
       │       ├─> Check cache (4-hour TTL)
       │       ├─> Check rate limit (2/20 daily)
       │       └─> Fetch UK100.INDX (FTSE 100 futures)
       │
       └─> Priority 2: Market Close Correlation (fallback)

3. Stock Scanning Phase (uses sentiment result)
4. Event Risk Assessment
5. Batch Prediction (FinBERT + LSTM)
6. Opportunity Scoring (14-factor)
7. Report Generation
```

**Key Point**: When you run `run_uk_pipeline.py`, it automatically:
1. Initializes UKOvernightPipeline
2. Pipeline initializes RealtimeFTSEPredictor
3. Predictor initializes EODHDClient (if .env configured)
4. EODHDClient makes API call during sentiment analysis
5. Result flows through rest of pipeline

**No separate EODHD script needed!**

---

## Daily Execution Schedule

### Typical Production Schedule

| Time (AEST) | Command | Pipeline | EODHD Call | Symbol |
|-------------|---------|----------|------------|--------|
| **06:30 AM** | `python run_au_pipeline.py` | Australian | 1 | AP.INDX (SPI 200) |
| **07:00 AM** | `python run_uk_pipeline.py` | UK | 1 | UK100.INDX (FTSE) |

**Total EODHD API Usage**: 2 calls per day (10% of 20-call free tier)

---

## Code Integration Points

### 1. Australian Pipeline Integration

**File**: `pipelines/models/screening/spi_monitor.py`  
**Lines**: 41-51, 110-120, 165-195

```python
# Initialization (lines 110-120)
if EODHD_AVAILABLE:
    try:
        self.eodhd_client = EODHDClient()
        logger.info("[OK] EODHD Client initialized")
    except Exception as e:
        logger.warning(f"[!] EODHD initialization failed: {e}")
        self.eodhd_client = None

# Usage in get_market_sentiment() (lines 165-195)
if self.eodhd_client is not None:
    try:
        logger.info("[EODHD] Attempting to fetch SPI 200 futures data...")
        eodhd_result = self.eodhd_client.get_spi_200_overnight_gap()
        
        if eodhd_result and eodhd_result.get('predicted_gap_pct') is not None:
            gap_prediction = {
                'predicted_gap_pct': eodhd_result['predicted_gap_pct'],
                'confidence': eodhd_result['confidence'],
                'direction': eodhd_result['direction'],
                'method': eodhd_result['method'],
                'spi_price': eodhd_result.get('spi_price'),
                'source': 'EODHD_FUTURES'
            }
            method_used = 'EODHD'
            logger.info(f"[EODHD] [OK] Success! Gap: {eodhd_result['predicted_gap_pct']:+.2f}%, "
                      f"Confidence: {eodhd_result['confidence']:.0%}, "
                      f"Direction: {eodhd_result['direction']}")
    except Exception as e:
        logger.warning(f"[EODHD] Failed: {e}")
```

**Called by**: `OvernightPipeline.run_full_pipeline()` → Market sentiment phase

---

### 2. UK Pipeline Integration

**File**: `pipelines/models/screening/ftse_proxy_realtime.py`  
**Lines**: 18-20, 147-157, 211-253

```python
# Initialization (lines 147-157)
if EODHD_AVAILABLE:
    try:
        self.eodhd_client = EODHDClient()
        logger.info("[OK] EODHD Client initialized for FTSE predictions")
    except Exception as e:
        logger.warning(f"[!] EODHD initialization failed: {e}")
        self.eodhd_client = None

# Usage in compute_prediction() (lines 211-253)
if self.eodhd_client is not None:
    try:
        logger.info("[EODHD] Attempting to fetch FTSE 100 futures data...")
        eodhd_result = self.eodhd_client.get_ftse_100_overnight_gap()
        
        if eodhd_result and eodhd_result.get('predicted_gap_pct') is not None:
            # Apply world risk adjustment if needed
            predicted_gap = eodhd_result['predicted_gap_pct']
            confidence = eodhd_result['confidence']
            
            result = {
                'predicted_gap_pct': round(predicted_gap, 2),
                'confidence': round(confidence, 2),
                'direction': direction,
                'method': 'EODHD_FTSE_FUTURES',
                'timestamp': eodhd_result['timestamp'],
                'ftse_price': eodhd_result.get('ftse_price'),
                'source': 'EODHD',
                'available': True
            }
            
            return result
    except Exception as e:
        logger.warning(f"[EODHD] Failed: {e} - falling back to market correlation")
```

**Called by**: `UKOvernightPipeline.run_full_pipeline()` → Market sentiment phase

---

## Execution Examples

### Running Australian Pipeline (with EODHD)

```bash
cd ULTIMATE_v193_COMPLETE/pipelines
python run_au_pipeline.py --mode full
```

**Log Output (with EODHD configured):**
```
[OK] Using FinBERT venv: C:\...\finbert_v4.4.4\venv\Lib\site-packages
[OK] Created required directories
[OK] EODHD Client initialized
[OK] SPI Proxy initialized
[OK] Realtime SPI Predictor initialized
[EODHD] Attempting to fetch SPI 200 futures data...
[EODHD] [OK] Success! Gap: +0.42%, Confidence: 95%, Direction: BULLISH
[EODHD] SPI 200 Price: 7845.50
[OK] Market Sentiment Retrieved:
  Sentiment Score: 72.5/100
  Gap Prediction: +0.42%
  Direction: BULLISH
  Recommendation: BUY
```

**Log Output (without EODHD configured):**
```
[OK] Using FinBERT venv: C:\...\finbert_v4.4.4\venv\Lib\site-packages
[OK] Created required directories
[!] EODHD unavailable - using fallback methods
[OK] SPI Proxy initialized
[OK] Realtime SPI Predictor initialized
[REALTIME] Using actual US/UK market close data for prediction...
[REALTIME] [OK] Success! Gap: +0.38%, Confidence: 85%, Direction: BULLISH
[OK] Market Sentiment Retrieved:
  Sentiment Score: 68.2/100
  Gap Prediction: +0.38%
  Direction: BULLISH
  Recommendation: BUY
```

---

### Running UK Pipeline (with EODHD)

```bash
cd ULTIMATE_v193_COMPLETE/pipelines
python run_uk_pipeline.py --mode full
```

**Log Output (with EODHD configured):**
```
[OK] Using FinBERT venv: C:\...\finbert_v4.4.4\venv\Lib\site-packages
[OK] Created required directories
[OK] EODHD Client initialized for FTSE predictions
[EODHD] Attempting to fetch FTSE 100 futures data...
[EODHD] [OK] Success! Gap: +0.28%, Confidence: 95%, Direction: NEUTRAL
[EODHD] FTSE 100 Price: 7623.80
[REALTIME FTSE] PREDICTION: +0.28% (NEUTRAL, 95% confidence)
```

---

## Verification

### Check EODHD Is Being Used

**Method 1: Check Logs**
```bash
# Australian pipeline
grep "EODHD" logs/screening/*.log

# Expected output:
# [EODHD] Attempting to fetch SPI 200 futures data...
# [EODHD] [OK] Success! Gap: +0.42%, Confidence: 95%
```

**Method 2: Check Rate Limit File**
```bash
# View rate limit state
cat state/eodhd_rate_limit.json

# Expected output:
{
  "last_reset": "2026-03-12T00:00:00",
  "call_count": 2,
  "max_calls_per_day": 20
}
```

**Method 3: Check Cache Directory**
```bash
# View cached EODHD responses
dir cache/eodhd/  # Windows
ls cache/eodhd/   # Linux/Mac

# Expected files:
# AP.INDX_realtime_2026-03-12.json
# UK100.INDX_realtime_2026-03-12.json
```

---

## Configuration States

### State 1: EODHD Configured and Working ✅

**.env exists with valid API key**

**Pipeline behavior:**
1. ✓ EODHDClient initializes
2. ✓ API call made to EODHD (if not cached)
3. ✓ 95% confidence predictions
4. ✓ Logs show "[EODHD] [OK] Success!"
5. ✓ Rate limit tracked (2/20 calls)

**Reports show:**
- Method: `EODHD_SPI_FUTURES` or `EODHD_FTSE_FUTURES`
- Confidence: 95%
- Source: EODHD

---

### State 2: EODHD Not Configured (No .env file)

**No .env file or API key not set**

**Pipeline behavior:**
1. ⚠ EODHDClient initialization skipped
2. → Falls back to Realtime Predictor (Australian)
3. → Falls back to Market Correlation (UK)
4. ✓ 75-85% confidence predictions
5. ✓ System continues working normally

**Reports show:**
- Method: `REALTIME` or `MARKET_CLOSE_CORRELATION`
- Confidence: 75-85%
- Source: Calculated

**System continues to function perfectly - just uses fallback methods!**

---

### State 3: EODHD Rate Limit Exceeded

**20 API calls used today (unlikely - only need 2!)**

**Pipeline behavior:**
1. ⚠ Rate limiter blocks API call
2. ✓ Uses cached data (if valid)
3. → Falls back to next method if cache expired
4. ✓ System continues working
5. ✓ Resets at midnight UTC

**Logs show:**
```
[EODHD] Rate limit exceeded! Resets in: 4h 23m
[REALTIME] Using actual US/UK market close data for prediction...
```

---

## Standalone Testing vs Pipeline Integration

### Standalone Test Scripts (Optional - For Testing Only)

**Purpose**: Verify EODHD configuration before running full pipeline

```bash
# Test configuration
python utils/secure_config.py

# Test EODHD API
python utils/eodhd_integration.py
```

**These are NOT needed for normal operation!**

---

### Pipeline Integration (Normal Operation)

**Purpose**: Run full trading pipeline (includes EODHD automatically)

```bash
# Run Australian pipeline (includes EODHD SPI 200 call)
python pipelines/run_au_pipeline.py

# Run UK pipeline (includes EODHD FTSE 100 call)
python pipelines/run_uk_pipeline.py
```

**EODHD calls happen automatically during pipeline execution!**

---

## Summary

### ✅ EODHD Calls ARE Part of Pipeline Runs

- **NOT** separate instances
- **NOT** standalone scripts
- **FULLY INTEGRATED** into market sentiment analysis
- **AUTOMATIC** when .env configured
- **TRANSPARENT** - logs show method used
- **GRACEFUL** - falls back if unavailable

### How It Works

1. You configure `.env` with EODHD API key (one time)
2. You run `python run_au_pipeline.py` (Australian market)
3. Pipeline automatically:
   - Initializes SPIMonitor
   - SPIMonitor initializes EODHDClient
   - EODHDClient fetches SPI 200 futures
   - Result flows through pipeline
4. Same for UK: `python run_uk_pipeline.py`
   - Initializes RealtimeFTSEPredictor
   - Predictor initializes EODHDClient
   - EODHDClient fetches FTSE 100 futures
   - Result flows through pipeline

### Daily API Usage

| Pipeline Run | EODHD Calls | When |
|-------------|-------------|------|
| Australian Morning | 1 (SPI 200) | 06:30 AM AEST |
| UK Pre-Market | 1 (FTSE 100) | 07:00 AM AEST |
| **Total** | **2 per day** | **10% of limit** |

**No separate EODHD script execution needed!**

---

**Version**: v193.11.7.6  
**Integration Status**: Complete  
**Execution Model**: Fully integrated into pipeline runners  
**User Action Required**: Configure .env file only
