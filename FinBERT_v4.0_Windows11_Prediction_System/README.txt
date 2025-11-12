================================================================================
  FINBERT v4.0 - PREDICTION CACHING SYSTEM
  Windows 11 Deployment Package
================================================================================

QUICK START GUIDE
-----------------

Step 1: Install Python
   - Download Python 3.8+ from https://www.python.org/downloads/
   - Run installer and CHECK "Add Python to PATH"
   - Complete installation

Step 2: Install Dependencies
   - Double-click INSTALL.bat
   - Wait for installation to complete (2-5 minutes)
   - Installation will show "Installation Complete!" when done

Step 3: Start the Server
   - Double-click START_SERVER.bat
   - Server will start on http://localhost:5001
   - Keep the window open while using the application

Step 4: Use the Application
   - Open your web browser
   - Go to: http://localhost:5001
   - Enter a stock symbol (e.g., AAPL)
   - Click "Analyze" button
   - View prediction with charts and accuracy dashboard

Step 5: Stop the Server
   - In the server window, press Ctrl+C
   - Or simply close the window


PACKAGE CONTENTS
----------------

Main Files:
  INSTALL.bat                   - One-click installation script
  START_SERVER.bat              - One-click server startup
  app_finbert_v4_dev.py         - Main Flask application
  finbert_v4_enhanced_ui.html   - Web interface
  config_dev.py                 - Configuration settings
  requirements.txt              - Python dependencies

Documentation:
  README.txt                    - This file (quick start)
  README_PREDICTION_SYSTEM.md   - Complete feature guide
  INSTALLATION_GUIDE.md         - Detailed setup instructions
  QUICK_REFERENCE.txt           - Quick reference card
  MULTI_TIMEZONE_PREDICTIONS.md - Technical documentation

Models Directory:
  models/prediction_manager.py      - Prediction lifecycle manager
  models/market_timezones.py        - Multi-timezone handler
  models/prediction_scheduler.py    - Automated validation
  models/lstm_predictor.py          - LSTM neural network
  models/finbert_sentiment.py       - Sentiment analyzer
  models/trading/                   - Trading system modules

Auto-Created Files:
  trading.db                    - Prediction database (created on first run)
  news_sentiment_cache.db       - Sentiment cache (created on first run)
  trained_models/               - LSTM models (created after training)


SYSTEM REQUIREMENTS
-------------------

Minimum:
  - Windows 11 (or Windows 10)
  - Python 3.8 or higher
  - 4 GB RAM
  - 500 MB free disk space
  - Internet connection

Recommended:
  - Windows 11 (latest updates)
  - Python 3.10 or 3.11
  - 8 GB RAM
  - 2 GB free disk space
  - Broadband internet


FEATURES
--------

✅ Prediction Caching
   - One prediction per stock per day
   - Predictions stored in database
   - Consistent results throughout trading day

✅ Multi-Timezone Support
   - US Markets (NYSE/NASDAQ) - EST/EDT
   - Australian Markets (ASX) - AEDT/AEST
   - UK Markets (LSE) - GMT/BST

✅ Prediction Locking
   - Predictions lock at market open
   - Cannot change during trading hours
   - Pre-market generation window (90 minutes before open)

✅ Automated Validation
   - Scheduler validates predictions at market close
   - Calculates accuracy automatically
   - Updates database with results

✅ Accuracy Tracking
   - Historical prediction storage
   - Direction accuracy (BUY/SELL/HOLD)
   - Price accuracy metrics
   - Visual dashboard with charts

✅ Interactive Frontend
   - Real-time charts (candlestick & volume)
   - Sentiment analysis display
   - Prediction status indicators
   - Accuracy dashboard


SUPPORTED MARKETS
-----------------

United States (NYSE/NASDAQ):
   Trading Hours: 9:30 AM - 4:00 PM EST
   Symbols: AAPL, TSLA, MSFT, GOOGL (no suffix)

Australia (ASX):
   Trading Hours: 10:00 AM - 4:00 PM AEDT
   Symbols: BHP.AX, CBA.AX, ANZ.AX (use .AX suffix)

United Kingdom (LSE):
   Trading Hours: 8:00 AM - 4:30 PM GMT
   Symbols: BP.L, HSBA.L, VOD.L (use .L suffix)


