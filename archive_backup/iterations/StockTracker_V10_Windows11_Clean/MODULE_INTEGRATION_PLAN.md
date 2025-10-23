# Module Integration Plan - Complete Modular Architecture

## 🏗️ Current Architecture Status

### ✅ **Working Enhanced Backends (Ports 8000-8006)**
```
Port 8000: main_backend_integrated.py / orchestrator_backend.py
Port 8002: ml_backend_enhanced_finbert.py
Port 8003: finbert_backend.py  
Port 8004: historical_backend_sqlite.py
Port 8005: backtesting_enhanced.py
Port 8006: enhanced_global_scraper.py
```

### 🔍 **Discovered Original Modules That Need Integration**

## 📦 Original Module Categories

### 1. **CBA (Commonwealth Bank) Modules**
**Existing Files Found:**
- `cba_enhanced_prediction_system.py` - Full CBA prediction system
- `cba_specialist_server.py` - CBA specialist backend
- `cba_enhanced_api.py` - CBA API endpoints

**HTML Interfaces:**
- `cba_enhanced.html`
- `cba_analysis_enhanced_fixed.html`

**Features Needed:**
- ASX (Australian Stock Exchange) integration
- Banking sector correlation
- RBA (Reserve Bank of Australia) rate tracking
- Australian market specific analysis

### 2. **Indices Tracker Modules**
**HTML Interfaces:**
- `indices_tracker.html`
- `indices_tracker_fixed_times.html`

**Features Needed:**
- Real-time index data (S&P 500, NASDAQ, DOW, FTSE, DAX, Nikkei)
- Sector rotation analysis
- Global market correlation
- Market breadth indicators

### 3. **Social Sentiment Tracker**
**Existing File Found:**
- `social_sentiment_tracker.py`

**Integration Needed:**
- Reddit API integration
- Twitter/X sentiment
- StockTwits integration
- Social media trend analysis

### 4. **Performance Tracker**
**Existing Files Found:**
- `phase4_accuracy_tracker.py`
- `enhanced_performance_tracker.py`

**Features:**
- Model accuracy tracking
- Prediction performance metrics
- Historical accuracy analysis
- Performance degradation alerts

### 5. **Central Bank Integration**
**Referenced Import:**
- `central_bank_rate_integration.py`

**Features Needed:**
- Federal Reserve tracking
- ECB monitoring
- Bank of England updates
- RBA (Australia) integration
- Rate change predictions

## 🎯 Integration Architecture

### Proposed Port Allocation
```
Existing Services (8000-8006) - Keep as is
New Services:
Port 8007: indices_tracker_backend.py
Port 8008: cba_specialist_backend.py  
Port 8009: social_sentiment_backend.py
Port 8010: performance_tracker_backend.py
Port 8011: central_bank_backend.py
Port 8012: real_time_feed_backend.py (WebSocket)
```

## 📋 Implementation Plan

### Phase 1: Create Missing Core Backends

#### 1.1 Create `indices_tracker_backend.py` (Port 8007)
```python
Features:
- Real-time index data fetching
- Global indices: US, Europe, Asia, Australia
- Sector performance tracking
- Market breadth calculations
- Index correlation analysis
```

#### 1.2 Create `cba_specialist_backend.py` (Port 8008)
```python
Features:
- ASX data integration
- Australian banking sector analysis
- RBA rate impact modeling
- Commonwealth Bank specific metrics
- Regional market correlation
```

#### 1.3 Create `social_sentiment_backend.py` (Port 8009)
```python
Features:
- Reddit scraping (WSB, ASX_Bets, stocks)
- Twitter/X API integration
- StockTwits sentiment
- Trending ticker detection
- Sentiment momentum tracking
```

### Phase 2: Integration Layer

#### 2.1 Update `orchestrator_backend.py`
```python
# Add new service endpoints
SERVICES = {
    "ml": "http://localhost:8002",
    "finbert": "http://localhost:8003",
    "historical": "http://localhost:8004",
    "backtesting": "http://localhost:8005",
    "scraper": "http://localhost:8006",
    "indices": "http://localhost:8007",      # NEW
    "cba": "http://localhost:8008",          # NEW
    "social": "http://localhost:8009",       # NEW
    "performance": "http://localhost:8010",  # NEW
    "central_bank": "http://localhost:8011", # NEW
    "realtime": "ws://localhost:8012"        # NEW WebSocket
}
```

