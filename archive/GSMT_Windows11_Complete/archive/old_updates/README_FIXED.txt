================================================================================
                    GSMT Ver 8.1.3 - FIXED VERSION
                         ALL ISSUES RESOLVED
================================================================================

HOW TO RUN:
-----------
1. Double-click "RUN_GSMT.cmd" (NOT the .bat files)
2. Wait for servers to start
3. Main dashboard opens automatically in browser
4. Click any module to use it

FIXED ISSUES:
-------------
✓ Batch files now execute properly (use .cmd extension)
✓ Landing page scrolling fixed (no infinite scroll)
✓ Indices tracker only plots during market hours
✓ AEST/AEDT timezone with 24-hour display from 9:00
✓ Markets display in order: Australia → Europe → USA
✓ CBA module data connectivity restored
✓ Single stock tracker uses correct version
✓ Technical analysis loads properly
✓ All API endpoints configured correctly

KEY FILES:
----------
RUN_GSMT.cmd                - Main launcher (DOUBLE-CLICK THIS)
START_GSMT.cmd              - Alternative launcher
frontend/main_dashboard.html    - Main dashboard with all modules
frontend/indices_tracker_fixed.html - Fixed indices with AEST
frontend/single_stock_tracker.html  - Working stock tracker
frontend/cba_market_tracker.html    - CBA analysis module

MARKET HOURS (AEST):
--------------------
ASX (^AORD):     10:00 - 16:00
Nikkei:          10:00 - 16:00  
Hong Kong:       11:30 - 18:00
London FTSE:     17:00 - 01:30 (next day)
Frankfurt DAX:   17:00 - 01:30 (next day)
NYSE/S&P 500:    23:30 - 06:00 (next day)

IMPORTANT:
----------
- Markets only show data during their trading hours
- X-axis starts at 9:00 AEST with hourly increments
- Toggle AEST/AEDT with the switch in indices tracker
- Keep the command window open while using the system

TROUBLESHOOTING:
----------------
If launcher opens in Notepad:
- Right-click RUN_GSMT.cmd
- Select "Open with" → "Command Prompt" or "cmd"
- Or rename to .cmd extension if it's .bat

If servers don't start:
- Check Python is installed: python --version
- Check ports 8000 and 8001 are free
- Run as Administrator if needed

If no data loads:
- Wait 10-15 seconds for servers to initialize
- Check internet connection
- Markets may be closed (shows last data)

================================================================================