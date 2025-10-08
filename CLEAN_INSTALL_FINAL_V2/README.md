# Stock Tracker Pro - Clean Install Package v5.0.0

## 🚀 Quick Start

1. **Install Dependencies**
   ```batch
   INSTALL.bat
   ```

2. **Start All Services**
   ```batch
   START_ALL_SERVICES.bat
   ```

3. **Access Application**
   Open browser to: http://localhost:8000

---

## ✅ What's Included

### Core Features
- ✅ **Real Yahoo Finance Data Only** - No synthetic/demo data
- ✅ **ADST Timezone Support** - Correct Australian Daylight Saving Time
- ✅ **Fixed Market Hours Display**
  - ASX: 10:00-16:00 ADST
  - FTSE: 19:00-03:30 ADST (evening/night)
  - S&P 500: 01:30-08:00 ADST (early morning)
- ✅ **FinBERT Document Analysis** - Consistent sentiment analysis
- ✅ **100MB File Upload Support**
- ✅ **Caching for Consistency** - Same document = same results

### Fixed Issues
- ✅ Backend connection showing "Disconnected" - FIXED
- ✅ FTSE/S&P plotting at wrong times - FIXED with time offsets
- ✅ Document analyzer giving different results - FIXED with caching
- ✅ All API URLs hardcoded to localhost - FIXED
- ✅ ML Training Centre connection - FIXED

---

## 📁 File Structure

```
CLEAN_INSTALL_FINAL_V2/
├── backend.py              # Main backend API (port 8002)
├── backend_core.py         # Core stock functions
├── document_analyzer.py    # FinBERT sentiment analysis
├── ml_backend.py          # ML service (port 8003)
├── market_tracker.html    # Fixed market tracker with ADST
├── index.html             # Main dashboard
├── START_ALL_SERVICES.bat # Master startup script
├── INSTALL.bat           # Installation script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🔧 System Requirements

### Required
- Windows 10/11
- Python 3.8+
- Internet connection (for Yahoo Finance)

### Python Packages
- fastapi, uvicorn (API framework)
- yfinance (stock data)
- pandas, numpy (data processing)
- PyPDF2, python-docx (document processing)
- transformers, torch (FinBERT sentiment - optional)

---

## 📊 Service Architecture

```
Frontend (Port 8000)
    │
    ├── Backend API (Port 8002)
    │   ├── Stock data (Yahoo Finance)
    │   ├── Market summary
    │   ├── Document analysis
    │   └── Historical data
    │
    └── ML Backend (Port 8003)
        ├── Model training
        ├── Predictions
        └── Model management
```

---

## 🎯 Key Endpoints

### Backend API (8002)
- `GET /api/health` - Health check
- `GET /api/stock/{symbol}` - Real-time stock data
- `GET /api/market-summary` - Market overview with ADST
- `GET /api/historical/{symbol}` - Historical data
- `POST /api/documents/upload` - Upload & analyze (100MB)
- `POST /api/predict` - Price prediction

### ML Backend (8003)
- `GET /health` - Service health
- `GET /api/ml/status` - ML service status
- `POST /api/ml/train` - Train model
- `GET /api/ml/models` - List models

---

## ⚠️ Important Notes

1. **First Run**: FinBERT model downloads on first use (~400MB)
2. **Market Hours**: All times displayed in ADST (UTC+11)
3. **Data Source**: Yahoo Finance only - no fallback data
4. **Caching**: Document analysis cached for consistency
5. **CBA.AX**: Should show real price (~$170 range)

---

## 🔍 Troubleshooting

### Backend shows "Disconnected"
- Check if backend.py is running on port 8002
- Verify Windows Firewall settings
- Restart with START_ALL_SERVICES.bat

### Document analysis inconsistent
- Ensure FinBERT is installed: `pip install transformers torch`
- Check analysis_cache folder exists
- Clear cache if needed: delete files in analysis_cache/

### Wrong market hours displayed
- Clear browser cache (Ctrl+F5)
- Verify using market_tracker.html from this package
- Check system time is correct

### Installation fails
- Run as Administrator
- Check Python version: `python --version` (needs 3.8+)
- Install pip if missing: `python -m ensurepip`

---

## 📈 Market Hours Reference (ADST)

| Market | Open | Close | Local Time |
|--------|------|-------|------------|
| ASX | 10:00 | 16:00 | Sydney |
| FTSE | 19:00 | 03:30* | London (+11h) |
| S&P 500 | 01:30 | 08:00 | New York (+16h) |

*Next day

---

## 🚦 Status Indicators

- **Backend Connected**: Real-time data available
- **ML Operational**: Predictions available
- **FinBERT Available**: Document sentiment active
- **Cache Active**: Consistent results enabled

---

## 📝 Version History

### v5.0.0 (Current)
- Complete rewrite with all fixes
- Real Yahoo Finance data only
- ADST timezone support
- FinBERT sentiment analysis
- 100MB upload support
- Consistent caching system
- Fixed all known issues

---

## 💡 Tips

1. **Performance**: First analysis takes longer (model loading)
2. **Accuracy**: CBA.AX should show ~$170 (real market price)
3. **Consistency**: Same document always gives same sentiment
4. **Updates**: Refresh data with Ctrl+F5 in browser

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Verify all services running (check console windows)
3. Review service logs in console output
4. Restart services if needed

---

**Stock Tracker Pro v5.0.0** - Real-time market analysis with no synthetic data