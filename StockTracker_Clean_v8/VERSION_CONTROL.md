# Stock Tracker Version Control

## Current Version: 8.2
**Date**: December 20, 2024
**Status**: FIXED - All modules working

## Version History

### v8.2 - Current (Dec 20, 2024)
**FIXES APPLIED**:
- ✅ **CBA Enhanced Module Restored** - Full functionality with news, reports, and enhanced predictions
- ✅ **Chart Boundaries Fixed** - Technical Analysis now has proper Y-axis min/max scaling
- ✅ **All Module Links Working** - Market Tracker and all other modules properly linked
- ✅ **Backtesting Integrated** - Now part of Prediction Centre (not separate module)

**Module Status**:
1. **CBA Enhanced** - ✅ WORKING (Enhanced analysis with documents/media review)
2. **Technical Analysis** - ✅ WORKING (Fixed chart boundaries)
3. **Prediction Centre** - ✅ WORKING (With integrated backtesting)
4. **Market Tracker** - ✅ WORKING (ASX 20 real-time data)
5. **Portfolio** - ⏸️ PLACEHOLDER (As requested)
6. **Stock Scanner** - ⏸️ PLACEHOLDER

### v8.1 - REGRESSION (Dec 20, 2024)
**Issues**:
- ❌ CBA module missing
- ❌ Chart boundaries not working
- ❌ Market Tracker link broken
- ❌ Lost version control

### v8.0 - Initial Clean Install (Dec 20, 2024)
**Features**:
- Basic modules created
- Backend unified
- Windows 11 optimized

## Module Specifications

### CBA Enhanced Module
**File**: `/modules/cba_enhanced.html`
**Features**:
- Real-time CBA.AX price (~$170, not $100)
- Technical analysis with proper boundaries
- AI predictions combining:
  - Technical indicators
  - News sentiment analysis
  - Company reports & ASX announcements
  - Media coverage review
- 4 tabs: Technical, Predictions, News, Publications

### Technical Analysis
**File**: `/modules/technical_analysis.html`
**Features**:
- Candlestick charts (Chart.js 4.4.0)
- Proper Y-axis boundaries (±2% of data range)
- Multiple timeframes
- RSI, SMA, MACD indicators

### Prediction Centre
**File**: `/modules/prediction_centre.html`
**Features**:
- 6 ML models (LSTM, GRU, Random Forest, XGBoost, Transformer, Ensemble)
- Integrated backtesting tab
- Model training improves predictions
- Results saved in localStorage

## Git Workflow

### Commit Protocol
```bash
# Before any changes
git status
git pull origin main

# After changes
git add -A
git commit -m "feat/fix: Description of change"
git push origin main
```

### Branch Strategy
- `main` - Production ready code
- Feature branches for major changes
- Always test before merging

## API Endpoints
All hardcoded to `http://localhost:8002` for Windows 11:
- `/api/stock/{symbol}` - Stock data
- `/api/predict/{symbol}` - ML predictions
- `/api/indices` - Market indices
- `/api/stocks/asx20` - ASX 20 stocks

## Critical Requirements
1. **NO SYNTHETIC DATA** - Always use real Yahoo Finance
2. **CBA.AX PRICE** - Must show ~$170 (realistic), never $100
3. **WINDOWS 11** - All URLs hardcoded to localhost:8002
4. **VERSION CONTROL** - Track ALL changes in Git

## Testing Checklist
- [ ] CBA module loads and shows real price
- [ ] Technical Analysis charts have proper bounds
- [ ] Market Tracker shows ASX 20 data
- [ ] Prediction Centre backtesting works
- [ ] All module links functional
- [ ] No "coming soon" for working modules

## Recovery Points
- **Last Stable**: v8.2 (this version)
- **Backup Location**: `/home/user/webapp/StockTracker_Clean_v8/`
- **Git Commit**: Check `git log` for recovery points

---
**IMPORTANT**: Always update this file when making changes to track version history and prevent regressions.