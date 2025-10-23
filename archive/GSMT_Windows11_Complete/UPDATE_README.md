# GSMT Global Indices Tracker - Update v2.0

## What's New in This Update

### 🎯 Key Features
1. **Percentage Changes Display**: Y-axis now shows percentage change from previous day's close instead of absolute prices
2. **Regional Market Selection**: Easy switching between Asia Pacific, Europe, and Americas markets
3. **Enhanced Visual Design**: Improved market cards with live status indicators
4. **Real-time Statistics**: Live calculation of regional averages, top gainers/losers, and volume
5. **Better Performance**: Optimized data fetching and chart rendering

### 📊 Regional Markets Coverage

#### Asia Pacific
- ASX 200 (Australia)
- Nikkei 225 (Japan)
- Hang Seng (Hong Kong)
- Shanghai Composite (China)
- KOSPI (South Korea)
- STI (Singapore)

#### Europe
- FTSE 100 (UK)
- DAX (Germany)
- CAC 40 (France)
- Euro Stoxx 50
- IBEX 35 (Spain)
- AEX (Netherlands)

#### Americas
- Dow Jones (US)
- S&P 500 (US)
- NASDAQ (US)
- Russell 2000 (US)
- TSX (Canada)
- Bovespa (Brazil)

## Installation Instructions

### Quick Update (Existing Installation)
1. Place all update files in your GSMT installation directory
2. Run `UPDATE_INDICES_ENHANCED.cmd`
3. Launch the application with `RUN_GSMT.cmd`

### Direct Tracker Launch
- Run `LAUNCH_INDICES_TRACKER.cmd` to open just the enhanced indices tracker

## File Structure
```
GSMT_Windows11_Complete/
├── frontend/
│   ├── indices_tracker_percentage.html  (New enhanced tracker)
│   └── [other frontend files]
├── backend/
│   └── market_data_server.py
├── UPDATE_INDICES_ENHANCED.cmd  (Update script)
├── LAUNCH_INDICES_TRACKER.cmd   (Direct launcher)
└── UPDATE_README.md             (This file)
```

## How to Use

### Regional Selection
1. Click on the region buttons at the top (Asia Pacific, Europe, Americas)
2. Markets will automatically update to show available indices for that region
3. First 3 markets are auto-selected, click on market cards to customize

### Viewing Percentage Changes
- The main chart displays percentage changes from previous close
- Green indicates positive change, red indicates negative
- Zero line is highlighted for easy reference
- Hover over the chart for detailed values

### Market Status Indicators
- **Green dot**: Market is currently open
- **Red dot**: Market is closed
- **Orange dot**: Market in pre/post trading hours

### Time Controls
- **Period Selection**: Choose from 1 Day, 5 Days, 1 Month, 3 Months, 1 Year
- **Historical Date**: Use the calendar to view historical data
- **Timezone Toggle**: Switch between AEST and AEDT

### Statistics Panel
View real-time statistics at the bottom:
- Regional average percentage change
- Top performing index
- Worst performing index
- Total trading volume

## Troubleshooting

### Chart Not Displaying Data
1. Ensure the backend server is running (port 8000)
2. Check your internet connection for Yahoo Finance access
3. Try refreshing the page or clicking the Refresh button

### Markets Not Updating
- The tracker updates automatically every 60 seconds
- Click the Refresh button for immediate update
- Check if markets are open (see status indicators)

### Backend Server Issues
If the backend server fails to start:
1. Ensure Python is installed and in PATH
2. Check that port 8000 is not in use
3. Verify yfinance package is installed: `pip install yfinance`

## Technical Details

### Data Source
- Primary: Yahoo Finance API via yfinance library
- Fallback: Demo data for visualization when API is unavailable
- Update frequency: 60 seconds (automatic)

### Browser Compatibility
- Chrome/Edge: Fully supported
- Firefox: Fully supported
- Safari: Fully supported
- IE: Not supported

### Performance
- Optimized for tracking up to 10 indices simultaneously
- Chart renders 96 data points (15-minute intervals over 24 hours)
- Responsive design adapts to screen size

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify the backend server is running
4. Check browser console for error messages

## Version History

### v2.0 (Current)
- Added percentage change display
- Implemented regional market selection
- Enhanced visual design
- Added real-time statistics

### v1.0
- Initial unified tracker
- Basic price display
- Market selection

---

**Last Updated**: September 2024
**Version**: 2.0
**Status**: Production Ready