# Global Stock Market Tracker (GSMT) v7.0

## 🚀 Quick Start

1. **Run `INSTALL_CLEAN.cmd`** - Complete installation with all dependencies
2. **Run `LAUNCH_GSMT.cmd`** - Start the tracker

That's it! The tracker will open in your browser automatically.

## ✨ Key Features

### Real Market Data Only
- **100% Yahoo Finance data** - No demo or synthetic data
- **Live updates** - Automatic refresh every minute
- **Real-time prices** - Actual market values with full precision

### Market Hours Display
- **Markets shown only during trading hours** on the X-axis
- **ASX 200**: 10:00 - 16:00 AEST
- **FTSE 100**: 17:00 - 01:30 AEST
- **S&P 500**: 23:30 - 06:00 AEST

### Smart Features
- **Multi-region support** - Track Asia, Europe, and Americas simultaneously
- **Percentage changes** - Clear visualization from previous close
- **AEST/AEDT toggle** - Automatic timezone adjustment
- **Historical data** - Select any past date to view

## 📁 File Structure

```
GSMT_Windows11_Complete/
├── INSTALL_CLEAN.cmd          # One-click installation
├── LAUNCH_GSMT.cmd            # Main launcher (opens in browser)
├── backend/
│   └── live_market_server_simple.py  # Yahoo Finance API server
├── frontend/
│   ├── index.html             # Main tracker interface
│   └── indices_tracker_market_hours.html  # Market hours version
├── config/
│   └── settings.json          # Configuration file
└── archive/                   # Old versions (archived)
```

## 🔧 Troubleshooting

### Tracker doesn't open in browser?
The launcher uses multiple methods to open the browser:
1. Creates a temporary HTML redirect
2. Uses Windows file:// protocol
3. Falls back to Windows Explorer

### "Module not found" error?
Run `INSTALL_CLEAN.cmd` to install all dependencies automatically.

### Connection error in tracker?
1. Ensure the backend server window is open
2. Check if port 8000 is blocked by firewall
3. Wait a few seconds for the server to start

### Markets not showing data?
- Markets only display during their trading hours
- Outside trading hours, previous day's close is shown
- Check your internet connection for Yahoo Finance access

## 📊 Market Trading Hours (AEST)

| Region | Markets | Trading Hours |
|--------|---------|---------------|
| **Asia-Pacific** | ASX 200, Nikkei 225, Hang Seng | 10:00 - 17:00 |
| **Europe** | FTSE 100, DAX, CAC 40 | 17:00 - 01:30 (+1 day) |
| **Americas** | S&P 500, Dow Jones, NASDAQ | 23:30 - 06:00 (+1 day) |

## 🛠 Technical Details

### Backend Server
- **Framework**: FastAPI with Uvicorn
- **Data Source**: Yahoo Finance API (yfinance)
- **Port**: 8000 (configurable)
- **Caching**: 2-minute TTL for performance

### Frontend
- **Framework**: Vanilla JavaScript with Chart.js
- **Updates**: Real-time with 60-second auto-refresh
- **Storage**: No local storage of market data

## 📝 Version History

### v7.0 (Current)
- Fixed market hours display on X-axis
- Markets now only show during trading hours
- Improved browser launching reliability
- Complete removal of all demo data
- Clean installation script

### v6.x
- Removed all synthetic data generation
- Live Yahoo Finance integration

### Previous Versions
- Archived in `/archive/old_versions/`

## 💡 Tips

1. **Default Markets**: ASX 200, FTSE 100, and S&P 500 are pre-selected
2. **Multi-Selection**: Click markets to add/remove from tracking
3. **Region Toggle**: Click region headers to select/deselect all
4. **Best Performance**: Keep selected markets under 10 for smooth updates

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the backend server window
3. Ensure Python 3.8+ and all dependencies are installed

---

**NO DEMO DATA** - This tracker uses exclusively real market data from Yahoo Finance.