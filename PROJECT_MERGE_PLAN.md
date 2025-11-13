# Project Merge Plan - FinBERT v4.0 + Overnight Screener

**Date**: November 10, 2025  
**Goal**: Combine FinBERT v4.0 Paper Trading Platform with v4.4.4 Overnight Screener  
**Approach**: Copy FinBERT v4.0, integrate screener into it (non-destructive)  
**Status**: PLANNING PHASE

---

## 🎯 Project Overview

### Project A: FinBERT v4.0 Paper Trading Platform
**Package**: `FinBERT_v4.0_COMPLETE_Windows11_Package.zip` (232 KB, Nov 3)  
**Location**: `/home/user/webapp/FinBERT_v4.0_COMPLETE_Windows11_Package.zip`

**Features**:
- ✅ LSTM prediction engine
- ✅ FinBERT sentiment analysis
- ✅ Paper trading platform (virtual $10K)
- ✅ Backtesting framework
- ✅ Parameter optimization
- ✅ Portfolio management
- ✅ Chart visualization (candlesticks, indicators)
- ✅ Interactive web UI (Flask + HTML)
- ✅ Multi-timezone support (US, ASX, UK)
- ✅ Prediction database with validation
- ✅ **Working yfinance integration** (ticker.history() only)

**Architecture**:
```
FinBERT_v4.0/
├── app_finbert_v4_dev.py          # Main Flask app
├── config_dev.py                   # Configuration
├── models/
│   ├── lstm_predictor.py           # LSTM model
│   ├── finbert_sentiment.py        # Sentiment analysis
│   ├── news_sentiment_real.py      # News scraping
│   ├── prediction_manager.py       # Prediction lifecycle
│   ├── market_timezones.py         # Multi-timezone
│   ├── backtesting/                # Backtesting engine
│   │   ├── backtest_engine.py
│   │   ├── parameter_optimizer.py
│   │   └── portfolio_backtester.py
│   └── trading/                    # Paper trading
│       ├── paper_trading_engine.py
│       ├── trade_database.py
│       └── portfolio_manager.py
├── templates/
│   └── finbert_v4_enhanced_ui.html # Web interface
└── requirements-full.txt
```

---

### Project B: FinBERT v4.4.4 Overnight Screener
**Current**: Working directory (`/home/user/webapp`)

**Features**:
- ✅ Multi-sector stock screening (8 ASX sectors)
- ✅ Technical analysis (RSI, MA, volatility)
- ✅ Stock validation and scoring (0-100)
- ✅ SPI 200 futures monitoring
- ✅ US market indices tracking
- ✅ Batch prediction engine
- ✅ Opportunity scoring
- ✅ Morning report generation (HTML + charts)
- ✅ Email notifications
- ✅ Automated overnight pipeline
- ✅ **Fixed yfinance integration** (ticker.history() only)

**Architecture**:
```
v4.4.4_Screener/
├── models/
│   └── screening/
│       ├── stock_scanner.py            # Stock validation + analysis
│       ├── spi_monitor.py              # SPI futures + indices
│       ├── batch_predictor.py          # Mass predictions
│       ├── opportunity_scorer.py       # Ranking algorithm
│       ├── report_generator.py         # HTML reports
│       └── overnight_pipeline.py       # Orchestrator
├── scripts/
│   └── screening/
│       └── run_overnight_screener.py   # Entry point
├── models/config/
│   ├── asx_sectors.json                # 8 sectors, 200+ stocks
│   └── screening_config.json           # Screening parameters
└── reports/
    └── morning_reports/                # Generated reports
```

---

## 🎯 Merge Goals

### Primary Objectives:
1. **Unified Platform**: Single application with both prediction and screening
2. **Non-Destructive**: Keep both projects working independently during merge
3. **Code Reuse**: Leverage FinBERT v4.0's proven architecture
4. **Enhanced Features**: Combine strengths of both systems

