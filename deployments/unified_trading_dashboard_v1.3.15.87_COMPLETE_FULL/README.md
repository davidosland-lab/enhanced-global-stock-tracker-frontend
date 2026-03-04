# Unified Trading Dashboard v1.3.15.87 COMPLETE

## Quick Start
1. Run `INSTALL.bat`
2. Run `START.bat`
3. Open http://localhost:8050

## What's New in v1.3.15.87
**HOTFIX**: Fixed missing get_trading_gate() method
- Error: 'IntegratedSentimentAnalyzer' object has no attribute 'get_trading_gate'
- Solution: Added complete get_trading_gate() implementation
- Impact: Dashboard now loads without errors

## Previous Fixes
- v1.3.15.86: Trading Controls (Confidence slider, Stop Loss, Force Trade)
- v1.3.15.85: State Persistence (atomic writes, trades persist)
- v1.3.15.84: Morning Report Naming (dated/non-dated files)

## Package Contents
- Core dashboard with all fixes
- Full ML pipeline (70-75% win rate)
- FinBERT v4.4.4 sentiment (FIXED)
- Market calendar and tax audit
- AU/UK/US pipeline runners
- Complete documentation

## Documentation
See `docs/` folder for:
- INSTALLATION_GUIDE.md
- HOTFIX_v87.md
- TRADING_CONTROLS_GUIDE_v86.md
- COMPLETE_FIX_SUMMARY_v84_v85_v86.md

## Version
- v1.3.15.87 COMPLETE FULL
- Date: 2026-02-03
- Commit: c23cc3c
