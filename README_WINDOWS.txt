================================================================================
UNIFIED STOCK ANALYSIS SYSTEM - WINDOWS 11 INSTALLATION
================================================================================

FEATURES:
- Real-time stock prices with intraday tracking (1min, 5min, 15min, 30min, 1hr)
- ML predictions using Random Forest and Gradient Boosting
- 12 Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Professional charts with Plotly and TradingView
- Australian stocks support with automatic .AX suffix
- Yahoo Finance and Alpha Vantage data sources
- Your Alpha Vantage API key integrated: 68ZFANK047DL0KSR

================================================================================
INSTALLATION INSTRUCTIONS:
================================================================================

1. PREREQUISITES:
   - Windows 11 (also works on Windows 10)
   - Python 3.8 or higher installed
   - Internet connection for package installation

2. QUICK START:
   a) Extract the ZIP file to any folder (e.g., C:\StockAnalysis)
   b) Double-click "setup_windows.bat" (first time only)
   c) The application will start automatically
   d) Open your browser to: http://localhost:8000

3. DAILY USE:
   - Double-click "run_windows.bat" to start the application
   - Or run: python unified_stock_professional.py

================================================================================
USAGE GUIDE:
================================================================================

1. BASIC ANALYSIS:
   - Enter stock symbol (e.g., CBA for Commonwealth Bank)
   - Select time period (Intraday, 5 Days, 1 Month, etc.)
   - For intraday: Select interval (1min, 5min, 15min, 30min, 1hr)
   - Click "Analyze Stock"

2. QUICK ACCESS STOCKS:
   - Australian: CBA, BHP, CSL, NAB, WBC (auto-adds .AX)
   - US: AAPL, MSFT, GOOGL, TSLA, AMZN

3. VIEW RESULTS:
   - Live Price Display (prominent at top)
   - Technical Indicators Card (RSI, MACD, etc.)
   - ML Predictions Card (price forecast, BUY/HOLD/SELL)
   - Professional Charts (TradingView and Plotly)

4. CHART OPTIONS:
   - Click "Plotly Chart" for server-side charts (no JS errors)
   - Use Candlestick/Line/Area buttons for different views
   - Toggle Volume on/off

================================================================================
TROUBLESHOOTING:
================================================================================

ISSUE: "Python is not installed"
SOLUTION: Download Python from https://python.org and install with "Add to PATH" checked

ISSUE: Port 8000 already in use
SOLUTION: Edit unified_stock_professional.py, change port 8000 to 8080 on last line

ISSUE: Package installation fails
SOLUTION: Run as Administrator: pip install -r requirements.txt

ISSUE: UTF-8 encoding errors
SOLUTION: Already fixed! FLASK_SKIP_DOTENV=1 is set automatically

ISSUE: No data for Australian stocks
SOLUTION: System automatically adds .AX suffix, just enter "CBA" not "CBA.AX"

================================================================================
TECHNICAL DETAILS:
================================================================================

SYSTEM REQUIREMENTS:
- RAM: 4GB minimum, 8GB recommended
- Disk: 500MB for installation
- Network: Required for real-time data
- Python: 3.8+ with pip

INCLUDED PACKAGES:
- Flask (Web framework)
- yfinance (Yahoo Finance API)
- pandas (Data analysis)
- numpy (Numerical computing)
- scikit-learn (Machine learning)
- plotly (Professional charts)
- flask-cors (Cross-origin support)

DATA SOURCES:
- Primary: Yahoo Finance (real-time)
- Backup: Alpha Vantage (with your API key)
- Cache: 5 minutes for daily, 1 minute for intraday

================================================================================
SUPPORT:
================================================================================

For issues or questions:
1. Check the console window for error messages
2. Ensure all prerequisites are installed
3. Try running setup_windows.bat again
4. Verify internet connection for data fetching

This is a complete, production-ready financial analysis system with professional
features including ML predictions, technical indicators, and real-time tracking.

================================================================================