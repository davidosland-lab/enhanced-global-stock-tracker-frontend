================================================================================
                  FinBERT Ultimate Trading System v3.3
                         QUICK START GUIDE
================================================================================

INSTALLATION (First Time Only):
--------------------------------
1. Double-click INSTALL.bat
2. Follow the installation wizard
3. System will start automatically after installation

STARTING THE SYSTEM:
--------------------
Option 1: Double-click "FinBERT Trading System" on your Desktop
Option 2: Double-click START_SYSTEM.bat in this folder

USING THE SYSTEM:
-----------------
1. Browser will open to http://localhost:5000
2. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
3. Click "Get Analysis"
4. View real-time data, predictions, and charts

FEATURES:
---------
✓ Real market data from Yahoo Finance
✓ ML predictions (BUY/HOLD/SELL)
✓ Sentiment analysis
✓ Candlestick charts
✓ Volume analysis
✓ Technical indicators

STOPPING THE SYSTEM:
--------------------
Option 1: Close all command windows
Option 2: Run STOP_SYSTEM.bat

TROUBLESHOOTING:
----------------
If system doesn't start:
1. Run INSTALL.bat again
2. Check Python is installed (python --version in CMD)
3. Run TEST_API.bat to test the backend

If you see $0.00 prices:
- Backend isn't running - run START_SYSTEM.bat
- Check internet connection

FILES IN THIS PACKAGE:
----------------------
INSTALL.bat                      - Installation wizard (RUN THIS FIRST)
START_SYSTEM.bat                 - Start the trading system
STOP_SYSTEM.bat                  - Stop all processes
TEST_API.bat                     - Test if system is working
app_finbert_predictions_clean.py - Backend server (don't edit)
finbert_charts_complete.html     - Web interface
requirements.txt                 - Python dependencies
diagnose_finbert_fixed.py        - Diagnostic tool

SYSTEM REQUIREMENTS:
--------------------
- Windows 10 or 11
- Python 3.8 or higher
- Internet connection
- Chrome, Edge, or Firefox browser

SUPPORT:
--------
Run diagnose_finbert_fixed.py for system diagnostics
Check INSTALLATION_GUIDE.md for detailed instructions

================================================================================
Version: 3.3 CLEAN | Date: October 2024 | Status: PRODUCTION READY
================================================================================