### User Benefits:
- 🎯 **Single UI**: Access predictions, trading, AND screening from one interface
- 🎯 **Automated Workflow**: Overnight screening → morning predictions → trading decisions
- 🎯 **Better Predictions**: Use screener to find stocks → predict on best candidates
- 🎯 **Portfolio Integration**: Screen → Predict → Trade → Track (full lifecycle)
- 🎯 **Unified Data**: Share historical data, predictions, and screening results

---

## 📋 Merge Strategy

### Phase 1: Preparation (No Code Changes)
**Goal**: Analyze compatibility and plan integration  
**Duration**: Planning only

**Tasks**:
1. ✅ Document FinBERT v4.0 architecture
2. ✅ Document v4.4.4 Screener architecture
3. ✅ Identify integration points
4. ✅ Plan directory structure
5. ✅ Design unified data flow
6. ✅ Create merge checklist

**Deliverable**: This plan document

---

### Phase 2: Copy and Prepare (Non-Destructive)
**Goal**: Create merge workspace without breaking either project  
**Duration**: ~30 minutes

**Tasks**:
1. Copy FinBERT v4.0 to new directory: `finbert_v4_unified/`
2. Keep original v4.4.4 screener untouched
3. Verify FinBERT v4.0 runs independently in new location
4. Create integration branch: `finbert-v4-unified-development`

**Commands**:
```bash
cd /home/user/webapp
mkdir finbert_v4_unified
cd finbert_v4_unified
unzip ../FinBERT_v4.0_COMPLETE_Windows11_Package.zip
mv FinBERT_v4.0_COMPLETE_Windows11_Package/* .
rmdir FinBERT_v4.0_COMPLETE_Windows11_Package

# Test it still works
python app_finbert_v4_dev.py
```

**Deliverable**: Working copy of FinBERT v4.0 in new location

---

### Phase 3: Integration Architecture (Planning)
**Goal**: Design how components will work together  
**Duration**: Design only

#### Integration Points Identified:

**1. Stock Selection Integration**
```
Screener → FinBERT Predictor
Flow: Screen 40 stocks → Top 10 → Generate predictions
```

**2. Prediction Enhancement**
```
Technical Analysis → LSTM + Sentiment
Flow: Screener metrics → Enhanced prediction context
```

**3. Trading Integration**
```
Screen + Predict → Paper Trade
Flow: High-score stocks → Predictions → Trade signals
```

**4. Portfolio Integration**
```
Screener → Active Positions
Flow: Monitor holdings with screening scores
```

**5. UI Integration**
```
Single Interface: Predictions + Screening + Trading
New Tab: "Overnight Screening" in FinBERT UI
```

---

### Phase 4: Module Integration (Coding Starts)
**Goal**: Copy screener modules into FinBERT v4.0 structure  
**Duration**: ~1-2 hours

#### Step 4.1: Copy Screening Modules
```bash
cd /home/user/webapp/finbert_v4_unified

# Create screening directory structure
mkdir -p models/screening
mkdir -p models/config

# Copy screening modules (FIXED versions)
cp ../models/screening/stock_scanner.py models/screening/
cp ../models/screening/spi_monitor.py models/screening/
cp ../models/screening/batch_predictor.py models/screening/
cp ../models/screening/opportunity_scorer.py models/screening/
cp ../models/screening/report_generator.py models/screening/
cp ../models/screening/overnight_pipeline.py models/screening/
cp ../models/screening/__init__.py models/screening/

# Copy configuration
cp ../models/config/asx_sectors.json models/config/
cp ../models/config/screening_config.json models/config/

# Copy screening scripts
mkdir -p scripts/screening
cp ../scripts/screening/*.py scripts/screening/
```

#### Step 4.2: Update Imports
Modify screener modules to work with FinBERT v4.0 structure:
- Update relative imports
- Use FinBERT's existing prediction_manager
- Share database connections
- Reuse chart generation utilities

