# Endpoint Analysis and Fix Plan for Windows 11 Stock Tracker

## Current Situation Analysis

### Backend Available Endpoints (backend.py)
Based on the grep results, the backend currently provides these endpoints:
1. `GET /` - Root endpoint
2. `GET /api/stock/{symbol}` - Get real-time stock data ✅ WORKING
3. `GET /api/historical/{symbol}` - Get historical stock data ✅ WORKING  
4. `GET /api/indices` - Get market indices data ✅ WORKING

### Module Endpoint Usage

#### 1. CBA Enhanced Analysis Module (`cba_analysis_enhanced.html`)
- **Uses:**
  - `/api/stock/${CBA_SYMBOL}` ✅ EXISTS
  - `/api/historical/${CBA_SYMBOL}?period=1mo&interval=1d` ✅ EXISTS
- **Status:** Should work correctly

#### 2. Market Tracker Module (`market_tracker_final.html`)
- **Uses:**
  - `/api/stock/${market.symbol}` ✅ EXISTS
  - `/api/historical/${market.symbol}?period=${period}&interval=${interval}` ✅ EXISTS
- **Status:** Should work correctly

#### 3. Technical Analysis Module (`technical_analysis_enhanced.html`)
- **Uses:**
  - `/api/stock/${currentSymbol}` ✅ EXISTS
  - `/api/historical/${currentSymbol}?period=${period}&interval=${interval}` ✅ EXISTS
- **Status:** Should work correctly

#### 4. Prediction Centre Module (`prediction_centre_real_ml.html`)
- **Uses:**
  - `/api/stock/${symbol}` ✅ EXISTS
  - `/api/historical/${symbol}?period=${period}&interval=1d` ✅ EXISTS
  - `/api/predict` ❌ DOES NOT EXIST - This is the problem!
  - Also references `ML_BACKEND_URL` on port 8004 ❌ NOT RUNNING
- **Status:** Partially broken - prediction functionality won't work

#### 5. Landing Page (`index.html`)
- **Uses:**
  - `http://localhost:8002/` for status check ✅ EXISTS
- **Status:** Should work but may need adjustment

## Problems Identified

1. **Missing `/api/predict` endpoint** - The prediction module expects this but it doesn't exist in the backend
2. **ML Backend on port 8004** - Referenced but not running
3. **Missing `/api/status` endpoint** - Some modules may check this (based on user's screenshots)
4. **Missing Phase 4 endpoints** - `/api/phase4/predict`, `/api/phase4/backtest` don't exist
5. **Missing Document Upload Module** - No document uploader with FinBERT found in current deployment

## Fix Strategy

### Option 1: Quick Fix (Update Frontend Only)
- Remove or comment out calls to non-existent endpoints
- Use existing endpoints for basic functionality
- Disable advanced features temporarily

### Option 2: Complete Fix (Update Backend + Frontend)
- Add missing endpoints to backend
- Implement prediction functionality
- Add document upload capability
- Ensure all modules work with full functionality

### Option 3: Hybrid Approach (Recommended)
1. Fix connection status checks to use working endpoints
2. Create stub endpoints for missing functionality
3. Implement basic prediction using simple methods
4. Add document upload module
5. Gradually enhance with real ML models

## Immediate Actions Required

### 1. Fix Backend Status Checks
All modules should check `/api/stock/AAPL` or `/` instead of non-existent `/api/status`

### 2. Fix Prediction Module
Either:
- Add `/api/predict` endpoint to backend with simple prediction logic
- Update frontend to work without predictions
- Use historical data to show trend analysis instead

### 3. Add Missing Document Upload Module
Create a new module for document upload with FinBERT integration

### 4. Hardcode localhost:8002
Ensure ALL fetch calls use hardcoded `http://localhost:8002` not relative URLs

### 5. Remove ML Backend References
Update prediction module to use main backend on port 8002 only

## Implementation Priority

1. **Critical** - Fix backend status checks (prevents "Disconnected" errors)
2. **High** - Fix prediction module endpoints
3. **High** - Ensure CBA.AX shows real price ($170)
4. **Medium** - Add document upload module
5. **Low** - Add advanced ML features

## Next Steps

1. Update all modules to use correct endpoints
2. Add basic `/api/predict` endpoint to backend
3. Create document upload module
4. Test all modules with real data
5. Verify Windows 11 deployment works correctly