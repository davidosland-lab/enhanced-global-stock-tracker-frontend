# FinBERT Ultimate Trading System v3.2
## Advanced AI-Powered Market Analysis Platform

### 🚀 Features

#### Core Capabilities
- **Real-Time Market Data**: Direct integration with Yahoo Finance API
- **AI Sentiment Analysis**: FinBERT-powered news sentiment analysis
- **Machine Learning Predictions**: Random Forest classifier with confidence scores
- **Technical Indicators**: RSI, MACD, ATR, SMA, EMA, VWAP
- **Economic Indicators**: VIX, Treasury Yield, Dollar Index, Gold prices
- **Intraday Trading**: 1m, 3m, 5m, 15m, 30m, 60m, Daily intervals
- **Interactive Charts**: Candlestick charts with zoom, pan, and crosshair

#### Key Improvements in v3.2
- ✅ Fixed candlestick chart rendering (no more overlapping)
- ✅ Restored prediction panel with confidence percentages
- ✅ Restored sentiment gauge with visual indicator
- ✅ Added Alpha Vantage API integration (Key: 68ZFANK047DL0KSR)
- ✅ Fixed all API endpoint mismatches
- ✅ Implemented proper data aggregation for daily OHLC
- ✅ Added zoom functionality (mouse wheel, pinch, drag)
- ✅ Fixed technical indicators display
- ✅ Ensured only real market data (no synthetic fallback)

---

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 11 (64-bit)
- **RAM**: 8 GB (16 GB recommended)
- **Storage**: 2 GB free space
- **Internet**: Broadband connection required
- **Python**: 3.8 or higher (3.12 recommended)

### Browser Requirements
- Chrome 90+ (recommended)
- Firefox 88+
- Edge 90+
- Safari 14+

---

## 🛠️ Installation

### Method 1: Automated Installation (Recommended)
1. Extract the ZIP file to your desired location (e.g., `C:\FinBERT_Trading`)
2. Right-click on `INSTALL_WINDOWS.bat` and select "Run as Administrator"
3. Follow the on-screen prompts
4. Installation will automatically:
   - Check/install Python
   - Create virtual environment
   - Install all dependencies
   - Verify the installation

### Method 2: Manual Installation
1. Install Python 3.8+ from https://www.python.org/downloads/
2. Open Command Prompt as Administrator
3. Navigate to the extracted folder:
   ```cmd
   cd C:\FinBERT_Trading
   ```
4. Create virtual environment:
   ```cmd
   python -m venv venv
   ```
5. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
6. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

---

## 🚀 Starting the System

### Quick Start
1. Double-click `START_SYSTEM.bat`
2. Wait for the system to initialize (10-15 seconds)
3. Your default browser will automatically open to http://localhost:5000
4. If browser doesn't open, manually navigate to http://localhost:5000

### Manual Start
1. Open Command Prompt
2. Navigate to the installation folder
3. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
4. Run the application:
   ```cmd
   python app_finbert_complete_v3.2.py
   ```

---

## 📊 Using the System

### Main Interface
1. **Stock Symbol Input**: Enter any valid stock ticker (e.g., AAPL, MSFT, TSLA)
2. **Time Interval Selection**: Choose from 1m to Daily intervals
3. **Analysis Button**: Click to fetch data and run analysis

### Chart Controls
- **Zoom**: Use mouse wheel or pinch gesture
- **Pan**: Click and drag on the chart
- **Crosshair**: Hover to see precise values
- **Reset**: Double-click to reset zoom

### Panels Overview
1. **Price Chart**: Candlestick chart with volume bars
2. **Technical Indicators**: RSI, MACD, ATR values
3. **ML Prediction**: Buy/Hold/Sell with confidence percentage
4. **Sentiment Analysis**: Market sentiment gauge (0-100)
5. **Economic Indicators**: VIX, Treasury, Dollar, Gold
6. **News Feed**: Latest news with individual sentiment scores

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### System Won't Start
- **Solution**: Run INSTALL_WINDOWS.bat as Administrator
- Check Python installation: `python --version` in Command Prompt
- Verify all files are extracted properly

#### "Module Not Found" Errors
- **Solution**: Reinstall dependencies
  ```cmd
  venv\Scripts\activate
  pip install --upgrade -r requirements.txt
  ```

#### Chart Not Loading
- **Solution**: Clear browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Check console for errors (F12 → Console tab)

#### No Market Data
- **Issue**: Markets closed or API limit reached
- **Solution**: Wait for markets to open (9:30 AM - 4:00 PM EST)
- Try different stock symbols

#### Port 5000 Already in Use
- **Solution**: Stop other applications using port 5000
- Or modify app_finbert_complete_v3.2.py:
  ```python
  app.run(debug=True, port=5001)  # Change to different port
  ```

---

## 🔐 API Configuration

### Alpha Vantage API
- **Current Key**: 68ZFANK047DL0KSR
- **Limits**: 25 requests per day (free tier)
- **To Change Key**: Edit line 35 in app_finbert_complete_v3.2.py:
  ```python
  self.alpha_vantage_key = "YOUR_NEW_KEY_HERE"
  ```

### Getting New API Keys
1. **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
2. **Yahoo Finance**: No key required (public API)

---

## 📁 File Structure

```
FinBERT_v3.2_FINAL_DEPLOYMENT/
├── app_finbert_complete_v3.2.py    # Backend server
├── finbert_charts_complete.html    # Frontend UI
├── requirements.txt                # Python dependencies
├── INSTALL_WINDOWS.bat             # Installation script
├── START_SYSTEM.bat                # Startup script
├── README.md                       # This file
└── venv/                          # Virtual environment (created during install)
```

---

## ⚠️ Important Notes

### Security
- This system is designed for LOCAL use only
- Do not expose to public internet without proper security measures
- API keys are embedded for convenience - replace with your own for production

### Data Accuracy
- Market data has 15-minute delay for free tier
- Intraday data limited to last 5 trading days
- Historical data goes back 2 years maximum

### Performance
- First load may take 30-60 seconds (model initialization)
- Subsequent analyses are faster (5-10 seconds)
- Chrome/Edge provides best performance

---

## 📞 Support

### Getting Help
1. Check this README first
2. Review error messages in console (F12)
3. Restart the system
4. Reinstall if issues persist

### Known Limitations
- FinBERT model requires internet for initial download (500MB)
- Some international stocks may have limited data
- Cryptocurrency analysis not supported in this version

---

## 📈 Version History

### v3.2 FINAL (Current)
- Complete system overhaul
- Fixed all major bugs
- Added intraday trading support
- Restored all AI components
- Windows 11 optimized deployment

### Previous Versions
- v3.1: Partial fixes, unstable
- v3.0: Initial release with bugs
- v2.x: Legacy versions (deprecated)

---

## 📄 License

This software is provided as-is for educational and research purposes.
Not intended for production trading without proper testing and validation.

---

## 🙏 Credits

- **FinBERT Model**: ProsusAI
- **Market Data**: Yahoo Finance, Alpha Vantage
- **Charts**: Chart.js with Financial Plugin
- **ML Framework**: scikit-learn
- **Backend**: Flask, Python

---

**Last Updated**: October 28, 2024
**Version**: 3.2 FINAL DEPLOYMENT