#### Step 4.3: Resolve Dependencies
```python
# screening modules will use:
from models.prediction_manager import PredictionManager  # Already exists
from models.lstm_predictor import lstm_predictor        # Already exists
from models.finbert_sentiment import finbert_analyzer   # Already exists
```

**Deliverable**: Screener modules copied and import-compatible

---

### Phase 5: Unified Data Layer (Coding)
**Goal**: Share data between systems  
**Duration**: ~1 hour

#### Database Schema Extension:
```sql
-- Extend existing prediction_database.py

-- New table: screening_results
CREATE TABLE screening_results (
    id INTEGER PRIMARY KEY,
    scan_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    sector TEXT,
    price REAL,
    volume INTEGER,
    screening_score REAL,
    technical_indicators TEXT,  -- JSON
    timestamp TEXT
);

-- New table: overnight_reports
CREATE TABLE overnight_reports (
    id INTEGER PRIMARY KEY,
    report_date TEXT NOT NULL,
    total_stocks INTEGER,
    validated_stocks INTEGER,
    top_opportunities TEXT,  -- JSON
    market_sentiment TEXT,
    report_path TEXT,
    timestamp TEXT
);
```

#### Shared Data Manager:
```python
# models/unified_data_manager.py (NEW)
class UnifiedDataManager:
    """Manages data for both predictions and screening"""
    
    def __init__(self):
        self.prediction_db = PredictionDatabase()  # Existing
        self.screening_db = ScreeningDatabase()    # New
    
    def get_stock_complete_info(self, symbol):
        """Get predictions + screening data"""
        return {
            'prediction': self.prediction_db.get_prediction(symbol),
            'screening': self.screening_db.get_screening_result(symbol)
        }
```

**Deliverable**: Unified database with screening tables

---

### Phase 6: UI Integration (Coding)
**Goal**: Add screening to FinBERT web interface  
**Duration**: ~2 hours

#### New UI Components:

**1. New Tab: "Overnight Screening"**
```html
<!-- Add to templates/finbert_v4_enhanced_ui.html -->

<div class="tab-button" onclick="showTab('screening')">
    📊 Overnight Screening
</div>

<div id="screening-tab" class="tab-content">
    <h2>Overnight Screening Results</h2>
    
    <!-- Screening Controls -->
    <div class="screening-controls">
        <button onclick="runScreening()">Run Screening Now</button>
        <button onclick="viewLastReport()">View Last Report</button>
        <button onclick="scheduleScan()">Schedule Overnight</button>
    </div>
    
    <!-- Screening Results Table -->
    <table id="screening-results">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Symbol</th>
                <th>Sector</th>
                <th>Score</th>
                <th>Price</th>
                <th>RSI</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="screening-results-body">
            <!-- Populated by JavaScript -->
        </tbody>
    </table>
    
    <!-- Market Overview -->
    <div class="market-overview">
        <h3>Market Sentiment</h3>
        <div id="spi-status"></div>
        <div id="us-markets"></div>
    </div>
</div>
```

**2. New API Endpoints**
```python
# Add to app_finbert_v4_dev.py

@app.route('/api/screening/run', methods=['POST'])
def run_screening():
    """Run overnight screening"""
    pipeline = OvernightPipeline()
    results = pipeline.run()
    return jsonify(results)

@app.route('/api/screening/results', methods=['GET'])
def get_screening_results():
    """Get latest screening results"""
    db = UnifiedDataManager()
    results = db.screening_db.get_latest_results()
    return jsonify(results)

@app.route('/api/screening/predict', methods=['POST'])
def screening_to_prediction():
    """Generate predictions for screened stocks"""
    symbols = request.json.get('symbols', [])
    predictions = []
    for symbol in symbols:
        pred = prediction_manager.get_daily_eod_prediction(symbol)
        predictions.append(pred)
    return jsonify(predictions)
```

