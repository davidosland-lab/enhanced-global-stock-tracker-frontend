# Stock Analysis System - Windows 11

## 📈 Professional Stock Market Analysis Tool

A comprehensive stock analysis system with real-time data from Yahoo Finance, advanced technical indicators, and professional charting capabilities.

## ✨ Features

- **Real-Time Market Data**: Live stock prices from Yahoo Finance
- **Multiple Chart Types**: Candlestick (OHLC), Line, and Area charts
- **Technical Indicators**:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Simple Moving Averages (SMA 20, 50)
  - Volume Analysis
- **Time Periods**: 1 Day to 5 Years with appropriate intervals
- **Australian Stock Support**: Automatic .AX suffix for ASX stocks
- **Auto-Refresh**: 30-second interval updates
- **Professional UI**: Modern, responsive design

## 🚀 Quick Start

### Prerequisites
- Windows 11
- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- Internet connection

### Installation

1. **Extract the ZIP file** to your desired location (e.g., `C:\StockAnalysis`)

2. **Run the installer**:
   - Double-click `install.bat`
   - Follow the on-screen instructions
   - Wait for all packages to install

3. **Start the server**:
   - Double-click `start_server.bat`
   - The server will start at http://localhost:8000

4. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## 📊 How to Use

### Basic Usage

1. **Enter a Stock Symbol**:
   - US Stocks: AAPL, GOOGL, MSFT, TSLA, etc.
   - Australian Stocks: CBA, BHP, CSL (auto-adds .AX)

2. **Select Time Period**:
   - 1 Day: 5-minute intervals
   - 5 Days: 30-minute intervals
   - 1 Month to 5 Years: Daily/Weekly intervals

3. **Choose Chart Type**:
   - Candlestick: Shows OHLC (Open, High, Low, Close)
   - Line: Simple closing price line
   - Area: Filled area chart

4. **Click "Generate Chart"** to load the data

### Quick Access Stocks
Click any of the quick access buttons for popular stocks:
- AAPL (Apple)
- GOOGL (Google)
- MSFT (Microsoft)
- TSLA (Tesla)
- CBA (Commonwealth Bank)
- BHP (BHP Group)
- CSL (CSL Limited)

### Auto-Refresh
- Click "Auto Refresh: OFF" to enable
- Updates every 30 seconds
- Useful for tracking intraday movements

## 🛠️ Troubleshooting

### Python Not Found
- Install Python from https://www.python.org/downloads/
- During installation, check ✅ "Add Python to PATH"
- Restart your computer after installation

### Port 8000 Already in Use
- Close any other applications using port 8000
- Or modify the port in `stock_analysis_fixed_charts.py` (last line)

### No Data Showing
- Check your internet connection
- Verify the stock symbol is correct
- Try a known symbol like AAPL or GOOGL

### Installation Errors
- Run Command Prompt as Administrator
- Try: `pip install --user -r requirements.txt`
- Check firewall settings for Python

## 📁 Files Included

- `stock_analysis_fixed_charts.py` - Main application
- `requirements.txt` - Python package dependencies
- `install.bat` - Automated installer
- `start_server.bat` - Server launcher
- `README.md` - This documentation

## 🔧 Advanced Configuration

### Change Port
Edit `stock_analysis_fixed_charts.py`, find the last line:
```python
app.run(host='0.0.0.0', port=8000, debug=False)
```
Change `8000` to your desired port.

### Alpha Vantage Integration
The system includes Alpha Vantage API support. To enable:
1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Add your key to the code where indicated

## 📝 System Requirements

- **OS**: Windows 11 (also works on Windows 10)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **Storage**: 500MB free space
- **Internet**: Required for real-time data

## 🔒 Security Notes

- The application runs locally on your computer
- No data is stored or transmitted to external servers
- Stock data is fetched directly from Yahoo Finance
- Safe to use with no privacy concerns

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Ensure all prerequisites are installed
3. Try reinstalling with `install.bat`

## 📜 License

This software is provided as-is for personal use. Stock data is provided by Yahoo Finance and is subject to their terms of service.

## 🎯 Version

Version 1.0 - Fixed Charts Edition
- Resolved candlestick rendering issues
- Fixed price scale accuracy
- Enhanced technical indicators
- Improved Windows 11 compatibility

---

**Enjoy professional stock analysis on your Windows 11 PC!** 📈💹