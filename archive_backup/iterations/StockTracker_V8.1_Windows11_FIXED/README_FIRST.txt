====================================================================
    STOCK TRACKER V8.1 - WINDOWS 11 - FIXED EDITION
    Real ML Implementation - No Fake Data
====================================================================

QUICK START INSTRUCTIONS:

1. INSTALL (Choose one):
   Option A: Run QUICK_INSTALL.bat (recommended, simpler)
   Option B: Run INSTALL.bat (full install with virtual environment)

2. START SERVICES:
   Run START_TRACKER.bat (or START.bat - they're the same)

3. ACCESS:
   Open http://localhost:8080 in your browser
   If issues, try http://localhost:8080/index_fixed.html

====================================================================

FILES IN THIS PACKAGE:

QUICK_INSTALL.bat    - Simple, fast installation (RECOMMENDED)
INSTALL.bat          - Full installation with virtual environment
START_TRACKER.bat    - Start all backend services
START.bat            - Same as START_TRACKER.bat
DIAGNOSE.bat         - Check what's wrong if not working
VERIFY_INSTALLATION.bat - Verify installation integrity

====================================================================

IF SERVICES SHOW "OFFLINE":

1. Run DIAGNOSE.bat to check what's wrong
2. Make sure you ran QUICK_INSTALL.bat first
3. Make sure START_TRACKER.bat console window is still open
4. Wait 10-15 seconds after starting for services to initialize
5. Try refreshing the browser page

====================================================================

TROUBLESHOOTING STEPS:

Step 1: Check Python
- Open Command Prompt
- Type: python --version
- Should show Python 3.8 or higher
- If not, install from python.org

Step 2: Install packages
- Run QUICK_INSTALL.bat
- Should take 1-3 minutes
- Watch for any error messages

Step 3: Start services
- Run START_TRACKER.bat
- Keep the black console window open
- Should show 4 services starting

Step 4: Check services
- Run DIAGNOSE.bat in a new window
- Should show services responding
- If not, check Windows Firewall

Step 5: Access interface
- Open Chrome or Edge browser
- Go to http://localhost:8080
- Or try http://localhost:8080/index_fixed.html

====================================================================

WINDOWS FIREWALL:

If Windows Firewall asks for permission:
- Click "Allow access" for Python
- Need to allow ports: 8002, 8003, 8004, 8080

====================================================================

FEATURES INCLUDED:

- REAL Machine Learning (10-60 second training times)
- NO fake or simulated data (verified)
- 15+ Global market indices tracking
- FinBERT sentiment analysis
- Backtesting with $100,000 capital
- SQLite cached historical data
- All 13 professional trading modules

====================================================================

SUPPORT FILES:

- WINDOWS_SETUP_GUIDE.md - Detailed setup instructions
- config/settings.json - Configuration options
- backends/*.py - Python backend services
- modules/*.html - Web interface modules

====================================================================

STILL HAVING ISSUES?

1. Close all Python windows
2. Run: taskkill /F /IM python.exe (in Command Prompt)
3. Delete venv folder if it exists
4. Run QUICK_INSTALL.bat again
5. Run START_TRACKER.bat
6. Use index_fixed.html instead of index.html

====================================================================