**3. Integration Actions**
```javascript
// New JavaScript functions

function runScreening() {
    showLoadingOverlay('Running overnight screening...');
    fetch('/api/screening/run', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
            hideLoadingOverlay();
            displayScreeningResults(data);
        });
}

function predictOnScreened(symbol) {
    // Generate prediction for screened stock
    // Pre-fill prediction form with symbol
    showTab('predictions');
    document.getElementById('symbol-input').value = symbol;
    generatePrediction();
}

function tradeOnScreened(symbol) {
    // Open paper trading modal with screened stock
    showTab('trading');
    document.getElementById('trade-symbol').value = symbol;
    fetchCurrentPrice(symbol);
}
```

**Deliverable**: Full UI integration with new screening tab

---

### Phase 7: Unified Workflow (Coding)
**Goal**: Automated end-to-end workflow  
**Duration**: ~1 hour

#### Automated Pipeline:
```python
# models/unified_pipeline.py (NEW)

class UnifiedPipeline:
    """Orchestrates screening → prediction → trading workflow"""
    
    def __init__(self):
        self.screener = StockScanner()
        self.predictor = PredictionManager()
        self.trader = PaperTradingEngine()
        self.data = UnifiedDataManager()
    
    def run_overnight_workflow(self):
        """
        Complete overnight automation:
        1. Screen stocks (40 stocks → top 10)
        2. Generate predictions (10 stocks)
        3. Identify trade opportunities (top 3)
        4. Optional: Execute paper trades
        5. Generate morning report
        """
        
        # Step 1: Screen
        logger.info("Step 1: Screening stocks...")
        screening_results = self.screener.scan_all_sectors(top_n=10)
        
        # Step 2: Predict on top stocks
        logger.info("Step 2: Generating predictions...")
        predictions = {}
        for sector, stocks in screening_results.items():
            for stock in stocks[:3]:  # Top 3 per sector
                symbol = stock['symbol']
                pred = self.predictor.get_daily_eod_prediction(symbol)
                predictions[symbol] = pred
        
        # Step 3: Score opportunities
        logger.info("Step 3: Scoring opportunities...")
        opportunities = self._score_opportunities(
            screening_results, 
            predictions
        )
        
        # Step 4: Generate report
        logger.info("Step 4: Generating report...")
        report = self._generate_unified_report(
            screening_results,
            predictions,
            opportunities
        )
        
        return {
            'screening': screening_results,
            'predictions': predictions,
            'opportunities': opportunities,
            'report': report
        }
    
    def _score_opportunities(self, screening, predictions):
        """
        Combine screening score + prediction confidence
        Formula: (screening_score * 0.4) + (prediction_confidence * 0.6)
        """
        opportunities = []
        
        for sector, stocks in screening.items():
            for stock in stocks:
                symbol = stock['symbol']
                pred = predictions.get(symbol)
                
                if pred:
                    combined_score = (
                        stock['score'] * 0.4 +
                        pred['confidence'] * 0.6
                    )
                    
                    opportunities.append({
                        'symbol': symbol,
                        'sector': sector,
                        'screening_score': stock['score'],
                        'prediction': pred['prediction'],
                        'confidence': pred['confidence'],
                        'combined_score': combined_score,
                        'price': stock['price']
                    })
        
        # Sort by combined score
        opportunities.sort(key=lambda x: x['combined_score'], reverse=True)
        return opportunities[:10]  # Top 10
```

**Deliverable**: Automated screening → prediction workflow

---

### Phase 8: Enhanced Reporting (Coding)
**Goal**: Unified morning report  
**Duration**: ~1 hour

#### New Report Structure:
```
Morning Report (HTML)
├── Market Overview
│   ├── SPI 200 Futures
│   ├── US Markets (S&P, Nasdaq, Dow)
│   └── Market Sentiment
│
├── Screening Results
│   ├── Top Opportunities (10 stocks)
│   ├── By Sector (8 sectors)
│   └── Technical Summary
│
├── Predictions
│   ├── Daily EOD Predictions (10 stocks)
│   ├── Confidence Levels
│   └── Target Prices
│
├── Combined Analysis
│   ├── Best Trade Opportunities (top 3)
│   ├── Screening + Prediction alignment
│   └── Risk Assessment
│
└── Portfolio Status (if paper trading active)
    ├── Current Positions
    ├── Today's Predictions for Holdings
    └── Recommended Actions
```

