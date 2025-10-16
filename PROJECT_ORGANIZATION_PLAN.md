# Project Organization Plan

## Current Status
- Multiple iterations of the Stock Tracker (V1-V12)
- Various implementation attempts
- Core modules that must be preserved
- New ML enhancements ready for integration

## Organization Structure

### 1. Archive Directory (Historical Versions)
All previous iterations will be moved to `/archive/iterations/` for reference

### 2. Core Modules (To Keep)
- Enhanced CBA module
- Indices tracker (AORD, FTSE, S&P)
- Sentiment scraper
- Technical analysis
- Document uploader
- ML prediction & backtesting (unified)

### 3. Clean Deployment Structure
```
StockTracker_Production/
├── backend/
│   ├── ml_prediction_backtesting_unified.py
│   ├── indices_tracker_backend.py
│   ├── performance_tracker_backend.py
│   ├── ml_enhancements_based_on_research.py
│   └── cache_manager.py
├── frontend/
│   ├── index.html
│   ├── ml_dashboard.html
│   ├── cba_enhanced.html
│   ├── indices_tracker.html
│   └── technical_analysis.html
├── data/
│   ├── ml_models.db
│   ├── predictions.db
│   ├── historical_cache.db
│   └── backtest_results.db
├── requirements.txt
├── START_SYSTEM.bat
└── README.md
```

## Files to Archive
- All StockTracker_V* directories and zips
- Test files and diagnostic tools
- Duplicate backends
- Old deployment packages

## Git Strategy
1. Create archive branch for historical versions
2. Push all files to GitHub
3. Clean main branch for production
4. Tag important versions for easy retrieval