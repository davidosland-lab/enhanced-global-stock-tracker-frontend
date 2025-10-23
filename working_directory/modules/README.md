# Modules Directory Structure

## Organization
The modules are organized by functionality into the following categories:

### 📊 market-tracking/
Market visualization and real-time tracking modules
- Market period charts (ASX/FTSE/S&P zones)
- Global indices tracking
- Single stock monitoring
- Real-time updates every 30 seconds

### 📈 analysis/
Analytical tools for detailed market analysis
- CBA (Commonwealth Bank) detailed analysis
- Technical indicators
- Volume and price patterns

### 🔮 predictions/
Machine learning and predictive analytics
- ML-based market predictions
- Trend forecasting
- Pattern recognition

### 📄 documents/
Document management and navigation
- Central documentation hub
- Module navigation interface
- Quick links to all features

### 🧪 sandbox/
Development and testing modules
- Experimental features
- Debug versions
- Testing interfaces

## Module Standards
- All modules use `http://localhost:8002` for API calls
- AEST time zone for all displays
- Real Yahoo Finance data only (NO synthetic data)
- Chart.js for visualizations
- 30-second update intervals for real-time data

## Quick Start
1. Ensure backend is running: `python backend_fixed.py`
2. Open Document Center: `modules/documents/document_center.html`
3. Navigate to desired module from the hub

## Primary Production Modules
- **Market Visualization**: `market-tracking/market_periods_working_chart.html`
- **Analysis**: `analysis/cba_analysis.html`
- **Predictions**: `predictions/ml_predictions.html`
- **Navigation Hub**: `documents/document_center.html`