**Deliverable**: Enhanced HTML report with all features

---

### Phase 9: Testing (Validation)
**Goal**: Verify everything works together  
**Duration**: ~1 hour

#### Test Suite:
```python
# tests/test_unified_system.py (NEW)

def test_screening_module():
    """Test screener works in unified app"""
    scanner = StockScanner()
    results = scanner.scan_sector('Technology', top_n=5)
    assert len(results) > 0
    assert 'score' in results[0]

def test_prediction_module():
    """Test predictions work in unified app"""
    predictor = PredictionManager()
    pred = predictor.get_daily_eod_prediction('CBA.AX')
    assert pred is not None
    assert 'prediction' in pred

def test_unified_pipeline():
    """Test complete workflow"""
    pipeline = UnifiedPipeline()
    results = pipeline.run_overnight_workflow()
    assert 'screening' in results
    assert 'predictions' in results
    assert 'opportunities' in results

def test_data_sharing():
    """Test data flows between systems"""
    data = UnifiedDataManager()
    info = data.get_stock_complete_info('CBA.AX')
    assert 'prediction' in info
    assert 'screening' in info

def test_ui_endpoints():
    """Test all API endpoints"""
    # Test screening endpoints
    # Test prediction endpoints
    # Test unified workflow endpoints
```

**Deliverable**: Passing test suite

---

### Phase 10: Documentation (Final)
**Goal**: Complete user documentation  
**Duration**: ~30 minutes

#### Documents to Create:
1. `UNIFIED_SYSTEM_README.md` - Overview
2. `INTEGRATION_GUIDE.md` - How systems work together
3. `USER_GUIDE_UNIFIED.md` - Using all features
4. `API_REFERENCE.md` - All endpoints
5. `DEPLOYMENT_UNIFIED.md` - Installation guide

**Deliverable**: Complete documentation

---

## 📊 Merged System Architecture

### Directory Structure:
```
finbert_v4_unified/
├── app_finbert_v4_dev.py          # Main Flask app (EXTENDED)
├── config_dev.py                   # Configuration (EXTENDED)
│
├── models/
│   ├── lstm_predictor.py           # From v4.0
│   ├── finbert_sentiment.py        # From v4.0
│   ├── news_sentiment_real.py      # From v4.0
│   ├── prediction_manager.py       # From v4.0
│   ├── market_timezones.py         # From v4.0
│   │
│   ├── screening/                  # FROM v4.4.4 (NEW)
│   │   ├── stock_scanner.py        # Fixed version
│   │   ├── spi_monitor.py          # Fixed version
│   │   ├── batch_predictor.py
│   │   ├── opportunity_scorer.py
│   │   ├── report_generator.py
│   │   └── overnight_pipeline.py
│   │
│   ├── backtesting/                # From v4.0
│   │   ├── backtest_engine.py
│   │   ├── parameter_optimizer.py
│   │   └── portfolio_backtester.py
│   │
│   ├── trading/                    # From v4.0
│   │   ├── paper_trading_engine.py
│   │   ├── trade_database.py
│   │   └── portfolio_manager.py
│   │
│   ├── unified_data_manager.py     # NEW
│   └── unified_pipeline.py         # NEW
│
├── templates/
│   └── finbert_v4_enhanced_ui.html # EXTENDED with screening
│
├── scripts/
│   └── screening/                  # From v4.4.4
│       └── run_overnight_screener.py
│
├── models/config/
│   ├── asx_sectors.json            # From v4.4.4
│   └── screening_config.json       # From v4.4.4
│
├── reports/
│   ├── morning_reports/            # From v4.4.4
│   └── backtesting/                # From v4.0
│
├── tests/
│   └── test_unified_system.py      # NEW
│
└── requirements_unified.txt        # MERGED
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Web UI)                   │
│  ┌──────────┬───────────┬────────────┬──────────┬─────────┐│
│  │Prediction│ Screening │ Backtesting│  Trading │Portfolio││
│  └──────────┴───────────┴────────────┴──────────┴─────────┘│
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌─────────┐
    │ Flask  │  │ Flask  │  │  Flask  │
    │  API   │  │  API   │  │   API   │
    │Predict │  │Screening│  │ Trading │
    └────┬───┘  └────┬───┘  └────┬────┘
         │           │           │
         └───────────┼───────────┘
                     ▼
         ┌───────────────────────┐
         │  Unified Data Manager │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌────────┐     ┌──────────┐     ┌─────────┐
│Predict │     │Screening │     │ Trading │
│Database│     │ Database │     │Database │
└────────┘     └──────────┘     └─────────┘
    
    
OVERNIGHT WORKFLOW:
    
    Screen 40 Stocks
         │
         ▼
    Top 10 by Score
         │
         ▼
    Generate Predictions
         │
         ▼
    Score Opportunities
         │
         ▼
    Morning Report
```

