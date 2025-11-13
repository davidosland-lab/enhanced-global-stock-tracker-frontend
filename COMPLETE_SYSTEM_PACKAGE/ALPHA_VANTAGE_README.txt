═══════════════════════════════════════════════════════════════════════════════
             ALPHA VANTAGE MODE - INSTALLATION & USAGE GUIDE
═══════════════════════════════════════════════════════════════════════════════

📦 THIS PACKAGE USES ALPHA VANTAGE API (Yahoo Finance disabled due to IP blocking)

✅ WHAT'S CHANGED:
  • Data source: Alpha Vantage API (free tier: 500 req/day, 5 req/min)
  • Default config: 40 stocks (5 per sector) - Fast mode
  • Cache duration: 4 hours (to minimize API usage)
  • Rate limiting: 12 seconds between calls

⏱️ EXPECTED PERFORMANCE:
  • First run: ~16 minutes (validates + fetches 40 stocks)
  • Cached runs: <1 minute (uses 4-hour cache)
  • API usage: 80/500 calls per day

═══════════════════════════════════════════════════════════════════════════════
                            QUICK START
═══════════════════════════════════════════════════════════════════════════════

1. INSTALL DEPENDENCIES
   ---------------------
   pip install yfinance pandas numpy requests

2. TEST ALPHA VANTAGE CONNECTION
   ------------------------------
   python -c "from models.screening.alpha_vantage_fetcher import AlphaVantageDataFetcher; print('✅ Ready!')"

3. RUN OVERNIGHT SCREENER
   -----------------------
   python scripts\run_overnight_screener.py

4. MONITOR PROGRESS
   -----------------
   Watch console output:
   - Validating 40 tickers... (takes ~8 min)
   - Fetching data... (takes ~8 min)
   - Total: ~16 minutes

═══════════════════════════════════════════════════════════════════════════════
                        CONFIGURATION OPTIONS
═══════════════════════════════════════════════════════════════════════════════

OPTION A: FAST MODE (Default - 40 stocks, 16 minutes)
------------------------------------------------------
✅ Already configured!

Config file: models\config\asx_sectors_fast.json
  • 8 sectors × 5 stocks = 40 total
  • API calls: 80/500 per day
  • Time: ~16 minutes

OPTION B: FULL MODE (240 stocks, 48 minutes)
--------------------------------------------
Edit: models\screening\stock_scanner.py (line 51)

CHANGE:
  config_path = Path(__file__).parent.parent / "config" / "asx_sectors_fast.json"

TO:
  config_path = Path(__file__).parent.parent / "config" / "asx_sectors.json"

Config file: models\config\asx_sectors.json
  • 8 sectors × 30 stocks = 240 total
  • API calls: 480/500 per day
  • Time: ~48 minutes

═══════════════════════════════════════════════════════════════════════════════
                          FILES MODIFIED
═══════════════════════════════════════════════════════════════════════════════

1. models\screening\stock_scanner.py
   • Line 25: Uses alpha_vantage_fetcher instead of data_fetcher
   • Line 41: Cache TTL increased to 240 minutes (4 hours)
   • Line 51: Default config set to asx_sectors_fast.json

2. models\screening\alpha_vantage_fetcher.py (NEW)
   • Complete Alpha Vantage implementation
   • 4-hour caching
   • 12-second rate limiting (5 calls/min)
   • Tracks daily API usage (500 limit)

3. models\config\asx_sectors_fast.json (NEW)
   • Reduced ticker list: 5 stocks per sector
   • Total: 40 stocks (vs 240 in full config)
   • Optimized for Alpha Vantage free tier

═══════════════════════════════════════════════════════════════════════════════
                         ALPHA VANTAGE LIMITS
═══════════════════════════════════════════════════════════════════════════════

FREE TIER:
  • 500 requests per day
  • 5 requests per minute
  • Daily data only (no intraday)

WHAT HAPPENS IF LIMIT REACHED:
  • Error: "⛔ Daily API limit reached (500/500)"
  • Solution: Wait until midnight (resets daily)
  • Or: Upgrade to paid tier

PAID TIERS (optional):
  • $50/month: 1,200 req/min, unlimited daily
  • Intraday data support
  • Full scan in <5 minutes

═══════════════════════════════════════════════════════════════════════════════
                           CACHE BEHAVIOR
═══════════════════════════════════════════════════════════════════════════════

Cache Location: cache\ folder
Cache Duration: 4 hours
Cache Files: av_TICKER_daily.pkl

HOW IT WORKS:
  1. First run: Fetches all data from Alpha Vantage (~16 min)
  2. Data cached for 4 hours
  3. Second run (within 4 hours): Loads from cache (<1 min)
  4. After 4 hours: Refreshes data from Alpha Vantage

CLEAR CACHE:
  del cache\av_*.pkl

