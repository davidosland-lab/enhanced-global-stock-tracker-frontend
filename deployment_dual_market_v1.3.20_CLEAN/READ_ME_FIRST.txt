================================================================================
   DUAL MARKET SCREENING SYSTEM v1.3.20 - HOTFIX CLEAN BUILD
================================================================================

** READ THIS FIRST BEFORE EXTRACTION/INSTALLATION **

================================================================================
WHAT'S IN THIS PACKAGE
================================================================================

This is a CLEAN BUILD with ALL CRITICAL HOTFIXES applied.

Previous deployment packages (especially those with "UI_FIXES" in the name)
contained BREAKING BUGS that prevented the US pipeline from functioning.

This package fixes ALL known issues and restores full functionality.

================================================================================
CRITICAL BUGS FIXED
================================================================================

✅ US Pipeline Report Generation Error (PRIMARY FIX)
   Error: "ReportGenerator.generate_morning_report() got unexpected keyword 
          argument 'stocks'"
   
   ROOT CAUSE: US pipeline was calling generate_morning_report() with 
               incorrect parameter names
   
   FIXED: Corrected all parameter names to match ReportGenerator signature

✅ US Pipeline Method Call Errors
   - BatchPredictor parameter mismatch (market_sentiment → spi_sentiment)
   - OpportunityScorer method name (score_batch → score_opportunities)
   - CSVExporter method name (export_opportunities → export_screening_results)

✅ US Regime Engine Datetime Error
   Error: "can't compare datetime.datetime to datetime.date"
   FIXED: Added DatetimeIndex conversion after MultiIndex handling

✅ ASX Email Notification Error
   Error: "'bool' object is not callable"
   FIXED: Removed redundant boolean checks before method calls

✅ US Regime Data Display
   - Reports now correctly display regime engine analysis
   - Fixed dictionary key mapping (regime_label, crash_risk_score)

================================================================================
WHEN TO USE THIS PACKAGE
================================================================================

Use this package if you're experiencing:

❌ "got an unexpected keyword argument 'stocks'" error
❌ US pipeline report generation failures
❌ Missing regime data in reports
❌ AttributeError for score_batch or export_opportunities
❌ Datetime comparison errors in regime engine
❌ Boolean callable errors in email notifications

================================================================================
INSTALLATION INSTRUCTIONS
================================================================================

1. BACKUP YOUR CURRENT INSTALLATION
   - If you have a working system, keep a backup before upgrading
   - Previous working version: event_risk_guard_v1.3.20_REGIME_FINAL

2. EXTRACT THIS PACKAGE
   - Extract to a NEW directory (recommended)
   - OR extract over existing installation after backup

3. CLEAR PYTHON CACHE (CRITICAL!)
   
   Windows:
   ```
   for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
   del /s /q *.pyc
   ```
   
   Linux/Mac:
   ```
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```
   
   ⚠️ IMPORTANT: Not clearing cache will cause old code to run!

4. VERIFY INSTALLATION
   
   Run the verification script:
   ```
   python VERIFY.py
   ```
   
   This will check all critical files are present and correct.

5. CONFIGURE (if first-time install)
   
   Edit models/config/screening_config.json:
   - Set your email notification preferences (optional)
   - Adjust sector selections if needed
   - Most defaults work out of the box

6. RUN TESTS
   
   Test ASX pipeline:
   ```
   python run_screening.py --asx-only
   ```
   
   Test US pipeline:
   ```
   python run_screening.py --us-only
   ```
   
   Test both markets:
   ```
   python run_screening.py --both
   ```

7. START WEB UI
   
   Windows:
   ```
   START_WEB_UI.bat
   ```
   
   Linux/Mac:
   ```
   ./START_WEB_UI.sh
   ```
   
   Access at: http://localhost:5000

================================================================================
VERIFICATION CHECKLIST
================================================================================

After installation, verify:

[ ] Python cache cleared (no __pycache__ directories with old .pyc files)
[ ] VERIFY.py runs without errors
[ ] US pipeline completes without "stocks" parameter error
[ ] ASX pipeline completes without boolean callable error
[ ] Reports generated in reports/us/ and reports/asx/
[ ] Reports show regime engine data (market state, crash risk)
[ ] CSV exports created successfully
[ ] Web UI displays data for both markets
[ ] No AttributeError for score_batch or export_opportunities

================================================================================
TROUBLESHOOTING
================================================================================

Problem: Still getting "got unexpected keyword argument 'stocks'"
Solution: 
  1. Delete ALL __pycache__ directories
  2. Delete ALL .pyc files
  3. Restart Python/terminal
  4. Run from CLEAN directory (not old installation)