---

## 🎯 Feature Matrix

### What Each System Provides:

| Feature | FinBERT v4.0 | Screener v4.4.4 | Unified System |
|---------|--------------|-----------------|----------------|
| **LSTM Predictions** | ✅ Single stock | ❌ | ✅ Batch on screened |
| **FinBERT Sentiment** | ✅ | ❌ | ✅ Enhanced with screening |
| **Stock Screening** | ❌ | ✅ 40 stocks | ✅ Full integration |
| **Technical Analysis** | ⚠️ Basic | ✅ Advanced | ✅ Combined |
| **Paper Trading** | ✅ | ❌ | ✅ With screening scores |
| **Backtesting** | ✅ | ❌ | ✅ Full |
| **Portfolio Tracking** | ✅ | ❌ | ✅ Enhanced |
| **Morning Reports** | ❌ | ✅ | ✅ Enhanced |
| **Web UI** | ✅ | ❌ | ✅ Unified |
| **Multi-timezone** | ✅ | ⚠️ Basic | ✅ Full |
| **Overnight Automation** | ❌ | ✅ | ✅ Complete |
| **SPI Futures** | ❌ | ✅ | ✅ |
| **Opportunity Scoring** | ❌ | ✅ | ✅ Enhanced |

---

## 🚀 Unified System Benefits

### For User:

**1. Complete Workflow**
```
Evening:   Schedule overnight screening
Overnight: Screen 40 → Predict top 10 → Score opportunities
Morning:   Review report → Make trading decisions → Track portfolio
```

**2. Single Interface**
- One web UI for everything
- No switching between applications
- Unified data and reports
- Consistent user experience

**3. Better Decisions**
- Screening finds best candidates
- Predictions provide direction
- Combined scoring reduces risk
- Portfolio tracking shows results

**4. Automation**
- Set it and forget it
- Wake up to analysis
- Ready-to-trade opportunities
- Daily performance tracking

### For System:

**1. Code Reuse**
- Share yfinance integration (ticker.history() only)
- Single prediction engine
- Unified database
- Common utilities

**2. Data Synergy**
- Screening informs predictions
- Predictions enhance trading
- Trading validates predictions
- Feedback loop improves all

**3. Maintainability**
- Single codebase
- Shared dependencies
- Unified testing
- Easier updates

---

## ⚠️ Integration Challenges & Solutions

### Challenge 1: Different Database Schemas
**Problem**: v4.0 has prediction_database, v4.4.4 uses JSON files

**Solution**:
- Create UnifiedDataManager
- Extend prediction_database with screening tables
- Migrate JSON to SQLite
- Maintain backward compatibility

