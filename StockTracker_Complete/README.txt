========================================================================
          STOCK TRACKER PRO - COMPLETE WINDOWS 11 PACKAGE
                        Version 3.0 - FINAL
========================================================================

PACKAGE CONTENTS:
-----------------
✓ Complete frontend with all HTML modules
✓ FastAPI backend with real Yahoo Finance data
✓ ML Backend with unified backtesting service
✓ All required startup scripts
✓ Full module structure preserved

KEY FEATURES:
-------------
• Real-time stock data from Yahoo Finance
• CBA.AX showing actual market price (~$167)
• ML Training Centre with centralized backtesting
• Document analyzer with sentiment integration
• All modules fully interconnected
• Windows 11 optimized

QUICK START (3 STEPS):
----------------------
1. Extract this zip to any folder (e.g., C:\StockTracker)
2. Double-click "INSTALL_AND_RUN.bat"
3. Open http://localhost:8000 in your browser

MANUAL START:
-------------
If the batch file doesn't work:
1. Open Command Prompt in the folder
2. Run: python start_all_services.py
3. Open http://localhost:8000

REQUIREMENTS:
-------------
• Windows 11 (also works on Windows 10)
• Python 3.8 or higher
• Internet connection for Yahoo Finance data

SERVICES PORTS:
---------------
• Frontend: http://localhost:8000
• Backend API: http://localhost:8002  
• ML Backend: http://localhost:8003

TROUBLESHOOTING:
----------------
1. If "Python not found":
   - Install Python from https://www.python.org
   - Make sure to check "Add Python to PATH" during installation

2. If ports are already in use:
   - The script will skip already running services
   - Or manually stop other applications using these ports

3. If packages fail to install:
   - Run: pip install -r requirements.txt
   - Or manually install: pip install fastapi uvicorn yfinance pandas numpy scikit-learn

FOLDER STRUCTURE:
-----------------
StockTracker_Complete/
├── index.html                 # Main dashboard
├── stock_analysis.html        # Stock analysis module
├── ml_training_centre.html    # ML training with backtesting
├── backend.py                 # Main backend service
├── ml_backend.py             # ML service with unified backtesting
├── unified_backtest_service.py # Centralized backtesting
├── start_all_services.py     # Python startup script
├── INSTALL_AND_RUN.bat       # Windows quick start
├── modules/                   # Additional modules
│   ├── analysis/
│   ├── market-tracking/
│   ├── predictions/
│   └── technical_analysis_*.html
└── README.txt                # This file

STOPPING THE SYSTEM:
--------------------
Press Ctrl+C in the command window to stop all services

SUPPORT:
--------
This is a complete, self-contained package. All dependencies will be
automatically installed on first run.

========================================================================
                    ENJOY YOUR STOCK TRACKING!
========================================================================