Problem: Reports don't show regime data
Solution:
  - This is FIXED in this build
  - Clear cache and extract fresh package
  - Verify you're running from this deployment, not old one

Problem: yfinance 401 errors
Solution:
  - This is a Yahoo Finance API issue (external)
  - NOT a bug in the code
  - System has fallback mechanisms
  - Usually self-resolves

Problem: "No module named X"
Solution:
  - Run: pip install -r requirements.txt
  - Check TROUBLESHOOTING_IMPORTS.md

================================================================================
IMPORTANT NOTES
================================================================================

1. UI AND REPORTS NOW WORK PERFECTLY
   - All regime engine data displays correctly
   - Both ASX and US market reports functional
   - No parameter mismatch errors

2. PYTHON CACHE IS CRITICAL
   - ALWAYS clear cache after extracting
   - Old .pyc files will cause errors
   - Cache clearing is NOT optional

3. yfinance 401 ERRORS ARE NORMAL
   - These are Yahoo Finance API issues
   - NOT a "DNS error" (your internet is fine)
   - System continues with fallback data

4. PREVIOUS VERSIONS HAD BUGS
   - Any package with "UI_FIXES" had breaking bugs
   - This HOTFIX_CLEAN build is the first fully working version
   - Rollback to REGIME_FINAL if you need stability without new features

================================================================================
WHAT'S WORKING
================================================================================

✅ ASX Market Pipeline (full functionality)
✅ US Market Pipeline (all phases working)
✅ Regime Engine Analysis (ASX and US)
✅ Report Generation (with regime data display)
✅ CSV Export (both markets)
✅ Web UI Dashboard (dual market display)
✅ Email Notifications (if configured)
✅ Event Risk Guard (optional)
✅ Batch Prediction & Scoring (both markets)

================================================================================
FILE LOCATIONS
================================================================================

Critical Documentation:
- READ_ME_FIRST.txt (this file)
- CRITICAL_FIXES_APPLIED.txt (detailed technical fixes)
- HOTFIX_CHANGELOG_v1.3.20_CRITICAL.md (full changelog)
- DEPLOYMENT_README.md (comprehensive guide)

Launchers:
- RUN_BOTH_MARKETS.bat / .sh
- RUN_US_MARKET.bat / .sh
- START_WEB_UI.bat / .sh

Configuration:
- models/config/screening_config.json (main config)
- models/config/us_sectors.json (US market sectors)
- models/config/asx_sectors.json (ASX market sectors)

Reports:
- reports/us/ (US market reports)
- reports/asx/ or reports/morning_reports/ (ASX reports)
- reports/html/ (archived reports)

Logs:
- logs/screening/us/ (US pipeline logs)
- logs/screening/ (ASX pipeline logs)

================================================================================
SUPPORT
================================================================================

For detailed technical information:
1. Read CRITICAL_FIXES_APPLIED.txt
2. Check HOTFIX_CHANGELOG_v1.3.20_CRITICAL.md
3. Review TROUBLESHOOTING_IMPORTS.md

For installation issues:
1. Ensure Python 3.8+ installed
2. Run: pip install -r requirements.txt
3. Clear all Python cache
4. Check DEPLOYMENT_README.md

For runtime errors:
1. Check logs in logs/screening/
2. Verify cache is cleared
3. Ensure running from clean deployment directory

================================================================================
VERSION INFORMATION
================================================================================

Package: Dual_Market_Screening_v1.3.20_HOTFIX_CLEAN
Build Date: 2025-11-22
Git Commit: eb110fe
Branch: finbert-v4.0-development
Status: PRODUCTION READY

Previous Versions:
- v1.3.20 REGIME_FINAL: Last stable before UI fixes (working, no new features)
- v1.3.20 UI_FIXES: BROKEN - had parameter mismatch bugs
- v1.3.20 HOTFIX_CLEAN: THIS VERSION - all bugs fixed

================================================================================
QUICK START (after extraction)
================================================================================

1. Clear cache:
   Windows: for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
   Linux/Mac: find . -type d -name "__pycache__" -exec rm -rf {} +

2. Install dependencies:
   pip install -r requirements.txt

3. Run verification:
   python VERIFY.py

4. Test system:
   python run_screening.py --both

5. Start web UI:
   Windows: START_WEB_UI.bat
   Linux/Mac: ./START_WEB_UI.sh

6. Access dashboard:
   http://localhost:5000

================================================================================
END OF QUICK START GUIDE
================================================================================

For detailed information, see:
- DEPLOYMENT_README.md
- CRITICAL_FIXES_APPLIED.txt
- HOTFIX_CHANGELOG_v1.3.20_CRITICAL.md

This package contains ALL fixes and is PRODUCTION READY.

================================================================================
