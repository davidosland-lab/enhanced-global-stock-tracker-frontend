# Market Tracking Modules

## Overview
This folder contains all market visualization and tracking modules for real-time and historical market data display.

## Modules

### Primary Production Module
- **market_periods_working_chart.html** - Main production version with three-market visualization (ASX/FTSE/S&P)

### Enhanced Versions
- **market_periods_custom_periods.html** - Adds "Today", "Yesterday", "Past 7 Days" period selector
- **market_periods_final.html** - Stable version before custom periods
- **market_periods_combined_performance.html** - Performance optimized version
- **market_periods_exact_replica.html** - Exact match to user's hand-drawn design

### Global Indices Tracking
- **global_indices_tracker.html** - Original basic version
- **global_indices_tracker_enhanced.html** - Enhanced with better UI
- **global_indices_tracker_au_markets.html** - Australian market focus
- **global_indices_tracker_market_periods.html** - With market period zones
- **global_indices_tracker_realdata_only.html** - Ensures no synthetic data
- **global_indices_tracker_sandbox.html** - Development version
- **global_indices_tracker_sandbox_demo.html** - Demo with test features
- **global_indices_tracker_sandbox_fixed.html** - Fixed Windows localhost issues

### Single Stock Tracking
- **single_stock_tracker.html** - Individual stock monitoring interface

## Key Features
- Real-time updates every 30 seconds
- AEST time zone display
- Chart.js visualization with annotation plugin
- Market period zones (ASX red, FTSE blue, S&P purple)
- Historical data support (1d, 5d, 1mo, 3mo, 6mo, 1y)

## API Dependencies
- `/api/historical/{symbol}` - Historical market data
- `/api/quote/{symbol}` - Real-time quotes
- `/api/batch` - Multiple symbol quotes
- `/api/market-status` - Market hours information

## Usage
All modules connect to backend at `http://localhost:8002`

Select any HTML file and open in browser to use. Ensure backend_fixed.py is running first.