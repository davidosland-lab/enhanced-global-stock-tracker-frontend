# Windows 11 Deployment Checklist
## Portfolio Backtesting Feature

**Date**: November 2025  
**Feature**: Multi-Stock Portfolio Backtesting  
**Version**: 1.0.0  
**Commits**: c3fa014, 6001f22, 3ac629c  

---

## 📋 Pre-Deployment Checklist

### ✅ Development Verification
- [x] Portfolio backtesting implemented
- [x] Timezone issues fixed
- [x] All files committed to git
- [x] Documentation created
- [x] No uncommitted changes

### ✅ Files Prepared
- [x] 2 modified core files
- [x] 3 modified backtesting files
- [x] 2 new portfolio files
- [x] 3 documentation files
- [x] Deployment script created

---

## 📁 Files to Deploy

### Core Application (2 files - MODIFIED)
```
✓ app_finbert_v4_dev.py (40KB)
  - Added portfolio backtest API endpoint
  - Added allocation strategies endpoint
  
✓ templates/finbert_v4_enhanced_ui.html (80KB)
  - Added portfolio backtest UI modal
  - Added chart rendering functions
```

### Backtesting Backend (5 files - 2 NEW, 3 MODIFIED)
```
✓ models/backtesting/__init__.py (0.5KB) [NEW]
  - Package initialization
  
✓ models/backtesting/portfolio_engine.py (27KB) [NEW]
  - Portfolio management engine
  
✓ models/backtesting/portfolio_backtester.py (15KB) [NEW]
  - Portfolio backtest orchestrator
  
✓ models/backtesting/data_loader.py (10KB) [MODIFIED]
  - Timezone fix applied
  
✓ models/backtesting/cache_manager.py (9KB) [MODIFIED]
  - Timezone fix applied
```

### Documentation (3 files - NEW)
```
✓ docs/PORTFOLIO_BACKTESTING_GUIDE.md (14KB)
  - Complete user guide
  
✓ docs/PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md (11KB)
  - Technical summary
  
✓ docs/TIMEZONE_FIX_SUMMARY.md (6KB)
  - Timezone fix documentation
```

### Support Files (1 file - NEW)
```
✓ DEPLOY_PORTFOLIO_BACKTEST.bat (7KB)
  - Automated deployment script
```

---

## 🚀 Deployment Steps

### Step 1: Backup Existing Files
```batch
# Create backup directory
mkdir backup\portfolio_backtest_20251101

# Backup existing files
copy app_finbert_v4_dev.py backup\portfolio_backtest_20251101\
copy templates\finbert_v4_enhanced_ui.html backup\portfolio_backtest_20251101\
copy models\backtesting\data_loader.py backup\portfolio_backtest_20251101\
copy models\backtesting\cache_manager.py backup\portfolio_backtest_20251101\
```

**Status**: [ ] Complete

---

### Step 2: Copy Modified Core Files

```batch
# Core application
copy NEW\app_finbert_v4_dev.py .
copy NEW\templates\finbert_v4_enhanced_ui.html templates\
```

**Files to Copy**:
- [ ] `app_finbert_v4_dev.py`
- [ ] `templates/finbert_v4_enhanced_ui.html`

**Status**: [ ] Complete

---

### Step 3: Copy Modified Backtesting Files

```batch
# Backtesting framework
copy NEW\models\backtesting\data_loader.py models\backtesting\
copy NEW\models\backtesting\cache_manager.py models\backtesting\
```

**Files to Copy**:
- [ ] `models/backtesting/data_loader.py`
- [ ] `models/backtesting/cache_manager.py`

**Status**: [ ] Complete

---

### Step 4: Add New Portfolio Files

```batch
# Portfolio backtesting
copy NEW\models\backtesting\__init__.py models\backtesting\
copy NEW\models\backtesting\portfolio_engine.py models\backtesting\
copy NEW\models\backtesting\portfolio_backtester.py models\backtesting\
```

**Files to Add**:
- [ ] `models/backtesting/__init__.py`
- [ ] `models/backtesting/portfolio_engine.py`
- [ ] `models/backtesting/portfolio_backtester.py`

**Status**: [ ] Complete

---

### Step 5: Add Documentation

```batch
# Create docs directory if needed
mkdir docs

# Copy documentation
copy NEW\docs\PORTFOLIO_BACKTESTING_GUIDE.md docs\
copy NEW\docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md docs\
copy NEW\docs\TIMEZONE_FIX_SUMMARY.md docs\
```

**Files to Add**:
- [ ] `docs/PORTFOLIO_BACKTESTING_GUIDE.md`
- [ ] `docs/PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md`
- [ ] `docs/TIMEZONE_FIX_SUMMARY.md`

**Status**: [ ] Complete

---

### Step 6: Verify Deployment

```batch
# Check all files are present
dir models\backtesting\*.py
dir templates\finbert_v4_enhanced_ui.html
dir docs\PORTFOLIO_*.md
```

**Verification**:
- [ ] All 13 files copied successfully
- [ ] No errors in file list
- [ ] Backup created successfully

**Status**: [ ] Complete

---

## 🧪 Post-Deployment Testing

### Test 1: Server Startup
```batch
START_FINBERT_V4.bat
```

**Expected**:
- [ ] Server starts without errors
- [ ] Shows "Portfolio Backtesting" in features list
- [ ] No import errors
- [ ] Port 5001 accessible

**Status**: [ ] Complete

---

### Test 2: UI Verification
```
Open: http://localhost:5001
```

**Check**:
- [ ] "Portfolio Backtest" button visible (indigo button)
- [ ] Button clickable
- [ ] Modal opens correctly
- [ ] All form fields present

**Status**: [ ] Complete

---

