================================================================================
                 DUAL MARKET SCREENING SYSTEM v1.3.20
          Complete ASX + US Stock Screening & Analysis Platform
================================================================================

📦 PACKAGE CONTENTS
================================================================================

This package contains a complete dual-market stock screening system covering:
  ✅ 240 ASX stocks across 8 sectors
  ✅ 240 US stocks across 8 sectors
  ✅ Unified launcher for both markets
  ✅ Market regime detection (crash risk analysis)
  ✅ Event risk protection (earnings, regulatory)
  ✅ LSTM price predictions
  ✅ Comprehensive reporting (HTML, JSON, CSV)

================================================================================
🚀 QUICK START (3 STEPS)
================================================================================

LINUX/MAC:
  1. ./INSTALL.sh              # Install dependencies
  2. python3 VERIFY.py         # Verify installation
  3. ./RUN_QUICK_TEST.sh       # Run test (5 stocks)

WINDOWS:
  1. INSTALL.bat               # Install dependencies
  2. python VERIFY.py          # Verify installation
  3. RUN_QUICK_TEST.bat        # Run test (5 stocks)

================================================================================
📁 FILE GUIDE
================================================================================

INSTALLATION & VERIFICATION:
  INSTALL.sh / INSTALL.bat          Install dependencies (Linux/Mac or Windows)
  VERIFY.py                         Comprehensive verification script
  requirements.txt                  Python package dependencies

EXECUTION SCRIPTS:
  run_screening.py                  Main unified launcher
  RUN_QUICK_TEST.sh / .bat          Quick test (5 stocks, ~3 min)
  RUN_US_MARKET.sh / .bat           US market only (~15-20 min)
  RUN_BOTH_MARKETS.sh / .bat        Both markets parallel (~20-25 min)

WEB UI (DASHBOARD):
  START_WEB_UI.sh / .bat            Launch web dashboard
  web_ui.py                         Flask web application
  templates/dashboard.html          Dashboard template
  static/css/dashboard.css          Dashboard styles
  static/js/dashboard.js            Dashboard JavaScript
  WEB_UI_README.txt                 Web UI documentation

DOCUMENTATION:
  README.txt                        This file (quick reference)
  DEPLOYMENT_README.md              Complete deployment guide
  US_MARKET_PIPELINE_README.md      US pipeline documentation
  US_PIPELINE_DEPLOYMENT_SUMMARY.md Technical specifications
  QUICK_START_US_PIPELINE.txt       Quick reference guide
  ROLLBACK_POINT_v1.3.20_REGIME_FINAL.md  ASX pipeline reference
  QUICK_REFERENCE_ROLLBACK_POINT.txt      ASX quick reference

CORE SYSTEM:
  models/                           All pipeline modules
    ├── config/                     Market configurations
    │   ├── asx_sectors.json        ASX 240 stocks
    │   ├── us_sectors.json         US 240 stocks
    │   └── us_market_config.py     US parameters
    └── screening/                  Pipeline modules
        ├── overnight_pipeline.py   ASX pipeline
        ├── us_overnight_pipeline.py US pipeline
        ├── us_stock_scanner.py     US scanner
        ├── us_market_monitor.py    US sentiment
        ├── us_market_regime_engine.py US regime
        └── [shared modules...]

================================================================================
⚡ USAGE EXAMPLES
================================================================================

BASIC COMMANDS:
  python run_screening.py --market us          # US market only
  python run_screening.py --market asx         # ASX market only
  python run_screening.py --market both        # Both (sequential)
  python run_screening.py --market both --parallel  # Both (parallel)

CUSTOM OPTIONS:
  python run_screening.py --market us --stocks 20  # 20 stocks/sector
  python run_screening.py --market us --sectors "Technology,Healthcare"

TEST INDIVIDUAL COMPONENTS:
  python models/screening/us_market_monitor.py      # Test US sentiment
  python models/screening/us_stock_scanner.py       # Test US scanner
  python models/screening/us_market_regime_engine.py # Test regime engine

WEB DASHBOARD:
  START_WEB_UI.bat (or .sh)         # Start web dashboard
  Browser: http://localhost:5000    # Access dashboard
  Features: Reports, Logs, Regime Status, Model Management

================================================================================
📊 SYSTEM SPECIFICATIONS
================================================================================

ASX Market:
  - Stocks: 240 across 8 sectors
  - Index: ^AXJO (ASX 200)
  - Market Cap: $500M+ AUD
  - Volume: 500K+ shares/day

US Market:
  - Stocks: 240 across 8 sectors
  - Indices: ^GSPC (S&P 500), ^VIX
  - Market Cap: $2B+ USD
  - Volume: 1M+ shares/day

Total Coverage:
  - 480 stocks
  - 16 sectors
  - 2 markets

================================================================================
⏱️ EXECUTION TIMES
================================================================================

  Quick Test (5 stocks/sector):          2-3 minutes
  US Market Full (30 stocks/sector):     15-20 minutes
  ASX Market Full (30 stocks/sector):    15-20 minutes
  Both Markets Sequential:               30-40 minutes
  Both Markets Parallel:                 20-25 minutes

================================================================================
📊 OUTPUT LOCATIONS
================================================================================

REPORTS (HTML):
  reports/morning_report_YYYYMMDD.html          ASX report
  reports/us/us_morning_report_YYYYMMDD.html    US report

