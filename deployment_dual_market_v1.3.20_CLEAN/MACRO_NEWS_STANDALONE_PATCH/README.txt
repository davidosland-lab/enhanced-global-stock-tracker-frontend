================================================================================
MACRO NEWS MONITOR - STANDALONE INSTALLER
================================================================================

NO GIT REQUIRED - Direct file installation

This package installs the Macro News Monitor feature that downloads and 
analyzes Federal Reserve and RBA announcements to adjust market sentiment.

================================================================================
WHAT'S INCLUDED
================================================================================

Files in this package:

  MACRO_NEWS_STANDALONE_PATCH/
  ├── install.bat                     - Automatic installer
  ├── README.txt                      - This file
  ├── test_installation.py            - Test script
  └── files/
      └── macro_news_monitor.py       - The main module (23KB)

================================================================================
INSTALLATION (2 STEPS)
================================================================================

STEP 1: Run the Installer
--------------------------

  cd C:\Users\david\AATelS\MACRO_NEWS_STANDALONE_PATCH
  install.bat

The installer will:
  1. Check your environment
  2. Create backups (in BACKUPS folder)
  3. Copy macro_news_monitor.py to models/screening/
  4. Check if pipelines are integrated
  5. Verify installation

STEP 2: Test It
---------------

  cd C:\Users\david\AATelS
  python test_macro.py

Expected output:
  Testing macro news...
  
  ================================================================================
  MACRO NEWS ANALYSIS - US MARKET
  ================================================================================
  Fetching Federal Reserve press releases...
    ✓ Found: FOMC...
    ✓ Found: Fed Statement...
  
  Articles found: 6
  Sentiment: -0.150
  
  ✓ MACRO NEWS IS WORKING!

================================================================================
WHAT THIS DOES
================================================================================

After installation, your pipelines will automatically:

1. Monitor Federal Reserve (US):
   - Press releases
   - FOMC statements  
   - Fed speeches
   - Interest rate announcements

2. Monitor RBA (Australia):
   - Media releases
   - Cash rate decisions
   - RBA speeches
   - Board minutes

3. Analyze with FinBERT:
   - AI sentiment analysis of each article
   - Bullish/Bearish/Neutral classification
   - Sentiment scores: -1.0 to +1.0

4. Adjust Market Sentiment:
   - Macro news has 20% weight
   - Impact: ±10 points on sentiment scale
   - Applied during Phase 1 of pipeline

================================================================================
EXPECTED PIPELINE OUTPUT
================================================================================

When you run the pipeline, you'll see:

  PHASE 1: US MARKET SENTIMENT
  
  ================================================================================
  MACRO NEWS ANALYSIS - US MARKET
  ================================================================================
    Fetching Federal Reserve press releases...
      ✓ Found: Federal Reserve Board announces...
      ✓ Found: FOMC Statement - November 2025
    ✓ Federal Reserve Releases: 2 articles
    
    Fetching Federal Reserve speeches...
      ✓ Found: Chair Powell Speech on Economic Outlook
    ✓ Federal Reserve Speeches: 1 article
    
    FinBERT sentiment: -0.250
  ✓ US Macro News: 3 articles, Sentiment: BEARISH (-0.250)
  
    Macro News Impact: -2.5 points
    Adjusted Sentiment: 65.0 → 62.5

================================================================================
TROUBLESHOOTING
================================================================================

Issue: "ModuleNotFoundError: No module named 'models.screening.macro_news_monitor'"

  Solution: The file wasn't installed. Re-run install.bat

---

Issue: "No articles found"

  Possible causes:
    - No internet connection
    - Firewall blocking requests
    - Website structure changed
    - Rate limiting
  
  Check:
    1. Can you access federalreserve.gov in your browser?
    2. Are you behind a corporate proxy?

---

Issue: Pipeline doesn't show macro news

  The file is installed but not integrated into your pipeline.
  
  Check if integration exists:
    findstr "MacroNewsMonitor" models\screening\us_overnight_pipeline.py
  
  If nothing found, your pipeline needs the integration code added.
  (Your pipelines should already have this if you installed Phase 8 patch)

---

Issue: "requests" or "beautifulsoup4" module not found

  Install dependencies:
    pip install requests beautifulsoup4

================================================================================
DEPENDENCIES
================================================================================

Required Python packages:
  - requests (for web scraping)
  - beautifulsoup4 (for HTML parsing)
  - FinBERT (optional, for sentiment analysis)

Install if missing:
  pip install requests beautifulsoup4

================================================================================
FILE LOCATIONS
================================================================================

After installation:

  C:\Users\david\AATelS\
  ├── models\screening\
  │   └── macro_news_monitor.py          (NEW - 23KB)
  ├── test_macro.py                       (Test script)
  └── BACKUPS\
      └── macro_news_backup_YYYYMMDD\    (Your backups)

================================================================================
ROLLBACK
================================================================================

If you need to undo the installation:

1. Find your backup folder:
   C:\Users\david\AATelS\BACKUPS\macro_news_backup_YYYYMMDD\

2. Restore files:
   copy BACKUPS\macro_news_backup_YYYYMMDD\*.* models\screening\ /Y

3. Or simply delete:
   del models\screening\macro_news_monitor.py

================================================================================
SUPPORT
================================================================================

For issues:
  1. Run test_macro.py to verify installation
  2. Check pipeline logs for "MACRO NEWS ANALYSIS"
  3. Verify dependencies are installed
  4. Check internet connectivity

================================================================================
VERSION INFO
================================================================================

Package Version: 1.0 (Standalone - No Git)
Module Size: ~23KB
Date: 2025-11-30
Compatibility: Python 3.7+

================================================================================
