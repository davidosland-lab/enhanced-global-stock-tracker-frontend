# Component Documentation

## Backend Components

### backend_fixed.py
**Purpose**: Core API server providing real-time and historical market data  
**Location**: `/home/user/webapp/backend_fixed.py`  
**Status**: PROTECTED - Do not modify without backup  

**Key Features**:
- Real-time quote endpoint with percentage calculations
- Historical data endpoint with configurable periods
- Batch quote processing for multiple symbols
- Market status checking
- CORS configuration for localhost access

**Critical Code Sections**:
```python
# Line 87-119: Percentage calculation logic
change_percent = ((latest_price - prev_close) / prev_close) * 100

# Line 228-260: Historical data endpoint
@app.get("/api/historical/{symbol}")
# Returns nested format: {symbol, period, data: [...]}
```

## Frontend Modules

### Market Tracking Modules

#### market_periods_working_chart.html
**Purpose**: Primary market visualization with three-zone display  
**Location**: `/modules/market-tracking/market_periods_working_chart.html`  
**Status**: Production - Final working version  

**Features**:
- Displays ASX (red), European (blue), US (purple) market zones
- Real-time updates every 30 seconds
- Handles nested backend response format correctly
- AEST time display for all markets

**Key Functions**:
- `fetchMarketData()`: Fetches and processes market data
- `updateChart()`: Renders Chart.js visualization
- `formatTime()`: Converts to AEST display

#### market_periods_custom_periods.html
**Purpose**: Enhanced version with custom period selector  
**Location**: `/modules/market-tracking/market_periods_custom_periods.html`  

**Features**:
- "Today", "Yesterday", "Past 7 Days" period selector
- Dynamic period calculation based on AEST
- Maintains three-zone market visualization

#### global_indices_tracker_sandbox_fixed.html
**Purpose**: Development version with debugging features  
**Location**: `/modules/market-tracking/global_indices_tracker_sandbox_fixed.html`  

**Features**:
- Console logging for debugging
- Error boundary implementation
- Test mode for development

### Analysis Modules

#### cba_analysis.html
**Purpose**: Detailed analysis for Commonwealth Bank (CBA.AX)  
**Location**: `/modules/analysis/cba_analysis.html`  

**Features**:
- Technical indicators
- Volume analysis
- Price trend visualization
- Moving averages

### Prediction Modules

#### ml_predictions.html
**Purpose**: Machine learning based market predictions  
**Location**: `/modules/predictions/ml_predictions.html`  

**Features**:
- Trend prediction visualization
- Confidence intervals
- Historical accuracy tracking

### Document Management

#### document_center.html
**Purpose**: Central hub for project documentation  
**Location**: `/modules/documents/document_center.html`  

**Features**:
- Document listing
- Quick links to all modules
- Version history tracking

## Shared Components

### Chart.js Configuration
**Used By**: All visualization modules  
**Version**: Chart.js 3.x with annotation plugin  

**Standard Configuration**:
```javascript
{
    type: 'line',
    options: {
        responsive: true,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
            annotation: { annotations: {...} },
            legend: { position: 'top' }
        },
        scales: {
            x: { type: 'time', time: { unit: 'hour' } },
            y: { position: 'left', title: { text: 'Price (AUD)' } },
            y1: { position: 'right', title: { text: 'Change (%)' } }
        }
    }
}
```

### API Integration Pattern
**Used By**: All frontend modules  

**Standard Fetch Pattern**:
```javascript
async function fetchData(symbol, period) {
    try {
        const response = await fetch(`http://localhost:8002/api/historical/${symbol}?period=${period}`);
        const result = await response.json();
        const data = result.data || result; // Handle nested response
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}
```

## Module Dependencies

### External Libraries
- **Chart.js 3.x**: Core charting library
- **chartjs-adapter-date-fns**: Date handling for Chart.js
- **chartjs-plugin-annotation**: Market zone annotations

### Internal Dependencies
- All modules depend on `backend_fixed.py` API endpoints
- Market tracking modules share common chart configurations
- Analysis modules may reference market tracking data

## Configuration Files

### CORS Settings
**Location**: `backend_fixed.py` lines 35-41  
**Allowed Origins**: `http://localhost:*`

### API Endpoints
- `/api/quote/{symbol}`: Real-time quotes
- `/api/historical/{symbol}`: Historical data
- `/api/batch`: Multiple symbol quotes
- `/api/market-status`: Market open/close status

## Testing Considerations
- All modules must work with hardcoded `http://localhost:8002`
- Test with real ASX symbols (e.g., CBA.AX, BHP.AX)
- Verify percentage calculations match Yahoo Finance
- Ensure AEST time display is accurate
- Test all period selections (Today/Yesterday/7 Days)