### Phase 3: Module HTML Updates

#### 3.1 Update Module References
Each HTML module needs to point to the correct backend:

```javascript
// Old (broken)
const API_URL = 'http://localhost:3000/api';

// New (fixed)
const API_ENDPOINTS = {
    ml: 'http://localhost:8002',
    indices: 'http://localhost:8007',
    cba: 'http://localhost:8008',
    social: 'http://localhost:8009'
};
```

### Phase 4: Create Module Registry

#### 4.1 `module_registry.json`
```json
{
  "modules": {
    "prediction_centre": {
      "versions": ["v1", "v2", "phase4", "fixed", "real_ml"],
      "current": "phase4_real",
      "backend": "ml",
      "port": 8002
    },
    "indices_tracker": {
      "versions": ["v1", "fixed_times"],
      "current": "fixed_times",
      "backend": "indices",
      "port": 8007
    },
    "cba_analysis": {
      "versions": ["enhanced", "fixed"],
      "current": "enhanced_fixed",
      "backend": "cba",
      "port": 8008
    }
  }
}
```

## 🚀 Deployment Strategy

### Option 1: Gradual Integration
1. Keep existing enhanced backends (8000-8006)
2. Add new backends one at a time
3. Test each integration independently
4. Update HTML modules incrementally

### Option 2: Complete Rebuild
1. Create all missing backends
2. Update all HTML modules
3. Full system test
4. Deploy as complete package

### Option 3: Hybrid Approach (Recommended)
1. Keep working enhanced backends
2. Create critical missing backends (indices, CBA)
3. Use module registry for version management
4. Implement WebSocket for real-time updates
5. Gradual migration of HTML modules

## 📝 Module Priority Matrix

| Priority | Module | Backend Status | Integration Complexity | Business Value |
|----------|--------|---------------|----------------------|----------------|
| P1 | Indices Tracker | Missing | Medium | High |
| P1 | CBA Analysis | Exists (needs update) | Low | High |
| P2 | Social Sentiment | Partial | High | Medium |
| P2 | Performance Tracker | Exists | Low | Medium |
| P3 | Central Bank | Missing | Medium | Medium |
| P3 | Real-time Feed | Missing | High | High |

## 🔧 Technical Requirements

### Backend Development
- FastAPI for all new services
- SQLite for caching (consistent with current)
- WebSocket support for real-time
- Redis for pub/sub (optional)

### Frontend Updates
- Update API endpoints in all HTML modules
- Add WebSocket client for real-time
- Implement module version switching
- Add error handling for service failures

### Testing Strategy
- Unit tests for each backend
- Integration tests for cross-service
- End-to-end tests for complete workflows
- Performance testing for real-time feeds

## 📊 Success Metrics

1. **All HTML modules functional** - No 404 errors
2. **Service response time** < 500ms for all endpoints
3. **Real-time latency** < 100ms for WebSocket
4. **Cache hit rate** > 80% for repeated queries
5. **Module loading time** < 2 seconds

## 🎯 Next Steps

1. **Immediate Priority:**
   - Create `indices_tracker_backend.py`
   - Update `cba_enhanced_prediction_system.py` for new architecture
   - Fix HTML module API endpoints

2. **Short Term (1 week):**
   - Implement social sentiment backend
   - Add WebSocket support
   - Create module registry

3. **Long Term (2 weeks):**
   - Complete all missing backends
   - Full HTML module migration
   - Performance optimization
   - Documentation update

## 📚 Module Documentation Needed

Each module needs:
1. API documentation
2. HTML interface guide
3. Backend service specs
4. Integration examples
5. Troubleshooting guide

This plan provides a complete roadmap for integrating all discovered modules into the enhanced modular architecture while maintaining the improvements you've already made (FinBERT, global sentiment, SQLite caching, etc.).