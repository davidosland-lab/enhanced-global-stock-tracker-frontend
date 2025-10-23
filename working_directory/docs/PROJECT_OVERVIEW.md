# ASX Market Dashboard - Project Overview

## Project Description
A comprehensive real-time market tracking dashboard focused on Australian markets (ASX) with global market integration. The system provides live data visualization, historical analysis, and market period tracking across ASX, European, and US markets.

## Core Purpose
- **Primary Goal**: Provide real-time market data visualization for ASX stocks and global indices
- **Key Focus**: Australian Eastern Time (AEST) based market period tracking
- **Data Source**: Yahoo Finance API (yfinance) - REAL DATA ONLY, no synthetic generation

## Project Status
- **Current Phase**: Production with ongoing improvements
- **Last Major Update**: October 1, 2024
- **Version Control**: Git with protected branches and backup system

## Key Features
1. **Real-time Market Data**: Live updates every 30 seconds
2. **Market Period Visualization**: Shows ASX, European, and US market hours
3. **Historical Data Analysis**: Supports Today, Yesterday, Past 7 Days views
4. **Multi-Market Tracking**: Simultaneous display of multiple market indices
5. **Percentage Change Calculations**: Using previous close for accurate calculations

## Technical Stack
- **Backend**: Python FastAPI with yfinance
- **Frontend**: HTML5, JavaScript, Chart.js
- **Data Source**: Yahoo Finance API
- **Server**: Uvicorn ASGI server
- **Port**: 8002 (hardcoded for Windows compatibility)

## Recent Critical Fixes
1. **Windows Localhost Issue**: Fixed by using hardcoded `http://localhost:8002`
2. **Data Format Mismatch**: Resolved nested response handling
3. **Percentage Calculations**: Corrected to use `hist['Close'].iloc[-2]`
4. **Git Protection**: Implemented backup and version control system

## Project Structure
```
/home/user/webapp/
├── backend_fixed.py           # Protected backend server
├── modules/                   # Organized module structure
│   ├── market-tracking/      # Market visualization modules
│   ├── analysis/             # Analysis tools
│   ├── predictions/          # ML prediction modules
│   ├── documents/            # Document management
│   └── sandbox/              # Development/testing modules
├── docs/                      # Project documentation
│   ├── architecture/         # System architecture docs
│   ├── components/           # Component documentation
│   └── processes/            # Process documentation
├── static/                    # Static assets
└── backups/                  # Timestamped backups
```

## Development Guidelines
1. **NO SYNTHETIC DATA**: Always use real Yahoo Finance data
2. **Git Workflow**: Commit all changes immediately, create PRs
3. **Testing**: Test on Windows with hardcoded localhost URLs
4. **Backups**: Create timestamped backups before major changes
5. **Documentation**: Update docs with all significant changes

## Contact & Support
- **Environment**: Linux sandbox with Windows client testing
- **Critical Files**: backend_fixed.py (DO NOT MODIFY without backup)
- **Recovery**: Use GIT_PROTECTION_STATUS.md for rollback procedures