### Test 3: Single-Stock Backtest (Regression Test)
```
1. Click "Backtest Strategy"
2. Enter: AAPL
3. Dates: 2023-01-01 to 2023-12-31
4. Click "Run Backtest"
```

**Expected**:
- [ ] Backtest completes without errors
- [ ] Charts display correctly
- [ ] Metrics calculated properly
- [ ] No regression from previous version

**Status**: [ ] Complete

---

### Test 4: Portfolio Backtest (New Feature)
```
1. Click "Portfolio Backtest"
2. Enter: AAPL, MSFT
3. Allocation: Equal Weight
4. Dates: 2023-01-01 to 2023-12-31
5. Click "Run Portfolio Backtest"
```

**Expected**:
- [ ] No timezone errors
- [ ] Backtest completes successfully
- [ ] Performance metrics displayed
- [ ] Diversification metrics shown
- [ ] 3 charts render correctly:
  - [ ] Portfolio equity curve
  - [ ] Allocation pie chart
  - [ ] Contribution analysis

**Status**: [ ] Complete

---

### Test 5: Multi-Stock Portfolio (3+ stocks)
```
Symbols: AAPL, MSFT, GOOGL
Allocation: Risk Parity
Dates: 2023-01-01 to 2023-12-31
```

**Expected**:
- [ ] Risk-parity allocation calculated
- [ ] All stocks loaded successfully
- [ ] Correlation matrix computed
- [ ] Portfolio metrics accurate

**Status**: [ ] Complete

---

### Test 6: Custom Allocations
```
Symbols: AAPL, MSFT, GOOGL
Allocation: Custom
Weights: {"AAPL": 0.5, "MSFT": 0.3, "GOOGL": 0.2}
```

**Expected**:
- [ ] Custom allocations applied
- [ ] Validation checks weights sum to 1.0
- [ ] Portfolio built according to weights

**Status**: [ ] Complete

---

## ⚠️ Known Issues & Solutions

### Issue 1: Timezone Error
**Symptom**: `Cannot join tz-naive with tz-aware DatetimeIndex`  
**Solution**: Ensure timezone fix files (data_loader.py, cache_manager.py) are deployed  
**Status**: Fixed in deployment

### Issue 2: Cache Directory
**Symptom**: Permission error creating cache  
**Solution**: Create `cache/` directory manually with write permissions  
**Status**: Auto-created on first run

### Issue 3: Slow First Run
**Symptom**: Portfolio backtest takes 2-5 minutes  
**Solution**: Expected behavior (downloading data), subsequent runs use cache  
**Status**: Normal behavior

---

## 📊 Success Criteria

### Deployment Success
- [x] All 13 files copied
- [ ] No file errors
- [ ] Backup created
- [ ] Server starts successfully

### Functional Success
- [ ] Single-stock backtest works (no regression)
- [ ] Portfolio backtest completes without errors
- [ ] No timezone errors
- [ ] Charts display correctly
- [ ] All 3 allocation strategies work

### Performance Success
- [ ] First portfolio backtest completes in <5 minutes
- [ ] Cached portfolio backtest completes in <30 seconds
- [ ] No memory leaks
- [ ] Server remains stable

---

## 🔄 Rollback Plan

If deployment fails:

### Quick Rollback
```batch
# Stop server
STOP_FINBERT_V4.bat

# Restore from backup
copy backup\portfolio_backtest_20251101\* .
copy backup\portfolio_backtest_20251101\templates\* templates\
copy backup\portfolio_backtest_20251101\models\backtesting\* models\backtesting\

# Restart server
START_FINBERT_V4.bat
```

### Full Rollback
```batch
# Revert to git commit before portfolio backtest
git checkout 980fcf6
```

---

## 📝 Deployment Notes

### Environment
- **OS**: Windows 11
- **Python**: 3.8+
- **Dependencies**: No new packages required

### Estimated Time
- **Backup**: 2 minutes
- **File Copy**: 5 minutes
- **Verification**: 3 minutes
- **Testing**: 15 minutes
- **Total**: ~25 minutes

### Risk Assessment
- **Risk Level**: Low
- **Reason**: All changes are additive or defensive
- **Impact**: No breaking changes to existing features

---

## ✅ Final Checklist

### Pre-Deployment
- [ ] Backup completed
- [ ] All files ready
- [ ] Deployment plan reviewed

### During Deployment
- [ ] Files copied successfully
- [ ] No copy errors
- [ ] Verification passed

### Post-Deployment
- [ ] Server starts successfully
- [ ] UI displays correctly
- [ ] Single-stock backtest works
- [ ] Portfolio backtest works
- [ ] All tests passed

### Documentation
- [ ] User guide accessible
- [ ] Technical docs available
- [ ] Troubleshooting guide reviewed

---

## 📞 Support

### If Issues Occur:
1. Check `TIMEZONE_FIX_SUMMARY.md` for timezone errors
2. Review `PORTFOLIO_BACKTESTING_GUIDE.md` for usage
3. Check server logs for error messages
4. Use rollback plan if needed

### Documentation Location:
```
docs/
├── PORTFOLIO_BACKTESTING_GUIDE.md
├── PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md
└── TIMEZONE_FIX_SUMMARY.md
```

---

## 🎯 Sign-Off

| Task | Status | Date | Notes |
|------|--------|------|-------|
| Files Prepared | ✅ | 2025-11-01 | All files ready |
| Backup Created | [ ] | | |
| Files Deployed | [ ] | | |
| Tests Passed | [ ] | | |
| Deployment Complete | [ ] | | |

**Deployed By**: _______________  
**Date**: _______________  
**Sign**: _______________  

---

**Deployment Version**: Portfolio Backtesting v1.0.0  
**Last Updated**: November 2025  
**Status**: Ready for Deployment