### Challenge 2: Different yfinance Patterns
**Problem**: Both use ticker.history() but different data processing

**Solution**:
- Use v4.4.4's fixed pattern (already proven)
- Update v4.0 components to match
- Share common data fetching utilities
- Standardize on working pattern

### Challenge 3: UI Integration
**Problem**: v4.0 has complex UI, screener is CLI-only

**Solution**:
- Add new tab to existing UI
- Use existing chart libraries
- Maintain UI consistency
- Progressive enhancement

### Challenge 4: Configuration Management
**Problem**: Different config files and formats

**Solution**:
- Merge into single config_dev.py
- Keep sector configs as JSON
- Environment-based settings
- Validation on startup

### Challenge 5: Import Dependencies
**Problem**: Circular imports possible

**Solution**:
- Careful module organization
- Dependency injection
- Clear separation of concerns
- Proper __init__.py files

---

## 📋 Pre-Merge Checklist

### Before Starting Code:
- [ ] Both projects working independently
- [ ] FinBERT v4.0 package extracted
- [ ] v4.4.4 screener with ticker.history() fix
- [ ] Test environment prepared
- [ ] Git branch created
- [ ] Backup of both projects
- [ ] This plan reviewed and approved

### Requirements:
- [ ] Python 3.8-3.12
- [ ] All dependencies for both projects
- [ ] 500 MB disk space
- [ ] Access to both project directories

---

## 🎯 Success Criteria

### Merge is Successful When:
1. ✅ Both systems work independently
2. ✅ Screener accessible from FinBERT UI
3. ✅ Predictions work on screened stocks
4. ✅ Paper trading uses screening scores
5. ✅ Unified reports generated
6. ✅ All tests passing
7. ✅ No breaking changes to either system
8. ✅ Single deployment package works
9. ✅ Documentation complete
10. ✅ User can run complete workflow

---

## 📅 Estimated Timeline

### Total Time: ~8-10 hours (spread over multiple sessions)

| Phase | Duration | Type |
|-------|----------|------|
| 1. Preparation | Complete | Planning |
| 2. Copy & Prepare | 30 min | Setup |
| 3. Architecture | 1 hour | Planning |
| 4. Module Integration | 1-2 hours | Coding |
| 5. Data Layer | 1 hour | Coding |
| 6. UI Integration | 2 hours | Coding |
| 7. Workflow | 1 hour | Coding |
| 8. Reporting | 1 hour | Coding |
| 9. Testing | 1 hour | Validation |
| 10. Documentation | 30 min | Documentation |

---

## 🚦 When to Start

### Prerequisites:
1. ✅ Current screener fix verified working
2. ✅ FinBERT v4.0 package available
3. ✅ User approval of this plan
4. ✅ Time allocated for merge work

### User Decision Point:
**"Are you ready to proceed with the merge, or do you want to use the systems separately for now?"**

Options:
- **A**: Start merge now (begin Phase 2)
- **B**: Test screener fix for a few days first
- **C**: Use separately, merge later
- **D**: Modify plan before proceeding

---

## 📝 Notes

### Important Principles:
1. **Non-Destructive**: Keep originals safe
2. **Incremental**: Test after each phase
3. **Reversible**: Can rollback anytime
4. **Documented**: Track all changes
5. **Tested**: Verify at every step

### Risk Mitigation:
- Work in separate directory
- Keep git commits small
- Test frequently
- Maintain backups
- Document issues

---

## 🎯 Final Deliverable

### When Complete:
```
finbert_v4_unified/
├── Complete FinBERT v4.0 features
├── Complete v4.4.4 Screener features
├── Unified web interface
├── Automated overnight workflow
├── Enhanced morning reports
├── Single deployment package
└── Complete documentation
```

**One application, all features, seamless integration.**

---

**Status**: ✅ **PLAN COMPLETE - READY FOR USER APPROVAL**

**Next Step**: User decides when to start Phase 2 (Copy and Prepare)
