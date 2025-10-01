# Link Mapping and URL References

## API Endpoint URLs
All frontend modules connect to the backend using these endpoints:

### Base URL
```
http://localhost:8002
```

### API Endpoints
- `GET /api/quote/{symbol}` - Real-time stock quote
- `GET /api/historical/{symbol}?period={period}` - Historical data
- `POST /api/batch` - Multiple symbol quotes
- `GET /api/market-status` - Market open/close status

## Module File Paths

### Old Structure (before reorganization)
```
/modules/
├── market_periods_working_chart.html
├── market_periods_custom_periods.html
├── global_indices_tracker_sandbox_fixed.html
├── cba_analysis.html
├── ml_predictions.html
└── document_center.html
```

### New Structure (after reorganization)
```
/modules/
├── market-tracking/
│   ├── market_periods_working_chart.html
│   ├── market_periods_custom_periods.html
│   └── global_indices_tracker_sandbox_fixed.html
├── analysis/
│   └── cba_analysis.html
├── predictions/
│   └── ml_predictions.html
└── documents/
    └── document_center.html
```

## Internal Module Links

### Document Center Navigation Links
The document center needs to be updated with new paths:

**Old links**:
- `./market_periods_working_chart.html`
- `./cba_analysis.html`
- `./ml_predictions.html`

**New links**:
- `../market-tracking/market_periods_working_chart.html`
- `../analysis/cba_analysis.html`
- `../predictions/ml_predictions.html`

## External Library CDN Links

### Chart.js
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@2.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.4.0/dist/chartjs-plugin-annotation.min.js"></script>
```

## Data Flow Links

### Symbol References
- ASX Index: `^AORD`
- FTSE 100: `^FTSE`
- S&P 500: `^GSPC`
- Commonwealth Bank: `CBA.AX`
- BHP: `BHP.AX`

### Time Period Parameters
- Today: `1d`
- Yesterday: `2d` with filtering
- Past 7 Days: `5d` (market days)
- 1 Month: `1mo`
- 3 Months: `3mo`
- 6 Months: `6mo`
- 1 Year: `1y`

## Cross-Module Data References

### Market Context Flow
```
Global Indices Tracker
    ↓ (provides market context)
CBA Analysis
    ↓ (provides analysis data)
ML Predictions
```

### Update Intervals
- Real-time data: 30 seconds
- Historical data: On demand
- Market status: 60 seconds

## Configuration References

### Backend Settings (backend_fixed.py)
- Port: 8002
- Host: 0.0.0.0
- CORS: Enabled for localhost
- Cache: 5 minutes

### Frontend Settings
- Update Timer: 30000ms (30 seconds)
- Chart Animation: 750ms
- Tooltip Delay: 0ms
- Legend Position: top

## Git References

### Branches
- `main` - Production branch
- `genspark_ai_developer` - AI development
- `backup-YYYY-MM-DD-HHMM` - Timestamped backups

### Important Commits
- Initial protected backend
- Fixed Windows localhost issue
- Implemented market period zones
- Added custom period selector

## File System References

### Critical Files
```
/home/user/webapp/
├── backend_fixed.py (PROTECTED - DO NOT MODIFY)
├── GIT_PROTECTION_STATUS.md
├── MODULE_ORGANIZATION_PROPOSAL.md
└── docs/
    ├── PROJECT_OVERVIEW.md
    ├── architecture/
    │   ├── SYSTEM_ARCHITECTURE.md
    │   └── COMPONENT_RELATIONSHIPS.md
    ├── components/
    │   └── COMPONENT_DOCUMENTATION.md
    └── processes/
        └── DEVELOPMENT_PROCESSES.md
```

## URL Parameters

### Historical Data Requests
```
/api/historical/CBA.AX?period=5d
```

### Batch Request Body
```json
{
  "symbols": ["CBA.AX", "BHP.AX", "^AORD"]
}
```

## Error Page References
When errors occur, modules should redirect to:
- Connection Error: Show inline error message
- Data Error: Display "No data available"
- Auth Error: Not applicable (public API)

## Testing URLs

### Local Testing
- Frontend: `file:///home/user/webapp/modules/documents/document_center.html`
- Backend: `http://localhost:8002/docs` (FastAPI documentation)
- Health Check: `http://localhost:8002/api/quote/CBA.AX`

## Navigation Hierarchy

### Level 1: Document Center
Entry point for all navigation

### Level 2: Feature Categories
- Market Tracking
- Analysis
- Predictions

### Level 3: Individual Modules
- Specific functionality pages

## Quick Access Links

### Most Used Modules
1. Market Periods Chart: `/modules/market-tracking/market_periods_working_chart.html`
2. Document Center: `/modules/documents/document_center.html`
3. CBA Analysis: `/modules/analysis/cba_analysis.html`

### Development Tools
1. Backend API Docs: `http://localhost:8002/docs`
2. Git Status: Run `git status` in `/home/user/webapp`
3. Server Logs: Check console where `backend_fixed.py` is running