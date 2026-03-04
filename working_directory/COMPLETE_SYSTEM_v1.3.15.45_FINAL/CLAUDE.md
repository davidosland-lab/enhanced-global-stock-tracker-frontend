# Project Context for AI Assistants (GenSpark/Claude)

**Last Updated**: 2026-02-03  
**Project**: Enhanced Global Stock Tracker  
**Version**: v1.3.15.85  
**Status**: ✅ Operational (Critical fixes applied)

---

## 🎯 Project Overview

**Type**: Paper trading dashboard with ML-based trading signals  
**Tech Stack**: Python, Dash, Plotly, yfinance, FinBERT, LSTM  
**Purpose**: Real-time paper trading with sentiment analysis and technical indicators  
**Deployment**: Windows 11 local machine (C:\Users\david)

---

## 📂 Critical Directory Structure

```
C:\Users\david\enhanced-global-stock-tracker-frontend\
│
├── working_directory\
│   └── COMPLETE_SYSTEM_v1.3.15.45_FINAL\  ← 🎯 PRIMARY WORKING DIRECTORY
│       │
│       ├── unified_trading_dashboard.py       (59K)  ← Main dashboard app
│       ├── paper_trading_coordinator.py       (73K)  ← Trading engine
│       │
│       ├── state\
│       │   └── paper_trading_state.json       (714 bytes+)  ← Trading data (FIXED!)
│       │
│       ├── reports\screening\
│       │   ├── au_morning_report.json         (1.3K)  ← Market sentiment (canonical)
│       │   └── au_morning_report_2026-02-03.json     ← Dated backup
│       │
│       ├── COMPLETE_FIX_v85_STATE_PERSISTENCE.py  ← Latest fix script
│       ├── COMPLETE_FIX_v84_SIGNAL_AND_NAMING.py  ← Previous fix
│       ├── COMPLETE_FIX_v83.py                     ← Earlier fix
│       │
│       ├── QUICKSTART_v85.md            ← Quick start guide
│       ├── EXECUTIVE_SUMMARY_v85.md     ← Complete fix analysis
│       ├── START_HERE.md                ← User guide
│       └── START_NOW.md                 ← Immediate start instructions
│
├── CLAUDE.md           ← This file (context for AI)
└── README.md           ← Project documentation
```

**Key Point**: Always work in `COMPLETE_SYSTEM_v1.3.15.45_FINAL` directory!

---

## 🔥 Critical Issues History & Fixes

### v1.3.15.85 (2026-02-03) ✅ FIXED - State Persistence
**Issue**: Dashboard showing "reverting to previous trades"  
**Root Cause**: State file was EMPTY (0 bytes) → Dashboard reset every 5 seconds  
**Symptoms**:
- ✅ 24h market chart displayed correctly
- ❌ Trades disappeared on refresh
- ❌ Positions not persisting
- ❌ Morning report stale (39.4 hours old)

**Solution Applied**:
1. ✅ Created valid state file (714 bytes)
2. ✅ Implemented atomic writes (crash-safe)
3. ✅ Added state validation on load
4. ✅ Generated fresh morning reports (0.0 hours)

**Files Modified**:
- `paper_trading_coordinator.py` - Atomic write pattern
- `unified_trading_dashboard.py` - State validation
- `state/paper_trading_state.json` - Created/initialized
- `reports/screening/au_morning_report*.json` - Fresh reports

**Fix Script**: `COMPLETE_FIX_v85_STATE_PERSISTENCE.py`  
**Status**: ✅ Complete and tested  
**Result**: Dashboard now stable, trades persist

---

### v1.3.15.84 (2026-02-03) ✅ FIXED - Morning Report Naming
**Issue**: Morning report file naming mismatch  
**Root Cause**: 
- Pipeline saved: `./au_morning_report_2026-01-27.json` (dated, root)
- Dashboard expected: `reports/screening/au_morning_report.json` (canonical, subdir)

**Solution**:
- Support both dated and canonical filenames
- Generate both versions
- Smart loader with fallback logic

**Fix Script**: `COMPLETE_FIX_v84_SIGNAL_AND_NAMING.py`  
**Status**: ✅ Complete

---

### v1.3.15.83 (Earlier) ✅ FIXED - Three Critical Issues
**Issues**:
1. Market performance chart missing
2. Live prices not updating (stale data)
3. Buy/sell signals blocked

**Status**: ✅ All resolved

---

## 🎯 Current System Status

| Component | Status | Details |
|-----------|--------|---------|
| **Dashboard** | ✅ OPERATIONAL | unified_trading_dashboard.py |
| **Trading Engine** | ✅ OPERATIONAL | paper_trading_coordinator.py |
| **State File** | ✅ VALID | 714 bytes (was 0) |
| **Morning Report** | ✅ FRESH | 0.0 hours (was 39.4h) |
| **Signals** | ✅ GENERATING | Buy/sell signals working |
| **Trade Persistence** | ✅ WORKING | No more revert issues |
| **GitHub Sync** | ✅ CURRENT | Branch: market-timing-critical-fix |

