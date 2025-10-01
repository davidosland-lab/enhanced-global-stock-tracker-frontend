# ASX Market Dashboard - Working Directory

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the backend server:**
```bash
python backend_fixed.py
```
Wait for message: "Uvicorn running on http://0.0.0.0:8002"

3. **Open the dashboard:**
Open `index.html` in your web browser

## 📁 Directory Structure

```
working_directory/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── backend_fixed.py              # Backend API server (PROTECTED)
├── index.html                    # Main landing page
├── modules/                      # All frontend modules
│   ├── market-tracking/         # Market visualization modules
│   ├── analysis/                # Analysis tools
│   ├── predictions/             # ML predictions
│   └── documents/               # Document center
└── docs/                        # Complete documentation
    ├── PROJECT_OVERVIEW.md      # Project description
    ├── LINK_MAPPING.md          # URL references
    ├── architecture/            # System architecture
    ├── components/              # Component docs
    └── processes/               # Development processes
```

## 🎯 Primary Modules

### Production Ready
- **Market Periods Chart**: `modules/market-tracking/market_periods_working_chart.html`
  - Displays ASX, FTSE, and S&P 500 market zones
  - Real-time updates every 30 seconds
  - AEST time zone display

- **Document Center**: `modules/documents/document_center.html`
  - Central navigation hub
  - Links to all modules and documentation

### Key Features
- ✅ Real Yahoo Finance data only (NO synthetic data)
- ✅ Windows localhost compatibility (hardcoded `http://localhost:8002`)
- ✅ Market period visualization with colored zones
- ✅ Custom period selector (Today/Yesterday/7 Days)
- ✅ Git version control and backup protection

## 🔧 Configuration

### Backend Settings
- **Port**: 8002 (hardcoded for Windows compatibility)
- **Host**: 0.0.0.0
- **API Base**: `http://localhost:8002`
- **Cache**: 5 minutes for efficiency
- **CORS**: Enabled for localhost

### Frontend Settings
- **Update Interval**: 30 seconds
- **Time Zone**: Australian Eastern Time (AEST)
- **Chart Library**: Chart.js 3.x with annotation plugin

## 📊 API Endpoints

- `GET /api/quote/{symbol}` - Real-time stock quote
- `GET /api/historical/{symbol}` - Historical data
- `POST /api/batch` - Multiple symbol quotes
- `GET /api/market-status` - Market open/close status

### Symbol Examples
- ASX Index: `^AORD`
- Commonwealth Bank: `CBA.AX`
- BHP: `BHP.AX`
- FTSE 100: `^FTSE`
- S&P 500: `^GSPC`

## 🛠️ Development

### Git Workflow
1. Create feature branch
2. Make changes
3. Commit immediately after changes
4. Create pull request
5. Merge to main

### Testing
- Test with real ASX symbols
- Verify percentage calculations
- Check AEST time display
- Test all period selections

## 📚 Documentation

- **Project Overview**: `docs/PROJECT_OVERVIEW.md`
- **System Architecture**: `docs/architecture/SYSTEM_ARCHITECTURE.md`
- **Component Documentation**: `docs/components/COMPONENT_DOCUMENTATION.md`
- **Development Processes**: `docs/processes/DEVELOPMENT_PROCESSES.md`
- **Link Mapping**: `docs/LINK_MAPPING.md`

## ⚠️ Important Notes

1. **DO NOT MODIFY** `backend_fixed.py` without creating a backup first
2. Always use real Yahoo Finance data - no synthetic/random data
3. All times displayed in Australian Eastern Time (AEST)
4. Windows users: Ensure URLs use `http://localhost:8002`

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8002 is already in use
- Verify Python dependencies are installed
- Check for syntax errors in console output

### No data showing
- Ensure backend is running
- Check browser console for errors
- Verify internet connection for Yahoo Finance

### Windows localhost issues
- URLs must be hardcoded as `http://localhost:8002`
- Don't use dynamic URL construction

## 📧 Support

For issues or questions, refer to:
- Git Protection Status: `GIT_PROTECTION_STATUS.md`
- Module Organization: `MODULE_ORGANIZATION_PROPOSAL.md`
- Full documentation in `/docs` folder

## 🔄 Version

Last Updated: October 2024
Backend Version: Protected (DO NOT MODIFY)
Frontend Version: Production with market periods