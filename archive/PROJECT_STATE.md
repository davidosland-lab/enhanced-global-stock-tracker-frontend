# GSMT PROJECT STATE TRACKER - DO NOT DELETE
**Last Updated:** September 30, 2025, 12:47 AEST

## CRITICAL RULES - NEVER VIOLATE
1. **NO SYNTHETIC DATA** - Only use Yahoo Finance real-time data
2. **NO DEMO DATA** - Never generate fake prices or percentages  
3. **PRESERVE WORKING MODULES** - Never modify working code without explicit permission
4. **TEST BEFORE CLAIMING FIXED** - Always verify fixes work before reporting complete

## CURRENT REAL MARKET DATA (Sep 30, 2025)
- All Ordinaries: DOWN -0.14% (Closed at 16:00 AEST) ✓ REAL
- S&P 500: Last close UP +0.26% (Sep 29, opens 00:30 AEST Sep 30) ✓ REAL  
- FTSE 100: UP +0.15% (Currently trading, closes 02:30 AEST Oct 1) ✓ REAL

## WORKING MODULES - DO NOT MODIFY
```
✅ NONE CURRENTLY - ALL BROKEN DUE TO RECENT CHANGES
```

## BROKEN MODULES
```
❌ Global Indices Tracker - Wrong data, wrong timing
❌ CBA Module - Links broken
❌ Technical Analysis - Links broken
❌ Prediction Dashboard - Links broken
❌ Document Center - Links broken
❌ Single Stock Tracker - MISSING from dashboard
```

## BACKEND STATUS
- Port 8000: enhanced_market_backend.py RUNNING
- Real data confirmed: YES
- API working: YES at http://localhost:8000/api/indices

## REQUIRED FIXES
1. Use REAL backend data from port 8000
2. Fix ALL module links in dashboard
3. Add Single Stock Tracker to dashboard
4. Ensure market timing is correct
5. Test EVERYTHING before claiming fixed

## REGRESSION LOG
- Sep 30: Complete regression - all modules broken after "fixing" indices tracker
- Sep 29: Had working modules, lost during timing fix attempts
- Sep 28: Working CBA module, broken by subsequent changes

## PATH FORWARD
1. Create IMMUTABLE base files that work
2. Version control properly with Git
3. Test in isolation before integration
4. Keep working backups
5. Document what works BEFORE changing anything