DATA (JSON):
  data/pipeline_results_YYYYMMDD.json           ASX results
  data/us/us_pipeline_results_YYYYMMDD.json     US results

EXPORTS (CSV):
  data/opportunities_YYYYMMDD.csv               ASX opportunities
  data/us/us_opportunities_YYYYMMDD.csv         US opportunities

LOGS:
  logs/screening/overnight_pipeline.log         ASX logs
  logs/screening/us/us_overnight_pipeline.log   US logs
  logs/screening/us/errors/                     Error states

================================================================================
🔧 SYSTEM REQUIREMENTS
================================================================================

SOFTWARE:
  - Python 3.8 or higher
  - pip (package manager)
  - Internet connection (for data fetching)

HARDWARE:
  - CPU: 2+ cores recommended
  - RAM: 4GB+ recommended
  - Disk: 2GB+ free space

DEPENDENCIES (auto-installed by INSTALL script):
  - yahooquery (market data)
  - pandas, numpy (data processing)
  - hmmlearn (regime detection)
  - scikit-learn (ML models)
  - [see requirements.txt for complete list]

================================================================================
🆘 TROUBLESHOOTING
================================================================================

IMPORT ERRORS:
  Solution: Run installation script again
    Linux/Mac: ./INSTALL.sh
    Windows:   INSTALL.bat

DATA FETCH FAILURES:
  - Check internet connection
  - Verify yahooquery service is accessible
  - Try again later (may be rate-limited)

MEMORY ERRORS:
  - Reduce stocks per sector: --stocks 20
  - Run markets separately (not --market both)
  - Close other applications

SLOW EXECUTION:
  - Use parallel mode: --parallel
  - Reduce stocks per sector
  - Check system resources

CHECK LOGS:
  - ASX: logs/screening/overnight_pipeline.log
  - US: logs/screening/us/us_overnight_pipeline.log
  - Errors: logs/screening/us/errors/

================================================================================
📚 DETAILED DOCUMENTATION
================================================================================

For complete information, see:

  1. DEPLOYMENT_README.md
     Complete deployment guide with all details

  2. US_MARKET_PIPELINE_README.md
     US market pipeline documentation (12KB, comprehensive)

  3. QUICK_START_US_PIPELINE.txt
     Quick reference for US pipeline (8KB)

  4. US_PIPELINE_DEPLOYMENT_SUMMARY.md
     Technical specifications and deployment info (14KB)

================================================================================
🔄 SCHEDULING (OPTIONAL)
================================================================================

LINUX/MAC (Cron):
  # Edit crontab
  crontab -e
  
  # Add line (runs daily at 6 AM ET, weekdays)
  0 6 * * 1-5 cd /path/to/deployment_dual_market_v1.3.20 && python3 run_screening.py --market both

WINDOWS (Task Scheduler):
  1. Open Task Scheduler
  2. Create Basic Task
  3. Trigger: Daily, 6:00 AM, Weekdays
  4. Action: Start Program
  5. Program: python
  6. Arguments: run_screening.py --market both
  7. Start in: C:\path\to\deployment_dual_market_v1.3.20

================================================================================
⚠️ IMPORTANT DISCLAIMERS
================================================================================

NOT FINANCIAL ADVICE:
  This system is for educational and research purposes only.
  Not intended as financial advice or trading recommendations.

NO GUARANTEES:
  Past performance does not guarantee future results.
  Market conditions change and models may not predict accurately.

USER RESPONSIBILITY:
  Users are solely responsible for all trading decisions.
  Always verify data accuracy with official sources.
  Comply with all applicable regulations and laws.

DATA SOURCE:
  Uses Yahoo Finance API via yahooquery (free tier)
  Data may be delayed, incomplete, or inaccurate

================================================================================
📝 VERSION INFORMATION
================================================================================

Package:       Dual_Market_Screening_v1.3.20_20251121.zip
Version:       ASX v1.3.20 + US v1.0.0
Release Date:  2025-11-21
Status:        Production Ready

Components:
  - ASX Event Risk Guard:     v1.3.20 (Stable)
  - US Market Pipeline:       v1.0.0 (Production Ready)
  - Market Regime Engines:    ASX + US (Complete)
  - Unified Launcher:         v1.0.0 (Operational)

================================================================================
📞 SUPPORT
================================================================================

DOCUMENTATION:
  - Read DEPLOYMENT_README.md for complete information
  - Check QUICK_START_US_PIPELINE.txt for quick help
  - Review logs in logs/screening/ for error details

VERIFICATION:
  - Run: python VERIFY.py
  - This tests all components and connectivity

COMMON ISSUES:
  - Import errors: Re-run INSTALL script
  - Data errors: Check internet connection
  - Memory errors: Reduce --stocks parameter

SYSTEM CHECK:
  - Python version: python --version (requires 3.8+)
  - Dependencies: pip list | grep -E "yahooquery|pandas|numpy"

================================================================================
✅ READY TO USE
================================================================================

Your system is ready! Start with:

  1. Run verification:
     python VERIFY.py

  2. Run quick test:
     python run_screening.py --market both --stocks 5

  3. Review outputs in:
     reports/ and data/

  4. Scale up to production:
     python run_screening.py --market both --parallel

For detailed help, see DEPLOYMENT_README.md

================================================================================
Package: Dual_Market_Screening_v1.3.20_20251121.zip
Maintainer: Event Risk Guard Team
Date: 2025-11-21
================================================================================