TESTING THE SYSTEM
------------------

After installation, test with these examples:

US Stocks:
   - AAPL (Apple)
   - TSLA (Tesla)
   - MSFT (Microsoft)

Australian Stocks:
   - BHP.AX (BHP Group)
   - CBA.AX (Commonwealth Bank)

UK Stocks:
   - BP.L (BP)
   - HSBA.L (HSBC)


TROUBLESHOOTING
---------------

Problem: Python not found
Solution: 
   - Reinstall Python from python.org
   - Make sure to check "Add Python to PATH"
   - Restart your computer after installation

Problem: INSTALL.bat fails
Solution:
   - Run as Administrator (right-click -> Run as administrator)
   - Check internet connection
   - Try manual installation: pip install -r requirements.txt

Problem: Port 5001 already in use
Solution:
   - Find process: netstat -ano | findstr :5001
   - Kill process: taskkill /PID <PID> /F
   - Or change port in config_dev.py

Problem: Server starts but browser shows error
Solution:
   - Make sure you're using: http://localhost:5001 (not https)
   - Try: http://127.0.0.1:5001
   - Check firewall settings

Problem: No predictions showing
Solution:
   - Check internet connection (needed for stock data)
   - Try a different symbol
   - Check server console for error messages

Problem: TensorFlow warnings
Solution:
   - This is normal if TensorFlow not installed
   - System works without TensorFlow
   - Install with: pip install tensorflow (optional)


CONFIGURATION
-------------

To customize settings, edit config_dev.py:

Change Port:
   PORT = 5001  # Change to your preferred port

Cache Duration:
   PREDICTION_CACHE_HOURS = 24  # Hours to cache predictions

Enable/Disable Scheduler:
   ENABLE_SCHEDULER = True  # Set to False to disable


ADVANCED FEATURES
-----------------

Train LSTM Models:
   python models/train_lstm.py --symbol AAPL --epochs 50

View API Endpoints:
   http://localhost:5001/api/predictions/AAPL
   http://localhost:5001/api/predictions/AAPL/history
   http://localhost:5001/api/predictions/scheduler/status

Check System Health:
   http://localhost:5001/api/health


FILE STRUCTURE
--------------

FinBERT_v4.0_Windows11_Prediction_System/
├── INSTALL.bat              ← Run this first
├── START_SERVER.bat         ← Then run this to start
├── app_finbert_v4_dev.py    ← Main application
├── finbert_v4_enhanced_ui.html
├── config_dev.py
├── requirements.txt
├── models/
│   ├── prediction_manager.py
│   ├── market_timezones.py
│   ├── prediction_scheduler.py
│   └── trading/
└── Documentation files


SUPPORT & DOCUMENTATION
-----------------------

For detailed information:
   - README_PREDICTION_SYSTEM.md: Complete feature guide
   - INSTALLATION_GUIDE.md: Step-by-step setup
   - QUICK_REFERENCE.txt: Quick reference card

For technical details:
   - MULTI_TIMEZONE_PREDICTIONS.md: Technical architecture


VERSION INFORMATION
-------------------

Version: 4.0.0
Release Date: November 2025
Target Platform: Windows 11 (Windows 10 compatible)
Status: Production Ready


IMPORTANT NOTES
---------------

⚠️  This software is for trading analysis purposes only
⚠️  Not financial advice - use at your own risk
⚠️  Predictions are based on AI/ML models and may be incorrect
⚠️  Always verify predictions with your own research
⚠️  Keep your system and Python updated for security


LICENSE
-------

This software is provided as-is without warranty.
Use at your own risk for trading analysis purposes.


GETTING HELP
------------

1. Check troubleshooting section above
2. Review INSTALLATION_GUIDE.md for common issues
3. Check server console for error messages
4. Verify Python and dependencies are installed correctly


================================================================================
FinBERT v4.0 | Prediction Caching System | Windows 11 Optimized
================================================================================

REMEMBER:
1. Run INSTALL.bat first (one time only)
2. Run START_SERVER.bat to start the application
3. Open browser to http://localhost:5001
4. Enter stock symbol and click "Analyze"
5. Scroll down to see accuracy dashboard

Enjoy using FinBERT v4.0!