═══════════════════════════════════════════════════════════════════════════════
                          TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

ERROR: "⛔ Daily API limit reached (500/500)"
SOLUTION: Wait until midnight (UTC), limit resets daily

ERROR: "Alpha Vantage rate limit: Thank you for using Alpha Vantage!"
SOLUTION: Slow down requests. Edit alpha_vantage_fetcher.py line 45:
          self.rate_limit_delay = 15.0  # Increase from 12 to 15 seconds

ERROR: "No Alpha Vantage data for CBA.AX"
SOLUTION: Alpha Vantage may not support all ASX stocks
          • Check if ticker is valid on Yahoo Finance
          • Try without .AX suffix
          • Remove from config if consistently fails

ERROR: Import error "No module named 'alpha_vantage_fetcher'"
SOLUTION: Ensure you're in COMPLETE_SYSTEM_PACKAGE directory
          cd COMPLETE_SYSTEM_PACKAGE

ERROR: All tickers fail validation
SOLUTION: Check API key is valid (hardcoded: 68ZFANK047DL0KSR)
          • Test: curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=68ZFANK047DL0KSR"
          • If invalid, get new key at: https://www.alphavantage.co/support/#api-key

═══════════════════════════════════════════════════════════════════════════════
                         API USAGE TRACKING
═══════════════════════════════════════════════════════════════════════════════

The system tracks API usage automatically:

Console output shows:
  "API usage: 80/500 calls today"

Warning at 90% limit:
  "⚠️  High API usage: 455/500 calls today"

Error at limit:
  "⛔ Daily API limit reached (500/500)"

═══════════════════════════════════════════════════════════════════════════════
                         EXPECTED OUTPUT
═══════════════════════════════════════════════════════════════════════════════

FIRST RUN (No cache):
--------------------
2025-11-08 18:00:00 - INFO - Validating 40 tickers via Alpha Vantage...
2025-11-08 18:00:00 - INFO - ⚠️  This will take ~8.0 minutes (rate limiting)
2025-11-08 18:00:12 - INFO -   [1/40] ✓ CBA.AX: Valid (price=$175.91)
2025-11-08 18:00:24 - INFO -   [2/40] ✓ WBC.AX: Valid (price=$38.98)
...
2025-11-08 18:08:00 - INFO - Validation complete: 38/40 passed
2025-11-08 18:08:00 - INFO - API usage: 40/500 calls today

2025-11-08 18:08:00 - INFO - Batch fetching 38 tickers...
2025-11-08 18:08:12 - INFO -   [1/38] ✓ CBA.AX: 100 days
...
2025-11-08 18:16:00 - INFO - Batch fetch complete: 38/38 tickers
2025-11-08 18:16:00 - INFO - API usage: 78/500 calls today

SUBSEQUENT RUNS (With cache):
-----------------------------
2025-11-08 20:00:00 - INFO - All 40 tickers loaded from cache
2025-11-08 20:00:00 - INFO - Batch fetch complete: 40/40 tickers (cached)
2025-11-08 20:00:00 - INFO - API usage: 78/500 calls today (no new calls)

═══════════════════════════════════════════════════════════════════════════════
                         UPGRADE PATH
═══════════════════════════════════════════════════════════════════════════════

If you need faster performance or more stocks:

OPTION 1: Alpha Vantage Premium ($50/month)
  • 1,200 requests per minute
  • Unlimited daily calls
  • Intraday data support
  • Full 240 stock scan in <5 minutes

OPTION 2: Alternative APIs
  • EOD Historical Data: $20/month, unlimited
  • Financial Modeling Prep: $15/month, 250/min
  • Polygon.io: $29/month, unlimited historical

OPTION 3: VPN + Yahoo Finance
  • Connect to VPN (US/UK region)
  • Yahoo Finance might work through VPN
  • Revert to original data_fetcher.py

═══════════════════════════════════════════════════════════════════════════════
                         SUPPORT & RESOURCES
═══════════════════════════════════════════════════════════════════════════════

Alpha Vantage Documentation:
  https://www.alphavantage.co/documentation/

Get New API Key (if needed):
  https://www.alphavantage.co/support/#api-key

Test API Key:
  curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=YOUR_KEY"

═══════════════════════════════════════════════════════════════════════════════
                              STATUS
═══════════════════════════════════════════════════════════════════════════════

✅ Alpha Vantage fetcher implemented
✅ Fast config created (40 stocks)
✅ Stock scanner updated to use Alpha Vantage
✅ Cache TTL increased to 4 hours
✅ Rate limiting configured (12s = 5/min)
✅ Ready to run!

═══════════════════════════════════════════════════════════════════════════════
Generated: 2025-11-08
Package: FinBERT v4.4.4 - Alpha Vantage Edition
═══════════════════════════════════════════════════════════════════════════════
