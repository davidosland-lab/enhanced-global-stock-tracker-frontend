# 🚀 ML Stock Predictor - Unified System v2.0

## ✨ One System, One Interface, Zero Configuration

Your Alpha Vantage API key `68ZFANK047DL0KSR` is already integrated!

## 🎯 Quick Start (30 seconds)

### Option 1: Install & Run (Recommended for first time)
```batch
Double-click: INSTALL_AND_START.bat
```

### Option 2: Direct Start (If already installed)
```batch
Double-click: START_UNIFIED_SYSTEM.bat
```

### Option 3: Manual Start
```bash
python unified_ml_system.py
```

Then open your browser to: **http://localhost:8000**

## 🎨 What You Get - Single Unified Interface

### One URL, Everything Included:
- **📊 Market Data**: Real-time prices with automatic Yahoo/Alpha Vantage switching
- **🎯 Model Training**: Train Random Forest, XGBoost, or Gradient Boosting
- **🔮 Predictions**: 1-30 day forecasts with confidence intervals
- **📈 Backtesting**: Test strategies on historical data
- **🤖 MCP Integration**: Built-in AI assistant capabilities

## 🏗️ Simplified Architecture

```
INSTALL_AND_START.bat
    ↓
START_UNIFIED_SYSTEM.bat
    ↓
unified_ml_system.py
    ├── Web Interface (Port 8000) → unified_interface.html
    ├── Yahoo Finance (Primary, no key needed)
    ├── Alpha Vantage (Backup, your key integrated)
    ├── ML Models (3 algorithms, 35+ indicators)
    └── MCP Server (Port 8001, AI integration)
```

## 📁 Clean File Structure

```
ML_Stock_Final_Package/
├── 🚀 INSTALL_AND_START.bat      # One-click install & run
├── ▶️ START_UNIFIED_SYSTEM.bat    # Quick start
├── 🔧 TROUBLESHOOT.bat           # If something goes wrong
├── 🎨 unified_interface.html     # Single web interface
├── 🧠 unified_ml_system.py       # Main controller
├── ⚙️ config.py                  # Your API key & settings
├── 📊 ml_stock_predictor.py      # ML engine
├── 🌐 alpha_vantage_fetcher.py   # Backup data source
├── 🤖 mcp_integration.py         # AI assistant bridge
└── 📝 README.md                  # This file
```

## 🔑 Data Sources - Automatic Failover

### Primary: Yahoo Finance
- ✅ No API key required
- ✅ Unlimited requests
- ✅ Real-time data
- ✅ 1+ year historical data

### Backup: Alpha Vantage  
- ✅ Your API key pre-configured: `68ZFANK047DL0KSR`
- ✅ Automatic activation if Yahoo fails
- ✅ High-quality financial data
- ⚠️ Rate limited: 5 req/min, 500/day

**The system automatically switches between sources as needed!**

## 📊 Features in Detail

### Machine Learning Models
- **Random Forest**: Ensemble learning with multiple decision trees
- **XGBoost**: Gradient boosting with regularization
- **Gradient Boosting**: Sequential error correction

### Technical Indicators (35+)
- Moving averages (SMA, EMA, WMA)
- Momentum indicators (RSI, MACD, Stochastic)
- Volatility indicators (Bollinger Bands, ATR)
- Volume indicators (OBV, VWAP)
- And many more...

### Prediction Capabilities
- 1-30 day price forecasts
- Confidence intervals (90%, 95%, 99%)
- Multiple model comparison
- Visual prediction charts

### Backtesting Engine
- Historical strategy testing
- Performance metrics (Sharpe, returns, drawdown)
- Risk analysis
- Strategy optimization

## 🛠️ Troubleshooting

### If system won't start:
1. Run `TROUBLESHOOT.bat` to diagnose
2. Check Python version: `python --version` (need 3.8+)
3. Manually install packages: `pip install -r requirements_windows_py312.txt`

### Common Issues & Solutions:

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python from python.org |
| "Module not found" | Run `INSTALL_AND_START.bat` |
| "Port already in use" | Change port in `config.py` |
| "No data returned" | Check internet connection |
| "API rate limit" | Wait 12 seconds (Alpha Vantage) |

## ⚙️ Configuration (config.py)

```python
# Already configured with your API key!
ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
DEFAULT_DATA_SOURCE = 'yahoo'
USE_ALPHA_VANTAGE_BACKUP = True
API_PORT = 8000
MCP_PORT = 8001
```

## 📡 Status Indicators

The interface shows real-time status:
- 🟢 Green = Active/Working
- 🔴 Red = Inactive/Error
- 🟡 Yellow = Warning/Degraded

Monitored components:
- Yahoo Finance connection
- Alpha Vantage connection
- ML Engine status
- MCP Server status
- Current active data source

## 🤖 MCP Integration (For AI Assistants)

Connect your AI assistant to: `http://localhost:8001`

Available endpoints:
- `/tools/list` - List all available tools
- `/tools/call` - Execute a tool
- `/market_data` - Get stock data
- `/sentiment` - Analyze text sentiment

## 📈 Performance Tips

1. **Cache Usage**: Data cached for 5 minutes to reduce API calls
2. **Rate Limiting**: Automatic throttling for Alpha Vantage
3. **Model Persistence**: Trained models saved to disk
4. **Efficient Indicators**: Vectorized calculations for speed

## 🔒 Security Notes

- API key stored locally in `config.py`
- No external data transmission except to Yahoo/Alpha Vantage
- All processing done locally on your machine
- MCP server binds to localhost only

## 🚫 What Was Removed (Simplified)

- ❌ Multiple startup files → ✅ One unified launcher
- ❌ Three different interfaces → ✅ Single interface
- ❌ Separate MCP setup → ✅ Integrated into main system
- ❌ Complex configuration → ✅ Pre-configured with your API key
- ❌ Manual source switching → ✅ Automatic failover

## 📊 System Requirements

- **OS**: Windows 10/11 (Linux/Mac compatible)
- **Python**: 3.8+ (optimized for 3.12)
- **RAM**: 2GB minimum
- **Disk**: 500MB free space
- **Network**: Internet connection required

## 🎯 Next Steps

1. **Start the system**: Run `INSTALL_AND_START.bat`
2. **Open browser**: Navigate to http://localhost:8000
3. **Enter a stock symbol**: Try AAPL, MSFT, GOOGL
4. **Train a model**: Use the Train Models tab
5. **Make predictions**: Generate forecasts in the Predictions tab

## 📝 Support

If you encounter issues:
1. Run `TROUBLESHOOT.bat` first
2. Check the console output for error messages
3. Verify your internet connection
4. Ensure ports 8000 and 8001 are not in use

## 🎉 Ready to Trade!

Your ML Stock Predictor is fully configured and ready to use. The system will automatically handle data source switching, model training, and predictions. Just start it and begin analyzing!

---
**Version**: 2.0 Unified
**Last Updated**: October 19, 2024
**Your API Key**: ✅ Integrated and Active
**Support**: All features working with real market data only