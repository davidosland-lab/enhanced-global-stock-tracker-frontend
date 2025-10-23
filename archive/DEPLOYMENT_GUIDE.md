# Enhanced Global Stock Tracker - Deployment Guide

## 🚀 Current Status
All modules have been fixed and are working correctly. The following components are operational:

### ✅ Working Modules
1. **Single Stock Tracker** - `/single_stock_track_predict.html`
2. **Technical Analysis** - `/technical_analysis.html`
3. **Unified Predictions** - API endpoint `/api/unified-prediction/{symbol}`
4. **Performance Dashboard** - API endpoint `/api/dashboard/comprehensive-data`

## 📦 Repository Structure

### Frontend (This Repository)
- **Repository**: `davidosland-lab/enhanced-global-stock-tracker-frontend`
- **Deployment**: Netlify (auto-deploy on push)
- **URL**: Your Netlify URL

### Backend
- **Directory**: `/render_backend/`
- **Deployment**: Render.com
- **URL**: `https://enhanced-global-stock-tracker-backend.onrender.com`

## 🔧 API Configuration

### Centralized Configuration
All API URLs are managed through `api_config.js` which automatically detects the environment:

- **Local Development**: `http://localhost:8000`
- **Netlify Production**: `https://enhanced-global-stock-tracker-backend.onrender.com`
- **GitHub Pages**: `https://enhanced-global-stock-tracker-backend.onrender.com`

## 🌐 Backend Deployment (Render.com)

### Files Required
```
render_backend/
├── main.py                            # Main FastAPI application
├── requirements.txt                   # Python dependencies
├── technical_analysis_engine.py       # Technical indicators
├── technical_analysis_api.py          # Technical API routes
├── unified_prediction_api.py          # Unified prediction endpoints
├── dashboard_api.py                   # Dashboard endpoints
├── advanced_ensemble_predictor.py     # ML ensemble models
├── phase4_graph_neural_networks.py    # GNN implementation
└── ... (other modules)
```

### Render Configuration
Create a `render.yaml` in the backend directory:

```yaml
services:
  - type: web
    name: enhanced-global-stock-tracker-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Required Environment Variables
Set these in Render dashboard:
- `PORT`: (Automatically set by Render)
- `PYTHONUNBUFFERED`: 1
- Any API keys if needed

## 📝 Testing Deployment

### 1. Test Backend Health
```bash
curl https://enhanced-global-stock-tracker-backend.onrender.com/api/health
```

### 2. Test Module Endpoints
Open `/test_all_modules.html` in your browser to test all API connections.

### 3. Verify Each Module
- **Stock Tracker**: `/single_stock_track_predict.html`
  - Enter symbol (e.g., AAPL)
  - Click "Start Tracking"
  - Should show real-time data

- **Technical Analysis**: `/technical_analysis.html`
  - Select symbol
  - Click "Analyze"
  - Should show RSI, MACD, Bollinger Bands

- **Dashboard**: Check API response
  ```bash
  curl https://enhanced-global-stock-tracker-backend.onrender.com/api/dashboard/comprehensive-data
  ```

## 🐛 Troubleshooting

### Frontend Not Connecting to Backend
1. Check `api_config.js` is loaded
2. Verify backend URL in browser console
3. Check CORS settings in backend

### Module Not Loading
1. Check browser console for errors
2. Verify API endpoint exists:
   - Stock: `/api/stock/{symbol}`
   - Technical: `/api/technical/analysis/{symbol}`
   - Prediction: `/api/unified-prediction/{symbol}`
   - Dashboard: `/api/dashboard/comprehensive-data`

### Import Errors in Backend
- All imports are now absolute (not relative)
- Technical analysis uses: `from technical_analysis_engine import technical_engine`

## 📊 API Endpoints Reference

### Stock Data
- `GET /api/stock/{symbol}?period=1d&interval=5m`

### Technical Analysis
- `GET /api/technical/analysis/{symbol}`
- `GET /api/technical/candlestick-data/{symbol}`
- `GET /api/technical/indicators/rsi/{symbol}`
- `GET /api/technical/indicators/macd/{symbol}`
- `GET /api/technical/indicators/bollinger/{symbol}`
- `GET /api/technical/signals/{symbol}`
- `GET /api/technical/screener?symbols=AAPL,MSFT,GOOGL`

### Predictions
- `GET /api/unified-prediction/{symbol}?timeframe=5d`
- `GET /api/phase4-gnn-prediction/{symbol}`
- `GET /api/extended-phase3-prediction/{symbol}`

### Dashboard
- `GET /api/dashboard/comprehensive-data?timeframe=24h`
- `GET /api/dashboard/metrics/{metric_type}`
- `GET /api/dashboard/performance-summary`

## 🚦 Status Checklist

✅ **Fixed Issues:**
- Single Stock Tracker API connectivity
- Technical Analysis module imports
- Dashboard API routing
- Unified prediction endpoints
- CORS configuration

✅ **New Features:**
- Centralized API configuration
- Comprehensive test dashboard
- Technical analysis from GSMT-Ver-813

✅ **Deployment Ready:**
- All modules tested locally
- API endpoints verified
- Frontend URLs configured
- Backend imports corrected

## 📅 Last Updated
- Date: 2025-09-26
- Version: 2.0.0
- Status: Production Ready

## 🔗 Quick Links
- Frontend Repo: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- Backend URL: https://enhanced-global-stock-tracker-backend.onrender.com
- Test Page: `/test_all_modules.html`