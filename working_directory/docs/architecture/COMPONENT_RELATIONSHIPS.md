# Component Relationships and Links

## System Component Map

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend Modules                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Market Tracking                Analysis            Predictions│
│  ┌─────────────┐               ┌─────────────┐    ┌──────────┐│
│  │Market Periods├───────────────>CBA Analysis │    │ML Predict││
│  │(Working)     │               └─────────────┘    └──────────┘│
│  └──────┬───────┘                      ^                  ^    │
│         │                              │                  │    │
│  ┌──────▼───────┐                      │                  │    │
│  │Custom Periods│                      │                  │    │
│  └──────┬───────┘                      │                  │    │
│         │                              │                  │    │
│  ┌──────▼───────┐                      │                  │    │
│  │Global Indices├──────────────────────┴──────────────────┘    │
│  └──────┬───────┘                                              │
│         │                                                      │
│  ┌──────▼───────┐                                              │
│  │Single Stock  │                                              │
│  └──────────────┘                                              │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                        API Layer                              │
│                    backend_fixed.py                           │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  /api/quote/{symbol}     -> Real-time data           │    │
│  │  /api/historical/{symbol} -> Historical data         │    │
│  │  /api/batch              -> Multiple symbols         │    │
│  │  /api/market-status      -> Market hours             │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Module Dependencies

### 1. Market Periods Working Chart
**File**: `/modules/market-tracking/market_periods_working_chart.html`

**Depends On**:
- `backend_fixed.py` - `/api/historical/{symbol}` endpoint
- Chart.js 3.x library
- chartjs-plugin-annotation for market zones

**Used By**:
- Document Center (as primary market view)
- Referenced by Custom Periods module as base

**Data Flow**:
1. Fetches ASX (^AORD), FTSE (^FTSE), S&P (^GSPC) data
2. Processes nested response format `{data: [...], symbol}`
3. Renders combined chart with three market zones

### 2. Market Periods Custom Periods
**File**: `/modules/market-tracking/market_periods_custom_periods.html`

**Extends**: Market Periods Working Chart
**Enhancement**: Adds period selector (Today/Yesterday/Past 7 Days)

**Additional Dependencies**:
- Date calculation functions for AEST
- Period state management

### 3. Global Indices Tracker
**File**: `/modules/market-tracking/global_indices_tracker_sandbox_fixed.html`

**Depends On**:
- `backend_fixed.py` - `/api/batch` endpoint
- `/api/quote/{symbol}` for real-time updates

**Provides Data To**:
- CBA Analysis (market context)
- ML Predictions (market indicators)

### 4. CBA Analysis
**File**: `/modules/analysis/cba_analysis.html`

**Depends On**:
- `backend_fixed.py` - `/api/historical/CBA.AX`
- Market tracking modules for context

**Relationships**:
- Receives market context from Global Indices
- Provides analysis data to ML Predictions

### 5. ML Predictions
**File**: `/modules/predictions/ml_predictions.html`

**Depends On**:
- Historical data from backend
- Analysis results from CBA Analysis
- Market indicators from Global Indices

## API Endpoint Usage Matrix

| Module | /api/quote | /api/historical | /api/batch | /api/market-status |
|--------|------------|-----------------|------------|-------------------|
| Market Periods Working | ❌ | ✅ | ❌ | ❌ |
| Custom Periods | ❌ | ✅ | ❌ | ❌ |
| Global Indices | ✅ | ✅ | ✅ | ✅ |
| Single Stock | ✅ | ✅ | ❌ | ❌ |
| CBA Analysis | ✅ | ✅ | ❌ | ❌ |
| ML Predictions | ❌ | ✅ | ❌ | ❌ |

## Shared Functions and Utilities

### Time Handling Functions
**Used By**: All market tracking modules
```javascript
function toAEST(date) {
    // Convert UTC to Australian Eastern Time
}

function formatTime(date) {
    // Format time for display
}
```

### Data Processing Functions
**Shared Between**: All visualization modules
```javascript
function processHistoricalData(data) {
    // Extract and format data for charts
}

function calculatePercentageChange(current, previous) {
    // Standard percentage calculation
}
```

### Chart Configuration Templates
**Base Configuration**: Used by all chart modules
```javascript
const baseChartConfig = {
    type: 'line',
    options: {
        responsive: true,
        interaction: { intersect: false }
    }
}
```

## Inter-Module Communication

### Direct Links
1. **Document Center** → All modules (navigation hub)
2. **Market Periods** → Custom Periods (extends functionality)
3. **Global Indices** → Analysis modules (provides context)

### Data Sharing Patterns
1. **Market Context**: Global indices provide market state to analysis
2. **Historical Patterns**: Analysis modules share patterns with predictions
3. **Time Synchronization**: All modules use AEST for consistency

## Configuration Dependencies

### Backend Configuration
**File**: `backend_fixed.py`
- CORS settings affect all frontend modules
- Cache timeout (5 minutes) impacts all data requests
- Port 8002 hardcoded in all module URLs

### Frontend Configuration
**Shared Settings**:
- Update interval: 30 seconds (all real-time modules)
- Chart colors: ASX (red), FTSE (blue), S&P (purple)
- Time zone: AEST for all displays

## Module Loading Order

### Recommended Initialization Sequence
1. **Backend**: Start `backend_fixed.py` first
2. **Document Center**: Load as main navigation
3. **Market Periods**: Initialize primary market view
4. **Global Indices**: Start real-time tracking
5. **Analysis/Predictions**: Load on demand

## Error Propagation

### Error Handling Chain
1. **Backend Error** → Returns error JSON
2. **Frontend Catch** → Logs to console
3. **User Notification** → Shows error message
4. **Fallback** → Retries or shows cached data

## Performance Considerations

### Resource Sharing
- Chart.js instances share rendering context
- API calls can be batched using `/api/batch`
- 5-minute backend cache reduces Yahoo Finance calls
- 30-second update interval synchronized across modules

## Module Evolution Path

### Version Progression
1. `global_indices_tracker.html` (v1 - basic)
2. `global_indices_tracker_enhanced.html` (v2 - improved)
3. `global_indices_tracker_realdata_only.html` (v3 - no synthetic)
4. `global_indices_tracker_sandbox_fixed.html` (v4 - debugging)
5. `market_periods_*.html` (v5 - market zones)

### Future Integration Points
- WebSocket support for real-time updates
- Shared state management system
- Module plugin architecture
- Cross-module event system