---

## 🚀 How to Start the Dashboard

### Windows 11 (Local Machine):

```cmd
cd C:\Users\david\enhanced-global-stock-tracker-frontend\working_directory\COMPLETE_SYSTEM_v1.3.15.45_FINAL

python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000
```

Then open: **http://localhost:8050**

### If Fix Needed:

```cmd
cd C:\Users\david\enhanced-global-stock-tracker-frontend\working_directory\COMPLETE_SYSTEM_v1.3.15.45_FINAL

python COMPLETE_FIX_v85_STATE_PERSISTENCE.py
```

---

## 🔄 Development Workflow

```
┌──────────────────────┐
│  Linux Sandbox       │  ← AI works here (testing/fixing)
│  /home/user/webapp   │
└──────────┬───────────┘
           │
           │ git push
           ▼
┌──────────────────────┐
│  GitHub Repository   │  ← Backup/version control
│  market-timing-...   │
└──────────┬───────────┘
           │
           │ git pull
           ▼
┌──────────────────────┐
│  Windows 11 Local    │  ← User runs here
│  C:\Users\david      │
└──────────────────────┘
```

**Key Understanding**:
- AI fixes issues in Linux sandbox
- Commits to GitHub (backup)
- User pulls to Windows and runs locally
- GitHub is for backup, NOT primary deployment

---

## 📝 Key Files Explained

### Core Application Files

**1. unified_trading_dashboard.py** (59K)
- Main dashboard web application
- Runs on http://localhost:8050
- Updates every 5 seconds
- Displays: portfolio, charts, positions, signals
- **Recent Fix**: Added state validation (v1.3.15.85)

**2. paper_trading_coordinator.py** (73K)
- Trading engine/logic
- Generates ML signals
- Executes paper trades
- Manages positions
- **Recent Fix**: Atomic state writes (v1.3.15.85)

### Data Files

**3. state/paper_trading_state.json** (714+ bytes)
- Current trading state
- Capital, positions, trades, performance
- **Critical**: Was 0 bytes (broken), now valid
- Updates every trading cycle (grows to 1-3 KB)

**4. reports/screening/au_morning_report.json** (1.3K)
- Market sentiment analysis (canonical version)
- FinBERT sentiment scores
- Market summary, top stocks
- **Critical**: Was 39.4h old, now fresh (0.0h)

**5. reports/screening/au_morning_report_2026-02-03.json**
- Dated backup version
- Same content as canonical
- Allows historical reference

### Fix Scripts

**6. COMPLETE_FIX_v85_STATE_PERSISTENCE.py** (17K)
- Latest fix (2026-02-03)
- Fixes state persistence issues
- Run if dashboard reverting or state file empty

**7. COMPLETE_FIX_v84_SIGNAL_AND_NAMING.py** (15K)
- Morning report naming fix
- Signal generation restoration

**8. COMPLETE_FIX_v83.py** (7.9K)
- Three critical issues fix
- Charts, prices, signals

### Documentation

**9. QUICKSTART_v85.md** - Quick start guide  
**10. EXECUTIVE_SUMMARY_v85.md** - Complete analysis  
**11. START_HERE.md** - User onboarding  
**12. START_NOW.md** - Immediate start guide

---

## 🐛 Known Issues

**None Currently** - All critical issues resolved in v1.3.15.85

---

## ⚠️ Common Problems & Solutions

### Problem: State file empty (0 bytes)
```cmd
python COMPLETE_FIX_v85_STATE_PERSISTENCE.py
```

### Problem: Dashboard reverting trades
```cmd
# Clear and reinitialize
del state\paper_trading_state.json
python COMPLETE_FIX_v85_STATE_PERSISTENCE.py
```

### Problem: Morning report stale
```cmd
python COMPLETE_FIX_v85_STATE_PERSISTENCE.py
# Or run pipeline:
python run_au_pipeline_v1.3.13.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000
```

### Problem: No trades executing
- Check market hours: ASX 10:00-16:00 AEDT (Mon-Fri)
- Check logs: `tail -f logs/unified_trading.log`
- Look for: `[SIGNAL]` and `[TRADE]` entries

---

## 📊 Expected Dashboard Behavior

### Within 10 Minutes of Starting:

```
Total Capital: $100,000.00
Return: +0.35%
━━━━━━━━━━━━━━━━━━━━━━━━━
Open Positions: 2
Unrealized P&L: +$350.00
━━━━━━━━━━━━━━━━━━━━━━━━━
Win Rate: 66.7%
Total Trades: 3 trades
━━━━━━━━━━━━━━━━━━━━━━━━━
Market Sentiment: 65.0 ⬤
CAUTIOUSLY_OPTIMISTIC
```

