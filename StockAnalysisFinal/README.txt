STOCK ANALYSIS SYSTEM - WINDOWS 11 FINAL VERSION
=================================================

This version is specifically fixed for Windows 11 connectivity issues.

FEATURES:
---------
✅ Automatic fallback to test data if APIs fail
✅ Fixed 404 errors
✅ Working candlestick, line, and area charts
✅ RSI technical indicator
✅ Volume analysis
✅ Support for US and Australian stocks

INSTALLATION & RUN:
------------------
1. Double-click "install_and_run.bat"
2. Browser will open automatically
3. Start analyzing stocks!

HOW IT WORKS:
-------------
1. First tries Yahoo Finance API
2. If that fails, tries Alpha Vantage API  
3. If both fail, uses test data so charts always work

TROUBLESHOOTING:
---------------
Problem: "Python not found"
Solution: Install Python from https://www.python.org
         Make sure to check "Add to PATH"

Problem: Port 8000 in use
Solution: Close other programs using port 8000
         Or edit app.py and change 8000 to another port (e.g., 8080)

Problem: No internet warning
Solution: The app will still work with test data
         Real data will load when connection is restored

QUICK START:
-----------
1. Run "install_and_run.bat"
2. Try these symbols: AAPL, MSFT, GOOGL, TSLA, CBA, BHP
3. Select time period and chart type
4. Click "Generate Chart"

The system will automatically handle any connection issues and 
ensure you always get a working chart!

TECHNICAL DETAILS:
-----------------
- Uses Flask web framework
- Plotly for interactive charts
- yfinance for Yahoo data
- Alpha Vantage as backup
- Test data generator for offline use

Enjoy analyzing stocks on Windows 11!