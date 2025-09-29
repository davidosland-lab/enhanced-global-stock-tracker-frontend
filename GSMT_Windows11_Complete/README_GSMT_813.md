# GSMT Ver 8.1.3 - Complete Windows 11 Package
## Global Stock Market Tracker with Commonwealth Bank of Australia Specialist Module

### 🚀 Overview
GSMT Ver 8.1.3 is a comprehensive stock market analysis platform featuring advanced ML models, real-time market tracking, and specialized analysis for Commonwealth Bank of Australia (CBA.AX). This complete package includes all Phase 3 & 4 implementations with local deployment capabilities.

### ✅ Key Features

#### 1. **CBA Specialist Module** (Commonwealth Bank of Australia)
- **Real-time CBA.AX Stock Tracking**: Live price updates from ASX
- **Document Intelligence**: Analyze financial reports, PDFs, and publications
- **Market Sentiment Analysis**: News and social media sentiment scoring
- **ML Predictions**: 5 advanced models (LSTM, GRU, Transformer, GNN, Ensemble)
- **Banking Sector Comparison**: Big 4 Australian banks analysis
- **Publications Database**: Track CBA reports and announcements

#### 2. **Global Market Coverage**
- 18 major global indices in real-time
- Support for all ASX stocks
- International markets (NYSE, NASDAQ, LSE, etc.)
- Timezone-aware market hours

#### 3. **Advanced ML Models**
- **LSTM** (Long Short-Term Memory)
- **GRU** (Gated Recurrent Units)
- **Transformer** (Attention-based)
- **CNN-LSTM Hybrid**
- **Graph Neural Networks** (GNN)
- **Ensemble Methods**: XGBoost, LightGBM, CatBoost

#### 4. **Technical Analysis**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- Support/Resistance Levels
- ATR (Average True Range)

### 📦 Installation

#### Prerequisites
- Windows 11 (or Windows 10)
- Python 3.8 or higher
- 4GB RAM minimum
- Internet connection

#### Quick Start
1. **Extract the Package**
   ```
   Extract GSMT_VER_813_COMPLETE.zip to any folder
   ```

2. **Run Installation**
   ```
   Double-click INSTALL.bat
   ```

3. **Launch GSMT**
   ```
   Double-click LAUNCH_GSMT_813.bat
   ```

### 🖥️ System Architecture

#### Dual Server Architecture
- **Port 8000**: Market Data Server
  - Global indices tracking
  - Real-time price simulation
  - Historical data generation
  - Market hours management

- **Port 8001**: CBA Specialist Server
  - CBA.AX specific analysis
  - Document processing
  - Sentiment analysis
  - Banking sector comparison

### 📊 Module Details

#### CBA Module (Commonwealth Bank of Australia)
The CBA module is specifically designed to track and analyze Commonwealth Bank of Australia (ASX: CBA), Australia's largest bank by market capitalization.

**Features:**
- **Stock Price Tracking**: Real-time CBA.AX price with 5-minute updates
- **Document Analysis**: Process annual reports, research papers, regulatory filings
- **Sentiment Analysis**: Aggregate sentiment from Australian Financial Review, The Australian, Bloomberg
- **Peer Comparison**: Compare with WBC, ANZ, NAB, MQG
- **ML Predictions**: 1-day, 7-day, 30-day price predictions
- **Publications Tracking**: Monitor CBA official publications and announcements

**API Endpoints:**
- `/api/cba/price` - Current price and metrics
- `/api/cba/history` - Historical price data
- `/api/cba/prediction` - ML-based predictions
- `/api/cba/publications` - Official publications
- `/api/cba/sentiment` - Market sentiment
- `/api/cba/banking-sector` - Sector comparison
- `/api/cba/document-analysis` - Document upload and analysis

### 🎯 Testing

Run the comprehensive test suite:
```batch
python TEST_CBA_MODULE.py
```

To start servers and test:
```batch
python TEST_CBA_MODULE.py --start-servers
```

