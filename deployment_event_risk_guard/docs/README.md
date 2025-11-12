# ASX Market Dashboard

A professional real-time market tracking dashboard focused on Australian markets (ASX) with global market integration.

## 🚀 Quick Start

All production files are in the `working_directory/` folder.

```bash
cd working_directory
pip install -r requirements.txt
python backend_fixed.py
# Open index.html in your browser
```

## 📁 Repository Structure

```
.
├── working_directory/     # ✅ PRODUCTION FILES - Everything needed to run the project
│   ├── backend_fixed.py   # Backend API server
│   ├── index.html         # Main landing page
│   ├── requirements.txt   # Python dependencies
│   ├── modules/           # All frontend modules
│   ├── docs/              # Complete documentation
│   └── README.md          # Detailed setup instructions
│
└── archive/               # 📦 ARCHIVED - Old versions and development files
    ├── *.zip             # Previous versions
    ├── GSMT_*/           # Old packages
    └── ...               # Development/test files
```

## 🎯 Key Features

- **Real-time Market Data**: Live ASX, FTSE, and S&P 500 tracking
- **Market Period Visualization**: Color-coded market zones (ASX red, FTSE blue, S&P purple)
- **Australian Focus**: All times in AEST, ASX-centric design
- **Real Data Only**: Yahoo Finance integration, no synthetic data
- **Windows Compatible**: Hardcoded localhost:8002 for reliability

## 📊 Main Components

### Backend
- FastAPI server on port 8002
- Yahoo Finance (yfinance) integration
- Real-time and historical data endpoints
- CORS enabled for localhost

### Frontend
- Chart.js for visualizations
- 30-second auto-refresh
- Responsive design
- Multiple view options (Today/Yesterday/7 Days)

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, yfinance
- **Frontend**: HTML5, JavaScript, Chart.js
- **Data Source**: Yahoo Finance API
- **Version Control**: Git

## 📚 Documentation

Complete documentation is available in `working_directory/docs/`:
- Project Overview
- System Architecture
- Component Documentation
- Development Processes
- API Reference

## ⚠️ Important Notes

1. **Protected Files**: Do not modify `backend_fixed.py` without backup
2. **Port 8002**: Hardcoded for Windows compatibility
3. **Real Data**: Always uses Yahoo Finance, no synthetic data
4. **Time Zone**: All displays in Australian Eastern Time (AEST)

## 🔧 Development

See `working_directory/docs/processes/DEVELOPMENT_PROCESSES.md` for:
- Git workflow
- Testing procedures
- Deployment guide
- Troubleshooting

## 📈 Live Demo

1. Start backend: `python working_directory/backend_fixed.py`
2. Open: `working_directory/index.html`
3. Select module from landing page

## 🤝 Contributing

1. Create feature branch
2. Make changes in `working_directory/`
3. Test with real market data
4. Submit pull request

## 📄 License

This project is for educational purposes. See archived LICENSE file for details.

---

**Current Version**: October 2024 - Production Ready with Full Documentation
**Status**: ✅ Organized and Production Ready