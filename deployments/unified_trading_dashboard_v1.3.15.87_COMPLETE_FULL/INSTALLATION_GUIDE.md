# Unified Trading Dashboard v1.3.15.87 - Installation Guide

## Version Info
- Version: v1.3.15.87 COMPLETE FULL
- Date: 2026-02-03
- Includes: All ML components + Hotfix v87

## What's Included
1. Core dashboard with trading controls (v86)
2. Full ML pipeline (70-75% win rate)
3. FinBERT v4.4.4 sentiment integration (FIXED v87)
4. Market calendar and tax audit
5. Pipeline runners (AU/UK/US)

## Installation Steps

### 1. Extract Package
```cmd
cd C:\Users\david\Regime_trading\
:: Extract unified_trading_dashboard_v1.3.15.87_COMPLETE_FULL.zip here
```

### 2. Install Dependencies
```cmd
cd unified_trading_dashboard_v1.3.15.87_COMPLETE_FULL
INSTALL.bat
```

### 3. Start Dashboard
```cmd
START.bat
```

### 4. Access Dashboard
Open browser: http://localhost:8050

## Verification
- Dashboard loads without errors
- No "get_trading_gate" errors in logs
- Trading controls visible and working
- Charts updating every 5 seconds
- State file grows (trades persist)

## Fixes Included
- v1.3.15.87: Fixed missing get_trading_gate() method (HOTFIX)
- v1.3.15.86: Added trading controls (Confidence, Stop Loss, Force Trade)
- v1.3.15.85: Fixed state persistence (atomic writes)
- v1.3.15.84: Fixed morning report naming

## Support
- GitHub: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- Branch: market-timing-critical-fix
- Commit: c23cc3c
