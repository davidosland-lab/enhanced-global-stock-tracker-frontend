================================================================================
                          STOCK TRACKER v2.0
                         Windows 11 Edition
================================================================================

QUICK START GUIDE
-----------------
1. Double-click "INSTALL.bat" to set up everything automatically
2. Use desktop shortcuts to manage Stock Tracker
3. Access the web interface at http://localhost:8000

INCLUDED FILES
--------------
• INSTALL.bat               - One-click installer (RUN THIS FIRST!)
• StockTracker.bat         - Control Panel for managing services
• startup.bat              - Quick start all services
• shutdown.bat             - Stop all services
• backend.py               - Main backend server (port 8002)
• backend_ml_enhanced.py   - ML prediction backend (port 8003)
• index.html               - Landing page interface
• modules/                 - All trading modules

SYSTEM REQUIREMENTS
-------------------
• Windows 10/11
• Python 3.8 or higher
• Internet connection (for Yahoo Finance data)
• 500MB free disk space
• 4GB RAM recommended

FEATURES
--------
✓ Real-time stock tracking (ASX focus, especially CBA.AX)
✓ ML-powered predictions with 8 different models
✓ Historical data analysis and downloads
✓ Technical analysis indicators
✓ Document analysis (100MB file support)
✓ Global market tracking
✓ Phase 1-4 ML models integrated

MODULES INCLUDED
----------------
1. Indices Tracker - Track global market indices
2. Historical Data Manager - Download and analyze historical data
3. Document Analyser - Upload and analyze financial documents
4. Technical Analysis - Advanced charting and indicators
5. Prediction Centre - ML-powered price predictions
6. ML Training Centre - Train and test ML models
7. Stock Tracker - Main dashboard for ASX stocks

TROUBLESHOOTING
---------------
If you encounter issues:

1. Services won't start:
   - Run StockTracker.bat as Administrator
   - Choose option 6 (Troubleshoot) to diagnose issues
   - Ensure Python is installed and in PATH

2. "Module not found" errors:
   - Run INSTALL.bat again to reinstall packages
   - Or manually run: pip install fastapi uvicorn yfinance pandas numpy

3. Port conflicts:
   - Use StockTracker.bat option 2 to stop all services
   - Then use option 1 to restart

4. Cannot access web interface:
   - Check Windows Firewall settings
   - Ensure services are running (StockTracker.bat option 3)
   - Try: http://127.0.0.1:8000 instead of localhost

5. ML Backend disconnected:
   - Restart services using StockTracker.bat option 4
   - Check that port 8003 is not blocked

MANUAL INSTALLATION
-------------------
If INSTALL.bat doesn't work:

1. Install Python packages:
   pip install fastapi uvicorn yfinance pandas numpy scikit-learn python-multipart

2. Start services manually:
   - Open 3 command prompts
   - In prompt 1: python -m http.server 8000
   - In prompt 2: python backend.py
   - In prompt 3: python backend_ml_enhanced.py

3. Open browser to: http://localhost:8000

PORTS USED
----------
• 8000 - Frontend web server
• 8002 - Main backend API
• 8003 - ML backend API

SUPPORT
-------
For issues or questions:
1. Check the troubleshooting section above
2. Run StockTracker.bat option 6 for diagnostics
3. Ensure all files are in the same directory
4. Check that Python 3.8+ is installed

VERSION HISTORY
---------------
v2.0 (Current)
- Fixed Windows 11 localhost issues
- Replaced synthetic data with real Yahoo Finance data
- Fixed 404 errors on all modules
- Added ML Backend health endpoint
- Integrated 8 ML models (LSTM, GRU, Random Forest, XGBoost, etc.)
- Increased document upload limit to 100MB
- Added comprehensive batch file controls
- Created desktop shortcut system

================================================================================
                    © 2024 Stock Tracker - All Rights Reserved
================================================================================