### Console Logs:
```
[STATE] Loaded valid state (1247 bytes)
[SENTIMENT] Morning report loaded (age: 0.0 hours)
[SIGNAL] Generated BUY signal for RIO.AX (confidence: 72.3%)
[TRADE] BUY 50 RIO.AX @ $122.45
State saved to state/paper_trading_state.json (1428 bytes)
```

---

## 🔑 Key Technical Details

### State File Structure:
```json
{
  "timestamp": "2026-02-03T01:01:39",
  "version": "v1.3.15.85",
  "capital": {"total": 100000, "cash": 85000, "invested": 15000},
  "positions": {"count": 2, "open": [...]},
  "performance": {"total_trades": 3, "win_rate": 66.7},
  "market": {"sentiment": 65.0, "sentiment_class": "moderate"},
  "state_version": 2
}
```

### Morning Report Structure:
```json
{
  "date": "2026-02-03",
  "market": "au",
  "finbert_sentiment": {
    "overall_sentiment": 65.0,
    "recommendation": "CAUTIOUSLY_OPTIMISTIC",
    "confidence": "MODERATE"
  },
  "top_stocks": [
    {"symbol": "RIO.AX", "sentiment": 70},
    {"symbol": "BHP.AX", "sentiment": 68}
  ]
}
```

---

## 🔗 GitHub Information

**Repository**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend  
**Branch**: market-timing-critical-fix  
**Latest PR**: #11  
**Latest Commit**: 7cfac14 (v1.3.15.85)

---

## 📋 Quick Reference Commands

### Pull Latest Fixes:
```cmd
cd C:\Users\david\enhanced-global-stock-tracker-frontend
git pull origin market-timing-critical-fix
```

### Start Dashboard:
```cmd
cd working_directory\COMPLETE_SYSTEM_v1.3.15.45_FINAL
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000
```

### Apply Fix:
```cmd
python COMPLETE_FIX_v85_STATE_PERSISTENCE.py
```

### Check Files:
```cmd
dir state\paper_trading_state.json
dir reports\screening\au_morning_report*.json
```

### Watch Logs:
```cmd
type logs\unified_trading.log
```

---

## 🎯 For AI Assistants

### When Starting a New Session:

1. **Read this file** (CLAUDE.md) to understand project context
2. **Check current status** section above
3. **Review recent fixes** to know what's been done
4. **Understand the workflow**: Linux sandbox → GitHub → Windows local

### Key Things to Remember:

- ✅ User is on **Windows 11** (C:\Users\david)
- ✅ Work directory: `COMPLETE_SYSTEM_v1.3.15.45_FINAL`
- ✅ State file was **empty** (0 bytes) - now **fixed** (714 bytes)
- ✅ Dashboard runs on **http://localhost:8050**
- ✅ All fixes from v1.3.15.85 are **applied and tested**
- ✅ GitHub is **backup only**, not primary deployment
- ✅ User pulls fixes from GitHub to Windows
- ✅ **NO uncommitted changes** - everything pushed

### Don't Suggest:

- ❌ Running git commands without context
- ❌ Deploying to cloud (it's local Windows)
- ❌ Fixing issues already resolved (check history above)
- ❌ Commands for Linux when user is on Windows

### Do Suggest:

- ✅ Windows-compatible commands (cmd/PowerShell)
- ✅ Running fix scripts if issues recur
- ✅ Checking logs for diagnostics
- ✅ Updating this CLAUDE.md file after changes

---

## 📅 Session History

### Session 2026-02-03 - State Persistence Fix
**Issue**: Dashboard reverting to previous trades  
**Root Cause**: Empty state file (0 bytes)  
**Solution**: v1.3.15.85 fix with atomic writes + validation  
**Files Changed**: 
- paper_trading_coordinator.py
- unified_trading_dashboard.py
- state/paper_trading_state.json (created)
- reports/screening/au_morning_report*.json (created)

**Status**: ✅ Complete  
**Commits**: d935bef, 644ce5a, a7bd5f9, 7cfac14  
**Result**: Dashboard stable, trades persisting correctly

---

## 🎓 What to Know

1. **This is a local Windows deployment** - not cloud
2. **State file was THE problem** - 0 bytes caused all revert issues
3. **Atomic writes prevent corruption** - crash-safe now
4. **State validation catches errors** - graceful recovery
5. **Morning report must be fresh** - < 24 hours old
6. **GitHub is backup** - user pulls to Windows
7. **All fixes are applied** - system is operational

---

**Status**: ✅ System operational, all critical fixes applied  
**Next**: Monitor dashboard stability, watch for any new issues  
**Support**: Read QUICKSTART_v85.md or EXECUTIVE_SUMMARY_v85.md for details

---

*This file should be read by AI assistants at the start of each session to maintain context.*