### 📁 Directory Structure
```
GSMT_Windows11_Complete/
│
├── backend/
│   ├── market_data_server.py      # Global market data
│   ├── cba_specialist_server.py   # CBA specific analysis
│   ├── main_server.py             # Main backend server
│   └── enhanced_ml_backend.py    # ML models implementation
│
├── frontend/
│   ├── comprehensive_dashboard.html  # All modules dashboard
│   ├── cba_market_tracker.html      # CBA specialist interface
│   ├── indices_tracker.html         # Global indices
│   ├── single_stock_tracker.html    # Individual stock analysis
│   ├── technical_analysis.html      # Technical indicators
│   ├── prediction_center.html       # ML predictions
│   └── config.js                    # Local configuration
│
├── data/
│   └── market_data/               # Local data storage
│
├── logs/
│   └── server.log                 # Application logs
│
└── Launch Files:
    ├── LAUNCH_GSMT_813.bat       # Complete system launcher
    ├── INSTALL.bat                # Installation script
    └── TEST_CBA_MODULE.py         # Test suite
```

### 🔧 Troubleshooting

#### Servers Not Starting
1. Check Python installation: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Check ports 8000 and 8001 are free
4. Run `TROUBLESHOOT.bat`

#### CBA Module Issues
1. Ensure port 8001 is not blocked
2. Check `backend/cba_specialist_server.py` exists
3. Run test suite: `python TEST_CBA_MODULE.py`

#### Frontend Not Loading
1. Ensure servers are running (check console windows)
2. Clear browser cache
3. Try different browser
4. Check `frontend/config.js` points to localhost

### 🌟 Key Improvements in Ver 8.1.3

1. **Fixed CBA Module**: Properly tracks Commonwealth Bank of Australia (CBA.AX) instead of Central Bank rates
2. **Dual Server Architecture**: Separate servers for market data and CBA specialist functions
3. **Complete Module Restoration**: All 9 original modules from Netlify deployment
4. **Local Deployment**: No dependency on Render.com or external services
5. **Enhanced ML Models**: Fully integrated Phase 3 & 4 implementations
6. **Comprehensive Testing**: Test suite for all functionality

### 📈 Market Coverage

#### Australian Markets (ASX)
- ASX 200 Index (^AXJO)
- All ASX listed stocks
- Focus on Big 4 Banks: CBA, WBC, ANZ, NAB
- Mining sector: BHP, RIO, FMG
- Tech sector: XRO, WTC, APT

#### Global Markets
- US: S&P 500, NASDAQ, Dow Jones
- Europe: FTSE 100, DAX, CAC 40
- Asia: Nikkei 225, Hang Seng, Shanghai Composite
- Emerging: BSE SENSEX, Bovespa, JSE

### 🔐 Security Features
- Local deployment (no external data transmission)
- CORS properly configured
- Input validation on all endpoints
- Secure document processing

### 📞 Support

For issues or questions about GSMT Ver 8.1.3:
1. Check the test suite: `python TEST_CBA_MODULE.py`
2. Review logs in `logs/` directory
3. Run troubleshooting: `TROUBLESHOOT.bat`
4. Check API documentation: http://localhost:8000/docs

### 🎉 Credits

GSMT Ver 8.1.3 - Complete Phase 3 & 4 Implementation
- Advanced ML Models Integration
- Commonwealth Bank of Australia Specialist Module
- Global Market Coverage
- Local Windows 11 Deployment

### ⚡ Quick Commands

```batch
# Install
INSTALL.bat

# Launch Complete System
LAUNCH_GSMT_813.bat

# Test CBA Module
python TEST_CBA_MODULE.py

# Check Status
CHECK_SERVER_STATUS.bat

# Emergency Start
EMERGENCY_START.bat

# Troubleshoot
TROUBLESHOOT.bat
```

### 📌 Important Notes

1. **CBA = Commonwealth Bank of Australia** (NOT Central Bank)
   - Stock Symbol: CBA.AX
   - Exchange: Australian Securities Exchange (ASX)
   - Sector: Banking & Financial Services
   - Market Cap: ~$193 Billion AUD

2. **Server Ports**
   - 8000: Market Data Server
   - 8001: CBA Specialist Server
   - Both required for full functionality

3. **Browser Compatibility**
   - Chrome (Recommended)
   - Firefox
   - Edge
   - Safari

---

**Version**: 8.1.3  
**Release**: September 2024  
**Platform**: Windows 11/10  
**Requirements**: Python 3.8+  
**Status**: Production Ready